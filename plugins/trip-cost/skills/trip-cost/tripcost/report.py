"""A trip plan as a Markdown message or as JSON."""
from datetime import date

from .fuel import FUEL_NAMES, FuelStation, StationNearby, StationOnRoute
from .planner import LegPlan, PricedStation, TripPlan

SOURCES = ("Tolls: [mydiodia.gr](https://mydiodia.gr/) (2026 car prices from the operators). "
           "Fuel: prices stations reported to [fuelprices.gr](https://www.fuelprices.gr/), via fuelGR")


def euros(amount: float) -> str:
    return f"€{amount:.2f}"


def litre_price(price: float) -> str:
    return f"€{price:.3f}/L"


def duration(seconds: int) -> str:
    hours, minutes = divmod(round(seconds / 60), 60)
    return f"{hours} h {minutes:02d} min" if hours else f"{minutes} min"


def station_link(station: FuelStation) -> str:
    place = " ".join((station.address or station.name).split()).title()
    return f"[{station.brand}, {place}]({station.maps_url})"


def place_name(label: str) -> str:
    return label[:1].upper() + label[1:]


def trip_message(plan: TripPlan) -> str:
    first = plan.legs[0].route.request
    title = f"{place_name(first.start.label)} → {place_name(first.end.label)}"
    title += " and back" if len(plan.legs) > 1 else ""
    lines = [
        f"**🚗 {title}: about {euros(plan.cost)}**",
        "",
        (f"Tolls **{euros(plan.toll_cost)}** + fuel **{euros(plan.fuel_cost)}** "
         f"({plan.litres:.1f} L of {FUEL_NAMES.get(plan.car.fuel, plan.car.fuel)}, "
         f"{plan.litres / plan.meters * 100_000:.1f} L/100 km)"),
        "",
    ]
    if len(plan.legs) == 1:
        lines += _leg_lines(plan.legs[0], plan, first_items=_start_lines(plan))
    else:
        lines += _start_lines(plan)
        for heading, leg in zip(("### Out", "### Back"), plan.legs):
            totals = f"**{euros(leg.cost)}**: tolls {euros(leg.toll_cost)} + fuel {euros(leg.fuel.cost)}"
            lines += ["", heading, "", totals, "", *_leg_lines(leg, plan)]
    lines += ["", f"*{plan.car.name}, estimated consumption. {SOURCES}, {_dates(plan.price_dates)}.*"]
    return "\n".join(lines)


def nearby_message(place: str, found: list[StationNearby], fuel: str) -> str:
    if not found:
        return f"No matching station within reach of {place}."
    lines = [f"**⛽ Cheapest {FUEL_NAMES.get(fuel, fuel)} near {place}**", ""]
    lines += [f"{number}. {litre_price(near.price)} · {station_link(near.station)} · {near.meters / 1000:.1f} km"
              for number, near in enumerate(found, 1)]
    lines += ["", f"*{SOURCES}, {_dates(sorted({near.station.price_date for near in found}))}.*"]
    return "\n".join(lines)


def trip_json(plan: TripPlan) -> dict:
    return {
        "car": plan.car.name, "fuel": plan.car.fuel, "brands": list(plan.wanted.brands),
        "total_eur": round(plan.cost, 2), "tolls_eur": round(plan.toll_cost, 2),
        "fuel_eur": round(plan.fuel_cost, 2), "litres": round(plan.litres, 1), "km": round(plan.meters / 1000, 1),
        "start_fill": {"station": _station_json(plan.start.station), "price": plan.start.price,
                       "fill_before_leaving": plan.start.fill_before_leaving,
                       "alternative": _priced_json(plan.start.alternative)},
        "legs": [_leg_json(leg) for leg in plan.legs],
    }


def _start_lines(plan: TripPlan) -> list[str]:
    start = plan.start
    if start.station is None:
        return [(f"- ⛽ No {_brands(plan)} station near the start: fuel priced at their average, "
                 f"{litre_price(start.price)}")]
    if start.fill_before_leaving:
        return [f"- ⛽ Fill up before you go: {station_link(start.station)}, {litre_price(start.price)}"
                + _or(start.alternative)]
    return [(f"- ⛽ Fuel in the tank valued at {litre_price(start.price)}, the cheapest {_brands(plan)} "
             f"near the start: {station_link(start.station)}")]


def _leg_lines(leg: LegPlan, plan: TripPlan, first_items: list[str] = ()) -> list[str]:
    route = leg.route
    road = f" · via {route.description}" if route.description else ""
    lines = [f"- {route.meters / 1000:.0f} km · {duration(route.seconds)} with traffic now{road}", *first_items]
    lines += _stop_lines(leg, plan)
    lines += ["", *_toll_details(leg), "", *_cheapest_details(leg, plan), "",
              f"[Open the route in Google Maps]({leg.maps_link})"]
    return lines


