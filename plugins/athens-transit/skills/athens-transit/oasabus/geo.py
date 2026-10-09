"""Points on the map and the distances between them."""
import math
import re
from typing import NamedTuple

EARTH_RADIUS_M = 6_371_000
# Streets aren't straight lines: a walk is about this much longer than the crow flies.
STREET_DETOUR = 1.3
WALK_METERS_PER_MIN = 75  # 4.5 km/h
COORDINATES_RE = re.compile(r"\s*(?P<lat>-?\d{1,2}\.\d+)\s*[,\s]\s*(?P<lon>-?\d{1,3}\.\d+)\s*")


class Point(NamedTuple):
    lat: float
    lon: float

    @classmethod
    def parse(cls, text: str) -> "Point | None":
        """A point written as "37.9755, 23.7348", or None."""
        m = COORDINATES_RE.fullmatch(text)
        return cls(float(m["lat"]), float(m["lon"])) if m else None

    def meters_to(self, other: "Point") -> float:
        lat1, lon1, lat2, lon2 = map(math.radians, (self.lat, self.lon, other.lat, other.lon))
        h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))

    def __str__(self) -> str:
        return f"{self.lat:.6f},{self.lon:.6f}"


def estimated_walk_minutes(start: Point, end: Point) -> float:
    return start.meters_to(end) * STREET_DETOUR / WALK_METERS_PER_MIN
