"""Fuel stations and their prices today.

Greek stations must report their prices to the Ministry of Development's observatory
(fuelprices.gr) twice a day. The fuelGR project publishes those prices, station by station with
positions and brands, as a JSON file updated twice a day: that file is the feed read here.
"""
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode

from .feeds import cached_download
from .geo import Point
from .routes import Route

FEED_URL = "https://github.com/athanasso/fuelGR-scraper/releases/latest/download/stations_latest.min.json"
FEED_FILE = "fuel-stations.json"
MAX_AGE_S = 3 * 3600
FUEL_NAMES = {"u95": "unleaded 95", "u98": "unleaded 98", "u100": "unleaded 100", "d": "diesel",
              "dp": "premium diesel", "lpg": "LPG", "cng": "CNG"}
BRAND_ALIASES = {"ECO": "EKO", "ΕΚΟ": "EKO", "ΒΡ": "BP"}  # what people type, and Greek letters

MOTORWAY_KMH = 90  # a step this fast is a motorway: only its own service areas are on the way
ROADSIDE_M = 150  # a service area sits right by the carriageway
OFF_ROUTE_M = 1_000  # on other roads a station this far off is a short detour


@dataclass(frozen=True)
class FuelStation:
    id: str
    brand: str
    name: str
    address: str
    point: Point
    prices: dict[str, float]
    price_date: str  # when the station last reported, YYYY-MM-DD
    maps_url: str

    @classmethod
    def from_feed(cls, record: dict) -> "FuelStation":
        point = Point(record["lat"], record["lng"])
        maps_url = record.get("mu") or "https://www.google.com/maps/search/?" + urlencode(
            {"api": 1, "query": str(point)})
        return cls(id=str(record["id"]), brand=normal_brand(record.get("b", "")), name=record.get("n", ""),
                   address=record.get("a", "").strip(), point=point, prices=record.get("p", {}),
                   price_date=record.get("dt", ""), maps_url=maps_url)


@dataclass(frozen=True)
class StationOnRoute:
    station: FuelStation
    price: float
    km: float  # how far along the route
    litres_at: float  # burned from the start of the route to there
    off_route_m: float


@dataclass(frozen=True)
class StationNearby:
    station: FuelStation
    price: float
    meters: float


@dataclass(frozen=True)
class StationFilter:
    brands: tuple[str, ...]  # by preference: the first brand wherever it can be, the next ones as alternatives;
    fuel: str                # none: every brand alike

    def price(self, station: FuelStation) -> float | None:
        return station.prices.get(self.fuel) if self.wants(station) else None

    def wants(self, station: FuelStation) -> bool:
        return not self.brands or station.brand in self.brands

    def rank(self, station: FuelStation) -> int:
        return self.brands.index(station.brand) if self.brands else 0

    def groups(self, stations: list) -> list[list]:
        """Stations (anything with a .station) by brand in order of preference; one group without brands."""
        if not self.brands:
            return [stations]
        return [[stop for stop in stations if stop.station.brand == brand] for brand in self.brands]


def normal_brand(name: str) -> str:
    upper = name.strip().upper()
    return BRAND_ALIASES.get(upper, upper)


def load_stations(data_folder: Path) -> list[FuelStation]:
    records = json.loads(cached_download(FEED_URL, data_folder / FEED_FILE, MAX_AGE_S))
    return [FuelStation.from_feed(record) for record in records if "lat" in record and "lng" in record]


def stations_on_route(route: Route, litres_along: list[float], stations: list[FuelStation],
                      wanted: StationFilter) -> list[StationOnRoute]:
    """The wanted stations a driver can pull into without leaving the route, in route order."""
    found = []
    for station in stations:
        price = wanted.price(station)
        if price is None:
            continue
        hit = route.polyline.closest_hit(station.point, OFF_ROUTE_M)
        if hit is None:
            continue
        on_motorway = route.segment_kmh[hit.segment] >= MOTORWAY_KMH
        if on_motorway and not (hit.on_right and hit.meters <= ROADSIDE_M):
            continue  # the other carriageway's service area, or off an exit
        found.append(StationOnRoute(station, price, route.polyline.km_at(hit.segment),
                                    litres_along[hit.segment], hit.meters))
    return sorted(found, key=lambda stop: stop.km)


def stations_near(point: Point, stations: list[FuelStation], wanted: StationFilter,
                  radius_m: float) -> list[StationNearby]:
    """The wanted stations within the radius, cheapest first, then nearest."""
    nearby = []
    for station in stations:
        price = wanted.price(station)
        if price is None:
            continue
        meters = point.meters_to(station.point)
        if meters <= radius_m:
            nearby.append(StationNearby(station, price, meters))
    return sorted(nearby, key=lambda found: (found.price, found.meters))
