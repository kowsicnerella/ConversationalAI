from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, AssessmentQuestionResponse, ActivityQuestionResponse, 
    UserAnalytics, LearningStreak, AIGeneratedContent, 
    UserLearningTimeline, PerformanceTrend, ProficiencyAssessment,
    Activity, UserActivityLog
)
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, and_, or_
from collections import defaultdict
import traceback

analytics_bp = Blueprint('enhanced_analytics', __name__)

@analytics_bp.route('/performance-trends', methods=['GET'])
@jwt_required()
def get_performance_trends():
    """
    Get performance trends over time for the current user.
    Query parameters:
    - period: daily, weekly, monthly (default: weekly)
    - days: number of days to look back (default: 30)
    - skill_area: optional filter by skill area
    """
    try:
        user_id = get_jwt_identity()
        
        period = request.args.get('period', 'weekly')
        days = int(request.args.get('days', 30))
        skill_area = request.args.get('skill_area')
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get analytics data
        query = UserAnalytics.query.filter(
            UserAnalytics.user_id == user_id,
            UserAnalytics.date_recorded >= start_date,
            UserAnalytics.date_recorded <= end_date
        )
        
        if skill_area:
            query = query.filter(UserAnalytics.skill_area == skill_area)
        
        analytics_data = query.order_by(UserAnalytics.date_recorded).all()
        
        # Group by date and calculate trends
        trends = defaultdict(lambda: {
            'accuracy': [],
            'speed': [],
            'consistency': [],
            'improvement_rate': []
        })
        
        for record in analytics_data:
            date_key = record.date_recorded.isoformat()
            trends[date_key][record.metric_type].append(record.metric_value)
        
        # Calculate averages for each date
        result = []
        for date_key, metrics in trends.items():
            date_data = {'date': date_key}
            for metric, values in metrics.items():
                if values:
                    date_data[metric] = sum(values) / len(values)
                else:
                    date_data[metric] = 0.0
            result.append(date_data)
        
        # Sort by date
        result.sort(key=lambda x: x['date'])
        
        return jsonify({
            'success': True,
            'trends': result,
            'period': period,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get performance trends',
            'details': str(e)
        }), 500

@analytics_bp.route('/learning-streaks', methods=['GET'])
@jwt_required()
def get_learning_streaks():
    """Get current learning streaks for the user."""
    try:
        user_id = get_jwt_identity()
        
        streaks = LearningStreak.query.filter(
            LearningStreak.user_id == user_id,
            LearningStreak.is_active == True
        ).all()
        
        streak_data = []
        for streak in streaks:
            streak_info = {
                'id': streak.id,
                'type': streak.streak_type,
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
                'last_activity_date': streak.last_activity_date.isoformat() if streak.last_activity_date else None,
                'streak_start_date': streak.streak_start_date.isoformat() if streak.streak_start_date else None,
                'activity_type': streak.activity_type,
                'skill_area': streak.skill_area,
                'milestones': streak.milestone_reached
            }
            streak_data.append(streak_info)
        
        return jsonify({
            'success': True,
            'streaks': streak_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get learning streaks',
            'details': str(e)
        }), 500

