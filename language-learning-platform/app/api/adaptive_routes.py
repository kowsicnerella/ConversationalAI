from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.adaptive_learning_service import AdaptiveLearningAlgorithm
from app.models import User, Activity, UserActivityLog
from app.models import db
from typing import Dict, List
import traceback

adaptive_routes = Blueprint('adaptive', __name__)
adaptive_service = AdaptiveLearningAlgorithm()


@adaptive_routes.route('/api/adaptive/performance-analysis', methods=['GET'])
@jwt_required()
def get_performance_analysis():
    """
    Get comprehensive performance analysis for the current user.
    Query Parameters:
    - days: Number of days to analyze (default: 7)
    """
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 7, type=int)
        
        # Validate days parameter
        if days < 1 or days > 90:
            return jsonify({
                'error': 'Days parameter must be between 1 and 90',
                'telugu_error': 'రోజుల సంఖ్య 1 మరియు 90 మధ్య ఉండాలి'
            }), 400
        
        performance = adaptive_service.analyze_user_performance(user_id, days)
        
        return jsonify({
            'success': True,
            'performance_analysis': performance,
            'recommendations': {
                'overall_level': _get_performance_level(performance['overall_accuracy']),
                'areas_for_improvement': _identify_improvement_areas(performance),
                'strengths': _identify_strengths(performance)
            },
            'telugu_summary': _generate_telugu_performance_summary(performance),
            'analysis_timestamp': performance.get('analysis_timestamp', 'just_now')
        }), 200
        
    except Exception as e:
        print(f"Error in performance analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to analyze performance',
            'telugu_error': 'పనితీరు విశ్లేషణలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/next-activities', methods=['GET'])
@jwt_required()
def get_next_activities():
    """
    Get personalized activity recommendations based on adaptive learning algorithm.
    Query Parameters:
    - learning_path_id: Specific learning path (optional)
    - count: Number of recommendations (default: 5, max: 10)
    """
    try:
        user_id = get_jwt_identity()
        learning_path_id = request.args.get('learning_path_id', type=int)
        count = request.args.get('count', 5, type=int)
        
        # Validate count parameter
        if count < 1 or count > 10:
            return jsonify({
                'error': 'Count must be between 1 and 10',
                'telugu_error': 'సంఖ్య 1 మరియు 10 మధ్య ఉండాలి'
            }), 400
        
        recommendations = adaptive_service.recommend_next_activities(
            user_id, learning_path_id, count
        )
        
        if not recommendations:
            return jsonify({
                'success': True,
                'recommendations': [],
                'message': 'No activities available for recommendation',
                'telugu_message': 'సిఫార్సు చేయడానికి కార్యకలాపాలు లేవు',
                'suggestion': 'Complete more activities to get better recommendations'
            }), 200
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_count': len(recommendations),
            'learning_path_id': learning_path_id,
            'personalization_factors': [
                'Performance history',
                'Learning gaps analysis',
                'Difficulty progression',
                'Activity type preferences',
                'Time availability'
            ],
            'telugu_message': f"{len(recommendations)} వ్యక్తిగతీకరించిన కార్యకలాపాలు సిఫార్సు చేయబడ్డాయి"
        }), 200
        
    except Exception as e:
        print(f"Error in activity recommendations: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to get activity recommendations',
            'telugu_error': 'కార్యకలాప సిఫార్సులు పొందడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/adjust-difficulty', methods=['POST'])
