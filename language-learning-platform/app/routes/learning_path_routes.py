"""
Learning Path API Routes
Endpoints for AI-personalized learning path and activity management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.learning_path_orchestrator import LearningPathOrchestrator
from app.models.user import User, Profile
from app.models.curriculum import (
    CurriculumLevel,
    LearningNode,
    UserLearningPathProgress,
    NodeCompletion
)
from app.models.activity import Activity, UserActivityLog
from app.models import db
from app.models.learning_node import (
    CurriculumLevel as Phase3CurriculumLevel,
    SkillDomain as Phase3SkillDomain,
    LearningNode as Phase3LearningNode,
    UserLearningNodeProgress as Phase3UserLearningNodeProgress,
    UserSkillProfile as Phase3UserSkillProfile
)
from app.services.adaptive_difficulty_engine import AdaptiveDifficultyEngine
from sqlalchemy import desc, and_
from datetime import datetime, timedelta

learning_path_bp = Blueprint('ai_learning_path', __name__, url_prefix='/api/learning-path')

# Initialize orchestrator and difficulty engine
orchestrator = LearningPathOrchestrator()
difficulty_engine = AdaptiveDifficultyEngine()


@learning_path_bp.route('/next-activity', methods=['POST'])
@jwt_required()
def get_next_activity():
    """
    Get the next personalized AI-generated activity for the current user.
    
    Uses intelligent orchestration to determine:
    - Vocabulary reviews (spaced repetition)
    - Weak area reinforcement
    - Curriculum progression
    - Mixed review
    
    Returns:
        JSON: Fully generated activity with content, metadata, and activity_id
    """
    try:
        # Get current user from JWT token
        current_user_id = get_jwt_identity()
        
        # Determine and generate next activity
        activity_data = orchestrator.determine_next_activity(current_user_id)
        
        if "error" in activity_data:
            return jsonify({
                "success": False,
                "error": activity_data["error"]
            }), 404
        
        # Extract components for frontend
        response = {
            "success": True,
            "data": {
                "activity": activity_data,
                "reasoning": activity_data.get('orchestration_message', 'Next activity selected'),
                "message": activity_data.get('orchestration_message', 'Next activity ready'),
                "node_info": {
                    "node_id": activity_data.get('learning_node', {}).get('node_id'),
                    "node_name": activity_data.get('learning_node', {}).get('name'),
                    "level_name": activity_data.get('learning_node', {}).get('level_name'),
                    "focus_areas": [activity_data.get('learning_node', {}).get('skill_domain')]
                },
                "activity_id": activity_data.get('activity_id'),  # Database ID for resuming/completing
                "can_resume": activity_data.get('can_resume', True)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in get_next_activity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/complete-activity', methods=['POST'])
@jwt_required()
def complete_activity():
    """
    Record completion of an activity and update user progress.
    
    Expected JSON body:
    {
        "activity_id": 123,  # Required: Activity database ID
        "learning_node_id": "A1_VOCAB_GREETINGS",  # Required
        "performance_score": 0.85,  # Required: 0.0 to 1.0
        "time_spent_seconds": 180,  # Required
        "user_responses": {...}  # Optional: user's answers for review
    }
    
    Returns:
        JSON: Updated progress and mastery information
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('learning_node_id'):
            return jsonify({
                "success": False,
                "error": "learning_node_id is required"
            }), 400
        
        if 'performance_score' not in data:
            return jsonify({
                "success": False,
                "error": "performance_score is required"
            }), 400
        
        learning_node_id = data['learning_node_id']
        performance_score = float(data['performance_score'])
        time_spent_seconds = int(data.get('time_spent_seconds', 0))
        activity_id = data.get('activity_id')  # Optional but recommended
        user_responses = data.get('user_responses', {})  # Optional
        
        # Validate performance score range
        if not 0.0 <= performance_score <= 1.0:
            return jsonify({
                "success": False,
                "error": "performance_score must be between 0.0 and 1.0"
            }), 400
        
        # Record completion
        result = orchestrator.complete_activity(
            user_id=current_user_id,
            learning_node_id=learning_node_id,
            performance_score=performance_score,
            time_spent_seconds=time_spent_seconds,
            activity_id=activity_id,
            user_responses=user_responses
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_progress(user_id):
    """
    Get comprehensive progress information for a user.
    
    Returns:
        JSON: User's learning path progress, completed nodes, current level, etc.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Only allow users to view their own progress (or admins in future)
        if current_user_id != user_id:
            return jsonify({
                "success": False,
                "error": "Unauthorized to view this user's progress"
            }), 403
        
        # Get user and profile
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return jsonify({"error": "User profile not found"}), 404
        
        # Get learning path progress
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        # Get current level
        current_level = None
        if progress and progress.current_level_id:
            level = CurriculumLevel.query.get(progress.current_level_id)
            if level:
                current_level = level.to_dict()
        
        # Get completed nodes
        completed_nodes = NodeCompletion.query.filter_by(user_id=user_id).all()
        completed_nodes_data = [
            {
                "node_id": nc.node_id,
                "mastery_level": nc.mastery_level,
                "attempts": nc.attempts,
                "last_attempted_at": nc.last_attempted_at.isoformat() if nc.last_attempted_at else None
            }
            for nc in completed_nodes
        ]
        
        # Calculate level completion percentage
        level_completion = 0.0
        if progress and progress.current_level_id:
            level_completion = orchestrator._calculate_level_completion(
                user_id, 
                progress.current_level_id
            )
        
        return jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "profile": {
                "proficiency_level": profile.proficiency_level,
                "native_language": profile.native_language,
                "target_language": profile.target_language,
                "current_streak": profile.current_streak,
                "points": profile.points,
                "mastery_metrics": profile.mastery_metrics
            },
            "learning_path": progress.to_dict() if progress else None,
            "current_level": current_level,
            "level_completion_percentage": round(level_completion * 100, 1),
            "completed_nodes": completed_nodes_data,
            "total_completed_nodes": len(completed_nodes_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/nodes', methods=['GET'])
@jwt_required()
def get_available_nodes():
    """
    Get all available learning nodes, optionally filtered by level or skill domain.
    
    Query params:
    - level: CEFR level (A1, A2, B1, etc.)
    - skill_domain: vocabulary, grammar, reading, writing, etc.
    
    Returns:
        JSON: List of learning nodes
    """
    try:
        # Get query parameters
        cefr_level = request.args.get('level')
        skill_domain = request.args.get('skill_domain')
        
        # Build query
        query = LearningNode.query
        
        if cefr_level:
            level = CurriculumLevel.query.filter_by(cefr_level=cefr_level).first()
            if level:
                query = query.filter_by(curriculum_level_id=level.id)
        
        if skill_domain:
            query = query.filter_by(skill_domain=skill_domain)
        
        nodes = query.all()
        
        return jsonify({
            "success": True,
            "nodes": [node.to_dict() for node in nodes],
            "total": len(nodes)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/levels', methods=['GET'])
@jwt_required()
def get_curriculum_levels():
    """
    Get all CEFR curriculum levels.
    
    Returns:
        JSON: List of curriculum levels with metadata
    """
    try:
        levels = CurriculumLevel.query.order_by(CurriculumLevel.cefr_level).all()
        
        return jsonify({
            "success": True,
            "levels": [level.to_dict() for level in levels],
            "total": len(levels)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/node/<string:node_id>', methods=['GET'])
@jwt_required()
def get_node_details(node_id):
    """
    Get detailed information about a specific learning node.
    
    Returns:
        JSON: Learning node details including objectives, prerequisites, etc.
    """
    try:
        node = LearningNode.query.filter_by(node_id=node_id).first()
        
        if not node:
            return jsonify({
                "success": False,
                "error": f"Node {node_id} not found"
            }), 404
        
        # Get user's completion status for this node
        current_user_id = get_jwt_identity()
        completion = NodeCompletion.query.filter_by(
            user_id=current_user_id,
            node_id=node_id
        ).first()
        
        node_data = node.to_dict()
        node_data['user_completion'] = {
            "completed": completion is not None,
            "mastery_level": completion.mastery_level if completion else 0.0,
            "attempts": completion.attempts if completion else 0,
            "last_attempted_at": completion.last_attempted_at.isoformat() if completion and completion.last_attempted_at else None
        }
        
        return jsonify({
            "success": True,
            "node": node_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_learning_stats():
    """
    Get comprehensive learning statistics for the current user.
    
    Returns:
        JSON: Detailed learning statistics and analytics
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get user data
        user = User.query.get(current_user_id)
        profile = Profile.query.filter_by(user_id=current_user_id).first()
        progress = UserLearningPathProgress.query.filter_by(user_id=current_user_id).first()
        completed_nodes = NodeCompletion.query.filter_by(user_id=current_user_id).all()
        
        if not user or not profile:
            return jsonify({"error": "User or profile not found"}), 404
        
        # Calculate statistics
        total_nodes_completed = len([nc for nc in completed_nodes if nc.mastery_level >= 0.7])
        total_attempts = sum(nc.attempts for nc in completed_nodes)
        average_mastery = (
            sum(nc.mastery_level for nc in completed_nodes) / len(completed_nodes)
            if completed_nodes else 0.0
        )
        
        # Get skill domain breakdown
        skill_breakdown = {}
        for nc in completed_nodes:
            node = LearningNode.query.filter_by(node_id=nc.node_id).first()
            if node:
                domain = node.skill_domain
                if domain not in skill_breakdown:
                    skill_breakdown[domain] = {
                        "completed": 0,
                        "average_mastery": 0.0,
                        "total_attempts": 0
                    }
                skill_breakdown[domain]["completed"] += 1
                skill_breakdown[domain]["average_mastery"] += nc.mastery_level
                skill_breakdown[domain]["total_attempts"] += nc.attempts
        
        # Calculate averages
        for domain in skill_breakdown:
            if skill_breakdown[domain]["completed"] > 0:
                skill_breakdown[domain]["average_mastery"] /= skill_breakdown[domain]["completed"]
        
        return jsonify({
            "success": True,
            "stats": {
                "total_nodes_completed": total_nodes_completed,
                "total_attempts": total_attempts,
                "average_mastery": round(average_mastery, 2),
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "total_points": profile.points,
                "skill_breakdown": skill_breakdown,
                "mastery_metrics": profile.mastery_metrics,
                "weak_areas": progress.weak_areas if progress else [],
                "strong_areas": progress.strong_areas if progress else [],
                "total_activities_completed": progress.nodes_completed if progress else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
#  ACTIVITY CRUD ENDPOINTS
# ============================================================================

@learning_path_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_user_activities():
    """
    Get all activities for the current user with filtering options.
    
    Query Parameters:
        status (str): Filter by status - 'completed', 'in_progress', 'not_started'
        activity_type (str): Filter by type - 'vocabulary', 'grammar', 'conversation', etc.
        limit (int): Number of results (default: 50)
        offset (int): Pagination offset (default: 0)
        from_date (str): Filter activities created after this date (ISO format)
        to_date (str): Filter activities created before this date (ISO format)
    
    Returns:
        JSON: List of activities with metadata
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')
        activity_type = request.args.get('activity_type')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Build query
        query = Activity.query.filter_by(user_id=current_user_id)
        
        # Apply filters
        if status:
            query = query.filter_by(status=status)
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        if from_date:
            query = query.filter(Activity.created_at >= datetime.fromisoformat(from_date))
        if to_date:
            query = query.filter(Activity.created_at <= datetime.fromisoformat(to_date))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        activities = query.order_by(desc(Activity.created_at))\
                          .limit(limit)\
                          .offset(offset)\
                          .all()
        
        # Format response
        activities_data = []
        for activity in activities:
            activity_dict = {
                "id": activity.id,
                "learning_node_id": activity.learning_node_id,
                "activity_type": activity.activity_type,
                "status": activity.status,
                "created_at": activity.created_at.isoformat() if activity.created_at else None,
                "completed_at": activity.completed_at.isoformat() if activity.completed_at else None,
                "content": activity.content,
                "generation_metadata": activity.generation_metadata,
                "performance_score": activity.performance_score,
                "time_spent_seconds": activity.time_spent_seconds
            }
            activities_data.append(activity_dict)
        
        return jsonify({
            "success": True,
            "data": {
                "activities": activities_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_user_activities: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/activities/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity_detail(activity_id):
    """
    Get detailed information about a specific activity.
    
    Args:
        activity_id (int): The ID of the activity
    
    Returns:
        JSON: Complete activity details with content and logs
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get activity
        activity = Activity.query.filter_by(
            id=activity_id,
            user_id=current_user_id
        ).first()
        
        if not activity:
            return jsonify({
                "success": False,
                "error": "Activity not found or access denied"
            }), 404
        
        # Get associated activity log if completed
        activity_log = None
        if activity.status == 'completed':
            activity_log = UserActivityLog.query.filter_by(
                activity_id=activity_id
            ).first()
        
        # Format response
        activity_data = {
            "id": activity.id,
            "user_id": activity.user_id,
            "learning_node_id": activity.learning_node_id,
            "activity_type": activity.activity_type,
            "status": activity.status,
            "created_at": activity.created_at.isoformat() if activity.created_at else None,
            "completed_at": activity.completed_at.isoformat() if activity.completed_at else None,
            "content": activity.content,
            "generation_metadata": activity.generation_metadata,
            "performance_score": activity.performance_score,
            "time_spent_seconds": activity.time_spent_seconds
        }
        
        # Add log data if available
        if activity_log:
            activity_data["completion_log"] = {
                "id": activity_log.id,
                "performance_score": activity_log.performance_score,
                "time_spent_seconds": activity_log.time_spent_seconds,
                "accuracy_score": activity_log.accuracy_score,
                "confidence_score": activity_log.confidence_score,
                "mastery_level": activity_log.mastery_level,
                "needs_review": activity_log.needs_review,
                "next_review_date": activity_log.next_review_date.isoformat() if activity_log.next_review_date else None,
                "review_count": activity_log.review_count,
                "user_responses": activity_log.user_responses,
                "completed_at": activity_log.completed_at.isoformat() if activity_log.completed_at else None
            }
        
        return jsonify({
            "success": True,
            "data": activity_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_activity_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/activities/incomplete', methods=['GET'])
@jwt_required()
def get_incomplete_activities():
    """
    Get all incomplete activities for the current user (for resume functionality).
    
    Returns:
        JSON: List of incomplete activities that can be resumed
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Query UserActivityLog for incomplete activities (is_completed = False)
        incomplete_logs = UserActivityLog.query.filter(
            UserActivityLog.user_id == current_user_id,
            UserActivityLog.is_completed == False
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        # Format response
        activities_data = []
        for log in incomplete_logs:
            if log.activity:  # Make sure activity exists
                activity = log.activity
                activity_dict = {
                    "id": activity.id,
                    "log_id": log.id,
                    "learning_path_id": activity.learning_path_id,
                    "activity_type": activity.activity_type,
                    "title": activity.title,
                    "description": activity.description,
                    "content": activity.content,
                    "started_at": log.completed_at.isoformat() if log.completed_at else None,
                    "generation_metadata": activity.generation_metadata,
                    "skill_area": activity.skill_area,
                    "concept_focus": activity.concept_focus,
                    "difficulty_level": activity.difficulty_level,
                    "estimated_duration_minutes": activity.estimated_duration_minutes
                }
                activities_data.append(activity_dict)
        
        return jsonify({
            "success": True,
            "data": {
                "activities": activities_data,
                "count": len(activities_data)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_incomplete_activities: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/activities/<int:activity_id>/resume', methods=['PUT'])
@jwt_required()
def resume_activity(activity_id):
    """
    Mark an activity as resumed and update its status.
    
    Args:
        activity_id (int): The ID of the activity to resume
    
    Returns:
        JSON: Updated activity data
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get activity
        activity = Activity.query.filter_by(
            id=activity_id,
            user_id=current_user_id
        ).first()
        
        if not activity:
            return jsonify({
                "success": False,
                "error": "Activity not found or access denied"
            }), 404
        
        # Update status
        if activity.status != 'completed':
            activity.status = 'in_progress'
            db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity resumed successfully",
            "data": {
                "id": activity.id,
                "status": activity.status,
                "content": activity.content
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in resume_activity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
#  ACTIVITY LOG CRUD ENDPOINTS
# ============================================================================

@learning_path_bp.route('/activity-logs', methods=['GET'])
@jwt_required()
def get_user_activity_logs():
    """
    Get activity completion logs for the current user with filtering.
    
    Query Parameters:
        mastery_level (str): Filter by mastery - 'not_started', 'learning', 'proficient', 'mastered'
        needs_review (bool): Filter by review status - 'true' or 'false'
        limit (int): Number of results (default: 50)
        offset (int): Pagination offset (default: 0)
        from_date (str): Filter logs created after this date (ISO format)
        to_date (str): Filter logs created before this date (ISO format)
    
    Returns:
        JSON: List of activity logs with performance metrics
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        mastery_level = request.args.get('mastery_level')
        needs_review = request.args.get('needs_review')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        # Build query
        query = UserActivityLog.query.filter_by(user_id=current_user_id)
        
        # Apply filters
        if mastery_level:
            query = query.filter_by(mastery_level=mastery_level)
        if needs_review is not None:
            review_bool = needs_review.lower() == 'true'
            query = query.filter_by(needs_review=review_bool)
        if from_date:
            query = query.filter(UserActivityLog.completed_at >= datetime.fromisoformat(from_date))
        if to_date:
            query = query.filter(UserActivityLog.completed_at <= datetime.fromisoformat(to_date))
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(desc(UserActivityLog.completed_at))\
                   .limit(limit)\
                   .offset(offset)\
                   .all()
        
        # Format response
        logs_data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "activity_id": log.activity_id,
                "learning_node_id": log.learning_node_id,
                "performance_score": log.performance_score,
                "time_spent_seconds": log.time_spent_minutes * 60 if log.time_spent_minutes else 0,  # Convert minutes to seconds
                "accuracy_score": log.accuracy_score,
                "confidence_score": log.confidence_score,
                "mastery_level": log.mastery_level,
                "needs_review": log.needs_review,
                "next_review_date": log.next_review_date.isoformat() if log.next_review_date else None,
                "review_count": log.review_count,
                "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                "user_responses": log.user_responses
            }
            logs_data.append(log_dict)
        
        return jsonify({
            "success": True,
            "data": {
                "logs": logs_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_user_activity_logs: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/activity-logs/<int:log_id>', methods=['GET'])
@jwt_required()
def get_activity_log_detail(log_id):
    """
    Get detailed information about a specific activity log.
    
    Args:
        log_id (int): The ID of the activity log
    
    Returns:
        JSON: Complete log details with user responses
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get log
        log = UserActivityLog.query.filter_by(
            id=log_id,
            user_id=current_user_id
        ).first()
        
        if not log:
            return jsonify({
                "success": False,
                "error": "Activity log not found or access denied"
            }), 404
        
        # Get associated activity
        activity = Activity.query.filter_by(id=log.activity_id).first()
        
        # Format response
        log_data = {
            "id": log.id,
            "activity_id": log.activity_id,
            "user_id": log.user_id,
            "learning_node_id": log.learning_node_id,
            "performance_score": log.performance_score,
            "time_spent_seconds": log.time_spent_minutes * 60 if log.time_spent_minutes else 0,  # Convert minutes to seconds
            "accuracy_score": log.accuracy_score,
            "confidence_score": log.confidence_score,
            "mastery_level": log.mastery_level,
            "needs_review": log.needs_review,
            "next_review_date": log.next_review_date.isoformat() if log.next_review_date else None,
            "review_count": log.review_count,
            "completed_at": log.completed_at.isoformat() if log.completed_at else None,
            "user_responses": log.user_responses
        }
        
        # Add activity data
        if activity:
            log_data["activity"] = {
                "learning_node_id": activity.learning_node_id,
                "activity_type": activity.activity_type,
                "content": activity.content
            }
        
        return jsonify({
            "success": True,
            "data": log_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_activity_log_detail: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/activity-history', methods=['GET'])
@jwt_required()
def get_activity_history():
    """
    Get comprehensive activity history with statistics for the current user.
    
    Returns:
        JSON: Activity history with performance stats and insights
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get all completed activity logs (UserActivityLog tracks user's activity completion)
        completed_logs = UserActivityLog.query.filter_by(
            user_id=current_user_id,
            is_completed=True
        ).order_by(desc(UserActivityLog.completed_at)).limit(100).all()
        
        # Get all activity logs for statistics
        activity_logs = UserActivityLog.query.filter_by(
            user_id=current_user_id
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        # Calculate statistics
        total_activities = len(completed_logs)
        # Use time_spent_minutes (not time_spent_seconds)
        total_time_spent = sum(log.time_spent_minutes * 60 for log in activity_logs if log.time_spent_minutes) if activity_logs else 0
        # Use accuracy_score (not performance_score)
        avg_performance = sum(log.accuracy_score for log in activity_logs if log.accuracy_score) / len(activity_logs) if activity_logs else 0
        
        # Mastery breakdown
        mastery_breakdown = {
            "mastered": sum(1 for log in activity_logs if log.mastery_level == 'mastered'),
            "proficient": sum(1 for log in activity_logs if log.mastery_level == 'proficient'),
            "learning": sum(1 for log in activity_logs if log.mastery_level == 'learning'),
            "not_started": sum(1 for log in activity_logs if log.mastery_level == 'not_started')
        }
        
        # Activities needing review
        needs_review = UserActivityLog.query.filter_by(
            user_id=current_user_id,
            needs_review=True
        ).order_by(UserActivityLog.next_review_date).limit(10).all()
        
        review_activities = []
        for log in needs_review:
            activity = Activity.query.filter_by(id=log.activity_id).first()
            if activity:
                review_activities.append({
                    "activity_id": log.activity_id,
                    "learning_path_id": log.learning_path_id,  # Use learning_path_id (exists)
                    "activity_type": activity.activity_type,
                    "title": activity.title,
                    "next_review_date": log.next_review_date.isoformat() if log.next_review_date else None,
                    "mastery_level": log.mastery_level,
                    "last_score": log.accuracy_score  # Use accuracy_score (not performance_score)
                })
        
        # Recent activity timeline
        recent_logs = activity_logs[:20]  # Last 20 activities
        timeline = []
        for log in recent_logs:
            activity = Activity.query.filter_by(id=log.activity_id).first()
            if activity:
                timeline.append({
                    "activity_id": log.activity_id,
                    "learning_path_id": log.learning_path_id,  # Use learning_path_id (exists)
                    "activity_type": activity.activity_type,
                    "title": activity.title,
                    "accuracy_score": log.accuracy_score,  # Use accuracy_score (not performance_score)
                    "mastery_level": log.mastery_level,
                    "time_spent_seconds": log.time_spent_minutes * 60 if log.time_spent_minutes else 0,  # Convert minutes to seconds
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None
                })
        
        return jsonify({
            "success": True,
            "data": {
                "statistics": {
                    "total_activities_completed": total_activities,
                    "total_time_spent_seconds": total_time_spent,
                    "average_performance_score": round(avg_performance, 2),
                    "mastery_breakdown": mastery_breakdown
                },
                "needs_review": review_activities,
                "recent_timeline": timeline
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_activity_history: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/spaced-repetition/due', methods=['GET'])
@jwt_required()
def get_due_reviews():
    """
    Get activities due for spaced repetition review.
    
    Returns:
        JSON: List of activities that need review based on spaced repetition schedule
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get activities due for review (next_review_date <= today)
        today = datetime.utcnow()
        
        due_reviews = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.needs_review == True,
                UserActivityLog.next_review_date <= today
            )
        ).order_by(UserActivityLog.next_review_date).all()
        
        # Format response
        reviews_data = []
        for log in due_reviews:
            activity = Activity.query.filter_by(id=log.activity_id).first()
            if activity:
                reviews_data.append({
                    "activity_id": log.activity_id,
                    "learning_node_id": log.learning_node_id,
                    "activity_type": activity.activity_type,
                    "mastery_level": log.mastery_level,
                    "last_performance_score": log.performance_score,
                    "review_count": log.review_count,
                    "next_review_date": log.next_review_date.isoformat() if log.next_review_date else None,
                    "days_overdue": (today - log.next_review_date).days if log.next_review_date else 0,
                    "activity_content": activity.content
                })
        
        return jsonify({
            "success": True,
            "data": {
                "due_reviews": reviews_data,
                "count": len(reviews_data)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_due_reviews: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
#  PHASE 3 CEFR-BASED LEARNING PATH ENDPOINTS
# ============================================================================

@learning_path_bp.route('/phase3/curriculum-levels', methods=['GET'])
@jwt_required()
def get_phase3_curriculum_levels():
    """
    Get all CEFR curriculum levels for Phase 3 learning system.
    
    Returns:
        JSON: List of CEFR levels (A1-C2) with full details
    """
    try:
        levels = Phase3CurriculumLevel.query.order_by(Phase3CurriculumLevel.level_order).all()
        
        return jsonify({
            "success": True,
            "data": {
                "levels": [level.to_dict() for level in levels],
                "total": len(levels)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/skill-domains', methods=['GET'])
@jwt_required()
def get_phase3_skill_domains():
    """
    Get all 6 skill domains for Phase 3 (Listening, Speaking, Reading, Writing, Vocabulary, Grammar).
    
    Returns:
        JSON: List of skill domains with sub-skills and assessment criteria
    """
    try:
        domains = Phase3SkillDomain.query.order_by(Phase3SkillDomain.order).all()
        
        return jsonify({
            "success": True,
            "data": {
                "domains": [domain.to_dict() for domain in domains],
                "total": len(domains)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/skill-level/<skill_domain>', methods=['GET'])
@jwt_required()
def get_user_skill_level(skill_domain):
    """
    Get user's current skill level (0-100 scale) for a specific skill domain.
    
    Args:
        skill_domain (str): One of: listening, speaking, reading, writing, vocabulary, grammar
    
    Returns:
        JSON: User's current skill level and progress metrics
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        if not skill_profile:
            skill_profile = Phase3UserSkillProfile(user_id=current_user_id)
            db.session.add(skill_profile)
            db.session.commit()
        
        # Map skill domain to attribute
        skill_mapping = {
            'listening': 'listening_level',
            'speaking': 'speaking_level',
            'reading': 'reading_level',
            'writing': 'writing_level',
            'vocabulary': 'vocabulary_level',
            'grammar': 'grammar_level'
        }
        
        if skill_domain.lower() not in skill_mapping:
            return jsonify({
                "success": False,
                "error": f"Invalid skill domain. Must be one of: {', '.join(skill_mapping.keys())}"
            }), 400
        
        skill_attr = skill_mapping[skill_domain.lower()]
        skill_level = getattr(skill_profile, skill_attr)
        trend_attr = f"{skill_domain.lower()}_trend"
        trend = getattr(skill_profile, trend_attr, 'stable')
        
        return jsonify({
            "success": True,
            "data": {
                "skill_domain": skill_domain.lower(),
                "current_level": skill_level,
                "trend": trend,
                "overall_level": skill_profile.overall_level,
                "last_updated": skill_profile.last_updated.isoformat() if skill_profile.last_updated else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/skill-levels', methods=['GET'])
@jwt_required()
def get_all_user_skill_levels():
    """
    Get user's skill levels for all 6 domains.
    
    Returns:
        JSON: All skill levels (0-100 each) and overall metrics
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get or create skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        if not skill_profile:
            skill_profile = Phase3UserSkillProfile(user_id=current_user_id)
            db.session.add(skill_profile)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "data": skill_profile.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/next-activity', methods=['POST'])
@jwt_required()
def get_phase3_next_activity():
    """
    Get next optimal activity based on Phase 3 adaptive difficulty engine.
    
    Request Body (optional):
    {
        "preferred_skill": "listening",  # Optional: preferred skill domain
        "target_difficulty": 0.5  # Optional: target difficulty (0-1)
    }
    
    Returns:
        JSON: Recommended next activity with optimal difficulty
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get user's skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        if not skill_profile:
            skill_profile = Phase3UserSkillProfile(user_id=current_user_id)
            db.session.add(skill_profile)
            db.session.commit()
        
        # Get preferred skill (optional)
        preferred_skill = data.get('preferred_skill')
        
        # Get weak areas for targeting
        weak_areas = skill_profile.weak_areas or []
        
        # Determine optimal difficulty
        if preferred_skill:
            skill_level = getattr(skill_profile, f"{preferred_skill.lower()}_level", 0)
        else:
            # Use overall level if no preference
            skill_level = skill_profile.overall_level
        
        # Use difficulty engine to get recommended difficulty
        recommended_difficulty = difficulty_engine.recommend_difficulty_adjustment(
            current_accuracy=skill_level / 100,  # Convert to 0-1 scale
            attempt_count=1
        )
        
        # Get learning nodes for recommendation
        query = Phase3LearningNode.query.filter_by(is_active=True)
        
        if preferred_skill:
            domain = Phase3SkillDomain.query.filter_by(domain_name=preferred_skill.title()).first()
            if domain:
                query = query.filter_by(skill_domain_id=domain.id)
        
        # Get nodes matching difficulty range
        nodes = query.all()
        suitable_nodes = [
            n for n in nodes
            if n.difficulty_min <= recommended_difficulty <= n.difficulty_max
        ]
        
        if not suitable_nodes:
            # Fall back to any available node
            suitable_nodes = nodes[:3] if nodes else []
        
        if not suitable_nodes:
            return jsonify({
                "success": False,
                "error": "No suitable learning nodes found"
            }), 404
        
        # Return top recommended node
        recommended_node = suitable_nodes[0]
        
        return jsonify({
            "success": True,
            "data": {
                "node": recommended_node.to_dict(),
                "recommended_difficulty": recommended_difficulty,
                "reason": "Selected based on your current skill level and learning pattern",
                "weak_areas_targeted": weak_areas[:3] if weak_areas else []
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_phase3_next_activity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/plan-session', methods=['POST'])
@jwt_required()
def plan_phase3_session():
    """
    Plan a complete learning session (warm-up → main → cool-down).
    
    Request Body:
    {
        "duration_minutes": 30,  # Total session duration
        "focus_skill": "listening"  # Optional: focus on specific skill
    }
    
    Returns:
        JSON: Session plan with activity sequence and timing
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        duration = int(data.get('duration_minutes', 30))
        focus_skill = data.get('focus_skill')
        
        # Plan structure: 20% warmup, 60% main, 20% cooldown
        warmup_time = int(duration * 0.2)
        main_time = int(duration * 0.6)
        cooldown_time = int(duration * 0.2)
        
        # Get skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        if not skill_profile:
            skill_profile = Phase3UserSkillProfile(user_id=current_user_id)
            db.session.add(skill_profile)
            db.session.commit()
        
        # Get available nodes
        nodes = Phase3LearningNode.query.filter_by(is_active=True).all()
        
        plan = {
            "total_duration_minutes": duration,
            "sections": {
                "warmup": {
                    "duration_minutes": warmup_time,
                    "description": "Review previous concepts to build confidence",
                    "nodes": [n.to_dict() for n in nodes[:1]] if nodes else []
                },
                "main": {
                    "duration_minutes": main_time,
                    "description": f"Main learning focus: {focus_skill or 'comprehensive practice'}",
                    "nodes": [n.to_dict() for n in nodes[1:min(4, len(nodes))]]
                },
                "cooldown": {
                    "duration_minutes": cooldown_time,
                    "description": "Practice new concepts with lower pressure",
                    "nodes": [n.to_dict() for n in nodes[min(4, len(nodes)):-1]]
                }
            }
        }
        
        return jsonify({
            "success": True,
            "data": plan
        }), 200
        
    except Exception as e:
        print(f"Error in plan_phase3_session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/adjust-difficulty', methods=['POST'])
@jwt_required()
def adjust_phase3_difficulty():
    """
    Adjust recommended difficulty based on user's performance.
    
    Request Body:
    {
        "current_accuracy": 0.85,  # User's current accuracy (0-1)
        "attempt_count": 3  # Number of attempts so far
    }
    
    Returns:
        JSON: Recommended difficulty level and explanation
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        current_accuracy = float(data.get('current_accuracy', 0.5))
        attempt_count = int(data.get('attempt_count', 1))
        
        # Validate inputs
        if not 0.0 <= current_accuracy <= 1.0:
            return jsonify({
                "success": False,
                "error": "current_accuracy must be between 0.0 and 1.0"
            }), 400
        
        # Use difficulty engine
        recommended_difficulty = difficulty_engine.recommend_difficulty_adjustment(
            current_accuracy=current_accuracy,
            attempt_count=attempt_count
        )
        
        # Determine adjustment direction
        target_accuracy = 0.75  # 75% is sweet spot
        if current_accuracy > target_accuracy:
            adjustment = "increase"
            explanation = "Your performance is strong. Increasing difficulty to continue challenging yourself."
        elif current_accuracy < 0.5:
            adjustment = "decrease"
            explanation = "Your performance indicates this level is challenging. Decreasing difficulty to build confidence."
        else:
            adjustment = "maintain"
            explanation = "Your performance is at a good learning level. Maintaining current difficulty."
        
        return jsonify({
            "success": True,
            "data": {
                "current_accuracy": current_accuracy,
                "recommended_difficulty": recommended_difficulty,
                "adjustment": adjustment,
                "explanation": explanation,
                "target_accuracy": target_accuracy
            }
        }), 200
        
    except Exception as e:
        print(f"Error in adjust_phase3_difficulty: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/skill-trajectory/<skill_domain>', methods=['GET'])
@jwt_required()
def get_phase3_skill_trajectory(skill_domain):
    """
    Get skill improvement trajectory and progress analysis for a specific domain.
    
    Args:
        skill_domain (str): One of: listening, speaking, reading, writing, vocabulary, grammar
    
    Returns:
        JSON: Skill trajectory with trend analysis and recommendations
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Validate skill domain
        valid_domains = ['listening', 'speaking', 'reading', 'writing', 'vocabulary', 'grammar']
        if skill_domain.lower() not in valid_domains:
            return jsonify({
                "success": False,
                "error": f"Invalid skill domain. Must be one of: {', '.join(valid_domains)}"
            }), 400
        
        # Get user's skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        if not skill_profile:
            return jsonify({
                "success": False,
                "error": "User skill profile not found"
            }), 404
        
        # Get current level and trend
        skill_attr = f"{skill_domain.lower()}_level"
        trend_attr = f"{skill_domain.lower()}_trend"
        
        current_level = getattr(skill_profile, skill_attr, 0)
        trend = getattr(skill_profile, trend_attr, 'stable')
        
        # Get user's node progress for this domain
        domain = Phase3SkillDomain.query.filter_by(domain_name=skill_domain.title()).first()
        if domain:
            node_progress = Phase3UserLearningNodeProgress.query.filter(
                Phase3UserLearningNodeProgress.user_id == current_user_id,
                Phase3LearningNode.skill_domain_id == domain.id
            ).all()
        else:
            node_progress = []
        
        # Calculate trajectory metrics
        completed_nodes = len([p for p in node_progress if p.status == 'completed'])
        avg_score = (
            sum(p.best_score for p in node_progress if p.best_score) / len(node_progress)
            if node_progress else 0
        )
        
        # Determine trajectory message
        if trend == 'improving':
            trajectory_msg = "Excellent! Your skills are improving steadily."
        elif trend == 'declining':
            trajectory_msg = "Your performance is declining. Consider more practice in this area."
        else:
            trajectory_msg = "Your performance is stable. Keep consistent practice!"
        
        return jsonify({
            "success": True,
            "data": {
                "skill_domain": skill_domain.lower(),
                "current_level": current_level,
                "trend": trend,
                "trajectory_message": trajectory_msg,
                "progress": {
                    "nodes_completed": completed_nodes,
                    "average_score": round(avg_score, 2),
                    "total_attempts": sum(p.attempts for p in node_progress)
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_phase3_skill_trajectory: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/difficulty-recommendation', methods=['POST'])
@jwt_required()
def get_phase3_difficulty_recommendation():
    """
    Get AI recommendation for difficulty level based on comprehensive user metrics.
    
    Request Body:
    {
        "recent_performance": [0.8, 0.75, 0.82],  # Recent accuracy scores
        "time_in_system_days": 30  # How long user has been in system
    }
    
    Returns:
        JSON: Difficulty recommendation with reasoning
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        recent_performance = data.get('recent_performance', [0.75])
        time_in_system_days = int(data.get('time_in_system_days', 1))
        
        # Calculate average performance
        avg_performance = sum(recent_performance) / len(recent_performance) if recent_performance else 0.5
        
        # Get skill profile
        skill_profile = Phase3UserSkillProfile.query.filter_by(user_id=current_user_id).first()
        overall_level = skill_profile.overall_level if skill_profile else 0
        
        # Use engine to recommend
        recommended_difficulty = difficulty_engine.recommend_difficulty_adjustment(
            current_accuracy=avg_performance,
            attempt_count=len(recent_performance)
        )
        
        # Generate recommendation explanation
        factors = {
            "average_performance": round(avg_performance, 2),
            "overall_skill_level": round(overall_level, 2),
            "time_in_system_days": time_in_system_days,
            "recommended_difficulty": round(recommended_difficulty, 2)
        }
        
        recommendation_text = f"Based on your {time_in_system_days}-day journey with {round(avg_performance*100, 1)}% accuracy, we recommend difficulty level {round(recommended_difficulty*100, 0)}/100."
        
        return jsonify({
            "success": True,
            "data": {
                "recommendation": recommendation_text,
                "recommended_difficulty": recommended_difficulty,
                "factors": factors,
                "confidence": 0.85  # Confidence in the recommendation
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_phase3_difficulty_recommendation: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/learning-nodes', methods=['GET'])
@jwt_required()
def get_phase3_learning_nodes():
    """
    Get all available Phase 3 learning nodes with filtering options.
    
    Query Parameters:
    - level: CEFR level (A1, A2, B1, B2, C1, C2)
    - skill_domain: Skill domain ID
    - difficulty_min: Minimum difficulty (0-1)
    - difficulty_max: Maximum difficulty (0-1)
    
    Returns:
        JSON: List of learning nodes
    """
    try:
        # Get query parameters
        level_code = request.args.get('level')
        skill_domain_id = request.args.get('skill_domain_id', type=int)
        difficulty_min = request.args.get('difficulty_min', type=float)
        difficulty_max = request.args.get('difficulty_max', type=float)
        
        # Build query
        query = Phase3LearningNode.query.filter_by(is_active=True)
        
        # Filter by CEFR level
        if level_code:
            level = Phase3CurriculumLevel.query.filter_by(cefr_level=level_code.upper()).first()
            if level:
                query = query.filter_by(curriculum_level_id=level.id)
        
        # Filter by skill domain
        if skill_domain_id:
            query = query.filter_by(skill_domain_id=skill_domain_id)
        
        # Filter by difficulty range
        if difficulty_min is not None:
            query = query.filter(Phase3LearningNode.difficulty_min >= difficulty_min)
        if difficulty_max is not None:
            query = query.filter(Phase3LearningNode.difficulty_max <= difficulty_max)
        
        nodes = query.all()
        
        return jsonify({
            "success": True,
            "data": {
                "nodes": [node.to_dict() for node in nodes],
                "total": len(nodes)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_phase3_learning_nodes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@learning_path_bp.route('/phase3/node-progress/<node_id>', methods=['GET'])
@jwt_required()
def get_phase3_node_progress(node_id):
    """
    Get user's progress on a specific learning node.
    
    Args:
        node_id (str): The learning node ID (e.g., "A1_GREETING_001")
    
    Returns:
        JSON: User's progress, attempts, mastery level, etc.
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get learning node
        node = Phase3LearningNode.query.filter_by(node_id=node_id).first()
        if not node:
            return jsonify({
                "success": False,
                "error": f"Learning node {node_id} not found"
            }), 404
        
        # Get user's progress on this node
        progress = Phase3UserLearningNodeProgress.query.filter_by(
            user_id=current_user_id,
            learning_node_id=node.id
        ).first()
        
        if not progress:
            # Create new progress record if doesn't exist
            progress = Phase3UserLearningNodeProgress(
                user_id=current_user_id,
                learning_node_id=node.id,
                status='not_started'
            )
            db.session.add(progress)
            db.session.commit()
        
        return jsonify({
            "success": True,
            "data": {
                "node": node.to_dict(),
                "user_progress": progress.to_dict()
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_phase3_node_progress: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
