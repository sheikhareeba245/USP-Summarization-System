"""Ollama local AI chat utility for USP Summarization System."""
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"
MAX_CONTEXT_WORDS = 800


def is_ollama_running():
    """Check if Ollama service is running."""
    try:
        response = requests.get(
            "http://localhost:11434",
            timeout=2
        )
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def generate_ai_answer(question, document_text):
    """
    Generate context-grounded answer using Ollama.
    Uses only document context — no external knowledge.
    """
    words = document_text.split()
    if len(words) > MAX_CONTEXT_WORDS:
        context = ' '.join(words[:MAX_CONTEXT_WORDS])
    else:
        context = document_text

    prompt = f"""You are a document assistant. Answer the question using ONLY the provided document context below.
If the answer is not in the context, say: "This information is not available in the document."
Do NOT use any outside knowledge. Keep answer concise — maximum 3 sentences.

Document Context:
{context}

Question: {question}

Answer:"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            return {
                "success": True,
                "answer": response.json().get("response", "").strip()
            }

        return {
            "success": False,
            "answer": "AI service returned an error. Please try again."
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "answer": "AI Assistant is not available right now."
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "answer": "AI Assistant took too long. Please try again."
        }
