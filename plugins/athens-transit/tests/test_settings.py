import json

from oasabus import settings


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
    monkeypatch.setenv("TG_CHAT_ID", "42")
    loaded = settings.load()
    assert loaded.data == tmp_path / "ws" / ".oasa"
    assert loaded.telegram_chat == "42"
