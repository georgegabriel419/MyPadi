import streamlit as st
import google.generativeai as genai
from symptom_data import sti_questions, pregnancy_questions

# ✅ SET YOUR GOOGLE API KEY
GOOGLE_API_KEY = "AIzaSyDyoAA9MRyZvBSLD45vp9xJdsuyJff3xDo"

if not GOOGLE_API_KEY:
    st.error("Google API key is missing. Please set it in the code.")
    st.stop()

# ✅ Configure Gemini
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")  # faster + cheaper
except Exception as e:
    st.error("Failed to initialize Gemini model. Check your API key or model name.")
    st.stop()

# ✅ Initialize session state
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# ✅ Page setup
st.set_page_config(page_title="Smart Symptom Checker", page_icon="🩺")
st.title("🩺 Smart Symptom Checker")
st.write("Answer a few quick questions to get a personalized health risk estimate.")

# ✅ Choose category
category = st.selectbox("Choose a category:", ["STI", "Pregnancy"])
questions = sti_questions if category == "STI" else pregnancy_questions

# ✅ Quiz logic
if st.session_state.question_index < len(questions):
    current = questions[st.session_state.question_index]
    st.markdown(f"**Q{st.session_state.question_index + 1}: {current['question']}**")

    col1, col2 = st.columns(2)
    if col1.button("Yes"):
        st.session_state.score += current["risk_weight"]
        st.session_state.answers.append(f"✅ {current['question']}")
        st.session_state.question_index += 1
        st.rerun()
    elif col2.button("No"):
        st.session_state.answers.append(f"❌ {current['question']}")
        st.session_state.question_index += 1
        st.rerun()

# ✅ Final result + AI feedback
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

    # ✅ AI-generated advice
    with st.spinner("Thinking like your bestie... 🤔"):
        user_summary = "\n".join(st.session_state.answers)
        prompt = f"""
        You are MyPadi — a friendly and caring health buddy for teens and young adults.

        A user just finished a {category} symptom quiz.
        Based on their answers:

        1. Explain their possible **risk level** (don’t just repeat score).
        2. Give 1–2 short, practical **next steps** (like “get tested”, “rest”, or “see a clinic”).
        3. Share an encouraging, kind **emotional support** message.
        4. Suggest one gentle **follow-up question** to keep them informed or safe.

        Use a casual, warm tone. No big words or judgment — just gist like you're their best friend.

        Their answers:
        {user_summary}
        """

        try:
            response = model.generate_content(prompt)
            st.markdown("### 🤖 AI-Powered Summary")
            st.success(response.text.strip())
        except Exception as e:
            st.error("Failed to generate AI summary.")
            st.exception(e)

    # ✅ Restart button
    if st.button("🔄 Restart Quiz"):
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()