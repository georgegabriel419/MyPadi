import os
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types

from langchain_google_genai import ChatGoogleGenerativeAI
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
# GET SECRETS
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
# API KEY CHECK
# ============================================================

if not PINECONE_API_KEY:
    st.error("PINECONE_API_KEY is missing.")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is missing.")


# ============================================================
# INITIALIZE GOOGLE GENAI CLIENT
# ============================================================

google_client = None

if GOOGLE_API_KEY:

    try:

        google_client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        print("GOOGLE GENAI CLIENT INITIALIZED")

    except Exception as e:

        print(
            "GOOGLE GENAI INITIALIZATION ERROR:",
            repr(e)
        )

        google_client = None


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

SYSTEM_PROMPT = """
You are MyPadi — a friendly, caring and youth-friendly health
information assistant.

You provide accurate, simple and non-judgmental information
about sexually transmitted infections (STIs) and teenage
pregnancy.

The user selected the language: {lang}

IMPORTANT LANGUAGE RULE:
Respond in {lang}.

Do not unnecessarily mix languages.

Use simple, natural, conversational language.

Keep responses concise, usually 1–3 short paragraphs.

Do not invent medical information.

Use the trusted information retrieved from the knowledge base
when it is relevant.

TRUSTED INFORMATION:
{doc_content}

If the user's question is unrelated to STIs or teenage
pregnancy, politely redirect them toward those topics.

If the retrieved information does not contain the answer,
use your general medical knowledge carefully and avoid
making unsupported claims.
"""


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
# OFF-TOPIC RESPONSES
# ============================================================

def off_topic_response(lang):

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
        lang,
        responses["English"]
    )


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
# GOOGLE EMBEDDING
# ============================================================

def create_embedding(text):

    if google_client is None:

        raise RuntimeError(
            "Google GenAI client is not initialized."
        )

    print("Starting Google embedding...")

    result = google_client.models.embed_content(

        model="gemini-embedding-001",

        contents=text,

        config=types.EmbedContentConfig(

            task_type="RETRIEVAL_QUERY",

            output_dimensionality=768

        )
    )

    if not result.embeddings:

        raise RuntimeError(
            "Google returned no embedding."
        )

    embedding = result.embeddings[0].values

    if not embedding:

        raise RuntimeError(
            "Google returned an empty embedding."
        )

    embedding = [
        float(value)
        for value in embedding
    ]

    print(
        "Embedding successful."
    )

    print(
        "Embedding dimension:",
        len(embedding)
    )

    return embedding


# ============================================================
# SEARCH PINECONE
# ============================================================

