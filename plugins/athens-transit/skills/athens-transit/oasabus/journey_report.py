"""Journeys on any Athens transport, told for Telegram (Markdown), for Siri (one or two spoken
sentences) or as JSON."""
import math
from datetime import datetime

from .journeys import Option
from .links import follow_live
from .planner import AT_STOP_M, athens_now
from .transit import Ride, Walk

ALSO_SHOWN = 2


def minutes_until(moment: datetime, now: datetime) -> int:
    return math.floor((moment - now).total_seconds() / 60)


def leave_phrase(leave_at: datetime, now: datetime) -> str:
    return "leave now" if minutes_until(leave_at, now) <= 0 else f"leave by {leave_at:%H:%M}"


def telegram(options: list[Option], destination: str) -> str:
    now = athens_now()
    best = options[0]
    journey = best.journey
    minutes = minutes_until(journey.leave_at, now)
    when = f" *(in {minutes} min)*" if minutes > 0 else ""
    icon = journey.rides[0].icon
    lines = [f"**{icon} {destination}: {leave_phrase(journey.leave_at, now)}**{when}", ""]
    steps = [leg_line(index, best, destination) for index, leg in enumerate(journey.legs)
             if not (isinstance(leg, Walk) and leg.meters == 0)]
    lines += [f"{n}. {step}" for n, step in enumerate(steps, 1)]
    lines += ["", f"🏁 Arrive ≈ **{journey.arrives:%H:%M}** · [Google Maps]({journey.url})"]
    buses = [ride.line for ride in journey.rides if ride.is_oasa_bus]
    if buses:
        lines.append(follow_live(buses))
    if len(options) > 1:
        lines += ["", "**Other ways**"] + [f"- {summary(option)}" for option in options[1:]]
    lines += ["", footnote(options)]
    return "\n".join(lines)


def leg_line(index: int, option: Option, destination: str) -> str:
    legs = option.journey.legs
    leg = legs[index]
    if isinstance(leg, Walk):
        to = destination if index == len(legs) - 1 else f"**{legs[index + 1].board}**"
        return f"🚶 Walk {math.ceil(leg.minutes)} min ({leg.meters} m) to {to}"
    also = option.also[:ALSO_SHOWN] if leg is option.journey.rides[0] else []
    stops = f"{leg.stops} stop{'s' if leg.stops != 1 else ''}"
    text = f"{leg.icon} **{leg.line}** → {leg.headsign} · **{leg.departs:%H:%M}**{live_mark(leg)} · {stops} to **{leg.alight}**"
    return text + (f" · also {', '.join(f'{t:%H:%M}' for t in also)}" if also else "")


def live_mark(ride: Ride) -> str:
    if not ride.live:
        return ""
    away = f", {ride.stops_away} stops away" if ride.stops_away else ""
    return f" 🟢 live{away}"


def summary(option: Option) -> str:
    journey = option.journey
    rides = " → ".join(f"{r.icon} {r.line}" for r in journey.rides)
    first = journey.rides[0]
    return (f"{rides}: {first.departs:%H:%M}{live_mark(first)} from {first.board}, "
            f"arrive ≈ {journey.arrives:%H:%M}")


def footnote(options: list[Option]) -> str:
    any_live = any(ride.live for option in options for ride in option.journey.rides)
    live = "🟢 = OASA's live prediction; other times are the timetable" if any_live else "Times are the timetable"
    return f"*{live} · routes: Google Maps*"


def voice(options: list[Option]) -> str:
    journey = options[0].journey
    first = journey.rides[0]
    now = athens_now()
    leave = leave_phrase(journey.leave_at, now).capitalize()
    minutes = minutes_until(journey.leave_at, now)
    if minutes > 0:
        leave += f", in {minutes} minutes"
    walk = f"walk to {first.board} and " if journey.first_walk.meters > AT_STOP_M else ""
    timing = "" if first.live else ", by the timetable"
    changes = "".join(f", then change at {ride.board} to the {ride.line}" for ride in journey.rides[1:])
    return (f"{leave}: {walk}take the {first.line} towards {first.headsign} at {first.departs:%H:%M}{timing}"
            f"{changes}. You'll arrive about {journey.arrives:%H:%M}.")


def as_json(options: list[Option]) -> list[dict]:
    return [{
        "leave_at": f"{o.journey.leave_at:%H:%M}", "arrives": f"{o.journey.arrives:%H:%M}", "url": o.journey.url,
        "also": [f"{t:%H:%M}" for t in o.also],
        "legs": [{"walk_m": leg.meters, "walk_min": round(leg.minutes, 1)} if isinstance(leg, Walk) else {
            "mode": leg.mode, "line": leg.line, "headsign": leg.headsign, "board": leg.board, "alight": leg.alight,
            "departs": f"{leg.departs:%H:%M}", "arrives": f"{leg.arrives:%H:%M}", "stops": leg.stops,
            "live": leg.live, "stops_away": leg.stops_away} for leg in o.journey.legs],
    } for o in options]
