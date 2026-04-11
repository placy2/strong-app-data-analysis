import streamlit as st
from home import home_page
from graphs import graphs_page
from edit import edit_page
from upload import upload_page
from utils import load_workouts


def main():
    """Main entry point - use st.navigation() for built-in navigation."""
    # Initialize session state for workouts if not present
    if "workouts" not in st.session_state:
        st.session_state["workouts"] = load_workouts()

    # Define pages using st.Page()
    pages = [
        st.Page(home_page, title="Home", icon="🏠"),
        st.Page(graphs_page, title="Graphs", icon="📊"),
        st.Page(upload_page, title="Upload Data", icon="📤"),
        st.Page(edit_page, title="Edit Data (under construction)", icon="✏️"),
    ]

    # Use st.navigation() for built-in navigation
    nav = st.navigation(pages)
    nav.run()

if __name__ == "__main__":
    main()