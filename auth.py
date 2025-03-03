from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import traceback

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET"])
def register_page():
    if "user_id" in session:
        return redirect(url_for("chat.chat_select"))
    return render_template("register.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        print("Starting registration...")
        
        # Get JSON data from request
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({"error": "Неверный формат данных"}), 400
            
        # Extract username and password
        username = data.get("username")
        password = data.get("password")
        
        print(f"Username: {username}, Password length: {len(password) if password else 0}")
        
        # Validate input
        if not username or not password:
            print("Missing username or password")
            return jsonify({"error": "Заполните все поля"}), 400
            
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists")
            return jsonify({"error": "Пользователь уже существует"}), 400
            
        # Create new user
        user = User()
        user.username = username
        user.set_password(password)
        user.registration_date = datetime.utcnow()
        
        # Save to database
        db.session.add(user)
        db.session.commit()
        
        print(f"Successfully created user: {username} with ID: {user.id}")
        
        # Set session
        session["user_id"] = user.id
        session["username"] = user.username
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Регистрация успешна",
            "redirect": url_for("chat.chat_select")
        })
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({"error": "Ошибка при регистрации"}), 500

@auth_bp.route("/login", methods=["GET"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("chat.chat_select"))
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        print("Starting login...")
        
        # Get JSON data from request
        data = request.get_json()
        print(f"Received login data: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({"error": "Неверный формат данных"}), 400
            
        # Extract username and password
        username = data.get("username")
        password = data.get("password")
        
        print(f"Login attempt for username: {username}")
        
        # Validate input
        if not username or not password:
            print("Missing username or password")
            return jsonify({"error": "Заполните все поля"}), 400
            
        # Find user
        user = User.query.filter_by(username=username).first()
        
        # Check user and password
        if not user:
            print(f"User not found: {username}")
            return jsonify({"error": "Неверное имя пользователя или пароль"}), 401
            
        if not user.check_password(password):
            print(f"Invalid password for user: {username}")
            return jsonify({"error": "Неверное имя пользователя или пароль"}), 401
            
        # Set session
        session["user_id"] = user.id
        session["username"] = user.username
        
        print(f"Successful login for user: {username} with ID: {user.id}")
        
        # Return success response
        return jsonify({
            "success": True,
            "message": "Вход выполнен",
            "redirect": url_for("chat.chat_select")
        })
    except Exception as e:
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": "Ошибка при входе"}), 500

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))