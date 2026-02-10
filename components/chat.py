"""Chat bubble rendering and streaming."""

import html as html_lib

import streamlit as st

from lib import client, state


def _esc(text: str) -> str:
    """HTML-escape text to prevent injection in rendered bubbles."""
    return html_lib.escape(str(text))


def _bubble_html(side: str, kind: str, content: str, timestamp: str = "") -> str:
    """Build the HTML string for a single message bubble."""
    meta = f'<div class="msg-meta">{timestamp}</div>' if timestamp else ""
    return (
        f'<div class="msg-row {side}">'
        f"<div>"
        f'<div class="msg-bubble {kind}">{_esc(content)}</div>'
        f"{meta}"
        f"</div>"
        f"</div>"
    )


def render_history(messages: list[dict]) -> None:
    """Render the full conversation history as bubbles."""
    for msg in messages:
        role = msg["role"]
        side = "right" if role == "user" else "left"
        kind = "user" if role == "user" else "bot"
        with st.chat_message(role):
            st.markdown(
                _bubble_html(side, kind, msg["content"], msg.get("time", "")),
                unsafe_allow_html=True,
            )


def render_user_bubble(content: str, timestamp: str) -> None:
    """Render a single user bubble (used right after input)."""
    with st.chat_message("user"):
        st.markdown(
            _bubble_html("right", "user", content, timestamp),
            unsafe_allow_html=True,
        )


def stream_response(settings: dict) -> None:
    """Stream an assistant response and persist it.

    Args:
        settings: dict with api_key, model, temperature, max_tokens
    """
    messages = state.get_messages()

    # Build the OpenAI payload
    payload = [{"role": "system", "content": state.get_system_prompt()}]
    payload.extend(
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] in ("user", "assistant")
    )

    with st.chat_message("assistant"):
        placeholder = st.empty()
        collected = ""

        try:
            for delta in client.stream_completion(
                api_key=settings["api_key"],
                model=settings["model"],
                messages=payload,
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
            ):
                collected += delta
                placeholder.markdown(
                    _bubble_html("left", "bot", collected),
                    unsafe_allow_html=True,
                )

            if not collected.strip():
                collected = "No response returned. Please try again."

        except Exception as exc:
            collected = f"Something went wrong: {exc}"

        # Final render with timestamp
        msg = state.add_message("assistant", collected)
        placeholder.markdown(
            _bubble_html("left", "bot", collected, msg["time"]),
            unsafe_allow_html=True,
        )


def toast(text: str) -> None:
    """Show a subtle inline notification."""
    st.markdown(
        f'<div class="toast">{_esc(text)}</div>',
        unsafe_allow_html=True,
    )
