"""Sidebar rendering — settings controls and actions."""

import json
import os

import streamlit as st

from lib import state


def render() -> dict:
    """Render the sidebar and return a settings dict.

    Returns:
        dict with keys: api_key, model, temperature, max_tokens, show_chart
    """
    with st.sidebar:
        st.markdown("#### WingStop Streamlit Test")
        st.caption("Chat settings")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        api_key = st.text_input(
            "API KEY",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            placeholder="sk-...",
            help="Session-only. Set OPENAI_API_KEY env var to auto-fill.",
        )

        model = st.selectbox(
            "MODEL",
            ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0,
        )

        temperature = st.slider("TEMPERATURE", 0.0, 1.5, 0.4, 0.05)
        max_tokens = st.slider("MAX TOKENS", 64, 4096, 1024, 64)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.session_state.system_prompt = st.text_area(
            "SYSTEM PROMPT",
            value=state.get_system_prompt(),
            height=100,
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        show_chart = st.toggle("Show sales chart", value=False)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Clear chat", use_container_width=True):
                state.clear()
        with col_b:
            st.download_button(
                "Export",
                data=json.dumps(
                    state.get_messages(), indent=2, ensure_ascii=False
                ),
                file_name="chat_export.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-footer">v1.0 &middot; WingStop</div>',
            unsafe_allow_html=True,
        )

    return {
        "api_key": api_key,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "show_chart": show_chart,
    }
