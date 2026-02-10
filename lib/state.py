"""Session state management for the Streamlit chat app."""

from datetime import datetime

import streamlit as st

_DEFAULTS = {
    "messages": [],
    "system_prompt": "You are a helpful, concise assistant.",
}


def init() -> None:
    """Ensure all required keys exist in session state."""
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_message(role: str, content: str) -> dict:
    """Append a message and return it (includes timestamp)."""
    msg = {
        "role": role,
        "content": content,
        "time": datetime.now().strftime("%H:%M"),
    }
    st.session_state.messages.append(msg)
    return msg


def clear() -> None:
    """Reset conversation history and rerun."""
    st.session_state.messages = []
    st.rerun()


def get_messages() -> list:
    """Return the current message list."""
    return st.session_state.messages


def get_system_prompt() -> str:
    """Return the current system prompt."""
    return st.session_state.system_prompt
