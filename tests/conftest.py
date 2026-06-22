"""Shared pytest fixtures for the test suite.

Test imports such as ``from models import Workout`` resolve because
``pythonpath = ["src"]`` is configured in pyproject.toml, so no manual
``sys.path`` manipulation is needed here.
"""
from datetime import datetime

import pytest

from models import Workout, Exercise, ExerciseSet, BodyPart


@pytest.fixture
def sample_workouts() -> list[Workout]:
    """Two in-memory workouts with exercises and sets for model/filter tests."""
    bench = Exercise("Bench Press", body_part=BodyPart.PECS)
    squat = Exercise("Squat", body_part=BodyPart.QUADS)
    curl = Exercise("Bicep Curl", body_part=BodyPart.BICEPS)

    push_day = Workout("Push", datetime(2026, 1, 1, 9, 0, 0), duration=60)
    leg_day = Workout("Legs", datetime(2026, 2, 1, 9, 0, 0), duration=45)

    bench.exercise_sets.append(
        ExerciseSet(push_day.name, push_day.date, set_number=1, weight=100, reps=10)
    )
    bench.exercise_sets.append(
        ExerciseSet(push_day.name, push_day.date, set_number=2, weight=110, reps=8)
    )
    curl.exercise_sets.append(
        ExerciseSet(push_day.name, push_day.date, set_number=1, weight=30, reps=12)
    )
    squat.exercise_sets.append(
        ExerciseSet(leg_day.name, leg_day.date, set_number=1, weight=200, reps=5)
    )

    push_day.exercises.extend([bench, curl])
    leg_day.exercises.append(squat)
    return [push_day, leg_day]


@pytest.fixture
def sample_csv(tmp_path) -> str:
    """Write a Strong-format CSV (incl. a warmup set and two workouts) and return its path."""
    rows = [
        "Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Notes,Workout Notes",
        '2026-01-01 09:00:00,Push,1h 0m,Bench Press,W,45,10,,Felt good',
        '2026-01-01 09:00:00,Push,1h 0m,Bench Press,1,100,8,,Felt good',
        '2026-01-01 09:00:00,Push,1h 0m,Bicep Curl,1,30,12,light,Felt good',
        '2026-02-01 09:00:00,Legs,45m,Squat,1,200,5,,',
    ]
    csv_path = tmp_path / "strong.csv"
    csv_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return str(csv_path)
