import json
from pathlib import Path

from oasabus.geo import Point
from oasabus.transit import parse_journey

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "google-transit.json").read_text())
SYNTAGMA, KIFISIA = Point(37.9755, 23.7348), Point(38.0739, 23.8086)


def test_walks_merge_and_rides_keep_their_line_and_stops():
    metro = parse_journey(FIXTURE["routes"][0], SYNTAGMA, KIFISIA)
    assert [type(leg).__name__ for leg in metro.legs] == ["Walk", "Ride", "Ride", "Walk"]  # a same-station change has no walk
    first, second = metro.rides
    assert (first.mode, first.line, first.board) == ("metro", "M2", "Syntagma")
    assert (second.line, second.alight) == ("M1", "Kifissia")
    assert metro.leave_at < first.departs < second.departs < metro.arrives


def test_a_trolley_ride_is_one_oasa_can_make_live():
    trolley = parse_journey(FIXTURE["routes"][1], SYNTAGMA, KIFISIA).rides[0]
    assert trolley.mode == "trolley" and trolley.line == "1" and trolley.is_oasa_bus