@analytics_bp.route('/skill-breakdown', methods=['GET'])
@jwt_required()
def get_skill_breakdown():
    """Get comprehensive skill analysis for the user."""
    try:
        user_id = get_jwt_identity()
        
        # Get recent assessment data
        recent_assessments = ProficiencyAssessment.query.filter(
            ProficiencyAssessment.user_id == user_id,
            ProficiencyAssessment.status == 'completed'
        ).order_by(desc(ProficiencyAssessment.completed_at)).limit(5).all()
        
        # Get skill-wise analytics from the last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        skill_analytics = db.session.query(
            UserAnalytics.skill_area,
            func.avg(UserAnalytics.metric_value).label('avg_score'),
            func.count(UserAnalytics.id).label('activity_count')
        ).filter(
            UserAnalytics.user_id == user_id,
            UserAnalytics.metric_type == 'accuracy',
            UserAnalytics.date_recorded >= thirty_days_ago,
            UserAnalytics.skill_area.isnot(None)
        ).group_by(UserAnalytics.skill_area).all()
        
        # Get question-level performance
        question_performance = db.session.query(
            AssessmentQuestionResponse.skill_area,
            func.avg(func.cast(AssessmentQuestionResponse.is_correct, db.Float)).label('accuracy'),
            func.avg(AssessmentQuestionResponse.time_spent_seconds).label('avg_time'),
            func.count(AssessmentQuestionResponse.id).label('question_count')
        ).filter(
            AssessmentQuestionResponse.user_id == user_id
        ).group_by(AssessmentQuestionResponse.skill_area).all()
        
        # Combine data
        skill_breakdown = {}
        
        # From analytics
        for skill, avg_score, count in skill_analytics:
            if skill:
                skill_breakdown[skill] = {
                    'skill_area': skill,
                    'average_score': float(avg_score) if avg_score else 0.0,
                    'activity_count': count,
                    'accuracy': 0.0,
                    'average_time_seconds': 0.0,
                    'question_count': 0
                }
        
        # From question responses
        for skill, accuracy, avg_time, q_count in question_performance:
            if skill:
                if skill not in skill_breakdown:
                    skill_breakdown[skill] = {
                        'skill_area': skill,
                        'average_score': 0.0,
                        'activity_count': 0,
                        'accuracy': 0.0,
                        'average_time_seconds': 0.0,
                        'question_count': 0
                    }
                skill_breakdown[skill]['accuracy'] = float(accuracy) if accuracy else 0.0
                skill_breakdown[skill]['average_time_seconds'] = float(avg_time) if avg_time else 0.0
                skill_breakdown[skill]['question_count'] = q_count
        
        # Get latest skill breakdown from assessment
        latest_skill_data = {}
        if recent_assessments:
            latest_assessment = recent_assessments[0]
            if latest_assessment.skill_breakdown:
                latest_skill_data = latest_assessment.skill_breakdown
        
        return jsonify({
            'success': True,
            'skill_breakdown': list(skill_breakdown.values()),
            'latest_assessment_skills': latest_skill_data,
            'assessment_count': len(recent_assessments)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get skill breakdown',
            'details': str(e)
        }), 500

@analytics_bp.route('/time-spent', methods=['GET'])
@jwt_required()
def get_time_analytics():
    """Get time spent analytics across different activities."""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get time spent from activity logs
        activity_time = db.session.query(
            UserActivityLog.completed_at,
            UserActivityLog.time_spent_minutes,
            Activity.activity_type
        ).join(Activity).filter(
            UserActivityLog.user_id == user_id,
            func.date(UserActivityLog.completed_at) >= start_date,
            func.date(UserActivityLog.completed_at) <= end_date,
            UserActivityLog.time_spent_minutes.isnot(None)
        ).all()
        
        # Group by activity type and date
        time_by_type = defaultdict(int)
        time_by_date = defaultdict(int)
        daily_breakdown = defaultdict(lambda: defaultdict(int))
        
        total_time = 0
        for log_date, time_spent, activity_type in activity_time:
            if time_spent:
                date_key = log_date.date().isoformat()
                time_by_type[activity_type] += time_spent
                time_by_date[date_key] += time_spent
                daily_breakdown[date_key][activity_type] += time_spent
                total_time += time_spent
        
        # Calculate averages
        total_days = (end_date - start_date).days + 1
        average_daily_time = total_time / total_days if total_days > 0 else 0
        
        return jsonify({
            'success': True,
            'total_time_minutes': total_time,
            'average_daily_minutes': round(average_daily_time, 2),
            'time_by_activity_type': dict(time_by_type),
            'time_by_date': dict(time_by_date),
            'daily_breakdown': {
                date: dict(activities) for date, activities in daily_breakdown.items()
            },
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get time analytics',
            'details': str(e)
        }), 500

