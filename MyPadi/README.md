# MyPadi 🤖💬

**MyPadi** is an AI-powered chatbot designed to educate, support, and guide users on sexual and reproductive health topics, particularly around HIV, STIs, and teenage pregnancy. The goal is to provide a judgment-free, informative space where users can learn, get answers, and check symptoms confidently.

---

## 🚀 Features

- ✅ **Symptom Checker** — Get insights based on selected symptoms.
- ✅ **HIV & STI Education** — Access reliable, well-researched medical information.
- ✅ **Myth Buster Quiz** — Interactive quiz to debunk common sexual health myths.
- ✅ **PDF Repository** — Browse official documents and fact sheets from CDC/WHO.
- ✅ **Vector Search (Pinecone)** — Smart, semantically relevant document retrieval.
- ✅ **Secure API Integration** — Easily manage API keys using `.env` files.

---

## 🛠️ Tech Stack

- **Python 3.12**
- **Streamlit** – Web-based app UI
- **Pinecone** – Vector similarity search for document queries
- **Langchain / OpenAI API** – Optional: Smart question answering
- **dotenv** – Environment variable management

---

## 📁 Project Structure

```bash
MyPadi/
├── main.py                  # Streamlit app entry point
├── requirements.txt         # Python dependencies
├── pinecone_vector.py       # Pinecone vector embedding & querying
├── symptom_checker.py       # Symptom analysis logic
├── myth_fact_quiz.py        # Myth vs fact quiz logic
├── keywords.py              # Keyword and topic detection
├── symptom_data.py          # Dictionary of symptoms
├── myth_data.py             # Myths and facts database
├── STI_TEENAGE_PREG/        # Folder with CDC/WHO PDF resources
├── __pycache__/             # Python bytecode cache
├── .env.example             # Sample env file
├── API_KEY.env              # Actual API keys (not committed)
└── README.md
```

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/georgegabriel419/MyPadi.git
cd MyPadi
```

### 2. Create Environment File

```bash
cp .env.example API_KEY.env
```

> Edit `API_KEY.env` to include your actual keys.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run main.py
```

---

## 🔐 Environment Variables

These should be stored in `API_KEY.env`:

```env
OPENAI_API_KEY=your_openai_key_here
PINECONE_API_KEY=your_pinecone_key_here
PINECONE_ENV=your_pinecone_environment
PINECONE_INDEX=your_pinecone_index
```

---

## 📄 PDF Resources

Located in the `STI_TEENAGE_PREG/` folder:

- CDC & WHO documents on:
  - Gonorrhea
  - Chlamydia
  - Pelvic Inflammatory Disease
  - HIV
  - STIs and Pregnancy
  - Congenital Syphilis
  - Mycoplasma genitalium
  - Teen pregnancy education

---

## 🧠 Educational Quiz

Play the interactive **Myth Buster Quiz** and learn the facts vs. common misconceptions around sexual and reproductive health.

---

## 👤 Author

**George Gabriel**  
GitHub: [@georgegabriel419](https://github.com/georgegabriel419)

---

## 📃 License

This project is for educational and non-commercial use only.  

---

## 🙏 Acknowledgments

- CDC and WHO for publicly available health education materials  
- Pinecone and OpenAI for enabling powerful AI experiences  
- Streamlit for making app deployment effortless
