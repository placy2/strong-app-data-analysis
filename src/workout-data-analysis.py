import streamlit as st

def main():
    st.title("Workout Data Analysis")

    # Date range picker
    date_range = st.date_input("Select a date range", [])

    # Numerical displays (placeholders)
    st.metric("Number of total workouts", "0")
    st.metric("Total duration exercised", "0")
    st.metric("Total weight lifted (lbs)", "0")
    st.metric("Placeholder 4", "0")
    st.metric("Placeholder 5", "0")

if __name__ == "__main__":
    main()