from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Profile, ProficiencyAssessment, LearningPath, Milestone
from app.models.milestone import LessonReview
from datetime import datetime
import json

onboarding_bp = Blueprint('onboarding', __name__)


@onboarding_bp.route('/status', methods=['GET'])
@jwt_required()
def get_onboarding_status():
    """
    Get current onboarding status for the authenticated user.
    Returns which step of the onboarding process the user is at.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        # Check for initial assessment
        initial_assessment = None
        if user.initial_assessment_id:
            initial_assessment = ProficiencyAssessment.query.get(user.initial_assessment_id)
        
        # Check for active learning paths
        active_paths = LearningPath.query.filter_by(user_id=user_id).all()
        
        # Determine current step
        onboarding_step = 'welcome'
        if not user.onboarding_completed:
            if user.needs_initial_assessment:
                onboarding_step = 'assessment_needed'
            elif initial_assessment and initial_assessment.completed_at:
                if not active_paths:
                    onboarding_step = 'choose_learning_path'
                else:
                    onboarding_step = 'ready_to_start'
            elif initial_assessment and not initial_assessment.completed_at:
                onboarding_step = 'assessment_in_progress'
        else:
            onboarding_step = 'completed'
        
        return jsonify({
            'success': True,
            'onboarding_status': {
                'onboarding_completed': user.onboarding_completed,
                'needs_initial_assessment': user.needs_initial_assessment,
                'current_learning_phase': user.current_learning_phase,
                'current_step': onboarding_step,
                'assessment': {
                    'taken': initial_assessment is not None,
                    'completed': initial_assessment.completed_at is not None if initial_assessment else False,
                    'assessment_id': user.initial_assessment_id,
                    'proficiency_level': initial_assessment.proficiency_level if initial_assessment else None
                } if initial_assessment else None,
                'learning_paths': {
                    'generated': len(active_paths) > 0,
                    'count': len(active_paths),
                    'paths': [
                        {
                            'id': path.id,
                            'title': path.title,
                            'difficulty_level': path.difficulty_level
                        } for path in active_paths[:3]  # First 3 paths
                    ]
                },
                'profile': {
                    'proficiency_level': profile.proficiency_level if profile else 'beginner',
                    'mastery_metrics': profile.mastery_metrics if profile else {}
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting onboarding status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get onboarding status: {str(e)}'}), 500


@onboarding_bp.route('/status', methods=['POST'])
@jwt_required()
def update_onboarding_status():
    """
    Update user's onboarding status.
    Used to track progress through the onboarding flow.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields based on provided data
        if 'onboarding_completed' in data:
            user.onboarding_completed = data['onboarding_completed']
        
        if 'needs_initial_assessment' in data:
            user.needs_initial_assessment = data['needs_initial_assessment']
        
        if 'current_learning_phase' in data:
            valid_phases = ['onboarding', 'assessment', 'learning', 'mastery']
            if data['current_learning_phase'] in valid_phases:
                user.current_learning_phase = data['current_learning_phase']
        
        if 'initial_assessment_id' in data:
            user.initial_assessment_id = data['initial_assessment_id']
            user.assessment_taken_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Onboarding status updated successfully',
            'telugu_message': 'ఆన్‌బోర్డింగ్ స్థితి విజయవంతంగా నవీకరించబడింది',
            'updated_status': {
                'onboarding_completed': user.onboarding_completed,
                'needs_initial_assessment': user.needs_initial_assessment,
                'current_learning_phase': user.current_learning_phase,
                'assessment_taken_at': user.assessment_taken_at.isoformat() if user.assessment_taken_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating onboarding status: {str(e)}")
        return jsonify({'error': f'Failed to update onboarding status: {str(e)}'}), 500


@onboarding_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_onboarding():
    """
    Mark onboarding as complete when user finishes the entire flow.
    Awards a milestone achievement.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Mark onboarding as complete
        user.onboarding_completed = True
        user.current_learning_phase = 'learning'
        
        # Create milestone for completing onboarding
        milestone = Milestone(
            user_id=user_id,
            milestone_type='onboarding_complete',
            title='Onboarding Complete!',
            description='Successfully completed the onboarding process and ready to start learning',
            telugu_title='ఆన్‌బోర్డింగ్ పూర్తయింది!',
            telugu_description='ఆన్‌బోర్డింగ్ ప్రక్రియను విజయవంతంగా పూర్తి చేసి నేర్చుకోవడానికి సిద్ధంగా ఉన్నారు',
            icon='🎉',
            color='success',
            points_awarded=50,
            milestone_data={'timestamp': datetime.utcnow().isoformat()}
        )
        
        db.session.add(milestone)
        
        # Update profile points
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            profile.points += 50
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Congratulations! Onboarding completed successfully!',
            'telugu_message': 'అభినందనలు! ఆన్‌బోర్డింగ్ విజయవంతంగా పూర్తయింది!',
            'milestone': milestone.to_dict(),
            'points_awarded': 50
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error completing onboarding: {str(e)}")
        return jsonify({'error': f'Failed to complete onboarding: {str(e)}'}), 500


@onboarding_bp.route('/progress/snapshot', methods=['GET'])
@jwt_required()
def get_progress_snapshot():
    """
    Get comprehensive progress snapshot for the user.
    Used by dashboard and progress tracking components.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        if not user or not profile:
            return jsonify({'error': 'User or profile not found'}), 404
        
        # Get active learning path
        active_paths = LearningPath.query.filter_by(user_id=user_id).all()
        current_path = active_paths[0] if active_paths else None
        
        # Get recent milestones
        recent_milestones = Milestone.query.filter_by(user_id=user_id)\
            .order_by(Milestone.achieved_at.desc())\
            .limit(5)\
            .all()
        
        # Get recent lesson reviews
        recent_reviews = LessonReview.query.filter_by(user_id=user_id)\
            .order_by(LessonReview.created_at.desc())\
            .limit(3)\
            .all()
        
        # Calculate completed lessons count
        from app.models import UserActivityLog
        completed_lessons = UserActivityLog.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        # Calculate overall mastery percentage
        mastery_metrics = profile.mastery_metrics or {}
        overall_mastery = mastery_metrics.get('overall', 0)
        
        # Determine next milestone
        next_milestone = None
        if overall_mastery < 25:
            next_milestone = {'type': 'mastery_25', 'target': 25, 'title': '25% Mastery'}
        elif overall_mastery < 50:
            next_milestone = {'type': 'mastery_50', 'target': 50, 'title': '50% Mastery'}
        elif overall_mastery < 75:
            next_milestone = {'type': 'mastery_75', 'target': 75, 'title': '75% Mastery'}
        elif overall_mastery < 100:
            next_milestone = {'type': 'mastery_100', 'target': 100, 'title': 'English Master!'}
        
        return jsonify({
            'success': True,
            'progress_snapshot': {
                'user': {
                    'username': user.username,
                    'current_learning_phase': user.current_learning_phase,
                    'onboarding_completed': user.onboarding_completed
                },
                'mastery': {
                    'overall_percentage': overall_mastery,
                    'skill_breakdown': mastery_metrics,
                    'next_milestone': next_milestone
                },
                'learning_path': {
                    'active': current_path is not None,
                    'title': current_path.title if current_path else None,
                    'difficulty_level': current_path.difficulty_level if current_path else None,
                    'path_id': current_path.id if current_path else None
                } if current_path else None,
                'statistics': {
                    'completed_lessons': completed_lessons,
                    'current_streak': profile.current_streak,
                    'longest_streak': profile.longest_streak,
                    'total_points': profile.points,
                    'proficiency_level': profile.proficiency_level
                },
                'recent_achievements': [m.to_dict() for m in recent_milestones],
                'recent_reviews': [r.to_dict() for r in recent_reviews]
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting progress snapshot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get progress snapshot: {str(e)}'}), 500
