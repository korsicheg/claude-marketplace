"""Whose trip this is. The same code serves everyone who installs it: each person's saved places,
plans and cache live in their own Claude Code project folder, under .oasa/, and Google Maps
uses the key of their own Maps MCP server.

Every setting can be given in the environment; the defaults fit a Claude Code session:
    OASA_WORKSPACE       the project folder (default: the folder the Claude Code session runs in)
    GOOGLE_MAPS_API_KEY  a key for Maps Grounding Lite and the Routes API (default: the key of the
                         project's MCP server at mapstools.googleapis.com, from ~/.claude.json)
    TG_CHAT_ID           the person's Telegram chat, for leave-now alerts
    OASA_LOCATIONS       a folder of <chat id>.json files with the person's latest shared location
                         (default ~/assistant/state/locations, where the Telegram front desk keeps them)
    OASA_TG              the command that sends Telegram messages (default: tg on the PATH, or
                         ~/assistant/bin/tg)
"""
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

CLAUDE_JSON = Path.home() / ".claude.json"
MAPS_ENDPOINT = "https://mapstools.googleapis.com/mcp"
FRONT_DESK = Path.home() / "assistant"


@dataclass(frozen=True)
class Settings:
    workspace: Path
    maps_headers: dict  # what the Maps endpoint needs: the key, and any headers of the person's server
    telegram_chat: str | None
    locations: Path
    tg: str | None

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
        telegram_chat=os.environ.get("TG_CHAT_ID"),
        locations=Path(os.environ.get("OASA_LOCATIONS") or FRONT_DESK / "state" / "locations"),
        tg=os.environ.get("OASA_TG") or shutil.which("tg") or existing(FRONT_DESK / "bin" / "tg"))


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


def existing(path: Path) -> str | None:
    return str(path) if path.exists() else None
