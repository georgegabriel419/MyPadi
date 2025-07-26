# style.py — shared theme module for all pages

def apply_custom_styles():
    import streamlit as st
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