def _stop_lines(leg: LegPlan, plan: TripPlan) -> list[str]:
    lines = [f"- ⛽ Stop at km {stop.stop.km:.0f}: {station_link(stop.stop.station)}, "
             f"{litre_price(stop.stop.price)}, about {stop.litres:.0f} L for {euros(stop.cost)}"
             + _or(_priced(stop.alternative)) for stop in leg.fuel.stops]
    if leg.fuel.runs_low_km is not None:
        elsewhere = "at another brand" if plan.wanted.brands else "off the route"
        lines.append(f"- ⚠️ No {_brands(plan)} station in reach: the tank runs low around km "
                     f"{leg.fuel.runs_low_km:.0f}, so fill up {elsewhere} before then")
    elif not leg.fuel.stops:
        lines.append(f"- No fuel stop needed: about {leg.tank_at_end_l:.0f} L left at the end")
    return lines


def _toll_details(leg: LegPlan) -> list[str]:
    if not leg.tolls:
        return ["No tolls on this route."]
    lines = [f"<details><summary>Tolls: {len(leg.tolls)} stations, {euros(leg.toll_cost)}</summary>", ""]
    lines += [f"- {charge.station.name} ({charge.station.highway}, km {charge.km:.0f}) {euros(charge.station.price)}"
              for charge in leg.tolls]
    return lines + ["", "</details>"]


def _cheapest_details(leg: LegPlan, plan: TripPlan) -> list[str]:
    if not leg.cheapest:
        return [f"No {_brands(plan)} station right on the way."]
    lines = [f"<details><summary>Cheapest {_brands(plan)} on the way</summary>", ""]
    lines += [f"- km {stop.km:.0f}: {station_link(stop.station)}, {litre_price(stop.price)}" for stop in leg.cheapest]
    return lines + ["", "</details>"]


def _brands(plan: TripPlan) -> str:
    """The wanted brands as a phrase: "EKO / BP", or "fuel" for every brand."""
    return " / ".join(plan.wanted.brands) or "fuel"


def _priced(stop: StationOnRoute | None) -> PricedStation | None:
    return PricedStation(stop.station, stop.price) if stop else None


def _or(alternative: PricedStation | None) -> str:
    """The best station of the other brands, after the preferred one."""
    return f" · or {station_link(alternative.station)}, {litre_price(alternative.price)}" if alternative else ""


def _dates(price_dates: list[str]) -> str:
    if not price_dates:
        return "latest prices"
    first, last = (date.fromisoformat(text) for text in (price_dates[0], price_dates[-1]))
    if first == last:
        return f"prices reported {first.day} {first:%b}"
    if first.month == last.month:
        return f"prices reported {first.day}–{last.day} {last:%b}"
    return f"prices reported {first.day} {first:%b} – {last.day} {last:%b}"


def _leg_json(leg: LegPlan) -> dict:
    route = leg.route
    return {
        "from": route.request.start.label, "to": route.request.end.label, "km": round(route.meters / 1000, 1),
        "minutes": round(route.seconds / 60), "road": route.description, "litres": round(leg.litres, 1),
        "tolls_eur": round(leg.toll_cost, 2), "fuel_eur": round(leg.fuel.cost, 2),
        "tolls": [{"name": charge.station.name, "name_gr": charge.station.name_gr, "highway": charge.station.highway,
                   "operator": charge.station.operator, "km": round(charge.km, 1), "eur": charge.station.price}
                  for charge in leg.tolls],
        "fuel_stops": [{"station": _station_json(stop.stop.station), "km": round(stop.stop.km, 1),
                        "price": stop.stop.price, "litres": round(stop.litres, 1), "eur": round(stop.cost, 2),
                        "alternative": None if stop.alternative is None else {
                            "station": _station_json(stop.alternative.station), "km": round(stop.alternative.km, 1),
                            "price": stop.alternative.price}}
                       for stop in leg.fuel.stops],
        "runs_low_km": leg.fuel.runs_low_km,
        "tank_at_end_l": round(leg.tank_at_end_l, 1),
        "cheapest_on_route": [{"station": _station_json(stop.station), "km": round(stop.km, 1), "price": stop.price,
                               "off_route_m": round(stop.off_route_m)} for stop in leg.cheapest],
        "maps_url": leg.maps_link,
    }


def _priced_json(priced: PricedStation | None) -> dict | None:
    return None if priced is None else {"station": _station_json(priced.station), "price": priced.price}


def _station_json(station: FuelStation | None) -> dict | None:
    if station is None:
        return None
    return {"brand": station.brand, "name": station.name, "address": station.address,
            "lat": station.point.lat, "lon": station.point.lon, "prices": station.prices,
            "price_date": station.price_date, "maps_url": station.maps_url}
