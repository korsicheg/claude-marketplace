import pytest
from tripcost.geo import Point, Polyline, angle_between, decode_polyline


def test_decodes_googles_example_polyline():
    points = decode_polyline("_p~iF~ps|U_ulLnnqC_mqNvxq`@")
    assert points == [Point(38.5, -120.2), Point(40.7, -120.95), Point(43.252, -126.453)]


@pytest.mark.parametrize("a, b, expected", [(10, 350, 20), (0, 180, 180), (90, 90, 0), (270, 45, 135)])
def test_angle_between_headings(a, b, expected):
    assert angle_between(a, b) == pytest.approx(expected)


def northbound_line() -> Polyline:
    return Polyline([Point(38.0 + i * 0.001, 23.0) for i in range(101)])  # about 11 km due north


def test_a_point_east_of_a_northbound_line_is_on_its_right():
    hit = northbound_line().closest_hit(Point(38.05, 23.0005), 100)
    assert hit.on_right
    assert hit.meters == pytest.approx(44, abs=2)


def test_a_point_west_of_a_northbound_line_is_on_its_left():
    assert not northbound_line().closest_hit(Point(38.05, 22.9995), 100).on_right


def test_nothing_is_hit_out_of_reach():
    assert northbound_line().closest_hit(Point(38.05, 23.01), 500) is None


def test_hits_come_in_route_order():
    line = northbound_line()
    hits = line.hits(Point(38.05, 23.0), 300)
    assert len(hits) > 1 and [hit.segment for hit in hits] == sorted(hit.segment for hit in hits)


def test_walks_along_the_line():
    line = northbound_line()
    assert line.km_at(100) == pytest.approx(11.12, abs=0.01)
    assert line.km_at(line.index_after(10, 1.0)) - line.km_at(10) >= 1.0
    assert line.index_before(5, 5.0) == 0
    assert line.bearing_between(0, 100) == pytest.approx(0, abs=0.01)
