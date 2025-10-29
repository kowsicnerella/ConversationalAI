"""
Activity History Tracking Routes
Endpoints for tracking user interactions with activities (view, start, complete)
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.activity import Activity, UserActivityLog
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import desc

activity_history_bp = Blueprint('activity_history', __name__, url_prefix='/api/activity-history')


@activity_history_bp.route('/view/<int:activity_id>', methods=['POST'])
@jwt_required()
def record_activity_view(activity_id):
    """
    Record that a user viewed an activity.
    
    POST /api/activity-history/view/:activity_id
    Body: { "source": "dashboard|history|recommendation" }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Verify activity exists
        activity = Activity.query.get_or_404(activity_id)
        
        # Check if there's already an incomplete log for this activity
        existing_log = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id,
            is_completed=False
        ).order_by(desc(UserActivityLog.completed_at)).first()
        
        if existing_log:
            # Update the existing log
            existing_log.completed_at = datetime.utcnow()
            log_id = existing_log.id
        else:
            # Create a new log entry for viewing
            log = UserActivityLog(
                user_id=user_id,
                activity_id=activity_id,
                learning_path_id=activity.learning_path_id,
                completed_at=datetime.utcnow(),
                is_completed=False,  # Just viewed, not completed
                skill_area=activity.skill_area,
                concept_focus=activity.concept_focus,
                attempt_number=1
            )
            db.session.add(log)
            db.session.flush()
            log_id = log.id
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity view recorded",
            "log_id": log_id,
            "activity_id": activity_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@activity_history_bp.route('/start/<int:activity_id>', methods=['POST'])
