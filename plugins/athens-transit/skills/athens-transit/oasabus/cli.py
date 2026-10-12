"""oasa: Athens public transport.

    oasa go TO [--from WHERE] [--line LINE] [--format markdown|voice|json]
        How to get to TO now. With a bus or trolley LINE ("040", "A1", "11"): that line, with
        OASA's live times. Otherwise (or with a metro/tram line such as "M1"): Google's transit
        journeys, bus and trolley rides made live. Saves the plan for `oasa watch`.
    oasa watch [--foreground | --stop | --status]
        Leave-now alerts for the last plan: in the background through OASA_NOTIFY, or with
        --foreground printed as they come, until the watch ends (see watch.py).
    oasa places [add NAME WHERE | remove NAME]
        Saved places such as home and work.
    oasa lines QUERY
        OASA lines whose number or name matches.

WHERE and TO: "here" (the person's latest shared location, OASA_LOCATION; the default for --from),
a saved place, "lat,lon", or anything Google Maps can find. Exit codes: 2 no usable location (ask
where the person is), 3 no such place or line, or no ride, 4 a service didn't answer or there's no
Google Maps key, 5 no alert command for a background watch (OASA_NOTIFY). Settings: see
settings.py.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from . import journey_report, trip_report
from .journeys import JourneyPlanner
from .live import LiveBuses
from .location import latest
from .maps import GoogleMaps, MapsUnavailable, Place
from .places import LocationUnknown, PlaceFinder, PlaceNotFound, SavedPlaces
from .planner import LineNotFound, LinePlanner, NoRide, line_key
from .settings import Settings, load
from .telematics import OasaUnavailable, Telematics
from .transit import GoogleTransit
from .watch import CommandNotifier, PrintNotifier, Watcher, WatchPlan, WatchProcess, watch_journey, watch_trip

ENTRY = Path(__file__).resolve().parents[1] / "oasa"


class Usage(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


class App:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.last_plan = settings.data / "last-plan.json"
        self.oasa = Telematics(settings.data / "cache")
        self.maps = GoogleMaps(settings.maps_headers)
        self.places = PlaceFinder(SavedPlaces(settings.data / "places.json"), self.maps, self.shared_location)
        self.live = LiveBuses(self.oasa)
        self.watcher = WatchProcess(settings.data / "watch.pid")

    def shared_location(self):
        return latest(self.settings.location)

    def go(self, to: str, start: str, line: str | None, output: str) -> str:
        origin, destination = self.places.find(start), self.places.find(to)
        if line and self.is_oasa_line(line):
            try:
                return self.go_by_bus(line, origin, destination, output)
            except OasaUnavailable:
                pass  # Google still has the timetable
        options = JourneyPlanner(GoogleTransit(self.settings.maps_key), self.live).plan(origin.point, destination.point, line)
        if not options:
            raise NoRide(f"Google has no transit journey{f' with {line}' if line else ''} to {destination.name} now")
        watch_journey(options[0], destination.name, self.live).save(self.last_plan)
        return {"markdown": lambda o: journey_report.markdown(o, destination.name), "voice": journey_report.voice,
                "json": lambda o: json.dumps(journey_report.as_json(o), ensure_ascii=False, indent=1)}[output](options)

    def go_by_bus(self, line: str, origin: Place, destination: Place, output: str) -> str:
        trip = LinePlanner(self.oasa, self.maps).plan(line, origin, destination)
        watch_trip(trip).save(self.last_plan)
        return {"markdown": trip_report.markdown, "voice": trip_report.voice,
                "json": lambda t: json.dumps(trip_report.as_json(t), ensure_ascii=False, indent=1)}[output](trip)

    def is_oasa_line(self, line: str) -> bool:
        try:
            return any(line_key(known.number) == line_key(line) for known in self.oasa.lines())
        except OasaUnavailable:
            return False

    def watch(self) -> str:
        plan = self.plan_to_watch()
        if not self.settings.notify:
            raise Usage("no alert command (OASA_NOTIFY) for a background watch: "
                        "run oasa watch --foreground, which prints the alerts", 5)
        env = os.environ | {"OASA_WORKSPACE": str(self.settings.workspace)}
        pid = self.watcher.start([sys.executable, "-I", str(ENTRY), "watch-run"], self.settings.data / "watch.log", env)
        return f"watching {plan.title} (pid {pid}); it sends its own status message"

    def watch_run(self) -> None:
        Watcher(self.plan_to_watch(), self.oasa, CommandNotifier(self.settings.notify), self.shared_location).run()

    def watch_foreground(self) -> None:
        plan = self.plan_to_watch()
        self.watcher.take_over()
        Watcher(plan, self.oasa, PrintNotifier(), self.shared_location).run()

    def plan_to_watch(self) -> WatchPlan:
        if not self.last_plan.exists():
            raise Usage("nothing to watch: run oasa go first", 3)
        return WatchPlan.load(self.last_plan)

    def lines(self, query: str) -> str:
        found = [line for line in self.oasa.lines()
                 if line_key(query) == line_key(line.number) or query.upper() in line.name.upper()]
        return "\n".join(f"{line.number}\t{line.name}" for line in found) or "no matching line"


def places_command(args, finder: PlaceFinder) -> str:
    saved = finder.saved
    if args.action == "add":
        place = finder.find(args.where)
        saved.save(args.name, place)
        return f"saved {args.name}: {place.name} ({place.point})"
    if args.action == "remove":
        return f"removed {args.name}" if saved.remove(args.name) else f"no place called {args.name}"
    return "\n".join(f"{name}\t{p.name}\t{p.point}" for name, p in saved.all().items()) or "no saved places"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="oasa", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    go = sub.add_parser("go")
    go.add_argument("to")
    go.add_argument("--from", dest="start", default="here")
    go.add_argument("--line")
    go.add_argument("--format", dest="output", choices=["markdown", "voice", "json"], default="markdown")
    watch = sub.add_parser("watch").add_mutually_exclusive_group()
    watch.add_argument("--foreground", action="store_true")
    watch.add_argument("--stop", action="store_true")
    watch.add_argument("--status", action="store_true")
    sub.add_parser("watch-run")
    places = sub.add_parser("places")
    places.add_argument("action", nargs="?", choices=["list", "add", "remove"], default="list")
    places.add_argument("name", nargs="?")
    places.add_argument("where", nargs="?")
    lines = sub.add_parser("lines")
    lines.add_argument("query")
    return p


def run(args) -> str | None:
    app = App(load())
    if args.command == "go":
        return app.go(args.to, args.start, args.line, args.output)
    if args.command == "watch":
        if args.stop:
            return "stopped" if app.watcher.stop() else "no watcher running"
        if args.status:
            pid = app.watcher.running()
            return f"watching (pid {pid})" if pid else "no watcher running"
        if args.foreground:
            return app.watch_foreground()
        return app.watch()
    if args.command == "watch-run":
        return app.watch_run()
    if args.command == "places":
        return places_command(args, app.places)
    return app.lines(args.query)


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        output = run(args)
    except LocationUnknown as e:
        print(f"oasa: {e}", file=sys.stderr)
        return 2
    except (PlaceNotFound, LineNotFound, NoRide) as e:
        print(f"oasa: {e}", file=sys.stderr)
        return 3
    except Usage as e:
        print(f"oasa: {e}", file=sys.stderr)
        return e.code
    except (OasaUnavailable, MapsUnavailable) as e:
        print(f"oasa: {e}", file=sys.stderr)
        return 4
    if output:
        print(output)
    return 0
