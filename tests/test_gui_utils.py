"""Tests for the pure GUI helper functions."""
import types
from datetime import date

from utils import gui_utils
from utils.gui_utils import filter_workouts


def test_filter_workouts_keeps_in_range(sample_workouts):
    # sample_workouts span 2026-01-01 (Push) and 2026-02-01 (Legs).
    result = filter_workouts(sample_workouts, [date(2026, 1, 1), date(2026, 1, 31)])
    assert [w.name for w in result] == ["Push"]


def test_filter_workouts_inclusive_bounds(sample_workouts):
    result = filter_workouts(sample_workouts, [date(2026, 1, 1), date(2026, 2, 1)])
    assert len(result) == 2


def test_filter_workouts_non_pair_range_returns_all(sample_workouts):
    # A single-element range (mid-selection in the UI) should not filter anything out.
    result = filter_workouts(sample_workouts, [date(2026, 1, 1)])
    assert result == sample_workouts


def test_initialize_page_seeds_workouts_once(monkeypatch, sample_workouts):
    fake_state = {}
    monkeypatch.setattr(gui_utils, "st", types.SimpleNamespace(session_state=fake_state))
    monkeypatch.setattr(gui_utils, "load_workouts", lambda: sample_workouts)

    gui_utils.initialize_page()
    assert fake_state["workouts"] == sample_workouts

    # A second call must not reload over an existing value.
    monkeypatch.setattr(gui_utils, "load_workouts", lambda: [])
    gui_utils.initialize_page()
    assert fake_state["workouts"] == sample_workouts


def test_render_page_with_workouts_passes_date_bounds(monkeypatch, sample_workouts):
    fake_state = {"workouts": sample_workouts}
    monkeypatch.setattr(gui_utils, "st", types.SimpleNamespace(session_state=fake_state))

    captured = {}

    def render(workouts, min_date, max_date):
        captured["args"] = (workouts, min_date, max_date)

    gui_utils.render_page_with_workouts(render)
    assert captured["args"] == (sample_workouts, date(2026, 1, 1), date(2026, 2, 1))


def test_render_page_with_workouts_empty_writes_message(monkeypatch):
    messages = []
    fake_st = types.SimpleNamespace(
        session_state={"workouts": []}, write=messages.append
    )
    monkeypatch.setattr(gui_utils, "st", fake_st)

    gui_utils.render_page_with_workouts(lambda *a: None)
    assert messages and "No data available" in messages[0]
