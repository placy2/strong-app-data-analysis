import streamlit as st
from parse_raw_data import parse_csv
import tempfile, os

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


def upload_page():
    """Wrapper for upload page navigation."""
    if "workouts" not in st.session_state:
        st.session_state["workouts"] = load_workouts()
    
    show_upload_page()