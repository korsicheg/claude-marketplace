import json
from argparse import Namespace

import pytest
from tripcost import cli, places, settings
from tripcost.car import Car, load_car
from tripcost.geo import Point


@pytest.fixture
def plain_session(tmp_path, monkeypatch):
    for name in ("TRIP_LOCATION", "TRIP_PLACES", "GOOGLE_MAPS_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TRIP_WORKSPACE", str(tmp_path))
    monkeypatch.setattr(settings, "CLAUDE_JSON", tmp_path / "no-claude.json")
    return tmp_path


def test_a_plain_session_has_no_location_and_shares_athens_transits_places(plain_session):
    loaded = settings.load()
    assert loaded.latest_location is None
    assert loaded.saved_places == plain_session / ".oasa" / "places.json"
    with pytest.raises(places.NoLocation):
        places.waypoint("here", loaded)


def test_here_and_saved_places_come_from_the_files_a_setup_names(plain_session, monkeypatch, tmp_path):
    shared = tmp_path / "where.json"
    shared.write_text(json.dumps({"latitude": 37.9, "longitude": 23.7, "updated": 0, "live_until": 4_000_000_000}))
    saved = tmp_path / "places.json"
    saved.write_text(json.dumps({"Home": {"lat": 38.1, "lon": 23.8}}))
    monkeypatch.setenv("TRIP_LOCATION", str(shared))
    monkeypatch.setenv("TRIP_PLACES", str(saved))
    loaded = settings.load()
    assert places.waypoint("here", loaded).point == Point(37.9, 23.7)
    assert places.waypoint("home", loaded).point == Point(38.1, 23.8)


def test_the_car_profile_overrides_the_typical_car_and_names_the_brands(tmp_path):
    assert load_car(tmp_path) == Car()
    (tmp_path / "car.json").write_text(json.dumps({"tank_l": 43, "brands": ["ECO", "BP"], "unknown": 1}))
    car = load_car(tmp_path)
    assert (car.tank_l, car.brands, car.fuel) == (43, ["ECO", "BP"], "u95")


@pytest.mark.parametrize("asked, brands", [(None, ("EKO", "BP")), ("any", ()), ("shell, eko", ("SHELL", "EKO"))])
def test_brands_come_from_the_command_else_the_car_profile(asked, brands):
    wanted = cli._wanted(Namespace(brands=asked, fuel=None), Car(brands=["eco", "BP"]))
    assert wanted.brands == brands


def test_without_brands_every_station_is_wanted_alike():
    wanted = cli._wanted(Namespace(brands=None, fuel="d"), Car())
    assert wanted.brands == () and wanted.fuel == "d"
