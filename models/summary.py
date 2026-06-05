"""Summary model for USP Summarization System."""
from datetime import datetime
from extensions import db

class Summary(db.Model):
    __tablename__ = 'summaries'
    summary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.document_id'), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    length = db.Column(db.String(20), nullable=False)
    summary_text = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
