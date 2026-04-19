import streamlit as st

#TODO: add new page for editing data file, allowing users to edit the raw CSV data
# Should allow users to edit the raw CSV data in a table format, then write to data/processed and prompt if they want to load in the new file in the GUI
def edit_page() -> None:
    st.title("Edit Data")
    st.write("This page will allow users to edit the raw CSV data in a table format, then write to data/processed and prompt if they want to load in the new file in the GUI.")
    st.info("This page is a future TODO and is not implemented yet.")