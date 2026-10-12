# trip-cost

What a drive in Greece costs, for Claude Code. Ask "how much is a weekend in Nafplio by car?" or "tolls to Thessaloniki and back?" and get:

- **Tolls**: every toll plaza and ramp booth the route pays, from [mydiodia.gr](https://mydiodia.gr/)'s 212 stations and the operators' 2026 car prices; totals agree with the site's own calculator.
- **Fuel**: the litres your car burns on each stretch at its speed, priced at real stations (the Ministry's fuelprices.gr data, through the fuelGR feed): where to **fill up before you go**, and a stop on the way only when the tank needs one.
- **The cheapest stations** on the way, of the brands you prefer if you have any, and the cheapest near any place.
- Drive time with today's traffic and a Google Maps link, there and back.

The tool is standard-library Python (3.10+), so there's nothing to install besides the plugin.

## Install

```
/plugin marketplace add korsicheg/claude-marketplace
/plugin install trip-cost@korsicheg-marketplace
```

Then give it a **Google Maps key** with the **Routes API** enabled, as for athens-transit: the plugin takes the key of your project's Maps MCP server (`https://mapstools.googleapis.com/mcp`, whatever it's called) or `GOOGLE_MAPS_API_KEY`.

## Your car and your places

- **Your car**: until you say which car you drive, costs are for a typical compact petrol car. Tell Claude your car (or what it burns) and the fuel brands you prefer, and it saves them in `.trip/car.json` in your project folder.
- **Saved places**: `home`, `work` and the others you saved with the athens-transit plugin work here too (`.oasa/places.json`); `TRIP_PLACES` points at another file.
- **Where you are**: to plan from where your phone is (`here`), set `TRIP_LOCATION` to a JSON file your own bridge keeps up to date with your latest shared position, e.g. `{"latitude": 37.97, "longitude": 23.73, "updated": 1791493200, "live_until": 1791494100}` (unix times; `live_until` is optional). Without it, you say where you start.

## Your data

The car profile and the toll and price caches live in `.trip/` in your own project folder. Nothing personal is in the plugin, and your key stays in your MCP settings.

## Development

`./check` runs the tests (pytest, on Python 3.10) and ruff through `uvx`.

Data: tolls from [mydiodia.gr](https://mydiodia.gr/), fuel prices from [fuelprices.gr](https://www.fuelprices.gr/) via [fuelGR](https://github.com/athanasso/fuelGR-scraper), routes from [Google Maps Platform](https://developers.google.com/maps).
