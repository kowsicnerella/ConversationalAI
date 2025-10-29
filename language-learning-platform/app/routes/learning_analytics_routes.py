"""
Learning Analytics Routes - Phase 7
REST API endpoints for comprehensive learning analytics and insights.

This is the Phase 7 analytics system with advanced features:
- Weekly AI-powered reports
- Progress visualization & predictions
- Peer comparisons & velocity tracking
- Study sessions & snapshots

The basic analytics_routes.py is Phase 4 and remains separate.

Author: GitHub Copilot
Date: October 20, 2025
Phase: 7 - Learning Analytics & Insights
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.learning_analytics_service import LearningAnalyticsService
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint with unique name to avoid conflicts with Phase 4 analytics
learning_analytics_bp = Blueprint('learning_analytics', __name__, url_prefix='/api/learning-analytics')

# Initialize service
analytics_service = LearningAnalyticsService()


# ============================================================
# WEEKLY REPORTS
# ============================================================

@learning_analytics_bp.route('/weekly-report', methods=['GET'])
@jwt_required()
def get_weekly_report():
    """
    Get weekly learning report.
    
    Query Parameters:
        week_offset (int): 0 for current week, -1 for last week, etc. (default: 0)
    
    Returns:
        200: Weekly report with all metrics
        400: Invalid parameters
        500: Server error
    
    Example:
        GET /api/learning-analytics/weekly-report?week_offset=-1
    """
    try:
        user_id = get_jwt_identity()
        week_offset = request.args.get('week_offset', 0, type=int)
        
        # Validate week offset
        if week_offset < -52 or week_offset > 0:
            return jsonify({
                'error': 'week_offset must be between -52 and 0'
            }), 400
        
        report = analytics_service.generate_weekly_report(user_id, week_offset)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting weekly report: {str(e)}")
        return jsonify({
            'error': 'Failed to generate weekly report',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/weekly-reports', methods=['GET'])
@jwt_required()
def get_weekly_reports():
    """
    Get historical weekly reports.
    
    Query Parameters:
        limit (int): Number of reports to return (default: 10, max: 52)
    
    Returns:
        200: List of weekly reports
        400: Invalid parameters
        500: Server error
    
    Example:
        GET /api/learning-analytics/weekly-reports?limit=20
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit
        if limit < 1 or limit > 52:
            return jsonify({
                'error': 'limit must be between 1 and 52'
            }), 400
        
        reports = analytics_service.get_weekly_reports(user_id, limit)
        
        return jsonify({
            'success': True,
            'reports': reports,
            'count': len(reports)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting weekly reports: {str(e)}")
        return jsonify({
            'error': 'Failed to get weekly reports',
            'details': str(e)
        }), 500


# ============================================================
# PROGRESS VISUALIZATION
# ============================================================

@learning_analytics_bp.route('/progress-visualization', methods=['GET'])
@jwt_required()
def get_progress_visualization():
    """
    Get progress visualization data.
    
    Query Parameters:
        time_range (str): '7d', '30d', '90d', '1y', 'all' (default: '30d')
    
    Returns:
        200: Visualization data (timeline, skills, velocity, milestones)
        400: Invalid parameters
        500: Server error
    
    Example:
        GET /api/learning-analytics/progress-visualization?time_range=90d
    """
    try:
        user_id = get_jwt_identity()
        time_range = request.args.get('time_range', '30d', type=str)
        
        # Validate time range
        valid_ranges = ['7d', '30d', '90d', '1y', 'all']
        if time_range not in valid_ranges:
            return jsonify({
                'error': f'time_range must be one of: {", ".join(valid_ranges)}'
            }), 400
        
        data = analytics_service.generate_progress_visualization(user_id, time_range)
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting progress visualization: {str(e)}")
        return jsonify({
            'error': 'Failed to generate progress visualization',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/skill-radar', methods=['GET'])
@jwt_required()
def get_skill_radar():
    """
    Get skill proficiency data for radar chart.
    
    Returns:
        200: Skill proficiency for all 6 skills
        500: Server error
    
    Example:
        GET /api/learning-analytics/skill-radar
        Response: {
            "listening": 75.5,
            "speaking": 60.2,
            ...
        }
    """
    try:
        user_id = get_jwt_identity()
        
        data = analytics_service.get_skill_radar_data(user_id)
        
        return jsonify({
            'success': True,
            'skills': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting skill radar data: {str(e)}")
        return jsonify({
            'error': 'Failed to get skill radar data',
            'details': str(e)
        }), 500


# ============================================================
# PREDICTIONS
# ============================================================

@learning_analytics_bp.route('/predictions/level-completion', methods=['GET'])
@jwt_required()
def predict_level_completion():
    """
    Predict when user will reach next CEFR level.
    
    Returns:
        200: Prediction with date, confidence, days remaining
        500: Server error
    
    Example:
        GET /api/learning-analytics/predictions/level-completion
        Response: {
            "current_level": "A2",
            "next_level": "B1",
            "predicted_date": "2025-12-15",
            "confidence": 0.85,
            "days_remaining": 45
        }
    """
    try:
        user_id = get_jwt_identity()
        
        prediction = analytics_service.predict_level_completion(user_id)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        logger.error(f"Error predicting level completion: {str(e)}")
        return jsonify({
            'error': 'Failed to predict level completion',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/predictions/skill-mastery/<skill>', methods=['GET'])
@jwt_required()
def predict_skill_mastery(skill):
    """
    Predict when user will master a specific skill (reach 90%).
    
    Path Parameters:
        skill (str): listening, speaking, reading, writing, grammar, vocabulary
    
    Returns:
        200: Prediction with date, confidence
        400: Invalid skill
        500: Server error
    
    Example:
        GET /api/learning-analytics/predictions/skill-mastery/listening
    """
    try:
        user_id = get_jwt_identity()
        
        # Validate skill
        valid_skills = ['listening', 'speaking', 'reading', 'writing', 'grammar', 'vocabulary']
        if skill not in valid_skills:
            return jsonify({
                'error': f'Invalid skill. Must be one of: {", ".join(valid_skills)}'
            }), 400
        
        prediction = analytics_service.predict_skill_mastery(user_id, skill)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        }), 200
        
    except Exception as e:
        logger.error(f"Error predicting skill mastery: {str(e)}")
        return jsonify({
            'error': 'Failed to predict skill mastery',
            'details': str(e)
        }), 500


# ============================================================
# COMPARISONS
# ============================================================

@learning_analytics_bp.route('/comparisons', methods=['GET'])
@jwt_required()
def get_comparisons():
    """
    Get comprehensive comparison insights.
    
    Returns:
        200: Comparisons vs self, peers, and expected curve
        500: Server error
    
    Example:
        GET /api/learning-analytics/comparisons
        Response: {
            "vs_self": {...},
            "vs_peers": {...},
            "vs_expected": {...}
        }
    """
    try:
        user_id = get_jwt_identity()
        
        comparisons = analytics_service.generate_comparison_insights(user_id)
        
        return jsonify({
            'success': True,
            'comparisons': comparisons
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting comparisons: {str(e)}")
        return jsonify({
            'error': 'Failed to generate comparison insights',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/percentile/<metric>', methods=['GET'])
@jwt_required()
def get_percentile(metric):
    """
    Get percentile ranking for a specific metric.
    
    Path Parameters:
        metric (str): total_study_time, weekly_velocity, etc.
    
    Returns:
        200: Percentile ranking and peer statistics
        400: Invalid metric
        500: Server error
    
    Example:
        GET /api/learning-analytics/percentile/weekly_velocity
    """
    try:
        user_id = get_jwt_identity()
        
        ranking = analytics_service.get_percentile_ranking(user_id, metric)
        
        if 'error' in ranking:
            return jsonify({
                'error': ranking['error']
            }), 400
        
        return jsonify({
            'success': True,
            'ranking': ranking
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting percentile: {str(e)}")
        return jsonify({
            'error': 'Failed to get percentile ranking',
            'details': str(e)
        }), 500


# ============================================================
# VELOCITY & MOMENTUM
# ============================================================

@learning_analytics_bp.route('/velocity', methods=['GET'])
@jwt_required()
def get_velocity():
    """
    Get learning velocity and momentum.
    
    Query Parameters:
        period (str): 'week' or 'month' (default: 'week')
    
    Returns:
        200: Velocity, acceleration, momentum, trend
        400: Invalid period
        500: Server error
    
    Example:
        GET /api/learning-analytics/velocity?period=week
    """
    try:
        user_id = get_jwt_identity()
        period = request.args.get('period', 'week', type=str)
        
        # Validate period
        valid_periods = ['week', 'month']
        if period not in valid_periods:
            return jsonify({
                'error': f'period must be one of: {", ".join(valid_periods)}'
            }), 400
        
        velocity = analytics_service.calculate_learning_velocity(user_id, period)
        
        return jsonify({
            'success': True,
            'velocity': velocity
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting velocity: {str(e)}")
        return jsonify({
            'error': 'Failed to calculate learning velocity',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/study-schedule', methods=['GET'])
@jwt_required()
def get_study_schedule():
    """
    Get optimal study schedule based on historical performance.
    
    Returns:
        200: Optimal time slots with engagement scores
        500: Server error
    
    Example:
        GET /api/learning-analytics/study-schedule
    """
    try:
        user_id = get_jwt_identity()
        
        schedule = analytics_service.get_optimal_study_schedule(user_id)
        
        return jsonify({
            'success': True,
            'schedule': schedule
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting study schedule: {str(e)}")
        return jsonify({
            'error': 'Failed to get optimal study schedule',
            'details': str(e)
        }), 500


# ============================================================
# INSIGHTS
# ============================================================

@learning_analytics_bp.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """
    Get personalized AI-generated insights.
    
    Returns:
        200: List of insights with type, category, priority
        500: Server error
    
    Example:
        GET /api/learning-analytics/insights
    """
    try:
        user_id = get_jwt_identity()
        
        insights = analytics_service.generate_personalized_insights(user_id)
        
        return jsonify({
            'success': True,
            'insights': insights,
            'count': len(insights)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        return jsonify({
            'error': 'Failed to generate insights',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/patterns', methods=['GET'])
@jwt_required()
def get_patterns():
    """
    Identify learning patterns and behaviors.
    
    Returns:
        200: Learning patterns (preferred days, times, consistency)
        500: Server error
    
    Example:
        GET /api/learning-analytics/patterns
    """
    try:
        user_id = get_jwt_identity()
        
        patterns = analytics_service.identify_learning_patterns(user_id)
        
        return jsonify({
            'success': True,
            'patterns': patterns
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting patterns: {str(e)}")
        return jsonify({
            'error': 'Failed to identify learning patterns',
            'details': str(e)
        }), 500


# ============================================================
# STUDY SESSIONS
# ============================================================

@learning_analytics_bp.route('/study-sessions', methods=['GET'])
@jwt_required()
def get_study_sessions():
    """
    Get study session history.
    
    Query Parameters:
        days (int): Number of days to look back (default: 30, max: 365)
    
    Returns:
        200: List of study sessions
        400: Invalid parameters
        500: Server error
    
    Example:
        GET /api/learning-analytics/study-sessions?days=30
    """
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        
        # Validate days
        if days < 1 or days > 365:
            return jsonify({
                'error': 'days must be between 1 and 365'
            }), 400
        
        sessions = analytics_service.get_study_history(user_id, days)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting study sessions: {str(e)}")
        return jsonify({
            'error': 'Failed to get study sessions',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/study-sessions', methods=['POST'])
@jwt_required()
def track_session():
    """
    Track a completed study session.
    
    Request Body:
        {
            "session_start": "2025-10-20T14:30:00",
            "session_end": "2025-10-20T15:15:00",
            "activities": [123, 456, 789]  // Optional activity IDs
        }
    
    Returns:
        201: Session tracked successfully
        400: Invalid request body
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data or 'session_start' not in data or 'session_end' not in data:
            return jsonify({
                'error': 'session_start and session_end are required'
            }), 400
        
        # Parse datetimes
        try:
            session_start = datetime.fromisoformat(data['session_start'].replace('Z', '+00:00'))
            session_end = datetime.fromisoformat(data['session_end'].replace('Z', '+00:00'))
        except ValueError as e:
            return jsonify({
                'error': 'Invalid datetime format. Use ISO 8601 format',
                'details': str(e)
            }), 400
        
        # Validate session duration
        duration = (session_end - session_start).total_seconds()
        if duration <= 0:
            return jsonify({
                'error': 'session_end must be after session_start'
            }), 400
        
        if duration > 86400:  # 24 hours
            return jsonify({
                'error': 'Session duration cannot exceed 24 hours'
            }), 400
        
        # Get activities
        activities = data.get('activities', [])
        
        # Track session
        session = analytics_service.track_study_session(
            user_id,
            session_start,
            session_end,
            activities
        )
        
        return jsonify({
            'success': True,
            'message': 'Study session tracked successfully',
            'session': session
        }), 201
        
    except Exception as e:
        logger.error(f"Error tracking study session: {str(e)}")
        return jsonify({
            'error': 'Failed to track study session',
            'details': str(e)
        }), 500


# ============================================================
# PROGRESS SNAPSHOTS
# ============================================================

@learning_analytics_bp.route('/snapshots', methods=['GET'])
@jwt_required()
def get_snapshots():
    """
    Get progress snapshot history.
    
    Query Parameters:
        days (int): Number of days to look back (default: 90, max: 365)
    
    Returns:
        200: List of progress snapshots
        400: Invalid parameters
        500: Server error
    
    Example:
        GET /api/learning-analytics/snapshots?days=90
    """
    try:
        user_id = get_jwt_identity()
        days = request.args.get('days', 90, type=int)
        
        # Validate days
        if days < 1 or days > 365:
            return jsonify({
                'error': 'days must be between 1 and 365'
            }), 400
        
        snapshots = analytics_service.get_snapshot_history(user_id, days)
        
        return jsonify({
            'success': True,
            'snapshots': snapshots,
            'count': len(snapshots)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting snapshots: {str(e)}")
        return jsonify({
            'error': 'Failed to get progress snapshots',
            'details': str(e)
        }), 500


@learning_analytics_bp.route('/snapshots/create', methods=['POST'])
@jwt_required()
def create_snapshot():
    """
    Create daily progress snapshot.
    
    Returns:
        201: Snapshot created successfully
        500: Server error
    
    Example:
        POST /api/learning-analytics/snapshots/create
    """
    try:
        user_id = get_jwt_identity()
        
        snapshot = analytics_service.create_daily_snapshot(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Progress snapshot created successfully',
            'snapshot': snapshot
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating snapshot: {str(e)}")
        return jsonify({
            'error': 'Failed to create progress snapshot',
            'details': str(e)
        }), 500


# ============================================================
# HEALTH CHECK
# ============================================================

@learning_analytics_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for learning analytics service.
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'healthy',
        'service': 'learning_analytics',
        'phase': 7,
        'version': '1.0.0',
        'endpoints': 17
    }), 200


# ============================================================
# ERROR HANDLERS
# ============================================================

@learning_analytics_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({
        'error': 'Bad Request',
        'message': str(error)
    }), 400


@learning_analytics_bp.errorhandler(401)
def unauthorized(error):
    """Handle 401 errors."""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required'
    }), 401


@learning_analytics_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not Found',
        'message': str(error)
    }), 404


@learning_analytics_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


# ============================================================
# ENDPOINT DOCUMENTATION
# ============================================================

"""
Learning Analytics API Endpoints (Phase 7) Summary:

Base URL: /api/learning-analytics

WEEKLY REPORTS:
1. GET  /weekly-report            - Get weekly report
2. GET  /weekly-reports           - Get historical reports

PROGRESS VISUALIZATION:
3. GET  /progress-visualization   - Get visualization data
4. GET  /skill-radar              - Get skill radar data

PREDICTIONS:
5. GET  /predictions/level-completion      - Predict next level
6. GET  /predictions/skill-mastery/<skill> - Predict skill mastery

COMPARISONS:
7. GET  /comparisons              - Get all comparisons
8. GET  /percentile/<metric>      - Get percentile ranking

VELOCITY & MOMENTUM:
9. GET  /velocity                 - Get learning velocity
10. GET /study-schedule           - Get optimal study times

INSIGHTS:
11. GET /insights                 - Get AI insights
12. GET /patterns                 - Get learning patterns

STUDY SESSIONS:
13. GET  /study-sessions          - Get session history
14. POST /study-sessions          - Track new session

PROGRESS SNAPSHOTS:
15. GET  /snapshots               - Get snapshot history
16. POST /snapshots/create        - Create new snapshot

HEALTH:
17. GET /health                   - Health check

All endpoints (except health) require JWT authentication.

Note: This is separate from Phase 4 analytics_routes.py (analytics_v2 blueprint)
which provides basic performance trends, skill breakdown, etc.
"""
