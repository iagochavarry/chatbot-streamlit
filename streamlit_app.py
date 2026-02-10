"""
Streamlit Chat — Minimal Nude UI
"""

import html as html_lib
import json
import os
from datetime import datetime

import streamlit as st
from openai import OpenAI

# ═══════════════════════════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Sandbox",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
# Theme — single CSS block, applied once
# ═══════════════════════════════════════════════════════════════

_NUDE = "#F3ECE4"
_SIDEBAR = "#FAF7F4"

st.markdown(
    f"""<style>
/* ════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ════════════════════════════════════════════════════════════ */
:root {{
    --bg:           {_NUDE};
    --sidebar-bg:   {_SIDEBAR};
    --white:        #FFFFFF;
    --text:         #1D1D1F;
    --text-muted:   #86868B;
    --text-faint:   #AEAEB2;
    --user-bg:      #1D1D1F;
    --user-text:    #FFFFFF;
    --bot-bg:       #FFFFFF;
    --bot-text:     #1D1D1F;
    --bot-border:   rgba(0,0,0,0.06);
    --border:       rgba(0,0,0,0.07);
    --border-hover: rgba(0,0,0,0.14);
    --radius-lg:    22px;
    --radius-md:    14px;
    --radius-sm:    10px;
    --font:         -apple-system, BlinkMacSystemFont, "SF Pro Text",
                    "Inter", "Segoe UI", system-ui, sans-serif;
}}

/* ════════════════════════════════════════════════════════════
   GLOBAL BACKGROUND — cover absolutely everything
   ════════════════════════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stMain"],
.main, .main .block-container,
[data-testid="stAppViewContainer"] > section,
[data-testid="stAppViewContainer"] > section > div {{
    background-color: {_NUDE} !important;
    background: {_NUDE} !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}}

.block-container {{
    max-width: 720px !important;
    padding: 2rem 1rem 5rem !important;
    margin: 0 auto;
}}

/* ════════════════════════════════════════════════════════════
   HIDE ALL STREAMLIT CHROME
   ════════════════════════════════════════════════════════════ */
#MainMenu,
footer,
header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[data-testid="manage-app-button"],
.viewerBadge_container__r5tak,
.stDeployButton,
[data-testid="stAppDeployButton"],
[data-testid="baseButton-header"],
div[data-testid="stAppViewContainer"] > div:last-child > div:last-child {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    overflow: hidden !important;
}}

/* ════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ════════════════════════════════════════════════════════════ */
h1, h2, h3, h4 {{
    font-family: var(--font) !important;
    letter-spacing: -0.03em !important;
    font-weight: 600 !important;
    color: var(--text) !important;
}}

/* ════════════════════════════════════════════════════════════
   SIDEBAR — always visible, never collapses
   ════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
    transform: none !important;
    min-width: 300px !important;
    width: 300px !important;
    visibility: visible !important;
    position: relative !important;
    z-index: 100 !important;
}}

[data-testid="stSidebar"] > div {{
    width: 300px !important;
    background: var(--sidebar-bg) !important;
}}

[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] > div:first-child {{
    padding: 1.5rem 1.25rem !important;
    max-width: 100% !important;
}}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: var(--text) !important;
}}

button[kind="header"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* ════════════════════════════════════════════════════════════
   FORM CONTROLS
   ════════════════════════════════════════════════════════════ */
.stTextInput label, .stSelectbox label,
.stTextArea label, .stSlider label {{
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}}

.stTextInput > div > div > input,
.stTextArea textarea {{
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    box-shadow: none !important;
}}

.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {{
    border-color: var(--border-hover) !important;
    outline: none !important;
}}

.stSelectbox > div > div {{
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    box-shadow: none !important;
}}

[data-testid="stSlider"] [role="slider"] {{
    background: var(--text) !important;
}}

/* ════════════════════════════════════════════════════════════
   BUTTONS
   ════════════════════════════════════════════════════════════ */
.stButton > button,
.stDownloadButton > button {{
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    padding: 0.5rem 1rem !important;
    box-shadow: none !important;
    transition: all 150ms ease !important;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background: rgba(0,0,0,0.03) !important;
    border-color: var(--border-hover) !important;
}}

.stButton > button:active {{
    transform: scale(0.97) !important;
}}

/* ════════════════════════════════════════════════════════════
   CHAT MESSAGES — strip every Streamlit default
   ════════════════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 2px 0 !important;
    gap: 0 !important;
    max-width: 100% !important;
}}

/* Kill the avatar column */
[data-testid="stChatMessage"] > div:first-child:not([data-testid="stChatMessageContent"]),
[data-testid="stChatMessage"] .stChatMessageAvatarContainer,
[data-testid="stChatMessage"] img[data-testid] {{
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}}

[data-testid="stChatMessageContent"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
}}

/* ════════════════════════════════════════════════════════════
   CUSTOM BUBBLES
   ════════════════════════════════════════════════════════════ */
.msg-row {{
    display: flex;
    width: 100%;
    margin: 3px 0;
}}
.msg-row.right {{ justify-content: flex-end; }}
.msg-row.left  {{ justify-content: flex-start; }}

.msg-bubble {{
    max-width: 75%;
    padding: 10px 16px;
    font-size: 0.9rem;
    line-height: 1.55;
    word-wrap: break-word;
    white-space: pre-wrap;
    font-family: var(--font);
}}

.msg-bubble.user {{
    background: var(--user-bg);
    color: var(--user-text);
    border-radius: 20px 20px 4px 20px;
}}

.msg-bubble.bot {{
    background: var(--bot-bg);
    color: var(--bot-text);
    border: 1px solid var(--bot-border);
    border-radius: 20px 20px 20px 4px;
}}

.msg-meta {{
    font-size: 0.65rem;
    color: var(--text-faint);
    margin-top: 3px;
    padding: 0 4px;
}}
.msg-row.right .msg-meta {{ text-align: right; }}
.msg-row.left  .msg-meta {{ text-align: left; }}

/* ════════════════════════════════════════════════════════════
   BOTTOM BAR — force nude background everywhere
   ════════════════════════════════════════════════════════════ */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInputContainer"],
.stChatInput,
div[data-testid="stBottom"] *:not(textarea):not(button):not(svg):not(path) {{
    background: {_NUDE} !important;
    background-color: {_NUDE} !important;
    border-top: none !important;
    border-color: transparent !important;
}}

[data-testid="stChatInput"] textarea {{
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
    background: var(--white) !important;
    background-color: var(--white) !important;
    font-family: var(--font) !important;
    font-size: 0.88rem !important;
    padding: 0.75rem 1rem !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.05) !important;
}}

[data-testid="stChatInput"] textarea:focus {{
    border-color: var(--border-hover) !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07) !important;
}}

/* Send button in chat input */
[data-testid="stChatInput"] button,
[data-testid="stChatInputSubmitButton"] {{
    background: var(--text) !important;
    background-color: var(--text) !important;
    border-radius: 50% !important;
    border: none !important;
}}

[data-testid="stChatInput"] button svg {{
    fill: var(--white) !important;
    stroke: var(--white) !important;
}}

/* ════════════════════════════════════════════════════════════
   INLINE TOAST (replaces st.warning)
   ════════════════════════════════════════════════════════════ */
.toast {{
    display: inline-block;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 10px 18px;
    font-size: 0.84rem;
    color: var(--text-muted);
    font-family: var(--font);
    margin: 6px 0;
}}

/* Also override native alerts just in case */
[data-testid="stAlert"] {{
    background: var(--white) !important;
    background-color: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-muted) !important;
    font-size: 0.84rem !important;
}}

[data-testid="stAlert"] p {{
    color: var(--text-muted) !important;
}}

/* ════════════════════════════════════════════════════════════
   WELCOME STATE
   ════════════════════════════════════════════════════════════ */
.welcome {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8rem 1rem 4rem;
    text-align: center;
}}
.welcome-title {{
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.03em;
    margin: 0 0 8px;
}}
.welcome-sub {{
    font-size: 0.88rem;
    color: var(--text-muted);
    max-width: 320px;
    line-height: 1.5;
    margin: 0;
}}

/* ════════════════════════════════════════════════════════════
   UTILITIES
   ════════════════════════════════════════════════════════════ */
.divider {{
    height: 1px;
    background: var(--border);
    margin: 1rem 0;
}}
.sidebar-footer {{
    font-size: 0.68rem;
    color: var(--text-faint);
    letter-spacing: 0.02em;
    padding-top: 0.25rem;
}}

::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: rgba(0,0,0,0.10);
    border-radius: 4px;
}}
</style>""",
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════════

if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful, concise assistant."

# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════


def _esc(text: str) -> str:
    """HTML-escape to prevent XSS in rendered bubbles."""
    return html_lib.escape(str(text))


def _bubble(role: str, content: str, timestamp: str = "") -> None:
    """Render one message as a left/right aligned bubble."""
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


def _stream_bubble(ph, content: str) -> None:
    """Update streaming placeholder with partial content."""
    ph.markdown(
        f'<div class="msg-row left">'
        f'<div><div class="msg-bubble bot">{_esc(content)}</div></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def _finish_bubble(ph, content: str, ts: str) -> None:
    """Final bubble with timestamp."""
    ph.markdown(
        f'<div class="msg-row left">'
        f"<div>"
        f'<div class="msg-bubble bot">{_esc(content)}</div>'
        f'<div class="msg-meta">{ts}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _toast(text: str) -> None:
    """Show a subtle inline notification (replaces st.warning)."""
    st.markdown(f'<div class="toast">{_esc(text)}</div>', unsafe_allow_html=True)


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
        '<div class="sidebar-footer">v1.0 &middot; Sandbox</div>',
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════
# Chat Area
# ═══════════════════════════════════════════════════════════════

if not st.session_state.messages:
    st.markdown(
        '<div class="welcome">'
        '<p class="welcome-title">Sandbox</p>'
        '<p class="welcome-sub">Type a message below to start.</p>'
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            _bubble(msg["role"], msg["content"], msg.get("time", ""))

# ═══════════════════════════════════════════════════════════════
# Input + Streaming
# ═══════════════════════════════════════════════════════════════

prompt = st.chat_input("Type a message...")

if prompt:
    if not api_key:
        _toast("Add your API key in the sidebar to start chatting.")
    else:
        now = datetime.now().strftime("%H:%M")

        st.session_state.messages.append(
            {"role": "user", "content": prompt, "time": now}
        )
        with st.chat_message("user"):
            _bubble("user", prompt, now)

        payload = [{"role": "system", "content": st.session_state.system_prompt}]
        payload.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ("user", "assistant")
        )

        client = OpenAI(api_key=api_key)

        with st.chat_message("assistant"):
            ph = st.empty()
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
                        _stream_bubble(ph, collected)

                if not collected.strip():
                    collected = "No response returned. Please try again."

            except Exception as exc:
                collected = f"Something went wrong: {exc}"

            resp_time = datetime.now().strftime("%H:%M")
            _finish_bubble(ph, collected, resp_time)

        st.session_state.messages.append(
            {"role": "assistant", "content": collected, "time": resp_time}
        )
