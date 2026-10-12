"""Where the person is: the latest position they shared from their phone, in the OASA_LOCATION file
(see settings.py), which whatever receives it rewrites with every move while a live location runs:
{"latitude", "longitude", "updated" (unix time), "live_until" (unix time, optional), "accuracy_m" (optional)}."""
import json
from dataclasses import dataclass
from pathlib import Path

from .geo import Point


@dataclass(frozen=True)
class SharedLocation:
    point: Point
    updated: float  # unix time of the last position
    live_until: float | None  # unix time a live location ends; None for a one-off location
    accuracy_m: float | None

    def is_live(self, now: float) -> bool:
        return self.live_until is not None and now < self.live_until


def latest(file: Path | None) -> SharedLocation | None:
    if not file:
        return None
    try:
        saved = json.loads(file.read_text())
    except (OSError, ValueError):
        return None
    return SharedLocation(Point(saved["latitude"], saved["longitude"]), saved["updated"],
                          saved.get("live_until"), saved.get("accuracy_m"))
