import tempfile
import re

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

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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
- If coding → give code + explanation + expected output
- If concept → explain with examples
- If debugging → explain error + root cause + fix + corrected code
- Always format code with fenced code blocks and include language tags
- Format outputs/errors/debug snippets in fenced code blocks
- Keep it beginner friendly
"""


# ---------------------------
# 🎙️ Audio helper
# ---------------------------
def generate_audio(text: str) -> str:
    clean_text = text.replace("`", "").replace("*", "").replace("#", "")
    tts = gTTS(clean_text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name


def render_message_content(content: str) -> None:
    """
    Render assistant content while keeping code/output/debug snippets very clear.
    """
    block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)
    last_end = 0

    for match in block_pattern.finditer(content):
        # Render any plain markdown before the code block
        if match.start() > last_end:
            plain_text = content[last_end:match.start()].strip()
            if plain_text:
                st.markdown(plain_text)

        language = (match.group(1) or "").strip()
        code_text = match.group(2).rstrip()
        st.code(code_text, language=language if language else None)
        last_end = match.end()

    # Render any remaining text after the final code block
    if last_end < len(content):
        tail_text = content[last_end:].strip()
        if tail_text:
            st.markdown(tail_text)


# ---------------------------
# 🧠 Session state
# ---------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------------------
# 🎨 Header
# ---------------------------
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
    .stChatMessage {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='main-title'>💻 AI Coding Mentor v2</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Ask coding, concept, or debugging questions. Your conversation is saved during this session.</div>",
    unsafe_allow_html=True,
)


# ---------------------------
# 🧰 Sidebar controls
# ---------------------------
with st.sidebar:
    st.header("⚙️ Controls")
    model_name = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"],
        index=0,
    )
    enable_audio = st.toggle("Read assistant responses aloud", value=False)

    if st.button("🧹 Clear chat history", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ---------------------------
# 🗂️ Chat history renderer
# ---------------------------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        render_message_content(msg["content"])
        if msg["role"] == "assistant" and msg.get("audio_file"):
            st.audio(msg["audio_file"], format="audio/mp3")


# ---------------------------
# 💬 Chat input
# ---------------------------
prompt = st.chat_input("Type your question here...")

if prompt:
    # Save + render user message
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message list for API
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.chat_history
    ]

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤖"):
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=api_messages,
                )
                answer = response.choices[0].message.content
                render_message_content(answer)

                audio_file = None
                if enable_audio:
                    audio_file = generate_audio(answer)
                    st.audio(audio_file, format="audio/mp3")

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "audio_file": audio_file,
                    }
                )
            except Exception as e:
                error_message = f"Error: {e}"
                st.markdown("### ❌ Error")
                st.code(error_message)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_message}
                )
