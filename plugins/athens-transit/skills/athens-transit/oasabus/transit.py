"""Whole journeys on Athens public transport (metro, tram, suburban rail, buses and trolleys) from
Google's Routes API. Google only knows the published timetables; live.py swaps in OASA's
predictions for bus and trolley rides. The key needs the Routes API enabled; 10,000 requests a
month are free."""
import json
import urllib.request
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from urllib.parse import urlencode

from .geo import Point
from .maps import MapsUnavailable
from .planner import ATHENS

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELDS = ",".join(f"routes.legs.steps.{name}"
                  for name in ("travelMode", "staticDuration", "distanceMeters", "transitDetails"))
TIMEOUT = 20
MODES = {"BUS": "bus", "INTERCITY_BUS": "bus", "TROLLEYBUS": "trolley", "SUBWAY": "metro", "METRO_RAIL": "metro",
         "TRAM": "tram", "LIGHT_RAIL": "tram", "HEAVY_RAIL": "train", "COMMUTER_TRAIN": "train", "RAIL": "train"}
ICONS = {"bus": "🚌", "trolley": "🚎", "metro": "🚇", "tram": "🚊", "train": "🚆"}


@dataclass(frozen=True)
class Walk:
    meters: int
    minutes: float


@dataclass(frozen=True)
class Ride:
    mode: str  # "bus", "trolley", "metro", "tram", "train"
    line: str  # as on the vehicle: "M1", "040", "Α1"
    headsign: str
    board: str
    board_point: Point
    alight: str
    alight_point: Point
    departs: datetime  # Athens time
    arrives: datetime
    stops: int
    live: bool = False  # departs is OASA's prediction rather than the timetable
    stops_away: int | None = None  # where the live bus is now

    @property
    def icon(self) -> str:
        return ICONS.get(self.mode, "🚍")

    @property
    def is_oasa_bus(self) -> bool:
        return self.mode in ("bus", "trolley")

    def with_live_departure(self, departs: datetime, stops_away: int | None) -> "Ride":
        """This ride on the bus OASA predicts, leaving at departs; it takes as long as scheduled."""
        return replace(self, departs=departs, arrives=self.arrives + (departs - self.departs), live=True,
                       stops_away=stops_away)


@dataclass(frozen=True)
class Journey:
    """Walks and rides in order."""
    legs: tuple[Walk | Ride, ...]
    origin: Point
    destination: Point

    @property
    def rides(self) -> list[Ride]:
        return [leg for leg in self.legs if isinstance(leg, Ride)]

    @property
    def first_walk(self) -> Walk:
        first = self.legs[0]
        return first if isinstance(first, Walk) else Walk(0, 0.0)

    @property
    def last_walk(self) -> Walk:
        last = self.legs[-1]
        return last if isinstance(last, Walk) else Walk(0, 0.0)

    @property
    def leave_at(self) -> datetime | None:
        rides = self.rides
        return rides[0].departs - timedelta(minutes=self.first_walk.minutes) if rides else None

    @property
    def arrives(self) -> datetime | None:
        rides = self.rides
        return rides[-1].arrives + timedelta(minutes=self.last_walk.minutes) if rides else None

    @property
    def shape(self) -> tuple:
        """What tells two journeys apart other than their times."""
        return tuple((ride.line, ride.board, ride.alight) for ride in self.rides)

    @property
    def url(self) -> str:
        return "https://www.google.com/maps/dir/?" + urlencode(
            {"api": 1, "origin": str(self.origin), "destination": str(self.destination), "travelmode": "transit"})

    def with_ride(self, index: int, ride: Ride) -> "Journey":
        """This journey with one ride replaced, the later rides shifted by any delay it brings."""
        legs = list(self.legs)
        position = [i for i, leg in enumerate(legs) if isinstance(leg, Ride)][index]
        delay = ride.departs - legs[position].departs
        legs[position] = ride
        if delay > timedelta(0):
            legs = [replace(leg, departs=leg.departs + delay, arrives=leg.arrives + delay)
                    if isinstance(leg, Ride) and i > position else leg for i, leg in enumerate(legs)]
        return replace(self, legs=tuple(legs))


class GoogleTransit:
    def __init__(self, api_key: str | None):
        self.api_key = api_key

    def journeys(self, origin: Point, destination: Point, departure: datetime | None = None) -> list[Journey]:
        request = {"origin": waypoint(origin), "destination": waypoint(destination), "travelMode": "TRANSIT",
                   "computeAlternativeRoutes": True, "languageCode": "en"}
        if departure:
            request["departureTime"] = departure.astimezone(ATHENS).isoformat()
        answer = self.call(request)
        return [journey for journey in (parse_journey(route, origin, destination) for route in answer.get("routes", []))
                if journey.rides]

    def call(self, request: dict) -> dict:
        if not self.api_key:
            raise MapsUnavailable("no Google Maps key: journeys need the Routes API")
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": self.api_key, "X-Goog-FieldMask": FIELDS}
        try:
            with urllib.request.urlopen(urllib.request.Request(ROUTES_URL, json.dumps(request).encode(), headers),
                                        timeout=TIMEOUT) as response:
                return json.loads(response.read())
        except (OSError, ValueError) as e:
            raise MapsUnavailable(f"Google Routes API: {e}") from e


def waypoint(point: Point) -> dict:
    return {"location": {"latLng": {"latitude": point.lat, "longitude": point.lon}}}


def parse_journey(route: dict, origin: Point, destination: Point) -> Journey:
    legs = []
    for step in route["legs"][0].get("steps", []):
        if step.get("transitDetails"):
            legs.append(parse_ride(step["transitDetails"]))
        elif legs and isinstance(legs[-1], Walk):
            legs[-1] = Walk(legs[-1].meters + step.get("distanceMeters", 0),
                            legs[-1].minutes + seconds(step) / 60)
        else:
            legs.append(Walk(step.get("distanceMeters", 0), seconds(step) / 60))
    return Journey(tuple(legs), origin, destination)


def parse_ride(details: dict) -> Ride:
    stops, line = details["stopDetails"], details["transitLine"]
    return Ride(
        mode=MODES.get(line.get("vehicle", {}).get("type", ""), "bus"),
        line=line.get("nameShort") or line.get("name", "?"),
        headsign=details.get("headsign", ""),
        board=stops["departureStop"]["name"], board_point=point_of(stops["departureStop"]),
        alight=stops["arrivalStop"]["name"], alight_point=point_of(stops["arrivalStop"]),
        departs=athens_time(stops["departureTime"]), arrives=athens_time(stops["arrivalTime"]),
        stops=int(details.get("stopCount", 0)))


def point_of(stop: dict) -> Point:
    lat_lng = stop["location"]["latLng"]
    return Point(lat_lng["latitude"], lat_lng["longitude"])


def athens_time(utc: str) -> datetime:
    return datetime.fromisoformat(utc.replace("Z", "+00:00")).astimezone(ATHENS)


def seconds(step: dict) -> int:
    return int(step.get("staticDuration", "0s").rstrip("s"))
