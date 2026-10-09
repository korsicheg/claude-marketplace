"""OASA's live predictions in Google's journeys. Google only knows the timetable, so each bus or
trolley ride gets the first bus the rider can still catch at that stop, as OASA predicts it."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta

from .planner import RideOption, athens_now, line_key, stops_away
from .telematics import OasaUnavailable, Telematics
from .transit import Journey, Ride, Walk

STOP_MATCH_M = 120  # Google and OASA place the same stop a little apart


@dataclass(frozen=True)
class LiveSource:
    """Where OASA predicts a ride's buses: one stop, the routes of that line through it."""
    stop_code: str
    route_codes: tuple[int, ...]
    option: RideOption  # the matched route, for where its buses are


class LiveBuses:
    def __init__(self, oasa: Telematics):
        self.oasa = oasa

    def update_all(self, journeys: list[Journey]) -> list[Journey]:
        with ThreadPoolExecutor(max_workers=6) as pool:
            return list(pool.map(self.update, journeys))

    def update(self, journey: Journey) -> Journey:
        """The journey with live departures for its bus and trolley rides, leaving now."""
        now = athens_now()
        reached = now  # when the rider gets to the next leg
        ride_index = 0
        for leg in journey.legs:
            if isinstance(leg, Walk):
                reached += timedelta(minutes=leg.minutes)
                continue
            ride = self.live_ride_or_none(leg, now, reached) if leg.is_oasa_bus else None
            if ride:
                journey = journey.with_ride(ride_index, ride)
            reached = journey.rides[ride_index].arrives
            ride_index += 1
        return journey

    def live_ride_or_none(self, ride: Ride, now: datetime, reached: datetime) -> Ride | None:
        """The ride on the first bus OASA predicts the rider can catch; None keeps the timetable's."""
        try:
            return self.live_ride(ride, now, reached)
        except OasaUnavailable:
            return None

    def live_ride(self, ride: Ride, now: datetime, reached: datetime) -> Ride | None:
        source = self.source(ride)
        if not source:
            return None
        arrivals = sorted((a for a in self.oasa.arrivals(source.stop_code) if a.route_code in source.route_codes),
                          key=lambda a: a.minutes)
        catchable = [a for a in arrivals if now + timedelta(minutes=a.minutes) >= reached]
        if not catchable:
            return None
        bus = catchable[0]
        positions = {b.vehicle: b for b in self.oasa.buses(source.option.route.code)}
        return ride.with_live_departure(now + timedelta(minutes=bus.minutes),
                                        stops_away(source.option, positions.get(bus.vehicle)))

    def source(self, ride: Ride) -> LiveSource | None:
        """The OASA stop and routes behind a ride Google planned, matched by line and position."""
        matches = []
        for line in self.oasa.lines():
            if line_key(line.number) != line_key(ride.line):
                continue
            for route in self.oasa.routes(line.code):
                stops = tuple(self.oasa.stops(route.code))
                board = nearest(stops, ride.board_point)
                alight = nearest(stops, ride.alight_point)
                if board and alight and board.order < alight.order:
                    matches.append(RideOption(route, stops, board, alight))
        if not matches:
            return None
        stop_code = matches[0].board.code
        routes = tuple(m.route.code for m in matches if m.board.code == stop_code)
        return LiveSource(stop_code, routes, matches[0])


def nearest(stops, point):
    closest = min(stops, key=lambda stop: stop.point.meters_to(point), default=None)
    return closest if closest and closest.point.meters_to(point) <= STOP_MATCH_M else None

