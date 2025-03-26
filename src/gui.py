import streamlit as st
import sys
import pandas as pd
import altair as alt
from parse_raw_data import parse_csv
from datetime import date
import tempfile
import os

def load_workouts():
    """Load workouts from CSV. Path can be overridden by a command-line argument."""
    data_path = "/Users/parkerlacy/coding/strong-data/data/raw/strong.csv"
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

def filter_workouts(workouts, date_range):
    """Filter workouts by the given date range."""
    if len(date_range) == 2:
        start, end = date_range
        return [w for w in workouts if start <= w.date.date() <= end]
    return workouts

def show_home_page(workouts, min_date, max_date):
    """Display the Home view with summary metrics."""
    st.title("Workout Data Analysis (Home)")
    date_range = st.date_input("Select a date range", [min_date, max_date])
    if st.button("Reset date range"):
        date_range = [min_date, max_date]

    filtered = filter_workouts(workouts, date_range)

    # Populate metrics
    st.metric("Number of total workouts", f"{len(filtered):,}")
    st.metric("Total duration exercised (mins)", f"{sum(w.duration for w in filtered):,}")
    st.metric("Total weight lifted (lbs)", f"{sum(w.total_weight_lifted for w in filtered):,}")
    st.metric("Total reps performed", f"{sum(w.total_reps_performed for w in filtered):,}")
    st.metric("Total number of exercises", f"{sum(w.number_of_exercises for w in filtered):,}")
    st.metric("Total number of exercise sets", f"{sum(w.number_of_exercise_sets for w in filtered):,}")

def show_graphs_page(workouts, min_date, max_date):
    """Display the Graphs view with line chart and stacked bar chart."""
    st.title("Workout Data Analysis (Graphs)")
    date_range = st.date_input("Select a date range", [min_date, max_date])
    if st.button("Reset date range"):
        date_range = [min_date, max_date]

    filtered = filter_workouts(workouts, date_range)

    # Line chart for total weight lifted over time
    weights_by_day = {}
    for w in filtered:
        d = w.date.date()
        weights_by_day[d] = weights_by_day.get(d, 0) + w.total_weight_lifted

    if weights_by_day:
        df_line = pd.DataFrame({
            "date": list(weights_by_day.keys()),
            "total_weight_lifted": list(weights_by_day.values())
        }).sort_values("date")
        df_line.set_index("date", inplace=True)

        st.subheader("Total Weight Lifted Over Time")
        st.line_chart(df_line["total_weight_lifted"])
    else:
        st.write("No data in selected date range.")

    # Stacked bar chart: number of exercise sets by body part per week
    weekly_bodypart_counts = {}
    for w in filtered:
        iso_year, iso_week, _ = w.date.isocalendar()
        week_key = f"{iso_year}-W{iso_week}"
        if week_key not in weekly_bodypart_counts:
            weekly_bodypart_counts[week_key] = {}

        # For each exercise, add the number of sets
        for e in w.exercises:
            bp = e.body_part.value  # e.body_part is an enum from parse_raw_data.py
            set_count = len(e.exercise_sets)
            weekly_bodypart_counts[week_key][bp] = (
                weekly_bodypart_counts[week_key].get(bp, 0) + set_count
            )

    if weekly_bodypart_counts:
        chart_data = []
        for week_key, bodyparts_dict in weekly_bodypart_counts.items():
            for bp, sets_total in bodyparts_dict.items():
                chart_data.append({
                    "week": week_key,
                    "body_part": bp,
                    "sets_count": sets_total
                })

        df_bar = pd.DataFrame(chart_data)
        chart = (
            alt.Chart(df_bar)
            .mark_bar()
            .encode(
                x=alt.X("week:N", title="Week"),
                y=alt.Y("sum(sets_count):Q", title="Number of Exercise Sets"),
                color=alt.Color("body_part:N", title="Body Part", scale=alt.Scale(scheme='category20'))
            )
            .properties(width=600)
        )
        st.subheader("Exercise Sets by Body Part per Week")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No body-part data in selected range.")

def show_upload_page():
    """
    Display the 'Upload Data' page, allowing users to either select a local file path
    or upload via drag-and-drop. Updates st.session_state["workouts"] after successful parse.
    """
    st.title("Upload Data")
    st.write("Please provide a CSV file. You can write a path or drag & drop it below.")

    # Text input for a local file path
    file_path = st.text_input("Local CSV file path (optional)")

    # Drag & drop
    uploaded_file = st.file_uploader("Drag & drop a CSV file", type=["csv"])

    # Button to trigger loading
    if st.button("Load Data"):
        if file_path.strip():
            with st.spinner("Loading data from local path..."):
                try:
                    new_workouts = parse_csv(file_path.strip())
                    st.success(f"Loaded {len(new_workouts)} workouts from {file_path.strip()}.")
                    st.session_state["workouts"] = new_workouts
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        elif uploaded_file is not None:
            with st.spinner("Parsing uploaded data..."):
                # Write to a temporary file, then parse
                temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
                temp.write(uploaded_file.read())
                temp.close()
                try:
                    new_workouts = parse_csv(temp.name)
                    os.remove(temp.name)
                    st.success(f"Loaded {len(new_workouts)} workouts from uploaded file.")
                    st.session_state["workouts"] = new_workouts
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.info("No file or path provided. Please try again.")

def main():
    """Main entry point - use session state for storing workouts, route pages accordingly."""
    # Initialize session state for workouts if not present
    if "workouts" not in st.session_state:
        initial_workouts = load_workouts()
        st.session_state["workouts"] = initial_workouts

    workouts = st.session_state["workouts"]

    # If no workouts found, default to "Upload Data" page
    if not workouts:
        page_options = ["Upload Data", "Home", "Graphs"]
        default_index = 0
    else:
        page_options = ["Home", "Graphs", "Upload Data"]
        default_index = 0

    page = st.sidebar.selectbox("Navigation", page_options, index=default_index)

    # Determine date range
    if workouts:
        dates = [w.date for w in workouts]
        min_date = min(dates).date()
        max_date = max(dates).date()
    else:
        # Dummy date range for when no workouts found
        min_date, max_date = date.today(), date.today()

    if page == "Home":
        if workouts:
            show_home_page(workouts, min_date, max_date)
        else:
            st.write("No data available. Please upload some data first.")
    elif page == "Graphs":
        if workouts:
            show_graphs_page(workouts, min_date, max_date)
        else:
            st.write("No data available. Please upload some data first.")
    elif page == "Upload Data":
        show_upload_page()

if __name__ == "__main__":
    main()