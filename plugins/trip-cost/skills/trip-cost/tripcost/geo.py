"""Points on the map, and a route drawn as a polyline that can say how far a point lies from it."""
import math
from collections import defaultdict
from itertools import pairwise
from typing import NamedTuple

EARTH_RADIUS_M = 6_371_000
METERS_PER_DEGREE_LAT = 110_574
METERS_PER_DEGREE_LON_AT_EQUATOR = 111_320
GRID_CELL_DEGREES = 0.02  # about 2 km: a lookup reads only the cells around the point


class Point(NamedTuple):
    lat: float
    lon: float

    def meters_to(self, other: "Point") -> float:
        lat1, lon1, lat2, lon2 = map(math.radians, (self.lat, self.lon, other.lat, other.lon))
        h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))

    def bearing_to(self, other: "Point") -> float:
        """The compass heading from here to the other point, 0-360 degrees."""
        lat1, lon1, lat2, lon2 = map(math.radians, (self.lat, self.lon, other.lat, other.lon))
        y = math.sin(lon2 - lon1) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
        return (math.degrees(math.atan2(y, x)) + 360) % 360

    def __str__(self) -> str:
        return f"{self.lat:.6f},{self.lon:.6f}"


def angle_between(bearing: float, other: float) -> float:
    """The smaller angle between two compass headings, 0-180 degrees."""
    difference = abs(bearing - other) % 360
    return 360 - difference if difference > 180 else difference


def decode_polyline(encoded: str) -> list[Point]:
    """Google's encoded polyline format, five decimals."""
    points, values, index = [], [], 0
    while index < len(encoded):
        shift = result = 0
        while True:
            byte = ord(encoded[index]) - 63
            index += 1
            result |= (byte & 0x1F) << shift
            shift += 5
            if byte < 0x20:
                break
        values.append(~(result >> 1) if result & 1 else result >> 1)
    lat = lon = 0
    for dlat, dlon in zip(values[::2], values[1::2]):
        lat += dlat
        lon += dlon
        points.append(Point(lat / 1e5, lon / 1e5))
    return points


class Hit(NamedTuple):
    """Where a point lies relative to the polyline."""
    segment: int  # the segment from points[segment] to points[segment + 1]
    meters: float  # how far off the line
    on_right: bool  # on the right-hand side, going the way the line goes


class Polyline:
    def __init__(self, points: list[Point]):
        self.points = points
        self.cumulative_m = [0.0]
        for a, b in pairwise(points):
            self.cumulative_m.append(self.cumulative_m[-1] + a.meters_to(b))
        self._grid = self._segments_by_cell()

    @property
    def segment_count(self) -> int:
        return max(len(self.points) - 1, 0)

    def km_at(self, index: int) -> float:
        return self.cumulative_m[index] / 1000

    def hits(self, point: Point, reach_m: float) -> list[Hit]:
        """Every segment within reach of the point, in route order."""
        found = []
        for segment in sorted(self._segments_near(point, reach_m)):
            hit = self._hit(point, segment)
            if hit.meters <= reach_m:
                found.append(hit)
        return found

    def closest_hit(self, point: Point, reach_m: float) -> Hit | None:
        found = self.hits(point, reach_m)
        return min(found, key=lambda hit: hit.meters) if found else None

    def bearing_between(self, start: int, end: int) -> float:
        start, end = max(0, start), min(len(self.points) - 1, end)
        return self.points[start].bearing_to(self.points[end])

    def index_after(self, index: int, km: float) -> int:
        """The first point at least km further along the line, or the last point."""
        target = self.cumulative_m[index] + km * 1000
        while index < len(self.points) - 1 and self.cumulative_m[index] < target:
            index += 1
        return index

    def index_before(self, index: int, km: float) -> int:
        """The first point at least km back along the line, or the first point."""
        target = self.cumulative_m[index] - km * 1000
        while index > 0 and self.cumulative_m[index] > target:
            index -= 1
        return index

    def _hit(self, point: Point, segment: int) -> Hit:
        a, b = self.points[segment], self.points[segment + 1]
        ax, ay = _meters_from(point, a)
        bx, by = _meters_from(point, b)
        dx, dy = bx - ax, by - ay
        length_squared = dx * dx + dy * dy
        t = 0.0 if length_squared == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / length_squared))
        meters = math.hypot(ax + t * dx, ay + t * dy)
        # The point sits at the origin; its side is the sign of the cross product of the
        # segment's direction with the vector from a to the point.
        on_right = dx * (-ay) - dy * (-ax) < 0
        return Hit(segment, meters, on_right)

    def _segments_by_cell(self) -> dict[tuple[int, int], list[int]]:
        grid = defaultdict(list)
        for segment in range(self.segment_count):
            a, b = self.points[segment], self.points[segment + 1]
            for cell in _cells_between(min(a.lat, b.lat), max(a.lat, b.lat), min(a.lon, b.lon), max(a.lon, b.lon)):
                grid[cell].append(segment)
        return grid

    def _segments_near(self, point: Point, reach_m: float) -> set[int]:
        dlat = reach_m / METERS_PER_DEGREE_LAT
        dlon = reach_m / (METERS_PER_DEGREE_LON_AT_EQUATOR * math.cos(math.radians(point.lat)))
        cells = _cells_between(point.lat - dlat, point.lat + dlat, point.lon - dlon, point.lon + dlon)
        return {segment for cell in cells for segment in self._grid.get(cell, ())}


def _meters_from(origin: Point, point: Point) -> tuple[float, float]:
    """The point's east and north offsets from the origin, flat-earth: exact enough within a few km."""
    x = (point.lon - origin.lon) * METERS_PER_DEGREE_LON_AT_EQUATOR * math.cos(math.radians(origin.lat))
    y = (point.lat - origin.lat) * METERS_PER_DEGREE_LAT
    return x, y


def _cells_between(lat_low: float, lat_high: float, lon_low: float, lon_high: float) -> list[tuple[int, int]]:
    rows = range(math.floor(lat_low / GRID_CELL_DEGREES), math.floor(lat_high / GRID_CELL_DEGREES) + 1)
    columns = range(math.floor(lon_low / GRID_CELL_DEGREES), math.floor(lon_high / GRID_CELL_DEGREES) + 1)
    return [(row, column) for row in rows for column in columns]
