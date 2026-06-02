# USP AI Document Summarization System

A free, privacy-focused academic document summarization system built exclusively for students of the **University of Southern Punjab, Multan**.

---

## What is this?

Most students rely on ChatGPT or Gemini to summarize their documents. These tools are powerful but come with serious problems they hallucinate, charge money, and send your documents to external servers.

This system was built to solve exactly that.

**USP Summarization System** uses LexRank an extractive AI algorithm that pulls important sentences directly from your document without generating new content. No hallucination. No subscription. No data leaks.

## Who is it for?

Only students of the University of Southern Punjab, Multan.
Login is done using your existing USP LMS credentials no new registration required.

---

## Features

| Feature | Description |
|---|---|
| LMS Login | Login with your USP username and password |
| PDF / DOCX / TXT Upload | Upload any academic document |
| Academic Mode | Structured summary  Abstract, Introduction, Methodology, Results, Conclusion |
| General Mode | Clean paragraph or bullet-point summary |
| Length Control | Short, Medium, or Detailed |
| Keyword Extraction | Top keywords automatically identified |
| Summary Library | All your summaries saved and organized |
| Download as PDF | Export any summary as a formatted PDF |
| Copy to Clipboard | One-click copy |
| Star Rating | Rate your generated summaries |
| Chat with Document | Ask questions about your uploaded document |
| Privacy First | All processing done locally  your documents never leave the server |
| Completely Free | No subscription, no limits, no ads |

---

## Why not just use ChatGPT?

ChatGPT is a generative model. When you ask it to summarize without a strict expert-level prompt, it blends your document content with its training data and invents information that was never in your document. This is called hallucination.

**Proof:**
Maynez et al. (2020) — *On Faithfulness and Factuality in Abstractive Summarization* found that over 70% of abstractive summaries contain hallucinated content, and over 90% of extrinsic hallucinations are factually incorrect.
Bang et al. (2023) *A Multitask, Multilingual, Multimodal Evaluation of ChatGPT* found that ChatGPT fails to answer truthfully 35.38% of the time.

Our system uses **LexRank** a graph-based extractive algorithm that scores and selects existing sentences from your document. Nothing is generated. Nothing is invented.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask |
| Database | SQLite (dev), MySQL (production) |
| Summarization | Sumy — LexRank Algorithm |
| Keywords | KeyBERT |
| PDF Extraction | PyMuPDF (fitz) |
| DOCX Extraction | python-docx |
| PDF Generation | ReportLab |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Deployment | PythonAnywhere |
| Version Control | Git, GitHub |

---

## Project Structure

summarization_system/
├── app.py                  # Application entry point
├── config.py               # Configuration settings
├── extensions.py           # SQLAlchemy instance
├── seed_users.py           # Mock LMS user data
├── requirements.txt        # Dependencies
│
├── models/
│   ├── user.py             # User model
│   ├── document.py         # Document model
│   ├── summary.py          # Summary model
│   └── chat.py             # Chat model
│
├── routes/
│   ├── auth.py             # Login, logout, dashboard
│   ├── upload.py           # Document upload
│   ├── summarize.py        # Summary generation, download
│   └── library.py          # Summary library management
│
├── utils/
│   ├── extractor.py        # Text extraction — PDF, DOCX, TXT
│   ├── summarizer.py       # LexRank summarization
│   └── keywords.py         # KeyBERT keyword extraction
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── summarize_options.html
│   ├── result.html
│   ├── library.html
│   └── summary_detail.html
│
├── static/
│   ├── css/style.css
│   └── js/main.js
│
└── uploads/                # Uploaded documents

## Installation

**Clone the repository:**
```bash
git clone https://github.com/sheikhareeba245/USP-Summarization-System.git
cd USP-Summarization-System
```

**Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Download NLTK data:**
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

**Setup database and seed users:**
```bash
python app.py
# Ctrl+C after "Database ready!"
python seed_users.py
```

**Run the application:**
```bash
python app.py
```

Open browser: `http://127.0.0.1:5000`

**Login with demo credentials:**
Username: BSIT022R24-31
Password: usp2021it001

---

## Research Basis

This project is backed by peer-reviewed research:

1. **Maynez et al. (2020)** — On Faithfulness and Factuality in Abstractive Summarization. *ACL 2020*. Proves 70%+ hallucination rate in abstractive models.

2. **Bang et al. (2023)** — A Multitask, Multilingual, Multimodal Evaluation of ChatGPT. *AACL 2023*. Proves ChatGPT fails truthfully 35.38% of the time.

---

## Team

Final Year Project — BSIT 8th Semester
University of Southern Punjab, Multan
Department of Information Technology

---

## License

This project is developed for academic purposes at the University of Southern Punjab, Multan.
