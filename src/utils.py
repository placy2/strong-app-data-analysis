from datetime import date
from models import Workout
import os, sys
from parse_raw_data import parse_csv

def filter_workouts(workouts: list[Workout], date_range: list[date]) -> list[Workout]:
    """Filter workouts by the given date range."""
    if len(date_range) == 2:
        start, end = date_range
        return [w for w in workouts if start <= w.date.date() <= end]
    return workouts

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
    except Exception:
        # If there's a parsing error, return an empty list
        return []