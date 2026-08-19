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


# ───── Apply Custom Theme ─────
apply_custom_styles()

st.set_page_config(
    page_title="Chat with MyPadi",
    page_icon="💬"
)

# ───── Load Environment Variables ─────
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SPITCH_API_KEY = os.getenv("SPITCH_API_KEY")


# ───── Check Required Keys ─────
if not PINECONE_API_KEY:
    st.error("Pinecone API key is missing.")

if not GOOGLE_API_KEY:
    st.error("Google API key is missing.")


# ───── Pinecone ─────
pc = Pinecone(api_key=PINECONE_API_KEY)

pinecone_index = pc.Index("sti-teenage-preg")

index_info = pc.describe_index("sti-teenage-preg")

print("PINECONE INDEX INFO:", index_info)


# ───── Google GenAI Client ─────
# Uses the newer Google GenAI SDK directly.
google_client = genai.Client(api_key=GOOGLE_API_KEY)


# ───── Spitch ─────
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

You give warm, non-judgy and medically responsible information
about STIs and teenage pregnancy in {lang}.

Sound casual, friendly, caring and easy to understand.

Use the following information from the knowledge base if helpful:

{doc_content}

Respond in {lang} ONLY.

Avoid using English or mixing languages when responding in
Yoruba, Igbo or Hausa.

Use everyday conversational language that sounds natural.

Keep the answer brief, around 1–3 sentences when possible.

If the question is not relevant to STI or teenage pregnancy,
kindly steer the conversation back to those topics.

