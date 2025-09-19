
from flask import Blueprint, jsonify, request
from app.services.progress_service import ProgressService
from app.services.gamification_service import GamificationService
from app.models import db, User, LearningPath

user_bp = Blueprint('user', __name__)
progress_service = ProgressService()
gamification_service = GamificationService()

@user_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile with statistics"""
    try:
        profile = progress_service.get_user_profile(user_id)
        if not profile:
            return jsonify({'error': 'User not found'}), 404
        
        if 'error' in profile:
            return jsonify({'error': profile['error']}), 500
        
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch profile', 'details': str(e)}), 500

@user_bp.route('/progress/<int:user_id>/<int:path_id>', methods=['GET'])
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
