"""Where the person is: the latest location they shared on Telegram. The Telegram front desk keeps
it in <locations>/<chat id>.json (see settings.py) and, while a live location runs, updates it
with every move: {"latitude", "longitude", "updated" (unix time), "live_until", "accuracy_m"}."""
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


def latest(folder: Path, chat: str | None) -> SharedLocation | None:
    if not chat:
        return None
    try:
        saved = json.loads((folder / f"{chat}.json").read_text())
    except (OSError, ValueError):
        return None
    return SharedLocation(Point(saved["latitude"], saved["longitude"]), saved["updated"],
                          saved.get("live_until"), saved.get("accuracy_m"))
