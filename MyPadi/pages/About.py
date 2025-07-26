import streamlit as st

st.set_page_config(page_title="About MyPadi", layout="centered")
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
""", unsafe_allow_html=True)

# ---- Styles ----
st.markdown("""
    <style>
        body, .stApp {
            background: linear-gradient(120deg, #f3eaff 0%, #e8f6f3 100%);
            font-family: 'Poppins', sans-serif;
        }

        .title {
            text-align: center;
            font-size: 2.4rem;
            font-weight: 700;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            color: #333;
        }

        .divider {
            border: 1px solid #ddd;
            margin: 1rem auto;
            width: 80%;
        }

        .about-text {
            font-size: 1rem;
            line-height: 1.7;
            color: #333;
            max-width: 750px;
            margin: 0 auto 2rem;
            text-align: center;
        }

        .feature-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin: 2rem auto;
            max-width: 650px;
        }

        .feature-item {
            background: #ffffffaa;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .feature-item i {
            font-size: 1.2rem;
            color: #7e57c2;
        }

        .footer {
            text-align: center;
            color: #777;
            margin-top: 2rem;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown("<div class='title'>About MyPadi</div>", unsafe_allow_html=True)
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---- Description ----
st.markdown("""
<div class="about-text">
    <strong>MyPadi</strong> is your digital best friend — helping you talk openly about sexual and reproductive health without shame or judgment.
    <br><br>
    Whether you're curious, confused, or concerned, MyPadi is here to listen and help. We provide honest, youth-friendly, and culturally sensitive support — all in your language.
    <br><br>
    Built for teens and young adults in Nigeria, MyPadi supports <strong>English</strong>, <strong>Yoruba</strong>, <strong>Igbo</strong>, <strong>Hausa</strong>, and <strong>Pidgeon</strong> — so no one is left out.
</div>
""", unsafe_allow_html=True)

# ---- Features ----
st.markdown("""
<div class="feature-list">
    <div class="feature-item">
        <i class="fas fa-comments"></i>
        <span><strong>Smart AI Chatbot:</strong> Ask anything about STIs, pregnancy & more</span>
    </div>
    <div class="feature-item">
        <i class="fas fa-heartbeat"></i>
        <span><strong>Symptom Checker:</strong> Quick risk check for STI & pregnancy</span>
    </div>
    <div class="feature-item">
        <i class="fas fa-question-circle"></i>
        <span><strong>Myth vs Fact Quiz:</strong> Bust common myths with fun learning</span>
    </div>
    <div class="feature-item">
        <i class="fas fa-shield-alt"></i>
        <span><strong>Private & Safe:</strong> No data stored, no judgment, always respectful</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---- Footer ----
st.markdown("<div class='footer'>Made with 💜 by your friends at MyPadi</div>", unsafe_allow_html=True)
