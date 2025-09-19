
from flask import Blueprint, jsonify, request
from app.services.gamification_service import GamificationService
from app.models import db, Badge, Achievement

gamification_bp = Blueprint('gamification', __name__)
gamification_service = GamificationService()

@gamification_bp.route('/badges/<int:user_id>', methods=['GET'])
def get_user_badges(user_id):
    """Get all badges earned by a user"""
    try:
        badges = gamification_service.get_user_badges(user_id)
        return jsonify({'badges': badges}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch badges', 'details': str(e)}), 500

@gamification_bp.route('/badges/available', methods=['GET'])
def get_available_badges():
    """Get all available badges in the system"""
    try:
        badges = Badge.query.all()
        
        badge_list = []
        for badge in badges:
            badge_list.append({
                'id': badge.id,
                'name': badge.name,
                'description': badge.description,
                'category': badge.category,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'points_reward': badge.points_reward,
                'rarity': badge.rarity,
                'icon_url': badge.icon_url
            })
        
        return jsonify({'available_badges': badge_list}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch available badges', 'details': str(e)}), 500

@gamification_bp.route('/check-achievements/<int:user_id>', methods=['POST'])
def check_achievements(user_id):
    """Check and award new achievements for a user"""
    try:
        new_badges = gamification_service.check_for_new_achievements(user_id)
        
        return jsonify({
            'message': 'Achievement check completed',
            'new_badges': new_badges,
            'badges_awarded': len(new_badges)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to check achievements', 'details': str(e)}), 500

@gamification_bp.route('/streak/<int:user_id>', methods=['POST'])
def update_streak(user_id):
    """Update user's daily streak"""
    try:
        success = gamification_service.update_streak(user_id)
        
        if success:
            return jsonify({'message': 'Streak updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update streak'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Streak update failed', 'details': str(e)}), 500

@gamification_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the points leaderboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        time_period = request.args.get('time_period', 'all_time')
        
        if limit > 50:  # Prevent excessive requests
            limit = 50
        
        leaderboard = gamification_service.get_leaderboard(limit, time_period)
        
        return jsonify({
            'leaderboard': leaderboard,
            'time_period': time_period,
            'total_users': len(leaderboard)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch leaderboard', 'details': str(e)}), 500

@gamification_bp.route('/daily-challenge/<int:user_id>', methods=['GET'])
def get_daily_challenge(user_id):
    """Get daily challenge status for a user"""
    try:
        challenge_status = gamification_service.get_daily_challenge_status(user_id)
        
        return jsonify({
            'daily_challenge': challenge_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch daily challenge', 'details': str(e)}), 500

@gamification_bp.route('/achievements', methods=['GET'])
def get_all_achievements():
    """Get all available achievements"""
    try:
        achievements = Achievement.query.filter_by(is_active=True).all()
        
        achievement_list = []
        for achievement in achievements:
            achievement_list.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'achievement_type': achievement.achievement_type,
                'target_value': achievement.target_value,
                'points_reward': achievement.points_reward
            })
        
        return jsonify({'achievements': achievement_list}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch achievements', 'details': str(e)}), 500

@gamification_bp.route('/stats/<int:user_id>', methods=['GET'])
def get_gamification_stats(user_id):
    """Get comprehensive gamification statistics for a user"""
    try:
        # Get user badges
        badges = gamification_service.get_user_badges(user_id)
        
        # Get daily challenge status
        daily_challenge = gamification_service.get_daily_challenge_status(user_id)
        
        # Get user's rank in leaderboard
        leaderboard = gamification_service.get_leaderboard(100)  # Get top 100
        user_rank = None
        for idx, entry in enumerate(leaderboard):
            if 'user_id' in entry and entry['user_id'] == user_id:
                user_rank = idx + 1
                break
        
        return jsonify({
            'gamification_stats': {
                'badges': badges,
                'total_badges': len(badges),
                'daily_challenge': daily_challenge,
                'leaderboard_rank': user_rank,
                'total_leaderboard_users': len(leaderboard)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch gamification stats', 'details': str(e)}), 500
