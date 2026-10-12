"""Places the person names: "here", a saved place such as "home" or "work", coordinates, or anything
Google Maps can find."""
import json
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from .geo import Point
from .location import SharedLocation
from .maps import GoogleMaps, Place, place_url

HERE = {"here", "me", "my location", "current location"}
# A one-off location older than this is probably not where the person is any more.
STALE_LOCATION_MIN = 30


class PlaceNotFound(Exception):
    pass


class LocationUnknown(PlaceNotFound):
    """No recent location shared."""


class SavedPlaces:
    def __init__(self, file: Path):
        self.file = file

    def all(self) -> dict[str, Place]:
        try:
            saved = json.loads(self.file.read_text())
        except (OSError, ValueError):
            return {}
        return {name: Place(p["name"], Point(p["lat"], p["lon"]), p["url"]) for name, p in saved.items()}

    def get(self, name: str) -> Place | None:
        return self.all().get(name.strip().lower())

    def save(self, name: str, place: Place) -> None:
        places = self.all() | {name.strip().lower(): place}
        self.write(places)

    def remove(self, name: str) -> bool:
        places = self.all()
        if places.pop(name.strip().lower(), None) is None:
            return False
        self.write(places)
        return True

    def write(self, places: dict[str, Place]) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        saved = {name: {"name": p.name, "lat": p.point.lat, "lon": p.point.lon, "url": p.url}
                 for name, p in sorted(places.items())}
        self.file.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n")


class PlaceFinder:
    def __init__(self, saved: SavedPlaces, maps: GoogleMaps, shared_location: Callable[[], SharedLocation | None]):
        self.saved = saved
        self.maps = maps
        self.shared_location = shared_location

    def find(self, where: str) -> Place:
        if where.strip().lower() in HERE:
            return self.here()
        point = Point.parse(where)
        if point:
            return Place(str(point), point, place_url(point))
        saved = self.saved.get(where)
        if saved:
            name = where.strip()
            return replace(saved, name=name[:1].upper() + name[1:])  # "Work", as the person calls it
        place = self.maps.find_place(where)
        if not place:
            raise PlaceNotFound(f"Google Maps found nothing for {where!r}")
        return place

    def here(self) -> Place:
        shared = self.shared_location()
        if not shared:
            raise LocationUnknown("no shared location (OASA_LOCATION)")
        now = time.time()
        if not shared.is_live(now) and now - shared.updated > STALE_LOCATION_MIN * 60:
            minutes = round((now - shared.updated) / 60)
            raise LocationUnknown(f"the last shared location is {minutes} min old")
        return Place("your location", shared.point, place_url(shared.point))
