
from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.progress_service import ProgressService
from app.services.gamification_service import GamificationService
from app.services.personalization_service import PersonalizationService
from app.models import db, User, Profile, LearningPath, UserGoal, VocabularyWord, LearningSession
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date, timedelta
from sqlalchemy import func
import json

user_bp = Blueprint('user', __name__)
progress_service = ProgressService()
gamification_service = GamificationService()
personalization_service = PersonalizationService()

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile with comprehensive statistics"""
    try:
        user_id = int(get_jwt_identity())
        profile = progress_service.get_user_profile(user_id)
        if not profile:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        if 'error' in profile:
            return jsonify({
                'error': profile['error'],
                'telugu_message': 'ప్రొఫైల్ డేటా లభించడంలో లోపం'
            }), 500
        
        return jsonify({
            'message': 'Profile retrieved successfully!',
            'telugu_message': 'ప్రొఫైల్ విజయవంతంగా తీసుకోబడింది!',
            'profile': profile
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting profile: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch profile',
            'telugu_message': 'ప్రొఫైల్ పొందడంలో విఫలం'
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile information.
    
    Expected JSON:
    {
        "bio": "Learning English for my career",
        "learning_goals": ["conversation", "business_english"],
        "timezone": "Asia/Kolkata",
        "notification_preferences": {
            "daily_reminders": true,
            "streak_celebrations": true,
            "weekly_progress": false
        }
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Update user fields
        if 'bio' in data:
            if user.profile:
                user.profile.bio = data['bio']
            else:
                profile = Profile(user_id=user_id, bio=data['bio'])
                db.session.add(profile)
        
        if 'learning_goals' in data:
            user.set_learning_goals(data['learning_goals'])
        
        if 'timezone' in data:
            user.timezone = data['timezone']
        
        if 'notification_preferences' in data:
            user.set_notification_preferences(data['notification_preferences'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully!',
            'telugu_message': 'ప్రొఫైల్ విజయవంతంగా అప్‌డేట్ చేయబడింది!',
            'profile': {
                'bio': user.profile.bio if user.profile else None,
                'learning_goals': user.get_learning_goals(),
                'timezone': user.timezone,
                'notification_preferences': user.get_notification_preferences()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'error': 'Failed to update profile',
            'telugu_message': 'ప్రొఫైల్ అప్‌డేట్ చేయడంలో విఫలం'
        }), 500

@user_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get user settings and preferences."""
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Get current goal
        current_goal = UserGoal.query.filter_by(user_id=user_id, is_active=True).first()
        
        settings = {
            'user_info': {
                'username': user.username,
                'email': user.email,
                'native_language': user.profile.native_language if user.profile else 'Telugu',
                'target_language': user.profile.target_language if user.profile else 'English',
                'joined_date': user.created_at.isoformat()
            },
            'learning_preferences': {
                'daily_time_goal': current_goal.daily_time_goal_minutes if current_goal else 10,
                'learning_focus': current_goal.learning_focus if current_goal else 'conversation',
                'preferred_difficulty': user.profile.proficiency_level if user.profile else 'beginner',
                'timezone': user.timezone or 'Asia/Kolkata'
            },
            'notification_settings': user.notification_preferences or {
                'daily_reminders': True,
                'streak_celebrations': True,
                'weekly_progress': True,
                'achievement_alerts': True
            },
            'privacy_settings': getattr(user, 'privacy_settings', None) or {
                'profile_visibility': 'private',
                'show_in_leaderboard': True,
                'share_progress': False
            }
        }
        
        return jsonify({
            'message': 'Settings retrieved successfully!',
            'telugu_message': 'సెట్టింగ్‌లు విజయవంతంగా తీసుకోబడ్డాయి!',
            'settings': settings
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting settings: {str(e)}")
        return jsonify({
            'error': 'Failed to get settings',
            'telugu_message': 'సెట్టింగ్‌లు పొందడంలో విఫలం'
        }), 500

@user_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """
    Update user settings and preferences.
    
    Expected JSON:
    {
        "notification_settings": {
            "daily_reminders": true,
            "streak_celebrations": false
        },
        "privacy_settings": {
            "profile_visibility": "public",
            "show_in_leaderboard": true
        },
        "learning_preferences": {
            "preferred_difficulty": "intermediate",
            "timezone": "Asia/Kolkata"
        }
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Update notification settings
        if 'notification_settings' in data:
            current_notifications = user.notification_preferences or {}
            current_notifications.update(data['notification_settings'])
            user.notification_preferences = current_notifications
        
        # Update privacy settings
        if 'privacy_settings' in data:
            current_privacy = getattr(user, 'privacy_settings', None) or {}
            if isinstance(current_privacy, str):
                current_privacy = json.loads(current_privacy) if current_privacy else {}
            current_privacy.update(data['privacy_settings'])
            user.privacy_settings = json.dumps(current_privacy)
        
        # Update learning preferences
        if 'learning_preferences' in data:
            prefs = data['learning_preferences']
            
            if 'timezone' in prefs:
                user.timezone = prefs['timezone']
            
            if 'preferred_difficulty' in prefs and user.profile:
                user.profile.proficiency_level = prefs['preferred_difficulty']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Settings updated successfully!',
            'telugu_message': 'సెట్టింగ్‌లు విజయవంతంగా అప్‌డేట్ చేయబడ్డాయి!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating settings: {str(e)}")
        return jsonify({
            'error': 'Failed to update settings',
            'telugu_message': 'సెట్టింగ్‌లు అప్‌డేట్ చేయడంలో విఫలం'
        }), 500

@user_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    
    Expected JSON:
    {
        "current_password": "old_password",
        "new_password": "new_password"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'error': 'Current password and new password are required',
                'telugu_message': 'ప్రస్తుత పాస్‌వర్డ్ మరియు కొత్త పాస్‌వర్డ్ అవసరం'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'error': 'New password must be at least 6 characters',
                'telugu_message': 'కొత్త పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({
                'error': 'Current password is incorrect',
                'telugu_message': 'ప్రస్తుత పాస్‌వర్డ్ తప్పు'
            }), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully!',
            'telugu_message': 'పాస్‌వర్డ్ విజయవంతంగా మార్చబడింది!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing password: {str(e)}")
        return jsonify({
            'error': 'Failed to change password',
            'telugu_message': 'పాస్‌వర్డ్ మార్చడంలో విఫలం'
        }), 500

@user_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_user_statistics():
    """Get comprehensive user learning statistics."""
    try:
        user_id = int(get_jwt_identity())
        
        # Get basic stats
        total_sessions = LearningSession.query.filter_by(user_id=user_id).count()
        total_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id).scalar() or 0
        
        total_vocabulary = VocabularyWord.query.filter_by(user_id=user_id).count()
        mastered_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id, 
            VocabularyWord.mastery_level >= 0.8  # Consider words with 80%+ mastery as "mastered"
        ).count()
        
        # Get weekly stats
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_sessions = LearningSession.query.filter(
            LearningSession.user_id == user_id,
            LearningSession.start_time >= week_ago
        ).count()
        
        weekly_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id,
                   LearningSession.start_time >= week_ago).scalar() or 0
        
        # Get streak info
        user = User.query.get(user_id)
        current_streak = user.profile.current_streak if user.profile else 0
        longest_streak = user.profile.longest_streak if user.profile else 0
        
        # Get goal progress
        current_goal = UserGoal.query.filter_by(user_id=user_id, is_active=True).first()
        
        today = date.today()
        today_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id,
                   func.date(LearningSession.start_time) == today).scalar() or 0
        
        goal_progress = 0
        if current_goal and current_goal.daily_time_goal_minutes > 0:
            goal_progress = min(100, (today_time / current_goal.daily_time_goal_minutes) * 100)
        
        statistics = {
            'overall': {
                'total_learning_sessions': total_sessions,
                'total_learning_time_minutes': total_time,
                'total_vocabulary_learned': total_vocabulary,
                'words_mastered': mastered_words,
                'current_streak_days': current_streak,
                'longest_streak_days': longest_streak
            },
            'this_week': {
                'sessions_completed': weekly_sessions,
                'time_spent_minutes': weekly_time,
                'average_session_length': round(weekly_time / weekly_sessions, 1) if weekly_sessions > 0 else 0
            },
            'today': {
                'time_spent_minutes': today_time,
                'goal_progress_percentage': round(goal_progress, 1),
                'daily_goal_minutes': current_goal.daily_time_goal_minutes if current_goal else 0
            },
            'vocabulary_breakdown': {
                'total_words': total_vocabulary,
                'mastered': mastered_words,
                'learning': VocabularyWord.query.filter(
                    VocabularyWord.user_id == user_id, 
                    VocabularyWord.mastery_level >= 0.3,
                    VocabularyWord.mastery_level < 0.8
                ).count(),  # Words with 30-79% mastery are "learning"
                'new': VocabularyWord.query.filter(
                    VocabularyWord.user_id == user_id, 
                    VocabularyWord.mastery_level < 0.3
                ).count()  # Words with <30% mastery are "new"
            }
        }
        
        return jsonify({
            'message': 'Statistics retrieved successfully!',
            'telugu_message': 'గణాంకాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'statistics': statistics
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to get statistics',
            'telugu_message': 'గణాంకాలు పొందడంలో విఫలం'
        }), 500

@user_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """
    Delete user account (soft delete).
    
    Expected JSON:
    {
        "password": "user_password",
        "confirmation": "DELETE_MY_ACCOUNT"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        password = data.get('password')
        confirmation = data.get('confirmation')
        
        if not password or confirmation != 'DELETE_MY_ACCOUNT':
            return jsonify({
                'error': 'Password and confirmation text required',
                'telugu_message': 'పాస్‌వర్డ్ మరియు నిర్ధారణ టెక్స్ట్ అవసరం'
            }), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Verify password
        if not check_password_hash(user.password_hash, password):
            return jsonify({
                'error': 'Incorrect password',
                'telugu_message': 'తప్పు పాస్‌వర్డ్'
            }), 400
        
        # Soft delete - mark as inactive
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Account deleted successfully',
            'telugu_message': 'ఖాతా విజయవంతంగా తొలగించబడింది'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting account: {str(e)}")
        return jsonify({
            'error': 'Failed to delete account',
            'telugu_message': 'ఖాతా తొలగించడంలో విఫలం'
        }), 500
def get_progress(user_id, path_id):
    """Get learning path progress for a user"""
    try:
        progress = progress_service.get_learning_path_progress(user_id, path_id)
        return jsonify({'progress': progress}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch progress', 'details': str(e)}), 500

@user_bp.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """Get user activity history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = progress_service.get_activity_history(user_id, limit)
        
        if isinstance(history, dict) and 'error' in history:
            return jsonify({'error': history['error']}), 500
        
        return jsonify({'history': history}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch history', 'details': str(e)}), 500

@user_bp.route('/learning-paths/<int:user_id>', methods=['GET'])
def get_learning_paths(user_id):
    """Get all learning paths for a user"""
    try:
        paths = progress_service.get_user_learning_paths(user_id)
        
        if isinstance(paths, dict) and 'error' in paths:
            return jsonify({'error': paths['error']}), 500
        
        return jsonify({'learning_paths': paths}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch learning paths', 'details': str(e)}), 500

@user_bp.route('/learning-paths', methods=['POST'])
def create_learning_path():
    """Create a new learning path"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        title = data['title'].strip()
        description = data['description'].strip()
        difficulty_level = data.get('difficulty_level', 'beginner')
        
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate difficulty level
        if difficulty_level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid difficulty level'}), 400
        
        learning_path = progress_service.create_learning_path(
            user_id, title, description, difficulty_level
        )
        
        return jsonify({
            'message': 'Learning path created successfully',
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'description': learning_path.description,
                'difficulty_level': learning_path.difficulty_level,
                'created_at': learning_path.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create learning path', 'details': str(e)}), 500

@user_bp.route('/activity-completion', methods=['POST'])
def log_activity_completion():
    """Log activity completion and update user progress"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'activity_id', 'score', 'max_score']
        for field in required_fields:
            if data.get(field) is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        activity_id = data['activity_id']
        score = data['score']
        max_score = data['max_score']
        user_response = data.get('user_response', {})
        time_spent_minutes = data.get('time_spent_minutes')
        feedback_provided = data.get('feedback_provided')
        
        # Log the activity completion
        activity_log = progress_service.update_user_activity_log(
            user_id, activity_id, score, max_score, user_response, 
            time_spent_minutes, feedback_provided
        )
        
        # Check for new achievements
        new_badges = gamification_service.check_for_new_achievements(user_id)
        
        # Update streak
        gamification_service.update_streak(user_id)
        
        return jsonify({
            'message': 'Activity completion logged successfully',
            'activity_log_id': activity_log.id,
            'new_badges': new_badges,
            'percentage': round((score / max_score) * 100, 2) if max_score > 0 else 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to log activity completion', 'details': str(e)}), 500

@user_bp.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard(user_id):
    """Get comprehensive dashboard data for a user"""
    try:
        # Get profile
        profile = progress_service.get_user_profile(user_id)
        if not profile or 'error' in profile:
            return jsonify({'error': 'User not found'}), 404
        
        # Get recent activity
        recent_activities = progress_service.get_activity_history(user_id, 5)
        
        # Get learning paths
        learning_paths = progress_service.get_user_learning_paths(user_id)
        
        # Get badges
        badges = gamification_service.get_user_badges(user_id)
        
        # Get daily challenge status
        daily_challenge = gamification_service.get_daily_challenge_status(user_id)
        
        return jsonify({
            'dashboard': {
                'profile': profile,
                'recent_activities': recent_activities,
                'learning_paths': learning_paths,
                'badges': badges,
                'daily_challenge': daily_challenge
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch dashboard', 'details': str(e)}), 500
