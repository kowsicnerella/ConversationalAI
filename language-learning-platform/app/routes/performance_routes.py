"""
Phase 4: Performance Tracking API Routes
Endpoints for comprehensive performance tracking and analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

from app.services.performance_tracking_service import PerformanceTrackingEngine
from app.models import db
from app.models.performance_tracking import (
    ListeningPerformance,
    SpeakingPerformance,
    ReadingPerformance,
    WritingPerformance,
    RealWorldPerformance,
    SkillTrajectory
)

performance_bp = Blueprint('performance', __name__)
tracking_engine = PerformanceTrackingEngine()


# ================== VALIDATION DECORATORS ==================

def validate_json(required_fields=None):
    """Decorator to validate JSON request body"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'error': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            if data is None:
                return jsonify({
                    'error': 'Invalid JSON payload'
                }), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_skill_domain(f):
    """Decorator to validate skill domain parameter"""
    @wraps(f)
    def decorated_function(skill_domain, *args, **kwargs):
        valid_domains = ['listening', 'speaking', 'reading', 'writing', 'real_world']
        if skill_domain not in valid_domains:
            return jsonify({
                'error': f'Invalid skill domain. Must be one of: {", ".join(valid_domains)}'
            }), 400
        return f(skill_domain, *args, **kwargs)
    return decorated_function


