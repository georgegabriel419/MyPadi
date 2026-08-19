import os
import time
import streamlit as st
from dotenv import load_dotenv
from spitch import Spitch
from google import genai
from google.genai import types

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Chat with MyPadi",
    page_icon="💬"
)

apply_custom_styles()


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")


# ============================================================
# CHECK API KEYS
# ============================================================

if not PINECONE_API_KEY:
    st.error("❌ PINECONE_API_KEY is missing.")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY is missing.")


# ============================================================
# PINECONE
# ============================================================

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

pinecone_index = pc.Index(
    "sti-teenage-preg"
)


# Check Pinecone
try:

    index_info = pc.describe_index(
        "sti-teenage-preg"
    )

    print(
        "PINECONE INDEX INFO:",
        index_info
    )

except Exception as e:

    print(
        "PINECONE ERROR:",
        repr(e)
    )


# ============================================================
# GOOGLE GENAI CLIENT
# ============================================================

try:

    google_client = genai.Client(
        api_key=GOOGLE_API_KEY
    )

    print("GOOGLE CLIENT: CREATED SUCCESSFULLY")

except Exception as e:

    google_client = None

    print(
        "GOOGLE CLIENT ERROR:",
        repr(e)
    )


# ============================================================
# GOOGLE EMBEDDING TEST
# ============================================================
#
# This runs when Streamlit starts.
# It allows us to determine whether the Google
# embedding API itself is working.
#
# IMPORTANT:
# We don't show the API key.
# ============================================================

if google_client:

    try:

        test_result = google_client.models.embed_content(
            model="gemini-embedding-001",
            contents="test"
        )

        test_embedding = test_result.embeddings[0].values

        print(
            "GOOGLE EMBEDDING TEST: SUCCESS"
        )

        print(
            "TEST EMBEDDING DIMENSION:",
            len(test_embedding)
        )

    except Exception as e:

        print(
            "GOOGLE EMBEDDING TEST FAILED:",
            repr(e)
        )


# ============================================================
# SPITCH
# ============================================================

try:

    spitch_client = Spitch()

except Exception as e:

    spitch_client = None

    print(
        "SPITCH ERROR:",
        repr(e)
    )


# ============================================================
# GREETINGS
# ============================================================

language_greetings = {

    "English":
        "Hey bestie! 😊 I'm MyPadi. "
        "Let's gist about STIs, pregnancy or anything health-y.",

    "Yoruba":
        "Ore mi! 😊 Oruko mi ni MyPadi. "
        "E je ka ba ara wa soro nipa STI ati oyun.",

    "Igbo":
        "Nwanne m! 😊 Aha m bu MyPadi. "
        "Ka anyi kparita okwu banyere STIs na ime nwa.",

    "Hausa":
        "Sannu kawaye! 😊 Ni MyPadi ne. "
        "Mu tattauna STI ko ciki na matasa.",

    "Pidgin":
        "Hey my padi! 😊 Make we yarn well-well "
        "about STI or belle palava."
}


# ============================================================
# OFF-TOPIC RESPONSES
# ============================================================

