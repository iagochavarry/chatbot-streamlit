"""Load the external stylesheet into the Streamlit app."""

import streamlit as st


def apply() -> None:
    """Inject static/style.css into the page."""
    st.html("static/style.css")
