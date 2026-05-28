import io
import json
from datetime import datetime
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
    send_file, jsonify
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from extensions import db
from models.summary import Summary
from models.document import Document
from utils.summarizer import general_summary, academic_summary
from utils.keywords import extract_keywords

summarize = Blueprint('summarize', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@summarize.route('/generate-summary', methods=['POST'])
@login_required
def generate_summary():
    
    doc_id = session.get('current_doc_id')
    if not doc_id:
        flash('Please upload a document first.', 'error')
        return redirect(url_for('upload.upload_document'))

    mode = request.form.get('mode', 'general')
    output_format = request.form.get('format', 'paragraph')
    length = request.form.get('length', 'medium')
    doc_name = session.get('current_doc_name')

    
    document = Document.query.get(doc_id)
    if not document:
        flash('Document not found in database. Please upload again.', 'error')
        return redirect(url_for('upload.upload_document'))
        
    text = document.extracted_text

    if mode == 'academic':
        summary_data = academic_summary(text, length, output_format)
        summary_text = json.dumps(summary_data)
        display_summary = summary_data
    else:
        summary_text = general_summary(text, length, output_format)
        display_summary = summary_text

    keywords = extract_keywords(text)
    keywords_str = ', '.join(keywords)

    new_summary = Summary(
        document_id=doc_id,
        mode=mode,
        length=length,
        summary_text=summary_text,
        keywords=keywords_str
    )
    db.session.add(new_summary)
    db.session.commit()

    session['current_summary_id'] = new_summary.summary_id
    session['current_summary'] = summary_text
    session['current_keywords'] = keywords_str
    session['current_mode'] = mode
    session['current_format'] = output_format

    return render_template('result.html',
        doc_name=doc_name,
        mode=mode,
        length=length,
        output_format=output_format,
        summary=display_summary,
        keywords=keywords,
        summary_id=new_summary.summary_id,
        is_academic=(mode == 'academic')
    )


@summarize.route('/download/<int:summary_id>')
@login_required
def download_summary(summary_id):
    summary = Summary.query.get_or_404(summary_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=12
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=6,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        leading=16
    )
    meta_style = ParagraphStyle(
        'Meta',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=4
    )

    story = []

    story.append(Paragraph("USP AI Document Summarization System", title_style))
    story.append(Spacer(1, 8))

    document = Document.query.get(summary.document_id)
    doc_name = document.filename if document else "Unknown"

    story.append(Paragraph(f"Document: {doc_name}", meta_style))
    story.append(Paragraph(f"Mode: {summary.mode.capitalize()} Mode", meta_style))
    story.append(Paragraph(f"Length: {summary.length.capitalize()}", meta_style))
    story.append(Paragraph(
        f"Generated: {summary.generated_date.strftime('%B %d, %Y %I:%M %p')}",
        meta_style
    ))
    story.append(Spacer(1, 16))

    try:
        summary_data = json.loads(summary.summary_text)
        if isinstance(summary_data, dict):
            for section, content in summary_data.items():
                story.append(Paragraph(section.upper(), heading_style))
                for line in content.split('\n'):
                    if line.strip():
                        safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(safe, body_style))
                story.append(Spacer(1, 8))
        else:
            for line in str(summary_data).split('\n'):
                if line.strip():
                    safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    story.append(Paragraph(safe, body_style))
    except Exception:
        for line in summary.summary_text.split('\n'):
            if line.strip():
                safe = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(safe, body_style))

    if summary.keywords:
        story.append(Spacer(1, 12))
        story.append(Paragraph("KEYWORDS", heading_style))
        story.append(Paragraph(summary.keywords, body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "Generated by USP AI Document Summarization System — University of Southern Punjab",
        meta_style
    ))

    doc.build(story)
    buffer.seek(0)

    filename = f"Summary_{doc_name.rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d')}.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


@summarize.route('/rate-summary', methods=['POST'])
@login_required
def rate_summary():
    data = request.get_json()
    summary_id = data.get('summary_id')
    rating = data.get('rating')

    summary = Summary.query.get(summary_id)
    if summary:
        summary.rating = rating
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})