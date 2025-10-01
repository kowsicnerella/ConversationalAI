
from flask import Blueprint, request, jsonify
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db, Activity, LearningPath, UserActivityLog
from flask_jwt_extended import jwt_required, get_jwt_identity
import base64
import io
from PIL import Image
from datetime import datetime, timedelta

activity_bp = Blueprint('activity', __name__)
activity_service = ActivityGeneratorService()

@activity_bp.route('/generate/quiz', methods=['POST'])
def generate_quiz():
    """Generate a quiz activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        quiz_content = activity_service.generate_quiz(topic, level)
        
        if 'error' in quiz_content:
            return jsonify({'error': 'Failed to generate quiz', 'details': quiz_content}), 500
        
        return jsonify({
            'activity_type': 'quiz',
            'topic': topic,
            'level': level,
            'content': quiz_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Quiz generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/flashcards', methods=['POST'])
def generate_flashcards():
    """Generate flashcard activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        flashcard_content = activity_service.generate_flashcards(topic, level)
        
        if 'error' in flashcard_content:
            return jsonify({'error': 'Failed to generate flashcards', 'details': flashcard_content}), 500
        
        return jsonify({
            'activity_type': 'flashcard',
            'topic': topic,
            'level': level,
            'content': flashcard_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Flashcard generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/reading', methods=['POST'])
def generate_reading():
    """Generate reading comprehension activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        reading_content = activity_service.generate_text_reading(topic, level)
        
        if 'error' in reading_content:
            return jsonify({'error': 'Failed to generate reading', 'details': reading_content}), 500
        
        return jsonify({
            'activity_type': 'reading',
            'topic': topic,
            'level': level,
            'content': reading_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Reading generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/writing-prompt', methods=['POST'])
def generate_writing_prompt():
    """Generate writing practice prompt"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        prompt_content = activity_service.generate_writing_practice_prompt(topic, level)
        
        if 'error' in prompt_content:
            return jsonify({'error': 'Failed to generate writing prompt', 'details': prompt_content}), 500
        
        return jsonify({
            'activity_type': 'writing',
            'topic': topic,
            'level': level,
            'content': prompt_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Writing prompt generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/role-play', methods=['POST'])
def generate_role_play():
    """Generate role-playing scenario"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        roleplay_content = activity_service.generate_role_playing_scenario(topic, level)
        
        if 'error' in roleplay_content:
            return jsonify({'error': 'Failed to generate role-play scenario', 'details': roleplay_content}), 500
        
        return jsonify({
            'activity_type': 'role_play',
            'topic': topic,
            'level': level,
            'content': roleplay_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Role-play generation failed', 'details': str(e)}), 500

@activity_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for vocabulary learning"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({'error': 'Invalid image data', 'details': str(e)}), 400
        
        analysis_content = activity_service.analyze_image_for_learning(image)
        
        if 'error' in analysis_content:
            return jsonify({'error': 'Failed to analyze image', 'details': analysis_content}), 500
        
        return jsonify({
            'activity_type': 'image_recognition',
            'content': analysis_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Image analysis failed', 'details': str(e)}), 500

@activity_bp.route('/chat', methods=['POST'])
def chat_with_tutor():
    """Chat with AI English tutor"""
    try:
        data = request.get_json()
        
        user_message = data.get('message', '').strip()
        message_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = activity_service.generate_general_chat_response(message_history, user_message)
        
        return jsonify({
            'activity_type': 'chat',
            'user_message': user_message,
            'tutor_response': response
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Chat failed', 'details': str(e)}), 500

@activity_bp.route('/feedback', methods=['POST'])
def get_writing_feedback():
    """Get feedback on user's English writing"""
    try:
        data = request.get_json()
        
        user_writing = data.get('text', '').strip()
        
        if not user_writing:
            return jsonify({'error': 'Text is required for feedback'}), 400
        
        feedback = activity_service.get_feedback_on_writing(user_writing)
        
        if 'error' in feedback:
            return jsonify({'error': 'Failed to generate feedback', 'details': feedback}), 500
        
        return jsonify({
            'activity_type': 'writing_feedback',
            'original_text': user_writing,
            'feedback': feedback
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Feedback generation failed', 'details': str(e)}), 500

@activity_bp.route('/save', methods=['POST'])
def save_activity():
    """Save a generated activity to a learning path"""
    try:
        data = request.get_json()
        
        required_fields = ['path_id', 'activity_type', 'title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        path_id = data['path_id']
        activity_type = data['activity_type']
        title = data['title'].strip()
        content = data['content']
        difficulty_level = data.get('difficulty_level', 'beginner')
        points_reward = data.get('points_reward', 10)
        estimated_duration = data.get('estimated_duration_minutes', 10)
        
        # Validate learning path exists
        learning_path = LearningPath.query.get(path_id)
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        # Get next order in path
        last_activity = Activity.query.filter_by(path_id=path_id).order_by(Activity.order_in_path.desc()).first()
        order_in_path = (last_activity.order_in_path + 1) if last_activity else 1
        
        # Create activity
        activity = Activity(
            path_id=path_id,
            activity_type=activity_type,
            title=title,
            content=content,
            difficulty_level=difficulty_level,
            order_in_path=order_in_path,
            estimated_duration_minutes=estimated_duration,
            points_reward=points_reward
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Activity saved successfully',
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'order_in_path': activity.order_in_path,
                'created_at': activity.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save activity', 'details': str(e)}), 500

@activity_bp.route('/path/<int:path_id>', methods=['GET'])
def get_path_activities(path_id):
    """Get all activities in a learning path"""
    try:
        learning_path = LearningPath.query.get(path_id)
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        activities = Activity.query.filter_by(path_id=path_id).order_by(Activity.order_in_path).all()
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'order_in_path': activity.order_in_path,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'content': activity.content
            })
        
        return jsonify({
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'description': learning_path.description
            },
            'activities': activity_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch activities', 'details': str(e)}), 500

# ===== ACTIVITY MANAGEMENT ENDPOINTS =====

@activity_bp.route('/user-activities', methods=['GET'])
@jwt_required()
def get_user_activities():
    """Get all activities for the current user with progress tracking"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        learning_path_id = request.args.get('learning_path_id', type=int)
        activity_type = request.args.get('activity_type')
        difficulty = request.args.get('difficulty')
        status = request.args.get('status')  # completed, in-progress, not-started
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Build query
        query = Activity.query
        
        if learning_path_id:
            query = query.filter(Activity.learning_path_id == learning_path_id)
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        if difficulty:
            query = query.filter(Activity.difficulty_level == difficulty)
        
        # Get activities with pagination
        activities = query.order_by(Activity.order_in_path).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get user's completed activities
        completed_logs = UserActivityLog.query.filter_by(user_id=user_id).all()
        completed_activity_ids = {log.activity_id: log for log in completed_logs}
        
        activity_list = []
        for activity in activities.items:
            completion_log = completed_activity_ids.get(activity.id)
            
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'order_in_path': activity.order_in_path,
                'learning_path_id': activity.learning_path_id,
                'status': 'completed' if completion_log else 'not-started',
                'completion_data': {
                    'completed_at': completion_log.completed_at.isoformat() if completion_log else None,
                    'score': completion_log.score if completion_log else None,
                    'max_score': completion_log.max_score if completion_log else None,
                    'time_spent_minutes': completion_log.time_spent_minutes if completion_log else None,
                    'attempt_number': completion_log.attempt_number if completion_log else 0
                }
            }
            
            # Filter by status if requested
            if status and activity_data['status'] != status:
                continue
                
            activity_list.append(activity_data)
        
        return jsonify({
            'message': 'User activities retrieved successfully!',
            'telugu_message': 'వినియోగదారు కార్యకలాపాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'activities': activity_list,
            'pagination': {
                'page': activities.page,
                'pages': activities.pages,
                'per_page': activities.per_page,
                'total': activities.total,
                'has_next': activities.has_next,
                'has_prev': activities.has_prev
            },
            'filters': {
                'learning_path_id': learning_path_id,
                'activity_type': activity_type,
                'difficulty': difficulty,
                'status': status
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user activities',
            'telugu_message': 'వినియోగదారు కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get user activities',
            'telugu_message': 'వినియోగదారు కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/details', methods=['GET'])
@jwt_required()
def get_activity_details(activity_id):
    """Get detailed information about a specific activity"""
    try:
        user_id = int(get_jwt_identity())
        
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        # Get user's completion log for this activity
        completion_log = UserActivityLog.query.filter_by(
            user_id=user_id, activity_id=activity_id
        ).first()
        
        # Get learning path info
        learning_path = LearningPath.query.get(activity.learning_path_id)
        
        activity_data = {
            'id': activity.id,
            'title': activity.title,
            'activity_type': activity.activity_type,
            'content': activity.content,
            'difficulty_level': activity.difficulty_level,
            'estimated_duration_minutes': activity.estimated_duration_minutes,
            'points_reward': activity.points_reward,
            'order_in_path': activity.order_in_path,
            'created_at': activity.created_at.isoformat(),
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'category': learning_path.category
            } if learning_path else None,
            'user_progress': {
                'is_completed': bool(completion_log),
                'completed_at': completion_log.completed_at.isoformat() if completion_log else None,
                'score': completion_log.score if completion_log else None,
                'max_score': completion_log.max_score if completion_log else None,
                'time_spent_minutes': completion_log.time_spent_minutes if completion_log else None,
                'attempt_number': completion_log.attempt_number if completion_log else 0,
                'user_response': completion_log.user_response if completion_log else None,
                'feedback_provided': completion_log.feedback_provided if completion_log else None
            }
        }
        
        return jsonify({
            'message': 'Activity details retrieved successfully!',
            'telugu_message': 'కార్యకలాప వివరాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'activity': activity_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get activity details',
            'telugu_message': 'కార్యకలాప వివరాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get activity details',
            'telugu_message': 'కార్యకలాప వివరాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/submit', methods=['POST'])
def submit_activity_answer(activity_id):
    """Submit answers for an activity and get feedback"""
    try:
        from flask_jwt_extended import jwt_required, get_jwt_identity
        from app.models import UserActivityLog
        from datetime import datetime
        
        @jwt_required()
        def protected_route():
            user_id = int(get_jwt_identity())
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'No data provided',
                    'telugu_message': 'డేటా అందించబడలేదు'
                }), 400
            
            activity = Activity.query.get(activity_id)
            if not activity:
                return jsonify({
                    'error': 'Activity not found',
                    'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
                }), 404
            
            user_answers = data.get('answers', {})
            time_spent = data.get('time_spent_minutes', 0)
            
            # Use activity generator service to evaluate answers
            evaluation_result = activity_service.evaluate_activity_submission(
                activity.content, user_answers, activity.activity_type
            )
            
            # Calculate score
            score = evaluation_result.get('score', 0)
            max_score = evaluation_result.get('max_score', 100)
            feedback = evaluation_result.get('feedback', {})
            
            # Check if user has already completed this activity
            existing_log = UserActivityLog.query.filter_by(
                user_id=user_id, activity_id=activity_id
            ).first()
            
            if existing_log:
                # Update existing log with new attempt
                existing_log.attempt_number += 1
                existing_log.score = max(existing_log.score or 0, score)  # Keep best score
                existing_log.user_response = user_answers
                existing_log.feedback_provided = feedback
                existing_log.time_spent_minutes = (existing_log.time_spent_minutes or 0) + time_spent
                existing_log.completed_at = datetime.utcnow()
            else:
                # Create new activity log
                activity_log = UserActivityLog(
                    user_id=user_id,
                    activity_id=activity_id,
                    learning_path_id=activity.learning_path_id,
                    score=score,
                    max_score=max_score,
                    time_spent_minutes=time_spent,
                    user_response=user_answers,
                    feedback_provided=feedback,
                    attempt_number=1,
                    completed_at=datetime.utcnow()
                )
                db.session.add(activity_log)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Activity submitted successfully!',
                'telugu_message': 'కార్యకલాపం విజయవంతంగా సమర్పించబడింది!',
                'evaluation': {
                    'score': score,
                    'max_score': max_score,
                    'percentage': round((score / max_score * 100), 1) if max_score > 0 else 0,
                    'feedback': feedback,
                    'points_earned': activity.points_reward if score >= (max_score * 0.7) else int(activity.points_reward * 0.5)
                },
                'user_progress': {
                    'attempt_number': existing_log.attempt_number if existing_log else 1,
                    'best_score': max(existing_log.score or 0, score) if existing_log else score,
                    'total_time_spent': (existing_log.time_spent_minutes or 0) + time_spent if existing_log else time_spent
                }
            }), 200
            
    except Exception as e:
        return jsonify({
            'error': 'Failed to submit activity',
            'telugu_message': 'కార్యకలాపం సమర్పించడంలో విఫలం',
            'details': str(e)
        }), 500

# ===== LEARNING PATH ACTIVITY MANAGEMENT =====

@activity_bp.route('/learning-path/<int:learning_path_id>/activities', methods=['GET'])
@jwt_required()
def get_learning_path_activities(learning_path_id):
    """Get all activities for a specific learning path with user progress"""
    try:
        user_id = int(get_jwt_identity())
        
        # Check if learning path exists
        learning_path = LearningPath.query.get(learning_path_id)
        if not learning_path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        # Get activities in order
        activities = Activity.query.filter_by(learning_path_id=learning_path_id)\
                                 .order_by(Activity.order_in_path).all()
        
        # Get user's progress for these activities
        completed_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                             .filter(UserActivityLog.activity_id.in_([a.id for a in activities]))\
                                             .all()
        completed_dict = {log.activity_id: log for log in completed_logs}
        
        activity_list = []
        for activity in activities:
            completion_log = completed_dict.get(activity.id)
            
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'order_in_path': activity.order_in_path,
                'is_unlocked': True,  # We'll implement unlock logic based on previous activities
                'progress': {
                    'is_completed': bool(completion_log),
                    'score': completion_log.score if completion_log else None,
                    'max_score': completion_log.max_score if completion_log else None,
                    'percentage': round((completion_log.score / completion_log.max_score * 100), 1) 
                                if completion_log and completion_log.max_score > 0 else 0,
                    'attempts': completion_log.attempt_number if completion_log else 0,
                    'completed_at': completion_log.completed_at.isoformat() if completion_log else None
                }
            }
            activity_list.append(activity_data)
        
        # Calculate overall progress
        completed_count = len([a for a in activity_list if a['progress']['is_completed']])
        total_count = len(activity_list)
        overall_progress = round((completed_count / total_count * 100), 1) if total_count > 0 else 0
        
        return jsonify({
            'message': 'Learning path activities retrieved successfully!',
            'telugu_message': 'అభ్యాస మార్గ కార్యకలాపాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'description': learning_path.description,
                'category': learning_path.category,
                'difficulty_level': learning_path.difficulty_level
            },
            'activities': activity_list,
            'progress_summary': {
                'completed_activities': completed_count,
                'total_activities': total_count,
                'completion_percentage': overall_progress,
                'estimated_total_time': sum(a['estimated_duration_minutes'] for a in activity_list),
                'time_spent': sum(log.time_spent_minutes or 0 for log in completed_logs)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get learning path activities',
            'telugu_message': 'అభ్యాస మార్గ కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/next-activity', methods=['GET'])
@jwt_required()
def get_next_activity():
    """Get the next recommended activity for the user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get user's enrolled learning paths
        from app.models.user import User
        user = User.query.get(user_id)
        if not user or not user.enrolled_paths:
            return jsonify({
                'error': 'No enrolled learning paths found',
                'telugu_message': 'నమోదు చేసిన అభ్యాస మార్గాలు కనుగొనబడలేదు'
            }), 404
        
        # Find next incomplete activity from enrolled paths
        next_activity = None
        learning_path_info = None
        
        for learning_path in user.enrolled_paths:
            # Get activities in order
            activities = Activity.query.filter_by(learning_path_id=learning_path.id)\
                                     .order_by(Activity.order_in_path).all()
            
            # Find first incomplete activity
            for activity in activities:
                completion_log = UserActivityLog.query.filter_by(
                    user_id=user_id, activity_id=activity.id
                ).first()
                
                if not completion_log:
                    next_activity = activity
                    learning_path_info = learning_path
                    break
            
            if next_activity:
                break
        
        if not next_activity:
            return jsonify({
                'message': 'All activities completed! Great job!',
                'telugu_message': 'అన్ని కార్యకలాపాలు పూర్తయ్యాయి! అద్భుతం!',
                'next_activity': None
            }), 200
        
        return jsonify({
            'message': 'Next activity found!',
            'telugu_message': 'తదుపరి కార్యకలాపం కనుగొనబడింది!',
            'next_activity': {
                'id': next_activity.id,
                'title': next_activity.title,
                'activity_type': next_activity.activity_type,
                'difficulty_level': next_activity.difficulty_level,
                'estimated_duration_minutes': next_activity.estimated_duration_minutes,
                'points_reward': next_activity.points_reward,
                'order_in_path': next_activity.order_in_path,
                'learning_path': {
                    'id': learning_path_info.id,
                    'title': learning_path_info.title,
                    'category': learning_path_info.category
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get next activity',
            'telugu_message': 'తదుపరి కార్యకలాపం పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/user-progress/summary', methods=['GET'])
@jwt_required()
def get_user_activity_summary():
    """Get comprehensive activity progress summary for the user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get all user's activity logs
        logs = UserActivityLog.query.filter_by(user_id=user_id).all()
        
        if not logs:
            return jsonify({
                'message': 'No activity progress found',
                'telugu_message': 'కార్యకలాప పురోగతి కనుగొనబడలేదు',
                'summary': {
                    'total_activities_completed': 0,
                    'total_time_spent_minutes': 0,
                    'average_score_percentage': 0,
                    'total_points_earned': 0,
                    'activity_type_breakdown': {},
                    'difficulty_level_breakdown': {},
                    'recent_activity': None
                }
            }), 200
        
        # Calculate summary statistics
        total_completed = len(logs)
        total_time = sum(log.time_spent_minutes or 0 for log in logs)
        
        # Calculate average score
        scores_with_max = [(log.score, log.max_score) for log in logs if log.score is not None and log.max_score and log.max_score > 0]
        avg_percentage = 0
        if scores_with_max:
            percentages = [(score / max_score * 100) for score, max_score in scores_with_max]
            avg_percentage = round(sum(percentages) / len(percentages), 1)
        
        # Calculate total points (assuming full points for 70%+ scores, half points otherwise)
        total_points = 0
        activity_ids = [log.activity_id for log in logs]
        activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()
        activity_points = {a.id: a.points_reward for a in activities}
        
        for log in logs:
            if log.score is not None and log.max_score and log.max_score > 0:
                percentage = (log.score / log.max_score)
                points = activity_points.get(log.activity_id, 10)
                total_points += points if percentage >= 0.7 else int(points * 0.5)
        
        # Activity type breakdown
        activity_types = {}
        for log in logs:
            activity = next((a for a in activities if a.id == log.activity_id), None)
            if activity:
                activity_type = activity.activity_type
                if activity_type not in activity_types:
                    activity_types[activity_type] = {'count': 0, 'avg_score': 0}
                activity_types[activity_type]['count'] += 1
        
        # Difficulty level breakdown
        difficulty_levels = {}
        for log in logs:
            activity = next((a for a in activities if a.id == log.activity_id), None)
            if activity:
                difficulty = activity.difficulty_level
                if difficulty not in difficulty_levels:
                    difficulty_levels[difficulty] = {'count': 0, 'avg_score': 0}
                difficulty_levels[difficulty]['count'] += 1
        
        # Recent activity
        recent_log = max(logs, key=lambda x: x.completed_at)
        recent_activity_info = next((a for a in activities if a.id == recent_log.activity_id), None)
        
        recent_activity = {
            'activity_title': recent_activity_info.title if recent_activity_info else 'Unknown',
            'activity_type': recent_activity_info.activity_type if recent_activity_info else 'Unknown',
            'score': recent_log.score,
            'max_score': recent_log.max_score,
            'completed_at': recent_log.completed_at.isoformat()
        } if recent_activity_info else None
        
        return jsonify({
            'message': 'Activity summary retrieved successfully!',
            'telugu_message': 'కార్యకలాప సారాంశం విజయవంతంగా తీసుకోబడింది!',
            'summary': {
                'total_activities_completed': total_completed,
                'total_time_spent_minutes': total_time,
                'average_score_percentage': avg_percentage,
                'total_points_earned': total_points,
                'activity_type_breakdown': activity_types,
                'difficulty_level_breakdown': difficulty_levels,
                'recent_activity': recent_activity
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get activity summary',
            'telugu_message': 'కార్యకలాప సారాంశం పొందడంలో విఫలం',
            'details': str(e)
        }), 500

# ========== NEW ACTIVITY MANAGEMENT ENDPOINTS ==========

@activity_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_activities():
    """
    Get all activities with comprehensive filtering options.
    Allows browsing and revisiting all generated activities.
    """
    try:
        # Get filter parameters
        activity_type = request.args.get('activity_type')  # quiz, flashcard, reading, writing, role_play
        difficulty_level = request.args.get('difficulty_level')  # beginner, intermediate, advanced
        topic = request.args.get('topic')  # filter by title/content topic
        learning_path_id = request.args.get('learning_path_id', type=int)
        created_after = request.args.get('created_after')  # ISO format date
        created_before = request.args.get('created_before')  # ISO format date
        min_duration = request.args.get('min_duration', type=int)
        max_duration = request.args.get('max_duration', type=int)
        sort_by = request.args.get('sort_by', 'created_at')  # created_at, title, difficulty_level, duration
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
        
        # Build query
        query = Activity.query
        
        # Apply filters
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        if difficulty_level:
            query = query.filter(Activity.difficulty_level == difficulty_level)
        
        if topic:
            query = query.filter(Activity.title.contains(topic))
        
        if learning_path_id:
            query = query.filter(Activity.learning_path_id == learning_path_id)
        
        if created_after:
            try:
                after_date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                query = query.filter(Activity.created_at >= after_date)
            except ValueError:
                pass
        
        if created_before:
            try:
                before_date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                query = query.filter(Activity.created_at <= before_date)
            except ValueError:
                pass
        
        if min_duration:
            query = query.filter(Activity.estimated_duration_minutes >= min_duration)
        
        if max_duration:
            query = query.filter(Activity.estimated_duration_minutes <= max_duration)
        
        # Apply sorting
        if hasattr(Activity, sort_by):
            order_attr = getattr(Activity, sort_by)
            if sort_order == 'desc':
                query = query.order_by(order_attr.desc())
            else:
                query = query.order_by(order_attr.asc())
        else:
            query = query.order_by(Activity.created_at.desc())
        
        # Paginate
        paginated_activities = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format activities
        activities = []
        for activity in paginated_activities.items:
            activities.append({
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'learning_path_id': activity.learning_path_id,
                'created_at': activity.created_at.isoformat(),
                'content_preview': str(activity.content)[:200] + "..." if len(str(activity.content)) > 200 else str(activity.content)
            })
        
        return jsonify({
            'success': True,
            'message': 'Activities retrieved successfully',
            'telugu_message': 'కార్యకలాపాలు విజయవంతంగా పొందబడ్డాయి',
            'data': {
                'activities': activities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': paginated_activities.pages,
                    'total_items': paginated_activities.total,
                    'has_next': paginated_activities.has_next,
                    'has_prev': paginated_activities.has_prev
                },
                'applied_filters': {
                    'activity_type': activity_type,
                    'difficulty_level': difficulty_level,
                    'topic': topic,
                    'learning_path_id': learning_path_id,
                    'created_after': created_after,
                    'created_before': created_before,
                    'min_duration': min_duration,
                    'max_duration': max_duration,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve activities',
            'telugu_message': 'కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/by-type/<activity_type>', methods=['GET'])
@jwt_required()
def get_activities_by_type(activity_type):
    """
    Get activities filtered by specific type for better categorization.
    """
    try:
        # Validate activity type
        valid_types = ['quiz', 'flashcard', 'reading', 'writing', 'role_play', 'image_recognition']
        if activity_type not in valid_types:
            return jsonify({
                'error': f'Invalid activity type. Must be one of: {", ".join(valid_types)}',
                'telugu_message': 'చెల్లని కార్యకలాప రకం',
                'valid_types': valid_types
            }), 400
        
        # Get optional filters
        difficulty_level = request.args.get('difficulty_level')
        learning_path_id = request.args.get('learning_path_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build query
        query = Activity.query.filter(Activity.activity_type == activity_type)
        
        if difficulty_level:
            query = query.filter(Activity.difficulty_level == difficulty_level)
        
        if learning_path_id:
            query = query.filter(Activity.learning_path_id == learning_path_id)
        
        # Order by creation date (newest first)
        query = query.order_by(Activity.created_at.desc())
        
        # Paginate
        paginated_activities = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format activities with type-specific content
        activities = []
        for activity in paginated_activities.items:
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'learning_path_id': activity.learning_path_id,
                'created_at': activity.created_at.isoformat(),
                'content': activity.content
            }
            
            # Add type-specific summaries
            if activity_type == 'quiz' and activity.content:
                activity_data['question_count'] = len(activity.content.get('questions', []))
            elif activity_type == 'flashcard' and activity.content:
                activity_data['card_count'] = len(activity.content.get('flashcards', []))
            elif activity_type == 'reading' and activity.content:
                activity_data['word_count'] = len(activity.content.get('passage', '').split()) if activity.content.get('passage') else 0
            
            activities.append(activity_data)
        
        return jsonify({
            'success': True,
            'message': f'{activity_type.title()} activities retrieved successfully',
            'telugu_message': f'{activity_type} కార్యకలాపాలు విజయవంతంగా పొందబడ్డాయి',
            'data': {
                'activity_type': activity_type,
                'activities': activities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': paginated_activities.pages,
                    'total_items': paginated_activities.total,
                    'has_next': paginated_activities.has_next,
                    'has_prev': paginated_activities.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve {activity_type} activities',
            'telugu_message': f'{activity_type} కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/my-generated', methods=['GET'])
@jwt_required()
def get_my_generated_activities():
    """
    Get all activities generated/accessed by the current user.
    Includes both completed and pending activities for personal library.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get filter parameters
        status = request.args.get('status')  # completed, pending, all
        activity_type = request.args.get('activity_type')
        difficulty_level = request.args.get('difficulty_level')
        days_back = request.args.get('days_back', type=int)  # Activities from last N days
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get user's activity logs with activities
        query = db.session.query(Activity, UserActivityLog).join(
            UserActivityLog, Activity.id == UserActivityLog.activity_id
        ).filter(UserActivityLog.user_id == current_user_id)
        
        # Apply filters
        if status == 'completed':
            query = query.filter(UserActivityLog.is_completed == True)
        elif status == 'pending':
            query = query.filter(UserActivityLog.is_completed == False)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        if difficulty_level:
            query = query.filter(Activity.difficulty_level == difficulty_level)
        
        if days_back:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(UserActivityLog.completed_at >= cutoff_date)
        
        # Order by most recent activity
        query = query.order_by(UserActivityLog.completed_at.desc())
        
        # Get total count for pagination
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        
        # Format results
        my_activities = []
        for activity, log in results:
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'created_at': activity.created_at.isoformat(),
                'user_progress': {
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                    'score': log.score,
                    'max_score': log.max_score,
                    'percentage': round((log.score / log.max_score * 100), 1) if log.score and log.max_score else None,
                    'time_spent_minutes': log.time_spent_minutes,
                    'is_completed': log.is_completed,
                    'attempt_number': log.attempt_number
                }
            }
            my_activities.append(activity_data)
        
        # Calculate summary statistics
        total_activities = len(my_activities)
        completed_activities = len([a for a in my_activities if a['user_progress']['is_completed']])
        completion_rate = round((completed_activities / total_activities * 100), 1) if total_activities > 0 else 0
        
        # Calculate average score
        scores = [a['user_progress']['percentage'] for a in my_activities if a['user_progress']['percentage'] is not None]
        average_score = round(sum(scores) / len(scores), 1) if scores else 0
        
        # Calculate total time spent
        time_spent = [a['user_progress']['time_spent_minutes'] for a in my_activities if a['user_progress']['time_spent_minutes']]
        total_time_spent = sum(time_spent) if time_spent else 0
        
        return jsonify({
            'success': True,
            'message': 'Your activities retrieved successfully',
            'telugu_message': 'మీ కార్యకలాపాలు విజయవంతంగా పొందబడ్డాయి',
            'data': {
                'activities': my_activities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'total_items': total_count,
                    'has_next': offset + per_page < total_count,
                    'has_prev': page > 1
                },
                'summary': {
                    'total_activities': total_activities,
                    'completed_activities': completed_activities,
                    'completion_rate_percentage': completion_rate,
                    'average_score_percentage': average_score,
                    'total_time_spent_minutes': total_time_spent
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve your activities',
            'telugu_message': 'మీ కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/update', methods=['PUT'])
@jwt_required()
def update_activity(activity_id):
    """
    Update an activity (title, content, difficulty, etc.)
    """
    try:
        # Get the activity
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        # Get update data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'telugu_message': 'డేటా అందించబడలేదు'
            }), 400
        
        # Update fields if provided
        if 'title' in data:
            activity.title = data['title']
        
        if 'content' in data:
            activity.content = data['content']
        
        if 'difficulty_level' in data:
            if data['difficulty_level'] in ['beginner', 'intermediate', 'advanced']:
                activity.difficulty_level = data['difficulty_level']
        
        if 'estimated_duration_minutes' in data:
            activity.estimated_duration_minutes = data['estimated_duration_minutes']
        
        if 'points_reward' in data:
            activity.points_reward = data['points_reward']
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity updated successfully',
            'telugu_message': 'కార్యకలాపం విజయవంతంగా నవీకరించబడింది',
            'data': {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'content': activity.content
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update activity',
            'telugu_message': 'కార్యకలాపం నవీకరించడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/delete', methods=['DELETE'])
@jwt_required()
def delete_activity(activity_id):
    """
    Delete an activity (and associated user logs)
    """
    try:
        # Get the activity
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        # Store activity info for response
        activity_info = {
            'id': activity.id,
            'title': activity.title,
            'activity_type': activity.activity_type
        }
        
        # Delete the activity (cascade will handle user logs)
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity deleted successfully',
            'telugu_message': 'కార్యకలాపం విజయవంతంగా తొలగించబడింది',
            'data': {
                'deleted_activity': activity_info
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to delete activity',
            'telugu_message': 'కార్యకలాపం తొలగించడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/bookmark', methods=['POST'])
@jwt_required()
def bookmark_activity(activity_id):
    """
    Bookmark/favorite an activity for easy access
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if activity exists
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        # For now, we'll use the user_response field in UserActivityLog to store bookmark info
        # Check if user already has a log for this activity
        existing_log = UserActivityLog.query.filter_by(
            user_id=current_user_id,
            activity_id=activity_id
        ).first()
        
        if existing_log:
            # Update existing log to add bookmark
            if not existing_log.user_response:
                existing_log.user_response = {}
            existing_log.user_response['bookmarked'] = True
            existing_log.user_response['bookmarked_at'] = datetime.utcnow().isoformat()
        else:
            # Create new log entry for bookmark
            new_log = UserActivityLog(
                user_id=current_user_id,
                activity_id=activity_id,
                learning_path_id=activity.learning_path_id,
                user_response={'bookmarked': True, 'bookmarked_at': datetime.utcnow().isoformat()},
                is_completed=False,
                completed_at=datetime.utcnow()
            )
            db.session.add(new_log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity bookmarked successfully',
            'telugu_message': 'కార్యకలాపం విజయవంతంగా బుక్‌మార్క్ చేయబడింది',
            'data': {
                'activity_id': activity_id,
                'activity_title': activity.title,
                'bookmarked': True,
                'bookmarked_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to bookmark activity',
            'telugu_message': 'కార్యకలాపం బుక్‌మార్క్ చేయడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/<int:activity_id>/unbookmark', methods=['DELETE'])
@jwt_required()
def unbookmark_activity(activity_id):
    """
    Remove bookmark from an activity
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Find the user's log for this activity
        user_log = UserActivityLog.query.filter_by(
            user_id=current_user_id,
            activity_id=activity_id
        ).first()
        
        if not user_log or not user_log.user_response or not user_log.user_response.get('bookmarked'):
            return jsonify({
                'error': 'Activity is not bookmarked',
                'telugu_message': 'కార్యకలాపం బుక్‌మార్క్ చేయబడలేదు'
            }), 404
        
        # Remove bookmark
        user_log.user_response['bookmarked'] = False
        user_log.user_response['unbookmarked_at'] = datetime.utcnow().isoformat()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Activity bookmark removed successfully',
            'telugu_message': 'కార్యకలాపం బుక్‌మార్క్ విజయవంతంగా తొలగించబడింది',
            'data': {
                'activity_id': activity_id,
                'bookmarked': False
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to remove bookmark',
            'telugu_message': 'బుక్‌మార్క్ తొలగించడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/bookmarks', methods=['GET'])
@jwt_required()
def get_bookmarked_activities():
    """
    Get all bookmarked activities for the current user
    """
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Get bookmarked activities
        query = db.session.query(Activity, UserActivityLog).join(
            UserActivityLog, Activity.id == UserActivityLog.activity_id
        ).filter(
            UserActivityLog.user_id == current_user_id,
            UserActivityLog.user_response.contains({'bookmarked': True})
        ).order_by(UserActivityLog.completed_at.desc())
        
        # Paginate
        total_count = query.count()
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        
        # Format results
        bookmarked_activities = []
        for activity, log in results:
            bookmarked_activities.append({
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'created_at': activity.created_at.isoformat(),
                'bookmarked_at': log.user_response.get('bookmarked_at') if log.user_response else None
            })
        
        return jsonify({
            'success': True,
            'message': 'Bookmarked activities retrieved successfully',
            'telugu_message': 'బుక్‌మార్క్ చేసిన కార్యకలాపాలు విజయవంతంగా పొందబడ్డాయి',
            'data': {
                'bookmarked_activities': bookmarked_activities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'total_items': total_count,
                    'has_next': offset + per_page < total_count,
                    'has_prev': page > 1
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve bookmarked activities',
            'telugu_message': 'బుక్‌మార్క్ చేసిన కార్యకలాపాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@activity_bp.route('/search', methods=['GET'])
@jwt_required()
def search_activities():
    """
    Advanced search endpoint with comprehensive filtering and keyword search
    """
    try:
        # Get search parameters
        keyword = request.args.get('keyword', '').strip()  # Search in title and content
        activity_type = request.args.get('activity_type')
        difficulty_level = request.args.get('difficulty_level')
        learning_path_id = request.args.get('learning_path_id', type=int)
        min_duration = request.args.get('min_duration', type=int)
        max_duration = request.args.get('max_duration', type=int)
        min_points = request.args.get('min_points', type=int)
        max_points = request.args.get('max_points', type=int)
        created_after = request.args.get('created_after')
        created_before = request.args.get('created_before')
        completion_status = request.args.get('completion_status')  # completed, not_completed, bookmarked
        user_score_min = request.args.get('user_score_min', type=int)  # Minimum percentage score
        user_score_max = request.args.get('user_score_max', type=int)  # Maximum percentage score
        sort_by = request.args.get('sort_by', 'relevance')  # relevance, created_at, title, difficulty, duration, points
        sort_order = request.args.get('sort_order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        current_user_id = get_jwt_identity()
        
        # Build base query
        if completion_status in ['completed', 'not_completed', 'bookmarked']:
            # Query with user activity logs
            query = db.session.query(Activity, UserActivityLog).join(
                UserActivityLog, Activity.id == UserActivityLog.activity_id
            ).filter(UserActivityLog.user_id == current_user_id)
            
            if completion_status == 'completed':
                query = query.filter(UserActivityLog.is_completed == True)
            elif completion_status == 'not_completed':
                query = query.filter(UserActivityLog.is_completed == False)
            elif completion_status == 'bookmarked':
                query = query.filter(UserActivityLog.user_response.contains({'bookmarked': True}))
        else:
            # Query activities only
            query = Activity.query
        
        # Apply keyword search
        if keyword:
            keyword_filter = f"%{keyword}%"
            if completion_status in ['completed', 'not_completed', 'bookmarked']:
                query = query.filter(
                    Activity.title.ilike(keyword_filter) |
                    Activity.content.astext.ilike(keyword_filter)
                )
            else:
                query = query.filter(
                    Activity.title.ilike(keyword_filter) |
                    Activity.content.astext.ilike(keyword_filter)
                )
        
        # Apply other filters
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        if difficulty_level:
            query = query.filter(Activity.difficulty_level == difficulty_level)
        
        if learning_path_id:
            query = query.filter(Activity.learning_path_id == learning_path_id)
        
        if min_duration:
            query = query.filter(Activity.estimated_duration_minutes >= min_duration)
        
        if max_duration:
            query = query.filter(Activity.estimated_duration_minutes <= max_duration)
        
        if min_points:
            query = query.filter(Activity.points_reward >= min_points)
        
        if max_points:
            query = query.filter(Activity.points_reward <= max_points)
        
        if created_after:
            try:
                after_date = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
                query = query.filter(Activity.created_at >= after_date)
            except ValueError:
                pass
        
        if created_before:
            try:
                before_date = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
                query = query.filter(Activity.created_at <= before_date)
            except ValueError:
                pass
        
        # Apply user score filters (only for user activity queries)
        if completion_status in ['completed', 'not_completed', 'bookmarked']:
            if user_score_min:
                query = query.filter(
                    (UserActivityLog.score * 100 / UserActivityLog.max_score) >= user_score_min
                ).filter(UserActivityLog.max_score > 0)
            
            if user_score_max:
                query = query.filter(
                    (UserActivityLog.score * 100 / UserActivityLog.max_score) <= user_score_max
                ).filter(UserActivityLog.max_score > 0)
        
        # Apply sorting
        if sort_by == 'relevance' and keyword:
            # Simple relevance scoring: title matches first, then content matches
            if completion_status in ['completed', 'not_completed', 'bookmarked']:
                query = query.order_by(
                    Activity.title.ilike(f"%{keyword}%").desc(),
                    Activity.created_at.desc()
                )
            else:
                query = query.order_by(
                    Activity.title.ilike(f"%{keyword}%").desc(),
                    Activity.created_at.desc()
                )
        else:
            # Standard sorting
            sort_attr = getattr(Activity, sort_by, None) if hasattr(Activity, sort_by) else Activity.created_at
            if sort_order == 'desc':
                query = query.order_by(sort_attr.desc())
            else:
                query = query.order_by(sort_attr.asc())
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        results = query.offset(offset).limit(per_page).all()
        
        # Format results
        search_results = []
        for result in results:
            if completion_status in ['completed', 'not_completed', 'bookmarked']:
                activity, log = result
                activity_data = {
                    'id': activity.id,
                    'title': activity.title,
                    'activity_type': activity.activity_type,
                    'difficulty_level': activity.difficulty_level,
                    'estimated_duration_minutes': activity.estimated_duration_minutes,
                    'points_reward': activity.points_reward,
                    'learning_path_id': activity.learning_path_id,
                    'created_at': activity.created_at.isoformat(),
                    'user_progress': {
                        'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                        'score': log.score,
                        'max_score': log.max_score,
                        'percentage': round((log.score / log.max_score * 100), 1) if log.score and log.max_score else None,
                        'time_spent_minutes': log.time_spent_minutes,
                        'is_completed': log.is_completed,
                        'is_bookmarked': log.user_response.get('bookmarked', False) if log.user_response else False
                    }
                }
            else:
                activity = result
                activity_data = {
                    'id': activity.id,
                    'title': activity.title,
                    'activity_type': activity.activity_type,
                    'difficulty_level': activity.difficulty_level,
                    'estimated_duration_minutes': activity.estimated_duration_minutes,
                    'points_reward': activity.points_reward,
                    'learning_path_id': activity.learning_path_id,
                    'created_at': activity.created_at.isoformat()
                }
            
            # Add keyword highlighting if keyword search was used
            if keyword:
                highlighted_title = activity.title.replace(
                    keyword, f"**{keyword}**"
                ) if keyword.lower() in activity.title.lower() else activity.title
                activity_data['highlighted_title'] = highlighted_title
            
            search_results.append(activity_data)
        
        return jsonify({
            'success': True,
            'message': f'Found {total_count} activities matching your search',
            'telugu_message': f'మీ శోధనకు సరిపోలే {total_count} కార్యకలాపాలు కనుగొనబడ్డాయి',
            'data': {
                'search_results': search_results,
                'search_parameters': {
                    'keyword': keyword,
                    'activity_type': activity_type,
                    'difficulty_level': difficulty_level,
                    'learning_path_id': learning_path_id,
                    'completion_status': completion_status,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                },
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_count + per_page - 1) // per_page,
                    'total_items': total_count,
                    'has_next': offset + per_page < total_count,
                    'has_prev': page > 1
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to search activities',
            'telugu_message': 'కార్యకలాపాలు శోధించడంలో విఫలం',
            'details': str(e)
        }), 500
