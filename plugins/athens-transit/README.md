# athens-transit

Athens public transport for Claude Code. Ask "040 to Syntagma" or "how do I get to the airport?" and get:

- **Buses and trolleys live**, from OASA's own predictions: which stop to walk to (up to three nearby stops are compared by when you'd arrive, not just the nearest), the next buses and how many stops away they are, when to leave, where to get off.
- **Metro, tram and suburban rail**, from Google's Routes API (the timetable; no live metro data exists), with every bus or trolley leg of the journey switched to OASA's live time.
- **Leave-now alerts** on Telegram, in the background without Claude: one status message counting down, a "🚶 Leave now" ping, a live location followed, a missed bus noticed, and where to get off once the bus has left.
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

## Telegram

Answers are Markdown made for Telegram. Shared locations and leave-now alerts expect a Telegram bridge that gives Claude Code a `tg` command (`tg send`, `tg edit`, `--chat ID`), the person's chat in `TG_CHAT_ID`, and their latest shared location in `~/assistant/state/locations/<chat id>.json`. Every path can be changed with an environment variable; see `skills/athens-transit/oasabus/settings.py`.

## Your data

Saved places, the last plan, the cache and the alert log live in `.oasa/` in your own project folder. Nothing personal is in the plugin, and your key stays in your MCP settings.

## Development

`./check` runs the tests (pytest) and ruff through `uvx`.

Data: [OASA telematics](https://telematics.oasa.gr/en/) (unofficial use of its public API), [Google Maps Platform](https://developers.google.com/maps), live map by [athens-transit-map](https://github.com/angelospk/athens-transit-map).
