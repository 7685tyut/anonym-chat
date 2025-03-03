from flask import Flask
from models import db
from flask_migrate import Migrate
from models.user import User  # Import models in correct order
from models.chat import Chat
from models.message import Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables.")
        
        # Create all tables
        db.create_all()
        print("Created all tables.")
        
        print("Database migration completed successfully!")