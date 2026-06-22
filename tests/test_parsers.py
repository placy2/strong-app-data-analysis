"""Tests for CSV parsing and the workout/exercise builder helpers."""
from datetime import datetime

from models import Workout, BodyPart
from parsers import (
    get_or_create_workout,
    get_or_create_exercise,
    load_workouts,
    parse_body_part,
    parse_csv,
)


def test_get_or_create_workout_creates_then_reuses():
    workouts = {}
    key = ("2026-01-01 09:00:00", "Push")
    first = get_or_create_workout(
        workouts, key, "Push", datetime(2026, 1, 1), 60, ""
    )
    second = get_or_create_workout(
        workouts, key, "Push", datetime(2026, 1, 1), 60, ""
    )
    assert first is second
    assert len(workouts) == 1


def test_get_or_create_exercise_creates_then_reuses():
    workout = Workout("Push", datetime(2026, 1, 1), duration=60)
    first = get_or_create_exercise(workout, "Bench Press", BodyPart.PECS)
    second = get_or_create_exercise(workout, "Bench Press", BodyPart.PECS)
    assert first is second
    assert workout.number_of_exercises == 1


def test_parse_body_part_known_mapping_returns_enum():
    mappings = {"Bench Press": "Pecs"}
    assert parse_body_part("Bench Press", mappings) is BodyPart.PECS


def test_parse_body_part_unknown_returns_none():
    assert parse_body_part("Unknown Lift", {}) is None


def test_parse_body_part_invalid_value_falls_back_to_a_body_part():
    # A mapping pointing at a string with no matching enum member falls back to a random part.
    result = parse_body_part("Bench Press", {"Bench Press": "NotARealPart"})
    assert result in list(BodyPart)


def test_parse_csv_builds_object_graph(sample_csv, tmp_path):
    mapping_file = tmp_path / "mappings.json"
    mapping_file.write_text(
        '{"Bench Press": "Pecs", "Bicep Curl": "Biceps", "Squat": "Quads"}',
        encoding="utf-8",
    )

    workouts = parse_csv(sample_csv, mappings_path=str(mapping_file))

    # Two distinct (date, name) keys -> two workouts.
    assert len(workouts) == 2
    by_name = {w.name: w for w in workouts}

    push = by_name["Push"]
    assert push.duration == 60
    assert push.number_of_exercises == 2
    # Warmup ("W") + regular set on bench, plus one curl set.
    assert push.number_of_exercise_sets == 3

    bench = next(e for e in push.exercises if e.name == "Bench Press")
    assert bench.body_part is BodyPart.PECS
    # Warmup row parses to set_number 0, regular row to 1.
    assert sorted(s.set_number for s in bench.exercise_sets) == [0, 1]

    legs = by_name["Legs"]
    assert legs.duration == 45
    assert legs.number_of_exercise_sets == 1


def test_load_workouts_missing_file_returns_empty(monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog", "/no/such/file.csv"])
    assert load_workouts() == []


def test_load_workouts_no_argument_returns_empty(monkeypatch):
    monkeypatch.setattr("sys.argv", ["prog"])
    assert load_workouts() == []


def test_load_workouts_parse_error_returns_empty(monkeypatch, sample_csv):
    monkeypatch.setattr("sys.argv", ["prog", sample_csv])

    def boom(_path):
        raise ValueError("bad data")

    monkeypatch.setattr("parsers.parse_csv", boom)
    assert load_workouts() == []


def test_load_workouts_parses_valid_file(monkeypatch, sample_csv):
    monkeypatch.setattr("sys.argv", ["prog", sample_csv])
    workouts = load_workouts()
    assert len(workouts) == 2
