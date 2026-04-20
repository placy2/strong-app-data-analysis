"""Graphs page for visualizing workout data."""
from datetime import date
import streamlit as st
import pandas as pd
import altair as alt
from models import Workout
from utils.gui_utils import filter_workouts, initialize_page, render_page_with_workouts


#TODO: rework date filter to a more general "filters" option & simplify/break up func
# include new filters like body part, exercise name, etc.
def show_graphs_page(workouts: list[Workout], min_date: date, max_date: date) -> None:
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
        print(f"Processing workout on {w.date} with exercises {w.exercises}")

        # For each exercise, add the number of sets
        for e in w.exercises:
            if e.body_part is not None:
                bp = e.body_part.value  # e.body_part is an enum from parse_raw_data.py
                set_count = len(e.exercise_sets)
                weekly_bodypart_counts[week_key][bp] = (
                    weekly_bodypart_counts[week_key].get(bp, 0) + set_count
                )
            else:
                print(f"Warning: Exercise '{e.name}' from {w.date} has no body part assigned.")

    if weekly_bodypart_counts:
        chart_data = []
        # Sorts weeks, but default sort results in "2026-W10" coming before "2026-W2"
        # thus, we use the iso_year and iso_week to sort properly
        sorted_weeks = sorted(
            weekly_bodypart_counts.keys(),
            key=lambda x: (int(x.split("-")[0]), int(x.split("-W")[1]))
        )
        for week_key in sorted_weeks:
            bodyparts_dict = weekly_bodypart_counts[week_key]
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
                x=alt.X("week:N", title="Week", sort={}),
                y=alt.Y("sum(sets_count):Q", title="Number of Exercise Sets"),
                color=alt.Color(
                    "body_part:N",
                    title="Body Part",
                    scale=alt.Scale(scheme='category20')
                )
            )
            .properties(width=600)
        )
        st.subheader("Exercise Sets by Body Part per Week")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No body-part data in selected range.")

def graphs_page() -> None:
    """Wrapper for graphs page navigation."""
    initialize_page()
    render_page_with_workouts(show_graphs_page)
