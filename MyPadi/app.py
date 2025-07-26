import streamlit as st

# ---- Page Config ----
st.set_page_config(page_title="MyPadi", layout="centered")

# ---- Custom CSS ----
st.markdown("""
    <style>
        body, .stApp {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(120deg, #f3eaff 0%, #e8f6f3 100%);
        }

        .welcome-title {
            text-align: center;
            font-size: 2.2rem;
            font-weight: 700;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .welcome-subtitle {
            text-align: center;
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 1.5rem;
        }

        .card {
            border-radius: 12px;
            padding: 1.2rem;
            margin: 1.2rem auto;
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
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
            color: #2a2a2a;
        }

        .card-desc {
            font-size: 0.9rem;
            color: #333;
            margin-bottom: 0.8rem;
        }

        .card-button {
            background: #7e57c2;
            color: white !important;
            padding: 0.4rem 1.2rem;
            font-size: 0.85rem;
            border: none;
            border-radius: 6px;
            text-decoration: none !important;
            display: inline-block;
            font-weight: 600;
        }

        .card-button:hover {
            background: #693cb3;
        }

        .menu {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1.2rem;
            margin-bottom: 2rem;
        }

        .menu a {
            font-weight: 600;
            color: #7e57c2;
            text-decoration: none;
            font-size: 0.95rem;
        }

        .menu a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Navigation Menu ----
st.markdown("""
<div class='menu'>
    <a href="/">Home</a>
    <a href="/About" target="_self">About</a>
    <a href="/Contact" target="_self">Contact</a>
</div>
""", unsafe_allow_html=True)

# ---- Title & Subtitle ----
st.markdown("<div class='welcome-title'>Welcome to MyPadi</div>", unsafe_allow_html=True)
st.markdown("<div class='welcome-subtitle'>Explore helpful tools to support your sexual health journey.</div>", unsafe_allow_html=True)

# ---- Feature Cards ----
def feature_card(emoji, title, desc, link, style_class):
    st.markdown(f"""
        <div class='card {style_class}'>
            <div class='card-title'>{emoji} {title}</div>
            <div class='card-desc'>{desc}</div>
            <a href="{link}" class="card-button">Get Started</a>
        </div>
    """, unsafe_allow_html=True)

feature_card("🤖", "MyPadi Chatbot", "Chat with a friendly AI about your sexual health questions.", "/Chatbot", "card1")
feature_card("🧠", "Myth vs Fact Quiz", "Play a fun quiz to test your sexual health knowledge.", "/Myth_vs_Fact_Quiz", "card2")
feature_card("🩺", "Symptom Checker", "Answer questions to assess your STI or pregnancy risk.", "/Symptom_Checker", "card3")

# ---- Footer ----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; font-size:0.75rem; margin-top:2rem; color:#777;'>
    © 2025 MyPadi. Built with 💜 for Nigeria's youth.
</div>
""", unsafe_allow_html=True)
