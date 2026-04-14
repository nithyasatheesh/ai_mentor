import streamlit as st
import os
from openai import OpenAI
from gtts import gTTS
import tempfile

# ✅ Correct way to read API key from Streamlit Secrets
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Coding Mentor", layout="centered")

st.title("💻 AI Coding Mentor (Online 🚀)")

# 🔊 Generate audio
def generate_audio(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# 💬 User input
user_input = st.text_input("Ask your coding mentor:")

if user_input:
    with st.spinner("Thinking... 🤖"):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful coding mentor. Explain clearly with examples."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ]
            )

            answer = response.choices[0].message.content

            # Show answer
            st.success("Answer:")
            st.write(answer)

            # 🔊 Play audio
            audio_file = generate_audio(answer)
            st.audio(audio_file, format="audio/mp3")

        except Exception as e:
            st.error("❌ Error occurred. Check API key or logs.")
            st.write(e)
