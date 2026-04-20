"""This module defines the edit page for the Streamlit app, allowing users to edit workout data."""
import streamlit as st

#TODO: add new page for editing data file, allowing users to edit the raw CSV data
# Should allow users to edit the raw CSV data in a table format,
# then write to data/processed and prompt if they want to load in the new file in the GUI
def edit_page() -> None:
    """Display the 'Edit Data' page, allowing users to edit the raw CSV data in a table format."""
    st.title("Edit Data")
    st.write("This page will allow users to edit the raw CSV data in a table format,")
    st.write("then write to data/processed and prompt if they want to save.")
    st.info("This page is a future TODO and is not implemented yet.")
