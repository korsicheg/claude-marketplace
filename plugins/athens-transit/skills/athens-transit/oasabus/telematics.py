"""OASA telematics: Athens buses and trolleys, their stops, live positions, arrival predictions and
today's timetable. No key needed.

telematics.oasa.gr resolves to an address that silently drops every packet, while a sister
server in the same block answers with the real certificate. So a call tries the address that
worked last, then what DNS says, then the rest of the block, always with SNI and Host set to
telematics.oasa.gr, so the certificate is still checked."""
import http.client
import itertools
import json
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from .geo import Point

ATHENS = ZoneInfo("Europe/Athens")

HOST = "telematics.oasa.gr"
BLOCK = [f"195.46.22.{n}" for n in range(88, 96)]
CONNECT_TIMEOUT = 3
READ_TIMEOUT = 6
ATTEMPTS_PER_ADDRESS = 3
STATIC_DATA_TTL = 3 * 24 * 60 * 60  # lines, routes and stops change with the network, rarely


class OasaUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Line:
    code: int
    number: str  # what's on the bus, such as "040", "Α1" (Greek letters) or "11"
    name: str


@dataclass(frozen=True)
class Route:
    """One direction (or loop) of a line."""
    code: int
    line_code: int
    name: str
    from_first_terminus: bool  # OASA's RouteType 1; False is the way back
    length_m: float


@dataclass(frozen=True)
class Stop:
    code: str
    name: str
    point: Point
    order: int  # its place along the route, from 1


@dataclass(frozen=True)
class Arrival:
    """OASA's prediction for one bus at one stop."""
    route_code: int
    vehicle: str
    minutes: int


@dataclass(frozen=True)
class Bus:
    vehicle: str
    point: Point
    reported: datetime


class PinnedConnection(http.client.HTTPSConnection):
    """HTTPS to one of OASA's addresses, verified as telematics.oasa.gr."""

    def __init__(self, address):
        super().__init__(HOST, timeout=READ_TIMEOUT, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        sock = socket.create_connection((self.address, 443), CONNECT_TIMEOUT)
        sock.settimeout(READ_TIMEOUT)
        self.sock = self._context.wrap_socket(sock, server_hostname=HOST)


class Telematics:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.working_address_file = cache_dir / "working-address"
        self.departures = {}  # line code -> todays_departures(), for this run
        self.departures_lock = threading.Lock()

    def lines(self) -> list[Line]:
        return [Line(int(x["LineCode"]), x["LineID"], x["LineDescrEng"] or x["LineDescr"])
                for x in self.static("webGetLines")]

    def routes(self, line_code: int) -> list[Route]:
        return [Route(int(x["RouteCode"]), line_code, x["RouteDescrEng"] or x["RouteDescr"],
                      str(x["RouteType"]) == "1", float(x["RouteDistance"] or 0))
                for x in self.static("webGetRoutes", p1=line_code)]

    def stops(self, route_code: int) -> list[Stop]:
        stops = [Stop(str(x["StopCode"]), x["StopDescrEng"] or x["StopDescr"],
                      Point(float(x["StopLat"]), float(x["StopLng"])), int(x["RouteStopOrder"]))
                 for x in self.static("webGetStops", p1=route_code)]
        return sorted(stops, key=lambda stop: stop.order)

    def arrivals(self, stop_code: str) -> list[Arrival]:
        return [Arrival(int(x["route_code"]), str(x["veh_code"]), int(x["btime2"]))
                for x in self.live("getStopArrivals", p1=stop_code)]

    def buses(self, route_code: int) -> list[Bus]:
        return [Bus(str(x["VEH_NO"]), Point(float(x["CS_LAT"]), float(x["CS_LNG"])),
                    datetime.strptime(x["CS_DATE"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=ATHENS))
                for x in self.live("getBusLocation", p1=route_code)]

    def todays_departures(self, line_code: int) -> dict[bool, list[tuple[str, str]]]:
        """Today's scheduled trips as (departure, arrival) "HH:MM" pairs, keyed by
        from_first_terminus. OASA lists each bus's duty: start1/end1 is a trip from the first
        terminus, start2/end2 one from the other end."""
        with self.departures_lock:
            if line_code not in self.departures:
                self.departures[line_code] = self.fetch_departures(line_code)
            return self.departures[line_code]

    def fetch_departures(self, line_code: int) -> dict[bool, list[tuple[str, str]]]:
        duties = self.live("getDailySchedule", line_code=line_code) or {}
        trips = {True: set(), False: set()}
        for duty in duties.get("go", []) + duties.get("come", []):
            for leg, outbound in (("1", True), ("2", False)):
                start, end = duty.get(f"sde_start{leg}"), duty.get(f"sde_end{leg}")
                if start and end:
                    trips[outbound].add((start[11:16], end[11:16]))
        return {outbound: sorted(pairs) for outbound, pairs in trips.items()}

    def static(self, act, **params):
        """Data that changes rarely, kept on disk for a day."""
        cached = self.cache_dir / ("_".join([act, *map(str, params.values())]) + ".json")
        try:
            if time.time() - cached.stat().st_mtime < STATIC_DATA_TTL:
                return json.loads(cached.read_text())
        except (OSError, ValueError):
            pass
        data = self.live(act, **params)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps(data, ensure_ascii=False))
        return data

    def live(self, act, **params):
        """An API call: its JSON, with OASA's null (nothing known) as []."""
        path = "/api/?" + urlencode({"act": act, **params})
        failures = []
        for address in self.addresses():
            for _attempt in range(ATTEMPTS_PER_ADDRESS):
                conn = PinnedConnection(address)
                try:
                    conn.request("GET", path)
                    body = conn.getresponse().read()
                except (OSError, http.client.HTTPException) as e:
                    failures.append(f"{address}: {e}")
                    if conn.sock is None:
                        break  # no connection at all: the next address
                    continue  # connected, then it hung: OASA's server does that now and then
                finally:
                    conn.close()
                self.remember_working(address)
                data = json.loads(body) if body.strip() else None
                return [] if data is None else data
        raise OasaUnavailable(f"OASA telematics didn't answer ({'; '.join(failures)})")

    def addresses(self):
        """The address that worked last, then what DNS says, then the rest of OASA's block. Lazily:
        DNS is only asked when the remembered address fails (it can hang when the network does)."""
        tried = set()
        for address in itertools.chain(self.remembered_address(), self.resolved_addresses(), BLOCK):
            if address not in tried:
                tried.add(address)
                yield address

    def remembered_address(self):
        try:
            yield self.working_address_file.read_text().strip()
        except OSError:
            return

    def resolved_addresses(self):
        try:
            yield from (info[4][0] for info in socket.getaddrinfo(HOST, 443, socket.AF_INET, socket.SOCK_STREAM))
        except OSError:
            return

    def remember_working(self, address):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.working_address_file.write_text(address + "\n")
