import streamlit as st
from PIL import Image

# ---- Page Config ----
st.set_page_config(page_title="MyPadi", layout="centered")

# ---- Custom CSS + Hamburger Menu ----
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        body, .stApp {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(120deg, #f3eaff 0%, #e8f6f3 100%);
            margin-top: -80px;
        }

        /* Logo center */
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: -30px;
            margin-bottom: -10px;
        }

        /* Hamburger menu */
        .menu-icon {
            position: absolute;
            top: 1.2rem;
            right: 1.5rem;
            font-size: 1.6rem;
            color: #7e57c2;
            cursor: pointer;
            z-index: 999;
        }

        .dropdown-menu {
            position: absolute;
            top: 3.5rem;
            right: 1.5rem;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            display: none;
            flex-direction: column;
            padding: 0.5rem 0;
            z-index: 999;
        }

        .dropdown-menu a {
            padding: 0.6rem 1.2rem;
            text-decoration: none;
            color: #333;
            font-weight: 600;
            transition: background 0.2s ease;
        }

        .dropdown-menu a:hover {
            background: #f3eaff;
        }

        /* Card styles */
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

        .emoji {
            display: inline-block;
            width: 1.5em;
            margin-right: 0.3rem;
        }

        /* JS for toggling dropdown */
        <script>
            const toggleMenu = () => {
                const menu = document.querySelector('.dropdown-menu');
                if (menu.style.display === 'flex') {
                    menu.style.display = 'none';
                } else {
                    menu.style.display = 'flex';
                }
            }
        </script>
    </style>

    <!-- Hamburger Icon -->
    <div class="menu-icon" onclick="toggleMenu()">
        <i class="fas fa-bars"></i>
    </div>

    <!-- Dropdown Menu -->
    <div class="dropdown-menu" id="menu">
        <a href="/">Home</a>
        <a href="/About">About</a>
        <a href="/Contact">Contact</a>
    </div>

    <!-- JS for menu toggle -->
    <script>
        const toggleMenu = () => {
            const menu = document.getElementById('menu');
            if (menu.style.display === 'flex') {
                menu.style.display = 'none';
            } else {
                menu.style.display = 'flex';
            }
        }
    </script>
""", unsafe_allow_html=True)

# ---- Logo ----
logo = Image.open("logo.png")
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
st.image(logo, width=100)
st.markdown("</div>", unsafe_allow_html=True)

# ---- Headline & Subtitle ----
st.markdown("<div class='welcome-title'>Welcome to MyPadi</div>", unsafe_allow_html=True)
st.markdown("<div class='welcome-subtitle'>Explore helpful tools to support your sexual health journey.</div>", unsafe_allow_html=True)

# ---- Feature Cards ----
def feature_card(emoji, title, desc, link, style_class):
    st.markdown(f"""
        <div class='card {style_class}'>
            <div class='card-title'>
                <span class="emoji" style="font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', sans-serif;">{emoji}</span>{title}
            </div>
            <div class='card-desc'>{desc}</div>
            <a href="{link}" class="card-button">Get Started</a>
        </div>
    """, unsafe_allow_html=True)

# ---- Cards ----
feature_card("🤖", "MyPadi Chatbot", "Chat with a friendly AI about your sexual health questions.", "/Chatbot", "card1")
feature_card("🧠", "Myth vs Fact Quiz", "Play a fun quiz to test your sexual health knowledge.", "/Myth_vs_Fact_Quiz", "card2")
feature_card("🩺", "Symptom Checker", "Answer quick questions to assess your STI or pregnancy risk.", "/Symptom_Checker", "card3")

# ---- Divider ----
st.markdown("<hr style='border: 1px solid #ddd; margin: 1rem auto; width: 70%;'>", unsafe_allow_html=True)

# ---- Why Choose Us ----
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

# ---- Footer ----
st.markdown("""
<div style='text-align:center; font-size:0.75rem; margin-top:2rem; color:#777;'>
    © 2025 MyPadi. Built with 💜 for Nigeria's youth.
</div>
""", unsafe_allow_html=True)
