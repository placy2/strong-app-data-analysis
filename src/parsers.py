"""This module defines functions to parse workout data from a CSV file."""
import csv
import random
import os
import sys
from datetime import datetime
from typing import Dict, Tuple, List, Optional

from models import Workout, Exercise, ExerciseSet, BodyPart
from utils.parse_utils import parse_duration, parse_set_order, parse_to_int, load_mappings

# pylint: disable=too-many-arguments,too-many-positional-arguments
def get_or_create_workout(
        workouts: Dict[Tuple[str, str], Workout],
        key: Tuple[str, str],
        name: str,
        date: datetime,
        duration: int,
        notes: str
    ) -> Workout:
    """Helper function to get or create a Workout object in the workouts dictionary."""
    if key not in workouts:
        workout = Workout(name, date, duration, notes)
        workouts[key] = workout
    else:
        workout = workouts[key]
    return workout


def get_or_create_exercise(
        workout: Workout, exercise_name: str, body_part: Optional[BodyPart]
    ) -> Exercise:
    """Helper function to get or create an Exercise object in a Workout's exercises list."""
    for e in workout.exercises:
        if e.name == exercise_name:
            return e
    exercise_obj = Exercise(exercise_name, body_part=body_part)
    workout.exercises.append(exercise_obj)
    return exercise_obj

def load_workouts() -> list[Workout]:
    """Load workouts from CSV. Path can be overridden by a command-line argument."""
    data_path = ""
    if len(sys.argv) > 1:
        data_path = sys.argv[1]

    # Check if file exists before parsing
    if not os.path.isfile(data_path):
        # Return an empty list if no valid file is found
        return []

    try:
        return parse_csv(data_path)
    #TODO: Add more specific exception handling for file parsing errors, etc.
    # pylint: disable=broad-exception-caught
    except Exception:
        # If there's a parsing error, return an empty list
        return []

def parse_body_part(exercise_name: str, mappings: Dict[str, str]) -> Optional[BodyPart]:
    """Parse the body part for a given exercise name using the provided mappings."""
    if exercise_name in mappings:
        # print(f"Found mapping for '{exercise_name}': {mappings[exercise_name]}")
        body_part_str = mappings[exercise_name]
        try:
            return next(bp for bp in BodyPart if bp.value == body_part_str)
        except StopIteration:
            return random.choice(list(BodyPart))
    print(f"No mapping found for '{exercise_name}', assigning random body part.")
    return None


def parse_csv(file_path: str, mappings_path: Optional[str] = None) -> List[Workout]:
    """
    Parses CSV from Strong app. Handles inserting data into a dict with key (date, workout name).
    """
    default_path = "../data/exercise_body_part_mapping.json"
    mappings = load_mappings(mappings_path) if mappings_path else load_mappings(default_path)
    workouts: Dict[Tuple[str, str], Workout] = {}

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row["Date"]
            workout_name = row["Workout Name"]
            duration_str = row["Duration"]
            exercise_name = row["Exercise Name"]
            set_order = row["Set Order"]
            weight = row["Weight"]
            reps = row["Reps"]
            notes = row["Notes"] or ""
            workout_notes = row["Workout Notes"] or ""

            parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            set_number = parse_set_order(set_order) if set_order else 0
            weight = parse_to_int(weight) if weight else 0
            reps = parse_to_int(reps) if reps else 0
            duration = parse_duration(duration_str) if duration_str else 0

            workout_key = (date_str, workout_name)
            workout = get_or_create_workout(
                workouts,
                workout_key,
                workout_name,
                parsed_date,
                duration,
                workout_notes
            )

            body_part = parse_body_part(exercise_name, mappings)
            exercise_obj = get_or_create_exercise(workout, exercise_name, body_part)

            exercise_set = ExerciseSet(
                workout=workout.name,
                date=parsed_date,
                set_number=set_number,
                weight=weight,
                reps=reps,
                notes=notes,
            )
            exercise_obj.exercise_sets.append(exercise_set)

    return list(workouts.values())
