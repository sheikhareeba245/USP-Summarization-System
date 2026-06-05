"""Document model for USP Summarization System."""
from datetime import datetime
from extensions import db

class Document(db.Model):
    __tablename__ = 'documents'
    document_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(10), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    extracted_text = db.Column(db.Text, nullable=False)
    summaries = db.relationship('Summary', backref='document', lazy=True)
    chats = db.relationship('Chat', backref='document', lazy=True)
