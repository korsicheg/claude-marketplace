"""Google Maps through the endpoint of the person's Maps MCP server (Maps Grounding Lite), called
with the same key, so scripts need no Claude. Google's terms ask answers that use it to link to
Google Maps, so places and walks carry their link."""
import json
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlencode

from .geo import Point, estimated_walk_minutes
from .settings import MAPS_ENDPOINT

ATHENS_CENTER = Point(37.9838, 23.7275)
SEARCH_RADIUS_M = 50_000  # Attica
TIMEOUT = 15


class MapsUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Place:
    name: str
    point: Point
    url: str


@dataclass(frozen=True)
class Walk:
    meters: int
    minutes: float
    url: str
    estimated: bool  # Google didn't answer; straight-line distance with a detour factor


def walking_directions_url(start: Point, end: Point) -> str:
    return "https://www.google.com/maps/dir/?" + urlencode(
        {"api": 1, "origin": str(start), "destination": str(end), "travelmode": "walking"})


def place_url(point: Point) -> str:
    return "https://www.google.com/maps/search/?" + urlencode({"api": 1, "query": str(point)})


class GoogleMaps:
    def __init__(self, headers: dict):
        self.headers = headers  # X-Goog-Api-Key, and any other headers of the person's server

    def find_place(self, query: str) -> Place | None:
        found = self.call_tool("search_places", {
            "textQuery": query, "pageSize": 1,
            "locationBias": {"circle": {"center": {"latitude": ATHENS_CENTER.lat, "longitude": ATHENS_CENTER.lon},
                                        "radiusMeters": SEARCH_RADIUS_M}}})
        places = found.get("places") or []
        if not places:
            return None
        place = places[0]
        name = place.get("attribution", {}).get("title", query).removesuffix(" - Google Maps")
        point = Point(place["location"]["latitude"], place["location"]["longitude"])
        return Place(name, point, place.get("googleMapsLinks", {}).get("placeUrl") or place_url(point))

    def walk(self, start: Point, end: Point) -> Walk:
        """Google's walking distance and time, or an estimate when Google doesn't answer."""
        url = walking_directions_url(start, end)
        try:
            routes = self.call_tool("compute_routes", {
                "origin": {"latLng": {"latitude": start.lat, "longitude": start.lon}},
                "destination": {"latLng": {"latitude": end.lat, "longitude": end.lon}},
                "travelMode": "WALK"}).get("routes") or []
            route = routes[0]
            return Walk(int(route["distanceMeters"]), int(route["duration"].rstrip("s")) / 60, url, False)
        except (MapsUnavailable, LookupError, ValueError):
            meters = round(start.meters_to(end))
            return Walk(meters, estimated_walk_minutes(start, end), url, True)

    def call_tool(self, name: str, arguments: dict) -> dict:
        if "X-Goog-Api-Key" not in self.headers:
            raise MapsUnavailable("no Google Maps key: add a Maps MCP server or set GOOGLE_MAPS_API_KEY")
        request = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", **self.headers}
        try:
            with urllib.request.urlopen(urllib.request.Request(MAPS_ENDPOINT, json.dumps(request).encode(), headers),
                                        timeout=TIMEOUT) as response:
                answer = json.loads(response.read())
        except (OSError, ValueError) as e:
            raise MapsUnavailable(f"Google Maps {name}: {e}") from e
        result = answer.get("result") or {}
        if "error" in answer or result.get("isError"):
            raise MapsUnavailable(f"Google Maps {name}: {answer.get('error') or result.get('content')}")
        return result.get("structuredContent") or {}
