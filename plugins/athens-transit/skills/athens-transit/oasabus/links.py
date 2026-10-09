"""Links for following buses and trolleys live, next to the Google Maps ones: OASA's own tracker
(the site behind its Telematics app; no links to a single line or stop) and the unofficial live
map at bus.haroldpoi.dev (angelospk/athens-transit-map), which opens on chosen lines."""
from urllib.parse import quote

OASA_TRACKER = "https://telematics.oasa.gr/en/"
LIVE_MAP = "https://bus.haroldpoi.dev/?l="


def live_map(lines: list[str]) -> str:
    return LIVE_MAP + quote(",".join(dict.fromkeys(lines)), safe=",")


def follow_live(lines: list[str]) -> str:
    """'📡 Follow live: …' for these bus or trolley lines, as Markdown."""
    names = ", ".join(dict.fromkeys(lines))
    return f"📡 Follow live: [{names} on the live map]({live_map(lines)}) · [OASA tracker]({OASA_TRACKER})"
