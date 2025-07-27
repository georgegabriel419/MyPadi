import streamlit as st
st.set_page_config(page_title="Myth vs Fact Quiz", page_icon="🧠")  # ✅ Must be first

import random
import os
from dotenv import load_dotenv
import google.generativeai as genai
from myth_data import (
    quiz_data_english,
    quiz_data_yoruba,
    quiz_data_igbo,
    quiz_data_hausa,
    quiz_data_pidgin
)
from style import apply_custom_styles

apply_custom_styles()

# Load API Key
load_dotenv()
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Language-to-quiz-data mapping
language_map = {
    "English": ("English", quiz_data_english),
    "Yoruba": ("Yoruba", quiz_data_yoruba),
    "Igbo": ("Igbo", quiz_data_igbo),
    "Hausa": ("Hausa", quiz_data_hausa),
    "Pidgin": ("Pidgin English", quiz_data_pidgin)
}

# Default session state
defaults = {
    "started": False,
    "age_group": None,
    "language": None,
    "questions": [],
    "index": 0,
    "score": 0,
    "feedback": [],
    "incorrect": [],
    "answered": False,
    "user_choice": None,
    "ai_response": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# 🌐 Language & Age Group Setup
if not st.session_state.started:
    st.title("🧠 SRH Myth vs Fact Quiz")

    st.subheader("🌍 Choose your language:")
    lang_choice = st.selectbox("Pick a language:", ["Select Language"] + list(language_map.keys()), index=0)

    st.subheader("👤 Choose your age group:")
    age_choice = st.selectbox("Pick your group:", ["Select Age Group", "10-13", "14-17", "18+"], index=0)

    if st.button("✅ Start Quiz"):
        if lang_choice == "Select Language" or age_choice == "Select Age Group":
            st.warning("Please select both language and age group to continue.")
        else:
            readable_lang, data = language_map[lang_choice]
            st.session_state.language = readable_lang
            st.session_state.age_group = age_choice

            all_questions = [q for q in data if q["age_group"] == age_choice]
            random.shuffle(all_questions)
            st.session_state.questions = all_questions[:10]

            st.session_state.started = True
            st.rerun()

# 🧠 Quiz Logic
elif st.session_state.index < len(st.session_state.questions):
    lang = st.session_state.language
    q = st.session_state.questions[st.session_state.index]
    st.subheader(f"Q{st.session_state.index + 1}: {q['statement']}")

    if not st.session_state.answered:
        user_answer = st.radio(
            "Is this a Myth or a Fact?",
            ["Myth", "Fact"],
            key=f"q_{st.session_state.index}",
            index=None
        )

        if user_answer:
            is_user_myth = user_answer == "Myth"
            correct = is_user_myth == q["is_myth"]

            if correct:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error("❌ Incorrect.")
                st.session_state.incorrect.append(q["statement"])

            with st.spinner("💡 Creating your tip..."):
                try:
                    prompt = f"""
                    A Nigerian teen who speaks {lang} answered: "{q['statement']}" and said it's a {"Myth" if is_user_myth else "Fact"}.
                    Respond in {lang} with a short, caring correction and 1 tip on sexual health.
                    Be friendly and helpful.
                    """
                    response = model.generate_content(prompt)
                    feedback = response.text.strip()
                except:
                    feedback = "⚠️ Feedback not available."

            st.session_state.ai_response = feedback
            st.session_state.feedback.append(feedback)
            st.session_state.answered = True

    if st.session_state.answered:
        st.markdown("### 💬 MyPadi's Tip:")
        st.info(st.session_state.ai_response)

        if st.session_state.index < len(st.session_state.questions) - 1:
            if st.button("➡️ Next Question"):
                st.session_state.index += 1
                st.session_state.answered = False
                st.session_state.user_choice = None
                st.session_state.ai_response = ""
                st.rerun()
        else:
            if st.button("📝 Submit Quiz"):
                st.session_state.index += 1
                st.rerun()

# ✅ Final Score Page
else:
    st.header("🎉 Quiz Completed!")
    st.markdown(f"**Your Score:** {st.session_state.score} / {len(st.session_state.questions)}")

    if st.session_state.incorrect:
        st.subheader("You missed:")
        for wrong in st.session_state.incorrect:
            st.write(f"❌ {wrong}")

        with st.spinner("🧠 Summarizing your learning tips..."):
            try:
                missed = "\n".join(st.session_state.incorrect)
                prompt = f"""
                A Nigerian teen who speaks {st.session_state.language} missed these questions:\n\n{missed}
                Write a friendly summary in {st.session_state.language} to help them improve and remember.
                """
                result = model.generate_content(prompt)
                st.markdown("### 🧠 Smart Tip Summary:")
                st.success(result.text.strip())
            except:
                st.warning("⚠️ Couldn't generate summary.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔁 Restart"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    with col2:
        st.markdown(
            "<a href='/Chatbot' target='_self'>"
            "<button style='padding:0.5rem 1rem; font-size:0.85rem; background:#7e57c2; color:white; border:none; border-radius:8px;'>"
            "💬 Chat with MyPadi</button></a>",
            unsafe_allow_html=True
        )

# 🟢 Optional main() definition
def main():
    pass  # No need to rerun main() inside this script since it's not used as a module
