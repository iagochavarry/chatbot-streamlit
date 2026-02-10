import os
import time
import json
import streamlit as st
from openai import OpenAI

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Studio Chat",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Custom UI (CSS injection)
# -----------------------------
CUSTOM_CSS = """
<style>
/* ---------- Global ---------- */
:root{
  --bg: #0b0f1a;
  --panel: rgba(255,255,255,0.06);
  --panel-2: rgba(255,255,255,0.09);
  --text: rgba(255,255,255,0.92);
  --muted: rgba(255,255,255,0.65);
  --border: rgba(255,255,255,0.12);
  --shadow: 0 12px 50px rgba(0,0,0,0.35);
  --radius: 18px;
  --radius-sm: 14px;
  --grad: radial-gradient(1200px 800px at 10% 0%, rgba(125, 211, 252, 0.28), transparent 60%),
          radial-gradient(1200px 800px at 90% 20%, rgba(167, 139, 250, 0.28), transparent 60%),
          radial-gradient(1200px 800px at 50% 100%, rgba(34, 211, 238, 0.18), transparent 60%),
          linear-gradient(180deg, #070914 0%, #0b0f1a 35%, #070914 100%);
  --accent: #7dd3fc;
  --accent2:#a78bfa;
  --good: #34d399;
  --warn: #fbbf24;
  --bad:  #fb7185;
  --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

html, body, [data-testid="stAppViewContainer"]{
  background: var(--grad) !important;
  color: var(--text) !important;
}

[data-testid="stHeader"]{
  background: rgba(0,0,0,0) !important;
}

[data-testid="stSidebar"]{
  background: rgba(5, 8, 18, 0.55) !important;
  border-right: 1px solid var(--border) !important;
}

.block-container{
  padding-top: 1.2rem !important;
  padding-bottom: 2.8rem !important;
  max-width: 1200px;
}

/* Hide the default Streamlit footer/menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ---------- Typography ---------- */
h1, h2, h3, h4 { letter-spacing: -0.02em; }
small, .muted { color: var(--muted); }

/* ---------- Cards ---------- */
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 18px;
}

.card-plain{
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px 16px;
}

.pill{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.06);
  color: var(--muted);
  font-size: 12px;
}

/* ---------- Buttons ---------- */
.stButton > button{
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  background: rgba(255,255,255,0.06) !important;
  color: var(--text) !important;
  padding: 0.55rem 0.85rem !important;
  transition: 160ms ease !important;
}
.stButton > button:hover{
  transform: translateY(-1px);
  border-color: rgba(125, 211, 252, 0.45) !important;
  background: rgba(125, 211, 252, 0.10) !important;
}
.stButton > button:active{
  transform: translateY(0px);
}

/* Primary button style via container class */
.primary-btn .stButton > button{
  background: linear-gradient(135deg, rgba(125, 211, 252, 0.20), rgba(167, 139, 250, 0.20)) !important;
  border-color: rgba(125, 211, 252, 0.35) !important;
}

/* ---------- Inputs ---------- */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea textarea{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.05) !important;
  color: var(--text) !important;
}

.stSlider [data-testid="stThumbValue"]{
  color: var(--muted) !important;
}

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"]{
  padding: 0.2rem 0 !important;
}

[data-testid="stChatMessageContent"]{
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.05);
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

[data-testid="stChatMessage"][aria-label="Chat message from user"] [data-testid="stChatMessageContent"]{
  background: linear-gradient(135deg, rgba(125, 211, 252, 0.14), rgba(167, 139, 250, 0.12));
  border-color: rgba(125, 211, 252, 0.22);
}

[data-testid="stChatMessage"][aria-label="Chat message from assistant"] [data-testid="stChatMessageContent"]{
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.12);
}

[data-testid="stChatInput"]{
  position: sticky;
  bottom: 0;
  background: rgba(11, 15, 26, 0.72);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255,255,255,0.10);
  padding-top: 0.6rem;
  padding-bottom: 0.2rem;
}

/* Make chat input prettier */
[data-testid="stChatInput"] textarea{
  border-radius: 16px !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  background: rgba(255,255,255,0.06) !important;
}

hr{
  border-color: rgba(255,255,255,0.12) !important;
}

/* ---------- Utility ---------- */
.kbd{
  font-family: var(--mono);
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.05);
  color: var(--muted);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key)

def export_transcript(messages):
    # Simple portable export
    return json.dumps(messages, indent=2, ensure_ascii=False)

def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = (
            "You are a helpful, concise assistant with excellent taste in UI and product writing."
        )

init_state()

# -----------------------------
# Sidebar (controls)
# -----------------------------
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ✨ Studio Chat")
    st.caption("A polished Streamlit chatbot UI with streaming responses.")
    st.markdown('<div class="pill">⚡ Streaming · 🎛 Controls · 🧾 Export</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card-plain">', unsafe_allow_html=True)
    st.subheader("🔐 API Key")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-... (kept only in your session)",
        value=os.getenv("OPENAI_API_KEY", ""),
    )
    if not api_key:
        st.info("Add your OpenAI API key to start chatting.", icon="🗝️")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card-plain">', unsafe_allow_html=True)
    st.subheader("⚙️ Model & Behavior")

    # Pick models you likely have access to; adjust freely.
    model = st.selectbox(
        "Model",
        options=[
            "gpt-4.1-mini",
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-3.5-turbo",
        ],
        index=1,
        help="Choose a model. If one isn't available for your key, pick another.",
    )
    temperature = st.slider("Temperature", 0.0, 1.2, 0.4, 0.1)
    max_tokens = st.slider("Max tokens (response)", 64, 2048, 512, 64)

    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=110,
        help="Sets the assistant style/role. Kept in session.",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
        if st.button("🧹 Clear chat", use_container_width=True):
            st.session_state.messages = []
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        transcript = export_transcript(st.session_state.messages)
        st.download_button(
            "⬇️ Export",
            data=transcript,
            file_name="chat_transcript.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("---")
    st.caption(
        'Tip: Press <span class="kbd">Enter</span> to send · '
        '<span class="kbd">Shift</span>+<span class="kbd">Enter</span> for newline',
        unsafe_allow_html=True,
    )

# -----------------------------
# Main header
# -----------------------------
left, right = st.columns([0.72, 0.28], vertical_alignment="center")

with left:
    st.markdown(
        """
        <div class="card">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:14px;">
            <div>
              <div style="font-size:28px; font-weight:700; line-height:1.1;">💬 Beautiful Chatbot</div>
              <div style="margin-top:6px; color:rgba(255,255,255,0.68);">
                A premium, minimal chat interface built in Streamlit — with custom UI injection.
              </div>
            </div>
            <div class="pill">✨ Designer-grade polish</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="card-plain">
          <div style="font-weight:650; margin-bottom:6px;">Status</div>
          <div style="display:flex; flex-direction:column; gap:6px;">
            <div class="pill">Model: <span style="color:rgba(255,255,255,0.9); font-weight:600;">{}</span></div>
            <div class="pill">Temp: <span style="color:rgba(255,255,255,0.9); font-weight:600;">{}</span></div>
          </div>
        </div>
        """.format(model, temperature),
        unsafe_allow_html=True,
    )

st.write("")  # spacing

# -----------------------------
# Chat area
# -----------------------------
# Seed message (optional)
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": "Hey — I’m ready. Ask me anything, or tell me what you want to build.",
        }
    )

# Render messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# Chat input + streaming response
# -----------------------------
prompt = st.chat_input("Ask anything…")

if prompt:
    if not api_key:
        st.warning("Please add your OpenAI API key in the sidebar.", icon="🗝️")
    else:
        # Store user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build OpenAI messages payload (include system prompt)
        payload = [{"role": "system", "content": st.session_state.system_prompt}]
        payload.extend(
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
            if m["role"] in ("user", "assistant")
        )

        client = get_client(api_key)

        # Stream assistant response
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
                    # event.choices[0].delta.content for streaming chunks
                    chunk = ""
                    if event and event.choices and event.choices[0].delta:
                        chunk = event.choices[0].delta.content or ""
                    if chunk:
                        collected += chunk
                        placeholder.markdown(collected)

                if not collected.strip():
                    collected = "I didn’t receive any text. Try again (or switch models)."
                    placeholder.markdown(collected)

            except Exception as e:
                collected = f"⚠️ Error: {e}"
                placeholder.markdown(collected)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": collected})
