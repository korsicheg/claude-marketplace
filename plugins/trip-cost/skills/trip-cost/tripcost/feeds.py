"""Downloads kept in the data folder: a fresh copy is fetched once the saved one is too old, and the
saved one is used when the source can't be reached."""
import time
import urllib.error
import urllib.request
from pathlib import Path

TIMEOUT = 30
USER_AGENT = "trip-cost/1.0 (personal trip planner)"


class FeedUnavailable(Exception):
    pass


def fresh(saved: Path, max_age_s: float) -> bool:
    return saved.exists() and time.time() - saved.stat().st_mtime < max_age_s


def cached_download(url: str, saved: Path, max_age_s: float) -> bytes:
    if fresh(saved, max_age_s):
        return saved.read_bytes()
    try:
        content = download(url)
    except FeedUnavailable:
        if saved.exists():
            return saved.read_bytes()
        raise
    save(saved, content)
    return content


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise FeedUnavailable(f"{url}: {error}") from error


def save(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    partial.write_bytes(content)
    partial.replace(path)
