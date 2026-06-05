"""Chat model for USP Summarization System."""
from datetime import datetime
from extensions import db
class Chat(db.Model):
    __tablename__ = 'chats'
    chat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.document_id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
