import streamlit as st
from PIL import Image

# --- Setup ---
st.set_page_config(page_title="MyPadi", layout="centered", initial_sidebar_state="collapsed")

# --- Persistent Page State ---
if "page" not in st.session_state:
    st.session_state.page = "Home"

# --- Query Params Routing ---
params = st.query_params
page = params.get("page", st.session_state.page)

if st.session_state.page != page:
    st.session_state.page = page

# --- Custom Navigation Menu ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        body, .stApp {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(120deg, #f3eaff 0%, #e8f6f3 100%);
            margin-top: -80px;
        }

        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: -30px;
            margin-bottom: -10px;
        }

        .nav {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1.5rem;
            gap: 1rem;
        }

        .nav button {
            background-color: #7e57c2;
            color: white;
            padding: 0.4rem 0.9rem;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
        }

        .nav button:hover {
            background-color: #693cb3;
        }

        .card {
            border-radius: 10px;
            padding: 1rem;
            margin: 0.6rem auto;
            width: 90%;
            max-width: 420px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            text-align: center;
            transition: all 0.3s ease-in-out;
        }

        .card1 { background: #f3eaff; }
        .card2 { background: #fff3e6; }
        .card3 { background: #e8f6f3; }

        .card:hover {
            transform: scale(1.01);
            box-shadow: 0 8px 18px rgba(126, 87, 194, 0.2), 0 0 6px rgba(126, 87, 194, 0.1);
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: #2a2a2a;
        }

        .card-desc {
            font-size: 0.85rem;
            color: #333;
            margin-bottom: 0.8rem;
        }

        .card-button {
            background: #7e57c2;
            color: white !important;
            padding: 0.35rem 1rem;
            font-size: 0.85rem;
            border: none;
            border-radius: 6px;
            text-decoration: none !important;
            transition: background 0.2s ease;
            display: inline-block;
        }

        .card-button:hover {
            background: #693cb3;
        }

        .welcome-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-top: 0.5rem;
            margin-bottom: 0.3rem;
            color: #333;
        }

        .welcome-subtitle {
            text-align: center;
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 0.6rem;
        }

    </style>
""", unsafe_allow_html=True)

# --- Navigation Buttons ---
st.markdown("<div class='nav'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🏠 Home"):
        st.session_state.page = "Home"
        st.query_params["page"] = "Home"
with col2:
    if st.button("ℹ️ About"):
        st.session_state.page = "About"
        st.query_params["page"] = "About"
with col3:
    if st.button("📬 Contact"):
        st.session_state.page = "Contact"
        st.query_params["page"] = "Contact"
st.markdown("</div>", unsafe_allow_html=True)

# --- Logo ---
logo = Image.open("logo.png")
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image(logo, width=100)
st.markdown("</div>", unsafe_allow_html=True)

# --- Page Routing Logic ---
def feature_card(emoji, title, desc, link, style_class):
    st.markdown(f"""
        <div class='card {style_class}'>
            <div class='card-title'>
                <span style="font-family: 'Segoe UI Emoji'; margin-right: 0.3rem;">{emoji}</span>{title}
            </div>
            <div class='card-desc'>{desc}</div>
            <a href="{link}" class="card-button">Get Started</a>
        </div>
    """, unsafe_allow_html=True)

if st.session_state.page == "Home":
    st.markdown("<div class='welcome-title'>Welcome to MyPadi</div>", unsafe_allow_html=True)
    st.markdown("<div class='welcome-subtitle'>Explore helpful tools to support your sexual health journey.</div>", unsafe_allow_html=True)

    feature_card("🤖", "MyPadi Chatbot", "Chat with a friendly AI about your sexual health questions.", "/Chatbot", "card1")
    feature_card("🧠", "Myth vs Fact Quiz", "Play a fun quiz to test your sexual health knowledge.", "/Myth_vs_Fact_Quiz", "card2")
    feature_card("🩺", "Symptom Checker", "Answer quick questions to assess your STI or pregnancy risk.", "/Symptom_Checker", "card3")

    st.markdown("<hr style='border: 1px solid #ddd; margin: 1rem auto; width: 70%;'>", unsafe_allow_html=True)

    st.markdown("<h4 style='text-align:center;'>Why Choose MyPadi?</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    benefits = [
        ("fas fa-lock", "Confidential & Secure"),
        ("fas fa-language", "Multilingual Support"),
        ("fas fa-user-graduate", "Youth Friendly"),
        ("fas fa-mobile-alt", "Mobile Ready"),
    ]
    for i, (icon, text) in enumerate(benefits):
        with cols[i]:
            st.markdown(f"""
                <div style='text-align:center; font-size:1.8rem; color:#7e57c2; margin-bottom:0.2rem;'>
                    <i class="{icon}"></i>
                </div>
                <div style='text-align:center; font-size:0.85rem; color:#333;'>{text}</div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "About":
    st.markdown("## ℹ️ About MyPadi")
    st.markdown("MyPadi is a youth-focused platform built to offer safe, fun, and informative sexual health resources.")
    st.markdown("- 💬 Chat with a non-judgy bot")
    st.markdown("- 🤓 Bust common myths")
    st.markdown("- 🧪 Do a quick symptom check")

elif st.session_state.page == "Contact":
    st.markdown("## 📬 Contact Us")
    st.markdown("We'd love to hear from you!")
    st.markdown("📧 Email: hello@mypadi.org")
    st.markdown("📍 Location: Lagos, Nigeria")

# --- Footer ---
st.markdown("""
    <div style='text-align:center; font-size:0.75rem; margin-top:2rem; color:#777;'>
        © 2025 MyPadi. Built with 💜 for Nigeria's youth.
    </div>
""", unsafe_allow_html=True)
