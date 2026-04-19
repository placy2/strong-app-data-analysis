import json, os
from models import BodyPart
from utils.parse_utils import load_mappings
from parsers import parse_csv

# TODO add better info & description for this script around the mapping features




def save_mappings(mapping_dict: dict[str, str], filename: str) -> None:
    """Save exercise→body part mappings to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(mapping_dict, f, indent=2)

def prompt_for_body_part(exercise_name: str) -> str | None:
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

if __name__ == "__main__":
    dirname = os.path.dirname(__file__)
    MAPPING_FILE = os.path.join(dirname, '../data/exercise_body_part_mapping.json')
    EXIT_FLAG = "__USER_EXIT__"  # A sentinel to detect user exit
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
    mapping_dict = load_mappings(MAPPING_FILE)

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