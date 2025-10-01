from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.comprehensive_assessment_service import ComprehensiveAssessmentService
from app.services.adaptive_learning_path_generator import AdaptiveLearningPathGenerator
from app.services.real_time_performance_monitor import RealTimePerformanceMonitor
from app.services.adaptive_learning_service import AdaptiveLearningAlgorithm
from app.models import db, User, LearningPath, Activity, UserActivityLog
from datetime import datetime
import logging

adaptive_learning_bp = Blueprint('adaptive_learning', __name__)

# Initialize services
assessment_service = ComprehensiveAssessmentService()
path_generator = AdaptiveLearningPathGenerator()
performance_monitor = RealTimePerformanceMonitor()
adaptive_algorithm = AdaptiveLearningAlgorithm()


@adaptive_learning_bp.route('/assessment/comprehensive/start', methods=['POST'])
@jwt_required()
def start_comprehensive_assessment():
    """
    Start a comprehensive initial assessment for a user.
    """
    try:
        user_id = int(get_jwt_identity())
        
        assessment_result = assessment_service.conduct_comprehensive_assessment(user_id)
        
        if 'error' in assessment_result:
            return jsonify({
                'error': assessment_result['error'],
                'telugu_message': 'మూల్యాంకనం ప్రారంభించడంలో సమస్య'
            }), 500
        
        return jsonify({
            'message': 'Comprehensive assessment started successfully',
            'telugu_message': 'సమగ్ర మూల్యాంకనం విజయవంతంగా ప్రారంభమైంది',
            'assessment': assessment_result
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error starting comprehensive assessment: {str(e)}")
        return jsonify({
            'error': 'Failed to start assessment',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/assessment/<int:assessment_id>/respond', methods=['POST'])
@jwt_required()
def submit_assessment_response():
    """
    Submit a response to an assessment question.
    """
    try:
        user_id = int(get_jwt_identity())
        assessment_id = request.view_args['assessment_id']
        data = request.get_json()
        
        question_id = data.get('question_id')
        user_response = data.get('user_response')
        response_type = data.get('response_type', 'text')
        
        if not question_id or not user_response:
            return jsonify({
                'error': 'Question ID and response are required',
                'telugu_message': 'ప్రశ్న ID మరియు సమాధానం అవసరం'
            }), 400
        
        evaluation_result = assessment_service.evaluate_assessment_response(
            assessment_id, question_id, user_response, response_type
        )
        
        if 'error' in evaluation_result:
            return jsonify({'error': evaluation_result['error']}), 500
        
        return jsonify({
            'message': 'Response evaluated successfully',
            'telugu_message': 'సమాధానం విజయవంతంగా మూల్యాంకనం చేయబడింది',
            'evaluation': evaluation_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error evaluating assessment response: {str(e)}")
        return jsonify({
            'error': 'Failed to evaluate response',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/assessment/<int:assessment_id>/complete', methods=['POST'])
@jwt_required()
def complete_assessment():
    """
    Complete the assessment and generate learning path.
    """
    try:
        user_id = int(get_jwt_identity())
        assessment_id = request.view_args['assessment_id']
        
        # Finalize assessment
        assessment_result = assessment_service.finalize_assessment(assessment_id)
        
        if 'error' in assessment_result:
            return jsonify({'error': assessment_result['error']}), 500
        
        # Generate personalized learning path
        learning_path_result = path_generator.generate_personalized_learning_path(
            user_id, assessment_id
        )
        
        if 'error' in learning_path_result:
            return jsonify({
                'assessment_completed': True,
                'assessment_results': assessment_result,
                'learning_path_error': learning_path_result['error']
            }), 200
        
        return jsonify({
            'message': 'Assessment completed and learning path generated!',
            'telugu_message': 'మూల్యాంకనం పూర్తయ్యింది మరియు అభ్యాస మార్గం రూపొందించబడింది!',
            'assessment_results': assessment_result,
            'learning_path': learning_path_result,
            'next_step': 'start_first_activity'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error completing assessment: {str(e)}")
        return jsonify({
            'error': 'Failed to complete assessment',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/learning-path/<int:path_id>/next-activity', methods=['GET'])
@jwt_required()
def get_next_adaptive_activity():
    """
    Get the next adaptive activity based on user's progress and performance.
    """
    try:
        user_id = int(get_jwt_identity())
        path_id = request.view_args['path_id']
        
        # Get performance data for last activity if provided
        last_performance = request.args.get('last_performance')
        performance_data = None
        
        if last_performance:
            try:
                performance_data = eval(last_performance)  # In production, use proper JSON parsing
            except:
                performance_data = None
        
        next_activity_result = path_generator.get_next_adaptive_activity(
            user_id, path_id, performance_data
        )
        
        if 'error' in next_activity_result:
            return jsonify({'error': next_activity_result['error']}), 500
        
        return jsonify({
            'message': 'Next activity generated successfully',
            'telugu_message': 'తదుపరి కార్యకలాపం విజయవంతంగా రూపొందించబడింది',
            'next_activity': next_activity_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting next activity: {str(e)}")
        return jsonify({
            'error': 'Failed to get next activity',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/activity/<int:activity_id>/start-session', methods=['POST'])
@jwt_required()
def start_activity_session():
    """
    Start a monitored learning session for real-time adaptation.
    """
    try:
        user_id = int(get_jwt_identity())
        activity_id = request.view_args['activity_id']
        
        session_result = performance_monitor.start_learning_session(user_id, activity_id)
        
        if 'error' in session_result:
            return jsonify({'error': session_result['error']}), 500
        
        return jsonify({
            'message': 'Learning session started with real-time monitoring',
            'telugu_message': 'నిజ-సమయ పర్యవేక్షణతో అభ్యాస సెషన్ ప్రారంభమైంది',
            'session': session_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error starting activity session: {str(e)}")
        return jsonify({
            'error': 'Failed to start session',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/session/track-interaction', methods=['POST'])
@jwt_required()
def track_user_interaction():
    """
    Track user interaction during learning session for real-time adaptation.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['is_correct', 'response_time_seconds']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'{field} is required',
                    'telugu_message': f'{field} అవసరం'
                }), 400
        
        tracking_result = performance_monitor.track_user_interaction(user_id, data)
        
        if 'error' in tracking_result:
            return jsonify({'error': tracking_result['error']}), 500
        
        return jsonify({
            'message': 'Interaction tracked successfully',
            'telugu_message': 'పరస్పర చర్య విజయవంతంగా ట్రాక్ చేయబడింది',
            'tracking_result': tracking_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error tracking interaction: {str(e)}")
        return jsonify({
            'error': 'Failed to track interaction',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/session/end', methods=['POST'])
@jwt_required()
def end_learning_session():
    """
    End the learning session and get performance summary.
    """
    try:
        user_id = int(get_jwt_identity())
        
        session_summary = performance_monitor.end_learning_session(user_id)
        
        if 'error' in session_summary:
            return jsonify({'error': session_summary['error']}), 500
        
        return jsonify({
            'message': 'Learning session completed successfully',
            'telugu_message': 'అభ్యాస సెషన్ విజయవంతంగా పూర్తయ్యింది',
            'session_summary': session_summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error ending session: {str(e)}")
        return jsonify({
            'error': 'Failed to end session',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/concept/<skill_area>/<concept>/mastery-check', methods=['POST'])
@jwt_required()
def check_concept_mastery():
    """
    Check if user has mastered a specific concept.
    """
    try:
        user_id = int(get_jwt_identity())
        skill_area = request.view_args['skill_area']
        concept = request.view_args['concept']
        
        mastery_result = adaptive_algorithm.assess_concept_mastery(user_id, skill_area, concept)
        
        return jsonify({
            'message': 'Mastery assessment completed',
            'telugu_message': 'నైపుణ్య మూల్యాంకనం పూర్తయ్యింది',
            'mastery_assessment': mastery_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error checking concept mastery: {str(e)}")
        return jsonify({
            'error': 'Failed to assess mastery',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/learning-difficulties/detect', methods=['GET'])
@jwt_required()
def detect_learning_difficulties():
    """
    Detect learning difficulties and suggest interventions.
    """
    try:
        user_id = int(get_jwt_identity())
        skill_area = request.args.get('skill_area')
        
        difficulty_analysis = adaptive_algorithm.detect_learning_difficulties(user_id, skill_area)
        
        return jsonify({
            'message': 'Learning difficulty analysis completed',
            'telugu_message': 'అభ్యాస కష్టాల విశ్లేషణ పూర్తయ్యింది',
            'analysis': difficulty_analysis
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error detecting learning difficulties: {str(e)}")
        return jsonify({
            'error': 'Failed to analyze learning difficulties',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/spaced-repetition/<concept>/schedule', methods=['GET'])
@jwt_required()
def get_spaced_repetition_schedule():
    """
    Get spaced repetition schedule for a concept.
    """
    try:
        user_id = int(get_jwt_identity())
        concept = request.view_args['concept']
        
        repetition_schedule = adaptive_algorithm.implement_spaced_repetition(user_id, concept)
        
        return jsonify({
            'message': 'Spaced repetition schedule calculated',
            'telugu_message': 'అంతర పुनरावృత్తి షెడ్యూల్ లెక్కించబడింది',
            'schedule': repetition_schedule
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error calculating spaced repetition: {str(e)}")
        return jsonify({
            'error': 'Failed to calculate repetition schedule',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/learning-path/<int:path_id>/validate-mastery', methods=['POST'])
@jwt_required()
def validate_concept_mastery():
    """
    Validate concept mastery through multiple assessment methods.
    """
    try:
        user_id = int(get_jwt_identity())
        path_id = request.view_args['path_id']
        data = request.get_json()
        
        skill_area = data.get('skill_area')
        concept = data.get('concept')
        
        if not skill_area or not concept:
            return jsonify({
                'error': 'skill_area and concept are required',
                'telugu_message': 'నైపుణ్య క్షेత్రం మరియు భావన అవసరం'
            }), 400
        
        validation_result = path_generator.validate_concept_mastery(
            user_id, path_id, skill_area, concept
        )
        
        return jsonify({
            'message': 'Concept mastery validation initiated',
            'telugu_message': 'భావన నైపుణ్య ధృవీకరణ ప్రారంభించబడింది',
            'validation': validation_result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error validating concept mastery: {str(e)}")
        return jsonify({
            'error': 'Failed to validate mastery',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/performance/adaptive-content', methods=['POST'])
@jwt_required()
def generate_adaptive_content():
    """
    Generate adaptive content based on current performance.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        performance_data = data.get('performance_data', {})
        
        adaptive_content = performance_monitor.generate_adaptive_content(user_id, performance_data)
        
        if 'error' in adaptive_content:
            return jsonify({'error': adaptive_content['error']}), 500
        
        return jsonify({
            'message': 'Adaptive content generated successfully',
            'telugu_message': 'అనుకూల కంటెంట్ విజయవంతంగా రూపొందించబడింది',
            'adaptive_content': adaptive_content
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating adaptive content: {str(e)}")
        return jsonify({
            'error': 'Failed to generate adaptive content',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/user/progress-analytics', methods=['GET'])
@jwt_required()
def get_progress_analytics():
    """
    Get comprehensive progress analytics for the user.
    """
    try:
        user_id = int(get_jwt_identity())
        days = int(request.args.get('days', 7))
        
        progress_analysis = adaptive_algorithm.analyze_user_performance(user_id, days)
        
        return jsonify({
            'message': 'Progress analytics retrieved successfully',
            'telugu_message': 'ప్రగతి విశ్లేషణ విజయవంతంగా పొందబడింది',
            'analytics': progress_analysis,
            'analysis_period': f'Last {days} days'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting progress analytics: {str(e)}")
        return jsonify({
            'error': 'Failed to get progress analytics',
            'details': str(e)
        }), 500


@adaptive_learning_bp.route('/activity-recommendations', methods=['GET'])
@jwt_required()
def get_activity_recommendations():
    """
    Get AI-powered activity recommendations based on user performance.
    """
    try:
        user_id = int(get_jwt_identity())
        learning_path_id = request.args.get('learning_path_id', type=int)
        count = int(request.args.get('count', 5))
        
        recommendations = adaptive_algorithm.recommend_next_activities(
            user_id, learning_path_id, count
        )
        
        return jsonify({
            'message': 'Activity recommendations generated',
            'telugu_message': 'కార్యకలాప సిఫార్సులు రూపొందించబడ్లేయి',
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting activity recommendations: {str(e)}")
        return jsonify({
            'error': 'Failed to get recommendations',
            'details': str(e)
        }), 500