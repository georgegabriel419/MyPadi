import os
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from spitch import Spitch
import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.chains import LLMChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory

from pinecone import Pinecone
from keywords import allowed_keywords
from style import apply_custom_styles


# ───── Apply Custom Theme ─────
apply_custom_styles()
st.set_page_config(
    page_title="Chat with MyPadi",
    page_icon="💬"
)


# ───── Init ─────
nest_asyncio.apply()
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")


# ───── Validate API Keys ─────
if not PINECONE_API_KEY:
    st.error("PINECONE_API_KEY is missing from Streamlit Secrets.")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing from Streamlit Secrets.")


# ───── Configure Google Generative AI ─────
genai.configure(api_key=GOOGLE_API_KEY)


# ───── Initialize Pinecone ─────
pc = Pinecone(api_key=PINECONE_API_KEY)

pinecone_index = pc.Index("sti-teenage-preg")

# Print index information to Streamlit Cloud logs
try:
    index_info = pc.describe_index("sti-teenage-preg")
    print("PINECONE INDEX INFO:", index_info)
except Exception as e:
    print("Could not retrieve Pinecone index information:", e)


# ───── Initialize Spitch ─────
spitch_client = Spitch()


# ───── Greetings ─────
language_greetings = {
    "English": (
        "Hey bestie! 😊 I'm MyPadi. "
        "Let's gist about STIs, pregnancy or anything health-y."
    ),

    "Yoruba": (
        "Ore mi! 😊 Oruko mi ni MyPadi. "
        "E je ka ba ara wa soro nipa STI ati oyun."
    ),

    "Igbo": (
        "Nwanne m! 😊 Aha m bu MyPadi. "
        "Ka anyi kparita okwu banyere STIs na ime nwa."
    ),

    "Hausa": (
        "Sannu kawaye! 😊 Ni MyPadi ne. "
        "Mu tattauna STI ko ciki na matasa."
    ),

    "Pidgin": (
        "Hey my padi! 😊 Make we yarn well-well "
        "about STI or belle palava."
    )
}


# ───── System Prompt ─────
system_prompt_template_base = """
You are MyPadi — the user's best friend and health gist buddy.

You give warm, non-judgy advice about STIs and teenage pregnancy in {lang}.
Sound casual, fun, and caring. Like you're chatting with your close friend.

Use this information if helpful:

{doc_content}

Respond in {lang} ONLY.
Avoid using English or mixing languages.

Use everyday, conversational phrases that sound natural in {lang}.

Be brief (1–3 sentences), but full of love and help.

If the question is not relevant, kindly steer it back to STI or teenage pregnancy.

IMPORTANT:
Do NOT write in English or mix in English words, even for emphasis.
"""


# ───── Language for TTS ─────
def translate_prompt_language(lang):
    return {
        "Yoruba": "yo",
        "Igbo": "ig",
        "Hausa": "ha",
        "Pidgin": None
    }.get(lang, "en")


# ───── Limit Response Length ─────
def trim_to_words(text, max_words=300):
    words = text.split()

    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."

    return " ".join(words)


# ───── Generate Embedding ─────
def generate_embedding(text):
    """
    Generate a 768-dimensional embedding using
    Google's Gemini embedding model.

    The Pinecone index was created with dimension=768,
    so we explicitly request 768 dimensions.
    """

    try:
        embedding_response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query",
            output_dimensionality=768
        )

        embedding = embedding_response["embedding"]

        # Make sure Pinecone receives normal floats
        embedding = [float(value) for value in embedding]

        print("Embedding generated successfully.")
        print("Embedding dimension:", len(embedding))

        return embedding

    except Exception as e:
        print("EMBEDDING ERROR:", repr(e))
        raise


