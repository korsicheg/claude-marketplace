import sys
import time
from datetime import timedelta

import pytest
from fakes import EAST, FakeTelematics, arrival
from oasabus import cli, watch
from oasabus.location import SharedLocation
from oasabus.planner import athens_now
from oasabus.telematics import OasaUnavailable
from oasabus.watch import CommandNotifier, PrintNotifier, Watcher, WatchPlan


@pytest.fixture(autouse=True)
def no_signals(monkeypatch):
    monkeypatch.setattr(watch.signal, "signal", lambda *a: None)


class FakeNotifier:
    def __init__(self):
        self.sent, self.edits = [], []

    def send(self, text):
        self.sent.append(text)
        return str(len(self.sent))

    def edit(self, message_id, text):
        self.edits.append((message_id, text))


def plan(**overrides):
    fields = {"title": "Α1 → East End", "vehicle": "bus", "stop_name": "Stop E2", "stop_point": EAST[1].point,
                  "origin": EAST[3].point, "walk_m": 900, "walk_min": 12.0, "live_stop": "E2", "live_routes": [1],
                  "after_boarding": "Get off at **Stop E9**."}
    return WatchPlan(**(fields | overrides))


def watcher(arrivals, location=None, **overrides):
    oasa = FakeTelematics(arrivals={"E2": arrivals})
    return Watcher(plan(**overrides), oasa, FakeNotifier(), lambda: location), oasa


def live_at(point):
    now = time.time()
    return SharedLocation(point, now, now + 900, 10)


def test_it_says_when_to_leave_and_only_once():
    w, oasa = watcher([arrival(20)])
    assert not w.tick()
    assert w.notifier.sent == [w.status_text] and "Leave in **7 min**" in w.status_text

    oasa.arrivals_by_stop["E2"] = [arrival(13)]
    w.tick()
    w.tick()
    leave_now = [m for m in w.notifier.sent if m.startswith("🚶 **Leave now**")]
    assert leave_now == ["🚶 **Leave now** for **Stop E2**: the Α1 → East End comes in 13 min, 12 min walk."]


def test_without_a_live_location_it_ends_when_the_bus_leaves():
    w, oasa = watcher([arrival(13)])
    w.tick()
    oasa.arrivals_by_stop["E2"] = [arrival(1)]
    w.tick()
    oasa.arrivals_by_stop["E2"] = []
    assert w.tick()
    assert w.notifier.sent[-1] == "🚌 Your Α1 → East End has left Stop E2. Get off at **Stop E9**."
    assert w.notifier.edits[-1][1].endswith("*✅ Done watching.*")


def test_a_live_location_at_the_stop_means_on_board():
    w, oasa = watcher([arrival(1)], location=live_at(EAST[1].point))
    w.tick()
    assert "You're at the stop" in w.status_text
    oasa.arrivals_by_stop["E2"] = []
    assert w.tick()
    assert w.notifier.sent[-1] == "✅ On board? Get off at **Stop E9**."


def test_a_live_location_far_away_means_missed_and_it_moves_to_the_next_bus():
    w, oasa = watcher([arrival(13, "V1"), arrival(30, "V2")], location=live_at(EAST[3].point))
    w.tick()
    oasa.arrivals_by_stop["E2"] = [arrival(1, "V1"), arrival(17, "V2")]
    w.tick()
    oasa.arrivals_by_stop["E2"] = [arrival(16, "V2")]
    assert not w.tick()
    assert "😕 Missed the Α1 → East End. Looking at the next one." in w.notifier.sent
    assert w.target.key == "V2"


def test_timetable_departures_follow_the_live_ones():
    later = (athens_now() + timedelta(minutes=40)).isoformat()
    w, _ = watcher([arrival(20)], scheduled=[later])
    assert [d.live for d in w.departures()] == [True, False]


def test_an_oasa_outage_is_not_a_departure():
    w, oasa = watcher([arrival(13)])
    w.tick()
    oasa.arrivals_by_stop["E2"] = [arrival(1)]
    w.tick()

    def down(stop_code):
        raise OasaUnavailable("no answer")
    oasa.arrivals = down
    with pytest.raises(OasaUnavailable):
        w.tick()
    assert not any("has left" in m for m in w.notifier.sent)


def test_the_alert_command_gets_send_and_edit_with_their_arguments():
    echo = [sys.executable, "-c", "import sys; print(' | '.join(sys.argv[1:]))"]
    notifier = CommandNotifier(echo)
    assert notifier.send("🚶 Leave now") == "send | 🚶 Leave now"
    notifier.edit("7", "Done")  # no error


def test_a_failing_alert_command_raises_with_its_error():
    notifier = CommandNotifier([sys.executable, "-c", "import sys; sys.exit('no chat')"])
    with pytest.raises(RuntimeError, match="no chat"):
        notifier.send("hi")


def test_a_foreground_watch_prints_messages_and_keeps_its_log_off_stdout(capsys):
    watch.log("skipped a look: OASA is down")
    PrintNotifier().send("🚶 **Leave now**")
    out, err = capsys.readouterr()
    assert out == "🚶 **Leave now**\n\n" and "skipped a look" in err


def test_a_background_watch_needs_an_alert_command(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("OASA_WORKSPACE", str(tmp_path))
    monkeypatch.delenv("OASA_NOTIFY", raising=False)
    plan().save(tmp_path / ".oasa" / "last-plan.json")
    assert cli.main(["watch"]) == 5
    assert "oasa watch --foreground" in capsys.readouterr().err
