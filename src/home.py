# Home page logic
import streamlit as st
from datetime import date
from models import Workout
from utils.gui_utils import filter_workouts, initialize_page, render_page_with_workouts

def show_home_page(workouts: list[Workout], min_date: date, max_date: date) -> None:
    """Display the Home view with summary metrics or prompts for data upload if not available."""
    st.title("Workout Data Analysis (Home)")
    date_range = st.date_input("Select a date range", [min_date, max_date])
    if st.button("Reset date range"):
        date_range = (min_date, max_date)

    filtered = filter_workouts(workouts, date_range)

    # Populate metrics
    st.metric("Number of total workouts", f"{len(filtered):,}")
    st.metric("Total duration exercised (mins)", f"{sum(w.duration for w in filtered):,}")
    st.metric("Total weight lifted (lbs)", f"{sum(w.total_weight_lifted for w in filtered):,}")
    st.metric("Total reps performed", f"{sum(w.total_reps_performed for w in filtered):,}")
    st.metric("Total number of exercises", f"{sum(w.number_of_exercises for w in filtered):,}")
    st.metric("Total number of exercise sets", f"{sum(w.number_of_exercise_sets for w in filtered):,}")

def home_page() -> None:
    """Streamlit wrapper for home page navigation."""
    initialize_page()
    
    render_page_with_workouts(show_home_page)