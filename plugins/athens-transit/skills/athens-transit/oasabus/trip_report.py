"""A ride on a named bus or trolley line, told in Markdown, in one or two sentences to be spoken,
or as JSON."""
import math

from .links import follow_live
from .planner import ComingBus, Trip

FAR_WALK_M = 1500
NEXT_TIMES_SHOWN = 3


def stop_name(name: str) -> str:
    """OASA writes stop names in capitals ("17th STASH"); words read better capitalised."""
    return " ".join(word.capitalize() for word in name.split())


def minutes(value: float) -> int:
    return max(0, math.floor(value))


def bus_time(bus: ComingBus) -> str:
    return f"{minutes(bus.minutes)}" + ("" if bus.live else "*")


def headline(trip: Trip) -> str:
    route = f"{trip.line} → {trip.destination.name}"
    if trip.walk_from_stop.meters > FAR_WALK_M:
        return f"⚠️ {trip.line} doesn't go near {trip.destination.name}"
    if not trip.next_bus:
        return f"🚌 {route}: no bus you can still catch"
    if trip.at_stop:
        return f"🚌 {route}: next bus in {minutes(trip.next_bus.minutes)} min"
    if minutes(trip.leave_in) == 0:
        return f"🚶 {route}: leave now"
    return f"🚌 {route}: leave in {minutes(trip.leave_in)} min"


def markdown(trip: Trip) -> str:
    option = trip.option
    lines = [f"**{headline(trip)}**", ""]
    walk = trip.walk_to_stop
    if trip.at_stop:
        lines.append(f"- 📍 You're at the **{stop_name(option.board.name)}** stop")
    else:
        lines.append(f"- 🚶 Walk to **{stop_name(option.board.name)}**: {walk.meters} m, "
                     f"{math.ceil(walk.minutes)} min · [route]({walk.url})")
    lines.append(f"- 🚌 {next_buses(trip)}")
    lines.append(f"- {follow_live([trip.line])}")
    walk_off = trip.walk_from_stop
    lines.append(f"- 🛑 Get off at **{stop_name(option.alight.name)}**: {option.stop_count} stops, "
                 f"≈{round(trip.ride_minutes)} min, then {math.ceil(walk_off.minutes)} min on foot · "
                 f"[route]({walk_off.url})")
    if trip.arrival:
        lines.append(f"- 🏁 Arrive ≈ **{trip.arrival:%H:%M}**")
    lines += warnings(trip)
    lines += ["", footnote(trip)]
    return "\n".join(lines)


def next_buses(trip: Trip) -> str:
    bus = trip.next_bus
    if not bus:
        return "Nothing you can reach in time" + (f" (one in {bus_time(trip.missed[-1])} min)" if trip.missed else "")
    where = f", {bus.stops_away} stops away" if bus.stops_away else ""
    first = f"Bus in **{minutes(bus.minutes)} min**" + (f" (live{where})" if bus.live else " (timetable)")
    later = [bus_time(b) for b in trip.catchable[1:NEXT_TIMES_SHOWN]]
    missed = f" · you'd miss the one in {bus_time(trip.missed[-1])}" if trip.missed else ""
    return first + (f" · then {', '.join(later)} min" if later else "") + missed


def warnings(trip: Trip) -> list[str]:
    found = []
    if trip.walk_to_stop.meters > FAR_WALK_M:
        found.append(f"- ⚠️ The nearest {trip.line} stop is {trip.walk_to_stop.meters / 1000:.1f} km away")
    if trip.walk_from_stop.meters > FAR_WALK_M:
        found.append(f"- ⚠️ {trip.line} only gets you within {trip.walk_from_stop.meters / 1000:.1f} km "
                     f"of {trip.destination.name}")
    if trip.walk_to_stop.estimated or trip.walk_from_stop.estimated:
        found.append("- ⚠️ Google Maps didn't answer, so walks are rough estimates")
    return found


def footnote(trip: Trip) -> str:
    marks = ["Live times: OASA", "walks: Google Maps"]
    if any(not bus.live for bus in trip.buses):
        marks.insert(0, "\\* timetable")
    return "*" + " · ".join(marks) + "*"


def voice(trip: Trip) -> str:
    bus = trip.next_bus
    stop = stop_name(trip.option.board.name)
    if not bus:
        return f"There's no {trip.line} you can still catch at {stop} right now."
    when = f"in {minutes(bus.minutes)} minutes" + ("" if bus.live else ", by the timetable")
    if trip.at_stop:
        return f"The next {trip.line} reaches {stop} {when}."
    walk = f"It's a {math.ceil(trip.walk_to_stop.minutes)} minute walk"
    leave = "so leave now." if minutes(trip.leave_in) == 0 else f"so leave in {minutes(trip.leave_in)} minutes."
    return f"The next {trip.line} reaches the {stop} stop {when}. {walk}, {leave}"


def as_json(trip: Trip) -> dict:
    option = trip.option
    return {
        "line": trip.line, "route": option.route.name, "route_code": option.route.code,
        "origin": trip.origin.name, "destination": trip.destination.name,
        "board": {"name": stop_name(option.board.name), "code": option.board.code, "point": str(option.board.point),
                  "walk_m": trip.walk_to_stop.meters, "walk_min": round(trip.walk_to_stop.minutes, 1)},
        "alight": {"name": stop_name(option.alight.name), "code": option.alight.code, "stops": option.stop_count,
                   "walk_m": trip.walk_from_stop.meters, "walk_min": round(trip.walk_from_stop.minutes, 1)},
        "ride_min": round(trip.ride_minutes),
        "buses": [{"minutes": round(b.minutes, 1), "live": b.live, "vehicle": b.vehicle, "stops_away": b.stops_away}
                  for b in trip.buses],
        "leave_in_min": None if trip.leave_in is None else round(trip.leave_in, 1),
        "arrival": f"{trip.arrival:%H:%M}" if trip.arrival else None,
    }
