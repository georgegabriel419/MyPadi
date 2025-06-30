import streamlit as st
import random
import google.generativeai as genai
from myth_data import quiz_data  # Make sure your questions have "age_group"

# 🔐 Configure Gemini API Key
genai.configure(api_key="AIzaSyBOpT5FiGuqeLhjMiEDrVzWc2hsnzZNWkk")
model = genai.GenerativeModel("models/gemini-2.0-flash")

# 🧠 Session State Setup
if "age_group" not in st.session_state:
    st.session_state.age_group = None
if "started" not in st.session_state:
    st.session_state.started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "index" not in st.session_state:
    st.session_state.index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "incorrect" not in st.session_state:
    st.session_state.incorrect = []
if "answered" not in st.session_state:
    st.session_state.answered = False
if "user_choice" not in st.session_state:
    st.session_state.user_choice = None
if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""

st.title("🧠 SRH Myth vs Fact Quiz")

# 🧒 Age group selection
if not st.session_state.started:
    st.subheader("Choose your age group:")
    age_choice = st.radio("Pick your group:", ["10-13", "14-17", "18+"], key="age_select")

    if st.button("Start Quiz"):
        st.session_state.age_group = age_choice
        filtered = [q for q in quiz_data if q.get("age_group") == age_choice]
        random.shuffle(filtered)

        if not filtered:
            st.error("❌ No questions available for this age group.")
        else:
            st.session_state.questions = filtered
            st.session_state.started = True
            st.rerun()

# 🚀 Main Quiz
elif st.session_state.index < len(st.session_state.questions):
    q = st.session_state.questions[st.session_state.index]

    st.subheader(f"Q{st.session_state.index + 1}: {q['statement']}")

    if not st.session_state.answered:
        st.session_state.user_choice = st.radio("Is this a Myth or a Fact?", ["Myth", "Fact"], key=f"radio_{st.session_state.index}")

        if st.button("Submit Answer"):
            user_answer = st.session_state.user_choice == "Myth"
            correct = user_answer == q["is_myth"]

            if correct:
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error("❌ Incorrect.")
                st.session_state.incorrect.append(q["statement"])

            # 🔍 Get AI feedback
            with st.spinner("Getting expert feedback..."):
                try:
                    prompt = f"""
                    A Nigerian teen answered: "{q['statement']}" and said it's a {"Myth" if user_answer else "Fact"}.
                    Respond with a friendly correction and one quick SRH tip.
                    """
                    response = model.generate_content(prompt)
                    st.session_state.ai_response = response.text.strip()
                    st.session_state.feedback.append(st.session_state.ai_response)
                except:
                    st.session_state.ai_response = "⚠️ Feedback not available."
                    st.session_state.feedback.append(st.session_state.ai_response)

            st.session_state.answered = True

    if st.session_state.answered:
        st.markdown("### 🤖 AI Feedback:")
        st.info(st.session_state.ai_response)

        if st.button("Next Question"):
            st.session_state.index += 1
            st.session_state.answered = False
            st.session_state.user_choice = None
            st.session_state.ai_response = ""
            st.rerun()

# ✅ Completion
else:
    st.header("🎉 Quiz Completed!")
    st.markdown(f"**Score:** {st.session_state.score} / {len(st.session_state.questions)}")

    if st.session_state.incorrect:
        st.subheader("You missed:")
        for wrong in st.session_state.incorrect:
            st.write(f"❌ {wrong}")

        with st.spinner("Creating learning tip..."):
            try:
                wrongs_text = "\n".join(st.session_state.incorrect)
                prompt = f"""
                A Nigerian youth missed these SRH questions:

                {wrongs_text}

                Provide a short, positive summary to help them understand and improve. Make it sound friendly.
                """
                summary = model.generate_content(prompt)
                st.success(summary.text.strip())
            except:
                st.warning("⚠️ Couldn't generate summary.")

    if st.button("🔄 Restart Quiz"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()