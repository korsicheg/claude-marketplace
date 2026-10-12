"""Whose trip this is. Each person's car, downloads and saved places live in their own Claude Code
project folder, and Google uses the key of their own Maps MCP server.

Every setting can be given in the environment; the defaults fit a plain Claude Code session:
    TRIP_WORKSPACE       the project folder (default: the folder the Claude Code session runs in)
    GOOGLE_MAPS_API_KEY  a key with the Routes API enabled (default: the key of the project's MCP
                         server at mapstools.googleapis.com, from ~/.claude.json)
    TRIP_PLACES          a JSON file of saved places such as home and work (default: the athens-transit
                         plugin's, <project>/.oasa/places.json, so both mean the same places)
    TRIP_LOCATION        a JSON file with the person's latest position, kept up to date by whatever gets it
                         from their phone (see places.py); without it, "here" is unknown
"""
import json
import os
from dataclasses import dataclass
from pathlib import Path

CLAUDE_JSON = Path.home() / ".claude.json"
MAPS_ENDPOINT = "https://mapstools.googleapis.com/mcp"


@dataclass(frozen=True)
class Settings:
    workspace: Path
    maps_key: str | None
    saved_places: Path
    latest_location: Path | None

    @property
    def data(self) -> Path:
        return self.workspace / ".trip"


def load() -> Settings:
    workspace = Path(os.environ.get("TRIP_WORKSPACE") or session_folder() or Path.cwd())
    return Settings(
        workspace=workspace,
        maps_key=os.environ.get("GOOGLE_MAPS_API_KEY") or maps_server_key(workspace),
        saved_places=Path(os.environ.get("TRIP_PLACES") or workspace / ".oasa" / "places.json"),
        latest_location=Path(os.environ["TRIP_LOCATION"]) if os.environ.get("TRIP_LOCATION") else None)


def session_folder() -> Path | None:
    """The folder the Claude Code session runs in (Linux): its Bash commands may cd elsewhere."""
    try:
        return Path(f"/proc/{os.environ['CLAUDE_PID']}/cwd").resolve(strict=True)
    except (KeyError, OSError):
        return None


def maps_server_key(workspace: Path) -> str | None:
    try:
        servers = json.loads(CLAUDE_JSON.read_text())["projects"][str(workspace)]["mcpServers"]
    except (OSError, ValueError, KeyError):
        return None
    maps = [server for server in servers.values() if str(server.get("url", "")).startswith(MAPS_ENDPOINT)]
    return maps[0].get("headers", {}).get("X-Goog-Api-Key") if maps else None
