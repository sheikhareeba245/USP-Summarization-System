"""Chat with Document extractive QA and AI assistant routes."""
import re
from functools import wraps
from flask import (
    Blueprint, request, session,
    flash, redirect, url_for,
    jsonify, render_template
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from extensions import db
from models.chat import Chat
from models.document import Document

chat_bp = Blueprint('chat', __name__)


def login_required(f):
    """Decorator to protect routes that require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def find_relevant_sentences(question, document_text, top_n=3):
    """Find relevant sentences using TF-IDF cosine similarity."""
    sentences = [
        s.strip()
        for s in re.split(r'(?<=[.!?])\s+', document_text)
        if len(s.strip()) > 20
    ]

    if not sentences:
        return [], 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        all_texts = [question] + sentences
        tfidf_matrix = vectorizer.fit_transform(all_texts)

        question_vec = tfidf_matrix[0]
        sentence_vecs = tfidf_matrix[1:]

        similarities = cosine_similarity(
            question_vec, sentence_vecs
        )[0]

        top_indices = similarities.argsort()[-top_n:][::-1]
        best_score = float(similarities[top_indices[0]])

        relevant = [
            sentences[i]
            for i in top_indices
            if similarities[i] > 0.1
        ]

        return relevant, best_score

    except (ValueError, RuntimeError):
        question_words = set(
            w.lower().strip('.,;:?!')
            for w in question.split()
            if len(w) > 4
        )
        scored = []
        for sentence in sentences:
            words = set(
                w.lower().strip('.,;:?!')
                for w in sentence.split()
            )
            score = len(question_words & words)
            if score > 0:
                scored.append((score, sentence))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_n]], 0.0


@chat_bp.route('/chat-page')
@login_required
def chat_page():
    """Show document selection for chat."""
    user_id = session['user_id']
    documents = Document.query.filter_by(
        user_id=user_id
    ).order_by(Document.upload_date.desc()).all()

    return render_template('chat.html',
        documents=documents,
        selected_doc=None
    )


@chat_bp.route('/chat-page/<int:doc_id>')
@login_required
def chat_with_doc(doc_id):
    """Open chat for specific document."""
    document = Document.query.get_or_404(doc_id)

    if document.user_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('chat.chat_page'))

    session['current_doc_id'] = doc_id

    return render_template('chat.html',
        documents=[],
        selected_doc=document
    )


@chat_bp.route('/chat', methods=['POST'])
@login_required
def ask_question():
    """Handle chat question — extractive answer."""
    data = request.get_json()
    question = data.get('question', '').strip()
    doc_id = data.get('doc_id') or session.get('current_doc_id')

    if not question:
        return jsonify({
            'status': 'error',
            'answer': 'Please enter a question.'
        })

    if not doc_id:
        return jsonify({
            'status': 'error',
            'answer': 'No document found. Please upload first.'
        })

    document = Document.query.get(doc_id)
    if not document:
        return jsonify({
            'status': 'error',
            'answer': 'Document not found in database.'
        })

    relevant, score = find_relevant_sentences(
        question,
        document.extracted_text,
        top_n=3
    )

    if not relevant:
        answer = "Sorry, I could not find relevant information for your question in this document."
        show_ai_button = True
    else:
        answer = ' '.join(relevant)
        show_ai_button = True

    chat_record = Chat(
        document_id=doc_id,
        question=question,
        answer=answer
    )
    db.session.add(chat_record)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'answer': answer,
        'show_ai_button': show_ai_button,
        'chat_id': chat_record.chat_id,
        'method': 'extractive'
    })


@chat_bp.route('/chat/ai', methods=['POST'])
@login_required
def ask_ai():
    """Handle AI assistant question using Ollama."""
    from utils.ollama_chat import generate_ai_answer, is_ollama_running

    data = request.get_json()
    question = data.get('question', '').strip()
    doc_id = data.get('doc_id') or session.get('current_doc_id')

    if not question or not doc_id:
        return jsonify({
            'status': 'error',
            'answer': 'Invalid request.'
        })

    if not is_ollama_running():
        return jsonify({
            'status': 'error',
            'answer': 'AI Assistant is not available. Please make sure Ollama is running.'
        })

    document = Document.query.get(doc_id)
    if not document:
        return jsonify({
            'status': 'error',
            'answer': 'Document not found.'
        })

    result = generate_ai_answer(question, document.extracted_text)

    if result['success']:
        chat_record = Chat(
            document_id=doc_id,
            question=f"[AI] {question}",
            answer=result['answer']
        )
        db.session.add(chat_record)
        db.session.commit()

    return jsonify({
        'status': 'success' if result['success'] else 'error',
        'answer': result['answer'],
        'method': 'ai_generated'
    })


@chat_bp.route('/chat/history', methods=['GET'])
@login_required
def chat_history():
    """Return chat history for current document."""
    doc_id = session.get('current_doc_id')
    if not doc_id:
        return jsonify({'status': 'error', 'history': []})

    chats = Chat.query.filter_by(
        document_id=doc_id
    ).order_by(Chat.timestamp.asc()).all()

    history = [
        {
            'question': c.question,
            'answer': c.answer,
            'timestamp': c.timestamp.strftime('%I:%M %p')
        }
        for c in chats
    ]

    return jsonify({'status': 'success', 'history': history})
