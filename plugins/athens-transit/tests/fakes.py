"""A small made-up line for the tests: route 1 runs west to east along a street, route 2 back."""
from oasabus.geo import Point
from oasabus.telematics import Arrival, Bus, Line, Route, Stop

LAT = 37.97


def stop(code, order, lon):
    return Stop(code, f"STOP {code}", Point(LAT, lon), order)


EAST = [stop(f"E{n}", n, 23.70 + n * 0.005) for n in range(1, 11)]  # ~440 m apart
WEST = [stop(f"W{n}", n, 23.70 + (11 - n) * 0.005) for n in range(1, 11)]
EASTBOUND = Route(1, 100, "WEST END - EAST END", True, 4000)
WESTBOUND = Route(2, 100, "EAST END - WEST END", False, 4000)
NIGHT = Route(3, 100, "WEST END - EAST END [00:30-05:00]", True, 4000)


class FakeTelematics:
    def __init__(self, arrivals=None, buses=None, departures=None):
        self.arrivals_by_stop = arrivals or {}
        self.bus_list = buses or []
        self.departures = departures or {True: [], False: []}

    def lines(self):
        return [Line(100, "Α1", "WEST END - EAST END"), Line(200, "040", "SOMEWHERE ELSE")]

    def routes(self, line_code):
        return [EASTBOUND, WESTBOUND, NIGHT] if line_code == 100 else []

    def stops(self, route_code):
        return {1: EAST, 2: WEST, 3: EAST}[route_code]

    def arrivals(self, stop_code):
        return self.arrivals_by_stop.get(stop_code, [])

    def buses(self, route_code):
        return list(self.bus_list)

    def todays_departures(self, line_code):
        return self.departures


def arrival(minutes, vehicle="V1", route=1):
    return Arrival(route, vehicle, minutes)


def bus_at(vehicle, stop_index):
    return Bus(vehicle, EAST[stop_index].point, None)
