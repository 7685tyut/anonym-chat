from . import db
from datetime import datetime

class Chat(db.Model):
    __tablename__ = 'chats'  # Explicitly set table name
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(8), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='chat', lazy=True, cascade='all, delete-orphan')