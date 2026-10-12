"""A ride on one named bus or trolley line: which way it should go, which stop to walk to, which
bus to catch there, and where to get off.

The stop isn't simply the nearest one: up to three nearby stops are compared by when the rider
would reach the destination, using OASA's live predictions for each (a farther stop can still win
when the bus reaches it sooner). Without predictions (at a terminus, or late at night) the
times come from today's timetable."""
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from itertools import pairwise

from .geo import Point
from .maps import GoogleMaps, Place, Walk
from .telematics import ATHENS, Bus, Route, Stop, Telematics

ROUTE_HOURS_RE = re.compile(r"\[(?P<start>\d\d:\d\d)-(?P<end>\d\d:\d\d)\]")
LATIN_TO_GREEK = str.maketrans("ABEZHIKMNOPTYX", "ΑΒΕΖΗΙΚΜΝΟΡΤΥΧ")
BOARDING_CANDIDATES = 3
CANDIDATE_EXTRA_M = 400  # a stop this much farther than the nearest is still worth comparing
TYPICAL_BUS_KMH = 15  # when today's timetable doesn't tell how long a trip takes
LEAVE_EARLY_MIN = 1  # be at the stop a minute before the bus
AT_STOP_M = 60
SCHEDULED_BUSES = 3
SAME_BUS_MIN = 2  # a timetable bus this soon after the last live one is probably that bus


class LineNotFound(Exception):
    pass


class NoRide(Exception):
    """The line doesn't go from near here to near there."""


def line_key(number: str) -> str:
    """What identifies a line however it's typed: "a1", "A1" and "Α1" (Greek) are the same, as
    are "40" and "040"."""
    return number.strip().upper().translate(LATIN_TO_GREEK).lstrip("0") or "0"


def athens_now() -> datetime:
    return datetime.now(ATHENS)


@dataclass(frozen=True)
class RideOption:
    route: Route
    stops: tuple[Stop, ...]
    board: Stop
    alight: Stop
    # Every route of the line from board to alight (a line can have variants, such as a night
    # route over the same stops); OASA predicts each bus under its own route.
    route_codes: tuple[int, ...] = ()

    @property
    def stop_count(self) -> int:
        return self.alight.order - self.board.order

    def share_of_route(self, start: Stop, end: Stop) -> float:
        """How much of the route lies between two of its stops, by distance."""
        def along(first, last):
            between = [s for s in self.stops if first.order <= s.order <= last.order]
            return sum(a.point.meters_to(b.point) for a, b in pairwise(between))
        whole = along(self.stops[0], self.stops[-1])
        return along(start, end) / whole if whole else 0.0

    @property
    def ride_share(self) -> float:
        return self.share_of_route(self.board, self.alight)

    @property
    def share_before_board(self) -> float:
        return self.share_of_route(self.stops[0], self.board)

    def straight_walking_m(self, origin: Point, destination: Point) -> float:
        return origin.meters_to(self.board.point) + self.alight.point.meters_to(destination)


@dataclass(frozen=True)
class ComingBus:
    minutes: float  # until it reaches the boarding stop
    live: bool  # OASA's prediction; False when it comes from the timetable
    vehicle: str | None = None
    stops_away: int | None = None


@dataclass
class Trip:
    line: str
    option: RideOption
    origin: Place
    destination: Place
    walk_to_stop: Walk
    walk_from_stop: Walk
    ride_minutes: float
    buses: list[ComingBus]
    planned_at: datetime = field(default_factory=athens_now)

    @property
    def at_stop(self) -> bool:
        return self.walk_to_stop.meters <= AT_STOP_M

    @property
    def walk_minutes(self) -> float:
        return 0.0 if self.at_stop else self.walk_to_stop.minutes

    @property
    def catchable(self) -> list[ComingBus]:
        return [bus for bus in self.buses if bus.minutes >= self.walk_minutes]

    @property
    def missed(self) -> list[ComingBus]:
        return [bus for bus in self.buses if bus.minutes < self.walk_minutes]

    @property
    def next_bus(self) -> ComingBus | None:
        return self.catchable[0] if self.catchable else None

    @property
    def leave_in(self) -> float | None:
        """Minutes until it's time to start walking (negative: hurry)."""
        if not self.next_bus:
            return None
        return self.next_bus.minutes - self.walk_minutes - LEAVE_EARLY_MIN

    @property
    def arrival(self) -> datetime | None:
        if not self.next_bus:
            return None
        return self.planned_at + timedelta(
            minutes=self.next_bus.minutes + self.ride_minutes + self.walk_from_stop.minutes)


