
from flask import Blueprint, request, jsonify
from app.models import db, User, Profile
from werkzeug.security import check_password_hash
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate input
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create user profile
        profile = Profile(
            user_id=user.id,
            native_language='Telugu',
            target_language='English',
            proficiency_level=data.get('proficiency_level', 'beginner')
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'proficiency_level': profile.proficiency_level
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        username_or_email = data.get('username_or_email', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'error': 'Username/email and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email.lower())
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat(),
                'profile': {
                    'native_language': user.profile.native_language,
                    'target_language': user.profile.target_language,
                    'proficiency_level': user.profile.proficiency_level,
                    'current_streak': user.profile.current_streak,
                    'points': user.profile.points
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update user profile"""
    try:
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = user.profile
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update profile fields
        if 'proficiency_level' in data:
            if data['proficiency_level'] in ['beginner', 'intermediate', 'advanced']:
                profile.proficiency_level = data['proficiency_level']
            else:
                return jsonify({'error': 'Invalid proficiency level'}), 400
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': {
                'proficiency_level': profile.proficiency_level,
                'updated_at': profile.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Profile update failed', 'details': str(e)}), 500
