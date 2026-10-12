"""Greek motorway tolls on a route.

The stations, their positions and their 2026 prices come from mydiodia.gr, which keeps them in line
with the operators' official price lists. The rules that decide which stations a route pays are a
port of the site's own calculator (js/calculator.js, tollsOnRoute), which its author tuned against
real trips:

- a frontal plaza spans the whole carriageway, so a route passing near it pays it (unlike the
  site, at the route's closest point to it, not the first one in reach, so the order of plazas and
  ramp booths on the route is right);
- a side (ramp) booth is paid only by driving through it, so the route must pass within metres;
- a booth that charges one direction is paid only going that way;
- a side booth counts only where the route joins (entry) or leaves (exit) its motorway;
- a flat-rate network (Attiki Odos) charges once per trip.
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path

from .feeds import FeedUnavailable, download, fresh, save
from .geo import Point, Polyline, angle_between
from .jsliteral import JsLiteralError, literal_after

SITE = "https://mydiodia.gr/"
UNVERSIONED_DATASET_URL = SITE + "data/tolls.js"
DATASET_RE = re.compile(r"/data/tolls\.js\?v=[\w.-]+")
DATASET_MARKER = "const TOLL_DATA ="
MAX_AGE_S = 7 * 24 * 3600  # prices change once a year, in January
PARSED_FILE = "tolls.json"
CAR = "cat2"  # mydiodia's categories: cat1 motorcycle, cat2 car, cat3 van, cat4 truck

FRONTAL_REACH_M = 2_500
SIDE_REACH_M = 60  # booths a route really drives through sit 2-15 m off it; the site's 130 m caught ramps 100 m off
SAME_INTERCHANGE_KM = 0.6  # two side booths this close are the paired ramps of one interchange
MAINLINE_WALK_KM = 1.0  # how far to walk along the route to read the motorway's direction
MIN_WALK_KM = 0.15
DIRECTION_BEARINGS = {"northbound": 0, "eastbound": 90, "southbound": 180, "westbound": 270}


@dataclass(frozen=True)
class TollStation:
    id: str
    name: str
    name_gr: str
    highway: str
    operator: str
    kind: str  # frontal, side or bridge
    point: Point
    price: float  # for a car
    direction: str | None = None  # the one direction it charges, if not both
    role: str | None = None  # entry or exit, for side booths
    charge_once_group: str | None = None
    upcoming: bool = False  # on the map but not charging yet

    @classmethod
    def from_dataset(cls, record: dict) -> "TollStation":
        return cls(
            id=record["id"], name=record.get("name_en") or record["name_gr"], name_gr=record["name_gr"],
            highway=record.get("highway", ""), operator=record.get("operator", ""), kind=record["type"],
            point=Point(record["lat"], record["lng"]), price=float(record[CAR]),
            direction=record.get("direction"), role=record.get("role"),
            charge_once_group=record.get("charge_once_group"), upcoming=record.get("status") == "upcoming")

    @property
    def reach_m(self) -> float:
        return SIDE_REACH_M if self.kind == "side" else FRONTAL_REACH_M


@dataclass(frozen=True)
class TollCharge:
    station: TollStation
    segment: int  # where on the route it is paid
    km: float
    direction_margin: float  # degrees: how clearly the route goes the station's way (0 if it charges both)


def load_stations(data_folder: Path) -> list[TollStation]:
    parsed = data_folder / PARSED_FILE
    if not fresh(parsed, MAX_AGE_S):
        try:
            refresh_stations(data_folder)
        except (FeedUnavailable, JsLiteralError):
            if not parsed.exists():
                raise
    return [TollStation.from_dataset(record) for record in json.loads(parsed.read_text())]


def refresh_stations(data_folder: Path) -> int:
    """Downloads the dataset again; returns how many stations it has."""
    script = download(_dataset_url())
    records = literal_after(script.decode("utf-8"), DATASET_MARKER)
    if not isinstance(records, list) or not records:
        raise JsLiteralError("the toll dataset is empty")
    save(data_folder / PARSED_FILE, json.dumps(records, ensure_ascii=False).encode())
    return len(records)


def tolls_on_route(route: Polyline, stations: list[TollStation]) -> list[TollCharge]:
    matched = sorted(_matched(route, stations), key=lambda charge: charge.segment)
    once_per_network = _charge_networks_once(_one_booth_per_interchange(matched))
    return [charge for charge in once_per_network if _paid_where_route_uses_ramp(charge, once_per_network)]


def _dataset_url() -> str:
    """The dataset's current address, versioned on the site's front page."""
    try:
        page = download(SITE).decode("utf-8", "replace")
    except FeedUnavailable:
        return UNVERSIONED_DATASET_URL
    found = DATASET_RE.search(page)
    return SITE.rstrip("/") + found.group() if found else UNVERSIONED_DATASET_URL


def _matched(route: Polyline, stations: list[TollStation]):
    for station in stations:
        if station.upcoming:
            continue
        hit = route.closest_hit(station.point, station.reach_m)
        if hit is None:
            continue
        margin = _direction_margin(route, hit.segment, station)
        if margin is not None:
            yield TollCharge(station, hit.segment, route.km_at(hit.segment), margin)


def _direction_margin(route: Polyline, segment: int, station: TollStation) -> float | None:
    """How much closer the route's heading is to the station's direction than to the opposite one;
    None when the route goes the other way. Stations that charge both directions always match."""
    if station.direction not in DIRECTION_BEARINGS:
        return 0.0
    declared = DIRECTION_BEARINGS[station.direction]
    heading = _mainline_heading(route, segment, station.role)
    margin = angle_between(heading, (declared + 180) % 360) - angle_between(heading, declared)
    return margin if margin > 0 else None


def _mainline_heading(route: Polyline, segment: int, role: str | None) -> float:
    """The motorway's heading near a booth. On the ramp itself a loop can point anywhere, so read it
    over the kilometre the driver merges into (entry) or arrived on (exit, and mainline plazas)."""
    if role == "entry":
        ahead = route.index_after(segment, MAINLINE_WALK_KM)
        if route.km_at(ahead) - route.km_at(segment) >= MIN_WALK_KM:
            return route.bearing_between(segment, ahead)
    else:
        behind = route.index_before(segment, MAINLINE_WALK_KM)
        if route.km_at(segment) - route.km_at(behind) >= MIN_WALK_KM:
            return route.bearing_between(behind, segment)
    return route.bearing_between(segment - 2, segment + 3)


def _one_booth_per_interchange(charges: list[TollCharge]) -> list[TollCharge]:
    """Of two side booths at one interchange, the driver went through the one whose direction fits best."""
    kept: list[TollCharge] = []
    for charge in charges:
        previous = kept[-1] if kept else None
        if (previous and charge.station.kind == "side" and previous.station.kind == "side"
                and charge.km - previous.km < SAME_INTERCHANGE_KM):
            if charge.direction_margin > previous.direction_margin:
                kept[-1] = charge
            continue
        kept.append(charge)
    return kept


def _charge_networks_once(charges: list[TollCharge]) -> list[TollCharge]:
    seen = set()
    kept = []
    for charge in charges:
        group = charge.station.charge_once_group
        if group in seen:
            continue
        if group:
            seen.add(group)
        kept.append(charge)
    return kept


def _paid_where_route_uses_ramp(charge: TollCharge, charges: list[TollCharge]) -> bool:
    """A side booth is paid only where the route joins its motorway (first on it, an entry) or leaves
    it (last on it, an exit). Mid-run, the route only drove past the interchange."""
    station = charge.station
    if station.kind != "side":
        return True
    same_highway = [other for other in charges if other.station.highway == station.highway]
    is_first, is_last = same_highway[0] is charge, same_highway[-1] is charge
    if is_first and is_last:
        return True
    if is_first:
        return station.role == "entry"
    if is_last:
        return station.role == "exit"
    return False
