"""Tests for the aggregation properties on the core data models."""
from datetime import datetime

from models import Workout, Exercise, ExerciseSet, BodyPart


def _set(weight: float, reps: int) -> ExerciseSet:
    return ExerciseSet("W", datetime(2026, 1, 1), set_number=1, weight=weight, reps=reps)


def test_exercise_number_of_times_performed():
    exercise = Exercise("Bench Press", body_part=BodyPart.PECS)
    exercise.exercise_sets.extend([_set(100, 10), _set(110, 8)])
    assert exercise.number_of_times_performed == 2


def test_exercise_last_performed_returns_latest_date():
    exercise = Exercise("Bench Press")
    exercise.exercise_sets.append(
        ExerciseSet("W", "2026-01-01", set_number=1, weight=100, reps=10)
    )
    exercise.exercise_sets.append(
        ExerciseSet("W", "2026-03-15", set_number=1, weight=120, reps=6)
    )
    assert exercise.last_performed == "2026-03-15"


def test_exercise_last_performed_empty_is_none():
    assert Exercise("Bench Press").last_performed is None


def test_workout_aggregate_properties():
    workout = Workout("Push", datetime(2026, 1, 1), duration=60)
    bench = Exercise("Bench Press", body_part=BodyPart.PECS)
    curl = Exercise("Bicep Curl", body_part=BodyPart.BICEPS)
    bench.exercise_sets.extend([_set(100, 10), _set(110, 8)])
    curl.exercise_sets.append(_set(30, 12))
    workout.exercises.extend([bench, curl])

    assert workout.number_of_exercises == 2
    assert workout.number_of_exercise_sets == 3
    assert workout.total_weight_lifted == 240
    assert workout.total_reps_performed == 30


def test_empty_workout_aggregates_are_zero():
    workout = Workout("Rest", datetime(2026, 1, 1), duration=0)
    assert workout.number_of_exercises == 0
    assert workout.number_of_exercise_sets == 0
    assert workout.total_weight_lifted == 0
    assert workout.total_reps_performed == 0
