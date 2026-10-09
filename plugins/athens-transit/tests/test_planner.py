from datetime import datetime, timedelta

import pytest
from fakes import EAST, EASTBOUND, NIGHT, FakeTelematics, arrival, bus_at
from oasabus.geo import Point
from oasabus.maps import Place, Walk
from oasabus.planner import (
    ATHENS,
    ComingBus,
    LineNotFound,
    LinePlanner,
    RideOption,
    Trip,
    line_key,
    preference,
    runs_at,
)


class FakeMaps:
    def walk(self, start, end):
        meters = round(start.meters_to(end))
        return Walk(meters, meters / 75, "https://maps/walk", False)


def place(point):
    return Place("somewhere", point, "https://maps/place")


def planner(**fake):
    return LinePlanner(FakeTelematics(**fake), FakeMaps())


def test_line_numbers_match_however_they_are_typed():
    assert line_key("a1") == line_key("Α1") == line_key("A1")
    assert line_key("40") == line_key("040")
    assert line_key("11") != line_key("110")


def test_a_route_with_hours_in_its_name_runs_only_then():
    at = lambda hhmm: datetime(2026, 10, 9, int(hhmm[:2]), int(hhmm[3:]), tzinfo=ATHENS)
    assert runs_at(NIGHT, at("01:00")) and not runs_at(NIGHT, at("09:00"))
    assert runs_at(EASTBOUND, at("09:00"))


def test_the_direction_that_reaches_the_destination_is_chosen():
    options = planner().ride_options("A1", EAST[1].point, EAST[8].point)
    assert {o.route.code for o in options} == {1}
    assert options[0].board == EAST[1] and options[0].alight == EAST[8]

    back = planner().ride_options("A1", EAST[8].point, EAST[1].point)
    assert {o.route.code for o in back} == {2}


def test_nearby_stops_are_compared_but_not_far_ones():
    between = Point(37.97, (EAST[2].point.lon + EAST[3].point.lon) / 2)
    options = planner().ride_options("A1", between, EAST[9].point)
    assert {o.board.code for o in options} == {"E3", "E4"}


def test_an_unknown_line_is_reported():
    with pytest.raises(LineNotFound):
        planner().ride_options("999", EAST[0].point, EAST[5].point)


def test_live_buses_come_first_with_where_they_are():
    fake = {"arrivals": {"E3": [arrival(7, "V2"), arrival(2, "V1"), arrival(5, "X", route=9)]},
                "buses": [bus_at("V1", 0)]}
    trip = planner(**fake).plan("A1", place(EAST[2].point), place(EAST[8].point))
    assert [(b.minutes, b.vehicle, b.stops_away) for b in trip.buses] == [(2, "V1", 2), (7, "V2", None)]
    assert trip.at_stop and trip.next_bus.vehicle == "V1"


def test_a_bus_you_cannot_reach_in_time_is_skipped():
    trip = trip_with([ComingBus(3, True, "V1"), ComingBus(12, True, "V2")], walk_min=5)
    assert trip.missed == [ComingBus(3, True, "V1")]
    assert trip.next_bus.vehicle == "V2"
    assert trip.leave_in == 12 - 5 - 1


def test_live_predictions_beat_timetable_guesses():
    live = trip_with([ComingBus(9, True, "V1")], walk_min=2)
    guess = trip_with([ComingBus(4, False)], walk_min=2)
    assert min([guess, live], key=preference) is live


def trip_with(buses, walk_min):
    option = RideOption(EASTBOUND, tuple(EAST), EAST[1], EAST[8], (1,))
    walk = Walk(round(walk_min * 75), walk_min, "u", False)
    planned = datetime(2026, 10, 9, 9, 0, tzinfo=ATHENS)
    return Trip("Α1", option, place(EAST[0].point), place(EAST[9].point), walk, Walk(100, 1.3, "u", False),
                10.0, buses, planned)


def test_the_arrival_adds_the_wait_the_ride_and_the_last_walk():
    trip = trip_with([ComingBus(10, True, "V1")], walk_min=4)
    assert trip.arrival == trip.planned_at + timedelta(minutes=10 + 10 + 1.3)
