"""
Streamlit Chat UI — Minimal Nude Design
A clean, iMessage-inspired chat interface.
"""

import html as html_lib
import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

# ═══════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Sandbox",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# Design System (CSS)
# ═══════════════════════════════════════════════════════════════

_CSS = """<style>
/* ── Design Tokens ───────────────────────────────────────── */
:root {
    --bg:           #F3ECE4;
    --sidebar-bg:   #FAF7F4;
    --white:        #FFFFFF;
    --text:         #1D1D1F;
    --text-muted:   #86868B;
    --text-faint:   #AEAEB2;
    --user-bg:      #1D1D1F;
    --user-text:    #FFFFFF;
    --bot-bg:       #FFFFFF;
    --bot-text:     #1D1D1F;
    --bot-border:   rgba(0, 0, 0, 0.06);
    --border:       rgba(0, 0, 0, 0.07);
    --border-hover: rgba(0, 0, 0, 0.14);
    --hover-bg:     rgba(0, 0, 0, 0.03);
    --radius-lg:    22px;
    --radius-md:    14px;
    --radius-sm:    10px;
    --ease:         cubic-bezier(0.25, 0.1, 0.25, 1);
    --dur:          150ms;
    --font:         -apple-system, BlinkMacSystemFont, "SF Pro Text",
                    "Inter", "Segoe UI", system-ui, sans-serif;
}

/* ── Base ────────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    -webkit-font-smoothing: antialiased;
}

.block-container {
    max-width: 720px !important;
    padding: 2rem 1rem 7rem !important;
    margin: 0 auto;
}

/* ── Hide Streamlit Chrome ───────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {
    display: none !important;
}

/* ── Typography ──────────────────────────────────────────── */
h1, h2, h3, h4 {
    font-family: var(--font) !important;
    letter-spacing: -0.03em !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1.25rem !important;
    max-width: 100% !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--text) !important;
}

/* Sidebar toggle — expanded state */
button[kind="header"],
[data-testid="stSidebarCollapseButton"] button {
    opacity: 1 !important;
    visibility: visible !important;
    background: var(--sidebar-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    transition: all var(--dur) var(--ease) !important;
}

button[kind="header"]:hover,
[data-testid="stSidebarCollapseButton"] button:hover {
    background: var(--white) !important;
    border-color: var(--border-hover) !important;
}

/* Sidebar toggle — collapsed state (always visible, top-left) */
[data-testid="collapsedControl"] {
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 999999 !important;
}

[data-testid="collapsedControl"] button {
    opacity: 1 !important;
    visibility: visible !important;
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    width: 36px !important;
    height: 36px !important;
    transition: all var(--dur) var(--ease) !important;
}

[data-testid="collapsedControl"] button:hover {
    border-color: var(--border-hover) !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.10) !important;
}

/* ── Form Controls ───────────────────────────────────────── */
.stTextInput label, .stSelectbox label,
.stTextArea label, .stSlider label {
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    margin-bottom: 2px !important;
}

.stTextInput > div > div > input,
.stTextArea textarea {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    box-shadow: none !important;
    transition: border var(--dur) var(--ease) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: var(--border-hover) !important;
    box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.02) !important;
    outline: none !important;
}

.stSelectbox > div > div {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    box-shadow: none !important;
}

[data-testid="stSlider"] [role="slider"] {
    background: var(--text) !important;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button,
.stDownloadButton > button {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1rem !important;
    box-shadow: none !important;
    letter-spacing: 0.01em !important;
    transition: all var(--dur) var(--ease) !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: var(--hover-bg) !important;
    border-color: var(--border-hover) !important;
}

.stButton > button:active {
    transform: scale(0.97) !important;
}

/* ── Chat Messages (strip Streamlit defaults) ────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 0 !important;
    gap: 0 !important;
}

/* Hide built-in avatar column */
[data-testid="stChatMessage"] > div:first-child:not([data-testid="stChatMessageContent"]) {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
}

[data-testid="stChatMessageContent"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
}

/* ── Message Bubbles ─────────────────────────────────────── */
.msg-row {
    display: flex;
    width: 100%;
    margin: 2px 0;
}

.msg-row.right { justify-content: flex-end; }
.msg-row.left  { justify-content: flex-start; }

.msg-bubble {
    max-width: 78%;
    padding: 10px 16px;
    font-size: 0.9rem;
    line-height: 1.55;
    word-wrap: break-word;
    white-space: pre-wrap;
    font-family: var(--font);
}

.msg-bubble.user {
    background: var(--user-bg);
    color: var(--user-text);
    border-radius: 20px 20px 4px 20px;
}

.msg-bubble.bot {
    background: var(--bot-bg);
    color: var(--bot-text);
    border: 1px solid var(--bot-border);
    border-radius: 20px 20px 20px 4px;
}

.msg-meta {
    font-size: 0.65rem;
    color: var(--text-faint);
    margin-top: 3px;
    padding: 0 4px;
}

.msg-row.right .msg-meta { text-align: right; }
.msg-row.left  .msg-meta { text-align: left; }

/* ── Chat Input (sticky bottom bar) ──────────────────────── */
[data-testid="stBottom"] {
    background: linear-gradient(
        to bottom,
        rgba(243, 236, 228, 0),
        rgba(243, 236, 228, 0.96) 30%,
        rgba(243, 236, 228, 1) 50%
    ) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    padding: 0.5rem 0 !important;
}

[data-testid="stChatInput"] textarea {
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.04) !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: var(--border-hover) !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06) !important;
}

/* ── Utilities ───────────────────────────────────────────── */
.divider {
    height: 1px;
    background: var(--border);
    margin: 1.1rem 0;
}

.sidebar-footer {
    font-size: 0.68rem;
    color: var(--text-faint);
    letter-spacing: 0.02em;
    padding-top: 0.5rem;
}

[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.85rem !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.10);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.18);
}

/* ── Welcome (empty state) ───────────────────────────────── */
.welcome {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 6rem 1rem 4rem;
    text-align: center;
}

.welcome-title {
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.03em;
    margin: 0 0 6px;
}

.welcome-sub {
    font-size: 0.88rem;
    color: var(--text-muted);
    max-width: 300px;
    line-height: 1.5;
    margin: 0;
}
</style>"""

