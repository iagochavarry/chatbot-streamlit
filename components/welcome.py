"""Empty-state welcome screen."""

import streamlit as st


def render() -> None:
    """Show a centered welcome message when there are no messages yet."""
    st.markdown(
        '<div class="welcome">'
        '<p class="welcome-title">WingStop Streamlit Test</p>'
        '<p class="welcome-sub">Type a message below to start a conversation.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
