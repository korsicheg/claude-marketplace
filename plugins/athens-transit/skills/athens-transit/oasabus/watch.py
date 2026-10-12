"""Leave-now alerts. After `oasa go`, a watcher runs in the background without Claude: every half
minute it checks the coming departures at the boarding stop (OASA's live predictions for buses
and trolleys, the timetable otherwise), and where the person is when they share a live location. It
keeps one Telegram status message up to date, sends "Leave now" when it's time to walk, and
stops once the bus has left (telling them where to get off) or after a while.

The plan to watch is saved by `oasa go`; `oasa watch` starts a watcher for it."""
import json
import math
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from .geo import Point, estimated_walk_minutes
from .journeys import Option
from .live import LiveBuses
from .location import SharedLocation
from .planner import AT_STOP_M, LEAVE_EARLY_MIN, SAME_BUS_MIN, Trip, athens_now
from .telematics import OasaUnavailable, Telematics
from .trip_report import stop_name

TICK_S = 30
FAST_TICK_S = 15  # once the bus is SOON_MIN away
SOON_MIN = 5
WATCH_LIMIT_MIN = 75
BOARDED_M = 150  # still this near the stop when the bus leaves: on it
LEAVING_MIN = 2  # a departure this close that then disappears has left
STOP_WAIT_S = 5


@dataclass
class WatchPlan:
    title: str  # "040 → Syntagma Square"
    vehicle: str  # "bus", "metro"…
    stop_name: str
    stop_point: Point
    origin: Point
    walk_m: int
    walk_min: float
    live_stop: str | None = None  # OASA stop code with predictions for this ride
    live_routes: list[int] = field(default_factory=list)
    scheduled: list[str] = field(default_factory=list)  # ISO times from the timetable
    after_boarding: str = ""  # "Get off at …"

    def save(self, file: Path) -> None:
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=2) + "\n")

    @classmethod
    def load(cls, file: Path) -> "WatchPlan":
        saved = json.loads(file.read_text())
        saved["stop_point"], saved["origin"] = Point(*saved["stop_point"]), Point(*saved["origin"])
        return cls(**saved)


@dataclass(frozen=True)
class Departure:
    key: str  # the vehicle, or the scheduled time
    minutes: float
    live: bool


class Telegram:
    """The person's chat, through tg (see settings.py)."""

    def __init__(self, tg: str, chat: str):
        self.tg_command = tg
        self.chat = chat

    def send(self, text: str) -> str:
        return self.tg("send", text)

    def edit(self, message_id: str, text: str) -> None:
        self.tg("edit", message_id, text)

    def tg(self, *args: str) -> str:
        done = subprocess.run([self.tg_command, "--chat", self.chat, *args], capture_output=True, text=True, timeout=60,
                              check=False)
        if done.returncode:
            raise RuntimeError(f"tg {args[0]} failed: {done.stderr.strip()}")
        return done.stdout.strip()