st.markdown(_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════════

_DEFAULTS: dict = {
    "messages": [],
    "system_prompt": "You are a helpful, concise assistant.",
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════


def _esc(text: str) -> str:
    """HTML-escape user content to prevent injection in rendered bubbles."""
    return html_lib.escape(str(text))


def _bubble(role: str, content: str, timestamp: str = "") -> None:
    """Render a single message as an aligned, styled bubble."""
    side = "right" if role == "user" else "left"
    kind = "user" if role == "user" else "bot"
    escaped = _esc(content)
    meta = f'<div class="msg-meta">{timestamp}</div>' if timestamp else ""
    st.markdown(
        f'<div class="msg-row {side}">'
        f"<div>"
        f'<div class="msg-bubble {kind}">{escaped}</div>'
        f"{meta}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _streaming_bubble(placeholder, content: str) -> None:
    """Update the streaming placeholder with partial bot content."""
    escaped = _esc(content)
    placeholder.markdown(
        f'<div class="msg-row left">'
        f'<div><div class="msg-bubble bot">{escaped}</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _final_bubble(placeholder, content: str, timestamp: str) -> None:
    """Replace streaming placeholder with final bubble including timestamp."""
    escaped = _esc(content)
    placeholder.markdown(
        f'<div class="msg-row left">'
        f"<div>"
        f'<div class="msg-bubble bot">{escaped}</div>'
        f'<div class="msg-meta">{timestamp}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════
# Sidebar
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("#### Sandbox")
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
        value=st.session_state.system_prompt,
        height=100,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col_b:
        st.download_button(
            "Export",
            data=json.dumps(
                st.session_state.messages, indent=2, ensure_ascii=False
            ),
            file_name="chat_export.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sidebar-footer">v1.0 &middot; Sandbox Chat</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Main Chat Area
# ═══════════════════════════════════════════════════════════════

if not st.session_state.messages:
    # Empty state — clean welcome prompt
    st.markdown(
        '<div class="welcome">'
        '<p class="welcome-title">Sandbox</p>'
        '<p class="welcome-sub">Type a message below to start a conversation.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
else:
    # Render conversation history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            _bubble(msg["role"], msg["content"], msg.get("time", ""))

# ═══════════════════════════════════════════════════════════════
# Chat Input + Streaming
# ═══════════════════════════════════════════════════════════════

prompt = st.chat_input("Type a message...")

if prompt:
    if not api_key:
        st.warning("Enter your API key in the sidebar to begin.")
    else:
        now = datetime.now().strftime("%H:%M")

        # Persist and render user message
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "time": now}
        )
        with st.chat_message("user"):
            _bubble("user", prompt, now)

        # Build OpenAI payload
        payload = [{"role": "system", "content": st.session_state.system_prompt}]
        payload.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ("user", "assistant")
        )

        client = OpenAI(api_key=api_key)

        # Stream assistant reply
        with st.chat_message("assistant"):
            placeholder = st.empty()
            collected = ""

            try:
                stream = client.chat.completions.create(
                    model=model,
                    messages=payload,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                for event in stream:
                    delta = (
                        event.choices[0].delta.content
                        if event and event.choices and event.choices[0].delta
                        else None
                    )
                    if delta:
                        collected += delta
                        _streaming_bubble(placeholder, collected)

                if not collected.strip():
                    collected = "No response returned. Please try again."

            except Exception as exc:
                collected = f"Something went wrong: {exc}"

            resp_time = datetime.now().strftime("%H:%M")
            _final_bubble(placeholder, collected, resp_time)

        st.session_state.messages.append(
            {"role": "assistant", "content": collected, "time": resp_time}
        )
