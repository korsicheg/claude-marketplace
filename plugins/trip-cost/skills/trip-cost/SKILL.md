---
name: trip-cost
description: What a drive in Greece costs in Greek motorway tolls (διόδια) and fuel for the user's car, with the cheapest fuel stations on the way (of their preferred brands, if they have any) and where to stop for fuel. Use whenever the user asks how much a drive or road trip in Greece costs, about tolls on a Greek route, fuel for a trip, or where to fill up on the way or near a place in Greece.
---

# Trip cost

Everything goes through one command in this skill's folder. Below, `trip` means:

```bash
python3 -I <this skill's base directory>/trip
```

## Planning a drive

```bash
trip plan FROM TO [--via PLACE]… [--back] [--tank 40%|15L] [--brands EKO,BP|any] [--avoid-tolls] [--format markdown|json]
```

- **Places**: a saved place (`home`, `work`, the athens-transit plugin's saved places), `here` (the user's latest shared location, when the setup provides one: live, or under 30 min old), `lat,lon`, or any address or place name Google Maps finds ("Nafplio", "Meteora").
- It routes with Google (traffic now), finds every toll plaza and ramp booth the route pays, works out the litres from each stretch's speed, and plans the fuel: **fill up before you go** near the start, and a stop on the way only when the tank wouldn't reach the end with its reserve, once the tank is half empty or lower.
- **Brands**: without a preference, every brand is alike and each fill-up or stop is the cheapest station in reach. With the car profile's `brands` (or `--brands`), the first brand wins wherever it can be, followed by "or" the best of the next brand, and the cheapest stations on the way are listed per brand in that order. `--brands any` ignores the profile's preference.
- `--back` adds the drive back (routed separately: the tolls differ by direction). `--tank` says what's in the tank now instead of assuming the user fills up first.
- The fuel cost is what the trip burns, each litre at the price of the station it came from; a stop's line also says what filling up there costs at the pump.
- The default output is the finished answer in Markdown, with the Google Maps link Google's terms require: give it to the user as is. `--format json` gives every detail.
- If the user asks without saying where from, use `home` if it's saved, and say so; otherwise ask.

## Stations near a place

```bash
trip stations [PLACE] [--radius 3] [--brands EKO,BP|any] [--fuel u95]
```

The cheapest stations around a saved place, `here` or `lat,lon` (default `home`), cheapest first.

## The car

`trip car` shows the car profile the costs are for. Until the user sets theirs it's a typical compact petrol car, so say so in the answer, and ask once which car they drive, or what it burns. Then write their answer to `.trip/car.json` in their project folder; any field of `trip car` overrides the default:

```json
{"name": "Skoda Octavia 2.0 TDI (2020)", "fuel": "d", "tank_l": 45, "reserve_l": 6,
 "consumption": [[45, 5.2], [75, 4.1], [100, 4.5], [999, 5.6]], "brands": ["SHELL", "AVIN"]}
```

`consumption` is litres per 100 km by a stretch's average speed (`[up to km/h, litres]`, fastest last); `fuel` is `u95`, `u100`, `d` (diesel) or `lpg`; `brands` is the fuel brands the user prefers, preferred first (leave it out for every brand alike). When they tell you something new ("I get 5.2 on the highway", "I prefer Shell"), update the file.

## Data and caveats

- **Tolls**: the 212 stations of [mydiodia.gr](https://mydiodia.gr/), with positions and 2026 car prices from the operators' price lists (category 2). Kept in `.trip/tolls.json` and refreshed weekly; prices change each January, so run `trip tolls` then to download them at once. The matching rules port the site's own calculator; route totals agree with the site's published routes (Athens–Thessaloniki €36.70, –Patras €13.80, –Kalamata €16.35, plus Attiki Odos €2.55 when the route uses it).
- **Fuel**: per-station prices reported to the Ministry's observatory (fuelprices.gr), from the fuelGR feed (GitHub release file, updated twice a day), cached 3 hours in `.trip/`. A station's price date is when it last reported.
- On motorways only service areas on the right-hand side count as "on the way"; elsewhere stations up to 1 km off the route.
- Google's `--avoid-tolls` doesn't know the Greek tolls (it sent Athens–Patras over the Rio–Antirrio bridge): the report still shows what that route really pays.
- e-pass frequent-user discounts and Olympia Odos's per-km billing for e-pass users aren't modelled: prices are the plazas' posted car prices.

Exit codes: 2 `here` has no recent location (ask where the user is, or use a saved place); 3 no route to that place; 4 Google, the toll dataset or the price feed can't be reached and nothing is cached.

## Setup

- **Google Maps key** with the **Routes API** enabled: taken from the project's MCP server at `mapstools.googleapis.com`, or `GOOGLE_MAPS_API_KEY`.
- **Saved places**: the athens-transit plugin's, `.oasa/places.json` in the project folder, or the JSON file in `TRIP_PLACES`.
- **`here`**: `TRIP_LOCATION`, a JSON file with the user's latest position that something else keeps up to date (`{"latitude", "longitude", "updated", "live_until"}`, unix times, `live_until` optional).
- Each user's data stays in their own project folder, in `.trip/` (car profile, toll and price caches).
