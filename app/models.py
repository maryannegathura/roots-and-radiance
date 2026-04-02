from app import db
from datetime import datetime
import uuid

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_name = db.Column(db.String(100), nullable=True)

    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_session.session_id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='Pakistan')
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

