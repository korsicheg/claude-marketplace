"""What the user calls a place: "here" (their latest shared position), a saved place such as "home",
"lat,lon", or anything else, which Google looks up as an address or a place name.

The latest position is a JSON file (settings.TRIP_LOCATION) that whatever receives it from their phone
rewrites with every move while a live location runs: {"latitude", "longitude", "updated" (unix time),
"live_until" (unix time, optional)}."""
import json
import re
import time

from .geo import Point
from .routes import Waypoint
from .settings import Settings

COORDINATES_RE = re.compile(r"\s*(?P<lat>-?\d{1,2}\.\d+)\s*[,\s]\s*(?P<lon>-?\d{1,3}\.\d+)\s*")
HERE = "here"
LOCATION_MAX_AGE_S = 30 * 60


class NoLocation(Exception):
    """The user hasn't shared a recent location, so "here" means nothing."""


def waypoint(text: str, settings: Settings) -> Waypoint:
    name = text.strip()
    if name.lower() == HERE:
        return Waypoint("your location", latest_location(settings))
    saved = saved_places(settings).get(name.lower())
    if saved:
        return Waypoint(name, Point(saved["lat"], saved["lon"]))
    coordinates = COORDINATES_RE.fullmatch(name)
    if coordinates:
        return Waypoint(name, Point(float(coordinates["lat"]), float(coordinates["lon"])))
    return Waypoint(name, address=name)


def saved_places(settings: Settings) -> dict:
    try:
        return {name.lower(): place for name, place in json.loads(settings.saved_places.read_text()).items()}
    except (OSError, ValueError):
        return {}


def latest_location(settings: Settings) -> Point:
    path = settings.latest_location
    try:
        location = json.loads(path.read_text()) if path else None
    except (OSError, ValueError):
        location = None
    if not location:
        raise NoLocation("no shared location (TRIP_LOCATION)")
    still_live = location.get("live_until", 0) > time.time()
    if not still_live and time.time() - location.get("updated", 0) > LOCATION_MAX_AGE_S:
        raise NoLocation("the latest shared location is over 30 minutes old")
    return Point(location["latitude"], location["longitude"])
