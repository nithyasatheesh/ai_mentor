import tempfile

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
- If coding → give code + explanation
- If concept → explain with examples
- If debugging → explain error + fix
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
        st.markdown(msg["content"])


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
                st.markdown(answer)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )

                if enable_audio:
                    audio_file = generate_audio(answer)
                    st.audio(audio_file)
            except Exception as e:
                error_message = f"Error: {e}"
                st.error(error_message)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": error_message}
                )
