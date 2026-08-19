import os
import streamlit as st

from dotenv import load_dotenv
from google import genai
from google.genai import types
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
    Streamlit Cloud:
        Gets value from st.secrets

    Local development:
        Falls back to .env
    """

    try:
        value = st.secrets.get(name)

        if value:
            return value

    except Exception:
        pass

    return os.getenv(name)


GOOGLE_API_KEY = get_secret("GOOGLE_API_KEY")
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")


# ============================================================
# MODEL SETTINGS
# ============================================================

# Gemini generation model
GENERATION_MODEL = "gemini-3.6-flash"

# Gemini embedding model
EMBEDDING_MODEL = "gemini-embedding-001"

# MUST match your Pinecone index dimension
EMBEDDING_DIMENSION = 768

# Pinecone index
PINECONE_INDEX_NAME = "sti-teenage-preg"


# ============================================================
# INITIALIZE GOOGLE CLIENT
# ============================================================

google_client = None

if GOOGLE_API_KEY:

    try:

        google_client = genai.Client(
            api_key=GOOGLE_API_KEY
        )

        print(
            "GOOGLE GENAI CLIENT INITIALIZED"
        )

    except Exception as e:

        print(
            "GOOGLE CLIENT INITIALIZATION ERROR:",
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
            PINECONE_INDEX_NAME
        )

        print(
            "PINECONE INDEX INITIALIZED:",
            PINECONE_INDEX_NAME
        )

        # Diagnostic information
        try:

            index_info = pc.describe_index(
                PINECONE_INDEX_NAME
            )

            print(
                "PINECONE INDEX INFO:",
                index_info
            )

        except Exception as e:

            print(
                "PINECONE DESCRIBE ERROR:",
                repr(e)
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
You are MyPadi — a warm, friendly and non-judgmental sexual and
reproductive health information chatbot for young people.

Your main topics include:

- HIV
- STIs
- STI prevention
- STI testing
- STI symptoms
- STI treatment information
- Teenage pregnancy
- Pregnancy prevention
- Reproductive health
- Sexual health education

IMPORTANT RAG RULE:

The information retrieved from the trusted documents below is the
primary source of truth for your answer.

Use the retrieved context to answer the user's question.

Do NOT invent information that is not supported by the retrieved
context when the question requires information from the documents.

If the retrieved documents do not contain enough information to
answer the question confidently, say that you do not have enough
information in the available resources rather than making something
up.

You can provide a short general explanation when appropriate, but
do not contradict the trusted retrieved information.

Be:

- Warm
- Friendly
- Youth-friendly
- Non-judgmental
- Clear
- Easy to understand

Do not shame the user.

Do not claim to be a doctor.

Do not diagnose the user.

If a user describes symptoms, provide general educational information
and encourage appropriate professional healthcare support.

The selected language is:

{lang}

Respond in {lang}.

For English:
Use natural, simple English.

For Pidgin:
Use natural Nigerian Pidgin.

For Yoruba, Igbo and Hausa:
Use natural conversational language.

Keep the response concise, normally around 1–3 short paragraphs,
unless the question requires more explanation.

TRUSTED RETRIEVED INFORMATION:

{context}
"""


# ============================================================
# FALLBACK RESPONSE
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
# OFF-TOPIC RESPONSE
# ============================================================

def off_topic_response(lang):

    responses = {

        "English":
            "Hmm bestie 🫶🏾 — I mainly help with STI, HIV, pregnancy and reproductive health questions. Ask me something about those!",

        "Yoruba":
            "Ore mi 🫶🏾 — Mo maa n ran eniyan lowo lori STI, HIV, oyun ati ilera ibisi.",

        "Igbo":
            "Nwanne 🫶🏾 — Ana m enyere aka karịsịa na STI, HIV, ime nwa na ahụike ọmụmụ.",

        "Hausa":
            "Kawaye 🫶🏾 — Ina taimakawa musamman game da STI, HIV, ciki da lafiyar haihuwa.",

        "Pidgin":
            "Padi mi 🫶🏾 — Na STI, HIV, belle matter and reproductive health I dey focus on."
    }

    return responses.get(
        lang,
        responses["English"]
    )


