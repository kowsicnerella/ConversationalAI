"""
Analytics routes for performance tracking and insights.
Provides endpoints for charts, statistics, and learning analytics.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import db
from app.models.activity import UserActivityLog, Activity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from collections import defaultdict

analytics_bp = Blueprint('analytics_v2', __name__)  # NEW unique name to avoid conflicts


@analytics_bp.route('/performance-trends', methods=['GET'])
@jwt_required()
def get_performance_trends():
    """
    Get performance trends over time for charts.
    
    Query Parameters:
        time_range (str): '7days', '30days', '90days', 'all' (default: 30days)
    
    Returns:
        JSON: {
            dates: ['2025-10-01', '2025-10-02', ...],
            scores: [75, 80, 85, ...],
            activities: [3, 5, 4, ...],
            time_spent: [30, 45, 35, ...]
        }
    """
    try:
        current_user_id = get_jwt_identity()
        time_range = request.args.get('time_range', '30days')
        
        # Calculate date range
        end_date = datetime.utcnow().date()
        if time_range == '7days':
            start_date = end_date - timedelta(days=7)
        elif time_range == '90days':
            start_date = end_date - timedelta(days=90)
        elif time_range == 'all':
            start_date = datetime(2000, 1, 1).date()
        else:  # 30days default
            start_date = end_date - timedelta(days=30)
        
        # Query activity logs in date range
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= start_date,
                UserActivityLog.is_completed == True
            )
        ).order_by(UserActivityLog.completed_at).all()
        
        # Group by date
        daily_data = defaultdict(lambda: {
            'count': 0,
            'scores': [],
            'time': 0
        })
        
        for log in logs:
            date_key = log.completed_at.date().isoformat()
            daily_data[date_key]['count'] += 1
            if log.accuracy_score is not None:
                daily_data[date_key]['scores'].append(log.accuracy_score)
            if log.time_spent_minutes:
                daily_data[date_key]['time'] += log.time_spent_minutes
        
        # Generate complete date range
        dates = []
        scores = []
        activities = []
        time_spent = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            dates.append(date_str)
            
            data = daily_data.get(date_str, {'count': 0, 'scores': [], 'time': 0})
            activities.append(data['count'])
            
            # Average score for the day
            if data['scores']:
                avg_score = sum(data['scores']) / len(data['scores'])
                scores.append(round(avg_score, 2))
            else:
                scores.append(0)
            
            time_spent.append(data['time'])
            
            current_date += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'data': {
                'dates': dates,
                'scores': scores,
                'activities': activities,
                'time_spent': time_spent,
                'time_range': time_range
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_performance_trends: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/skill-breakdown', methods=['GET'])
@jwt_required()
def get_skill_breakdown():
    """
    Get current skill levels across all dimensions.
    
    Returns:
        JSON: {
            listening: 75,
            speaking: 60,
            reading: 80,
            writing: 70,
            vocabulary: 85,
            grammar: 65
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get recent activity logs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= thirty_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Group by skill area
        skill_scores = defaultdict(list)
        
        for log in logs:
            if log.skill_area and log.accuracy_score is not None:
                skill_scores[log.skill_area].append(log.accuracy_score)
        
        # Calculate averages
        skill_breakdown = {}
        default_skills = ['listening', 'speaking', 'reading', 'writing', 'vocabulary', 'grammar']
        
        for skill in default_skills:
            if skill in skill_scores and skill_scores[skill]:
                avg = sum(skill_scores[skill]) / len(skill_scores[skill])
                skill_breakdown[skill] = round(avg, 1)
            else:
                skill_breakdown[skill] = 0
        
        return jsonify({
            'success': True,
            'data': skill_breakdown
        }), 200
        
    except Exception as e:
        print(f"Error in get_skill_breakdown: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/activity-summary', methods=['GET'])
@jwt_required()
def get_activity_summary():
    """
    Get activity type distribution and completion stats.
    
    Returns:
        JSON: {
            by_type: {quiz: 20, flashcard: 15, reading: 10, ...},
            total_completed: 45,
            completion_rate: 85.5,
            favorite_type: 'quiz'
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get all completed activities
        completed_logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Get activity types
        activity_ids = [log.activity_id for log in completed_logs]
        activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()
        
        # Create activity type map
        activity_type_map = {a.id: a.activity_type for a in activities}
        
        # Count by type
        type_counts = defaultdict(int)
        for log in completed_logs:
            activity_type = activity_type_map.get(log.activity_id, 'unknown')
            type_counts[activity_type] += 1
        
        # Get total activities (including incomplete)
        total_activities = UserActivityLog.query.filter(
            UserActivityLog.user_id == current_user_id
        ).count()
        
        # Calculate completion rate
        total_completed = len(completed_logs)
        completion_rate = (total_completed / total_activities * 100) if total_activities > 0 else 0
        
        # Find favorite type
        favorite_type = max(type_counts, key=type_counts.get) if type_counts else None
        
        return jsonify({
            'success': True,
            'data': {
                'by_type': dict(type_counts),
                'total_completed': total_completed,
                'total_activities': total_activities,
                'completion_rate': round(completion_rate, 1),
                'favorite_type': favorite_type
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_activity_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/time-analytics', methods=['GET'])
@jwt_required()
def get_time_analytics():
    """
    Get time spent analysis by day/week.
    
    Returns:
        JSON: {
            daily_average: 30,
            weekly_total: 210,
            most_active_day: 'Monday',
            total_hours: 50.5
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get all completed activities
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Calculate total time
        total_minutes = sum(log.time_spent_minutes for log in logs if log.time_spent_minutes)
        total_hours = round(total_minutes / 60, 1)
        
        # Calculate by day of week
        day_minutes = defaultdict(int)
        for log in logs:
            if log.completed_at and log.time_spent_minutes:
                day_name = log.completed_at.strftime('%A')
                day_minutes[day_name] += log.time_spent_minutes
        
        # Find most active day
        most_active_day = max(day_minutes, key=day_minutes.get) if day_minutes else None
        
        # Calculate last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = [log for log in logs if log.completed_at >= seven_days_ago]
        weekly_total = sum(log.time_spent_minutes for log in recent_logs if log.time_spent_minutes)
        
        # Calculate last 30 days for daily average
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        month_logs = [log for log in logs if log.completed_at >= thirty_days_ago]
        month_minutes = sum(log.time_spent_minutes for log in month_logs if log.time_spent_minutes)
        daily_average = round(month_minutes / 30, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'daily_average': daily_average,
                'weekly_total': weekly_total,
                'most_active_day': most_active_day,
                'total_hours': total_hours,
                'by_day_of_week': dict(day_minutes)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_time_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/learning-velocity', methods=['GET'])
@jwt_required()
def get_learning_velocity():
    """
    Get learning pace and improvement rate.
    
    Returns:
        JSON: {
            activities_per_week: 15,
            improvement_rate: 12.5,
            consistency_score: 8.5,
            learning_pace: 'moderate'
        }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get activities from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= seven_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        activities_per_week = len(recent_logs)
        
        # Calculate improvement rate (compare first half vs second half of month)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        fifteen_days_ago = datetime.utcnow() - timedelta(days=15)
        
        first_half = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= thirty_days_ago,
                UserActivityLog.completed_at < fifteen_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        second_half = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= fifteen_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Calculate average scores
        first_avg = sum(log.accuracy_score for log in first_half if log.accuracy_score) / len(first_half) if first_half else 0
        second_avg = sum(log.accuracy_score for log in second_half if log.accuracy_score) / len(second_half) if second_half else 0
        
        improvement_rate = round((second_avg - first_avg), 1) if first_avg > 0 else 0
        
        # Calculate consistency (days studied in last week)
        study_dates = set()
        for log in recent_logs:
            if log.completed_at:
                study_dates.add(log.completed_at.date())
        
        consistency_score = round((len(study_dates) / 7) * 10, 1)
        
        # Determine learning pace
        if activities_per_week >= 20:
            learning_pace = 'fast'
        elif activities_per_week >= 10:
            learning_pace = 'moderate'
        elif activities_per_week >= 5:
            learning_pace = 'steady'
        else:
            learning_pace = 'slow'
        
        return jsonify({
            'success': True,
            'data': {
                'activities_per_week': activities_per_week,
                'improvement_rate': improvement_rate,
                'consistency_score': consistency_score,
                'learning_pace': learning_pace,
                'days_studied_this_week': len(study_dates)
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_learning_velocity: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analytics_bp.route('/weak-areas', methods=['GET'])
@jwt_required()
def get_weak_areas():
    """
    Get identified weak areas needing focus.
    
    Returns:
        JSON: [
            {skill: 'grammar', score: 55, priority: 'high', activities_count: 5},
            {skill: 'speaking', score: 62, priority: 'medium', activities_count: 3}
        ]
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get recent activity logs (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == current_user_id,
                UserActivityLog.completed_at >= thirty_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Group by skill area
        skill_data = defaultdict(lambda: {'scores': [], 'count': 0})
        
        for log in logs:
            if log.skill_area and log.accuracy_score is not None:
                skill_data[log.skill_area]['scores'].append(log.accuracy_score)
                skill_data[log.skill_area]['count'] += 1
        
        # Identify weak areas (score < 70)
        weak_areas = []
        for skill, data in skill_data.items():
            if data['scores']:
                avg_score = sum(data['scores']) / len(data['scores'])
                if avg_score < 70:
                    # Determine priority
                    if avg_score < 50:
                        priority = 'high'
                    elif avg_score < 60:
                        priority = 'medium'
                    else:
                        priority = 'low'
                    
                    weak_areas.append({
                        'skill': skill,
                        'score': round(avg_score, 1),
                        'priority': priority,
                        'activities_count': data['count']
                    })
        
        # Sort by score (lowest first)
        weak_areas.sort(key=lambda x: x['score'])
        
        return jsonify({
            'success': True,
            'data': weak_areas
        }), 200
        
    except Exception as e:
        print(f"Error in get_weak_areas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
