"""Driving routes from Google's Routes API, with each step's distance and time so the car's
consumption can follow the speed of the road. Google's terms ask answers that use it to link to
Google Maps, so a route carries its link."""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from functools import cached_property
from urllib.parse import urlencode

from .car import Car
from .geo import Point, Polyline, decode_polyline

ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = (
    "routes.distanceMeters,routes.duration,routes.description,routes.legs.startLocation,routes.legs.endLocation,"
    "routes.legs.steps.distanceMeters,routes.legs.steps.staticDuration,routes.legs.steps.polyline.encodedPolyline")
TIMEOUT = 30


class RoutesUnavailable(Exception):
    pass


class NoRoute(Exception):
    pass


@dataclass(frozen=True)
class Waypoint:
    label: str
    point: Point | None = None
    address: str | None = None

    def for_google(self) -> dict:
        if self.point:
            return {"location": {"latLng": {"latitude": self.point.lat, "longitude": self.point.lon}}}
        return {"address": self.address}

    def for_maps_link(self) -> str:
        return str(self.point) if self.point else self.address


@dataclass(frozen=True)
class RouteRequest:
    start: Waypoint
    end: Waypoint
    via: tuple[Waypoint, ...] = ()
    avoid_tolls: bool = False

    def reversed(self) -> "RouteRequest":
        return RouteRequest(self.end, self.start, tuple(reversed(self.via)), self.avoid_tolls)


@dataclass(frozen=True)
class Step:
    meters: int
    seconds: int
    points: list[Point]

    @property
    def kmh(self) -> float:
        return self.meters / self.seconds * 3.6 if self.seconds else 0.0


@dataclass
class Route:
    request: RouteRequest
    meters: int
    seconds: int  # with the traffic Google expects now
    description: str  # the main road, e.g. "A1"
    start: Point
    end: Point
    steps: list[Step] = field(repr=False)

    @cached_property
    def polyline(self) -> Polyline:
        return Polyline(self._track[0])

    @cached_property
    def segment_kmh(self) -> list[float]:
        """The average speed of the step each polyline segment belongs to."""
        return self._track[1]

    def litres_along(self, car: Car) -> list[float]:
        """Litres burned from the start to each point of the polyline."""
        burned = [0.0]
        meters = self.polyline.cumulative_m
        for segment, kmh in enumerate(self.segment_kmh):
            burned.append(burned[-1] + (meters[segment + 1] - meters[segment]) / 100_000 * car.litres_per_100km(kmh))
        return burned

    def maps_link(self, stops: list[Point] = ()) -> str:
        """The route in Google Maps, through the given stops (fuel stations) and the requested via points."""
        waypoints = [waypoint.for_maps_link() for waypoint in self.request.via] + [str(stop) for stop in stops]
        query = {"api": 1, "origin": self.request.start.for_maps_link(),
                 "destination": self.request.end.for_maps_link(), "travelmode": "driving"}
        if waypoints:
            query["waypoints"] = "|".join(waypoints)
        if self.request.avoid_tolls:
            query["avoid"] = "tolls"
        return "https://www.google.com/maps/dir/?" + urlencode(query)

    @cached_property
    def _track(self) -> tuple[list[Point], list[float]]:
        points: list[Point] = []
        kmh: list[float] = []
        for step in self.steps:
            new_points = step.points[1:] if points and step.points and step.points[0] == points[-1] else step.points
            for point in new_points:
                if points:
                    kmh.append(step.kmh)
                points.append(point)
        return points, kmh


class GoogleRoutes:
    def __init__(self, key: str | None):
        self.key = key

    def drive(self, request: RouteRequest) -> Route:
        body = {
            "origin": request.start.for_google(), "destination": request.end.for_google(),
            "intermediates": [waypoint.for_google() for waypoint in request.via],
            "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE", "polylineQuality": "HIGH_QUALITY",
            "routeModifiers": {"avoidTolls": request.avoid_tolls}, "languageCode": "en", "regionCode": "GR"}
        routes = self._post(body).get("routes") or []
        if not routes:
            raise NoRoute(f"Google found no driving route from {request.start.label} to {request.end.label}")
        return route_from_google(routes[0], request)

    def _post(self, body: dict) -> dict:
        if not self.key:
            raise RoutesUnavailable("no Google Maps key: add a Maps MCP server or set GOOGLE_MAPS_API_KEY")
        headers = {"Content-Type": "application/json", "X-Goog-Api-Key": self.key, "X-Goog-FieldMask": FIELD_MASK}
        http_request = urllib.request.Request(ROUTES_URL, json.dumps(body).encode(), headers)
        try:
            with urllib.request.urlopen(http_request, timeout=TIMEOUT) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            message = error.read().decode("utf-8", "replace")
            if error.code in (400, 404):
                raise NoRoute(f"Google couldn't route this: {message[:300]}") from error
            raise RoutesUnavailable(f"Google Routes API: HTTP {error.code} {message[:300]}") from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise RoutesUnavailable(f"Google Routes API: {error}") from error


def route_from_google(route: dict, request: RouteRequest) -> Route:
    legs = route.get("legs") or []
    steps = [Step(int(step.get("distanceMeters", 0)), _seconds(step.get("staticDuration", "0s")),
                  decode_polyline(step.get("polyline", {}).get("encodedPolyline", "")))
             for leg in legs for step in leg.get("steps", [])]
    return Route(request=request, meters=int(route["distanceMeters"]), seconds=_seconds(route["duration"]),
                 description=route.get("description", ""),
                 start=_point(legs[0]["startLocation"]), end=_point(legs[-1]["endLocation"]), steps=steps)


def _seconds(duration: str) -> int:
    return int(float(duration.rstrip("s") or 0))


def _point(location: dict) -> Point:
    return Point(location["latLng"]["latitude"], location["latLng"]["longitude"])