class Watcher:
    def __init__(self, plan: WatchPlan, oasa: Telematics, telegram: Telegram,
                 shared_location: Callable[[], SharedLocation | None]):
        self.plan = plan
        self.oasa = oasa
        self.telegram = telegram
        self.shared_location = shared_location
        self.status_id = None
        self.status_text = ""
        self.alerted = set()  # departures the person was told to leave for
        self.target = None  # the departure they're heading for

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self.stopped)
        deadline = time.time() + WATCH_LIMIT_MIN * 60
        while time.time() < deadline:
            try:
                if self.tick():
                    return
            except OasaUnavailable as e:
                print(f"{athens_now():%H:%M:%S} skipped a look: {e}", flush=True)  # the next one may work
            except (RuntimeError, subprocess.SubprocessError) as e:
                print(f"{athens_now():%H:%M:%S} telegram: {e}", flush=True)
            time.sleep(FAST_TICK_S if self.soon() else TICK_S)
        self.finish(f"⏹️ Stopped watching after {WATCH_LIMIT_MIN} min.")

    def tick(self) -> bool:
        """One look; True once there's nothing left to watch."""
        here, live = self.position()
        distance = here.meters_to(self.plan.stop_point)
        walk = self.walk_minutes(here, distance)
        departures = self.departures()
        if self.target and self.left(self.target, departures):
            if self.boarded(distance, live):
                return True
            self.telegram.send(f"😕 Missed the {self.plan.title}. Looking at the next one.")
            self.target = None
        self.target = self.next_target(departures, walk)
        leave_in = self.target.minutes - walk - LEAVE_EARLY_MIN if self.target else None
        if self.target and leave_in <= 0 and distance > AT_STOP_M and self.target.key not in self.alerted:
            self.telegram.send(f"🚶 **Leave now** for **{self.plan.stop_name}**: the {self.plan.title} comes in "
                               f"{math.floor(self.target.minutes)} min, {math.ceil(walk)} min walk.")
            self.alerted.add(self.target.key)
        self.show(walk, leave_in, distance, live)
        return False

    def next_target(self, departures: list[Departure], walk: float) -> Departure | None:
        """The departure the person was told to leave for, while it's still coming (they may walk
        faster than planned), else the first they can reach in time."""
        if self.target and self.target.key in self.alerted:
            still_coming = next((d for d in departures if d.key == self.target.key), None)
            if still_coming:
                return still_coming
        return next((d for d in departures if d.minutes >= walk), None)

    def position(self) -> tuple[Point, bool]:
        """Where the person is: their live location while it runs, else where the plan started."""
        shared = self.shared_location()
        if shared and shared.is_live(time.time()):
            return shared.point, True
        return self.plan.origin, False

    def walk_minutes(self, here: Point, distance: float) -> float:
        if distance <= AT_STOP_M:
            return 0.0
        planned = self.plan.origin.meters_to(self.plan.stop_point)
        if planned > AT_STOP_M:
            return self.plan.walk_min * distance / planned  # Google's walk, scaled to where they are now
        return estimated_walk_minutes(here, self.plan.stop_point)

    def departures(self) -> list[Departure]:
        now = athens_now()
        live = []
        if self.plan.live_stop:
            live = [Departure(a.vehicle, a.minutes, True) for a in self.oasa.arrivals(self.plan.live_stop)
                    if a.route_code in self.plan.live_routes]
        last_live = max((d.minutes for d in live), default=-1)
        scheduled = [Departure(at, (datetime.fromisoformat(at) - now).total_seconds() / 60, False)
                     for at in self.plan.scheduled]
        later = [d for d in scheduled if d.minutes >= 0 and d.minutes > last_live + SAME_BUS_MIN]
        return sorted(live, key=lambda d: d.minutes) + later

    def left(self, target: Departure, departures: list[Departure]) -> bool:
        if target.live:
            return target.minutes <= LEAVING_MIN and all(d.key != target.key for d in departures)
        return (datetime.fromisoformat(target.key) - athens_now()).total_seconds() < 0

    def boarded(self, distance: float, live: bool) -> bool:
        """After the bus left: done, unless a live location shows the person still far from the stop."""
        if live and distance > BOARDED_M:
            return False
        on_it = "✅ On board? " if live else f"🚌 Your {self.plan.title} has left {self.plan.stop_name}. "
        self.telegram.send(on_it + self.plan.after_boarding)
        self.finish("✅ Done watching.")
        return True

    def stopped(self, *_signal) -> None:
        self.finish("⏹️ Stopped watching.")
        sys.exit(0)

    def soon(self) -> bool:
        return bool(self.target) and self.target.minutes <= SOON_MIN

    def show(self, walk: float, leave_in: float | None, distance: float, live: bool) -> None:
        lines = [f"⏱️ **{self.plan.title}**"]
        if not self.target:
            lines.append(f"No {self.plan.vehicle} you can catch at **{self.plan.stop_name}** right now.")
        else:
            source = "live" if self.target.live else "timetable"
            lines.append(f"At **{self.plan.stop_name}** in **{math.floor(self.target.minutes)} min** ({source})")
            if distance <= AT_STOP_M:
                lines.append("📍 You're at the stop.")
            elif leave_in <= 0:
                lines.append(f"🚶 **Leave now**: {math.ceil(walk)} min walk")
            else:
                lines.append(f"👉 Leave in **{math.floor(leave_in)} min** ({math.ceil(walk)} min walk)")
        where = "following your live location" if live else "from where you were"
        lines.append(f"*Updated {athens_now():%H:%M} · {where} · say stop to end*")
        self.update_status("\n".join(lines))

    def update_status(self, text: str) -> None:
        if text == self.status_text:
            return
        if self.status_id:
            self.telegram.edit(self.status_id, text)
        else:
            self.status_id = self.telegram.send(text)
        self.status_text = text

    def finish(self, note: str) -> None:
        if self.status_id:
            lines = self.status_text.splitlines()
            self.telegram.edit(self.status_id, "\n".join(lines[:-1] + [f"*{note}*"]))


