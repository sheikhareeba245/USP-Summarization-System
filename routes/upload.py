"""Document upload and text extraction routes"""
import os
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)
from werkzeug.utils import secure_filename
from extensions import db
from models.document import Document
from utils.extractor import (
    extract_text, allowed_file,
    get_word_count, get_file_size
)

upload = Blueprint('upload', __name__)

def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@upload.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    """Handle documents upload and text extraction"""
    if request.method == 'GET':
        session.pop('current_doc_id', None)
        session.pop('current_doc_name', None)
        session.pop('current_doc_text', None)
        session.pop('word_count', None)
        session.pop('file_size', None)
        session.pop('current_summary_id', None)
        session.pop('current_summary', None)
        session.pop('current_keywords', None)
        session.pop('current_mode', None)
        session.pop('current_format', None)

    if request.method == 'POST':

        session.pop('current_doc_id', None)
        session.pop('current_doc_name', None)
        session.pop('current_doc_text', None)
        session.pop('current_doc_word_count', None)
        session.pop('current_summary_id', None)
        session.pop('current_summary', None)
        session.pop('current_keywords', None)

        # File check
        if 'document' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)

        file = request.files['document']

        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)

        # Extension check
        allowed = current_app.config['ALLOWED_EXTENSIONS']
        if not allowed_file(file.filename, allowed):
            flash('Invalid file type. Only PDF, DOCX, and TXT allowed.', 'error')
            return redirect(request.url)

        # Save file
        filename = secure_filename(file.filename)
        file_type = filename.rsplit('.', 1)[1].lower()
        upload_folder = current_app.config['UPLOAD_FOLDER']

        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        # Extract text
        extracted_text = extract_text(file_path, file_type)

        if not extracted_text or len(extracted_text.strip()) < 50:
            os.remove(file_path)
            flash('Could not extract text from this file. Please try another file.', 'error')
            return redirect(request.url)

        word_count = get_word_count(extracted_text)
        file_size = get_file_size(file_path)

        # Save to database
        document = Document(
            user_id=session['user_id'],
            filename=filename,
            filetype=file_type,
            extracted_text=extracted_text
        )
        db.session.add(document)
        db.session.commit()
        session['current_doc_id'] = document.document_id
        session['current_doc_name'] = filename
        session['word_count'] = word_count
        session['file_size'] = file_size

        flash('Document uploaded successfully!', 'success')
        return redirect(url_for('upload.summarize_options'))

    return render_template('upload.html')
@upload.route('/summarize-options')
@login_required
def summarize_options():
    """Show summarization option page"""
    if 'current_doc_id' not in session:
        flash('Please upload a document first.', 'error')
        return redirect(url_for('upload.upload_document'))

    return render_template('summarize_options.html',
        doc_name=session.get('current_doc_name'),
        word_count=session.get('word_count'),
        file_size=session.get('file_size')
    )
