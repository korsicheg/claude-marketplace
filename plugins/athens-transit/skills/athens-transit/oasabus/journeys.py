"""Getting somewhere on any Athens transport: Google's journeys with live bus times, best first.
Journeys that differ only in time fold into one, with the later departures as "also at"."""
from dataclasses import dataclass, field
from datetime import datetime

from .geo import Point
from .live import LiveBuses
from .planner import line_key
from .transit import GoogleTransit, Journey

OPTIONS_SHOWN = 3


@dataclass
class Option:
    journey: Journey
    also: list[datetime] = field(default_factory=list)  # later departures of the same first ride


class JourneyPlanner:
    def __init__(self, transit: GoogleTransit, live: LiveBuses):
        self.transit = transit
        self.live = live

    def plan(self, origin: Point, destination: Point, line: str | None = None) -> list[Option]:
        journeys = self.transit.journeys(origin, destination)
        if line:
            journeys = [j for j in journeys if any(line_key(r.line) == line_key(line) for r in j.rides)]
        journeys = sorted(self.live.update_all(journeys), key=lambda j: j.arrives)
        options: dict[tuple, Option] = {}
        for journey in journeys:
            if journey.shape in options:
                options[journey.shape].also.append(journey.rides[0].departs)
            else:
                options[journey.shape] = Option(journey)
        return list(options.values())[:OPTIONS_SHOWN]
