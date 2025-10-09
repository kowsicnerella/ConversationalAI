
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.gamification_service import GamificationService
from app.models import db, Badge, Achievement, Profile, User

gamification_bp = Blueprint('gamification', __name__)
gamification_service = GamificationService()

@gamification_bp.route('/points', methods=['GET'])
@jwt_required()
def get_user_points():
    """Get user's total points and streak"""
    try:
        user_id = int(get_jwt_identity())
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({
                'error': 'Profile not found',
                'telugu_error': 'ప్రొఫైల్ కనుగొనబడలేదు'
            }), 404
        
        return jsonify({
            'message': 'Points retrieved successfully',
            'telugu_message': 'పాయింట్లు విజయవంతంగా పొందబడ్డాయి',
            'points': profile.points or 0,
            'current_streak': profile.current_streak or 0,
            'proficiency_level': profile.proficiency_level,
            'last_activity_date': profile.last_activity_date.isoformat() if profile.last_activity_date else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch points',
            'telugu_error': 'పాయింట్లు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/badges', methods=['GET'])
@jwt_required()
def get_user_badges():
    """Get all badges (earned and available) for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get user's earned badges
        earned_badges = gamification_service.get_user_badges(user_id)
        earned_badge_ids = [b['id'] for b in earned_badges]
        
        # Get all available badges
        all_badges = Badge.query.all()
        
        badges_data = []
        for badge in all_badges:
            badge_info = {
                'id': badge.id,
                'name': badge.name,
                'description': badge.description,
                'category': badge.category,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'points_reward': badge.points_reward,
                'rarity': badge.rarity,
                'icon_url': badge.icon_url,
                'unlocked': badge.id in earned_badge_ids
            }
            
            # Add earned_at if unlocked
            if badge.id in earned_badge_ids:
                for earned in earned_badges:
                    if earned['id'] == badge.id:
                        badge_info['earned_at'] = earned['earned_at']
                        break
            
            badges_data.append(badge_info)
        
        return jsonify({
            'message': 'Badges retrieved successfully',
            'telugu_message': 'బ్యాడ్జ్‌లు విజయవంతంగా పొందబడ్డాయి',
            'badges': badges_data,
            'total_badges': len(badges_data),
            'earned_count': len(earned_badges),
            'locked_count': len(badges_data) - len(earned_badges)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch badges',
            'telugu_error': 'బ్యాడ్జ్‌లు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get the points leaderboard"""
    try:
        user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 10, type=int)
        timeframe = request.args.get('timeframe', 'all_time')  # all_time, weekly, monthly
        
        if limit > 100:  # Prevent excessive requests
            limit = 100
        
        leaderboard = gamification_service.get_leaderboard(limit, timeframe)
        
        # Find current user's rank
        user_rank = None
        user_entry = None
        for entry in leaderboard:
            if 'user_id' in entry and entry['user_id'] == user_id:
                user_rank = entry['rank']
                user_entry = entry
                break
        
        return jsonify({
            'message': 'Leaderboard retrieved successfully',
            'telugu_message': 'లీడర్‌బోర్డ్ విజయవంతంగా పొందబడింది',
            'leaderboard': leaderboard,
            'timeframe': timeframe,
            'total_users': len(leaderboard),
            'current_user_rank': user_rank,
            'current_user_entry': user_entry
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch leaderboard',
            'telugu_error': 'లీడర్‌బోర్డ్ పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/daily-challenge', methods=['GET'])
@jwt_required()
def get_daily_challenge_status():
    """Get daily challenge status for current user"""
    try:
        user_id = int(get_jwt_identity())
        challenge_status = gamification_service.get_daily_challenge_status(user_id)
        
        return jsonify({
            'message': 'Daily challenge status retrieved',
            'telugu_message': 'రోజువారీ సవాలు స్థితి పొందబడింది',
            'daily_challenge': challenge_status
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch daily challenge',
            'telugu_error': 'రోజువారీ సవాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/daily-challenge', methods=['POST'])
@jwt_required()
def track_daily_challenge():
    """Track progress towards daily challenge"""
    try:
        user_id = int(get_jwt_identity())
        
        # Update streak (will check and award daily bonus if applicable)
        gamification_service.update_streak(user_id)
        
        # Get updated challenge status
        challenge_status = gamification_service.get_daily_challenge_status(user_id)
        
        # Check for new achievements
        new_badges = gamification_service.check_for_new_achievements(user_id)
        
        response = {
            'message': 'Daily challenge progress updated',
            'telugu_message': 'రోజువారీ సవాలు పురోగతి నవీకరించబడింది',
            'daily_challenge': challenge_status
        }
        
        if new_badges:
            response['new_badges'] = new_badges
            response['badges_earned'] = len(new_badges)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to track daily challenge',
            'telugu_error': 'రోజువారీ సవాలును ట్రాక్ చేయడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_gamification_stats():
    """Get comprehensive gamification statistics for current user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get profile
        profile = Profile.query.filter_by(user_id=user_id).first()
        
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
            'message': 'Gamification stats retrieved',
            'telugu_message': 'గేమిఫికేషన్ గణాంకాలు పొందబడ్డాయి',
            'stats': {
                'points': profile.points or 0 if profile else 0,
                'current_streak': profile.current_streak or 0 if profile else 0,
                'badges': badges,
                'total_badges': len(badges),
                'daily_challenge': daily_challenge,
                'leaderboard_rank': user_rank,
                'total_leaderboard_users': len(leaderboard)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch gamification stats',
            'telugu_error': 'గేమిఫికేషన్ గణాంకాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@gamification_bp.route('/achievements', methods=['GET'])
@jwt_required()
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
        
        return jsonify({
            'message': 'Achievements retrieved successfully',
            'telugu_message': 'అచీవ్‌మెంట్‌లు విజయవంతంగా పొందబడ్డాయి',
            'achievements': achievement_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch achievements',
            'telugu_error': 'అచీవ్‌మెంట్‌లు పొందడంలో విఫలం',
            'details': str(e)
        }), 500
