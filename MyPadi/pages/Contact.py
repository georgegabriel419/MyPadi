import streamlit as st

# ---- Page Config ----
st.set_page_config(page_title="Contact Me | MyPadi", layout="centered", initial_sidebar_state="auto")

# ---- Font + CSS ----
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, .stApp {
            font-family: 'Poppins', sans-serif;
            background-color: #f8f4ff;
        }

        .contact-container {
            text-align: center;
            margin-top: 3rem;
        }

        .intro {
            font-size: 1.1rem;
            color: #444;
            margin-top: 1rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .social-icons {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 2.5rem;
            gap: 2.5rem;
            flex-wrap: wrap;
        }

        .social-item {
            text-align: center;
            font-size: 0.9rem;
        }

        .social-item i {
            font-size: 2.5rem;
            margin-bottom: 0.3rem;
        }

        .social-link {
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            margin-top: 0.3rem;
        }

        .instagram { color: #E1306C; }
        .linkedin { color: #0077B5; }
        .x-twitter { color: #000000; }
        .gmail { color: #D44638; }

        .social-item a:hover {
            opacity: 0.8;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Main Content ----
st.markdown("<div class='contact-container'>", unsafe_allow_html=True)
st.markdown("<h2>📬 Contact Me</h2>", unsafe_allow_html=True)
st.markdown("""
    <p class='intro'>
        Hi! I'm <strong>Gabriel George</strong>. Feel free to reach out or follow me on social media. <br>
        I'm always open to connecting and collaborations 💜
    </p>
""", unsafe_allow_html=True)

# ---- Social Links ----
socials = [
    {
        "name": "Instagram",
        "url": "https://www.instagram.com/george.gabriel.54772?igsh=bHFzMGw5Y2kzNGdu",
        "icon": "fab fa-instagram",
        "class": "instagram"
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/in/gabriel-george-mobolaji?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app",
        "icon": "fab fa-linkedin",
        "class": "linkedin"
    },
    {
        "name": "X",
        "url": "https://x.com/M0du1uss?t=AHkNx27wjU0Bwo268CHcnw&s=09",
        "icon": "fab fa-x-twitter",
        "class": "x-twitter"
    },
    {
        "name": "Gmail",
        "url": "mailto:georgegabriel546@gmail.com",
        "icon": "fas fa-envelope",
        "class": "gmail"
    }
]

# ---- Render Socials ----
st.markdown("<div class='social-icons'>", unsafe_allow_html=True)
for s in socials:
    st.markdown(f"""
        <div class='social-item'>
            <a href='{s["url"]}' target='_blank' class='social-link'>
                <i class='{s["icon"]} {s["class"]}'></i><br>
                {s["name"]}
            </a>
        </div>
    """, unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)
