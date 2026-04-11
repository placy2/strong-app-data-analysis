import csv
import json
import os
import random
from datetime import datetime
from models import Workout, Exercise, ExerciseSet, BodyPart

# Path to your JSON mapping file
dirname = os.path.dirname(__file__)
MAPPING_FILE = os.path.join(dirname, '../data/exercise_body_part_mapping.json')
EXIT_FLAG = "__USER_EXIT__"  # A sentinel to detect user exit

def parse_duration(duration_str):
    # Examples: "53m", "1h 31m", "32h 5m"
    parts = duration_str.split()
    total_minutes = 0
    for part in parts:
        if "h" in part:
            hrs = int(part.replace("h", ""))
            total_minutes += hrs * 60
        elif "m" in part:
            mins = int(part.replace("m", ""))
            total_minutes += mins
    return total_minutes

def parse_set_order(set_order_str):
    # Handles regular set orders like "1", "2", but also non-numeric cases gracefully
    # Includes "W" (warmup set), "F" (failure set), and "D" (drop set) as special cases
    # For now special cases always result in set number 0, but this may be adjusted
    if set_order_str.isdigit():
        return int(set_order_str)
    elif set_order_str in {"W", "F", "D"}:
        return 0
    else:
        raise ValueError(f"Invalid set order: {set_order_str}")

def parse_to_int(value_str):
    # Handles cases like "0", "0.0"
    try:
        return int(float(value_str))
    except ValueError:
        return 0

def load_mappings():
    """Load exercise→body part mappings from JSON file, if it exists."""
    if os.path.isfile(MAPPING_FILE):
        with open(MAPPING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_mappings(mapping_dict):
    """Save exercise→body part mappings to JSON file."""
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping_dict, f, indent=2)

def prompt_for_body_part(exercise_name):
    """
    Prompt user at the command line for which BodyPart an exercise should belong to.
    Returns a string matching BodyPart.value, 'EXIT_FLAG' if user chooses to quit, or None if invalid.
    """
    print(f"\nExercise name: {exercise_name}")
    print("Select a body part from this list (by number), or press 'q' to quit and save:")
    body_part_list = list(BodyPart)
    for i, bp in enumerate(body_part_list, start=1):
        print(f"  {i}. {bp.value}")

    choice = input("Enter the number or 'q' to exit: ").strip().lower()
    if choice == "q":
        return EXIT_FLAG
    if not choice.isdigit():
        print("Invalid choice. Skipping.")
        return None

    idx = int(choice) - 1
    if 0 <= idx < len(body_part_list):
        return body_part_list[idx].value
    else:
        print("Invalid index. Skipping.")
        return None

def parse_csv(file_path: str) -> list[Workout]:
    mappings = load_mappings()
    workouts = {}

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

            # Parse fields
            date_parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            set_number = parse_set_order(set_order) if set_order else 0
            weight = parse_to_int(weight) if weight else 0
            reps = parse_to_int(reps) if reps else 0
            duration = parse_duration(duration_str) if duration_str else 0

            # Get or create the Workout
            workout_key = (date_str, workout_name)
            if workout_key not in workouts:
                workout_obj = Workout(workout_name, date_parsed, duration, workout_notes)
                workouts[workout_key] = workout_obj
            else:
                workout_obj = workouts[workout_key]

            # Determine body part from JSON or random
            if exercise_name in mappings:
                body_part_str = mappings[exercise_name]
                # Convert string to BodyPart enum if possible
                try:
                    # next(...) gets the BodyPart member whose value matches
                    the_body_part = next(bp for bp in BodyPart if bp.value == body_part_str)
                except StopIteration:
                    the_body_part = random.choice(list(BodyPart))
            else:
                # Not in JSON, remain None for now
                the_body_part = None

            # Check if exercise already exists
            exercise_obj = None
            for e in workout_obj.exercises:
                if e.name == exercise_name:
                    exercise_obj = e
                    break
            if exercise_obj is None:
                exercise_obj = Exercise(exercise_name, body_part=the_body_part)
                workout_obj.exercises.append(exercise_obj)

            # Create the ExerciseSet
            exercise_set = ExerciseSet(
                workout=workout_obj.name,
                date=date_parsed,
                set_number=set_number,
                weight=weight,
                reps=reps,
                notes=notes,
            )
            exercise_obj.exercise_sets.append(exercise_set)

    return list(workouts.values())

if __name__ == "__main__":
    file_path = "/Users/parkerlacy/coding/strong-data/data/raw/strong.csv"

    # Perform initial parsing
    parsed_workouts = parse_csv(file_path)

    # Gather all unique exercise names that have no known mapping
    # (i.e., assigned a random body part or None).
    exercises_without_mapping = set()
    for w in parsed_workouts:
        for e in w.exercises:
            if not e.body_part:
                exercises_without_mapping.add(e.name)

    # Load existing mapping from JSON
    mapping_dict = load_mappings()

    # Prompt the user for those exercises
    for ex_name in exercises_without_mapping:
        if ex_name not in mapping_dict:
            chosen_part_str = prompt_for_body_part(ex_name)
            # If user decides to exit, break out and save what we have so far
            if chosen_part_str == EXIT_FLAG:
                print(f"\nExiting, saving {len(parsed_workouts)} partial mappings...")
                break
            elif chosen_part_str:
                mapping_dict[ex_name] = chosen_part_str

    # Save updated mappings
    save_mappings(mapping_dict)

    print(f"\nParsed {len(parsed_workouts)} workouts.")
    print("Any new body part mappings were saved to exercise_body_part_mapping.json.")