def handle_errors(f):
    """Decorator to handle common errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
        except Exception as e:
            print(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'error': 'An unexpected error occurred',
                'details': str(e) if request.args.get('debug') else None
            }), 500
    return decorated_function


# ================== PERFORMANCE TRACKING ENDPOINTS ==================

@performance_bp.route('/listening', methods=['POST'])
@jwt_required()
@validate_json(required_fields=['audio_duration', 'comprehension_score', 'difficulty_level'])
@handle_errors
def track_listening_performance():
    """
    Track listening comprehension performance
    
    Request body:
    {
        "activity_id": 123,
        "session_id": "session-uuid",
        "audio_duration": 120.5,
        "audio_url": "https://...",
        "accent_type": "american",
        "speed_factor": 1.0,
        "topic": "Travel",
        "difficulty_level": "intermediate",
        "comprehension_score": 85.5,
        "accuracy_percentage": 80.0,
        "playback_count": 2,
        "pause_points": [30.5, 45.2, 90.1],
        "replay_sections": [[20, 35], [80, 95]],
        "difficult_words": ["vocabulary", "pronunciation"],
        "new_vocabulary": ["idiom", "phrase"],
        "total_questions": 10,
        "correct_answers": 8,
        "time_to_complete": 300,
        ...
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    performance = tracking_engine.track_listening_performance(
        user_id=user_id,
        activity_id=data.get('activity_id'),
        performance_data=data
    )
    
    return jsonify({
        'success': True,
        'message': 'Listening performance tracked successfully',
        'performance': performance.to_dict()
    }), 201


@performance_bp.route('/speaking', methods=['POST'])
@jwt_required()
def track_speaking_performance():
    """
    Track speaking performance
    
    Request body includes pronunciation, fluency, grammar, vocabulary metrics
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        performance = tracking_engine.track_speaking_performance(
            user_id=user_id,
            activity_id=data.get('activity_id'),
            performance_data=data
        )
        
        return jsonify({
            'success': True,
            'message': 'Speaking performance tracked successfully',
            'performance': performance.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/reading', methods=['POST'])
@jwt_required()
def track_reading_performance():
    """
    Track reading comprehension performance
    
    Request body includes reading speed, comprehension, vocabulary metrics
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        performance = tracking_engine.track_reading_performance(
            user_id=user_id,
            activity_id=data.get('activity_id'),
            performance_data=data
        )
        
        return jsonify({
            'success': True,
            'message': 'Reading performance tracked successfully',
            'performance': performance.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/writing', methods=['POST'])
@jwt_required()
def track_writing_performance():
    """
    Track writing performance
    
    Request body includes grammar, vocabulary, coherence, structure metrics
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        performance = tracking_engine.track_writing_performance(
            user_id=user_id,
            activity_id=data.get('activity_id'),
            performance_data=data
        )
        
        return jsonify({
            'success': True,
            'message': 'Writing performance tracked successfully',
            'performance': performance.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/real-world', methods=['POST'])
@jwt_required()
def track_real_world_performance():
    """
    Track real-world scenario performance
    
    Request body includes task completion, appropriateness, professional language metrics
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        performance = tracking_engine.track_real_world_performance(
            user_id=user_id,
            activity_id=data.get('activity_id'),
            performance_data=data
        )
        
        return jsonify({
            'success': True,
            'message': 'Real-world performance tracked successfully',
            'performance': performance.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================== ANALYTICS ENDPOINTS ==================

@performance_bp.route('/trajectory/<skill_domain>', methods=['GET'])
@jwt_required()
@validate_skill_domain
@handle_errors
def get_skill_trajectory(skill_domain):
    """
    Get skill trajectory analysis
    
    Query params:
    - time_window_days: Number of days to analyze (default: 30)
    
    Skill domains: listening, speaking, reading, writing, real_world
    """
    user_id = get_jwt_identity()
    time_window = request.args.get('time_window_days', 30, type=int)
    
    analysis = tracking_engine.analyze_skill_trajectory(
        user_id=user_id,
        skill_domain=skill_domain,
        time_window_days=time_window
    )
    
    return jsonify(analysis), 200


@performance_bp.route('/patterns', methods=['GET'])
@jwt_required()
def get_learning_patterns():
    """
    Identify user's learning patterns
    
    Returns:
    - Best learning times
    - Optimal session length
    - Preferred activity types
    - Struggle patterns
    - Breakthrough moments
    """
    try:
        user_id = get_jwt_identity()
        
        patterns = tracking_engine.identify_learning_patterns(user_id)
        
        return jsonify(patterns), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/mastery-prediction/<skill_domain>', methods=['GET'])
@jwt_required()
@validate_skill_domain
@handle_errors
def predict_mastery(skill_domain):
    """
    Predict when user will master a skill
    
    Returns estimated timeline, confidence level, and recommendations
    """
    user_id = get_jwt_identity()
    
    prediction = tracking_engine.predict_mastery_timeline(
        user_id=user_id,
        skill_domain=skill_domain
    )
    
    return jsonify(prediction), 200


@performance_bp.route('/all-trajectories', methods=['GET'])
@jwt_required()
def get_all_trajectories():
    """
    Get all skill trajectories for the user
    """
    try:
        user_id = get_jwt_identity()
        
        trajectories = db.session.query(SkillTrajectory).filter_by(
            user_id=user_id
        ).all()
        
        return jsonify({
            'trajectories': [t.to_dict() for t in trajectories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================== PERFORMANCE HISTORY ENDPOINTS ==================

@performance_bp.route('/history/listening', methods=['GET'])
@jwt_required()
def get_listening_history():
    """
    Get listening performance history
    
    Query params:
    - limit: Number of records (default: 20)
    - offset: Pagination offset (default: 0)
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        performances = db.session.query(ListeningPerformance).filter_by(
            user_id=user_id
        ).order_by(ListeningPerformance.completed_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'performances': [p.to_dict() for p in performances],
            'total': db.session.query(ListeningPerformance).filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/history/speaking', methods=['GET'])
@jwt_required()
def get_speaking_history():
    """Get speaking performance history"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        performances = db.session.query(SpeakingPerformance).filter_by(
            user_id=user_id
        ).order_by(SpeakingPerformance.completed_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'performances': [p.to_dict() for p in performances],
            'total': db.session.query(SpeakingPerformance).filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/history/reading', methods=['GET'])
@jwt_required()
def get_reading_history():
    """Get reading performance history"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        performances = db.session.query(ReadingPerformance).filter_by(
            user_id=user_id
        ).order_by(ReadingPerformance.completed_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'performances': [p.to_dict() for p in performances],
            'total': db.session.query(ReadingPerformance).filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/history/writing', methods=['GET'])
@jwt_required()
def get_writing_history():
    """Get writing performance history"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        performances = db.session.query(WritingPerformance).filter_by(
            user_id=user_id
        ).order_by(WritingPerformance.completed_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'performances': [p.to_dict() for p in performances],
            'total': db.session.query(WritingPerformance).filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/history/real-world', methods=['GET'])
@jwt_required()
def get_real_world_history():
    """Get real-world performance history"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        performances = db.session.query(RealWorldPerformance).filter_by(
            user_id=user_id
        ).order_by(RealWorldPerformance.completed_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'performances': [p.to_dict() for p in performances],
            'total': db.session.query(RealWorldPerformance).filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ================== DETAILED PERFORMANCE ENDPOINTS ==================

@performance_bp.route('/listening/<int:performance_id>', methods=['GET'])
@jwt_required()
def get_listening_detail(performance_id):
    """Get detailed listening performance record"""
    try:
        user_id = get_jwt_identity()
        
        performance = db.session.query(ListeningPerformance).filter_by(
            id=performance_id,
            user_id=user_id
        ).first()
        
        if not performance:
            return jsonify({'error': 'Performance record not found'}), 404
        
        return jsonify(performance.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/speaking/<int:performance_id>', methods=['GET'])
@jwt_required()
def get_speaking_detail(performance_id):
    """Get detailed speaking performance record"""
    try:
        user_id = get_jwt_identity()
        
        performance = db.session.query(SpeakingPerformance).filter_by(
            id=performance_id,
            user_id=user_id
        ).first()
        
        if not performance:
            return jsonify({'error': 'Performance record not found'}), 404
        
        return jsonify(performance.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@performance_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_performance_dashboard():
    """
    Get comprehensive performance dashboard
    
    Returns overview of all skills with current levels, trends, and insights
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all trajectories
        trajectories = db.session.query(SkillTrajectory).filter_by(
            user_id=user_id
        ).all()
        
        # Get recent performance across all skills
        dashboard = {
            'skill_overview': [t.to_dict() for t in trajectories],
            'learning_patterns': tracking_engine.identify_learning_patterns(user_id),
        }
        
        # Add mastery predictions for each skill
        predictions = {}
        for skill in ['listening', 'speaking', 'reading', 'writing', 'real_world']:
            try:
                prediction = tracking_engine.predict_mastery_timeline(user_id, skill)
                predictions[skill] = prediction
            except:
                pass
        
        dashboard['mastery_predictions'] = predictions
        
        return jsonify(dashboard), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