# ───── Generate Chatbot Response ─────
def generate_response(question, user_lang):

    # ───── Keyword Filter ─────
    if not any(
        keyword in question.lower()
        for keyword in allowed_keywords
    ):
        return {
            "English": (
                "Hmm bestie 🫶🏾 — I can only help with STI and "
                "teenage pregnancy matters. Ask me something like that!"
            ),

            "Yoruba": (
                "Ore mi 🫶🏾 — Mo le ran e lowo lori koko STI "
                "ati oyun lasiko omode nikan."
            ),

            "Igbo": (
                "Nwanne 🫶🏾 — Ana m enyere maka STIs na ime nwa "
                "n'oge ntorobia."
            ),

            "Hausa": (
                "Kawaye 🫶🏾 — Tambayoyina na game da STI ko ciki "
                "a kuruciya ne kawai."
            ),

            "Pidgin": (
                "Padi mi 🫶🏾 — Na only STI or teenage belle "
                "I sabi talk about oh."
            )
        }.get(user_lang)


    # ───── Generate Query Embedding ─────
    query_embed = generate_embedding(question)


    # ───── Safety Check for Pinecone Dimension ─────
    if len(query_embed) != 768:
        raise ValueError(
            f"Embedding dimension is {len(query_embed)}, "
            f"but Pinecone requires 768 dimensions."
        )


    # ───── Search Pinecone ─────
    results = pinecone_index.query(
        vector=query_embed,
        top_k=3,
        include_metadata=True
    )


    # ───── Extract Retrieved Documents ─────
    doc_contents = []

    for match in results.get("matches", []):

        metadata = match.get("metadata", {})

        text = metadata.get("text", "")

        if text:
            doc_contents.append(text)


    # Combine retrieved information
    doc = "\n".join(doc_contents)

    # Escape curly brackets so they don't interfere
    # with the LangChain prompt formatting
    doc = doc.replace("{", "{{").replace("}", "}}")


    if not doc:
        doc = "No extra gist found."


    # ───── Build Prompt ─────
    prompt = system_prompt_template_base.format(
        doc_content=doc,
        lang=user_lang
    )


    # ───── Build Conversation History ─────
    history = ChatMessageHistory()

    for msg in st.session_state.chat_history:

        if msg["role"] == "user":

            history.add_user_message(
                msg["content"]
            )

        elif msg["role"] == "assistant":

            history.add_ai_message(
                msg["content"]
            )


    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=history,
        return_messages=True
    )


    # ───── Gemini Chat Model ─────
    chat = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )


    # ───── LangChain Chain ─────
    chain = LLMChain(
        llm=chat,

        prompt=ChatPromptTemplate(
            messages=[

                SystemMessagePromptTemplate.from_template(
                    prompt
                ),

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),

                HumanMessagePromptTemplate.from_template(
                    "{question}"
                )
            ]
        ),

        memory=memory,
        verbose=False
    )


    # ───── Generate Final Answer ─────
    res = chain.invoke(
        {
            "question": question
        }
    )


    full_text = res.get(
        "text",
        ""
    ).strip()


    return trim_to_words(full_text)


# ───── Text-to-Speech ─────
def synthesize_tts(text, lang_code):

    if not lang_code:
        return None

    if lang_code not in ["en", "yo", "ig", "ha"]:
        return None

    try:

        response = spitch_client.speech.generate(
            text=text,
            language=lang_code,
            voice="femi"
        )

        return response.read()

    except Exception as e:

        print("TTS ERROR:", repr(e))

        return None


# ───── Main App ─────
def main():

    # ───── Page Header ─────
    st.markdown(
        "<div style='margin-top:-160px'></div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<h2 style='font-size:1.75rem;'>"
        "Talk to MyPadi — Text & Voice"
        "</h2>",
        unsafe_allow_html=True
    )


    # ───── Language Selection ─────
    if "language" not in st.session_state:

        st.markdown(
            "<h4>🌍 Choose your language to gist:</h4>",
            unsafe_allow_html=True
        )

        lang = st.radio(
            "Select Language:",
            list(language_greetings.keys()),
            index=None
        )


        if st.button("✅ Let's Go!") and lang:

            st.session_state.language = lang

            st.rerun()


    # ───── Chat Interface ─────
    else:

        lang = st.session_state.language


        st.success(
            f"🗣️ You're chatting in: **{lang}**"
        )


        # ───── Change Language ─────
        if st.button("🔄 Change Language"):

            del st.session_state["language"]

            st.rerun()


        # ───── Greeting ─────
        st.markdown(
            f"#### {language_greetings.get(lang)}"
        )


        # ───── Initialize Chat History ─────
        if "chat_history" not in st.session_state:

            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": language_greetings.get(lang)
                }
            ]


        # ───── Display Previous Messages ─────
        for msg in st.session_state.chat_history:

            with st.chat_message(msg["role"]):

                st.markdown(
                    msg["content"]
                )


        # ───── Chat Input ─────
        if user_input := st.chat_input(
            "What’s on your mind?"
        ):

            # Display user message
            with st.chat_message("user"):

                st.markdown(user_input)


            # Save user message
            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )


            # ───── Generate Response ─────
            with st.spinner(
                "Hold on bestie... thinking 🤔"
            ):

                try:

                    reply = generate_response(
                        user_input,
                        lang
                    )

                except Exception as e:

                    print(
                        "CHATBOT ERROR:",
                        repr(e)
                    )

                    reply = (
                        "Sorry bestie 🫶🏾, "
                        "I'm having a little technical issue "
                        "right now. Please try again in a moment."
                    )


            # ───── Display Assistant Response ─────
            with st.chat_message("assistant"):

                st.markdown(reply)


            # ───── Save Assistant Response ─────
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )


            # ───── Text-to-Speech ─────
            lang_code = translate_prompt_language(lang)


            if (
                lang_code
                and SPITCH_API_KEY
                and lang != "Pidgin"
            ):

                audio_bytes = synthesize_tts(
                    reply,
                    lang_code
                )

                if audio_bytes:

                    st.audio(
                        audio_bytes,
                        format="audio/wav"
                    )


# ───── Run App ─────
if __name__ == "__main__":
    main()
