import os
import asyncio
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from spitch import Spitch
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from pinecone import Pinecone
from keywords import allowed_keywords
from style import apply_custom_styles

# ───── Apply Custom Theme ─────
apply_custom_styles()
st.set_page_config(page_title="Chat with MyPadi", page_icon="💬")

# ───── Init ─────
nest_asyncio.apply()
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("sti-teenage-preg")

index_info = pc.describe_index("sti-teenage-preg")
print("PINECONE INDEX INFO:", index_info)

embed_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)
spitch_client = Spitch()

# ───── Greetings ─────
language_greetings = {
    "English": "Hey bestie! 😊 I'm MyPadi. Let's gist about STIs, pregnancy or anything health-y.",
    "Yoruba": "Ore mi! 😊 Oruko mi ni MyPadi. E je ka ba ara wa soro nipa STI ati oyun.",
    "Igbo": "Nwanne m! 😊 Aha m bu MyPadi. Ka anyi kparita okwu banyere STIs na ime nwa.",
    "Hausa": "Sannu kawaye! 😊 Ni MyPadi ne. Mu tattauna STI ko ciki na matasa.",
    "Pidgin": "Hey my padi! 😊 Make we yarn well‑well about STI or belle palava."
}

system_prompt_template_base = """
You are MyPadi — the user's best friend and health gist buddy.
You give warm, non-judgy advice about STIs and teenage pregnancy in {lang}.
Sound casual, fun, and caring. Like you're chatting with your close friend.

Use this info if helpful:
{doc_content}

Respond in {lang} ONLY. Avoid using English or mixing languages.
Use everyday, conversational phrases that sound natural in {lang}.

Be brief (1–3 sentences), but full of love and help.
If the question is not relevant, kindly steer it back to STI or teenage pregnancy.

IMPORTANT: Do NOT write in English or mix in English words, even for emphasis.
"""

def translate_prompt_language(lang):
    return {
        "Yoruba": "yo",
        "Igbo": "ig",
        "Hausa": "ha",
        "Pidgin": None
    }.get(lang, "en")

def trim_to_words(text, max_words=300):
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

def generate_response(question, user_lang):
    if not any(keyword in question.lower() for keyword in allowed_keywords):
        return {
            "English": "Hmm bestie 🫶🏾 — I can only help with STI and teenage pregnancy matters. Ask me something like that!",
            "Yoruba": "Ore mi 🫶🏾 — Mo le ran e lowo lori koko STI ati oyun lasiko omode nikan.",
            "Igbo": "Nwanne 🫶🏾 — Ana m enyere maka STIs na ime nwa n'oge ntorobía.",
            "Hausa": "Kawaye 🫶🏾 — Tambayoyina na game da STI ko ciki a kuruciya ne kawai.",
            "Pidgin": "Padi mi 🫶🏾 — Na only STI or teenage belle I sabi talk about oh."
        }.get(user_lang)

    asyncio.set_event_loop(asyncio.new_event_loop())
    query_embed = embed_model.embed_query(question)
    query_embed = [float(v) for v in query_embed]

    results = pinecone_index.query(vector=query_embed, top_k=3, include_metadata=True)
    doc_contents = [m['metadata'].get('text', '') for m in results.get('matches', [])]
    doc = "\n".join(doc_contents).replace("{", "{{").replace("}", "}}") or "No extra gist found."

    prompt = system_prompt_template_base.format(doc_content=doc, lang=user_lang)
    history = ChatMessageHistory()
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            history.add_user_message(msg["content"])
        elif msg["role"] == "assistant":
            history.add_ai_message(msg["content"])
    memory = ConversationBufferMemory(memory_key="chat_history", chat_memory=history, return_messages=True)

    chat = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY)
    chain = LLMChain(
        llm=chat,
        prompt=ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{question}")
            ]
        ),
        memory=memory,
        verbose=False
    )

    res = chain.invoke({"question": question})
    full_text = res.get('text', '').strip()
    return trim_to_words(full_text)

def synthesize_tts(text, lang_code):
    if not lang_code or lang_code not in ["en", "yo", "ig", "ha"]:
        return None
    try:
        response = spitch_client.speech.generate(text=text, language=lang_code, voice="femi")
        return response.read()
    except:
        return None

# ───── Main App ─────
def main():
    st.markdown("<div style='margin-top:-160px'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size:1.75rem;'>Talk to MyPadi — Text & Voice</h2>", unsafe_allow_html=True)

    if "language" not in st.session_state:
        st.markdown("<h4>🌍 Choose your language to gist:</h4>", unsafe_allow_html=True)
        lang = st.radio("Select Language:", list(language_greetings.keys()), index=None)
        if st.button("✅ Let's Go!") and lang:
            st.session_state.language = lang
            st.rerun()
    else:
        lang = st.session_state.language
        st.success(f"🗣️ You're chatting in: **{lang}**")

        if st.button("🔄 Change Language"):
            del st.session_state["language"]
            st.rerun()

        st.markdown(f"#### {language_greetings.get(lang)}")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [{"role": "assistant", "content": language_greetings.get(lang)}]

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_input := st.chat_input("What’s on your mind?"):
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.spinner("Hold on bestie... thinking 🤔"):
                reply = generate_response(user_input, lang)

            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

            lang_code = translate_prompt_language(lang)
            if lang_code and SPITCH_API_KEY and lang != "Pidgin":
                audio_bytes = synthesize_tts(reply, lang_code)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")

if __name__ == "__main__":
    main()
