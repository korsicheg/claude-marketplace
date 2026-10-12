from tripcost.geo import Point, Polyline
from tripcost.tolls import TollStation, tolls_on_route

LON = 23.0


def northbound_motorway() -> Polyline:
    return Polyline([Point(38.0 + i * 0.001, LON) for i in range(101)])  # about 11 km due north


def station(id: str, lat: float, lon: float = LON, kind: str = "frontal", price: float = 1.0,
            highway: str = "A1", **details) -> TollStation:
    return TollStation(id=id, name=id, name_gr=id, highway=highway, operator="", kind=kind,
                       point=Point(lat, lon), price=price, **details)


def paid(*stations: TollStation) -> list[str]:
    return [charge.station.id for charge in tolls_on_route(northbound_motorway(), list(stations))]


def test_pays_frontal_plazas_on_the_way_in_route_order():
    assert paid(station("north", 38.08), station("south", 38.03)) == ["south", "north"]


def test_ignores_plazas_far_off_the_route():
    assert paid(station("elsewhere", 38.05, lon=LON + 0.05)) == []


def test_ignores_upcoming_plazas():
    assert paid(station("soon", 38.05, upcoming=True)) == []


def test_pays_a_ramp_booth_where_the_route_joins_the_motorway():
    entry = station("entry", 38.002, kind="side", direction="northbound", role="entry")
    assert paid(entry, station("plaza", 38.05)) == ["entry", "plaza"]


def test_ignores_a_ramp_booth_for_the_other_direction():
    southbound_exit = station("other way", 38.03, kind="side", direction="southbound", role="exit")
    assert paid(southbound_exit, station("plaza", 38.05)) == ["plaza"]


def test_ignores_a_ramp_booth_the_route_only_drives_past():
    exit_on_the_way = station("passed", 38.06, kind="side", direction="northbound", role="exit")
    assert paid(station("plaza", 38.05), exit_on_the_way, station("next plaza", 38.09)) == ["plaza", "next plaza"]


def test_ignores_a_ramp_booth_a_hundred_metres_off_the_motorway():
    ramp = station("ramp", 38.07, lon=LON + 0.00112, kind="side", direction="northbound", role="exit")
    assert paid(station("plaza", 38.05), ramp) == ["plaza"]


def test_a_plaza_before_a_ramp_booth_keeps_its_place_even_within_reach_of_it():
    """A frontal plaza 1.5 km after a ramp booth is in reach of the route before the booth: it is
    still paid after it, so the booth stays the last on the motorway and its exit is paid."""
    plaza, ramp = station("plaza", 38.05), station("ramp", 38.065, kind="side", direction="northbound", role="exit")
    assert paid(plaza, ramp) == ["plaza", "ramp"]


def test_a_flat_rate_network_charges_once():
    first = station("first", 38.02, highway="A6", charge_once_group="attiki", direction="northbound")
    second = station("second", 38.08, highway="A6", charge_once_group="attiki", direction="northbound")
    assert paid(first, second) == ["first"]


def test_a_one_way_plaza_charges_only_its_direction():
    assert paid(station("southbound plaza", 38.05, direction="southbound")) == []