@jwt_required()
def record_activity_start(activity_id):
    """
    Record that a user started an activity.
    
    POST /api/activity-history/start/:activity_id
    Body: { "session_id": "optional_session_id" }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Verify activity exists
        activity = Activity.query.get_or_404(activity_id)
        
        # Get the attempt number
        previous_attempts = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).count()
        
        # Create a new log entry for starting
        log = UserActivityLog(
            user_id=user_id,
            activity_id=activity_id,
            learning_path_id=activity.learning_path_id,
            completed_at=datetime.utcnow(),  # Start time
            is_completed=False,
            skill_area=activity.skill_area,
            concept_focus=activity.concept_focus,
            attempt_number=previous_attempts + 1,
            session_id=data.get('session_id')
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity start recorded",
            "log_id": log.id,
            "activity_id": activity_id,
            "attempt_number": log.attempt_number
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@activity_history_bp.route('/complete/<int:log_id>', methods=['PUT'])
@jwt_required()
def record_activity_completion(log_id):
    """
    Record that a user completed an activity.
    
    PUT /api/activity-history/complete/:log_id
    Body: {
        "score": 8,
        "max_score": 10,
        "time_spent_minutes": 15,
        "user_response": {...},
        "accuracy_score": 0.8,
        "mastery_level": "proficient"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get the log entry
        log = UserActivityLog.query.get_or_404(log_id)
        
        # Verify ownership
        if log.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403
        
        # Update completion data
        log.is_completed = True
        log.completed_at = datetime.utcnow()
        log.score = data.get('score')
        log.max_score = data.get('max_score')
        log.time_spent_minutes = data.get('time_spent_minutes')
        log.user_response = data.get('user_response')
        log.accuracy_score = data.get('accuracy_score')
        log.mastery_level = data.get('mastery_level', 'learning')
        log.hint_count = data.get('hint_count', 0)
        log.error_patterns = data.get('error_patterns')
        
        # Calculate time efficiency if we have both accuracy and time
        if log.accuracy_score and log.time_spent_minutes and log.time_spent_minutes > 0:
            log.time_efficiency = log.accuracy_score / log.time_spent_minutes
        
        db.session.commit()
        
        # Track vocabulary usage and exposure
        vocab_results = {}
        try:
            from app.services.vocabulary_integration_service import vocabulary_integration
            vocab_results = vocabulary_integration.on_activity_completed(user_id, log)
        except Exception as e:
            print(f"Error tracking vocabulary: {e}")
        
        return jsonify({
            "success": True,
            "message": "Activity completion recorded",
            "log_id": log.id,
            "activity_id": log.activity_id,
            "score": log.score,
            "mastery_level": log.mastery_level,
            "vocabulary_tracking": vocab_results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@activity_history_bp.route('/user/recent', methods=['GET'])
@jwt_required()
def get_recent_activity_history():
    """
    Get recent activity history for the current user.
    
    GET /api/activity-history/user/recent
    Query params:
    - limit: Number of results (default 10)
    - completed_only: true/false (default false)
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 10, type=int)
        completed_only = request.args.get('completed_only', 'false').lower() == 'true'
        
        # Build query
        query = UserActivityLog.query.filter_by(user_id=user_id)
        
        if completed_only:
            query = query.filter_by(is_completed=True)
        
        # Get recent logs
        logs = query.order_by(desc(UserActivityLog.completed_at)).limit(limit).all()
        
        # Format response
        history = []
        for log in logs:
            activity = Activity.query.get(log.activity_id)
            history.append({
                'log_id': log.id,
                'activity_id': log.activity_id,
                'activity_title': activity.title if activity else 'Unknown',
                'activity_type': activity.activity_type if activity else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'is_completed': log.is_completed,
                'score': log.score,
                'max_score': log.max_score,
                'time_spent_minutes': log.time_spent_minutes,
                'accuracy_score': log.accuracy_score,
                'mastery_level': log.mastery_level,
                'attempt_number': log.attempt_number
            })
        
        return jsonify({
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_history_bp.route('/activity/<int:activity_id>/attempts', methods=['GET'])
@jwt_required()
def get_activity_attempts(activity_id):
    """
    Get all attempts for a specific activity by the current user.
    
    GET /api/activity-history/activity/:activity_id/attempts
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify activity exists
        activity = Activity.query.get_or_404(activity_id)
        
        # Get all attempts
        logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        # Format response
        attempts = []
        for log in logs:
            attempts.append({
                'log_id': log.id,
                'attempt_number': log.attempt_number,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'is_completed': log.is_completed,
                'score': log.score,
                'max_score': log.max_score,
                'time_spent_minutes': log.time_spent_minutes,
                'accuracy_score': log.accuracy_score,
                'mastery_level': log.mastery_level,
                'hint_count': log.hint_count
            })
        
        # Calculate statistics
        completed_attempts = [a for a in attempts if a['is_completed']]
        avg_score = None
        best_score = None
        
        if completed_attempts:
            scores = [a['accuracy_score'] for a in completed_attempts if a['accuracy_score'] is not None]
            if scores:
                avg_score = sum(scores) / len(scores)
                best_score = max(scores)
        
        return jsonify({
            'activity_id': activity_id,
            'activity_title': activity.title,
            'activity_type': activity.activity_type,
            'total_attempts': len(attempts),
            'completed_attempts': len(completed_attempts),
            'average_score': avg_score,
            'best_score': best_score,
            'attempts': attempts
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_history_bp.route('/stats/summary', methods=['GET'])
@jwt_required()
def get_user_activity_stats():
    """
    Get comprehensive activity statistics for the current user.
    
    GET /api/activity-history/stats/summary
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all completed activities
        completed_logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()
        
        if not completed_logs:
            return jsonify({
                'total_completed': 0,
                'total_time_spent': 0,
                'average_accuracy': 0,
                'by_activity_type': {},
                'by_mastery_level': {},
                'recent_activity': []
            }), 200
        
        # Calculate statistics
        total_time = sum(log.time_spent_minutes or 0 for log in completed_logs)
        accuracy_scores = [log.accuracy_score for log in completed_logs if log.accuracy_score is not None]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        
        # Group by activity type
        by_type = {}
        for log in completed_logs:
            activity = Activity.query.get(log.activity_id)
            if activity:
                activity_type = activity.activity_type
                if activity_type not in by_type:
                    by_type[activity_type] = {'count': 0, 'total_score': 0, 'activities': []}
                by_type[activity_type]['count'] += 1
                if log.accuracy_score:
                    by_type[activity_type]['total_score'] += log.accuracy_score
                by_type[activity_type]['activities'].append(log.activity_id)
        
        # Group by mastery level
        by_mastery = {}
        for log in completed_logs:
            if log.mastery_level:
                by_mastery[log.mastery_level] = by_mastery.get(log.mastery_level, 0) + 1
        
        # Get recent activity
        recent_logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).order_by(desc(UserActivityLog.completed_at)).limit(5).all()
        
        recent_activity = []
        for log in recent_logs:
            activity = Activity.query.get(log.activity_id)
            if activity:
                recent_activity.append({
                    'activity_type': activity.activity_type,
                    'title': activity.title,
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                    'score': log.accuracy_score
                })
        
        return jsonify({
            'total_completed': len(completed_logs),
            'total_time_spent': total_time,
            'average_accuracy': round(avg_accuracy, 2),
            'by_activity_type': by_type,
            'by_mastery_level': by_mastery,
            'recent_activity': recent_activity
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
