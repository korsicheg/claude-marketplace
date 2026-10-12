"""Whose trip this is. The same code serves everyone who installs it: each person's saved places,
plans and cache live in their own Claude Code project folder, under .oasa/, and Google Maps
uses the key of their own Maps MCP server.

Every setting can be given in the environment; the defaults fit a plain Claude Code session:
    OASA_WORKSPACE       the project folder (default: the folder the Claude Code session runs in)
    GOOGLE_MAPS_API_KEY  a key for Maps Grounding Lite and the Routes API (default: the key of the
                         project's MCP server at mapstools.googleapis.com, from ~/.claude.json)
    OASA_LOCATION        a JSON file with the person's latest position, kept up to date by whatever
                         gets it from their phone (see location.py); without it, "here" is unknown
    OASA_NOTIFY          a command that delivers leave-now alerts in the background: called as
                         `COMMAND send TEXT` (printing the message's id) and `COMMAND edit ID TEXT`;
                         without it, `oasa watch --foreground` prints the alerts instead
"""
import json
import os
import shlex
from dataclasses import dataclass
from pathlib import Path

CLAUDE_JSON = Path.home() / ".claude.json"
MAPS_ENDPOINT = "https://mapstools.googleapis.com/mcp"


@dataclass(frozen=True)
class Settings:
    workspace: Path
    maps_headers: dict  # what the Maps endpoint needs: the key, and any headers of the person's server
    location: Path | None
    notify: list[str] | None  # the alert command and its own arguments

    @property
    def data(self) -> Path:
        return self.workspace / ".oasa"

    @property
    def maps_key(self) -> str | None:
        return self.maps_headers.get("X-Goog-Api-Key")


def load() -> Settings:
    workspace = Path(os.environ.get("OASA_WORKSPACE") or session_folder() or Path.cwd())
    return Settings(
        workspace=workspace,
        maps_headers=maps_headers(workspace),
        location=Path(os.environ["OASA_LOCATION"]) if os.environ.get("OASA_LOCATION") else None,
        notify=shlex.split(os.environ.get("OASA_NOTIFY", "")) or None)


def session_folder() -> Path | None:
    """The folder the Claude Code session runs in (Linux): its Bash commands may cd elsewhere."""
    try:
        return Path(f"/proc/{os.environ['CLAUDE_PID']}/cwd").resolve(strict=True)
    except (KeyError, OSError):
        return None


def maps_headers(workspace: Path) -> dict:
    if os.environ.get("GOOGLE_MAPS_API_KEY"):
        return {"X-Goog-Api-Key": os.environ["GOOGLE_MAPS_API_KEY"]}
    try:
        servers = json.loads(CLAUDE_JSON.read_text())["projects"][str(workspace)]["mcpServers"]
    except (OSError, ValueError, KeyError):
        return {}
    maps = [s for s in servers.values() if str(s.get("url", "")).startswith(MAPS_ENDPOINT)]
    return dict(maps[0].get("headers", {})) if maps else {}
