# athens-transit

Athens public transport for Claude Code. Ask "040 to Syntagma" or "how do I get to the airport?" and get:

- **Buses and trolleys live**, from OASA's own predictions: which stop to walk to (up to three nearby stops are compared by when you'd arrive, not just the nearest), the next buses and how many stops away they are, when to leave, where to get off.
- **Metro, tram and suburban rail**, from Google's Routes API (the timetable; no live metro data exists), with every bus or trolley leg of the journey switched to OASA's live time.
- **Leave-now alerts**: one status message counting down, a "🚶 Leave now" ping, a live location followed, a missed bus noticed, and where to get off once the bus has left. Claude passes them on in the session, or your own messaging command sends them in the background without Claude.
- Links to Google Maps, OASA's tracker and a live map of the line.

The tool is standard-library Python (3.10+), so there's nothing to install besides the plugin.

## Install

```
/plugin marketplace add korsicheg/claude-marketplace
/plugin install athens-transit@korsicheg-marketplace
```

Then give it a **Google Maps key** (each person their own):

1. In Google Cloud, enable **Maps Grounding Lite API** and **Routes API** on a project with billing, and create an API key restricted to those two.
2. Add Google's Maps MCP server to your project (local scope keeps the key yours):

   ```
   claude mcp add --scope local --transport http maps https://mapstools.googleapis.com/mcp --header "X-Goog-Api-Key: YOUR_KEY"
   ```

   The plugin finds the key there by its URL, whatever the server is called. Or set `GOOGLE_MAPS_API_KEY`.

Without a key, plans for a named bus line still work from coordinates and saved places, with estimated walks.

## Alerts and your location

Out of the box, answers are Markdown and Claude passes the alerts on right in the session (`oasa watch --foreground`, followed with Claude Code's Monitor tool). You tell Claude where you are, or save places such as home and work.

To get the alerts on your phone, or to plan from where your phone is, plug in your own messaging bridge with two optional environment variables, for example in your project's `.claude/settings.json`:

```json
{ "env": { "OASA_NOTIFY": "/path/to/notify", "OASA_LOCATION": "/path/to/location.json" } }
```

- `OASA_NOTIFY`: a command that sends a message with `COMMAND send TEXT`, printing the message's id, and edits it with `COMMAND edit ID TEXT`. With it, `oasa watch` runs in the background, without Claude.
- `OASA_LOCATION`: a JSON file your bridge keeps up to date with your latest shared position, e.g. `{"latitude": 37.97, "longitude": 23.73, "updated": 1791493200, "live_until": 1791494100}` (unix times; `live_until` and `accuracy_m` are optional). With it, `here` is where you are, and the alerts follow a live location.

The other settings are in `skills/athens-transit/oasabus/settings.py`.

## Your data

Saved places, the last plan, the cache and the alert log live in `.oasa/` in your own project folder. Nothing personal is in the plugin, and your key stays in your MCP settings.

## Development

`./check` runs the tests (pytest) and ruff through `uvx`.

Data: [OASA telematics](https://telematics.oasa.gr/en/) (unofficial use of its public API), [Google Maps Platform](https://developers.google.com/maps), live map by [athens-transit-map](https://github.com/angelospk/athens-transit-map).
