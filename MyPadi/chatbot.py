import os
import streamlit as st

from dotenv import load_dotenv

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

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


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Chat with MyPadi",
    page_icon="💬"
)

apply_custom_styles()


# ============================================================
# GET API KEYS
# ============================================================

def get_secret(name):
    """
    Get secret from Streamlit Secrets first.
    Fall back to .env for local development.
    """

    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(name)


PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")


# ============================================================
# CHECK REQUIRED API KEYS
# ============================================================

if not PINECONE_API_KEY:
    st.error("PINECONE_API_KEY is missing.")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing.")


# ============================================================
# INITIALIZE PINECONE
# ============================================================

pinecone_index = None

if PINECONE_API_KEY:

    try:

        pc = Pinecone(
            api_key=PINECONE_API_KEY
        )

        pinecone_index = pc.Index(
            "sti-teenage-preg"
        )

        # Diagnostic information
        index_info = pc.describe_index(
            "sti-teenage-preg"
        )

        print(
            "PINECONE INDEX INFO:",
            index_info
        )

    except Exception as e:

        print(
            "PINECONE INITIALIZATION ERROR:",
            repr(e)
        )

        pinecone_index = None


# ============================================================
# INITIALIZE GOOGLE EMBEDDINGS
# ============================================================

embed_model = None

if GOOGLE_API_KEY:

    try:

        embed_model = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GOOGLE_API_KEY,
            output_dimensionality=768
        )

        print(
            "GOOGLE EMBEDDING MODEL INITIALIZED"
        )

    except Exception as e:

        print(
            "GOOGLE EMBEDDING INITIALIZATION ERROR:",
            repr(e)
        )

        embed_model = None


# ============================================================
# GREETINGS
# ============================================================