@jwt_required()
def adjust_difficulty():
    """
    Dynamically adjust difficulty based on user performance.
    Expected JSON body:
    {
        "activity_id": 123,
        "user_performance": {
            "accuracy": 0.85,
            "time_spent_minutes": 15,
            "attempts": 2
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'telugu_error': 'అభ్యర్థన విషయం అవసరం'
            }), 400
        
        activity_id = data.get('activity_id')
        user_performance = data.get('user_performance', {})
        
        if not activity_id:
            return jsonify({
                'error': 'activity_id is required',
                'telugu_error': 'కార్యకలాపం ID అవసరం'
            }), 400
        
        # Validate activity exists
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({
                'error': 'Activity not found',
                'telugu_error': 'కార్యకలాపం కనుగొనబడలేదు'
            }), 404
        
        adjustment = adaptive_service.adjust_difficulty_dynamically(
            user_id, activity_id, user_performance
        )
        
        return jsonify({
            'success': True,
            'difficulty_adjustment': adjustment,
            'activity_info': {
                'id': activity.id,
                'title': activity.title,
                'current_difficulty': activity.difficulty_level,
                'activity_type': activity.activity_type
            },
            'user_performance_summary': user_performance
        }), 200
        
    except Exception as e:
        print(f"Error in difficulty adjustment: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to adjust difficulty',
            'telugu_error': 'కష్టతను సర్దుబాటు చేయడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/learning-gaps', methods=['GET'])
@jwt_required()
def identify_learning_gaps():
    """
    Identify specific learning gaps and recommend targeted interventions.
    """
    try:
        user_id = get_jwt_identity()
        
        gaps_analysis = adaptive_service.identify_learning_gaps(user_id)
        
        return jsonify({
            'success': True,
            'learning_gaps_analysis': gaps_analysis,
            'action_plan': _generate_gap_action_plan(gaps_analysis),
            'telugu_insights': _generate_telugu_gap_insights(gaps_analysis),
            'estimated_improvement_timeline': _calculate_improvement_timeline(gaps_analysis)
        }), 200
        
    except Exception as e:
        print(f"Error in learning gaps analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to analyze learning gaps',
            'telugu_error': 'అభ్యాస లోపాలను విశ్లేషించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/learning-pace', methods=['GET'])
@jwt_required()
def get_personalized_pace():
    """
    Get personalized learning pace recommendations.
    """
    try:
        user_id = get_jwt_identity()
        
        pace_analysis = adaptive_service.personalize_learning_pace(user_id)
        
        return jsonify({
            'success': True,
            'learning_pace_analysis': pace_analysis,
            'implementation_guide': _generate_pace_implementation_guide(pace_analysis),
            'telugu_guidance': _generate_telugu_pace_guidance(pace_analysis),
            'monitoring_metrics': _get_pace_monitoring_metrics()
        }), 200
        
    except Exception as e:
        print(f"Error in learning pace analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to analyze learning pace',
            'telugu_error': 'అభ్యాస వేగాన్ని విశ్లేషించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/generate-exercise', methods=['POST'])
@jwt_required()
def generate_adaptive_exercise():
    """
    Generate a custom exercise adapted to user's skill level.
    Expected JSON body:
    {
        "topic": "Daily Conversations",
        "skill_area": "speaking"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'telugu_error': 'అభ్యర్థన విषయం అవసరం'
            }), 400
        
        topic = data.get('topic')
        skill_area = data.get('skill_area')
        
        if not topic or not skill_area:
            return jsonify({
                'error': 'Both topic and skill_area are required',
                'telugu_error': 'అంశం మరియు నైపుణ్య రంగం రెండూ అవసరం'
            }), 400
        
        # Validate skill area
        valid_skill_areas = ['vocabulary', 'grammar', 'reading', 'writing', 'speaking', 'listening']
        if skill_area not in valid_skill_areas:
            return jsonify({
                'error': f'Invalid skill_area. Must be one of: {", ".join(valid_skill_areas)}',
                'telugu_error': 'చెల్లని నైపుణ్య రంగం'
            }), 400
        
        adaptive_exercise = adaptive_service.generate_adaptive_exercise(
            user_id, topic, skill_area
        )
        
        return jsonify({
            'success': True,
            'adaptive_exercise': adaptive_exercise,
            'generation_metadata': {
                'topic': topic,
                'skill_area': skill_area,
                'user_id': user_id,
                'generation_timestamp': 'now'
            },
            'telugu_message': f"{topic} అంశంపై {skill_area} నైపుణ్యం కోసం వ్యక్తిగతీకరించిన వ్యాయామం రూపొందించబడింది"
        }), 200
        
    except Exception as e:
        print(f"Error in adaptive exercise generation: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate adaptive exercise',
            'telugu_error': 'అనుకూల వ్యాయామం రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@adaptive_routes.route('/api/adaptive/learning-profile', methods=['GET'])
@jwt_required()
def get_comprehensive_learning_profile():
    """
    Get comprehensive adaptive learning profile combining all aspects.
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all components of the learning profile
        performance = adaptive_service.analyze_user_performance(user_id, days=14)
        gaps = adaptive_service.identify_learning_gaps(user_id)
        pace = adaptive_service.personalize_learning_pace(user_id)
        recommendations = adaptive_service.recommend_next_activities(user_id, count=3)
        
        # Get user info
        user = User.query.get(user_id)
        
        profile = {
            'user_info': {
                'id': user.id,
                'username': user.username,
                'total_activities_completed': UserActivityLog.query.filter_by(user_id=user_id).count(),
                'profile_generated_at': 'now'
            },
            'performance_overview': {
                'overall_accuracy': performance.get('overall_accuracy', 0),
                'total_activities': performance.get('total_activities', 0),
                'performance_trend': performance.get('performance_trend', 'stable'),
                'consistency_score': performance.get('consistency', 0)
            },
            'learning_gaps_summary': {
                'priority_areas': [gap['skill'] for gap in gaps.get('prioritized_gaps', [])[:3]],
                'improvement_areas': len([gap for gap in gaps.get('prioritized_gaps', []) if gap.get('gap_data', {}).get('gap_level') == 'high']),
                'overall_assessment': gaps.get('overall_assessment', {})
            },
            'optimal_learning_pace': pace.get('optimal_pace_recommendation', {}),
            'personalized_recommendations': recommendations[:3],
            'adaptive_insights': {
                'learning_style_indicators': _analyze_learning_style(performance),
                'motivation_factors': _identify_motivation_factors(user_id, performance),
                'success_predictors': _calculate_success_predictors(performance, gaps)
            }
        }
        
        return jsonify({
            'success': True,
            'comprehensive_learning_profile': profile,
            'telugu_summary': _generate_comprehensive_telugu_summary(profile),
            'actionable_insights': _generate_actionable_insights(profile)
        }), 200
        
    except Exception as e:
        print(f"Error in comprehensive learning profile: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate learning profile',
            'telugu_error': 'అభ్యాస ప్రొఫైల్ రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


# Helper functions

def _get_performance_level(accuracy: float) -> str:
    """Determine performance level based on accuracy."""
    if accuracy >= 0.85:
        return 'excellent'
    elif accuracy >= 0.7:
        return 'good'
    elif accuracy >= 0.5:
        return 'developing'
    else:
        return 'needs_support'


def _identify_improvement_areas(performance: Dict) -> List[str]:
    """Identify areas that need improvement."""
    areas = []
    
    for activity_type, score in performance.get('activity_type_performance', {}).items():
        if score < 0.6:
            areas.append(activity_type)
    
    for difficulty, score in performance.get('difficulty_performance', {}).items():
        if score < 0.6:
            areas.append(f"{difficulty}_level")
    
    return areas[:3]  # Return top 3


def _identify_strengths(performance: Dict) -> List[str]:
    """Identify user's strengths."""
    strengths = []
    
    for activity_type, score in performance.get('activity_type_performance', {}).items():
        if score >= 0.8:
            strengths.append(activity_type)
    
    if performance.get('consistency', 0) >= 0.8:
        strengths.append('consistent_learning')
    
    if performance.get('time_efficiency', 0) >= 0.8:
        strengths.append('time_efficient')
    
    return strengths


def _generate_telugu_performance_summary(performance: Dict) -> str:
    """Generate Telugu summary of performance."""
    accuracy = performance.get('overall_accuracy', 0)
    total_activities = performance.get('total_activities', 0)
    
    if accuracy >= 0.8:
        summary = f"మీ పనితీరు అద్భుతంగా ఉంది! {total_activities} కార్యకలాపాలలో {accuracy:.1%} ఖచ్చితత్వం"
    elif accuracy >= 0.6:
        summary = f"మీ పనితీరు మంచిగా ఉంది. {total_activities} కార్యకలాపాలలో {accuracy:.1%} ఖచ్చితత్వంతో మెరుగుపడుతూ ఉంది"
    else:
        summary = f"మరింత అభ్యాసం అవసరం. {total_activities} కార్యకలాపాలలో {accuracy:.1%} ఖచ్చితత్వం - మెరుగుపరచుకోవచ్చు"
    
    return summary


def _generate_gap_action_plan(gaps_analysis: Dict) -> Dict:
    """Generate actionable plan for addressing learning gaps."""
    priority_gaps = gaps_analysis.get('prioritized_gaps', [])[:3]
    
    action_plan = {
        'immediate_actions': [],
        'weekly_goals': [],
        'monthly_objectives': []
    }
    
    for gap in priority_gaps:
        skill = gap['skill']
        action_plan['immediate_actions'].append(f"Start daily {skill} practice")
        action_plan['weekly_goals'].append(f"Complete 5 {skill} activities")
        action_plan['monthly_objectives'].append(f"Achieve 70%+ accuracy in {skill}")
    
    return action_plan


def _generate_telugu_gap_insights(gaps_analysis: Dict) -> List[str]:
    """Generate Telugu insights about learning gaps."""
    insights = []
    
    priority_gaps = gaps_analysis.get('prioritized_gaps', [])
    for gap in priority_gaps[:2]:
        skill = gap['skill']
        insights.append(f"{skill} నైపుణ్యంలో మరింత దృష్టి పెట్టాలి")
    
    if gaps_analysis.get('overall_assessment', {}).get('overall_level') == 'needs_attention':
        insights.append("కొన్ని రంగాలలో అదనపు దృష్టి అవసరం")
    else:
        insights.append("మీ పురోగతి మంచిగా ఉంది")
    
    return insights


def _calculate_improvement_timeline(gaps_analysis: Dict) -> Dict:
    """Calculate realistic timeline for improvement."""
    priority_gaps = gaps_analysis.get('prioritized_gaps', [])
    high_priority_count = len([gap for gap in priority_gaps if gap.get('gap_data', {}).get('gap_level') == 'high'])
    
    return {
        'short_term_improvements': f"{2 + high_priority_count} weeks",
        'significant_progress': f"{4 + high_priority_count * 2} weeks",
        'mastery_level': f"{8 + high_priority_count * 3} weeks"
    }


def _generate_pace_implementation_guide(pace_analysis: Dict) -> Dict:
    """Generate implementation guide for optimal learning pace."""
    optimal_pace = pace_analysis.get('optimal_pace_recommendation', {})
    
    return {
        'daily_routine': f"Spend {optimal_pace.get('optimal_session_length_minutes', 20)} minutes per session",
        'frequency': f"Practice {optimal_pace.get('optimal_sessions_per_day', 1)} times daily",
        'weekly_commitment': f"Total {optimal_pace.get('weekly_time_commitment', 140)} minutes per week",
        'intensity_level': optimal_pace.get('pace_intensity', 'moderate')
    }


def _generate_telugu_pace_guidance(pace_analysis: Dict) -> List[str]:
    """Generate Telugu guidance for learning pace."""
    optimal_pace = pace_analysis.get('optimal_pace_recommendation', {})
    guidance = []
    
    sessions_per_day = optimal_pace.get('optimal_sessions_per_day', 1)
    session_length = optimal_pace.get('optimal_session_length_minutes', 20)
    
    guidance.append(f"రోజుకు {sessions_per_day} సార్లు అభ్यసించండి")
    guidance.append(f"ప్రతి సెషన్ {session_length} నిమిషాలు కొనసాగించండి")
    
    if optimal_pace.get('pace_intensity') == 'intensive':
        guidance.append("మీరు వేగవంతమైన అభ్యాసం చేయగలరు")
    else:
        guidance.append("స్థిరమైన అభ్యాసం చేయండి")
    
    return guidance


def _get_pace_monitoring_metrics() -> List[str]:
    """Get metrics for monitoring learning pace effectiveness."""
    return [
        'Daily activity completion rate',
        'Average session duration',
        'Weekly consistency score',
        'Performance improvement rate',
        'Engagement and motivation levels'
    ]


def _analyze_learning_style(performance: Dict) -> List[str]:
    """Analyze learning style indicators from performance data."""
    indicators = []
    
    activity_performance = performance.get('activity_type_performance', {})
    
    if activity_performance.get('visual', 0) > 0.8:
        indicators.append('visual_learner')
    if activity_performance.get('reading', 0) > 0.8:
        indicators.append('text_oriented')
    if activity_performance.get('listening', 0) > 0.8:
        indicators.append('auditory_learner')
    if activity_performance.get('quiz', 0) > 0.8:
        indicators.append('assessment_driven')
    
    if performance.get('consistency', 0) > 0.8:
        indicators.append('systematic_learner')
    
    return indicators


def _identify_motivation_factors(user_id: int, performance: Dict) -> List[str]:
    """Identify factors that motivate the user."""
    factors = []
    
    if performance.get('performance_trend') == 'improving':
        factors.append('progress_motivated')
    
    if performance.get('total_activities', 0) > 50:
        factors.append('high_engagement')
    
    if performance.get('consistency', 0) > 0.7:
        factors.append('routine_oriented')
    
    factors.append('achievement_oriented')  # Default assumption
    
    return factors


def _calculate_success_predictors(performance: Dict, gaps: Dict) -> Dict:
    """Calculate predictors of learning success."""
    consistency = performance.get('consistency', 0)
    overall_accuracy = performance.get('overall_accuracy', 0)
    total_activities = performance.get('total_activities', 0)
    
    # Calculate success probability
    success_score = (consistency * 0.4 + overall_accuracy * 0.4 + min(total_activities / 100, 1) * 0.2)
    
    return {
        'success_probability': round(success_score, 2),
        'key_factors': [
            f"Consistency: {consistency:.1%}",
            f"Accuracy: {overall_accuracy:.1%}",
            f"Engagement: {min(total_activities / 100, 1):.1%}"
        ],
        'improvement_potential': 'high' if success_score > 0.7 else 'medium' if success_score > 0.4 else 'needs_support'
    }


def _generate_comprehensive_telugu_summary(profile: Dict) -> str:
    """Generate comprehensive Telugu summary of learning profile."""
    performance = profile.get('performance_overview', {})
    accuracy = performance.get('overall_accuracy', 0)
    total_activities = performance.get('total_activities', 0)
    
    if accuracy >= 0.8:
        summary = f"మీ అభ్యాస ప్రయాణం అద్భుతంగా సాగుతోంది! {total_activities} కార్యకలాపాలతో {accuracy:.1%} విజయ రేటు"
    elif accuracy >= 0.6:
        summary = f"మీరు బాగా ముందుకు వెళ్తున్నారు. {total_activities} కార్యకలాపాలలో మంచి పురోగతి"
    else:
        summary = f"మీ అభ్యాస ప్రయాణం మొదలైంది. {total_activities} కార్యకలాపాలతో మెరుగుపడుతున్నారు"
    
    return summary


def _generate_actionable_insights(profile: Dict) -> List[Dict]:
    """Generate actionable insights from the learning profile."""
    insights = []
    
    performance = profile.get('performance_overview', {})
    gaps = profile.get('learning_gaps_summary', {})
    pace = profile.get('optimal_learning_pace', {})
    
    # Performance insight
    if performance.get('overall_accuracy', 0) < 0.6:
        insights.append({
            'category': 'performance',
            'insight': 'Focus on accuracy improvement',
            'action': 'Review incorrect answers and practice similar questions',
            'priority': 'high'
        })
    
    # Pace insight
    if pace.get('pace_intensity') == 'intensive':
        insights.append({
            'category': 'pace',
            'insight': 'You can handle more challenging content',
            'action': 'Increase difficulty level or add more practice sessions',
            'priority': 'medium'
        })
    
    # Gaps insight
    priority_areas = gaps.get('priority_areas', [])
    if priority_areas:
        insights.append({
            'category': 'gaps',
            'insight': f'Focus on {", ".join(priority_areas[:2])} skills',
            'action': 'Complete targeted exercises in these areas',
            'priority': 'high'
        })
    
    return insights