Do not invent medical facts.
Do not make a diagnosis.
Encourage the user to speak with a qualified healthcare professional
when the situation requires medical attention.
"""


# ───── Language Translation Codes ─────
def translate_prompt_language(lang):

    return {
        "Yoruba": "yo",
        "Igbo": "ig",
        "Hausa": "ha",
        "Pidgin": None
    }.get(lang, "en")


# ───── Trim Response ─────
def trim_to_words(text, max_words=300):

    if not text:
        return ""

    words = text.split()

    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."

    return " ".join(words)


# ───── Google Embedding Function ─────
def create_embedding(text, max_retries=3):

    """
    Creates a 768-dimensional embedding using
    Google's current GenAI SDK.

    The Pinecone index is 768 dimensions,
    so output_dimensionality must remain 768.
    """

    last_error = None

    for attempt in range(max_retries):

        try:

            result = google_client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )

            embedding = result.embeddings[0].values

            embedding = [float(value) for value in embedding]

            # Safety check
            if len(embedding) != 768:
                raise ValueError(
                    f"Expected 768 dimensions, got {len(embedding)}"
                )

            return embedding

        except Exception as e:

            last_error = e

            print(
                f"Embedding attempt {attempt + 1} failed: {e}"
            )

            if attempt < max_retries - 1:
                time.sleep(2)

    raise RuntimeError(
        f"Google embedding failed after {max_retries} attempts: "
        f"{last_error}"
    )


# ───── Generate Response ─────
def generate_response(question, user_lang):

    # Check allowed topics
    if not any(
        keyword in question.lower()
        for keyword in allowed_keywords
    ):

        return {
            "English": (
                "Hmm bestie 🫶🏾 — I can only help with STI "
                "and teenage pregnancy matters. "
                "Ask me something like that!"
            ),

            "Yoruba": (
                "Ore mi 🫶🏾 — Mo le ran e lowo lori koko "
                "STI ati oyun lasiko omode nikan."
            ),

            "Igbo": (
                "Nwanne 🫶🏾 — Ana m enyere maka STIs "
                "na ime nwa n'oge ntorobia."
            ),

            "Hausa": (
                "Kawaye 🫶🏾 — Tambayoyina na game da STI "
                "ko ciki a kuruciya ne kawai."
            ),

            "Pidgin": (
                "Padi mi 🫶🏾 — Na only STI or teenage "
                "belle I sabi talk about oh."
            )
        }.get(
            user_lang,
            "Please ask me something about STI or teenage pregnancy."
        )


    # ───── Create Query Embedding ─────
    try:

        query_embed = create_embedding(question)

    except Exception as e:

        print("EMBEDDING ERROR:", e)

        return {
            "English": (
                "Sorry bestie 🫶🏾, I'm having a little connection "
                "problem right now. Please try again in a moment."
            ),

            "Yoruba": (
                "Ma binu ore mi 🫶🏾, isoro kekere wa pelu asopọ "
                "bayi. Jowo gbiyanju lẹẹkansi."
            ),

            "Igbo": (
                "Ndo nwanne 🫶🏾, enwere obere nsogbu njikọ ugbu a. "
                "Biko nwaa ọzọ obere oge."
            ),

            "Hausa": (
                "Yi hakuri kawaye 🫶🏾, akwai karamar matsalar "
                "haɗi yanzu. Da fatan za ka sake gwadawa."
            ),

            "Pidgin": (
                "Sorry my padi 🫶🏾, connection get small problem "
                "now. Abeg try again in a little while."
            )
        }.get(
            user_lang,
            "Sorry, something went wrong. Please try again."
        )


    # ───── Pinecone Search ─────
    try:

        results = pinecone_index.query(
            vector=query_embed,
            top_k=3,
            include_metadata=True
        )

        matches = results.get("matches", [])

        doc_contents = []

        for match in matches:

            metadata = match.get("metadata", {})

            text = metadata.get("text", "")

            if text:
                doc_contents.append(text)

        doc = "\n".join(doc_contents)

        if not doc:
            doc = "No extra information was found."

    except Exception as e:

        print("PINECONE ERROR:", e)

        doc = "No extra information was found."


    # ───── Escape Curly Brackets ─────
    doc = (
        doc
        .replace("{", "{{")
        .replace("}", "}}")
    )


    # ───── Create Prompt ─────
    prompt = system_prompt_template_base.format(
        doc_content=doc,
        lang=user_lang
    )


    # ───── Conversation History ─────
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


    # ───── Gemini Chat Model ─────
    chat = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )


    # ───── LangChain Prompt ─────
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


    # ───── Generate Answer ─────
    try:

        response = chain.invoke({
            "question": question
        })

        full_text = response.get(
            "text",
            ""
        ).strip()

        return trim_to_words(
            full_text
        )

    except Exception as e:

        print("GEMINI CHAT ERROR:", e)

        return {
            "English": (
                "Sorry bestie 🫶🏾, I couldn't generate a response "
                "right now. Please try again."
            ),

            "Yoruba": (
                "Ma binu ore mi 🫶🏾, mi o le dahun bayii. "
                "Jowo gbiyanju lẹẹkansi."
            ),

            "Igbo": (
                "Ndo nwanne 🫶🏾, enweghị m ike ịza ugbu a. "
                "Biko nwaa ọzọ."
            ),

            "Hausa": (
                "Yi hakuri kawaye 🫶🏾, ba zan iya ba da amsa "
                "yanzu ba. Da fatan za ka sake gwadawa."
            ),

            "Pidgin": (
                "Sorry my padi 🫶🏾, I no fit generate response "
                "now. Abeg try again."
            )
        }.get(
            user_lang,
            "Sorry, I couldn't generate a response."
        )


# ───── Text-to-Speech ─────
def synthesize_tts(text, lang_code):

    if not lang_code:
        return None

    if lang_code not in [
        "en",
        "yo",
        "ig",
        "ha"
    ]:
        return None

    try:

        response = spitch_client.speech.generate(
            text=text,
            language=lang_code,
            voice="femi"
        )

        return response.read()

    except Exception as e:

        print("TTS ERROR:", e)

        return None


# ───── Main App ─────
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


        # ───── Initialize Chat ─────
        if "chat_history" not in st.session_state:

            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": language_greetings.get(lang)
                }
            ]


        # ───── Display Chat History ─────
        for msg in st.session_state.chat_history:

            with st.chat_message(
                msg["role"]
            ):

                st.markdown(
                    msg["content"]
                )


        # ───── User Input ─────
        if user_input := st.chat_input(
            "What's on your mind?"
        ):

            with st.chat_message("user"):

                st.markdown(
                    user_input
                )


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

                reply = generate_response(
                    user_input,
                    lang
                )


            with st.chat_message("assistant"):

                st.markdown(
                    reply
                )


            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )


            # ───── Text-to-Speech ─────
            lang_code = translate_prompt_language(
                lang
            )


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
