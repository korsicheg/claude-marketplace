import json

from oasabus import settings
from oasabus.location import latest


def write_config(tmp_path, monkeypatch, servers):
    config = tmp_path / ".claude.json"
    config.write_text(json.dumps({"projects": {str(tmp_path / "ws"): {"mcpServers": servers}}}))
    monkeypatch.setattr(settings, "CLAUDE_JSON", config)


def test_the_key_comes_from_the_projects_maps_server_whatever_its_name(tmp_path, monkeypatch):
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    write_config(tmp_path, monkeypatch, {
        "other": {"url": "https://example.com/mcp"},
        "my-maps": {"url": "https://mapstools.googleapis.com/mcp", "headers": {"X-Goog-Api-Key": "K", "X-User": "u"}}})
    headers = settings.maps_headers(tmp_path / "ws")
    assert headers == {"X-Goog-Api-Key": "K", "X-User": "u"}


def test_an_environment_key_wins_and_no_key_is_empty(tmp_path, monkeypatch):
    write_config(tmp_path, monkeypatch, {})
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    assert settings.maps_headers(tmp_path / "ws") == {}
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "E")
    assert settings.maps_headers(tmp_path / "ws") == {"X-Goog-Api-Key": "E"}


def test_each_person_keeps_their_data_in_their_own_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("OASA_WORKSPACE", str(tmp_path / "ws"))
    assert settings.load().data == tmp_path / "ws" / ".oasa"


def test_a_plain_session_has_no_location_and_no_alert_command(monkeypatch):
    monkeypatch.delenv("OASA_LOCATION", raising=False)
    monkeypatch.delenv("OASA_NOTIFY", raising=False)
    loaded = settings.load()
    assert loaded.location is None and loaded.notify is None
    assert latest(loaded.location) is None


def test_a_setup_plugs_in_its_location_file_and_alert_command(tmp_path, monkeypatch):
    shared = tmp_path / "where.json"
    shared.write_text(json.dumps({"latitude": 37.97, "longitude": 23.73, "updated": 1000, "live_until": 1900}))
    monkeypatch.setenv("OASA_LOCATION", str(shared))
    monkeypatch.setenv("OASA_NOTIFY", "/opt/bridge/notify --to 'my phone'")
    loaded = settings.load()
    assert loaded.notify == ["/opt/bridge/notify", "--to", "my phone"]
    location = latest(loaded.location)
    assert (location.point.lat, location.point.lon, location.updated) == (37.97, 23.73, 1000)
    assert location.is_live(1500) and not location.is_live(2000)
