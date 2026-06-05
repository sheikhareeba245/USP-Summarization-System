"""Summary library management routes"""
import json
from functools import wraps
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from extensions import db
from models.summary import Summary
from models.document import Document

library = Blueprint('library', __name__)

def login_required(f):
    """Decorator to protect routes that require login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@library.route('/library')
@login_required
def view_library():
    """Show user summary"""
    user_id = session['user_id']
    documents = Document.query.filter_by(
        user_id=user_id
    ).order_by(Document.upload_date.desc()).all()


    library_items = []
    for doc in documents:
        summaries = Summary.query.filter_by(
            document_id=doc.document_id
        ).order_by(Summary.generated_date.desc()).all()

        for summary in summaries:

            try:
                data = json.loads(summary.summary_text)
                if isinstance(data, dict):
                    first_section = list(data.values())[0]
                    if len(first_section) > 150:
                        preview = first_section[:150] + '...'
                    else:
                        preview = first_section
                else:
                    preview = str(data)[:150] + '...'
            except (json.JSONDecodeError, ValueError, KeyError):
                preview = summary.summary_text[:150] + '...'

            library_items.append({
                'summary_id': summary.summary_id,
                'doc_name': doc.filename,
                'doc_id': doc.document_id,
                'mode': summary.mode,
                'length': summary.length,
                'keywords': summary.keywords,
                'rating': summary.rating,
                'generated_date': summary.generated_date,
                'upload_date': doc.upload_date,
                'preview': preview
            })

    return render_template('library.html',
        items=library_items,
        total=len(library_items)
    )


@library.route('/library/view/<int:summary_id>')
@login_required
def view_summary(summary_id):
    """Show full summary in detail"""
    summary = Summary.query.get_or_404(summary_id)
    document = Document.query.get(summary.document_id)

    # Ownership check
    if document.user_id != session['user_id']:
        flash('Access denied.', 'error')
        return redirect(url_for('library.view_library'))

    try:
        summary_data = json.loads(summary.summary_text)
        is_academic=isinstance(summary_data, dict)
        if not is_academic:
            summary_data = summary.summary_text
    except (json.JSONDecodeError,ValueError):
        summary_data = summary.summary_text
        is_academic = False

    keywords = summary.keywords.split(', ') if summary.keywords else []

    return render_template('summary_detail.html',
        summary=summary_data,
        is_academic=is_academic,
        doc_name=document.filename,
        mode=summary.mode,
        length=summary.length,
        keywords=keywords,
        summary_id=summary.summary_id,
        generated_date=summary.generated_date,
        rating=summary.rating
    )


@library.route('/library/delete/<int:summary_id>', methods=['POST'])
@login_required
def delete_summary(summary_id):
    """Delete a summary from library"""
    summary = Summary.query.get_or_404(summary_id)
    document = Document.query.get(summary.document_id)

    if document.user_id != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Access denied'})

    db.session.delete(summary)
    db.session.commit()

    flash('Summary deleted successfully.', 'success')
    return redirect(url_for('library.view_library'))


@library.route('/library/rate/<int:summary_id>', methods=['POST'])
@login_required
def rate_summary(summary_id):
    """Rate a summary"""
    summary = Summary.query.get_or_404(summary_id)
    document = Document.query.get(summary.document_id)

    if document.user_id != session['user_id']:
        return jsonify({'status': 'error'})

    data = request.get_json()
    rating = data.get('rating')

    summary.rating = rating
    db.session.commit()

    return jsonify({'status': 'success'})
