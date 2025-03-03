from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Chat, Message
import os
from datetime import datetime

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__)

def init_routes(app):
    app.register_blueprint(auth)
    app.register_blueprint(main)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return jsonify({'success': True})
        
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401
    
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
        
        user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        return jsonify({'success': True})
    
    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))

@main.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.chat_list'))

@main.route('/chat')
def chat_list():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    # Проверяем наличие чатов только при первой регистрации
    if not user.chats and not Chat.query.filter_by(created_by=user.id).first():
        # Create a default chat
        new_chat = Chat(
            name=f"Чат {user.username}",
            created_by=user.id
        )
        new_chat.users.append(user)
        db.session.add(new_chat)
        db.session.commit()
    
    # Check for existing avatar
    avatar_url = None
    for ext in ALLOWED_EXTENSIONS:
        avatar_path = os.path.join(UPLOAD_FOLDER, f"user_{session['user_id']}.{ext}")
        if os.path.exists(avatar_path):
            avatar_url = f'/static/avatars/user_{session["user_id"]}.{ext}'
            break
    
    # Получаем первый чат пользователя
    first_chat = Chat.query.filter(Chat.users.any(id=user.id)).first()
    
    return render_template('chat.html', 
                         username=user.username,
                         avatar_url=avatar_url,
                         first_chat_id=first_chat.id if first_chat else None)

@main.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    # Check for existing avatar
    avatar_url = None
    for ext in ALLOWED_EXTENSIONS:
        avatar_path = os.path.join(UPLOAD_FOLDER, f"user_{session['user_id']}.{ext}")
        if os.path.exists(avatar_path):
            avatar_url = f'/static/avatars/user_{session["user_id"]}.{ext}'
            break
            
    return render_template('profile.html', 
                         username=user.username,
                         status=user.status,
                         avatar_url=avatar_url)

@main.route('/user/profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return jsonify({'error': 'User not found'}), 404
    
    try:
        data = request.get_json()
        username = data.get('username')
        status = data.get('status')
        new_password = data.get('new_password')
        
        if username and username != user.username:
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
            user.username = username
        
        if status is not None:
            user.status = status
            
        if new_password:
            user.password = generate_password_hash(new_password)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении профиля'}), 500

@main.route('/user/avatar', methods=['POST'])
def upload_avatar():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'avatar' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
    
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Create a unique filename using user_id
            filename = f"user_{session['user_id']}{os.path.splitext(secure_filename(file.filename))[1]}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Remove old avatar if exists
            for ext in ALLOWED_EXTENSIONS:
                old_avatar = os.path.join(UPLOAD_FOLDER, f"user_{session['user_id']}.{ext}")
                if os.path.exists(old_avatar):
                    os.remove(old_avatar)
            
            # Save new avatar
            file.save(file_path)
            return jsonify({
                'success': True,
                'avatar_url': f'/static/avatars/{filename}'
            })
        except Exception as e:
            print(f"Error uploading avatar: {str(e)}")
            return jsonify({'error': 'Ошибка при сохранении файла'}), 500
    
    return jsonify({'error': 'Недопустимый тип файла'}), 400

@main.route('/api/chats')
def get_chats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    chats = []
    for chat in Chat.query.filter(Chat.users.any(id=user.id)).all():
        chats.append({
            'id': chat.id,
            'name': chat.name,
            'created_by': chat.created_by,
            'member_count': len(chat.users)
        })
    
    return jsonify(chats)

@main.route('/api/chats', methods=['POST'])
def create_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    chat_name = data.get('name')
    
    if not chat_name:
        return jsonify({'error': 'Chat name is required'}), 400
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    chat = Chat(
        name=chat_name,
        created_by=user.id
    )
    chat.users.append(user)
    db.session.add(chat)
    db.session.commit()
    
    return jsonify({
        'id': chat.id,
        'name': chat.name,
        'created_by': chat.created_by,
        'member_count': len(chat.users)
    })

@main.route('/api/chats/<int:chat_id>/messages')
def get_messages(chat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
        
    # Проверяем, является ли пользователь участником чата
    if user not in chat.users:
        return jsonify({'error': 'Access denied'}), 403
    
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp.asc()).all()
    messages_data = []
    
    for message in messages:
        user = User.query.get(message.user_id)
        # Проверяем аватар пользователя
        avatar_url = None
        for ext in ALLOWED_EXTENSIONS:
            avatar_path = os.path.join(UPLOAD_FOLDER, f"user_{user.id}.{ext}")
            if os.path.exists(avatar_path):
                avatar_url = f'/static/avatars/user_{user.id}.{ext}'
                break
                
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'username': user.username,
            'avatar_url': avatar_url,
            'is_own': message.user_id == session['user_id']
        })
    
    return jsonify({
        'messages': messages_data,
        'chat_name': chat.name
    })

@main.route('/api/chats/<int:chat_id>/messages', methods=['POST'])
def send_message(chat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    data = request.get_json()
    content = data.get('content')
    
    if not content or not content.strip():
        return jsonify({'error': 'Message content is required'}), 400
    
    user = User.query.get(session['user_id'])
    message = Message(
        content=content,
        user_id=session['user_id'],
        chat_id=chat_id,
        timestamp=datetime.utcnow()
    )
    
    # Проверяем аватар пользователя
    avatar_url = None
    for ext in ALLOWED_EXTENSIONS:
        avatar_path = os.path.join(UPLOAD_FOLDER, f"user_{user.id}.{ext}")
        if os.path.exists(avatar_path):
            avatar_url = f'/static/avatars/user_{user.id}.{ext}'
            break
    
    try:
        db.session.add(message)
        db.session.commit()
        return jsonify({
            'success': True,
            'message_id': message.id,
            'username': user.username,
            'avatar_url': avatar_url
        })
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to send message'}), 500
