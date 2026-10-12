"""A whole trip: the route each way, the tolls it pays, where to fill up, and what it all costs.

Brands go by the person's preference, when they have one: where to fill up and where to stop is the
cheapest station of the preferred brand in reach, with the cheapest of the next brand as the alternative.
Without one, it's the cheapest station of any brand.

Fuel is costed at what the trip burns, each litre at the price of the station it came from: the tank
you leave with at the station you'd fill up at before leaving, and after a stop at that stop's
price. What's left in the tank at the end isn't the trip's cost.
"""
from bisect import bisect_left
from dataclasses import dataclass, field
from typing import NamedTuple

from .car import Car
from .fuel import FuelStation, StationFilter, StationOnRoute, stations_near, stations_on_route
from .geo import Point
from .routes import GoogleRoutes, Route, RouteRequest
from .tolls import TollCharge, TollStation, tolls_on_route

START_AREA_KM = 10  # where to fill up before leaving: along the first few km of the route…
START_RADIUS_M = 3_000  # …or around the start
CHEAPEST_PER_BRAND = 2
CHEAPEST_ANY_BRAND = 4  # on the way, when every brand is alike


@dataclass(frozen=True)
class TripRequest:
    route: RouteRequest
    wanted: StationFilter
    back: bool = False  # a return trip too
    tank_now_l: float | None = None  # None: you fill up before leaving


@dataclass
class Tank:
    litres: float
    price: float  # what a litre of the fuel now in the tank cost


@dataclass(frozen=True)
class FuelStop:
    stop: StationOnRoute
    litres: float  # what goes in at the pump: a full tank
    alternative: StationOnRoute | None = None  # the best of the other brands in the same stretch

    @property
    def cost(self) -> float:
        return self.litres * self.stop.price


@dataclass
class FuelPlan:
    stops: list[FuelStop] = field(default_factory=list)
    cost: float = 0.0  # of the litres burned
    runs_low_km: float | None = None  # where the tank hits its reserve with no wanted station in reach


@dataclass(frozen=True)
class LegPlan:
    route: Route
    tolls: list[TollCharge]
    litres: float
    fuel: FuelPlan
    cheapest: list[StationOnRoute]
    tank_at_end_l: float

    @property
    def toll_cost(self) -> float:
        return sum(charge.station.price for charge in self.tolls)

    @property
    def cost(self) -> float:
        return self.toll_cost + self.fuel.cost

    @property
    def maps_link(self) -> str:
        return self.route.maps_link([stop.stop.station.point for stop in self.fuel.stops])


class PricedStation(NamedTuple):
    station: FuelStation
    price: float


@dataclass(frozen=True)
class StartFill:
    """Where the fuel you leave with comes from, and so what it costs."""
    station: FuelStation | None  # None: no wanted station anywhere near, priced at their average
    price: float
    fill_before_leaving: bool  # False: you start with what's in the tank, valued at this price
    alternative: PricedStation | None = None  # the best of the other brands near the start


class RouteFuel(NamedTuple):
    km_along: list[float]  # from the start to each point of the route
    litres_along: list[float]  # burned from the start to each point of the route
    stations: list[StationOnRoute]  # the wanted ones on the way

    @property
    def litres(self) -> float:
        return self.litres_along[-1]

    def km_where_burned(self, litres: float) -> float:
        index = min(bisect_left(self.litres_along, litres), len(self.km_along) - 1)
        return self.km_along[index]


@dataclass(frozen=True)
class TripPlan:
    car: Car
    wanted: StationFilter
    start: StartFill
    legs: list[LegPlan]

    @property
    def toll_cost(self) -> float:
        return sum(leg.toll_cost for leg in self.legs)

    @property
    def fuel_cost(self) -> float:
        return sum(leg.fuel.cost for leg in self.legs)

    @property
    def cost(self) -> float:
        return self.toll_cost + self.fuel_cost

    @property
    def litres(self) -> float:
        return sum(leg.litres for leg in self.legs)

    @property
    def meters(self) -> int:
        return sum(leg.route.meters for leg in self.legs)

    @property
    def price_dates(self) -> list[str]:
        stations = [self.start.station] if self.start.station else []
        stations += [stop.stop.station for leg in self.legs for stop in leg.fuel.stops]
        return sorted({station.price_date for station in stations if station.price_date})


