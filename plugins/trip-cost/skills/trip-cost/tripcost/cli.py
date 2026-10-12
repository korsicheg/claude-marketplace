"""The trip command: what a drive in Greece costs in tolls and fuel, and where to fill up."""
import argparse
import json
import re
import sys
from dataclasses import asdict

from . import fuel, places, report, settings, tolls
from .car import load_car
from .feeds import FeedUnavailable
from .jsliteral import JsLiteralError
from .planner import Planner, TripRequest
from .routes import GoogleRoutes, NoRoute, RouteRequest, RoutesUnavailable

NEARBY_RADIUS_KM = 3.0
ANY_BRAND = "any"
NEARBY_SHOWN = 8
TANK_RE = re.compile(r"\s*(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>%|l|L)?\s*")

EXIT_NO_LOCATION = 2
EXIT_NOT_FOUND = 3
EXIT_UNAVAILABLE = 4


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = settings.load()
    try:
        return args.run(args, config)
    except places.NoLocation as error:
        print(f"No location: {error}", file=sys.stderr)
        return EXIT_NO_LOCATION
    except NoRoute as error:
        print(error, file=sys.stderr)
        return EXIT_NOT_FOUND
    except (RoutesUnavailable, FeedUnavailable, JsLiteralError) as error:
        print(error, file=sys.stderr)
        return EXIT_UNAVAILABLE


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="trip", description=__doc__)
    commands = root.add_subparsers(required=True)

    plan = commands.add_parser("plan", help="tolls, fuel and fuel stops for a drive")
    plan.add_argument("start", help='"home", "here", a saved place, "lat,lon", an address or a place name')
    plan.add_argument("end")
    plan.add_argument("--via", action="append", default=[], help="a stop on the way (repeat for several)")
    plan.add_argument("--back", action="store_true", help="and the drive back")
    plan.add_argument("--avoid-tolls", action="store_true", help="the route Google finds without tolls")
    plan.add_argument("--tank", help="fuel in the tank now, e.g. 40%% or 15L (default: you fill up first)")
    _add_station_options(plan)
    plan.add_argument("--format", choices=["markdown", "json"], default="markdown")
    plan.set_defaults(run=run_plan)

    near = commands.add_parser("stations", help="the cheapest stations near a place")
    near.add_argument("place", nargs="?", default="home")
    near.add_argument("--radius", type=float, default=NEARBY_RADIUS_KM, help="km (default 3)")
    _add_station_options(near)
    near.set_defaults(run=run_stations)

    toll_data = commands.add_parser("tolls", help="download the toll prices again (they change in January)")
    toll_data.set_defaults(run=run_tolls_update)

    car = commands.add_parser("car", help="the car the costs are for")
    car.set_defaults(run=run_car)
    return root


def run_plan(args, config: settings.Settings) -> int:
    car = load_car(config.data)
    wanted = _wanted(args, car)
    route = RouteRequest(places.waypoint(args.start, config), places.waypoint(args.end, config),
                         tuple(places.waypoint(stop, config) for stop in args.via), args.avoid_tolls)
    planner = Planner(GoogleRoutes(config.maps_key), tolls.load_stations(config.data),
                      fuel.load_stations(config.data), car)
    plan = planner.plan(TripRequest(route, wanted, args.back, _tank_litres(args.tank, car.tank_l)))
    _print(report.trip_json(plan) if args.format == "json" else report.trip_message(plan))
    return 0


def run_stations(args, config: settings.Settings) -> int:
    place = places.waypoint(args.place, config)
    if place.point is None:
        print(f"{args.place!r} isn't a saved place or lat,lon: give coordinates", file=sys.stderr)
        return EXIT_NOT_FOUND
    wanted = _wanted(args, load_car(config.data))
    found = fuel.stations_near(place.point, fuel.load_stations(config.data), wanted, args.radius * 1000)
    _print(report.nearby_message(place.label, found[:NEARBY_SHOWN], wanted.fuel))
    return 0


def run_tolls_update(args, config: settings.Settings) -> int:
    print(f"{tolls.refresh_stations(config.data)} toll stations downloaded from mydiodia.gr")
    return 0


def run_car(args, config: settings.Settings) -> int:
    print(json.dumps(asdict(load_car(config.data)), indent=2))
    return 0


def _add_station_options(command: argparse.ArgumentParser) -> None:
    command.add_argument("--brands", help="comma-separated, preferred first; \"any\" for every brand "
                                          "(default: the car profile's brands, or every brand)")
    command.add_argument("--fuel", help="u95, u100, d, lpg… (default: the car's fuel)")


def _wanted(args, car) -> fuel.StationFilter:
    named = car.brands if args.brands is None else [] if args.brands.strip().lower() == ANY_BRAND else args.brands.split(",")
    brands = tuple(dict.fromkeys(fuel.normal_brand(brand) for brand in named if brand.strip()))
    return fuel.StationFilter(brands, args.fuel or car.fuel)


def _tank_litres(text: str | None, tank_l: float) -> float | None:
    if text is None:
        return None
    match = TANK_RE.fullmatch(text)
    if not match:
        raise SystemExit(f"--tank takes a percentage or litres, e.g. 40% or 15L, not {text!r}")
    amount = float(match["amount"])
    return min(tank_l, amount / 100 * tank_l if match["unit"] == "%" else amount)


def _print(output: str | dict) -> None:
    print(json.dumps(output, ensure_ascii=False, indent=2) if isinstance(output, dict) else output)
