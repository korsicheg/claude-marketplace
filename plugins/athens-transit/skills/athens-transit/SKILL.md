---
name: athens-transit
description: Athens public transport — live bus and trolley times from OASA, metro/tram/suburban rail and whole journeys from Google, which stop to walk to, when to leave, and leave-now alerts on Telegram. Use whenever the user names an Athens bus, trolley, metro or tram line, asks how to get somewhere in Athens, when their bus comes, or shares their location for a trip.
---

# Athens transit

Everything goes through one command in this skill's folder. Below, `oasa` means:

```bash
python3 -I <this skill's base directory>/oasa
```

## Planning a trip

```bash
oasa go "<destination>" [--line <line>] [--from <where>] [--format telegram|voice|json]
```

- **A bus or trolley line** (`--line 040`, `A1`, `11`; Latin or Greek letters, leading zeros optional): that line with **OASA's live predictions**. It picks the direction, compares up to three nearby stops by when the user would arrive, and says where to get off.
- **No line, or a metro/tram line** (`M1`, `M3`, `T6`): Google's transit journeys (metro, tram, suburban rail, buses), every bus or trolley ride switched to OASA's live time. Metro and tram times are the timetable: no live metro data exists.
- `--from` defaults to `here`, the latest location the user shared on Telegram (live, or under 30 min old). Both ends also take a saved place (`home`, `work`), `lat,lon`, or anything Google Maps finds.
- The default output is a finished Telegram message in Markdown, with the Google Maps links Google's terms require and links to follow the bus live. Send it as is: `oasa go … | tg send`.
- `--format voice` gives one or two spoken sentences; `--format json` gives every detail (stops, codes, all buses).

## Flow

1. If the user asks how to get somewhere without saying how (no line, no "bus", "metro", "by car"…), **ask first: car or public transport?** Don't assume. By car, use a Google Maps driving route if you have one, not this tool.
2. Run `oasa go`. **Exit code 2** means there's no usable location: ask the user to share it on Telegram (📎 → Location → **Share My Live Location**, 15 min is enough, so the alerts can follow them), or to say where they are (`--from home`). A shared location arrives with a `location:` attachment line; then run it again.
3. Send the output. Then start the alerts, unless they're already on the way or only checking:

   ```bash
   oasa watch
   ```

   It watches the plan `oasa go` just saved, in the background without Claude: one status message it keeps updating, **"🚶 Leave now"** at the right moment, following the user's live location if they share one, noticing a missed bus, and ending once the bus has left (with where to get off). One watch at a time; a new one replaces it. `oasa watch --stop` when the user says stop or cancel; `oasa watch --status` to check.

Exit codes: 3 no such place or line, or the line doesn't go that way (say so and offer the trip without the line); 4 OASA or Google didn't answer, or there's no Google Maps key (see Setup); 5 alerts can't reach Telegram.

## Saved places

```bash
oasa places                                  # list
oasa places add work "Kifisias 115, Athens"  # an address, a place name, lat,lon, or here
oasa places remove work
```

Save a place when the user tells you their home or work, then use the names ("040 to work").

## Siri and other voice requests

When a request carries `[location: LAT,LON]` (a Siri shortcut can append it), pass `--from "LAT,LON"` and answer with `--format voice`. Without it, use `here` if they shared a location recently, else `home` if saved, and say "from home".

## Setup and data

- Each user's data stays in their own Claude Code project folder, in `.oasa/` (places, last plan, cache, watch log).
- **Google Maps key**: taken from the project's MCP server at `mapstools.googleapis.com` (Maps Grounding Lite), or `GOOGLE_MAPS_API_KEY`. Enable the **Routes API** on the same key for journeys and metro. Without a key, line plans still work from coordinates and saved places, with estimated walks.
- **Alerts** use `TG_CHAT_ID` and a `tg` command; shared locations come from `~/assistant/state/locations/<chat id>.json`, kept by the Telegram front desk. All of it can be changed with environment variables, listed in `oasabus/settings.py`.
- Lines: `oasa lines <number or name>` lists OASA lines that match.
- OASA's API (`telematics.oasa.gr`) is reached on the address that answers (its DNS points at a dead one) and retried when it hangs; with a bus line, an OASA outage falls back to Google's timetable.
