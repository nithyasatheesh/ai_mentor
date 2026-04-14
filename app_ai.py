import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile

client = OpenAI(api_key="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")

st.title("💻 AI Coding Mentor (Online 🚀)")

def generate_audio(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

user_input = st.text_input("Ask your coding mentor:")

if user_input:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a coding mentor. Explain clearly."},
            {"role": "user", "content": user_input}
        ]
    )

    answer = response.choices[0].message.content

    st.write(answer)

    audio_file = generate_audio(answer)
    st.audio(audio_file)
