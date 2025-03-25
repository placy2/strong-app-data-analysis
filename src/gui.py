import streamlit as st
import sys
import pandas as pd
import altair as alt
from parse_raw_data import parse_csv
from datetime import date

def load_workouts():
    """Load workouts from CSV. Path can be overridden by a command-line argument."""
    data_path = "/Users/parkerlacy/coding/strong-data/data/raw/strong.csv"
    if len(sys.argv) > 1:
        data_path = sys.argv[1]
    return parse_csv(data_path)

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
        st.line_chart(df_line["total_weight_lifted"])
    else:
        st.write("No data in selected date range.")

    # Stacked bar chart: exercises by body part per week
    weekly_bodypart_counts = {}
    for w in filtered:
        iso_year, iso_week, _ = w.date.isocalendar()
        week_key = f"{iso_year}-W{iso_week}"
        if week_key not in weekly_bodypart_counts:
            weekly_bodypart_counts[week_key] = {}
        for e in w.exercises:
            bp = e.body_part.value  # e.body_part is an enum
            weekly_bodypart_counts[week_key][bp] = weekly_bodypart_counts[week_key].get(bp, 0) + 1

    if weekly_bodypart_counts:
        chart_data = []
        for week_key, bodyparts_dict in weekly_bodypart_counts.items():
            for bp, count in bodyparts_dict.items():
                chart_data.append({
                    "week": week_key,
                    "body_part": bp,
                    "count": count
                })
        df_bar = pd.DataFrame(chart_data)
        chart = (
            alt.Chart(df_bar, title="Exercises by Body Part per Week")
            .mark_bar()
            .encode(
                x=alt.X("week:N", title="Week"),
                y=alt.Y("sum(count):Q", title="Number of Exercises"),
                color=alt.Color("body_part:N", title="Body Part")
            )
            .properties(width=600)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No body-part data in selected range.")

def main():
    """Main entry point - load workouts and route to Home or Graphs page."""
    workouts = load_workouts()
    if not workouts:
        st.title("Workout Data Analysis")
        st.write("No data found.")
        return

    # Determine date range
    dates = [w.date for w in workouts]
    min_date = min(dates).date()
    max_date = max(dates).date()

    page = st.sidebar.selectbox("Navigation", ["Home", "Graphs"])
    if page == "Home":
        show_home_page(workouts, min_date, max_date)
    elif page == "Graphs":
        show_graphs_page(workouts, min_date, max_date)

if __name__ == "__main__":
    main()