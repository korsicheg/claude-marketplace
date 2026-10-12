---
name: athens-transit
description: Athens public transport — live bus and trolley times from OASA, metro/tram/suburban rail and whole journeys from Google, which stop to walk to, when to leave, and leave-now alerts. Use whenever the user names an Athens bus, trolley, metro or tram line, asks how to get somewhere in Athens, when their bus comes, or shares their location for a trip.
---

# Athens transit

Everything goes through one command in this skill's folder. Below, `oasa` means:

```bash
python3 -I <this skill's base directory>/oasa
```

## Planning a trip

```bash
oasa go "<destination>" [--line <line>] [--from <where>] [--format markdown|voice|json]
```

- **A bus or trolley line** (`--line 040`, `A1`, `11`; Latin or Greek letters, leading zeros optional): that line with **OASA's live predictions**. It picks the direction, compares up to three nearby stops by when the user would arrive, and says where to get off.
- **No line, or a metro/tram line** (`M1`, `M3`, `T6`): Google's transit journeys (metro, tram, suburban rail, buses), every bus or trolley ride switched to OASA's live time. Metro and tram times are the timetable: no live metro data exists.
- `--from` defaults to `here`: the user's latest shared location, when the setup provides one (`OASA_LOCATION`; live, or under 30 min old). Both ends also take a saved place (`home`, `work`), `lat,lon`, or anything Google Maps finds.
- The default output is the finished answer in Markdown, with the Google Maps links Google's terms require and links to follow the bus live: give it to the user as is.
- `--format voice` gives one or two sentences to be spoken; `--format json` gives every detail (stops, codes, all buses).

## Flow

1. If the user asks how to get somewhere without saying how (no line, no "bus", "metro", "by car"…), **ask first: car or public transport?** Don't assume. By car, use a Google Maps driving route if you have one, not this tool.
2. Run `oasa go`. **Exit code 2** means there's no usable location: ask the user where they are (an address, a place, or a saved place such as `home`) and run it again with `--from`. If the setup receives their phone's location, they can share it instead; a live location lets the alerts follow them.
3. Give the user the answer. Then start the alerts, unless they're already on the way or only checking:

   ```bash
   oasa watch
   ```

   It watches the plan `oasa go` just saved, in the background without you, and sends its messages through the setup's alert command (`OASA_NOTIFY`): one status message it keeps updating, **"🚶 Leave now"** at the right moment, following the user's live location if they share one, noticing a missed bus, and ending once the bus has left (with where to get off).

   **Exit code 5** means there's no alert command. Then run `oasa watch --foreground` as a background command whose output you follow (in Claude Code, the Monitor tool, with its longest timeout; if it stops before the watch ends, run it again). It prints each message as it comes, followed by a blank line, and exits when the watch ends: pass each one on to the user.

   One watch at a time; a new one replaces it. `oasa watch --stop` when the user says stop or cancel; `oasa watch --status` to check.

Exit codes: 3 no such place or line, or the line doesn't go that way (say so and offer the trip without the line); 4 OASA or Google didn't answer, or there's no Google Maps key (see Setup); 5 no alert command for a background watch (see above).

## Saved places

```bash
oasa places                                  # list
oasa places add work "Kifisias 115, Athens"  # an address, a place name, lat,lon, or here
oasa places remove work
```

Save a place when the user tells you their home or work, then use the names ("040 to work").

## Voice answers

When the answer will be spoken (a voice assistant), use `--format voice`. When the request carries the user's coordinates, pass them as `--from "LAT,LON"`. Without them, use `here` if they shared a location recently, else `home` if saved, and say "from home".

## Setup and data

- Each user's data stays in their own Claude Code project folder, in `.oasa/` (places, last plan, cache, watch log).
- **Google Maps key**: taken from the project's MCP server at `mapstools.googleapis.com` (Maps Grounding Lite), or `GOOGLE_MAPS_API_KEY`. Enable the **Routes API** on the same key for journeys and metro. Without a key, line plans still work from coordinates and saved places, with estimated walks.
- **Location and alerts** plug in through two optional environment variables (see `oasabus/settings.py`): `OASA_LOCATION`, a JSON file with the user's latest position that something else keeps up to date (`{"latitude", "longitude", "updated", "live_until", "accuracy_m"}`, times in unix seconds, the last two optional), and `OASA_NOTIFY`, a command that takes `send TEXT` (printing the message's id) and `edit ID TEXT`, such as a messaging app's CLI.
- Lines: `oasa lines <number or name>` lists OASA lines that match.
- OASA's API (`telematics.oasa.gr`) is reached on the address that answers (its DNS points at a dead one) and retried when it hangs; with a bus line, an OASA outage falls back to Google's timetable.