def search_knowledge_base(question):

    if pinecone_index is None:

        print(
            "Pinecone unavailable."
        )

        return "No additional trusted information was retrieved."


    try:

        # -----------------------------------------------
        # CREATE QUERY EMBEDDING
        # -----------------------------------------------

        query_embedding = create_embedding(
            question
        )


        # -----------------------------------------------
        # QUERY PINECONE
        # -----------------------------------------------

        results = pinecone_index.query(

            vector=query_embedding,

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


        documents = []


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

                documents.append(
                    text
                )


        if documents:

            print(
                "Pinecone context retrieved successfully."
            )

            return "\n\n".join(
                documents
            )


        print(
            "Pinecone returned no usable text."
        )

        return "No additional trusted information was retrieved."


    except Exception as e:

        print(
            "PINECONE SEARCH ERROR:",
            repr(e)
        )

        return "No additional trusted information was retrieved."


# ============================================================
# GEMINI RESPONSE
# ============================================================

def generate_gemini_response(
    question,
    user_lang,
    doc_content
):

    if google_client is None:

        return fallback_response(
            user_lang
        )


    try:

        # ====================================================
        # BUILD SYSTEM INSTRUCTION
        # ====================================================

        system_instruction = SYSTEM_PROMPT.format(

            lang=user_lang,

            doc_content=doc_content
        )


        # ====================================================
        # BUILD CONVERSATION HISTORY
        # ====================================================

        history = []


        for msg in st.session_state.get(
            "chat_history",
            []
        ):

            role = msg.get(
                "role"
            )

            content = msg.get(
                "content",
                ""
            )


            # Don't include the greeting as
            # unnecessary model context.

            if not content:
                continue


            if role == "user":

                history.append(
                    f"User: {content}"
                )


            elif role == "assistant":

                history.append(
                    f"MyPadi: {content}"
                )


        previous_conversation = "\n".join(
            history[-10:]
        )


        # ====================================================
        # FINAL PROMPT
        # ====================================================

        final_prompt = f"""
{system_instruction}

PREVIOUS CONVERSATION:
{previous_conversation}

CURRENT USER QUESTION:
{question}

Now answer the user's current question.
"""


        print(
            "Starting Gemini response generation..."
        )


        # ====================================================
        # GEMINI
        # ====================================================

        chat = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=GOOGLE_API_KEY
        )


        response = chat.invoke(
            final_prompt
        )


        # ====================================================
        # EXTRACT TEXT
        # ====================================================

        full_text = ""


        if hasattr(
            response,
            "content"
        ):

            full_text = response.content


        elif isinstance(
            response,
            str
        ):

            full_text = response


        if isinstance(
            full_text,
            list
        ):

            parts = []

            for item in full_text:

                if isinstance(
                    item,
                    dict
                ):

                    if "text" in item:

                        parts.append(
                            item["text"]
                        )

                elif isinstance(
                    item,
                    str
                ):

                    parts.append(
                        item
                    )

            full_text = " ".join(
                parts
            )


        full_text = str(
            full_text
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
# GENERATE COMPLETE RESPONSE
# ============================================================

def generate_response(
    question,
    user_lang
):

    question_lower = question.lower()


    # ========================================================
    # TOPIC FILTER
    # ========================================================

    if not any(

        keyword.lower() in question_lower

        for keyword in allowed_keywords

    ):

        return off_topic_response(
            user_lang
        )


    # ========================================================
    # RETRIEVE KNOWLEDGE
    # ========================================================

    doc_content = search_knowledge_base(
        question
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    return generate_gemini_response(

        question=question,

        user_lang=user_lang,

        doc_content=doc_content
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

            list(
                language_greetings.keys()
            ),

            index=None
        )


        if st.button(
            "✅ Let's Go!"
        ) and lang:

            st.session_state.language = lang


            st.session_state.chat_history = [

                {
                    "role":
                    "assistant",

                    "content":
                    language_greetings[lang]
                }

            ]


            st.rerun()


        return


    # ========================================================
    # CHAT SCREEN
    # ========================================================

    lang = st.session_state.language


    st.success(
        f"🗣️ You're chatting in: **{lang}**"
    )


    # ========================================================
    # CHANGE LANGUAGE
    # ========================================================

    if st.button(
        "🔄 Change Language"
    ):

        if "language" in st.session_state:

            del st.session_state[
                "language"
            ]


        if "chat_history" in st.session_state:

            del st.session_state[
                "chat_history"
            ]


        st.rerun()


    # ========================================================
    # GREETING
    # ========================================================

    st.markdown(
        f"#### {language_greetings.get(lang)}"
    )


    # ========================================================
    # INITIALIZE HISTORY
    # ========================================================

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = [

            {
                "role":
                "assistant",

                "content":
                language_greetings.get(lang)
            }

        ]


    # ========================================================
    # DISPLAY HISTORY
    # ========================================================

    for msg in st.session_state.chat_history:

        with st.chat_message(
            msg["role"]
        ):

            st.markdown(
                msg["content"]
            )


    # ========================================================
    # USER INPUT
    # ========================================================

    user_input = st.chat_input(
        "What's on your mind?"
    )


    if user_input:

        # ----------------------------------------------------
        # DISPLAY USER MESSAGE
        # ----------------------------------------------------

        with st.chat_message(
            "user"
        ):

            st.markdown(
                user_input
            )


        st.session_state.chat_history.append(

            {
                "role":
                "user",

                "content":
                user_input
            }

        )


        # ----------------------------------------------------
        # GENERATE RESPONSE
        # ----------------------------------------------------

        with st.spinner(
            "Hold on bestie... thinking 🤔"
        ):

            reply = generate_response(

                question=user_input,

                user_lang=lang
            )


        # ----------------------------------------------------
        # DISPLAY RESPONSE
        # ----------------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                reply
            )


        st.session_state.chat_history.append(

            {
                "role":
                "assistant",

                "content":
                reply
            }

        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
