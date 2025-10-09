from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, UserActivityLog, User, Profile, Milestone
from app.services.lesson_review_service import LessonReviewService
from app.services.adaptive_lesson_curator import AdaptiveLessonCurator
from datetime import datetime
import json

lesson_bp = Blueprint('lesson', __name__)

# Initialize services
review_service = LessonReviewService()
curator_service = AdaptiveLessonCurator()


@lesson_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_lesson():
    """
    Mark a lesson/activity as complete and trigger AI review.
    
    Expected JSON:
    {
        "activity_id": int,
        "activity_type": str,
        "score": float,
        "time_spent": int (seconds),
        "completed_data": dict,
        "learning_path_id": int (optional)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        activity_type = data.get('activity_type')
        score = data.get('score', 0)
        time_spent = data.get('time_spent', 0)
        completed_data = data.get('completed_data', {})
        learning_path_id = data.get('learning_path_id')
        
        if not activity_type:
            return jsonify({'error': 'activity_type is required'}), 400
        
        # Create activity log
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            score=score,
            time_spent=time_spent,
            completed=True,
            completed_at=datetime.utcnow(),
            activity_data=completed_data,
            attempts=data.get('attempts', 1)
        )
        
        db.session.add(activity_log)
        db.session.flush()  # Get activity_log.id
        
        # Update user's last activity date and streak
        profile = Profile.query.filter_by(user_id=user_id).first()
        if profile:
            today = datetime.utcnow().date()
            if profile.last_activity_date:
                days_diff = (today - profile.last_activity_date).days
                if days_diff == 1:
                    # Continue streak
                    profile.current_streak += 1
                    if profile.current_streak > profile.longest_streak:
                        profile.longest_streak = profile.current_streak
                elif days_diff > 1:
                    # Streak broken
                    profile.current_streak = 1
            else:
                profile.current_streak = 1
            
            profile.last_activity_date = today
            profile.points += int(score / 10)  # Award points based on score
        
        db.session.commit()
        
        # Generate AI review
        review_result = review_service.generate_lesson_review(
            user_id=user_id,
            activity_log_id=activity_log.id,
            learning_path_id=learning_path_id
        )
        
        if 'error' in review_result:
            return jsonify({
                'success': False,
                'error': review_result['error']
            }), 500
        
        # Check for milestones
        milestones_achieved = _check_and_award_milestones(user_id, score, profile)
        
        # Get next lesson recommendation
        next_lesson = curator_service.curate_next_lesson(
            user_id=user_id,
            learning_path_id=learning_path_id,
            completed_activity_id=activity_log.id
        )
        
        return jsonify({
            'success': True,
            'message': 'Lesson completed successfully!',
            'telugu_message': 'పాఠం విజయవంతంగా పూర్తయింది!',
            'activity_log_id': activity_log.id,
            'review': review_result.get('review'),
            'motivational_message': review_result.get('motivational_message'),
            'telugu_motivational_message': review_result.get('telugu_motivational_message'),
            'next_lesson': next_lesson.get('lesson_plan') if 'lesson_plan' in next_lesson else None,
            'milestones_achieved': milestones_achieved,
            'points_earned': int(score / 10),
            'current_streak': profile.current_streak if profile else 0
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error completing lesson: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to complete lesson: {str(e)}'}), 500


@lesson_bp.route('/review/<int:review_id>', methods=['GET'])
@jwt_required()
def get_lesson_review(review_id):
    """Get a specific lesson review by ID"""
    try:
        user_id = int(get_jwt_identity())
        review = review_service.get_lesson_review(review_id, user_id)
        
        if not review:
            return jsonify({'error': 'Review not found or access denied'}), 404
        
        return jsonify({
            'success': True,
            'review': review
        }), 200
        
    except Exception as e:
        print(f"Error getting lesson review: {str(e)}")
        return jsonify({'error': f'Failed to get lesson review: {str(e)}'}), 500


@lesson_bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_user_reviews():
    """Get recent lesson reviews for the authenticated user"""
    try:
        user_id = int(get_jwt_identity())
        limit = request.args.get('limit', 10, type=int)
        
        reviews = review_service.get_user_reviews(user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'reviews': reviews,
            'count': len(reviews)
        }), 200
        
    except Exception as e:
        print(f"Error getting user reviews: {str(e)}")
        return jsonify({'error': f'Failed to get user reviews: {str(e)}'}), 500


@lesson_bp.route('/next', methods=['GET', 'POST'])
@jwt_required()
def get_next_lesson():
    """
    Get the next recommended lesson for the user.
    Optionally provide learning_path_id in query params or JSON body.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get learning_path_id from query params or JSON body
        learning_path_id = None
        if request.method == 'GET':
            learning_path_id = request.args.get('learning_path_id', type=int)
        else:
            data = request.get_json() or {}
            learning_path_id = data.get('learning_path_id')
        
        # Curate next lesson
        result = curator_service.curate_next_lesson(
            user_id=user_id,
            learning_path_id=learning_path_id
        )
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'lesson_plan': result.get('lesson_plan'),
            'activity': result.get('activity'),
            'performance_context': result.get('performance_context'),
            'message': result.get('message'),
            'telugu_message': result.get('telugu_message')
        }), 200
        
    except Exception as e:
        print(f"Error getting next lesson: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get next lesson: {str(e)}'}), 500


def _check_and_award_milestones(user_id: int, score: float, profile: Profile) -> list:
    """Check and award milestones based on user performance"""
    milestones_achieved = []
    
    try:
        # Check for perfect score milestone
        if score >= 100:
            # Check if already awarded
            existing = Milestone.query.filter_by(
                user_id=user_id,
                milestone_type='perfect_lesson'
            ).first()
            
            if not existing:
                milestone = Milestone(
                    user_id=user_id,
                    milestone_type='perfect_lesson',
                    title='Perfect Score!',
                    description='Achieved a perfect 100% score on a lesson',
                    telugu_title='పరిపూర్ణ స్కోరు!',
                    telugu_description='పాఠంలో పరిపూర్ణ 100% స్కోరు సాధించారు',
                    icon='🌟',
                    color='gold',
                    points_awarded=100
                )
                db.session.add(milestone)
                if profile:
                    profile.points += 100
                milestones_achieved.append(milestone.to_dict())
        
        # Check for streak milestones
        if profile and profile.current_streak == 7:
            existing = Milestone.query.filter_by(
                user_id=user_id,
                milestone_type='week_streak'
            ).first()
            
            if not existing:
                milestone = Milestone(
                    user_id=user_id,
                    milestone_type='week_streak',
                    title='Week Streak!',
                    description='Maintained a 7-day learning streak',
                    telugu_title='వారం స్ట్రీక్!',
                    telugu_description='7 రోజుల నేర్చుకునే స్ట్రీక్ కొనసాగించారు',
                    icon='🔥',
                    color='orange',
                    points_awarded=150
                )
                db.session.add(milestone)
                profile.points += 150
                milestones_achieved.append(milestone.to_dict())
        
        # Check for mastery milestones
        if profile and profile.mastery_metrics:
            overall_mastery = profile.mastery_metrics.get('overall', 0)
            
            mastery_thresholds = [
                (25, 'mastery_25', '25% Mastery', '25% ప్రావీణ్యత', 200),
                (50, 'mastery_50', '50% Mastery', '50% ప్రావీణ్యత', 300),
                (75, 'mastery_75', '75% Mastery', '75% ప్రావీణ్యత', 500),
                (100, 'mastery_100', 'English Master!', 'ఇంగ్లీష్ మాస్టర్!', 1000)
            ]
            
            for threshold, m_type, title, telugu_title, points in mastery_thresholds:
                if overall_mastery >= threshold:
                    existing = Milestone.query.filter_by(
                        user_id=user_id,
                        milestone_type=m_type
                    ).first()
                    
                    if not existing:
                        milestone = Milestone(
                            user_id=user_id,
                            milestone_type=m_type,
                            title=title,
                            description=f'Achieved {threshold}% overall English mastery',
                            telugu_title=telugu_title,
                            telugu_description=f'{threshold}% మొత్తం ఇంగ్లీష్ ప్రావీణ్యత సాధించారు',
                            icon='🏆',
                            color='gold',
                            points_awarded=points
                        )
                        db.session.add(milestone)
                        profile.points += points
                        milestones_achieved.append(milestone.to_dict())
                        break  # Only award the highest reached milestone
        
        if milestones_achieved:
            db.session.commit()
        
    except Exception as e:
        print(f"Error checking milestones: {str(e)}")
    
    return milestones_achieved
