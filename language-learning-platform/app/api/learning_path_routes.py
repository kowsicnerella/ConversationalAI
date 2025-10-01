from flask import Blueprint, request, jsonify
from app.models import db, LearningPath, Activity, UserActivityLog
from app.models.user import User
from app.services.activity_generator_service import ActivityGeneratorService
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json

learning_path_bp = Blueprint('learning_path', __name__)
activity_service = ActivityGeneratorService()

# ===== DYNAMIC LEARNING PATH SYSTEM =====

@learning_path_bp.route('/personalized-recommendation', methods=['POST'])
@jwt_required()
def get_personalized_learning_path_recommendation():
    """Generate personalized learning path recommendations based on user assessment"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Assessment data required',
                'telugu_message': 'అంచనా డేటా అవసరం'
            }), 400
        
        # Extract assessment data
        english_level = data.get('english_level', 'beginner')  # beginner, intermediate, advanced
        learning_goals = data.get('learning_goals', [])  # conversation, business, academic, travel
        interests = data.get('interests', [])  # technology, culture, movies, food, etc.
        time_available = data.get('time_available_minutes', 30)  # daily learning time
        previous_experience = data.get('previous_experience', {})
        
        # Use AI to generate personalized recommendations
        recommendation_prompt = f"""
        Generate personalized learning path recommendations for a Telugu speaker learning English.
        
        User Profile:
        - English Level: {english_level}
        - Learning Goals: {', '.join(learning_goals)}
        - Interests: {', '.join(interests)}
        - Daily Time Available: {time_available} minutes
        - Previous Experience: {json.dumps(previous_experience)}
        
        Based on this profile, recommend:
        1. 3-5 most suitable learning paths with priorities
        2. Suggested learning sequence
        3. Estimated timeline for each path
        4. Customization suggestions
        
        Return in JSON format:
        ```json
        {{
            "recommended_paths": [
                {{
                    "path_id": 1,
                    "title": "Business English Fundamentals",
                    "priority": "high",
                    "match_score": 95,
                    "estimated_weeks": 8,
                    "reasoning": "Perfect match for business goals and intermediate level",
                    "telugu_reasoning": "వ్యాపార లక్ష్యాలకు మరియు మధ్యస్థ స్థాయికి సరైన సరిపోలిక"
                }}
            ],
            "learning_sequence": [
                "Start with Business English Fundamentals",
                "Progress to Conversation Skills",
                "Advanced: Professional Communication"
            ],
            "customizations": [
                "Include more technology vocabulary based on interests",
                "Focus on formal communication for business goals"
            ],
            "daily_plan": {{
                "activities_per_day": 3,
                "estimated_time_per_activity": 10,
                "recommended_schedule": "Morning vocabulary, Afternoon practice, Evening review"
            }}
        }}
        ```
        """
        
        response = activity_service.model.generate_content(recommendation_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        recommendation_data = _extract_json_from_response(response.text)
        
        # Get actual learning paths from database
        available_paths = LearningPath.query.all()
        path_details = []
        
        for rec_path in recommendation_data.get('recommended_paths', []):
            # Find matching path in database (match by title similarity or create new logic)
            matching_path = None
            for db_path in available_paths:
                if any(keyword in db_path.title.lower() for keyword in rec_path['title'].lower().split()):
                    matching_path = db_path
                    break
            
            if matching_path:
                path_info = {
                    'id': matching_path.id,
                    'title': matching_path.title,
                    'description': matching_path.description,
                    'category': matching_path.category,
                    'difficulty_level': matching_path.difficulty_level,
                    'estimated_duration_hours': matching_path.estimated_duration_hours,
                    'recommendation_data': rec_path
                }
                path_details.append(path_info)
        
        return jsonify({
            'message': 'Personalized learning paths recommended successfully!',
            'telugu_message': 'వ్యక్తిగతీకరించిన అభ్యాస మార్గాలు విజయవంతంగా సిఫార్సు చేయబడ్డాయి!',
            'user_profile': {
                'english_level': english_level,
                'learning_goals': learning_goals,
                'interests': interests,
                'time_available': time_available
            },
            'recommended_paths': path_details,
            'ai_recommendations': recommendation_data,
            'next_steps': [
                'Review recommended paths',
                'Enroll in your preferred path',
                'Take initial assessment for personalized difficulty',
                'Start your learning journey'
            ]
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate personalized recommendations',
            'telugu_message': 'వ్యక్తిగతీకరించిన సిఫార్సులు రూపొందించడంలో విఫలం',
            'details': str(e)
        }), 500

@learning_path_bp.route('/create-custom-path', methods=['POST'])
@jwt_required()
def create_custom_learning_path():
    """Create a custom learning path based on user specifications"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Path specifications required',
                'telugu_message': 'మార్గ వివరణలు అవసరం'
            }), 400
        
        title = data.get('title')
        description = data.get('description', '')
        focus_areas = data.get('focus_areas', [])  # vocabulary, grammar, conversation, etc.
        difficulty_level = data.get('difficulty_level', 'beginner')
        duration_weeks = data.get('duration_weeks', 4)
        activities_per_week = data.get('activities_per_week', 5)
        
        if not title:
            return jsonify({
                'error': 'Path title is required',
                'telugu_message': 'మార్గ శీర్షిక అవసరం'
            }), 400
        
        # Generate custom learning path structure using AI
        generation_prompt = f"""
        Create a custom learning path for Telugu speakers learning English.
        
        Specifications:
        - Title: {title}
        - Description: {description}
        - Focus Areas: {', '.join(focus_areas)}
        - Difficulty Level: {difficulty_level}
        - Duration: {duration_weeks} weeks
        - Activities per week: {activities_per_week}
        
        Generate a structured learning path with:
        1. Week-by-week breakdown
        2. Activity types and topics for each week
        3. Progressive difficulty
        4. Balance of different skill areas
        
        Return in JSON format:
        ```json
        {{
            "path_structure": {{
                "week_1": {{
                    "theme": "Basic Vocabulary Building",
                    "activities": [
                        {{
                            "title": "Common Greetings Quiz",
                            "type": "quiz",
                            "order": 1,
                            "estimated_minutes": 15,
                            "topics": ["greetings", "basic_conversation"]
                        }}
                    ]
                }}
            }},
            "learning_objectives": [
                "Master basic vocabulary",
                "Understand simple sentences",
                "Basic conversation skills"
            ],
            "prerequisites": ["Basic Telugu literacy", "Motivation to learn"],
            "estimated_total_hours": 20
        }}
        ```
        """
        
        response = activity_service.model.generate_content(generation_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        path_structure = _extract_json_from_response(response.text)
        
        # Create the learning path in database
        new_learning_path = LearningPath(
            title=title,
            description=description,
            category='custom',
            difficulty_level=difficulty_level,
            estimated_duration_hours=path_structure.get('estimated_total_hours', duration_weeks * 2),
            is_premium=False,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_learning_path)
        db.session.flush()  # Get the ID
        
        # Generate and save activities for this path
        activities_created = []
        activity_order = 1
        
        for week_key, week_data in path_structure.get('path_structure', {}).items():
            for activity_spec in week_data.get('activities', []):
                # Generate actual activity content using existing methods
                activity_content = None
                activity_type = activity_spec.get('type', 'quiz')
                
                if activity_type == 'quiz':
                    activity_content = activity_service.generate_quiz(
                        ', '.join(activity_spec.get('topics', [])), 
                        difficulty_level
                    )
                elif activity_type == 'flashcard':
                    activity_content = activity_service.generate_flashcards(
                        ', '.join(activity_spec.get('topics', [])), 
                        difficulty_level
                    )
                
                if activity_content:
                    new_activity = Activity(
                        learning_path_id=new_learning_path.id,
                        activity_type=activity_type,
                        title=activity_spec.get('title', f'Activity {activity_order}'),
                        content=activity_content,
                        difficulty_level=difficulty_level,
                        order_in_path=activity_order,
                        estimated_duration_minutes=activity_spec.get('estimated_minutes', 15),
                        points_reward=15,  # Custom activities get bonus points
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(new_activity)
                    activities_created.append({
                        'title': new_activity.title,
                        'type': activity_type,
                        'order': activity_order
                    })
                    activity_order += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Custom learning path created successfully!',
            'telugu_message': 'అనుకూల అభ్యాస మార్గం విజయవంతంగా సృష్టించబడింది!',
            'learning_path': {
                'id': new_learning_path.id,
                'title': new_learning_path.title,
                'description': new_learning_path.description,
                'difficulty_level': new_learning_path.difficulty_level,
                'estimated_duration_hours': new_learning_path.estimated_duration_hours,
                'activities_count': len(activities_created)
            },
            'generated_structure': path_structure,
            'activities_created': activities_created,
            'next_steps': [
                'Enroll in your custom path',
                'Start with the first activity',
                'Track your progress',
                'Provide feedback for improvements'
            ]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create custom learning path',
            'telugu_message': 'అనుకూల అభ్యాస మార్గం సృష్టించడంలో విఫలం',
            'details': str(e)
        }), 500

@learning_path_bp.route('/adaptive-difficulty', methods=['POST'])
@jwt_required()
def adjust_adaptive_difficulty():
    """Adjust learning path difficulty based on user performance"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Performance data required',
                'telugu_message': 'పనితీరు డేటా అవసరం'
            }), 400
        
        learning_path_id = data.get('learning_path_id')
        if not learning_path_id:
            return jsonify({
                'error': 'Learning path ID required',
                'telugu_message': 'అభ్యాస మార్గ ID అవసరం'
            }), 400
        
        # Get user's recent performance in this learning path
        recent_logs = UserActivityLog.query.filter_by(
            user_id=user_id, learning_path_id=learning_path_id
        ).order_by(UserActivityLog.completed_at.desc()).limit(10).all()
        
        if not recent_logs:
            return jsonify({
                'error': 'No performance data found',
                'telugu_message': 'పనితీరు డేటా కనుగొనబడలేదు'
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
