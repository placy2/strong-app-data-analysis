import streamlit as st
from parse_raw_data import parse_csv
import sys

def main():
    # Default data path - set and you will not need to provide the path as an argument.
    # data_path = ""

    # If a path is passed as an argument, override the default
    if len(sys.argv) > 1:
        data_path = sys.argv[1]

    st.title("Workout Data Analysis")

    # Parse CSV data
    workouts = parse_csv(data_path)
    if not workouts:
        st.write("No data found.")
        return

    # Determine full date range
    dates = [w.date for w in workouts]
    min_date = min(dates).date()
    max_date = max(dates).date()

    # Date range picker (default to full range)
    date_range = st.date_input("Select a date range", [min_date, max_date])

    # Filter by selected range
    if len(date_range) == 2:
        start, end = date_range
        filtered = [w for w in workouts if start <= w.date.date() <= end]
    else:
        filtered = workouts

    # Populate metrics
    st.metric("Number of total workouts", f"{len(filtered):,}")
    st.metric("Total duration exercised (mins)", f"{sum(w.duration for w in filtered):,}")
    st.metric("Total weight lifted (lbs)", f"{sum(w.total_weight_lifted for w in filtered):,}")
    st.metric("Total reps performed", f"{sum(w.total_reps_performed for w in filtered):,}")
    st.metric("Total number of exercises", f"{sum(w.number_of_exercises for w in filtered):,}")
    st.metric("Total number of exercise sets", f"{sum(w.number_of_exercise_sets for w in filtered):,}")

if __name__ == "__main__":
    main()