import tempfile

import streamlit as st
from gtts import gTTS
from openai import OpenAI


# 🔐 Configure OpenAI client from Streamlit secrets.
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ---------------------------
# ⚙️ App configuration
# ---------------------------
st.set_page_config(page_title="AI Coding Mentor", layout="centered")
st.title("💻 AI Coding Mentor 🚀")
st.write("Ask coding, concept, or debugging questions (Java, React, Python, etc.)")


# ---------------------------
# 🎙️ Audio helper
# ---------------------------
def generate_audio(text: str) -> str:
    """Convert the assistant response into an MP3 file and return the file path."""
    # Remove markdown symbols that can make speech sound unnatural.
    clean_text = text.replace("`", "").replace("*", "").replace("#", "")

    # Generate speech from cleaned text.
    tts = gTTS(clean_text)

    # Save the audio to a temporary file and return it for Streamlit playback.
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name


# ---------------------------
# 🧠 System Prompt
# ---------------------------
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
# 🗂️ Session state setup
# ---------------------------
def initialize_state() -> None:
    """Initialize persistent state used for chat history and latest answer."""
    # Store all previous Q&A pairs so the UI can render conversation history.
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Keep the most recent answer for quick display and optional audio playback.
    if "latest_answer" not in st.session_state:
        st.session_state.latest_answer = ""


# ---------------------------
# 📜 History display
# ---------------------------
def render_chat_history() -> None:
    """Render previous user questions and assistant answers."""
    st.subheader("🕘 Chat History")

    # Show guidance when there are no previous entries.
    if not st.session_state.chat_history:
        st.info("No chat history yet. Ask your first question below.")
        return

    # Display older messages first so the conversation reads in order.
    for idx, item in enumerate(st.session_state.chat_history, start=1):
        with st.container(border=True):
            st.markdown(f"**Q{idx}:** {item['question']}")
            st.markdown(f"**A{idx}:** {item['answer']}")


# ---------------------------
# 🤖 Response generation
# ---------------------------
def get_mentor_answer(question: str) -> str:
    """Send the question to OpenAI and return the mentor response text."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


# ---------------------------
# 🧩 Main UI flow
# ---------------------------
def main() -> None:
    """Render controls, process user input, and show responses/history/audio."""
    initialize_state()

    # Toggle allows users to turn voice output on or off.
    voice_enabled = st.toggle("Enable voice output", value=True)

    # Multi-line text input for coding questions and longer debugging context.
    user_input = st.text_area(
        "Ask your question:",
        height=180,
        placeholder="""Example:

Explain why this React code is not updating:

const [count, setCount] = useState(0);

setCount(count + 1);
setCount(count + 1);
""",
    )

    # Action button triggers API call and app state updates.
    if st.button("Generate Answer"):
        if user_input.strip() == "":
            st.warning("Please enter a question")
        else:
            with st.spinner("Thinking... 🤖"):
                try:
                    # Generate and store new answer.
                    answer = get_mentor_answer(user_input)
                    st.session_state.latest_answer = answer

                    # Append new exchange to chat history.
                    st.session_state.chat_history.append(
                        {"question": user_input, "answer": answer}
                    )
                except Exception as e:
                    st.error(f"Error: {e}")

    # Display most recent answer when available.
    if st.session_state.latest_answer:
        st.subheader("📘 Latest Explanation")
        st.write(st.session_state.latest_answer)

        # Generate and play audio only when voice output is enabled.
        if voice_enabled:
            audio_file = generate_audio(st.session_state.latest_answer)
            st.audio(audio_file)

    # Always render full conversation history beneath the latest answer.
    render_chat_history()


if __name__ == "__main__":
    main()
