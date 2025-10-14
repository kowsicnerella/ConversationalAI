"""
Goal Achievement API Routes
Endpoints for goal management, progress tracking, and certificates
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.goal_service import GoalService

goals_bp = Blueprint('goals', __name__, url_prefix='/api/goals')

# ===== GOAL MANAGEMENT =====

@goals_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_goals():
    """Get all available goal types"""
    try:
        user_id = int(get_jwt_identity())
        
        goals = GoalService.get_available_goals(user_id)
        
        if isinstance(goals, dict) and 'error' in goals:
            return jsonify(goals), 400
        
        return jsonify({
            'success': True,
            'available_goals': goals,
            'total': len(goals)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/create', methods=['POST'])
@jwt_required()
def create_goal():
    """Create a new goal for user"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required'
            }), 400
        
        # Validate required fields for custom goals
        if data.get('is_custom'):
            if not data.get('title') or not data.get('criteria'):
                return jsonify({
                    'error': 'Title and criteria are required for custom goals'
                }), 400
        else:
            if not data.get('goal_type_id'):
                return jsonify({
                    'error': 'goal_type_id is required for template goals'
                }), 400
        
        result = GoalService.create_goal(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'message': 'Goal created successfully!',
            'goal': result
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/my-goals', methods=['GET'])
@jwt_required()
def get_my_goals():
    """Get user's goals with optional status filter"""
    try:
        user_id = int(get_jwt_identity())
        status = request.args.get('status')  # active, completed, paused, abandoned
        
        goals = GoalService.get_user_goals(user_id, status=status)
        
        if isinstance(goals, dict) and 'error' in goals:
            return jsonify(goals), 400
        
        # Separate by status for convenience
        active_goals = [g for g in goals if g['status'] == 'active']
        completed_goals = [g for g in goals if g['status'] == 'completed']
        
        return jsonify({
            'success': True,
            'goals': goals,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'total': len(goals),
            'active_count': len(active_goals),
            'completed_count': len(completed_goals)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/<int:goal_id>', methods=['GET'])
@jwt_required()
def get_goal_detail(goal_id):
    """Get detailed goal information with milestones"""
    try:
        user_id = int(get_jwt_identity())
        
        goal = GoalService.get_goal_detail(goal_id, include_milestones=True)
        
        if isinstance(goal, dict) and 'error' in goal:
            return jsonify(goal), 404
        
        # Verify goal belongs to user
        if goal['user_id'] != user_id:
            return jsonify({
                'error': 'Unauthorized access to goal'
            }), 403
        
        return jsonify({
            'success': True,
            'goal': goal
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/<int:goal_id>/update-progress', methods=['POST'])
@jwt_required()
def update_goal_progress(goal_id):
    """Update goal progress (called automatically by system)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Progress data is required'
            }), 400
        
        result = GoalService.update_goal_progress(user_id, data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully!'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/<int:goal_id>/complete', methods=['POST'])
@jwt_required()
def complete_goal_manually(goal_id):
    """Manually complete a goal (with celebration)"""
    try:
        result = GoalService.complete_goal(goal_id)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'message': '🎉 Congratulations! Goal completed!',
            **result
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/<int:goal_id>/abandon', methods=['POST'])
@jwt_required()
def abandon_goal(goal_id):
    """Mark a goal as abandoned"""
    try:
        user_id = int(get_jwt_identity())
        
        from app.models.goal import UserGoal
        goal = UserGoal.query.get(goal_id)
        
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        
        if goal.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        goal.status = 'abandoned'
        from app.models import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Goal abandoned'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== CERTIFICATES =====

@goals_bp.route('/certificates', methods=['GET'])
@jwt_required()
def get_my_certificates():
    """Get user's certificates"""
    try:
        user_id = int(get_jwt_identity())
        
        certificates = GoalService.get_user_certificates(user_id)
        
        if isinstance(certificates, dict) and 'error' in certificates:
            return jsonify(certificates), 400
        
        return jsonify({
            'success': True,
            'certificates': certificates,
            'total': len(certificates)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/certificates/<int:certificate_id>', methods=['GET'])
@jwt_required()
def get_certificate_detail(certificate_id):
    """Get certificate details"""
    try:
        user_id = int(get_jwt_identity())
        
        from app.models.goal import Certificate
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        if certificate.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'certificate': certificate.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/certificates/<int:certificate_id>/download', methods=['GET'])
@jwt_required()
def download_certificate(certificate_id):
    """Download certificate PDF"""
    try:
        user_id = int(get_jwt_identity())
        
        from app.models.goal import Certificate
        certificate = Certificate.query.get(certificate_id)
        
        if not certificate:
            return jsonify({'error': 'Certificate not found'}), 404
        
        if certificate.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # TODO: Generate and serve PDF
        return jsonify({
            'success': True,
            'message': 'PDF generation coming soon',
            'download_url': certificate.pdf_url
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@goals_bp.route('/certificates/verify/<certificate_number>', methods=['GET'])
def verify_certificate(certificate_number):
    """Public endpoint to verify certificate authenticity"""
    try:
        from app.models.goal import Certificate
        certificate = Certificate.query.filter_by(certificate_number=certificate_number).first()
        
        if not certificate:
            return jsonify({
                'valid': False,
                'message': 'Certificate not found'
            }), 404
        
        if not certificate.is_public:
            return jsonify({
                'valid': False,
                'message': 'This certificate is private'
            }), 403
        
        from app.models.user import User
        user = User.query.get(certificate.user_id)
        
        return jsonify({
            'valid': True,
            'certificate': {
                'number': certificate.certificate_number,
                'title': certificate.title,
                'issued_to': user.username if user else 'Unknown',
                'issued_date': certificate.issued_date.isoformat() if certificate.issued_date else None,
                'level_achieved': certificate.level_achieved,
                'skills_mastered': certificate.skills_mastered
            }
        }), 200
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


# ===== LEVEL PROGRESSION =====

@goals_bp.route('/level-progression', methods=['GET'])
@jwt_required()
def get_level_progression():
    """Get user's level progression history"""
    try:
        user_id = int(get_jwt_identity())
        
        progressions = GoalService.get_level_progression_history(user_id)
        
        if isinstance(progressions, dict) and 'error' in progressions:
            return jsonify(progressions), 400
        
        return jsonify({
            'success': True,
            'progressions': progressions,
            'total_levels': len(progressions)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== STATISTICS =====

@goals_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_goal_statistics():
    """Get goal statistics for dashboard"""
    try:
        user_id = int(get_jwt_identity())
        
        from app.models.goal import UserGoal, Certificate
        from sqlalchemy import func
        
        # Get counts by status
        active_count = UserGoal.query.filter_by(user_id=user_id, status='active').count()
        completed_count = UserGoal.query.filter_by(user_id=user_id, status='completed').count()
        total_count = UserGoal.query.filter_by(user_id=user_id).count()
        
        # Get certificates
        certificate_count = Certificate.query.filter_by(user_id=user_id).count()
        
        # Get current active goals
        active_goals = UserGoal.query.filter_by(user_id=user_id, status='active').all()
        active_goals_data = [g.to_dict() for g in active_goals]
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_goals': total_count,
                'active_goals': active_count,
                'completed_goals': completed_count,
                'certificates_earned': certificate_count,
                'completion_rate': round((completed_count / total_count * 100) if total_count > 0 else 0, 1)
            },
            'active_goals_summary': active_goals_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
