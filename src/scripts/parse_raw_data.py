"""Parse raw workout data from CSV and prompt for missing exercise→body part mappings."""
import json
import os
from typing import Optional
# pylint: disable=import-error
from models import BodyPart
# pylint: disable=import-error
from utils.parse_utils import load_mappings
# pylint: disable=import-error
from parsers import parse_csv

# TODO add better info & description for this script around the mapping features


MAPPING_FILE = os.path.join(os.path.dirname(__file__), '../data/exercise_body_part_mapping.json')
EXIT_FLAG = "__USER_EXIT__"  # A sentinel to detect user exit

def save_mappings(mapping_dict: dict[str, str], filename: str) -> None:
    """Save exercise→body part mappings to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(mapping_dict, f, indent=2)

def prompt_for_body_part(exercise_name: str) -> Optional[str]:
    """
    Prompt user at command line for which BodyPart an exercise should belong to.
    Returns a string BodyPart.value, 'EXIT_FLAG' if user chooses to quit, or None if invalid.
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

    print("Invalid index. Skipping.")
    return None

def main_flow(file_path=None, mapping_file=None) -> None:
    """Main flow to parse CSV, prompt for missing mappings, and save results."""
    print(
        "This script parses raw workout data and prompts for missing exercise→body part mappings."
    )
    print(
        "It will save any new mappings to exercise_body_part_mapping.json for future use."
    )
    print(
        "You can exit the prompt at any time by entering 'q', which will save your progress."
    )
    if file_path is None:
        cwd = os.getcwd()
        # EDIT ME IF DESIRED - this is a hack to let me run locally faster.
        if "parkerlacy" in cwd:
            file_path = "/Users/parkerlacy/coding/strong-data/data/raw/strong.csv"
        # UI handles no data gracefully, so we can just warn the user
        else:
            print("Warning: No file path provided and default path not found.")

    if mapping_file is None:
        mapping_file = MAPPING_FILE

    parsed_workouts = parse_csv(file_path)

    # Gather all unique exercise names that have no known mapping
    # (i.e., assigned a random body part or None).
    exercises_without_mapping = set()
    for w in parsed_workouts:
        for e in w.exercises:
            if not e.body_part:
                exercises_without_mapping.add(e.name)

    # Load existing mapping from JSON
    mapping_dict = load_mappings(MAPPING_FILE)

    # Prompt the user for those exercises
    for ex_name in exercises_without_mapping:
        if ex_name not in mapping_dict:
            chosen_part_str = prompt_for_body_part(ex_name)
            # If user decides to exit, break out and save what we have so far
            if chosen_part_str == EXIT_FLAG:
                print(f"\nExiting, saving {len(parsed_workouts)} partial mappings...")
                break
            if chosen_part_str:
                mapping_dict[ex_name] = chosen_part_str

    # Save updated mappings
    save_mappings(mapping_dict, mapping_file)

    print(f"\nParsed {len(parsed_workouts)} workouts.")
    print("Any new body part mappings were saved to exercise_body_part_mapping.json.")


if __name__ == "__main__":
    main_flow()
