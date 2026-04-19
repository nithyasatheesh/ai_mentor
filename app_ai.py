import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile
import os

# 🔐 Secure API key (from Streamlit secrets)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Coding Mentor", page_icon="💻")

st.title("💻 AI Coding Mentor 🚀")
st.write("Ask coding questions (Python, Java, React, .NET, PySpark)")

# Function to generate audio
def generate_audio(text):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# Input
user_input = st.text_input("Ask your coding mentor:")

# Button
if st.button("Get Answer"):
    if user_input.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking... 🤖"):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an expert AI coding mentor.

- Answer only coding-related questions
- Support Python, Java, React, .NET, PySpark
- Explain clearly with examples
- If not coding question, say:
'I can only help with coding-related questions.'
"""
                    },
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500
            )

            answer = response.choices[0].message.content

        # Show answer
        st.subheader("📘 Answer:")
        st.write(answer)

        # Show code format (if any)
        st.code(answer)

        # Generate audio
        audio_file = generate_audio(answer)

        st.subheader("🔊 Audio Explanation:")
        st.audio(audio_file)

        # Download button
        with open(audio_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Audio",
                data=f,
                file_name="answer.mp3",
                mime="audio/mpeg"
            )
