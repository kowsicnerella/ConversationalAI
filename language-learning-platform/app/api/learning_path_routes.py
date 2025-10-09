"""from flask import Blueprint, request, jsonify

Learning Path API Routesfrom app.models import db, LearningPath, Activity, UserActivityLog

Handles enrollment, progress tracking, and path management.from app.models.user import User

"""from app.services.activity_generator_service import ActivityGeneratorService

from flask_jwt_extended import jwt_required, get_jwt_identity

from flask import Blueprint, request, jsonifyfrom datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identityimport json

from app.services.learning_path_service import LearningPathService

from app.models.user import dblearning_path_bp = Blueprint('learning_path', __name__)

activity_service = ActivityGeneratorService()

learning_paths_bp = Blueprint('learning_paths', __name__, url_prefix='/api/learning-paths')

# ===== DYNAMIC LEARNING PATH SYSTEM =====



@learning_paths_bp.route('', methods=['GET'])@learning_path_bp.route('/personalized-recommendation', methods=['POST'])

def get_learning_paths():@jwt_required()

    """def get_personalized_learning_path_recommendation():

    Get all available learning paths with optional filters.    """Generate personalized learning path recommendations based on user assessment"""

        try:

    Query Parameters:        user_id = int(get_jwt_identity())

        - difficulty_level: beginner, intermediate, advanced        data = request.get_json()

        - category: vocabulary, grammar, conversation, etc.        

            if not data:

    Returns:            return jsonify({

        List of learning paths                'error': 'Assessment data required',

    """                'telugu_message': 'అంచనా డేటా అవసరం'

    try:            }), 400

        difficulty = request.args.get('difficulty_level')        

        category = request.args.get('category')        # Extract assessment data

                english_level = data.get('english_level', 'beginner')  # beginner, intermediate, advanced

        paths = LearningPathService.get_all_paths(        learning_goals = data.get('learning_goals', [])  # conversation, business, academic, travel

            difficulty_level=difficulty,        interests = data.get('interests', [])  # technology, culture, movies, food, etc.

            category=category        time_available = data.get('time_available_minutes', 30)  # daily learning time

        )        previous_experience = data.get('previous_experience', {})

                

        return jsonify({        # Use AI to generate personalized recommendations

            'success': True,        recommendation_prompt = f"""

            'learning_paths': paths,        Generate personalized learning path recommendations for a Telugu speaker learning English.

            'total': len(paths)        

        }), 200        User Profile:

            - English Level: {english_level}

    except Exception as e:        - Learning Goals: {', '.join(learning_goals)}

        return jsonify({        - Interests: {', '.join(interests)}

            'success': False,        - Daily Time Available: {time_available} minutes

            'message': f'Error fetching learning paths: {str(e)}',        - Previous Experience: {json.dumps(previous_experience)}

            'message_telugu': 'నేర్చుకునే మార్గాలను పొందడంలో లోపం'        

        }), 500        Based on this profile, recommend:

        1. 3-5 most suitable learning paths with priorities

        2. Suggested learning sequence

@learning_paths_bp.route('/<int:path_id>', methods=['GET'])        3. Estimated timeline for each path

@jwt_required(optional=True)        4. Customization suggestions

def get_path_detail(path_id):        

    """        Return in JSON format:

    Get detailed information about a specific learning path.        ```json

    Includes chapters and activities.        {{

    If user is authenticated, includes enrollment status.            "recommended_paths": [

                    {{

    Args:                    "path_id": 1,

        path_id: Learning path ID                    "title": "Business English Fundamentals",

                        "priority": "high",

    Returns:                    "match_score": 95,

        Detailed path information                    "estimated_weeks": 8,

    """                    "reasoning": "Perfect match for business goals and intermediate level",

    try:                    "telugu_reasoning": "వ్యాపార లక్ష్యాలకు మరియు మధ్యస్థ స్థాయికి సరైన సరిపోలిక"

        # Get user ID if authenticated                }}

        user_id = None            ],

        try:            "learning_sequence": [

            user_id = get_jwt_identity()                "Start with Business English Fundamentals",

        except:                "Progress to Conversation Skills",

            pass                "Advanced: Professional Communication"

                    ],

        path = LearningPathService.get_path_detail(path_id, user_id=user_id)            "customizations": [

                        "Include more technology vocabulary based on interests",

        if not path:                "Focus on formal communication for business goals"

            return jsonify({            ],

                'success': False,            "daily_plan": {{

                'message': 'Learning path not found',                "activities_per_day": 3,

                'message_telugu': 'నేర్చుకునే మార్గం కనుగొనబడలేదు'                "estimated_time_per_activity": 10,

            }), 404                "recommended_schedule": "Morning vocabulary, Afternoon practice, Evening review"

                    }}

        return jsonify({        }}

            'success': True,        ```

            'learning_path': path        """

        }), 200        

            response = activity_service.model.generate_content(recommendation_prompt)

    except Exception as e:        from app.services.activity_generator_service import _extract_json_from_response

        return jsonify({        recommendation_data = _extract_json_from_response(response.text)

            'success': False,        

            'message': f'Error fetching path details: {str(e)}',        # Get actual learning paths from database

            'message_telugu': 'మార్గం వివరాలను పొందడంలో లోపం'        available_paths = LearningPath.query.all()

        }), 500        path_details = []

        

        for rec_path in recommendation_data.get('recommended_paths', []):

@learning_paths_bp.route('/<int:path_id>/enroll', methods=['POST'])            # Find matching path in database (match by title similarity or create new logic)

@jwt_required()            matching_path = None

def enroll_in_path(path_id):            for db_path in available_paths:

    """                if any(keyword in db_path.title.lower() for keyword in rec_path['title'].lower().split()):

    Enroll the authenticated user in a learning path.                    matching_path = db_path

    Creates enrollment record and unlocks Chapter 1.                    break

                

    Args:            if matching_path:

        path_id: Learning path ID                path_info = {

                        'id': matching_path.id,

    Returns:                    'title': matching_path.title,

        Enrollment confirmation                    'description': matching_path.description,

    """                    'category': matching_path.category,

    try:                    'difficulty_level': matching_path.difficulty_level,

        user_id = get_jwt_identity()                    'estimated_duration_hours': matching_path.estimated_duration_hours,

                            'recommendation_data': rec_path

        result = LearningPathService.enroll_user(user_id, path_id)                }

                        path_details.append(path_info)

        status_code = 200 if result['success'] else 400        

        return jsonify(result), status_code        return jsonify({

                'message': 'Personalized learning paths recommended successfully!',

    except Exception as e:            'telugu_message': 'వ్యక్తిగతీకరించిన అభ్యాస మార్గాలు విజయవంతంగా సిఫార్సు చేయబడ్డాయి!',

        return jsonify({            'user_profile': {

            'success': False,                'english_level': english_level,

            'message': f'Error enrolling in path: {str(e)}',                'learning_goals': learning_goals,

            'message_telugu': 'మార్గంలో నమోదు చేసుకోవడంలో లోపం'                'interests': interests,

        }), 500                'time_available': time_available

            },

            'recommended_paths': path_details,

@learning_paths_bp.route('/enrolled', methods=['GET'])            'ai_recommendations': recommendation_data,

@jwt_required()            'next_steps': [

def get_enrolled_paths():                'Review recommended paths',

    """                'Enroll in your preferred path',

    Get all learning paths the user is enrolled in.                'Take initial assessment for personalized difficulty',

                    'Start your learning journey'

    Query Parameters:            ]

        - status: active, paused, completed, dropped        }), 200

            

    Returns:    except Exception as e:

        List of enrolled paths with progress        return jsonify({

    """            'error': 'Failed to generate personalized recommendations',

    try:            'telugu_message': 'వ్యక్తిగతీకరించిన సిఫార్సులు రూపొందించడంలో విఫలం',

        user_id = get_jwt_identity()            'details': str(e)

        status = request.args.get('status')        }), 500

        

        enrollments = LearningPathService.get_user_enrollments(user_id, status=status)@learning_path_bp.route('/create-custom-path', methods=['POST'])

        @jwt_required()

        return jsonify({def create_custom_learning_path():

            'success': True,    """Create a custom learning path based on user specifications"""

            'enrollments': enrollments,    try:

            'total': len(enrollments)        user_id = int(get_jwt_identity())

        }), 200        data = request.get_json()

            

    except Exception as e:        if not data:

        return jsonify({            return jsonify({

            'success': False,                'error': 'Path specifications required',

            'message': f'Error fetching enrollments: {str(e)}',                'telugu_message': 'మార్గ వివరణలు అవసరం'

            'message_telugu': 'నమోదులను పొందడంలో లోపం'            }), 400

        }), 500        

        title = data.get('title')

        description = data.get('description', '')

@learning_paths_bp.route('/<int:path_id>/progress', methods=['GET'])        focus_areas = data.get('focus_areas', [])  # vocabulary, grammar, conversation, etc.

@jwt_required()        difficulty_level = data.get('difficulty_level', 'beginner')

def get_path_progress(path_id):        duration_weeks = data.get('duration_weeks', 4)

    """        activities_per_week = data.get('activities_per_week', 5)

    Get detailed progress for user's enrollment in a learning path.        

    Includes chapters, activities, and completion status.        if not title:

                return jsonify({

    Args:                'error': 'Path title is required',

        path_id: Learning path ID                'telugu_message': 'మార్గ శీర్షిక అవసరం'

                }), 400

    Returns:        

        Detailed progress information        # Generate custom learning path structure using AI

    """        generation_prompt = f"""

    try:        Create a custom learning path for Telugu speakers learning English.

        user_id = get_jwt_identity()        

                Specifications:

        progress = LearningPathService.get_path_progress(user_id, path_id)        - Title: {title}

                - Description: {description}

        status_code = 200 if progress.get('success') else 404        - Focus Areas: {', '.join(focus_areas)}

        return jsonify(progress), status_code        - Difficulty Level: {difficulty_level}

            - Duration: {duration_weeks} weeks

    except Exception as e:        - Activities per week: {activities_per_week}

        return jsonify({        

            'success': False,        Generate a structured learning path with:

            'message': f'Error fetching progress: {str(e)}',        1. Week-by-week breakdown

            'message_telugu': 'పురోగతిని పొందడంలో లోపం'        2. Activity types and topics for each week

        }), 500        3. Progressive difficulty

        4. Balance of different skill areas

        

@learning_paths_bp.route('/<int:path_id>/unenroll', methods=['POST'])        Return in JSON format:

@jwt_required()        ```json

def unenroll_from_path(path_id):        {{

    """            "path_structure": {{

    Unenroll user from a learning path.                "week_1": {{

    Marks enrollment as dropped but preserves progress.                    "theme": "Basic Vocabulary Building",

                        "activities": [

    Args:                        {{

        path_id: Learning path ID                            "title": "Common Greetings Quiz",

                                "type": "quiz",

    Returns:                            "order": 1,

        Unenrollment confirmation                            "estimated_minutes": 15,

    """                            "topics": ["greetings", "basic_conversation"]

    try:                        }}

        user_id = get_jwt_identity()                    ]

                        }}

        result = LearningPathService.unenroll_user(user_id, path_id)            }},

                    "learning_objectives": [

        status_code = 200 if result['success'] else 404                "Master basic vocabulary",

        return jsonify(result), status_code                "Understand simple sentences",

                    "Basic conversation skills"

    except Exception as e:            ],

        return jsonify({            "prerequisites": ["Basic Telugu literacy", "Motivation to learn"],

            'success': False,            "estimated_total_hours": 20

            'message': f'Error unenrolling from path: {str(e)}',        }}

            'message_telugu': 'మార్గం నుండి నిష్క్రమించడంలో లోపం'        ```

        }), 500        """

        

        response = activity_service.model.generate_content(generation_prompt)

@learning_paths_bp.route('/<int:path_id>/chapters/<int:chapter_id>/complete-activity', methods=['POST'])        from app.services.activity_generator_service import _extract_json_from_response

@jwt_required()        path_structure = _extract_json_from_response(response.text)

def complete_chapter_activity(path_id, chapter_id):        

    """        # Create the learning path in database

    Mark an activity as completed and update progress.        new_learning_path = LearningPath(

    Unlocks next activity or chapter if applicable.            title=title,

                description=description,

    Args:            category='custom',

        path_id: Learning path ID            difficulty_level=difficulty_level,

        chapter_id: Chapter ID            estimated_duration_hours=path_structure.get('estimated_total_hours', duration_weeks * 2),

                is_premium=False,

    Request Body:            created_at=datetime.utcnow()

        - session_id: Learning session ID        )

        - score: Activity score (0-100)        

        - points_earned: Points from gamification        db.session.add(new_learning_path)

        - time_spent: Time spent in minutes        db.session.flush()  # Get the ID

            

    Returns:        # Generate and save activities for this path

        Updated progress and unlock information        activities_created = []

    """        activity_order = 1

    try:        

        user_id = get_jwt_identity()        for week_key, week_data in path_structure.get('path_structure', {}).items():

        data = request.get_json()            for activity_spec in week_data.get('activities', []):

                        # Generate actual activity content using existing methods

        session_id = data.get('session_id')                activity_content = None

        score = data.get('score', 0)                activity_type = activity_spec.get('type', 'quiz')

        points_earned = data.get('points_earned', 0)                

        time_spent = data.get('time_spent', 0)                if activity_type == 'quiz':

                            activity_content = activity_service.generate_quiz(

        if not session_id:                        ', '.join(activity_spec.get('topics', [])), 

            return jsonify({                        difficulty_level

                'success': False,                    )

                'message': 'session_id is required',                elif activity_type == 'flashcard':

                'message_telugu': 'సెషన్ ID అవసరం'                    activity_content = activity_service.generate_flashcards(

            }), 400                        ', '.join(activity_spec.get('topics', [])), 

                                difficulty_level

        result = LearningPathService.complete_activity(                    )

            user_id=user_id,                

            path_id=path_id,                if activity_content:

            chapter_id=chapter_id,                    new_activity = Activity(

            session_id=session_id,                        learning_path_id=new_learning_path.id,

            score=score,                        activity_type=activity_type,

            points_earned=points_earned,                        title=activity_spec.get('title', f'Activity {activity_order}'),

            time_spent=time_spent                        content=activity_content,

        )                        difficulty_level=difficulty_level,

                                order_in_path=activity_order,

        status_code = 200 if result.get('success') else 400                        estimated_duration_minutes=activity_spec.get('estimated_minutes', 15),

        return jsonify(result), status_code                        points_reward=15,  # Custom activities get bonus points

                            created_at=datetime.utcnow()

    except Exception as e:                    )

        return jsonify({                    

            'success': False,                    db.session.add(new_activity)

            'message': f'Error completing activity: {str(e)}',                    activities_created.append({

            'message_telugu': 'కార్యకలాపాన్ని పూర్తి చేయడంలో లోపం'                        'title': new_activity.title,

        }), 500                        'type': activity_type,

                        'order': activity_order

                    })

@learning_paths_bp.route('/statistics', methods=['GET'])                    activity_order += 1

@jwt_required()        

def get_user_statistics():        db.session.commit()

    """        

    Get overall statistics for user's learning path progress.        return jsonify({

                'message': 'Custom learning path created successfully!',

    Returns:            'telugu_message': 'అనుకూల అభ్యాస మార్గం విజయవంతంగా సృష్టించబడింది!',

        Overall learning statistics            'learning_path': {

    """                'id': new_learning_path.id,

    try:                'title': new_learning_path.title,

        user_id = get_jwt_identity()                'description': new_learning_path.description,

                        'difficulty_level': new_learning_path.difficulty_level,

        enrollments = LearningPathService.get_user_enrollments(user_id)                'estimated_duration_hours': new_learning_path.estimated_duration_hours,

                        'activities_count': len(activities_created)

        # Calculate statistics            },

        total_enrollments = len(enrollments)            'generated_structure': path_structure,

        active_enrollments = len([e for e in enrollments if e['status'] == 'active'])            'activities_created': activities_created,

        completed_enrollments = len([e for e in enrollments if e['status'] == 'completed'])            'next_steps': [

                        'Enroll in your custom path',

        total_points = sum(e.get('points_earned', 0) for e in enrollments)                'Start with the first activity',

        total_time = sum(e.get('total_time_spent_minutes', 0) for e in enrollments)                'Track your progress',

                        'Provide feedback for improvements'

        avg_completion = sum(e.get('completion_percentage', 0) for e in enrollments) / total_enrollments if total_enrollments > 0 else 0            ]

                }), 201

        return jsonify({        

            'success': True,    except Exception as e:

            'statistics': {        db.session.rollback()

                'total_enrollments': total_enrollments,        return jsonify({

                'active_enrollments': active_enrollments,            'error': 'Failed to create custom learning path',

                'completed_enrollments': completed_enrollments,            'telugu_message': 'అనుకూల అభ్యాస మార్గం సృష్టించడంలో విఫలం',

                'total_points_earned': total_points,            'details': str(e)

                'total_time_spent_minutes': total_time,        }), 500

                'total_time_spent_hours': round(total_time / 60, 2),

                'average_completion_percentage': round(avg_completion, 2)@learning_path_bp.route('/adaptive-difficulty', methods=['POST'])

            }@jwt_required()

        }), 200def adjust_adaptive_difficulty():

        """Adjust learning path difficulty based on user performance"""

    except Exception as e:    try:

        return jsonify({        user_id = int(get_jwt_identity())

            'success': False,        data = request.get_json()

            'message': f'Error fetching statistics: {str(e)}',        

            'message_telugu': 'గణాంకాలను పొందడంలో లోపం'        if not data:

        }), 500            return jsonify({

                'error': 'Performance data required',

                'telugu_message': 'పనితీరు డేటా అవసరం'

# Error handlers            }), 400

@learning_paths_bp.errorhandler(404)        

def not_found(error):        learning_path_id = data.get('learning_path_id')

    return jsonify({        if not learning_path_id:

        'success': False,            return jsonify({

        'message': 'Resource not found',                'error': 'Learning path ID required',

        'message_telugu': 'వనరు కనుగొనబడలేదు'                'telugu_message': 'అభ్యాస మార్గ ID అవసరం'

    }), 404            }), 400

        

        # Get user's recent performance in this learning path

@learning_paths_bp.errorhandler(500)        recent_logs = UserActivityLog.query.filter_by(

def internal_error(error):            user_id=user_id, learning_path_id=learning_path_id

    db.session.rollback()        ).order_by(UserActivityLog.completed_at.desc()).limit(10).all()

    return jsonify({        

        'success': False,        if not recent_logs:

        'message': 'Internal server error',            return jsonify({

        'message_telugu': 'అంతర్గత సర్వర్ లోపం'                'error': 'No performance data found',

    }), 500                'telugu_message': 'పనితీరు డేటా కనుగొనబడలేదు'

            }), 404
        
        # Calculate performance metrics
        total_activities = len(recent_logs)
        correct_answers = 0
        avg_time_per_activity = 0
        total_attempts = 0
        
        for log in recent_logs:
            if log.score and log.max_score and log.max_score > 0:
                if (log.score / log.max_score) >= 0.7:  # 70% threshold for "correct"
                    correct_answers += 1
            avg_time_per_activity += log.time_spent_minutes or 0
            total_attempts += log.attempt_number or 1
        
        success_rate = (correct_answers / total_activities) if total_activities > 0 else 0
        avg_time_per_activity = avg_time_per_activity / total_activities if total_activities > 0 else 0
        avg_attempts = total_attempts / total_activities if total_activities > 0 else 1
        
        # Determine difficulty adjustment using AI
        adjustment_prompt = f"""
        Analyze user performance and recommend difficulty adjustments for a Telugu-English learning path.
        
        Performance Data:
        - Success Rate: {success_rate:.2%}
        - Average Time per Activity: {avg_time_per_activity:.1f} minutes
        - Average Attempts per Activity: {avg_attempts:.1f}
        - Total Activities Completed: {total_activities}
        
        Based on this data, recommend:
        1. Whether to increase, decrease, or maintain difficulty
        2. Specific adjustments to make
        3. New activity types to introduce or remove
        4. Pacing adjustments
        
        Guidelines:
        - Success rate > 80% and low attempts: Increase difficulty
        - Success rate < 50% or high attempts: Decrease difficulty  
        - High time spent: Simplify or add more practice
        - Low time spent: Add more challenging content
        
        Return in JSON format:
        ```json
        {{
            "adjustment_recommendation": "increase",
            "new_difficulty_level": "intermediate",
            "reasoning": "High success rate (85%) indicates readiness for more challenging content",
            "telugu_reasoning": "అధిక విజయ రేటు (85%) మరింత సవాలు ఉన్న కంటెంట్‌కు సిద్ధతను సూచిస్తుంది",
            "specific_adjustments": [
                "Introduce more complex grammar concepts",
                "Add longer reading comprehension exercises",
                "Include conversation-based activities"
            ],
            "pacing_changes": {{
                "activities_per_week": 6,
                "estimated_time_per_activity": 20
            }},
            "encouragement": "Excellent progress! Ready for the next level.",
            "telugu_encouragement": "అద్భుతమైన పురోగతి! తదుపరి స్థాయికి సిద్ధం."
        }}
        ```
        """
        
        response = activity_service.model.generate_content(adjustment_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        adjustment_data = _extract_json_from_response(response.text)
        
        # Apply adjustments (in a real system, you might update user preferences or create new activities)
        user = User.query.get(user_id)
        learning_path = LearningPath.query.get(learning_path_id)
        
        # Store adjustment recommendation in user's enrollment data
        if not user.enrollment_data:
            user.enrollment_data = {}
        
        if 'adaptive_adjustments' not in user.enrollment_data:
            user.enrollment_data['adaptive_adjustments'] = {}
        
        user.enrollment_data['adaptive_adjustments'][str(learning_path_id)] = {
            'adjustment_date': datetime.utcnow().isoformat(),
            'previous_difficulty': learning_path.difficulty_level,
            'recommended_difficulty': adjustment_data.get('new_difficulty_level'),
            'performance_metrics': {
                'success_rate': success_rate,
                'avg_time': avg_time_per_activity,
                'avg_attempts': avg_attempts
            },
            'adjustments': adjustment_data
        }
        
        # Mark as modified for JSON field
        user.enrollment_data = dict(user.enrollment_data)
        db.session.commit()
        
        return jsonify({
            'message': 'Adaptive difficulty adjustment completed!',
            'telugu_message': 'అనుకూల కష్టता సర్దుబాటు పూర్తయింది!',
            'performance_analysis': {
                'success_rate': f"{success_rate:.1%}",
                'avg_time_per_activity': f"{avg_time_per_activity:.1f} minutes",
                'avg_attempts_per_activity': f"{avg_attempts:.1f}",
                'total_activities_analyzed': total_activities
            },
            'adjustment_recommendation': adjustment_data,
            'learning_path_info': {
                'id': learning_path.id,
                'title': learning_path.title,
                'current_difficulty': learning_path.difficulty_level
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to adjust adaptive difficulty',
            'telugu_message': 'అనుకూల కష్టత సర్దుబాటు చేయడంలో విఫలం',
            'details': str(e)
        }), 500

@learning_path_bp.route('/progress-analysis/<int:learning_path_id>', methods=['GET'])
@jwt_required()
def analyze_learning_path_progress(learning_path_id):
    """Analyze detailed progress for a specific learning path"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get learning path
        learning_path = LearningPath.query.get(learning_path_id)
        if not learning_path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        # Get all activities in this path
        activities = Activity.query.filter_by(learning_path_id=learning_path_id)\
                                 .order_by(Activity.order_in_path).all()
        
        # Get user's logs for these activities
        activity_ids = [a.id for a in activities]
        logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                   .filter(UserActivityLog.activity_id.in_(activity_ids))\
                                   .all()
        
        logs_by_activity = {log.activity_id: log for log in logs}
        
        # Analyze progress patterns
        progress_data = []
        completed_count = 0
        total_time = 0
        total_score = 0
        total_max_score = 0
        
        for activity in activities:
            log = logs_by_activity.get(activity.id)
            is_completed = bool(log)
            
            if is_completed:
                completed_count += 1
                total_time += log.time_spent_minutes or 0
                if log.score and log.max_score:
                    total_score += log.score
                    total_max_score += log.max_score
            
            progress_data.append({
                'activity_id': activity.id,
                'activity_title': activity.title,
                'activity_type': activity.activity_type,
                'order_in_path': activity.order_in_path,
                'is_completed': is_completed,
                'completion_date': log.completed_at.isoformat() if log else None,
                'score': log.score if log else None,
                'max_score': log.max_score if log else None,
                'percentage': round((log.score / log.max_score * 100), 1) if log and log.max_score > 0 else None,
                'time_spent': log.time_spent_minutes if log else None,
                'attempts': log.attempt_number if log else 0
            })
        
        # Calculate overall metrics
        completion_percentage = (completed_count / len(activities) * 100) if activities else 0
        average_score_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
        
        # Identify learning patterns and recommendations
        analysis_prompt = f"""
        Analyze the learning progress for a Telugu speaker in an English learning path.
        
        Learning Path: {learning_path.title}
        Progress Data: {json.dumps(progress_data[-5:], indent=2)}  # Recent 5 activities
        
        Overall Metrics:
        - Completion: {completion_percentage:.1f}%
        - Average Score: {average_score_percentage:.1f}%
        - Total Time: {total_time} minutes
        - Activities Completed: {completed_count}/{len(activities)}
        
        Provide analysis and recommendations:
        1. Learning pattern identification
        2. Strengths and areas for improvement
        3. Recommended next steps
        4. Motivational feedback
        
        Return in JSON format:
        ```json
        {{
            "learning_patterns": [
                "Consistent daily practice",
                "Strong in vocabulary, needs grammar work"
            ],
            "strengths": [
                "Quick comprehension",
                "Good retention rate"
            ],
            "improvement_areas": [
                "Grammar fundamentals",
                "Speaking confidence"
            ],
            "recommendations": [
                "Focus on grammar exercises",
                "Add conversation practice",
                "Increase difficulty level"
            ],
            "motivation_message": "Great progress! You're 70% through the path.",
            "telugu_motivation": "అద్భుతమైన పురోగతి! మీరు మార్గంలో 70% పూర్తి చేశారు.",
            "predicted_completion_date": "2024-02-15",
            "suggested_study_plan": {{
                "activities_per_day": 2,
                "focus_areas": ["grammar", "conversation"],
                "estimated_days_to_complete": 10
            }}
        }}
        ```
        """
        
        response = activity_service.model.generate_content(analysis_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        analysis_data = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Learning path progress analyzed successfully!',
            'telugu_message': 'అభ్యాస మార్గ పురోగతి విజయవంతంగా విశ్లేషించబడింది!',
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'difficulty_level': learning_path.difficulty_level,
                'total_activities': len(activities)
            },
            'progress_summary': {
                'completion_percentage': round(completion_percentage, 1),
                'activities_completed': completed_count,
                'total_activities': len(activities),
                'average_score_percentage': round(average_score_percentage, 1),
                'total_time_spent_minutes': total_time
            },
            'detailed_progress': progress_data,
            'ai_analysis': analysis_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze learning path progress',
            'telugu_message': 'అభ్యాస మార్గ పురోగతి విశ్లేషణలో విఫలం',
            'details': str(e)
        }), 500