off_topic_responses = {

    "English":
        "Hmm bestie 🫶🏾 — I can only help with STI "
        "and teenage pregnancy matters. "
        "Ask me something like that!",

    "Yoruba":
        "Ore mi 🫶🏾 — Mo le ran e lowo lori koko "
        "STI ati oyun lasiko omode nikan.",

    "Igbo":
        "Nwanne 🫶🏾 — Ana m enyere maka STIs "
        "na ime nwa n'oge ntorobia.",

    "Hausa":
        "Kawaye 🫶🏾 — Tambayoyina na game da STI "
        "ko ciki a kuruciya ne kawai.",

    "Pidgin":
        "Padi mi 🫶🏾 — Na only STI or teenage "
        "belle I sabi talk about oh."
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

system_prompt_template_base = """
You are MyPadi — the user's best friend and health gist buddy.

You give warm, non-judgmental and medically responsible
information about STIs and teenage pregnancy in {lang}.

Sound casual, friendly, caring and easy to understand.

Use the following information from the knowledge base
if it is helpful:

{doc_content}

Respond in {lang} ONLY.

Avoid using English or mixing languages when responding
in Yoruba, Igbo or Hausa.

Use everyday conversational language.

Keep answers brief and helpful.

If the question is not relevant to STI or teenage pregnancy,
kindly steer the conversation back to those topics.

Do not invent medical facts.

Do not make a diagnosis.

When appropriate, encourage the user to speak with
a qualified healthcare professional.
"""


# ============================================================
# LANGUAGE CODES
# ============================================================

def translate_prompt_language(lang):

    return {
        "Yoruba": "yo",
        "Igbo": "ig",
        "Hausa": "ha",
        "Pidgin": None
    }.get(
        lang,
        "en"
    )


# ============================================================
# TRIM RESPONSE
# ============================================================

def trim_to_words(
    text,
    max_words=300
):

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
# CREATE GOOGLE EMBEDDING
# ============================================================

def create_embedding(
    text,
    max_retries=3
):

    if not google_client:

        raise RuntimeError(
            "Google GenAI client was not created."
        )

    last_error = None

    for attempt in range(max_retries):

        try:

            print(
                f"Embedding attempt "
                f"{attempt + 1}/{max_retries}"
            )

            result = google_client.models.embed_content(

                model="gemini-embedding-001",

                contents=text,

                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )

            embedding = (
                result
                .embeddings[0]
                .values
            )

            embedding = [
                float(value)
                for value in embedding
            ]

            print(
                "Embedding dimension:",
                len(embedding)
            )

            # Pinecone index is 768 dimensions
            if len(embedding) != 768:

                raise ValueError(
                    "Embedding dimension mismatch. "
                    f"Expected 768 but got "
                    f"{len(embedding)}."
                )

            return embedding

        except Exception as e:

            last_error = e

            print(
                "EMBEDDING ATTEMPT FAILED:",
                repr(e)
            )

            if attempt < max_retries - 1:

                time.sleep(2)

    raise RuntimeError(
        "Google embedding failed after "
        f"{max_retries} attempts. "
        f"Original error: {repr(last_error)}"
    )


# ============================================================
# GENERATE RESPONSE
# ============================================================

def generate_response(
    question,
    user_lang
):

    # --------------------------------------------------------
    # CHECK KEYWORDS
    # --------------------------------------------------------

    if not any(
        keyword.lower() in question.lower()
        for keyword in allowed_keywords
    ):

        return off_topic_responses.get(
            user_lang,
            off_topic_responses["English"]
        )


    # --------------------------------------------------------
    # CREATE QUERY EMBEDDING
    # --------------------------------------------------------

    try:

        query_embed = create_embedding(
            question
        )

    except Exception as e:

        error_message = repr(e)

        print(
            "======================================"
        )

        print(
            "EMBEDDING ERROR:"
        )

        print(
            error_message
        )

        print(
            "======================================"
        )

        # Show error while debugging
        st.error(
            "Google embedding error: "
            + error_message
        )

        return {
            "English":
                "Sorry bestie 🫶🏾, I'm having "
                "a little connection problem right now. "
                "Please try again in a moment.",

            "Yoruba":
                "Ma binu ore mi 🫶🏾, isoro kekere wa "
                "pelu asopọ bayi. Jowo gbiyanju lẹẹkansi.",

            "Igbo":
                "Ndo nwanne 🫶🏾, enwere obere nsogbu "
                "njikọ ugbu a. Biko nwaa ọzọ.",

            "Hausa":
                "Yi hakuri kawaye 🫶🏾, akwai karamar "
                "matsalar haɗi yanzu. Da fatan za ka "
                "sake gwadawa.",

            "Pidgin":
                "Sorry my padi 🫶🏾, connection get "
                "small problem now. Abeg try again."
        }.get(
            user_lang,
            "Sorry, something went wrong."
        )


    # --------------------------------------------------------
    # PINECONE SEARCH
    # --------------------------------------------------------

    try:

        results = pinecone_index.query(

            vector=query_embed,

            top_k=3,

            include_metadata=True
        )

        matches = results.get(
            "matches",
            []
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

                doc_contents.append(
                    text
                )

        doc = "\n".join(
            doc_contents
        )

        if not doc:

            doc = (
                "No additional information "
                "was found."
            )

    except Exception as e:

        print(
            "PINECONE QUERY ERROR:",
            repr(e)
        )

        doc = (
            "No additional information "
            "was found."
        )


    # --------------------------------------------------------
    # ESCAPE CURLY BRACKETS
    # --------------------------------------------------------

    doc = (
        doc
        .replace("{", "{{")
        .replace("}", "}}")
    )


    # --------------------------------------------------------
    # BUILD SYSTEM PROMPT
    # --------------------------------------------------------

    prompt = (
        system_prompt_template_base
        .format(
            doc_content=doc,
            lang=user_lang
        )
    )


    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    history = ChatMessageHistory()

    for msg in st.session_state.get(
        "chat_history",
        []
    ):

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


    # --------------------------------------------------------
    # GEMINI CHAT MODEL
    # --------------------------------------------------------

    try:

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

        response = chain.invoke(
            {
                "question": question
            }
        )

        full_text = (
            response
            .get("text", "")
            .strip()
        )

        return trim_to_words(
            full_text
        )

    except Exception as e:

        print(
            "GEMINI CHAT ERROR:",
            repr(e)
        )

        st.error(
            "Gemini chat error: "
            + repr(e)
        )

        return {
            "English":
                "Sorry bestie 🫶🏾, I couldn't "
                "generate a response right now. "
                "Please try again.",

            "Yoruba":
                "Ma binu ore mi 🫶🏾, mi o le dahun "
                "bayii. Jowo gbiyanju lẹẹkansi.",

            "Igbo":
                "Ndo nwanne 🫶🏾, enweghị m ike ịza "
                "ugbu a. Biko nwaa ọzọ.",

            "Hausa":
                "Yi hakuri kawaye 🫶🏾, ba zan iya "
                "ba da amsa yanzu ba. Da fatan za "
                "ka sake gwadawa.",

            "Pidgin":
                "Sorry my padi 🫶🏾, I no fit generate "
                "response now. Abeg try again."
        }.get(
            user_lang,
            "Sorry, I couldn't generate a response."
        )


# ============================================================
# TEXT TO SPEECH
# ============================================================

def synthesize_tts(
    text,
    lang_code
):

    if not lang_code:

        return None

    if lang_code not in [
        "en",
        "yo",
        "ig",
        "ha"
    ]:

        return None

    if not spitch_client:

        return None

    try:

        response = (
            spitch_client
            .speech
            .generate(
                text=text,
                language=lang_code,
                voice="femi"
            )
        )

        return response.read()

    except Exception as e:

        print(
            "TTS ERROR:",
            repr(e)
        )

        return None


# ============================================================
# MAIN APP
# ============================================================

def main():

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

            st.rerun()


    # ========================================================
    # CHAT
    # ========================================================

    else:

        lang = st.session_state.language

        st.success(
            f"🗣️ You're chatting in: **{lang}**"
        )


        # ----------------------------------------------------
        # CHANGE LANGUAGE
        # ----------------------------------------------------

        if st.button(
            "🔄 Change Language"
        ):

            del st.session_state[
                "language"
            ]

            if "chat_history" in st.session_state:

                del st.session_state[
                    "chat_history"
                ]

            st.rerun()


        # ----------------------------------------------------
        # GREETING
        # ----------------------------------------------------

        st.markdown(
            f"#### {language_greetings.get(lang)}"
        )


        # ----------------------------------------------------
        # INITIALIZE CHAT
        # ----------------------------------------------------

        if "chat_history" not in st.session_state:

            st.session_state.chat_history = [

                {
                    "role": "assistant",

                    "content":
                        language_greetings.get(
                            lang
                        )
                }
            ]


        # ----------------------------------------------------
        # DISPLAY CHAT
        # ----------------------------------------------------

        for msg in st.session_state.chat_history:

            with st.chat_message(
                msg["role"]
            ):

                st.markdown(
                    msg["content"]
                )


        # ----------------------------------------------------
        # USER INPUT
        # ----------------------------------------------------

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


            # -----------------------------------------------
            # TEXT TO SPEECH
            # -----------------------------------------------

            lang_code = (
                translate_prompt_language(
                    lang
                )
            )


            if (
                lang_code
                and SPITCH_API_KEY
                and lang != "Pidgin"
            ):

                audio_bytes = (
                    synthesize_tts(
                        reply,
                        lang_code
                    )
                )

                if audio_bytes:

                    st.audio(
                        audio_bytes,
                        format="audio/wav"
                    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
