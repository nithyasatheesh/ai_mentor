import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile

# 🔐 Use Streamlit secrets (DO NOT hardcode key)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("💻 AI Coding Mentor (Smart + Concept Ready) 🚀")

# 🎙️ Generate audio
def generate_audio(text):
    clean_text = (
        text.replace("`", "")
        .replace("*", "")
        .replace("#", "")
    )

    tts = gTTS(clean_text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name


# 🧠 Mentor prompt (UPDATED)
SYSTEM_PROMPT = """
You are an AI coding mentor.

You can answer:
- Programming questions
- Conceptual questions
- Theoretical explanations
- Real-world scenarios
- Debugging problems

Guidelines:
- Explain in simple English
- Be clear and structured
- If coding question → give code + explanation
- If concept question → explain with examples
- Avoid complex jargon
- Keep it beginner friendly
"""

# 💬 User input
user_input = st.text_input("Ask your question (coding or concept):")

if user_input:

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response.choices[0].message.content

    # 📘 Show text
    st.subheader("📘 Explanation")
    st.write(answer)

    # 🎙️ Play audio
    audio_file = generate_audio(answer)
    st.audio(audio_file)
