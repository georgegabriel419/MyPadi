import os
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from pinecone import Pinecone
from keywords import allowed_keywords  # Make sure this exists

nest_asyncio.apply()
load_dotenv()

PINECONE_API_KEY = "pcsk_5dpELm_NtvrjntzjQt2by64KzgA8hDvm9gY6vSHDXdRA4CsL6G2wgMn6srfUAudeFznf4P"
GOOGLE_API_KEY = "AIzaSyBOpT5FiGuqeLhjMiEDrVzWc2hsnzZNWkk"

# Init Pinecone & Embedding
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("sti-teenage-preg")
embed_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GOOGLE_API_KEY
)

# Friendly tone greeting per language
language_greetings = {
    "English": "Hey bestie! 😊 I'm MyPadi. Let's gist about STIs, pregnancy or anything health-y.",
    "Yoruba": "Ore mi! 😊 Oruko mi ni MyPadi. E je ka ba ara wa soro nipa STI ati oyun.",
    "Igbo": "Nwanne m! 😊 Aha m bu MyPadi. Ka anyi kparita okwu banyere STIs na ime nwa.",
    "Hausa": "Sannu kawaye! 😊 Ni MyPadi ne. Mu tattauna STI ko ciki na matasa.",
    "Pidgin": "Hey my padi! 😊 Make we yarn well-well about STI or belle palava."
}

system_prompt_template_base = """
You are MyPadi — the user's best friend and health gist buddy.
You give warm, non-judgy advice about STIs and teenage pregnancy in {lang}.
Sound casual, fun, and caring. Like you're chatting with your close friend.

Use this info if helpful:
{doc_content}

Be brief (1–3 sentences), but full of love and help.
If question is not relevant, gently ask for STI or teenage pregnancy-related questions.

IMPORTANT: Always respond in {lang}, no matter the question’s language. If the user asks in English but chose {lang}, still reply in {lang}.
"""

def translate_prompt_language(lang):
    return {
        "Yoruba": "Yoruba",
        "Igbo": "Igbo",
        "Hausa": "Hausa",
        "Pidgin": "Pidgin English"
    }.get(lang, "English")

def generate_response(question, user_lang):
    if not any(keyword in question.lower() for keyword in allowed_keywords):
        return {
            "English": "Hmm bestie 🫶🏾 — I can only help with STI and teenage pregnancy matters. Ask me something like that!",
            "Yoruba": "Ore mi 🫶🏾 — Mo le ran e lowo lori koko STI ati oyun lasiko omode nikan.",
            "Igbo": "Nwanne 🫶🏾 — Ana m enyere maka STIs na ime nwa n'oge ntorobịa.",
            "Hausa": "Kawaye 🫶🏾 — Tambayoyina na game da STI ko ciki a kuruciya ne kawai.",
            "Pidgin": "Padi mi 🫶🏾 — Na only STI or teenage belle I sabi talk about oh."
        }.get(user_lang, "Sorry bestie — let’s stick to STIs and teenage pregnancy gists.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    query_embed = embed_model.embed_query(question)
    query_embed = [float(val) for val in query_embed]

    results = pinecone_index.query(
        vector=query_embed,
        top_k=3,
        include_values=False,
        include_metadata=True
    )

    doc_contents = [match['metadata'].get('text', '') for match in results.get('matches', [])]
    doc_content = "\n".join(doc_contents).replace("{", "{{").replace("}", "}}") or "No extra gist found."

    prompt_template = system_prompt_template_base.format(
        doc_content=doc_content,
        lang=translate_prompt_language(user_lang)
    )

    chat_history = ChatMessageHistory()
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_history.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            chat_history.add_ai_message(msg["content"])

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=chat_history,
        return_messages=True
    )

    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(prompt_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )

    chat = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    conversation = LLMChain(
        llm=chat,
        prompt=prompt,
        memory=memory,
        verbose=False
    )

    try:
        res = conversation.invoke({"question": question})
        return res.get('text', '').strip()
    except Exception as e:
        return f"Ahn ahn, something go wrong o 😥 ({str(e)})"

# ───── Streamlit UI ─────
st.set_page_config(page_title="Chat with MyPadi", page_icon="💬")
st.title("💬 Talk to MyPadi – Safe Gist, Real Answers")

# First-time language selection
if "language" not in st.session_state:
    st.subheader("🌍 Choose your language to gist:")
    lang = st.radio("Select Language:", ["English", "Yoruba", "Igbo", "Hausa", "Pidgin"])
    if st.button("✅ Let's Go!"):
        st.session_state.language = lang
        st.rerun()

# After language is picked
else:
    lang = st.session_state.language
    st.success(f"🗣️ You're chatting in: **{lang}**")

    if st.button("🔄 Change Language"):
        del st.session_state["language"]
        st.rerun()

    st.markdown(f"#### {language_greetings.get(lang)}")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": language_greetings.get(lang)}
        ]

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("What’s on your mind?")
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Hold on bestie... thinking 🤔"):
            reply = generate_response(user_input, lang)

        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
