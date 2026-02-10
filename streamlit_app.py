"""
Sandbox Chat — Streamlit Entry Point

Thin orchestrator that wires theme, state, sidebar, and chat components.
All heavy lifting lives in components/ and lib/.
"""

import streamlit as st

from components import charts, chat, sidebar, theme, welcome
from lib import state

# -- Page config (must be first Streamlit call) --------------------

st.set_page_config(
    page_title="WingStop Streamlit Test",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Theme & state -------------------------------------------------

theme.apply()
state.init()

# -- Sidebar (returns settings dict) ------------------------------

settings = sidebar.render()

# -- Chart (toggle from sidebar) -----------------------------------

if settings["show_chart"]:
    charts.render()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# -- Chat area -----------------------------------------------------

messages = state.get_messages()

if not messages and not settings["show_chart"]:
    welcome.render()
elif messages:
    chat.render_history(messages)

# -- Input handling ------------------------------------------------

prompt = st.chat_input("Type a message...")

if prompt:
    if not settings["api_key"]:
        chat.toast("Add your API key in the sidebar to start chatting.")
    else:
        msg = state.add_message("user", prompt)
        chat.render_user_bubble(prompt, msg["time"])
        chat.stream_response(settings)
