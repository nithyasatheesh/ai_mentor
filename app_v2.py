import io
from typing import Any

import streamlit as st
from gtts import gTTS
from openai import OpenAI

# ---------------------------
# ⚙️ App setup
# ---------------------------
st.set_page_config(
    page_title="AI Coding Mentor v2",
    page_icon="🤖",
    layout="wide",
)

SYSTEM_PROMPT = """
You are an AI coding mentor.

You can answer:
- Programming questions (Java, React, Python, etc.)
- Conceptual questions
- Debugging problems
- Real-world scenarios

Guidelines:
- Use simple English
- Be clear and structured
- If coding → give code + explanation
- If concept → explain with examples
- If debugging → explain error + fix
- Keep it beginner friendly
""".strip()

AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"]
MAX_HISTORY_MESSAGES = 30


def init_state() -> None:
    """Initialize all session keys used by the app."""
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("audio_cache", {})


def get_client() -> OpenAI | None:
    """Create API client safely and return None when key is missing."""
    api_key = st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        st.error(
            "Missing `OPENAI_API_KEY` in Streamlit secrets. "
            "Add it in `.streamlit/secrets.toml` to use chat."
        )
        return None
    return OpenAI(api_key=api_key)


# ---------------------------
# 🎙️ Audio helpers
# ---------------------------
def _clean_text_for_tts(text: str) -> str:
    replacements = ["`", "*", "#"]
    clean_text = text
    for token in replacements:
        clean_text = clean_text.replace(token, "")
    return clean_text.strip()


def generate_audio_bytes(text: str) -> bytes:
    """Generate in-memory mp3 bytes instead of temporary files."""
    clean_text = _clean_text_for_tts(text)
    if not clean_text:
        return b""

    audio_buffer = io.BytesIO()
    gTTS(clean_text).write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()


def get_audio_for_message(message_id: str, text: str) -> bytes:
    cache: dict[str, bytes] = st.session_state.audio_cache
    if message_id not in cache:
        cache[message_id] = generate_audio_bytes(text)
    return cache[message_id]


# ---------------------------
# 🧠 Chat helpers
# ---------------------------
def add_message(role: str, content: str) -> None:
    st.session_state.chat_history.append({"role": role, "content": content})
    if len(st.session_state.chat_history) > MAX_HISTORY_MESSAGES:
        st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY_MESSAGES:]


def build_api_messages() -> list[dict[str, Any]]:
    return [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.chat_history
    ]


def render_message(message: dict[str, str], idx: int, enable_audio: bool) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if enable_audio and message["role"] == "assistant":
            audio_bytes = get_audio_for_message(f"history_{idx}", message["content"])
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")


def request_assistant_response(client: OpenAI, model_name: str) -> str:
    response = client.chat.completions.create(
        model=model_name,
        messages=build_api_messages(),
    )
    answer = response.choices[0].message.content
    return answer or "I couldn't generate a response. Please try again."


# ---------------------------
# 🎨 UI
# ---------------------------
init_state()
client = get_client()

st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        color: #6b7280;
        margin-bottom: 1rem;
    }
    .status-pill {
        display: inline-block;
        border: 1px solid #d1d5db;
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        margin-right: 0.4rem;
        margin-bottom: 0.5rem;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='main-title'>💻 AI Coding Mentor v2</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Ask coding, concept, or debugging questions. "
    "Your conversation is saved during this session.</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<span class='status-pill'>Beginner-friendly explanations</span>"
    "<span class='status-pill'>Code + reasoning</span>"
    "<span class='status-pill'>Debug help</span>",
    unsafe_allow_html=True,
)

# ---------------------------
# 🧰 Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("⚙️ Controls")
    model_name = st.selectbox("Model", AVAILABLE_MODELS, index=0)
    enable_audio = st.toggle("🔊 Enable text-to-speech", value=False)

    st.caption("Tip: audio generation may be slower for long answers.")

    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.audio_cache = {}
        st.rerun()

# ---------------------------
# 🧪 Quick prompt starters
# ---------------------------
st.write("**Quick starters:**")
col1, col2, col3 = st.columns(3)
quick_prompts = [
    "Explain Python decorators with simple examples.",
    "Help me debug a React useEffect infinite loop.",
    "How do I design a REST API for a todo app?",
]

selected_quick_prompt = None
for col, text in zip([col1, col2, col3], quick_prompts, strict=True):
    if col.button(text, use_container_width=True):
        selected_quick_prompt = text

# ---------------------------
# 🗂️ Chat history renderer
# ---------------------------
for idx, message in enumerate(st.session_state.chat_history):
    render_message(message, idx, enable_audio)

# ---------------------------
# 💬 Chat input
# ---------------------------
user_prompt = st.chat_input("Type your question here...")
prompt = user_prompt or selected_quick_prompt

if prompt:
    add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤖"):
            if client is None:
                error_message = "Cannot answer yet because API key is not configured."
                st.error(error_message)
                add_message("assistant", error_message)
            else:
                try:
                    answer = request_assistant_response(client, model_name)
                    st.markdown(answer)
                    add_message("assistant", answer)

                    if enable_audio:
                        current_message_id = f"history_{len(st.session_state.chat_history) - 1}"
                        audio_bytes = get_audio_for_message(current_message_id, answer)
                        if audio_bytes:
                            st.audio(audio_bytes, format="audio/mp3")
                except Exception as exc:
                    error_message = f"Error while generating a response: {exc}"
                    st.error(error_message)
                    add_message("assistant", error_message)
