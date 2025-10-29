"""
Enhanced Activity Generation Routes - Phase 2
Provides endpoints for AI-powered personalized activity generation.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.enhanced_activity_generator import EnhancedActivityGenerator
from app.models.activity import Activity, UserActivityLog, db
from app.models.user import User

enhanced_activity_bp = Blueprint('enhanced_activity_v2', __name__)
generator = EnhancedActivityGenerator()


@enhanced_activity_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_personalized_activity():
    """
    Generate a fully personalized activity with Phase 2 enhancements.
    
    POST /api/activities-v2/generate
    
    Body (all optional):
    {
        "activity_type": "quiz",  // Optional: quiz, flashcard, reading, etc.
        "focus_skill": "vocabulary"  // Optional: vocabulary, grammar, reading, etc.
    }
    
    Returns:
    {
        "activity": {
            "activity_type": "quiz",
            "title": "...",
            "questions": [...],
            ...
        },
        "metadata": {
            "difficulty": 0.6,
            "focus_skill": "vocabulary",
            "weak_areas_targeted": ["grammar", "vocabulary"],
            ...
        }
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        activity_type = data.get('activity_type')
        focus_skill = data.get('focus_skill')
        
        # Generate personalized activity
        activity = generator.generate_personalized_activity(
            user_id=current_user_id,
            activity_type=activity_type,
            focus_skill=focus_skill
        )
        
        if 'error' in activity:
            return jsonify(activity), 400
        
        return jsonify(activity), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to generate activity', 'details': str(e)}), 500


@enhanced_activity_bp.route('/suggest', methods=['GET'])
@jwt_required()
def suggest_next_activity():
    """
    Suggest the optimal next activity type and focus area.
    
    GET /api/activities-v2/suggest
    
    Returns:
    {
        "suggested_type": "quiz",
        "suggested_skill": "grammar",
        "reason": "Your grammar scores are below 60%. Let's practice!",
        "difficulty": 0.5,
        "estimated_time": 7
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        # Get user profile and performance
        user_profile = generator._get_user_profile(current_user_id)
        if not user_profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        performance = generator._analyze_recent_performance(current_user_id)
        weak_areas = generator._identify_weak_areas(current_user_id, performance)
        difficulty = generator._calculate_optimal_difficulty(user_profile, performance)
        
        # Select activity type
        suggested_type = generator._select_activity_type(weak_areas, performance)
        suggested_skill = weak_areas[0]['skill'] if weak_areas else 'vocabulary'
        
        # Build reason
        if weak_areas:
            reason = f"Your {suggested_skill} scores are at {weak_areas[0]['score']}%. Let's practice to improve!"
        else:
            reason = "Great work! Let's keep up the momentum with balanced practice."
        
        return jsonify({
            'suggested_type': suggested_type,
            'suggested_skill': suggested_skill,
            'reason': reason,
            'difficulty': round(difficulty, 2),
            'estimated_time': 7,
            'weak_areas': weak_areas[:3],
            'performance_summary': performance
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to generate suggestion', 'details': str(e)}), 500


@enhanced_activity_bp.route('/performance', methods=['GET'])
@jwt_required()
def get_user_performance():
    """
    Get detailed performance analysis for the user.
    
    GET /api/activities-v2/performance?days=7
    
    Query params:
    - days: Number of days to analyze (default: 7)
    
    Returns:
    {
        "performance": {
            "total_activities": 15,
            "avg_accuracy": 78.5,
            "improvement_trend": 5.2,
            ...
        },
        "weak_areas": [...],
        "user_profile": {...}
    }
    """
    try:
        current_user_id = int(get_jwt_identity())
        days = int(request.args.get('days', 7))
        
        user_profile = generator._get_user_profile(current_user_id)
        if not user_profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        performance = generator._analyze_recent_performance(current_user_id, days)
        weak_areas = generator._identify_weak_areas(current_user_id, performance)
        difficulty = generator._calculate_optimal_difficulty(user_profile, performance)
        
        return jsonify({
            'performance': performance,
            'weak_areas': weak_areas,
            'user_profile': {
                'proficiency_level': user_profile['proficiency_level'],
                'current_streak': user_profile['current_streak'],
                'total_activities': user_profile['total_activities'],
                'avg_performance': user_profile['avg_performance']
            },
            'optimal_difficulty': round(difficulty, 2)
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to analyze performance', 'details': str(e)}), 500


@enhanced_activity_bp.route('/difficulty-test', methods=['GET'])
@jwt_required()
def test_difficulty_calculation():
    """
    Test endpoint to see how difficulty is calculated for the user.
    Useful for debugging and understanding the personalization logic.
    
    GET /api/activities-v2/difficulty-test
    
    Returns detailed breakdown of difficulty calculation.
    """
    try:
        current_user_id = int(get_jwt_identity())
        user_profile = generator._get_user_profile(current_user_id)
        if not user_profile:
            return jsonify({'error': 'User profile not found'}), 404
        
        performance = generator._analyze_recent_performance(current_user_id)
        difficulty = generator._calculate_optimal_difficulty(user_profile, performance)
        
        # Build explanation
        level_difficulty = {
            'beginner': 0.3, 'elementary': 0.4, 'intermediate': 0.5,
            'upper_intermediate': 0.6, 'advanced': 0.7, 'proficient': 0.8
        }
        
        base = level_difficulty.get(user_profile['proficiency_level'], 0.4)
        
        explanation = {
            'base_difficulty': base,
            'base_reason': f"User is {user_profile['proficiency_level']} level",
            'adjustments': []
        }
        
        if performance['avg_accuracy'] > 0:
            if performance['avg_accuracy'] >= 85:
                explanation['adjustments'].append({
                    'type': 'accuracy_high',
                    'change': +0.1,
                    'reason': f"High accuracy ({performance['avg_accuracy']}%) - increase challenge"
                })
            elif performance['avg_accuracy'] < 60:
                explanation['adjustments'].append({
                    'type': 'accuracy_low',
                    'change': -0.1,
                    'reason': f"Low accuracy ({performance['avg_accuracy']}%) - decrease challenge"
                })
        
        if performance['improvement_trend'] > 10:
            explanation['adjustments'].append({
                'type': 'improving',
                'change': +0.05,
                'reason': 'Showing strong improvement - push harder'
            })
        elif performance['improvement_trend'] < -10:
            explanation['adjustments'].append({
                'type': 'struggling',
                'change': -0.05,
                'reason': 'Struggling recently - ease up'
            })
        
        explanation['final_difficulty'] = round(difficulty, 2)
        
        return jsonify(explanation), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to calculate difficulty', 'details': str(e)}), 500
