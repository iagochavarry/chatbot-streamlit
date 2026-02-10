import os
import json
import streamlit as st
from openai import OpenAI

# ------------------------------------------------------------
# Page config (minimal)
# ------------------------------------------------------------
st.set_page_config(
    page_title="Chat",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# Minimal Nude UI (CSS injection)
# ------------------------------------------------------------
CUSTOM_CSS = """
<style>
/* ---------- Nude palette + typography ---------- */
:root{
  --bg: #f6f0ea;          /* light nude */
  --surface: #fbf7f2;     /* slightly lighter */
  --surface2:#ffffff;     /* clean white for controls */
  --text: #1f1f1f;
  --muted:#6b6b6b;
  --border: rgba(17, 17, 17, 0.10);
  --shadow: 0 8px 30px rgba(17,17,17,0.06);
  --radius: 16px;
  --radius-sm: 12px;
  --user: #1f1f1f;        /* iMessage-like dark bubble */
  --userText: #ffffff;
  --bot: rgba(17,17,17,0.05); /* soft bot bubble */
  --botText: #1f1f1f;
  --focus: rgba(17,17,17,0.18);
}

html, body, [data-testid="stAppViewContainer"]{
  background: var(--bg) !important;
  color: var(--text) !important;
}

.block-container{
  padding-top: 1.25rem !important;
  padding-bottom: 2.5rem !important;
  max-width: 1100px;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---------- Sidebar polish ---------- */
[data-testid="stSidebar"]{
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]{
  color: var(--text) !important;
}

/* Make the collapse/expand control visible and crisp */
button[kind="header"]{
  opacity: 1 !important;
  border-radius: 12px !important;
}
button[kind="header"]:hover{
  background: rgba(17,17,17,0.04) !important;
}

/* ---------- Inputs ---------- */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea textarea{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
  color: var(--text) !important;
  box-shadow: none !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus{
  border-color: var(--focus) !important;
  outline: none !important;
}

/* Buttons */
.stButton > button{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
  color: var(--text) !important;
  padding: 0.55rem 0.9rem !important;
  box-shadow: none !important;
  transition: 140ms ease !important;
}
.stButton > button:hover{
  background: rgba(17,17,17,0.03) !important;
}
.stButton > button:active{
  transform: translateY(1px);
}

/* Download button match */
.stDownloadButton > button{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
  color: var(--text) !important;
}

/* ---------- Layout helpers ---------- */
.hr{
  height:1px;
  background: var(--border);
  margin: 14px 0;
}

/* ---------- Chat area ---------- */
[data-testid="stChatMessage"]{
  padding: 0.15rem 0 !important;
}

/* Remove default "card" feel */
[data-testid="stChatMessageContent"]{
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
}

/* Bubble base */
.bubble{
  display: inline-block;
  max-width: min(780px, 92%);
  padding: 10px 14px;
  border-radius: 18px;
  line-height: 1.45;
  border: 1px solid transparent;
  word-wrap: break-word;
  white-space: pre-wrap;
}

/* Assistant bubble (left) */
.bubble.bot{
  background: var(--bot);
  color: var(--botText);
  border-color: rgba(17,17,17,0.06);
  border-top-left-radius: 8px;
}

/* User bubble (right) */
.bubble.user{
  background: var(--user);
  color: var(--userText);
  border-top-right-radius: 8px;
}

/* Align wrappers */
.row{
  display: flex;
  width: 100%;
  gap: 12px;
}
.row.left{
  justify-content: flex-start;
}
.row.right{
  justify-content: flex-end;
}

/* Sticky chat input area */
[data-testid="stChatInput"]{
  position: sticky;
  bottom: 0;
  background: rgba(246, 240, 234, 0.92);
  backdrop-filter: blur(6px);
  border-top: 1px solid var(--border);
  padding-top: 0.6rem;
  padding-bottom: 0.2rem;
}
[data-testid="stChatInput"] textarea{
  border-radius: 16px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
}

/* Small, minimalist headings */
h1, h2, h3{
  letter-spacing: -0.02em;
}

/* Reduce spacing around markdown */
[data-testid="stMarkdownContainer"] p{
  margin-bottom: 0.5rem;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# State
# ------------------------------------------------------------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = (
            "You are a helpful, concise assistant with excellent product sense."
        )

init_state()

# ------------------------------------------------------------
# Sidebar (polished, minimal)
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("### Chat")
    st.caption("Minimal Streamlit chat with streaming responses.")

    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

    api_key = st.text_input(
        "API key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        placeholder="Required to chat",
        help="Stored only in your session. You can also set OPENAI_API_KEY in your environment.",
    )

    model = st.selectbox(
        "Model",
        ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=1,
    )
    temperature = st.slider("Temperature", 0.0, 1.2, 0.4, 0.1)
    max_tokens = st.slider("Max tokens", 64, 2048, 512, 64)

    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=110,
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear", use_container_width=True):
            st.session_state.messages = []
    with c2:
        st.download_button(
            "Export",
            data=json.dumps(st.session_state.messages, indent=2, ensure_ascii=False),
            file_name="chat_transcript.json",
            mime="application/json",
            use_container_width=True,
        )

# ------------------------------------------------------------
# Main (minimal header)
# ------------------------------------------------------------
st.markdown("## Chat")
st.caption("A modern, minimal chat interface with right/left message bubbles.")

# Seed message (optional)
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {"role": "assistant", "content": "Hello. How can I help?"}
    )

# ------------------------------------------------------------
# Render chat messages as iMessage-like bubbles
# ------------------------------------------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    # We still use st.chat_message for accessibility / built-in spacing,
    # but we fully control the bubble UI inside it.
    with st.chat_message(role):
        if role == "user":
            st.markdown(
                f'<div class="row right"><div class="bubble user">{content}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="row left"><div class="bubble bot">{content}</div></div>',
                unsafe_allow_html=True,
            )

# ------------------------------------------------------------
# Chat input + streaming response
# ------------------------------------------------------------
prompt = st.chat_input("Message")

if prompt:
    if not api_key:
        st.warning("Add your API key in the sidebar to start chatting.")
    else:
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Build OpenAI payload
        payload = [{"role": "system", "content": st.session_state.system_prompt}]
        payload.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ("user", "assistant")
        )

        client = OpenAI(api_key=api_key)

        # Stream assistant response
        with st.chat_message("assistant"):
            row = st.empty()
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
                    chunk = ""
                    if event and event.choices and event.choices[0].delta:
                        chunk = event.choices[0].delta.content or ""
                    if chunk:
                        collected += chunk
                        row.markdown(
                            f'<div class="row left"><div class="bubble bot">{collected}</div></div>',
                            unsafe_allow_html=True,
                        )

                if not collected.strip():
                    collected = "No response returned. Try again or switch models."
                    row.markdown(
                        f'<div class="row left"><div class="bubble bot">{collected}</div></div>',
                        unsafe_allow_html=True,
                    )

            except Exception as e:
                collected = f"Error: {e}"
                row.markdown(
                    f'<div class="row left"><div class="bubble bot">{collected}</div></div>',
                    unsafe_allow_html=True,
                )

        # Save assistant message
        st.session_state.messages.append({"role": "assistant", "content": collected})