language_greetings = {

    "English":
        "Hey bestie! 😊 I'm MyPadi. Let's gist about STIs, pregnancy or anything health-y.",

    "Yoruba":
        "Ore mi! 😊 Oruko mi ni MyPadi. E je ka ba ara wa soro nipa STI ati oyun.",

    "Igbo":
        "Nwanne m! 😊 Aha m bu MyPadi. Ka anyi kparita okwu banyere STIs na ime nwa.",

    "Hausa":
        "Sannu kawaye! 😊 Ni MyPadi ne. Mu tattauna STI ko ciki na matasa.",

    "Pidgin":
        "Hey my padi! 😊 Make we yarn well-well about STI or belle palava."
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

system_prompt_template_base = """

You are MyPadi — the user's best friend and health gist buddy.

You give warm, non-judgmental and youth-friendly information
about STIs and teenage pregnancy in {lang}.

Sound casual, caring, friendly and easy to understand.

Use the following trusted information if helpful:

{doc_content}

Respond in {lang} ONLY.

Avoid unnecessary English or mixing languages.

Use everyday conversational language that sounds natural
in the selected language.

Keep the response brief, approximately 1–3 sentences,
unless more explanation is genuinely necessary.

If the question is unrelated to STIs or teenage pregnancy,
kindly steer the conversation back to those topics.

Do not invent medical facts.

"""


# ============================================================
# LANGUAGE SETTINGS
# ============================================================

def translate_prompt_language(lang):

    return {
        "Yoruba": "yo",
        "Igbo": "ig",
        "Hausa": "ha",
        "Pidgin": None
    }.get(lang, "en")


# ============================================================
# TRIM RESPONSE
# ============================================================

def trim_to_words(text, max_words=300):

    if not text:
        return ""

    words = text.split()

    if len(words) > max_words:

        return (
            " ".join(words[:max_words])
            + "..."
        )

    return " ".join(words)


# ============================================================
# FALLBACK RESPONSES
# ============================================================

def fallback_response(lang):

    responses = {

        "English":
            "Sorry bestie 🫶🏾, I'm having a little connection problem right now. Please try again in a moment.",

        "Yoruba":
            "Ma binu ore mi 🫶🏾, isoro kekere wa pelu asopo. Jowo gbiyanju lẹẹkansi ni igba diẹ.",

        "Igbo":
            "Ndo nwanne 🫶🏾, enwere obere nsogbu njikọ ugbu a. Biko nwaa ọzọ obere oge.",

        "Hausa":
            "Yi hakuri kawaye 🫶🏾, akwai karamar matsalar sadarwa yanzu. Ka sake gwadawa nan gaba kadan.",

        "Pidgin":
            "Sorry padi 🫶🏾, connection dey misbehave small. Abeg try again in a moment."
    }

    return responses.get(
        lang,
        responses["English"]
    )


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(question, user_lang):

    question_lower = question.lower()


    # ========================================================
    # CHECK ALLOWED TOPICS
    # ========================================================

    if not any(
        keyword.lower() in question_lower
        for keyword in allowed_keywords
    ):

        responses = {

            "English":
                "Hmm bestie 🫶🏾 — I can only help with STI and teenage pregnancy matters. Ask me something related to that!",

            "Yoruba":
                "Ore mi 🫶🏾 — Mo le ran e lowo lori koko STI ati oyun lasiko omode nikan.",

            "Igbo":
                "Nwanne 🫶🏾 — Ana m enyere maka STIs na ime nwa n'oge ntorobia.",

            "Hausa":
                "Kawaye 🫶🏾 — Tambayoyina na game da STI ko ciki a kuruciya ne kawai.",

            "Pidgin":
                "Padi mi 🫶🏾 — Na only STI or teenage belle I sabi talk about oh."
        }

        return responses.get(
            user_lang,
            responses["English"]
        )


    # ========================================================
    # DEFAULT DOCUMENT CONTEXT
    # ========================================================

    doc = "No additional information was retrieved."


    # ========================================================
    # PINECONE + GOOGLE EMBEDDING
    # ========================================================

    if embed_model is not None and pinecone_index is not None:

        try:

            print(
                "Starting embedding..."
            )

            query_embed = embed_model.embed_query(
                question
            )

            query_embed = [
                float(v)
                for v in query_embed
            ]

            print(
                "Embedding successful."
            )

            print(
                "Embedding dimension:",
                len(query_embed)
            )


            # =================================================
            # PINECONE SEARCH
            # =================================================

            results = pinecone_index.query(
                vector=query_embed,
                top_k=3,
                include_metadata=True
            )

            matches = results.get(
                "matches",
                []
            )

            print(
                "Pinecone matches:",
                len(matches)
            )


            doc_contents = []

            for match in matches:

                metadata = match.get(
                    "metadata",
                    {}
                )

                text = metadata.get(
                    "text",
                    ""
                )

                if text:
                    doc_contents.append(text)


            if doc_contents:

                doc = "\n\n".join(
                    doc_contents
                )

                print(
                    "Pinecone context retrieved successfully."
                )

            else:

                print(
                    "Pinecone returned no usable text."
                )


        except Exception as e:

            # IMPORTANT:
            # Do not crash the chatbot if embeddings fail.

            print(
                "EMBEDDING/PINECONE ERROR:",
                repr(e)
            )

            print(
                "Continuing without Pinecone context."
            )


    else:

        print(
            "Embedding model or Pinecone index unavailable."
        )

        print(
            "Continuing without Pinecone context."
        )


    # ========================================================
    # PREPARE PROMPT
    # ========================================================

    # Escape braces inside retrieved documents
    # so they don't interfere with .format()

    doc = (
        doc
        .replace("{", "{{")
        .replace("}", "}}")
    )


    prompt = system_prompt_template_base.format(
        doc_content=doc,
        lang=user_lang
    )


    # ========================================================
    # CHAT HISTORY
    # ========================================================

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


    # ========================================================
    # GEMINI
    # ========================================================

    if not GOOGLE_API_KEY:

        print(
            "GOOGLE_API_KEY is missing."
        )

        return fallback_response(
            user_lang
        )


    try:

        print(
            "Starting Gemini..."
        )

        chat = ChatGoogleGenerativeAI(

            model="gemini-2.0-flash",

            temperature=0.3,

            google_api_key=GOOGLE_API_KEY

        )


        chain = LLMChain(

            llm=chat,

            prompt=ChatPromptTemplate(

                messages=[

                    SystemMessagePromptTemplate
                    .from_template(
                        prompt
                    ),

                    MessagesPlaceholder(
                        variable_name="chat_history"
                    ),

                    HumanMessagePromptTemplate
                    .from_template(
                        "{question}"
                    )

                ]
            ),

            memory=memory,

            verbose=False
        )


        result = chain.invoke(
            {
                "question": question
            }
        )


        full_text = result.get(
            "text",
            ""
        ).strip()


        if not full_text:

            print(
                "Gemini returned an empty response."
            )

            return fallback_response(
                user_lang
            )


        print(
            "Gemini response generated successfully."
        )


        return trim_to_words(
            full_text
        )


    except Exception as e:

        print(
            "GEMINI ERROR:",
            repr(e)
        )

        return fallback_response(
            user_lang
        )


# ============================================================
# MAIN APP
# ============================================================

def main():

    st.markdown(
        "<div style='margin-top:-160px'></div>",
        unsafe_allow_html=True
    )


    st.markdown(
        """
        <h2 style='font-size:1.75rem;'>
        Talk to MyPadi — Text
        </h2>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LANGUAGE SELECTION
    # ========================================================

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


        if st.button(
            "✅ Let's Go!"
        ) and lang:

            st.session_state.language = lang

            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": language_greetings[lang]
                }
            ]

            st.rerun()


    # ========================================================
    # CHAT INTERFACE
    # ========================================================

    else:

        lang = st.session_state.language


        st.success(
            f"🗣️ You're chatting in: **{lang}**"
        )


        if st.button(
            "🔄 Change Language"
        ):

            del st.session_state["language"]

            if "chat_history" in st.session_state:
                del st.session_state["chat_history"]

            st.rerun()


        # ====================================================
        # GREETING
        # ====================================================

        st.markdown(
            f"#### {language_greetings.get(lang)}"
        )


        # ====================================================
        # INITIALIZE CHAT HISTORY
        # ====================================================

        if "chat_history" not in st.session_state:

            st.session_state.chat_history = [

                {
                    "role": "assistant",
                    "content": language_greetings.get(
                        lang
                    )
                }

            ]


        # ====================================================
        # DISPLAY CHAT HISTORY
        # ====================================================

        for msg in st.session_state.chat_history:

            with st.chat_message(
                msg["role"]
            ):

                st.markdown(
                    msg["content"]
                )


        # ====================================================
        # USER INPUT
        # ====================================================

        user_input = st.chat_input(
            "What's on your mind?"
        )


        if user_input:

            # -----------------------------------------------
            # USER MESSAGE
            # -----------------------------------------------

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    user_input
                )


            st.session_state.chat_history.append(

                {
                    "role": "user",
                    "content": user_input
                }

            )


            # -----------------------------------------------
            # GENERATE RESPONSE
            # -----------------------------------------------

            with st.spinner(
                "Hold on bestie... thinking 🤔"
            ):

                reply = generate_response(
                    user_input,
                    lang
                )


            # -----------------------------------------------
            # ASSISTANT RESPONSE
            # -----------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    reply
                )


            st.session_state.chat_history.append(

                {
                    "role": "assistant",
                    "content": reply
                }

            )


# ============================================================
# RUN APP
# ============================================================

if __name__ == "__main__":

    main()
