import os
import sys
import traceback
from flask import Flask
from models import db
from models.user import User
from models.chat import Chat
from models.message import Message

def check_database_file(db_path):
    """Check if database file exists and is accessible"""
    print(f"\n=== Checking database file: {db_path} ===")
    if os.path.exists(db_path):
        print(f"[OK] Database file exists: {db_path}")
        print(f"   File size: {os.path.getsize(db_path)} bytes")
        print(f"   Last modified: {os.path.getmtime(db_path)}")
    else:
        print(f"[ERROR] Database file does not exist: {db_path}")
    
    # Check parent directory permissions
    parent_dir = os.path.dirname(db_path)
    if os.path.exists(parent_dir):
        print(f"[OK] Parent directory exists: {parent_dir}")
        try:
            test_file = os.path.join(parent_dir, "test_write_permission.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"[OK] Directory is writable: {parent_dir}")
        except Exception as e:
            print(f"[ERROR] Directory is not writable: {parent_dir}")
            print(f"   Error: {str(e)}")
    else:
        print(f"[ERROR] Parent directory does not exist: {parent_dir}")

def check_models():
    """Check model definitions"""
    print("\n=== Checking model definitions ===")
    try:
        # Check User model
        print("User model attributes:")
        for column in User.__table__.columns:
            print(f"  - {column.name}: {column.type} (nullable: {column.nullable})")
        
        # Check Chat model
        print("\nChat model attributes:")
        for column in Chat.__table__.columns:
            print(f"  - {column.name}: {column.type} (nullable: {column.nullable})")
        
        # Check Message model
        print("\nMessage model attributes:")
        for column in Message.__table__.columns:
            print(f"  - {column.name}: {column.type} (nullable: {column.nullable})")
        
        print("\n[OK] All models loaded successfully")
    except Exception as e:
        print(f"\n[ERROR] Error checking models: {str(e)}")
        traceback.print_exc()

def test_user_creation():
    """Test creating a user"""
    print("\n=== Testing user creation ===")
    try:
        # Create a test user
        test_user = User()
        test_user.username = "test_user_" + os.urandom(4).hex()
        test_user.set_password("test_password")
        
        print(f"Created test user: {test_user.username}")
        print(f"Password hash length: {len(test_user.password_hash)}")
        
        # Try to add to session
        db.session.add(test_user)
        print("[OK] User added to session")
        
        # Try to commit
        db.session.commit()
        print(f"[OK] User committed to database with ID: {test_user.id}")
        
        # Try to query
        queried_user = User.query.filter_by(username=test_user.username).first()
        if queried_user:
            print(f"[OK] User retrieved from database: {queried_user.username} (ID: {queried_user.id})")
        else:
            print("[ERROR] Failed to retrieve user from database")
        
        # Cleanup
        db.session.delete(test_user)
        db.session.commit()
        print("[OK] Test user deleted")
    except Exception as e:
        print(f"[ERROR] Error testing user creation: {str(e)}")
        traceback.print_exc()
        db.session.rollback()

def main():
    """Main debug function"""
    print("=== Starting application debugging ===")
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Check database files
    check_database_file("chat.db")
    check_database_file("instance/chat.db")
    
    # Initialize database
    db.init_app(app)
    
    # Test with app context
    with app.app_context():
        try:
            # Check if tables exist
            print("\n=== Checking database tables ===")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables in database: {tables}")
            
            if not tables:
                print("Creating database tables...")
                db.create_all()
                print("Tables created.")
                tables = inspector.get_table_names()
                print(f"Tables after creation: {tables}")
            
            # Check models
            check_models()
            
            # Test user creation
            test_user_creation()
            
        except Exception as e:
            print(f"[ERROR] Error during debugging: {str(e)}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
