import pytest
from tripcost.car import Car
from tripcost.fuel import FuelStation, StationFilter, StationOnRoute
from tripcost.geo import Point
from tripcost.planner import FuelPlanner, RouteFuel, Tank

CAR = Car(tank_l=40.0, reserve_l=5.0)
WANTED = StationFilter(("EKO", "BP"), "u95")
START_PRICE = 2.0


def route(litres: float, *stations: tuple) -> RouteFuel:
    """A route burning a litre every 20 km, with stations given as (litres burned there, price[, brand])."""
    litres_along = [float(litre) for litre in range(int(litres) + 1)]
    km_along = [litre * 20 for litre in litres_along]
    on_route = [StationOnRoute(fuel_station(f"at {at}", *brand), price, at * 20, at, 0.0)
                for at, price, *brand in stations]
    return RouteFuel(km_along, litres_along, on_route)


def fuel_station(name: str, brand: str = "EKO") -> FuelStation:
    return FuelStation(id=name, brand=brand, name=name, address=name, point=Point(38.0, 23.0),
                       prices={}, price_date="2026-10-09", maps_url="")


def test_no_stop_when_the_tank_reaches_the_end_with_its_reserve():
    tank = Tank(CAR.tank_l, START_PRICE)
    plan = FuelPlanner(CAR, WANTED).plan(route(30, (10, 1.5)), tank)
    assert plan.stops == []
    assert plan.cost == pytest.approx(30 * START_PRICE)
    assert tank.litres == pytest.approx(10)


def test_stops_at_the_cheapest_station_once_the_tank_is_half_empty():
    # The tank runs low after 35 L; half empty from 15 L: the 1.5 at 10 L is too early, 2.5 at 40 L too late.
    plan = FuelPlanner(CAR, WANTED).plan(route(50, (10, 1.5), (20, 2.2), (30, 2.1), (40, 2.5)), Tank(CAR.tank_l, START_PRICE))
    [stop] = plan.stops
    assert stop.stop.litres_at == 30
    assert stop.litres == pytest.approx(30)  # filled up from 10 L left
    assert plan.cost == pytest.approx(30 * START_PRICE + 20 * 2.1)


def test_of_equally_cheap_stations_stops_at_the_later_one():
    plan = FuelPlanner(CAR, WANTED).plan(route(50, (20, 2.1), (30, 2.1)), Tank(CAR.tank_l, START_PRICE))
    assert [stop.stop.litres_at for stop in plan.stops] == [30]


def test_says_where_the_tank_runs_low_without_a_wanted_station():
    tank = Tank(CAR.tank_l, START_PRICE)
    plan = FuelPlanner(CAR, WANTED).plan(route(50), tank)
    assert plan.stops == []
    assert plan.runs_low_km == pytest.approx(35 * 20)
    assert plan.cost == pytest.approx(50 * START_PRICE)
    assert tank.litres == pytest.approx(CAR.tank_l - 15)


def test_a_low_tank_stops_early():
    plan = FuelPlanner(CAR, WANTED).plan(route(20, (3, 2.2), (15, 1.9)), Tank(8.0, START_PRICE))
    assert [stop.stop.litres_at for stop in plan.stops] == [3]


def test_stops_at_the_preferred_brand_with_the_other_as_the_alternative():
    plan = FuelPlanner(CAR, WANTED).plan(route(50, (25, 2.0, "BP"), (30, 2.1, "EKO"), (32, 2.05, "BP")),
                                         Tank(CAR.tank_l, START_PRICE))
    [stop] = plan.stops
    assert (stop.stop.station.brand, stop.stop.litres_at) == ("EKO", 30)
    assert (stop.alternative.station.brand, stop.alternative.price) == ("BP", 2.0)


def test_without_brand_preferences_it_stops_at_the_cheapest_of_any_brand():
    anyone = StationFilter((), "u95")
    plan = FuelPlanner(CAR, anyone).plan(route(50, (25, 2.0, "BP"), (30, 2.1, "EKO"), (32, 1.9, "SHELL")),
                                         Tank(CAR.tank_l, START_PRICE))
    [stop] = plan.stops
    assert (stop.stop.station.brand, stop.stop.price) == ("SHELL", 1.9)