@analytics_bp.route('/difficulty-progression', methods=['GET'])
@jwt_required()
def get_difficulty_progression():
    """Analyze how user handles increasing difficulty levels."""
    try:
        user_id = get_jwt_identity()
        
        # Get question responses grouped by difficulty
        difficulty_stats = db.session.query(
            AssessmentQuestionResponse.difficulty_level,
            func.avg(func.cast(AssessmentQuestionResponse.is_correct, db.Float)).label('accuracy'),
            func.avg(AssessmentQuestionResponse.time_spent_seconds).label('avg_time'),
            func.count(AssessmentQuestionResponse.id).label('question_count')
        ).filter(
            AssessmentQuestionResponse.user_id == user_id,
            AssessmentQuestionResponse.difficulty_level.isnot(None)
        ).group_by(AssessmentQuestionResponse.difficulty_level).all()
        
        # Also get from activity responses
        activity_difficulty_stats = db.session.query(
            ActivityQuestionResponse.difficulty_level,
            func.avg(func.cast(ActivityQuestionResponse.is_correct, db.Float)).label('accuracy'),
            func.avg(ActivityQuestionResponse.time_spent_seconds).label('avg_time'),
            func.count(ActivityQuestionResponse.id).label('question_count')
        ).filter(
            ActivityQuestionResponse.user_id == user_id,
            ActivityQuestionResponse.difficulty_level.isnot(None)
        ).group_by(ActivityQuestionResponse.difficulty_level).all()
        
        # Combine data
        combined_stats = {}
        
        for difficulty, accuracy, avg_time, count in difficulty_stats:
            combined_stats[difficulty] = {
                'difficulty_level': difficulty,
                'accuracy': float(accuracy) if accuracy else 0.0,
                'average_time_seconds': float(avg_time) if avg_time else 0.0,
                'question_count': count,
                'source': 'assessments'
            }
        
        for difficulty, accuracy, avg_time, count in activity_difficulty_stats:
            if difficulty in combined_stats:
                # Average the values
                total_questions = combined_stats[difficulty]['question_count'] + count
                combined_stats[difficulty]['accuracy'] = (
                    (combined_stats[difficulty]['accuracy'] * combined_stats[difficulty]['question_count'] +
                     float(accuracy if accuracy else 0.0) * count) / total_questions
                )
                combined_stats[difficulty]['average_time_seconds'] = (
                    (combined_stats[difficulty]['average_time_seconds'] * combined_stats[difficulty]['question_count'] +
                     float(avg_time if avg_time else 0.0) * count) / total_questions
                )
                combined_stats[difficulty]['question_count'] = total_questions
                combined_stats[difficulty]['source'] = 'both'
            else:
                combined_stats[difficulty] = {
                    'difficulty_level': difficulty,
                    'accuracy': float(accuracy) if accuracy else 0.0,
                    'average_time_seconds': float(avg_time) if avg_time else 0.0,
                    'question_count': count,
                    'source': 'activities'
                }
        
        # Order by difficulty
        difficulty_order = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        progression = sorted(
            combined_stats.values(),
            key=lambda x: difficulty_order.get(x['difficulty_level'], 4)
        )
        
        return jsonify({
            'success': True,
            'difficulty_progression': progression
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get difficulty progression',
            'details': str(e)
        }), 500

@analytics_bp.route('/learning-timeline', methods=['GET'])
@jwt_required()
def get_learning_timeline():
    """Get comprehensive learning timeline for the user."""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        event_type = request.args.get('event_type')  # Optional filter
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        query = UserLearningTimeline.query.filter(
            UserLearningTimeline.user_id == user_id,
            UserLearningTimeline.created_at >= start_date,
            UserLearningTimeline.created_at <= end_date
        )
        
        if event_type:
            query = query.filter(UserLearningTimeline.event_type == event_type)
        
        timeline_events = query.order_by(desc(UserLearningTimeline.created_at)).limit(100).all()
        
        events = []
        for event in timeline_events:
            event_data = {
                'id': event.id,
                'event_type': event.event_type,
                'event_subtype': event.event_subtype,
                'event_data': event.event_data,
                'related_id': event.related_id,
                'related_type': event.related_type,
                'proficiency_change': event.proficiency_change,
                'points_earned': event.points_earned,
                'skill_areas_affected': event.skill_areas_affected,
                'difficulty_level': event.difficulty_level,
                'performance_score': event.performance_score,
                'time_spent_minutes': event.time_spent_minutes,
                'milestone_achieved': event.milestone_achieved,
                'created_at': event.created_at.isoformat()
            }
            events.append(event_data)
        
        return jsonify({
            'success': True,
            'timeline': events,
            'total_events': len(events),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get learning timeline',
            'details': str(e)
        }), 500