# ============================================================
# CHECK ALLOWED TOPICS
# ============================================================

def is_allowed_topic(question):

    question_lower = question.lower()

    return any(
        keyword.lower() in question_lower
        for keyword in allowed_keywords
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
# CREATE QUERY EMBEDDING
# ============================================================

def create_query_embedding(question):

    if google_client is None:

        raise RuntimeError(
            "Google GenAI client is not initialized."
        )


    print(
        "Creating query embedding..."
    )

    print(
        "Embedding model:",
        EMBEDDING_MODEL
    )


    response = google_client.models.embed_content(

        model=EMBEDDING_MODEL,

        contents=question,

        config=types.EmbedContentConfig(

            task_type="RETRIEVAL_QUERY",

            output_dimensionality=EMBEDDING_DIMENSION
        )
    )


    # --------------------------------------------------------
    # Extract embedding
    # --------------------------------------------------------

    if not response.embeddings:

        raise RuntimeError(
            "Google returned no embedding."
        )


    embedding = response.embeddings[0].values


    if not embedding:

        raise RuntimeError(
            "Google returned an empty embedding."
        )


    embedding = [
        float(value)
        for value in embedding
    ]


    # --------------------------------------------------------
    # Verify dimension
    # --------------------------------------------------------

    print(
        "Query embedding dimension:",
        len(embedding)
    )


    if len(embedding) != EMBEDDING_DIMENSION:

        raise RuntimeError(
            f"Embedding dimension mismatch. "
            f"Expected {EMBEDDING_DIMENSION}, "
            f"received {len(embedding)}."
        )


    print(
        "QUERY EMBEDDING SUCCESSFUL"
    )


    return embedding


# ============================================================
# SEARCH PINECONE
# ============================================================

def retrieve_context(question):

    if pinecone_index is None:

        raise RuntimeError(
            "Pinecone index is not initialized."
        )


    # --------------------------------------------------------
    # Create query vector
    # --------------------------------------------------------

    query_vector = create_query_embedding(
        question
    )


    # --------------------------------------------------------
    # Semantic search
    # --------------------------------------------------------

    print(
        "Searching Pinecone..."
    )


    results = pinecone_index.query(

        vector=query_vector,

        top_k=3,

        include_metadata=True
    )


    matches = results.get(
        "matches",
        []
    )


    print(
        "PINECONE MATCHES:",
        len(matches)
    )


    # --------------------------------------------------------
    # Extract document text
    # --------------------------------------------------------

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

            score = match.get(
                "score",
                0
            )


            documents.append(
                {
                    "text": text,
                    "score": score
                }
            )


    if not documents:

        print(
            "NO DOCUMENT TEXT FOUND IN PINECONE"
        )

        return ""


    # --------------------------------------------------------
    # Build context
    # --------------------------------------------------------

    context_parts = []


    for i, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(

            f"""
SOURCE {i}

Relevance score:
{document["score"]}

Content:
{document["text"]}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    print(
        "PINECONE CONTEXT RETRIEVED SUCCESSFULLY"
    )


    return context


# ============================================================
# BUILD CHAT HISTORY
# ============================================================

def build_chat_history():

    history = []

    chat_history = st.session_state.get(
        "chat_history",
        []
    )


    for message in chat_history:

        role = message.get(
            "role"
        )

        content = message.get(
            "content",
            ""
        )


        if not content:
            continue


        # Skip the initial MyPadi greeting
        # because it isn't useful RAG context.

        if (
            role == "assistant"
            and content in language_greetings.values()
        ):

            continue


        if role == "user":

            history.append(
                f"User: {content}"
            )


        elif role == "assistant":

            history.append(
                f"MyPadi: {content}"
            )


    # Keep recent history only.
    # This prevents unnecessarily huge prompts.

    history = history[-8:]


    return "\n".join(
        history
    )


# ============================================================
# GENERATE GEMINI RESPONSE
# ============================================================

def generate_with_gemini(
    question,
    user_lang,
    context
):

    if google_client is None:

        raise RuntimeError(
            "Google GenAI client is not initialized."
        )


    # --------------------------------------------------------
    # Conversation history
    # --------------------------------------------------------

    history = build_chat_history()


    # --------------------------------------------------------
    # System instruction
    # --------------------------------------------------------

    system_instruction = SYSTEM_PROMPT.format(

        lang=user_lang,

        context=(
            context
            if context
            else
            "No relevant information was retrieved "
            "from the trusted knowledge base."
        )
    )


    # --------------------------------------------------------
    # Build user prompt
    # --------------------------------------------------------

    user_prompt = f"""
Conversation history:

{history}

Current user question:

{question}

Answer the current question using the trusted retrieved
information provided in your system instructions.

Do not mention Pinecone, embeddings, retrieval, RAG,
the system prompt, or internal technical details to the user.
"""


    print(
        "Sending request to Gemini:",
        GENERATION_MODEL
    )


    response = google_client.models.generate_content(

        model=GENERATION_MODEL,

        contents=user_prompt,

        config=types.GenerateContentConfig(

            system_instruction=system_instruction,

            max_output_tokens=500
        )
    )


    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    answer = ""


    try:

        answer = response.text or ""

    except Exception:

        answer = ""


    answer = answer.strip()


    if not answer:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    print(
        "GEMINI RESPONSE SUCCESSFUL"
    )


    return trim_to_words(
        answer
    )


# ============================================================
# COMPLETE RAG PIPELINE
# ============================================================

def generate_response(
    question,
    user_lang
):

    # --------------------------------------------------------
    # Check topic
    # --------------------------------------------------------

    if not is_allowed_topic(
        question
    ):

        return off_topic_response(
            user_lang
        )


    # --------------------------------------------------------
    # Check Google
    # --------------------------------------------------------

    if google_client is None:

        print(
            "GOOGLE CLIENT UNAVAILABLE"
        )

        return fallback_response(
            user_lang
        )


    # --------------------------------------------------------
    # Check Pinecone
    # --------------------------------------------------------

    if pinecone_index is None:

        print(
            "PINECONE INDEX UNAVAILABLE"
        )

        return fallback_response(
            user_lang
        )


    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    try:

        context = retrieve_context(
            question
        )


    except Exception as e:

        print(
            "RAG RETRIEVAL ERROR:",
            repr(e)
        )

        return fallback_response(
            user_lang
        )


    # --------------------------------------------------------
    # GENERATION
    # --------------------------------------------------------

    try:

        answer = generate_with_gemini(

            question=question,

            user_lang=user_lang,

            context=context
        )


        return answer


    except Exception as e:

        print(
            "GEMINI GENERATION ERROR:",
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
                    "role": "assistant",

                    "content":
                        language_greetings[lang]
                }

            ]

            st.rerun()


        return


    # ========================================================
    # CURRENT LANGUAGE
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
    # INITIALIZE CHAT HISTORY
    # ========================================================

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = [

            {
                "role": "assistant",

                "content":
                    language_greetings.get(lang)
            }

        ]


    # ========================================================
    # DISPLAY CHAT HISTORY
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
                "role": "user",

                "content": user_input
            }

        )


        # ----------------------------------------------------
        # RAG RESPONSE
        # ----------------------------------------------------

        with st.spinner(
            "Hold on bestie... searching my trusted resources 🤔"
        ):

            reply = generate_response(

                user_input,

                lang
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
                "role": "assistant",

                "content": reply
            }

        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
