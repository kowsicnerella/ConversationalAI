
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import db, User, Profile
from app.services.comprehensive_assessment_service import ComprehensiveAssessmentService
from app.services.adaptive_learning_path_generator import AdaptiveLearningPathGenerator
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

# Initialize services
assessment_service = ComprehensiveAssessmentService()
learning_path_generator = AdaptiveLearningPathGenerator()

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
        
        # Immediately start comprehensive assessment
        assessment_result = assessment_service.conduct_comprehensive_assessment(user.id)
        
        if 'error' in assessment_result:
            # If assessment fails, still return successful registration
            return jsonify({
                'message': 'User registered successfully',
                'warning': 'Assessment setup failed - can be completed later',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'proficiency_level': profile.proficiency_level
                }
            }), 201
        
        return jsonify({
            'message': 'User registered successfully! Please complete your assessment to get personalized learning.',
            'telugu_message': 'మీరు విజయవంతంగా నమోదు అయ్యారు! వ్యక్తిగతీకరించిన అభ్యాసం పొందడానికి మీ మూల్యాంకనం పూర్తి చేయండి.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'proficiency_level': profile.proficiency_level
            },
            'assessment': {
                'assessment_id': assessment_result['assessment_id'],
                'questions': assessment_result['questions'],
                'instructions': assessment_result['instructions'],
                'estimated_duration_minutes': assessment_result['estimated_duration_minutes'],
                'skills_being_assessed': assessment_result['skills_being_assessed']
            },
            'next_step': 'complete_assessment'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        username_or_email = data.get('username', '').strip()
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
        
        # Create JWT tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return jsonify({
            'message': 'Login successful',
            'telugu_message': 'లాగిన్ విజయవంతం!',
            'access_token': access_token,
            'refresh_token': refresh_token,
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

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 404
        
        # Create new access token
        new_access_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'telugu_message': 'టోకెన్ విజయవంతంగా రిఫ్రెష్ అయింది',
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user:
            # Update last activity (optional)
            user.last_login = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'message': 'Logout successful',
            'telugu_message': 'లాగ్ అవుట్ విజయవంతం'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Logout failed', 'details': str(e)}), 500

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

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if user exists or not for security
            return jsonify({
                'message': 'If the email exists, a password reset link has been sent.',
                'telugu_message': 'ఈమెయిల్ ఉంటే, పాస్‌వర్డ్ రీసెట్ లింక్ పంపబడింది.'
            }), 200
        
        # Generate reset token (In production, use a proper token with expiration)
        reset_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
        
        # In a real application, you would send an email here
        # For now, we'll return the token for testing purposes
        return jsonify({
            'message': 'Password reset token generated. Check your email.',
            'telugu_message': 'పాస్‌వర్డ్ రీసెట్ టోకెన్ జనరేట్ చేయబడింది. మీ ఈమెయిల్ చూడండి.',
            'reset_token': reset_token  # Remove this in production
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Password reset request failed', 'details': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        new_password = data.get('new_password', '')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully',
            'telugu_message': 'పాస్‌వర్డ్ విజయవంతంగా రీసెట్ చేయబడింది'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Password reset failed', 'details': str(e)}), 500