@analytics_bp.route('/comprehensive-report', methods=['GET'])
@jwt_required()
def get_comprehensive_report():
    """Generate a comprehensive learning report for the user."""
    try:
        user_id = get_jwt_identity()
        
        # Get user info
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range
        days = int(request.args.get('days', 30))
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Overall statistics
        total_activities = UserActivityLog.query.filter(
            UserActivityLog.user_id == user_id,
            func.date(UserActivityLog.completed_at) >= start_date
        ).count()
        
        total_assessments = ProficiencyAssessment.query.filter(
            ProficiencyAssessment.user_id == user_id,
            func.date(ProficiencyAssessment.completed_at) >= start_date,
            ProficiencyAssessment.status == 'completed'
        ).count()
        
        # Average scores
        avg_activity_score = db.session.query(
            func.avg(UserActivityLog.score * 100.0 / UserActivityLog.max_score)
        ).filter(
            UserActivityLog.user_id == user_id,
            func.date(UserActivityLog.completed_at) >= start_date,
            UserActivityLog.score.isnot(None),
            UserActivityLog.max_score > 0
        ).scalar() or 0.0
        
        avg_assessment_score = db.session.query(
            func.avg(ProficiencyAssessment.score * 100.0 / ProficiencyAssessment.max_score)
        ).filter(
            ProficiencyAssessment.user_id == user_id,
            func.date(ProficiencyAssessment.completed_at) >= start_date,
            ProficiencyAssessment.status == 'completed',
            ProficiencyAssessment.score.isnot(None),
            ProficiencyAssessment.max_score > 0
        ).scalar() or 0.0
        
        # Time spent
        total_time = db.session.query(
            func.sum(UserActivityLog.time_spent_minutes)
        ).filter(
            UserActivityLog.user_id == user_id,
            func.date(UserActivityLog.completed_at) >= start_date
        ).scalar() or 0
        
        # Current streaks
        active_streaks = LearningStreak.query.filter(
            LearningStreak.user_id == user_id,
            LearningStreak.is_active == True
        ).count()
        
        # Recent improvements
        recent_timeline = UserLearningTimeline.query.filter(
            UserLearningTimeline.user_id == user_id,
            UserLearningTimeline.created_at >= datetime.now() - timedelta(days=7)
        ).order_by(desc(UserLearningTimeline.created_at)).limit(10).all()
        
        report = {
            'user_info': {
                'username': user.username,
                'report_period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            },
            'overall_statistics': {
                'total_activities_completed': total_activities,
                'total_assessments_taken': total_assessments,
                'average_activity_score': round(avg_activity_score, 2),
                'average_assessment_score': round(avg_assessment_score, 2),
                'total_time_spent_minutes': total_time,
                'average_daily_minutes': round(total_time / days, 2) if days > 0 else 0,
                'active_streaks': active_streaks
            },
            'recent_achievements': [
                {
                    'event_type': event.event_type,
                    'event_subtype': event.event_subtype,
                    'milestone_achieved': event.milestone_achieved,
                    'points_earned': event.points_earned,
                    'created_at': event.created_at.isoformat()
                }
                for event in recent_timeline
                if event.milestone_achieved or event.points_earned > 0
            ]
        }
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate comprehensive report',
            'details': str(e)
        }), 500