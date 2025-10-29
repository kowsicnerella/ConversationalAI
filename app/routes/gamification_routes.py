"""
Gamification API Routes
Endpoints for daily challenges, achievements, leaderboards, streaks, milestones, and social features
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
import logging

from app.services.gamification_service import gamification_service
from app.models.gamification_enhanced import (
    DailyChallenge, Achievement, UserAchievement, LeaderboardEntry,
    LearningStreak, ProgressMilestone, SocialConnection, SharedAchievement
)
from app import db

logger = logging.getLogger(__name__)

# Create blueprint
gamification_bp = Blueprint('gamification', __name__, url_prefix='/api/gamification')


# ============================================================================
# DAILY CHALLENGES
# ============================================================================

@gamification_bp.route('/challenges/today', methods=['GET'])
@jwt_required()
def get_daily_challenges():
    """
    Get today's daily challenges for the user
    
    Returns:
        200: List of challenges
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        # Generate challenges if they don't exist
        challenges = gamification_service.generate_daily_challenges(user_id)
        
        return jsonify({
            'challenges': challenges,
            'count': len(challenges)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily challenges: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/challenges/history', methods=['GET'])
@jwt_required()
def get_challenge_history():
    """
    Get challenge history for past 30 days
    
    Returns:
        200: Challenge history
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        # Get challenges from last 30 days
        challenges = DailyChallenge.query.filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.challenge_date >= date.today() - timedelta(days=30)
        ).order_by(DailyChallenge.challenge_date.desc()).all()
        
        # Group by date
        history = {}
        for challenge in challenges:
            date_key = challenge.challenge_date.isoformat()
            if date_key not in history:
                history[date_key] = []
            history[date_key].append(challenge.to_dict())
        
        return jsonify({
            'history': history,
            'total_challenges': len(challenges),
            'completed_count': sum(1 for c in challenges if c.is_completed)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting challenge history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/challenges/<int:challenge_id>/complete', methods=['POST'])
@jwt_required()
def manual_complete_challenge(challenge_id):
    """
    Manually mark a challenge as complete (for testing or manual completion)
    
    Args:
        challenge_id: Challenge ID
        
    Returns:
        200: Challenge completed
        404: Challenge not found
        403: Unauthorized
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        challenge = DailyChallenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        if challenge.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if challenge.is_completed:
            return jsonify({'error': 'Challenge already completed'}), 400
        
        # Complete challenge
        challenge.update_progress(challenge.target_value)
        
        # Award points
        total_points = int(challenge.points_reward * challenge.bonus_multiplier)
        gamification_service._award_points(user_id, total_points, f"Challenge: {challenge.title}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Challenge completed',
            'challenge': challenge.to_dict(),
            'points_earned': total_points
        }), 200
        
    except Exception as e:
        logger.error(f"Error completing challenge: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# ACHIEVEMENTS
# ============================================================================

@gamification_bp.route('/achievements', methods=['GET'])
@jwt_required()
def get_achievements():
    """
    Get all achievements with user's progress
    
    Query params:
        category: Filter by category (optional)
        
    Returns:
        200: Achievement data
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        category = request.args.get('category')
        
        achievements = gamification_service.get_user_achievements(user_id, category)
        
        return jsonify(achievements), 200
        
    except Exception as e:
        logger.error(f"Error getting achievements: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/achievements/<int:achievement_id>/showcase', methods=['POST'])
@jwt_required()
def showcase_achievement(achievement_id):
    """
    Toggle showcase status for an achievement
    
    Args:
        achievement_id: Achievement ID
        
    Returns:
        200: Showcase updated
        404: Achievement not found
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        user_achievement = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement_id
        ).first()
        
        if not user_achievement:
            return jsonify({'error': 'Achievement not unlocked'}), 404
        
        # Toggle showcase
        user_achievement.is_showcased = not user_achievement.is_showcased
        db.session.commit()
        
        return jsonify({
            'message': 'Showcase status updated',
            'is_showcased': user_achievement.is_showcased
        }), 200
        
    except Exception as e:
        logger.error(f"Error showcasing achievement: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# LEADERBOARDS
# ============================================================================

@gamification_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """
    Get leaderboard rankings
    
    Query params:
        category: Leaderboard category (default: overall)
        time_period: Time period (daily, weekly, monthly, all_time) (default: weekly)
        limit: Number of entries (default: 100)
        
    Returns:
        200: Leaderboard data
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        category = request.args.get('category', 'overall')
        time_period = request.args.get('time_period', 'weekly')
        limit = int(request.args.get('limit', 100))
        
        leaderboard = gamification_service.get_leaderboard(
            category=category,
            time_period=time_period,
            limit=limit,
            user_id=user_id
        )
        
        return jsonify(leaderboard), 200
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/leaderboard/categories', methods=['GET'])
@jwt_required()
def get_leaderboard_categories():
    """
    Get available leaderboard categories
    
    Returns:
        200: List of categories
    """
    categories = [
        {'key': 'overall', 'name': 'Overall', 'icon': '🏆'},
        {'key': 'vocabulary', 'name': 'Vocabulary', 'icon': '📚'},
        {'key': 'grammar', 'name': 'Grammar', 'icon': '✍️'},
        {'key': 'reading', 'name': 'Reading', 'icon': '📖'},
        {'key': 'writing', 'name': 'Writing', 'icon': '✏️'},
        {'key': 'speaking', 'name': 'Speaking', 'icon': '🗣️'},
        {'key': 'listening', 'name': 'Listening', 'icon': '👂'},
        {'key': 'streak', 'name': 'Longest Streak', 'icon': '🔥'},
        {'key': 'study_time', 'name': 'Study Time', 'icon': '⏱️'}
    ]
    
    return jsonify({'categories': categories}), 200


# ============================================================================
# LEARNING STREAKS
# ============================================================================

@gamification_bp.route('/streak', methods=['GET'])
@jwt_required()
def get_streak():
    """
    Get user's learning streak information
    
    Returns:
        200: Streak data
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        streak = gamification_service.get_user_streak(user_id)
        
        return jsonify(streak), 200
        
    except Exception as e:
        logger.error(f"Error getting streak: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/streak/freeze', methods=['POST'])
@jwt_required()
def use_streak_freeze():
    """
    Use a streak freeze to protect today's streak
    
    Returns:
        200: Freeze used successfully
        400: Cannot use freeze
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        result = gamification_service.use_streak_freeze(user_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Error using streak freeze: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/streak/update', methods=['POST'])
@jwt_required()
def update_streak():
    """
    Manually update streak (called after completing an activity)
    
    Returns:
        200: Streak updated
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        streak = gamification_service.update_streak(user_id)
        
        return jsonify(streak), 200
        
    except Exception as e:
        logger.error(f"Error updating streak: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# PROGRESS MILESTONES
# ============================================================================

@gamification_bp.route('/milestones', methods=['GET'])
@jwt_required()
def get_milestones():
    """
    Get user's progress milestones
    
    Query params:
        milestone_type: Filter by type (optional)
        limit: Number of recent milestones (default: 20)
        
    Returns:
        200: Milestone data
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        milestone_type = request.args.get('milestone_type')
        limit = int(request.args.get('limit', 20))
        
        query = ProgressMilestone.query.filter_by(user_id=user_id)
        
        if milestone_type:
            query = query.filter_by(milestone_type=milestone_type)
        
        milestones = query.order_by(
            ProgressMilestone.reached_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'milestones': [m.to_dict() for m in milestones],
            'total_count': ProgressMilestone.query.filter_by(user_id=user_id).count(),
            'uncelebrated_count': ProgressMilestone.query.filter_by(
                user_id=user_id,
                celebrated=False
            ).count()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting milestones: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/milestones/<int:milestone_id>/celebrate', methods=['POST'])
@jwt_required()
def celebrate_milestone(milestone_id):
    """
    Mark a milestone as celebrated
    
    Args:
        milestone_id: Milestone ID
        
    Returns:
        200: Milestone celebrated
        404: Milestone not found
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        milestone = ProgressMilestone.query.filter_by(
            id=milestone_id,
            user_id=user_id
        ).first()
        
        if not milestone:
            return jsonify({'error': 'Milestone not found'}), 404
        
        milestone.celebrated = True
        db.session.commit()
        
        return jsonify({
            'message': 'Milestone celebrated',
            'milestone': milestone.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error celebrating milestone: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# SOCIAL FEATURES
# ============================================================================

@gamification_bp.route('/social/connections', methods=['GET'])
@jwt_required()
def get_connections():
    """
    Get user's social connections
    
    Query params:
        status: Filter by status (pending, accepted, blocked)
        connection_type: Filter by type (friend, study_partner, practice_partner)
        
    Returns:
        200: Connection list
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        status = request.args.get('status')
        connection_type = request.args.get('connection_type')
        
        query = SocialConnection.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if connection_type:
            query = query.filter_by(connection_type=connection_type)
        
        connections = query.all()
        
        return jsonify({
            'connections': [c.to_dict() for c in connections],
            'count': len(connections)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting connections: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/social/connect/<int:target_user_id>', methods=['POST'])
@jwt_required()
def send_connection_request(target_user_id):
    """
    Send a connection request to another user
    
    Body:
        connection_type: Type of connection (friend, study_partner, practice_partner)
        
    Returns:
        201: Connection request sent
        400: Invalid request
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        if user_id == target_user_id:
            return jsonify({'error': 'Cannot connect with yourself'}), 400
        
        data = request.get_json()
        connection_type = data.get('connection_type', 'friend')
        
        # Check if connection already exists
        existing = SocialConnection.query.filter_by(
            user_id=user_id,
            connected_user_id=target_user_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Connection already exists'}), 400
        
        # Create connection request
        connection = SocialConnection(
            user_id=user_id,
            connected_user_id=target_user_id,
            connection_type=connection_type,
            status='pending'
        )
        
        db.session.add(connection)
        db.session.commit()
        
        return jsonify({
            'message': 'Connection request sent',
            'connection': connection.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error sending connection request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/social/share-achievement', methods=['POST'])
@jwt_required()
def share_achievement():
    """
    Share an achievement to social feed
    
    Body:
        achievement_id: Achievement ID
        caption: Optional caption
        visibility: public, friends, private
        
    Returns:
        201: Achievement shared
        404: Achievement not found
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        achievement_id = data.get('achievement_id')
        caption = data.get('caption', '')
        visibility = data.get('visibility', 'friends')
        
        # Verify user has unlocked this achievement
        user_achievement = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement_id
        ).first()
        
        if not user_achievement:
            return jsonify({'error': 'Achievement not unlocked'}), 404
        
        # Create share
        share = SharedAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            caption=caption,
            visibility=visibility
        )
        
        db.session.add(share)
        db.session.commit()
        
        return jsonify({
            'message': 'Achievement shared',
            'share': share.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error sharing achievement: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@gamification_bp.route('/social/feed', methods=['GET'])
@jwt_required()
def get_social_feed():
    """
    Get social feed with shared achievements from connections
    
    Query params:
        limit: Number of posts (default: 20)
        
    Returns:
        200: Social feed
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 20))
        
        # Get accepted connections
        connections = SocialConnection.query.filter_by(
            user_id=user_id,
            status='accepted'
        ).all()
        
        connected_user_ids = [c.connected_user_id for c in connections]
        connected_user_ids.append(user_id)  # Include own posts
        
        # Get shared achievements from connections
        shares = SharedAchievement.query.filter(
            SharedAchievement.user_id.in_(connected_user_ids),
            SharedAchievement.visibility.in_(['public', 'friends'])
        ).order_by(SharedAchievement.shared_at.desc()).limit(limit).all()
        
        return jsonify({
            'feed': [s.to_dict() for s in shares],
            'count': len(shares)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting social feed: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# GAMIFICATION SUMMARY
# ============================================================================

@gamification_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_gamification_summary():
    """
    Get comprehensive gamification summary for user
    
    Returns:
        200: Gamification summary
        500: Server error
    """
    try:
        user_id = get_jwt_identity()
        
        # Get streak
        streak = gamification_service.get_user_streak(user_id)
        
        # Get today's challenges
        challenges = gamification_service.get_user_challenges(user_id)
        
        # Get achievement stats
        achievements = gamification_service.get_user_achievements(user_id)
        
        # Get user's rank
        leaderboard = gamification_service.get_leaderboard('overall', 'weekly', 100, user_id)
        
        # Get recent milestones
        recent_milestones = ProgressMilestone.query.filter_by(
            user_id=user_id,
            celebrated=False
        ).order_by(ProgressMilestone.reached_at.desc()).limit(5).all()
        
        return jsonify({
            'streak': streak,
            'daily_challenges': {
                'challenges': challenges,
                'completed_count': sum(1 for c in challenges if c['is_completed'])
            },
            'achievements': {
                'unlocked_count': len(achievements['unlocked']),
                'total_count': len(achievements['unlocked']) + len(achievements['locked']),
                'unlock_percentage': achievements['unlock_percentage'],
                'total_points': achievements['total_points']
            },
            'leaderboard': {
                'rank': leaderboard['user_rank'],
                'total_participants': leaderboard['total_participants']
            },
            'uncelebrated_milestones': [m.to_dict() for m in recent_milestones]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting gamification summary: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@gamification_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gamification',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
