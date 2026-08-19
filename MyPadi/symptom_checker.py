import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from spitch import Spitch
from symptom_data import sti_questions, pregnancy_questions
from style import apply_custom_styles

apply_custom_styles()

# ✅ Global style
st.set_page_config(page_title="Smart Symptom Checker", page_icon="🩺")

st.markdown("""
    <style>
    .stApp {
        background-color: #f8f5ff;
    }
    .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stCaption,
    .stTextInput > label, .stRadio > label, .stSelectbox > label,
    .stTextArea > label, .stNumberInput > label, .stCheckbox > label {
        color: black !important;
    }
    .stButton>button {
        background-color: #7e57c2;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: bold;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #693cb3;
    }
    </style>
""", unsafe_allow_html=True)

def trim_to_words(text, limit=500):
    words = text.split()
    return ' '.join(words[:limit]) + ('...' if len(words) > limit else '')

def synthesize_tts(text, lang="en"):
    try:
        spitch_client = Spitch()
        response = spitch_client.speech.generate(
            text=text,
            language=lang,
            voice="femi"
        )
        return response.read()
    except Exception:
        return None

def main():
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")  # Optional

    if not GOOGLE_API_KEY:
        st.error("❌ Google API key is missing. Add it to your .env file as GOOGLE_API_KEY.")
        return

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-3.6-flash")
    except Exception:
        st.error("⚠️ Failed to initialize Gemini model.")
        return

    for key, default in {
        "question_index": 0,
        "score": 0,
        "answers": []
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    st.title("🩺 Smart Symptom Checker")
    st.write("Answer a few quick questions to get a personalized health risk estimate.")

    category = st.selectbox("Choose a category:", ["STI", "Pregnancy"])
    questions = sti_questions if category == "STI" else pregnancy_questions

    if st.session_state.question_index < len(questions):
        current = questions[st.session_state.question_index]
        st.markdown(f"**Q{st.session_state.question_index + 1}: {current['question']}**")

        col1, col2 = st.columns(2)
        if col1.button("Yes"):
            st.session_state.score += current["risk_weight"]
            st.session_state.answers.append(f"✅ {current['question']}")
            st.session_state.question_index += 1
            st.rerun()

        if col2.button("No"):
            st.session_state.answers.append(f"❌ {current['question']}")
            st.session_state.question_index += 1
            st.rerun()

    else:
        max_score = sum(q["risk_weight"] for q in questions)
        percentage = (st.session_state.score / max_score) * 100
        risk_level = (
            "🟢 Low Risk" if percentage <= 33 else
            "🟡 Medium Risk" if percentage <= 66 else
            "🔴 High Risk"
        )

        st.subheader("📊 Risk Assessment Result")
        st.markdown(f"**Your Risk Level:** {risk_level}")
        st.markdown(f"**Score:** {st.session_state.score} / {max_score} → {percentage:.1f}%")

        with st.spinner("Thinking like your bestie... 🤔"):
            user_summary = "\n".join(st.session_state.answers)

            if category == "STI" and "High" in risk_level:
                prompt = f"""
                You are MyPadi, a helpful sexual health companion for Nigerian youth.

                A user just completed an STI symptom quiz with a HIGH risk score.
                Their answers:

                {user_summary}

                1. Based on symptoms, suggest a **possible STI** they may have (e.g., Chlamydia, Gonorrhea, etc.).
                2. Explain the risk in a friendly, easy-to-understand way.
                3. Give **next steps** (like testing or talking to a clinic).
                4. End with an **encouraging message** and helpful follow-up question.

                Your response should be structured well. Use bulletin where necessary. Don't make it essay format. 

                Avoid judgment. Be gentle, relatable, and supportive.
                """
            else:
                prompt = f"""
                You are MyPadi — a friendly and caring health buddy for teens and young adults.

                A user just finished a {category} symptom quiz.
                Based on their answers:

                1. Explain their possible **risk level** (don’t just repeat score).
                2. Give, practical **next steps** (like “get tested”, “rest”, or “see a clinic”).
                3. Share an encouraging, kind **emotional support** message.
                4. Suggest one gentle **follow-up question** to keep them informed or safe.
                Your response should be structured well. use bulletin where necessary. 
                Use a casual, warm tone. No big words or judgment — just gist like you're their best friend.

                Their answers:
                {user_summary}
                """

            try:
                response = model.generate_content(prompt)
                trimmed = trim_to_words(response.text.strip(), 500)
                st.markdown("### 💬 MyPadi's Summary")
                st.success(trimmed)

                # Play audio feedback
                if SPITCH_API_KEY:
                    audio_bytes = synthesize_tts(trimmed)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/wav")
            except Exception as e:
                st.error("⚠️ Failed to generate AI summary.")
                st.exception(e)

        if st.button("🔄 Restart Quiz"):
            for key in ["question_index", "score", "answers"]:
                st.session_state[key] = 0 if key != "answers" else []
            st.rerun()

if __name__ == "__main__":
    main()
