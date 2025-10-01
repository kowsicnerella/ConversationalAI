from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, LearningPath, Course, UserActivityLog, Activity
from app.services.activity_generator_service import ActivityGeneratorService
from datetime import datetime
from sqlalchemy import func
import json

courses_bp = Blueprint('courses', __name__)
activity_service = ActivityGeneratorService()

@courses_bp.route('/learning-paths', methods=['GET'])
@jwt_required()
def get_learning_paths():
    """
    Get available learning paths with user enrollment status.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', None)
        difficulty = request.args.get('difficulty', None)
        
        # Base query
        query = LearningPath.query.filter_by(is_active=True)
        
        # Apply filters
        if category:
            query = query.filter(LearningPath.category == category)
        if difficulty:
            query = query.filter(LearningPath.difficulty_level == difficulty)
        
        paths = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get user's enrolled paths
        user = User.query.get(user_id)
        enrolled_path_ids = [path.id for path in user.enrolled_paths] if user.enrolled_paths else []
        
        learning_paths = []
        for path in paths.items:
            # Calculate completion stats
            total_activities = Activity.query.filter_by(learning_path_id=path.id).count()
            completed_activities = UserActivityLog.query.filter_by(
                user_id=user_id,
                learning_path_id=path.id
            ).count() if path.id in enrolled_path_ids else 0
            
            completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            
            learning_paths.append({
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'category': path.category,
                'difficulty_level': path.difficulty_level,
                'estimated_duration_hours': path.estimated_duration_hours,
                'total_activities': total_activities,
                'is_enrolled': path.id in enrolled_path_ids,
                'completion_percentage': round(completion_percentage, 1),
                'completed_activities': completed_activities,
                'prerequisites': path.prerequisites or [],
                'learning_objectives': path.learning_objectives or [],
                'created_at': path.created_at.isoformat()
            })
        
        return jsonify({
            'message': 'Learning paths retrieved successfully!',
            'telugu_message': 'అభ్యాస మార్గాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'learning_paths': learning_paths,
            'pagination': {
                'page': paths.page,
                'per_page': paths.per_page,
                'total': paths.total,
                'pages': paths.pages,
                'has_next': paths.has_next,
                'has_prev': paths.has_prev
            },
            'filters': {
                'categories': ['conversation', 'grammar', 'vocabulary', 'business', 'academic'],
                'difficulties': ['beginner', 'intermediate', 'advanced']
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting learning paths: {str(e)}")
        return jsonify({
            'error': 'Failed to get learning paths',
            'telugu_message': 'అభ్యాస మార్గాలు పొందడంలో విఫలం'
        }), 500

@courses_bp.route('/learning-paths/<int:path_id>', methods=['GET'])
@jwt_required()
def get_learning_path_details(path_id):
    """
    Get detailed information about a specific learning path.
    """
    try:
        user_id = int(get_jwt_identity())
        
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        # Check if user is enrolled
        user = User.query.get(user_id)
        is_enrolled = path in user.enrolled_paths if user.enrolled_paths else False
        
        # Get activities in this path
        activities = Activity.query.filter_by(learning_path_id=path_id)\
            .order_by(Activity.order_in_path).all()
        
        # Get user's progress
        completed_activity_ids = []
        if is_enrolled:
            completed_logs = UserActivityLog.query.filter_by(
                user_id=user_id,
                learning_path_id=path_id
            ).all()
            completed_activity_ids = [log.activity_id for log in completed_logs]
        
        activity_list = []
        for activity in activities:
            activity_data = {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'order_in_path': activity.order_in_path,
                'is_completed': activity.id in completed_activity_ids,
                'points_reward': activity.points_reward
            }
            
            # Add completion info if completed
            if activity.id in completed_activity_ids:
                completion_log = next(log for log in completed_logs if log.activity_id == activity.id)
                activity_data.update({
                    'completed_at': completion_log.completed_at.isoformat(),
                    'score': completion_log.score,
                    'time_spent_minutes': completion_log.time_spent_minutes
                })
            
            activity_list.append(activity_data)
        
        # Calculate overall progress
        total_activities = len(activities)
        completed_activities = len(completed_activity_ids)
        completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        return jsonify({
            'message': 'Learning path details retrieved successfully!',
            'telugu_message': 'అభ్యాస మార్గం వివరాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'learning_path': {
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'category': path.category,
                'difficulty_level': path.difficulty_level,
                'estimated_duration_hours': path.estimated_duration_hours,
                'prerequisites': path.prerequisites or [],
                'learning_objectives': path.learning_objectives or [],
                'is_enrolled': is_enrolled,
                'progress': {
                    'total_activities': total_activities,
                    'completed_activities': completed_activities,
                    'completion_percentage': round(completion_percentage, 1),
                    'next_activity': next((a for a in activity_list if not a['is_completed']), None)
                },
                'activities': activity_list
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting learning path details: {str(e)}")
        return jsonify({
            'error': 'Failed to get learning path details',
            'telugu_message': 'అభ్యాస మార్గం వివరాలు పొందడంలో విఫలం'
        }), 500

@courses_bp.route('/enroll', methods=['POST'])
@jwt_required()
def enroll_user():
    """
    Enroll user in a learning path - simplified endpoint.
    Expected JSON: {"learning_path_id": 1}
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'telugu_message': 'JSON డేటా అందించబడలేదు'
            }), 400
        
        path_id = data.get('learning_path_id')
        if not path_id:
            return jsonify({
                'error': 'Learning path ID is required',
                'telugu_message': 'అభ్యాస మార్గం ID అవసరం'
            }), 400
        
        # Check if path exists
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Check if already enrolled
        if user.enrolled_paths and path in user.enrolled_paths:
            return jsonify({
                'error': 'Already enrolled in this learning path',
                'telugu_message': 'ఇప్పటికే ఈ అభ్యాస మార్గంలో నమోదు చేయబడింది'
            }), 400
        
        # Enroll user
        if not user.enrolled_paths:
            user.enrolled_paths = []
        user.enrolled_paths.append(path)
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully enrolled in learning path!',
            'telugu_message': 'అభ్యాస మార్గంలో విజయవంతంగా నమోదు చేయబడింది!',
            'learning_path': {
                'id': path.id,
                'title': path.title,
                'category': path.category,
                'difficulty_level': path.difficulty_level
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error enrolling user: {str(e)}")
        return jsonify({
            'error': 'Failed to enroll in learning path',
            'telugu_message': 'అభ్యాస మార్గంలో నమోదు చేయడంలో విఫలం'
        }), 500

@courses_bp.route('/learning-paths/<int:path_id>/enroll', methods=['POST'])
@jwt_required()
def enroll_in_learning_path(path_id):
    """
    Enroll user in a learning path.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if path exists
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Check if already enrolled
        if user.enrolled_paths and path in user.enrolled_paths:
            return jsonify({
                'error': 'Already enrolled in this learning path',
                'telugu_message': 'ఇప్పటికే ఈ అభ్యాస మార్గంలో నమోదు చేయబడింది'
            }), 400
        
        # Check prerequisites
        if path.prerequisites:
            user_proficiency = user.profile.proficiency_level if user.profile else 'beginner'
            
            # Handle both dictionary and list formats for prerequisites
            required_level = None
            if isinstance(path.prerequisites, dict):
                required_level = path.prerequisites.get('proficiency_level')
            elif isinstance(path.prerequisites, str):
                # If it's a JSON string, try to parse it
                try:
                    prereq_data = json.loads(path.prerequisites)
                    if isinstance(prereq_data, dict):
                        required_level = prereq_data.get('proficiency_level')
                except (json.JSONDecodeError, TypeError):
                    pass
            
            if required_level and required_level not in ['beginner'] and user_proficiency == 'beginner':
                return jsonify({
                    'error': f'This path requires {required_level} proficiency level',
                    'telugu_message': f'ఈ మార్గానికి {required_level} స్థాయి అవసరం'
                }), 400
        
        # Enroll user
        if not user.enrolled_paths:
            user.enrolled_paths = []
        user.enrolled_paths.append(path)
        
        # Create enrollment record
        enrollment_data = {
            'enrolled_at': datetime.utcnow().isoformat(),
            'enrollment_source': 'manual'
        }
        user.enrollment_data = user.enrollment_data or {}
        user.enrollment_data[str(path_id)] = enrollment_data
        
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully enrolled in learning path!',
            'telugu_message': 'అభ్యాస మార్గంలో విజయవంతంగా నమోదు చేయబడింది!',
            'enrollment': {
                'path_id': path_id,
                'path_title': path.title,
                'enrolled_at': enrollment_data['enrolled_at'],
                'next_steps': 'Start with the first activity to begin your learning journey!'
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error enrolling in learning path: {str(e)}")
        return jsonify({
            'error': 'Failed to enroll in learning path',
            'telugu_message': 'అభ్యాస మార్గంలో నమోదు చేయడంలో విఫలం'
        }), 500

@courses_bp.route('/enrollment/<int:path_id>/progress', methods=['GET'])
@jwt_required()
def get_enrollment_progress(path_id):
    """
    Get user's progress in a specific enrolled learning path.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if path exists
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Check if user is enrolled
        is_enrolled = path in user.enrolled_paths if user.enrolled_paths else False
        if not is_enrolled:
            return jsonify({
                'error': 'Not enrolled in this learning path',
                'telugu_message': 'ఈ అభ్యాస మార్గంలో నమోదు చేయబడలేదు'
            }), 400
        
        # Get all activities in this path
        activities = Activity.query.filter_by(learning_path_id=path_id)\
            .order_by(Activity.order_in_path).all()
        
        # Get completed activities
        completed_logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            learning_path_id=path_id
        ).all()
        
        completed_activity_ids = [log.activity_id for log in completed_logs]
        
        # Calculate progress
        total_activities = len(activities)
        completed_activities = len(completed_activity_ids)
        completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        # Get next activity
        next_activity = None
        for activity in activities:
            if activity.id not in completed_activity_ids:
                next_activity = {
                    'id': activity.id,
                    'title': activity.title,
                    'activity_type': activity.activity_type,
                    'difficulty_level': activity.difficulty_level,
                    'estimated_duration_minutes': activity.estimated_duration_minutes
                }
                break
        
        # Calculate time spent
        total_time_spent = sum(log.time_spent_minutes for log in completed_logs if log.time_spent_minutes)
        
        # Get recent activity
        recent_activity = None
        if completed_logs:
            latest_log = max(completed_logs, key=lambda x: x.completed_at)
            recent_activity = {
                'activity_id': latest_log.activity_id,
                'completed_at': latest_log.completed_at.isoformat(),
                'score': latest_log.score,
                'max_score': latest_log.max_score
            }
        
        return jsonify({
            'message': 'Enrollment progress retrieved successfully!',
            'telugu_message': 'నమోదు పురోగతి విజయవంతంగా తీసుకోబడింది!',
            'learning_path': {
                'id': path.id,
                'title': path.title,
                'category': path.category,
                'difficulty_level': path.difficulty_level
            },
            'progress': {
                'total_activities': total_activities,
                'completed_activities': completed_activities,
                'completion_percentage': round(completion_percentage, 1),
                'total_time_spent_minutes': total_time_spent,
                'is_completed': completion_percentage >= 100,
                'next_activity': next_activity,
                'recent_activity': recent_activity
            },
            'enrollment_info': {
                'enrolled_at': None,  # Will get from user_learning_paths table in future
                'days_since_enrollment': None
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting enrollment progress: {str(e)}")
        return jsonify({
            'error': 'Failed to get enrollment progress',
            'telugu_message': 'నమోదు పురోగతి పొందడంలో విఫలం'
        }), 500

@courses_bp.route('/my-learning-paths', methods=['GET'])
@jwt_required()
def get_my_learning_paths():
    """
    Get user's enrolled learning paths with progress.
    """
    try:
        user_id = int(get_jwt_identity())
        
        user = User.query.get(user_id)
        if not user or not user.enrolled_paths:
            return jsonify({
                'message': 'No enrolled learning paths',
                'telugu_message': 'నమోదు చేయబడిన అభ్యాస మార్గాలు లేవు',
                'learning_paths': []
            }), 200
        
        enrolled_paths = []
        for path in user.enrolled_paths:
            # Calculate progress
            total_activities = Activity.query.filter_by(learning_path_id=path.id).count()
            completed_activities = UserActivityLog.query.filter_by(
                user_id=user_id,
                learning_path_id=path.id
            ).count()
            
            completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
            
            # Get enrollment info
            enrollment_info = user.enrollment_data.get(str(path.id), {}) if user.enrollment_data else {}
            
            # Get next activity
            completed_activity_ids = [log.activity_id for log in UserActivityLog.query.filter_by(
                user_id=user_id, learning_path_id=path.id
            ).all()]
            
            next_activity = Activity.query.filter_by(learning_path_id=path.id)\
                .filter(~Activity.id.in_(completed_activity_ids))\
                .order_by(Activity.order_in_path).first()
            
            # Calculate time spent
            time_spent = db.session.query(func.sum(UserActivityLog.time_spent_minutes))\
                .filter(UserActivityLog.user_id == user_id,
                       UserActivityLog.learning_path_id == path.id).scalar() or 0
            
            enrolled_paths.append({
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'category': path.category,
                'difficulty_level': path.difficulty_level,
                'progress': {
                    'total_activities': total_activities,
                    'completed_activities': completed_activities,
                    'completion_percentage': round(completion_percentage, 1),
                    'time_spent_minutes': time_spent,
                    'next_activity': {
                        'id': next_activity.id,
                        'title': next_activity.title,
                        'activity_type': next_activity.activity_type
                    } if next_activity else None
                },
                'enrollment': {
                    'enrolled_at': enrollment_info.get('enrolled_at'),
                    'last_activity_at': UserActivityLog.query.filter_by(
                        user_id=user_id, learning_path_id=path.id
                    ).order_by(UserActivityLog.completed_at.desc()).first().completed_at.isoformat()
                    if UserActivityLog.query.filter_by(user_id=user_id, learning_path_id=path.id).first() else None
                }
            })
        
        return jsonify({
            'message': 'Enrolled learning paths retrieved successfully!',
            'telugu_message': 'నమోదు చేయబడిన అభ్యాస మార్గాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'learning_paths': enrolled_paths
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user learning paths: {str(e)}")
        return jsonify({
            'error': 'Failed to get learning paths',
            'telugu_message': 'అభ్యాస మార్గాలు పొందడంలో విఫలం'
        }), 500

@courses_bp.route('/start-activity', methods=['POST'])
@jwt_required()
def start_activity_simple():
    """
    Start a learning activity - simplified endpoint.
    Expected JSON: {"activity_id": 1}
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'telugu_message': 'JSON డేటా అందించబడలేదు'
            }), 400
        
        activity_id = data.get('activity_id')
        if not activity_id:
            return jsonify({
                'error': 'Activity ID is required',
                'telugu_message': 'కార్యాచరణ ID అవసరం'
            }), 400
        
        # Call the existing start_activity function
        return start_activity(activity_id)
        
    except Exception as e:
        current_app.logger.error(f"Error starting activity: {str(e)}")
        return jsonify({
            'error': 'Failed to start activity',
            'telugu_message': 'కార్యాచరణ ప్రారంభించడంలో విఫలం'
        }), 500

@courses_bp.route('/activities/<int:activity_id>/start', methods=['POST'])
@jwt_required()
def start_activity(activity_id):
    """
    Start a learning activity and generate content.
    """
    try:
        user_id = int(get_jwt_identity())
        
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        # Check if user is enrolled in the learning path
        user = User.query.get(user_id)
        learning_path = LearningPath.query.get(activity.learning_path_id)
        
        if learning_path not in (user.enrolled_paths or []):
            return jsonify({
                'error': 'You must be enrolled in the learning path to access this activity',
                'telugu_message': 'ఈ కార్యకలాపాన్ని యాక్సెస్ చేయడానికి మీరు అభ్యాస మార్గంలో నమోదు చేయబడాలి'
            }), 403
        
        # Check if activity is already completed
        existing_log = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).first()
        
        if existing_log:
            return jsonify({
                'error': 'Activity already completed',
                'telugu_message': 'కార్యకలాపం ఇప్పటికే పూర్తైంది',
                'completed_at': existing_log.completed_at.isoformat(),
                'score': existing_log.score
            }), 400
        
        # Generate activity content based on type
        activity_content = None
        
        try:
            if activity.activity_type == 'quiz':
                activity_content = activity_service.generate_quiz(
                    topic=activity.title,
                    level=activity.difficulty_level
                )
            elif activity.activity_type == 'flashcards':
                activity_content = activity_service.generate_flashcards(
                    topic=activity.title,
                    level=activity.difficulty_level
                )
            elif activity.activity_type == 'reading':
                activity_content = activity_service.generate_reading_exercise(
                    topic=activity.title,
                    level=activity.difficulty_level
                )
            elif activity.activity_type == 'writing':
                activity_content = activity_service.generate_writing_practice_prompt(
                    topic=activity.title,
                    level=activity.difficulty_level
                )
            elif activity.activity_type == 'role_play':
                activity_content = activity_service.generate_role_playing_scenario(
                    scenario_type=activity.title,
                    level=activity.difficulty_level
                )
            else:
                # Default to quiz if type not recognized
                activity_content = activity_service.generate_quiz(
                    topic=activity.title,
                    level=activity.difficulty_level
                )
        
        except Exception as content_error:
            current_app.logger.warning(f"Content generation failed: {str(content_error)}")
            # Provide fallback content
            activity_content = {
                'type': activity.activity_type,
                'title': activity.title,
                'instructions': f'Practice {activity.title} - Content will be loaded shortly.',
                'content': 'Content generation in progress...'
            }
        
        return jsonify({
            'message': 'Activity started successfully!',
            'telugu_message': 'కార్యకలాపం విజయవంతంగా ప్రారంభమైంది!',
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'learning_objectives': activity.learning_objectives or [],
                'content': activity_content,
                'started_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error starting activity: {str(e)}")
        return jsonify({
            'error': 'Failed to start activity',
            'telugu_message': 'కార్యకలాపం ప్రారంభించడంలో విఫలం'
        }), 500

@courses_bp.route('/activities/<int:activity_id>/complete', methods=['POST'])
@jwt_required()
def complete_activity(activity_id):
    """
    Complete an activity and record progress.
    
    Expected JSON:
    {
        "score": 85,
        "time_spent_minutes": 15,
        "answers": {...},
        "feedback": "The activity was helpful"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_message': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        score = data.get('score', 0)
        time_spent = data.get('time_spent_minutes', 0)
        answers = data.get('answers', {})
        feedback = data.get('feedback', '')
        
        # Validate score
        if score < 0 or score > 100:
            return jsonify({
                'error': 'Score must be between 0 and 100',
                'telugu_message': 'స్కోర్ 0 నుండి 100 మధ్య ఉండాలి'
            }), 400
        
        # Check if already completed
        existing_log = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).first()
        
        if existing_log:
            return jsonify({
                'error': 'Activity already completed',
                'telugu_message': 'కార్యకలాపం ఇప్పటికే పూర్తైంది'
            }), 400
        
        # Create completion log
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_id=activity_id,
            learning_path_id=activity.learning_path_id,
            score=score,
            time_spent_minutes=time_spent,
            completed_at=datetime.utcnow(),
            activity_data={
                'answers': answers,
                'feedback': feedback,
                'activity_type': activity.activity_type
            }
        )
        
        db.session.add(activity_log)
        
        # Update user progress and streaks
        user = User.query.get(user_id)
        if user.profile:
            user.profile.total_activities_completed += 1
            if score >= 70:  # Consider 70+ as good performance
                user.profile.total_points += score
        
        db.session.commit()
        
        # Get next activity suggestion
        next_activity = Activity.query.filter_by(learning_path_id=activity.learning_path_id)\
            .filter(Activity.order_in_path > activity.order_in_path)\
            .order_by(Activity.order_in_path).first()
        
        # Calculate learning path progress
        total_activities = Activity.query.filter_by(learning_path_id=activity.learning_path_id).count()
        completed_activities = UserActivityLog.query.filter_by(
            user_id=user_id,
            learning_path_id=activity.learning_path_id
        ).count()
        
        completion_percentage = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        return jsonify({
            'message': 'Activity completed successfully!',
            'telugu_message': 'కార్యకలాపం విజయవంతంగా పూర్తైంది!',
            'completion': {
                'score': score,
                'time_spent_minutes': time_spent,
                'completed_at': activity_log.completed_at.isoformat(),
                'performance_message': 'Excellent work!' if score >= 80 else 'Good job!' if score >= 60 else 'Keep practicing!'
            },
            'progress': {
                'learning_path_completion': round(completion_percentage, 1),
                'activities_completed': completed_activities,
                'total_activities': total_activities
            },
            'next_activity': {
                'id': next_activity.id,
                'title': next_activity.title,
                'activity_type': next_activity.activity_type
            } if next_activity else None,
            'celebration': {
                'show_celebration': score >= 80,
                'message': 'Great job! You\'re making excellent progress! గొప్పగా చేశారు!' if score >= 80 else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing activity: {str(e)}")
        return jsonify({
            'error': 'Failed to complete activity',
            'telugu_message': 'కార్యకలాపం పూర్తి చేయడంలో విఫలం'
        }), 500