class WatchProcess:
    """The one background watcher, its pid kept in a file."""

    def __init__(self, pid_file: Path):
        self.pid_file = pid_file

    def running(self) -> int | None:
        try:
            pid = int(self.pid_file.read_text())
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            return None

    def start(self, command: list[str], log: Path, env: dict) -> int:
        self.stop()
        with open(log, "a") as out:
            process = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                       env=env, start_new_session=True)
        self.pid_file.write_text(f"{process.pid}\n")
        return process.pid

    def stop(self) -> bool:
        pid = self.running()
        if not pid:
            return False
        os.kill(pid, signal.SIGTERM)
        for _ in range(STOP_WAIT_S * 10):
            if self.running() != pid:
                return True
            time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)  # stuck in a call that signals can't interrupt, such as a DNS lookup
        return True


def watch_trip(trip: Trip) -> WatchPlan:
    """What to watch for a ride on a named bus or trolley line."""
    option = trip.option
    scheduled = [(trip.planned_at + timedelta(minutes=bus.minutes)).isoformat() for bus in trip.buses if not bus.live]
    return WatchPlan(
        title=f"{trip.line} → {trip.destination.name}", vehicle="bus", stop_name=stop_name(option.board.name),
        stop_point=option.board.point, origin=trip.origin.point,
        walk_m=trip.walk_to_stop.meters, walk_min=trip.walk_to_stop.minutes,
        live_stop=option.board.code, live_routes=list(option.route_codes), scheduled=scheduled,
        after_boarding=f"Get off at **{stop_name(option.alight.name)}**: {option.stop_count} stops, "
                       f"≈{round(trip.ride_minutes)} min, then {math.ceil(trip.walk_from_stop.minutes)} min on foot.")


def watch_journey(option: Option, destination: str, live: LiveBuses) -> WatchPlan:
    """What to watch for a journey Google planned: its first ride."""
    journey = option.journey
    first = journey.rides[0]
    source = live.source(first) if first.is_oasa_bus else None
    scheduled = [] if first.live else [first.departs.isoformat()]
    scheduled += [t.isoformat() for t in option.also]
    rest = [f"{r.icon} {r.line} at {r.departs:%H:%M} from {r.board}" for r in journey.rides[1:]]
    after = f"Get off at **{first.alight}** ({first.stops} stops)" + (", then " + ", then ".join(rest) if rest else "")
    return WatchPlan(
        title=f"{first.line} → {destination}", vehicle=first.mode, stop_name=first.board,
        stop_point=first.board_point, origin=journey.origin,
        walk_m=journey.first_walk.meters, walk_min=journey.first_walk.minutes,
        live_stop=source.stop_code if source else None, live_routes=list(source.route_codes) if source else [],
        scheduled=scheduled, after_boarding=after + f". Arrive ≈ {journey.arrives:%H:%M}.")
