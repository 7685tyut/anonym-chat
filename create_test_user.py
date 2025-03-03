from app import app
from models import db
from models.user import User
import random
import string

def generate_random_username(length=8):
    """Generate a random username"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def create_test_user():
    """Create a test user in the database"""
    with app.app_context():
        # Generate random username
        username = generate_random_username()
        password = "password123"
        
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists")
            return
        
        # Create new user
        user = User()
        user.username = username
        user.set_password(password)
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        print(f"Test user created successfully:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  User ID: {user.id}")

if __name__ == "__main__":
    create_test_user()