class LinePlanner:
    def __init__(self, oasa: Telematics, maps: GoogleMaps):
        self.oasa = oasa
        self.maps = maps

    def plan(self, number: str, origin: Place, destination: Place) -> Trip:
        options = self.ride_options(number, origin.point, destination.point)
        number = self.line_number(options[0].route.line_code)
        with ThreadPoolExecutor(max_workers=8) as pool:
            walk_from = pool.submit(self.maps.walk, options[0].alight.point, destination.point)
            trips = [pool.submit(self.trip_from, option, number, origin, destination, walk_from)
                     for option in options]
            trips = [trip.result() for trip in trips]
        return min(trips, key=preference)

    def ride_options(self, number: str, origin: Point, destination: Point) -> list[RideOption]:
        """The boarding stops worth comparing, all on the route that fits the trip best."""
        lines = [line for line in self.oasa.lines() if line_key(line.number) == line_key(number)]
        if not lines:
            raise LineNotFound(f"no OASA bus or trolley line {number!r}")
        now = athens_now()
        stops_by_route = {route: tuple(self.oasa.stops(route.code))
                          for line in lines for route in self.oasa.routes(line.code) if runs_at(route, now)}
        by_route = [self.options_on(route, stops, origin, destination) for route, stops in stops_by_route.items()]
        by_route = [options for options in by_route if options]
        if not by_route:
            raise NoRide(f"line {number} doesn't run from near there towards that destination")
        best = min(by_route, key=lambda options: options[0].straight_walking_m(origin, destination))
        return [replace(option, route_codes=serving_routes(option, stops_by_route)) for option in best]

    def line_number(self, line_code: int) -> str:
        """The line's number as OASA writes it ("Α1" with a Greek Alpha)."""
        return next(line.number for line in self.oasa.lines() if line.code == line_code)

    def options_on(self, route: Route, stops: tuple[Stop, ...], origin: Point, destination: Point) -> list[RideOption]:
        if len(stops) < 2:
            return []
        alight = min(stops, key=lambda stop: stop.point.meters_to(destination))
        boards = sorted((stop for stop in stops if stop.order < alight.order),
                        key=lambda stop: stop.point.meters_to(origin))
        if not boards:
            return []
        reach = boards[0].point.meters_to(origin) + CANDIDATE_EXTRA_M
        nearby = [stop for stop in boards[:BOARDING_CANDIDATES] if stop.point.meters_to(origin) <= reach]
        return [RideOption(route, stops, board, alight) for board in nearby]

    def trip_from(self, option, number, origin, destination, walk_from_future) -> Trip:
        walk_to = self.maps.walk(origin.point, option.board.point)
        run_minutes = self.run_minutes(option.route)
        buses = self.coming_buses(option, run_minutes)
        return Trip(number, option, origin, destination, walk_to, walk_from_future.result(),
                    run_minutes * option.ride_share, buses)

    def coming_buses(self, option: RideOption, run_minutes: float) -> list[ComingBus]:
        """OASA's predictions for the boarding stop, then timetable buses after them."""
        live = [arrival for arrival in self.oasa.arrivals(option.board.code) if arrival.route_code in option.route_codes]
        positions = {bus.vehicle: bus for code in {arrival.route_code for arrival in live}
                     for bus in self.oasa.buses(code)}
        buses = [ComingBus(arrival.minutes, True, arrival.vehicle, stops_away(option, positions.get(arrival.vehicle)))
                 for arrival in sorted(live, key=lambda a: a.minutes)]
        last_live = buses[-1].minutes if buses else -1
        later = [minutes for minutes in self.scheduled_minutes(option, run_minutes)
                 if minutes > last_live + SAME_BUS_MIN]
        return buses + [ComingBus(minutes, False) for minutes in later[:SCHEDULED_BUSES]]

    def scheduled_minutes(self, option: RideOption, run_minutes: float) -> list[float]:
        """Minutes until today's scheduled buses reach the boarding stop."""
        now = athens_now()
        departures = self.oasa.todays_departures(option.route.line_code)[option.route.from_first_terminus]
        to_stop = timedelta(minutes=run_minutes * option.share_before_board)
        minutes = [(at(now, start) + to_stop - now).total_seconds() / 60 for start, _ in departures]
        return [m for m in minutes if m >= 0]

    def run_minutes(self, route: Route) -> float:
        """How long the scheduled trip nearest to now takes from end to end."""
        now = athens_now()
        trips = self.oasa.todays_departures(route.line_code)[route.from_first_terminus]
        if not trips:
            return route.length_m / 1000 / TYPICAL_BUS_KMH * 60
        start, end = min(trips, key=lambda trip: abs((at(now, trip[0]) - now).total_seconds()))
        minutes = (at(now, end) - at(now, start)).total_seconds() / 60
        return minutes if minutes > 0 else minutes + 24 * 60


def preference(trip: Trip) -> tuple:
    """Trips with a bus to catch first, live predictions before timetable guesses (the two can be
    the same bus), then the earliest arrival, then the shortest walk."""
    bus = trip.next_bus
    return (bus is None, bus is not None and not bus.live, trip.arrival or trip.planned_at, trip.walk_to_stop.meters)


def runs_at(route: Route, moment: datetime) -> bool:
    """OASA names a route that only runs part of the day with its hours: "… [22:00-06:00]"."""
    hours = ROUTE_HOURS_RE.search(route.name)
    if not hours:
        return True
    now, start, end = f"{moment:%H:%M}", hours["start"], hours["end"]
    return start <= now < end if start < end else now >= start or now < end


def serving_routes(option: RideOption, stops_by_route: dict[Route, tuple[Stop, ...]]) -> tuple[int, ...]:
    def serves(stops):
        order = {stop.code: stop.order for stop in stops}
        return order.get(option.board.code, 1_000) < order.get(option.alight.code, -1)
    return tuple(route.code for route, stops in stops_by_route.items() if serves(stops))


def at(day: datetime, hhmm: str) -> datetime:
    hours, minutes = map(int, hhmm.split(":"))
    return day.replace(hour=hours, minute=minutes, second=0, microsecond=0)


def stops_away(option: RideOption, bus: Bus | None) -> int | None:
    """How many stops before the boarding stop the bus is, judged by the stop nearest to it."""
    if not bus:
        return None
    nearest = min(option.stops, key=lambda stop: stop.point.meters_to(bus.point))
    gap = option.board.order - nearest.order
    return gap if gap >= 0 else None
