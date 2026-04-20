"""Utility functions for Streamlit GUI."""
from datetime import date, datetime
from typing import Callable
import streamlit as st
from models import Workout
from parsers import load_workouts


def filter_workouts(workouts: list[Workout], date_range: list[date]) -> list[Workout]:
    """Filter workouts by the given date range."""
    if len(date_range) == 2:
        start, end = date_range
        return [w for w in workouts if start <= w.date.date() <= end]
    return workouts

def initialize_page() -> None:
    """Seeds workouts into session_state"""
    if "workouts" not in st.session_state:
        st.session_state["workouts"] = load_workouts()

def render_page_with_workouts(
        render_func: Callable[[list[Workout], datetime, datetime], None]
    ) -> None:
    """Handles data presence and calls render function"""
    workouts = st.session_state["workouts"]

    if workouts:
        dates = [w.date for w in workouts]
        min_date = min(dates).date()
        max_date = max(dates).date()
        render_func(workouts, min_date, max_date)
    else:
        st.write("No data available. Please upload some data first.")
 