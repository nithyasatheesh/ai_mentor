import streamlit as st
from openai import OpenAI
from gtts import gTTS
import tempfile

# 🔐 Use Streamlit secrets (DO NOT hardcode key)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="AI Coding Mentor", layout="centered")

st.title("💻 AI Coding Mentor 🚀")
st.write("Ask coding or concept questions and get explanation + audio")

# ---------------------------
# 🎙️ Audio function
# ---------------------------
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


# ---------------------------
# 🧠 System Prompt
# ---------------------------
SYSTEM_PROMPT = """
You are an AI coding mentor.

You can answer:
- Programming questions
- Conceptual questions
- Real-world scenarios
- Debugging problems

Guidelines:
- Use simple English
- Be clear and structured
- If coding → give code + explanation
- If concept → explain with examples
- Keep it beginner friendly
"""


# ---------------------------
# 💬 Input
# ---------------------------
user_input = st.text_input("Ask your question:")

# ---------------------------
# 🚀 Button Trigger (FIXED)
# ---------------------------
if st.button("Generate Answer"):

    if user_input.strip() == "":
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking... 🤖"):

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_input}
                    ]
                )

                answer = response.choices[0].message.content

                # 📘 Output section (ALWAYS visible now)
                st.subheader("📘 Explanation")
                st.write(answer)

                # 🎙️ Audio
                audio_file = generate_audio(answer)
                st.audio(audio_file)

            except Exception as e:
                st.error(f"Error: {e}")