class FuelPlanner:
    """Where to stop: only when the tank wouldn't reach the end with its reserve, at the cheapest
    station of the preferred brand once the tank is half empty or lower, filling it up."""

    def __init__(self, car: Car, wanted: StationFilter):
        self.car = car
        self.wanted = wanted

    def plan(self, route: RouteFuel, tank: Tank) -> FuelPlan:
        """Drives the route with this tank, which is left as it is at the end, for the next leg."""
        plan = FuelPlan()
        burned, total_litres = 0.0, route.litres
        while tank.litres - (total_litres - burned) < self.car.reserve_l:
            stop = self._next_stop(route.stations, burned, tank.litres)
            if stop is None:
                low_at = burned + tank.litres - self.car.reserve_l
                if plan.runs_low_km is None:
                    plan.runs_low_km = route.km_where_burned(low_at)
                plan.cost += (low_at - burned) * tank.price
                tank.litres, burned = self.car.tank_l, low_at  # filled up at another brand, at about this price
                continue
            alternative = self._alternative(route.stations, burned, tank.litres, stop)
            plan.cost += (stop.litres_at - burned) * tank.price
            tank.litres -= stop.litres_at - burned
            plan.stops.append(FuelStop(stop, self.car.tank_l - tank.litres, alternative))
            tank.litres, tank.price, burned = self.car.tank_l, stop.price, stop.litres_at
        plan.cost += (total_litres - burned) * tank.price
        tank.litres -= total_litres - burned
        return plan

    def _next_stop(self, stations: list[StationOnRoute], burned: float, tank_l: float) -> StationOnRoute | None:
        candidates = self._candidates(stations, burned, tank_l)
        return min(candidates, key=self._preference, default=None)

    def _alternative(self, stations: list[StationOnRoute], burned: float, tank_l: float,
                     chosen: StationOnRoute) -> StationOnRoute | None:
        others = [stop for stop in self._candidates(stations, burned, tank_l)
                  if stop.station.brand != chosen.station.brand]
        return min(others, key=self._preference, default=None)

    def _candidates(self, stations: list[StationOnRoute], burned: float, tank_l: float) -> list[StationOnRoute]:
        low_at = burned + tank_l - self.car.reserve_l
        in_reach = [stop for stop in stations if burned < stop.litres_at <= low_at]
        half_empty = [stop for stop in in_reach if stop.litres_at >= low_at - self.car.tank_l / 2]
        return half_empty or in_reach

    def _preference(self, stop: StationOnRoute) -> tuple:
        """The preferred brand first, then the cheapest, then the later of equally cheap ones."""
        return self.wanted.rank(stop.station), stop.price, -stop.litres_at


class Planner:
    def __init__(self, routes: GoogleRoutes, toll_stations: list[TollStation],
                 fuel_stations: list[FuelStation], car: Car):
        self.routes = routes
        self.toll_stations = toll_stations
        self.fuel_stations = fuel_stations
        self.car = car

    def plan(self, request: TripRequest) -> TripPlan:
        routes = [self.routes.drive(request.route)]
        if request.back:
            routes.append(self.routes.drive(request.route.reversed()))
        on_routes = [self._stations_on(route, request.wanted) for route in routes]
        start = self._start_fill(routes[0].start, on_routes[0], request)
        tank = Tank(self.car.tank_l if request.tank_now_l is None else request.tank_now_l, start.price)
        legs = [self._leg(route, stations, tank, request.wanted) for route, stations in zip(routes, on_routes)]
        return TripPlan(self.car, request.wanted, start, legs)

    def _stations_on(self, route: Route, wanted: StationFilter) -> RouteFuel:
        litres_along = route.litres_along(self.car)
        km_along = [meters / 1000 for meters in route.polyline.cumulative_m]
        return RouteFuel(km_along, litres_along, stations_on_route(route, litres_along, self.fuel_stations, wanted))

    def _leg(self, route: Route, fuel_on_route: RouteFuel, tank: Tank, wanted: StationFilter) -> LegPlan:
        fuel = FuelPlanner(self.car, wanted).plan(fuel_on_route, tank)
        past_start = [stop for stop in fuel_on_route.stations if stop.km > START_AREA_KM]
        shown = CHEAPEST_PER_BRAND if wanted.brands else CHEAPEST_ANY_BRAND
        cheapest = [stop for group in wanted.groups(past_start)
                    for stop in sorted(group, key=lambda stop: (stop.price, stop.km))[:shown]]
        return LegPlan(route, tolls_on_route(route.polyline, self.toll_stations), fuel_on_route.litres, fuel,
                       cheapest, tank.litres)

    def _start_fill(self, start: Point, fuel_on_route: RouteFuel, request: TripRequest) -> StartFill:
        stations = fuel_on_route.stations
        fill_before_leaving = request.tank_now_l is None
        options = [(stop.price, stop.km, stop.station) for stop in stations if stop.km <= START_AREA_KM]
        options += [(near.price, near.meters / 1000, near.station)
                    for near in stations_near(start, self.fuel_stations, request.wanted, START_RADIUS_M)]
        if not options:
            options = [(stop.price, stop.km, stop.station) for stop in stations]
        if not options:
            return StartFill(None, self._average_price(request.wanted), fill_before_leaving)

        def preference(option: tuple) -> tuple:  # the preferred brand, then the cheapest, then the nearest
            return request.wanted.rank(option[2]), *option[:2]

        price, _, station = min(options, key=preference)
        others = [option for option in options if option[2].brand != station.brand]
        alternative = min(others, key=preference, default=None)
        return StartFill(station, price, fill_before_leaving,
                         PricedStation(alternative[2], alternative[0]) if alternative else None)

    def _average_price(self, wanted: StationFilter) -> float:
        prices = [price for station in self.fuel_stations if (price := wanted.price(station)) is not None]
        return sum(prices) / len(prices) if prices else 0.0
