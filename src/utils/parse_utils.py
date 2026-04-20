"""Utility functions for parsing workout data."""
import json
import os


def load_mappings(filename: str) -> dict[str, str]:
    """Load exercise→body part mappings from JSON file, if it exists."""
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def parse_duration(duration_str: str) -> int:
    """Parses string duration into length of time in minutes"""
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

def parse_set_order(set_order_str: str) -> int:
    """Parses set order, which includes special chars, into int"""
    # Handles regular set orders like "1", "2", but also non-numeric cases gracefully
    # Includes "W" (warmup set), "F" (failure set), and "D" (drop set) as special cases
    # For now special cases always result in set number 0, but this may be adjusted
    if set_order_str.isdigit():
        return int(set_order_str)
    if set_order_str in {"W", "F", "D"}:
        return 0
    else:
        raise ValueError(f"Invalid set order: {set_order_str}")

def parse_to_int(value_str: str) -> int:
    """Generic parsing str to int"""
    # Handles cases like "0", "0.0"
    try:
        return int(float(value_str))
    except ValueError:
        return 0
