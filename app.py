from flask import Flask, session
from models import db
from routes import init_routes
import os
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # 1 day
app.config['JSON_AS_ASCII'] = False  # Enable proper Unicode support

# Initialize database
db.init_app(app)

# Initialize routes
init_routes(app)

# Create database tables
with app.app_context():
    db.create_all()
    print("Database tables created successfully")

if __name__ == '__main__':
    app.run(debug=True)