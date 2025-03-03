from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    avatar_url = db.Column(db.String(200))
    status = db.Column(db.String(100))
    
    # Relationships
    messages = db.relationship('Message', backref='user', lazy=True)
    chats = db.relationship('Chat', backref='creator', lazy=True, foreign_keys='Chat.creator_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)