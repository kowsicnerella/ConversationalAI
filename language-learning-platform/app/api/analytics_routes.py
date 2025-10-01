from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, LearningSession, UserActivityLog, VocabularyWord, UserGoal, Activity
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, or_
from collections import defaultdict
import json

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard-summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """
    Get comprehensive dashboard analytics summary.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Date ranges
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Learning time analytics
        total_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id).scalar() or 0
        
        weekly_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id,
                   LearningSession.start_time >= week_ago).scalar() or 0
        
        monthly_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id,
                   LearningSession.start_time >= month_ago).scalar() or 0
        
        # Activity completion analytics
        total_activities = UserActivityLog.query.filter_by(user_id=user_id).count()
        
        weekly_activities = UserActivityLog.query.filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.completed_at >= week_ago
        ).count()
        
        # Vocabulary analytics
        total_vocabulary = VocabularyWord.query.filter_by(user_id=user_id).count()
        mastered_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.mastery_level >= 0.8
        ).count()
        
        weekly_new_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.discovered_at >= week_ago
        ).count()
        
        # Performance analytics
        avg_score = db.session.query(func.avg(UserActivityLog.score))\
            .filter(UserActivityLog.user_id == user_id).scalar() or 0
        
        recent_avg_score = db.session.query(func.avg(UserActivityLog.score))\
            .filter(UserActivityLog.user_id == user_id,
                   UserActivityLog.completed_at >= week_ago).scalar() or 0
        
        # Streak and goal analytics
        user = User.query.get(user_id)
        current_streak = user.profile.current_streak if user.profile else 0
        longest_streak = user.profile.longest_streak if user.profile else 0
        
        # Current goal progress
        current_goal = UserGoal.query.filter_by(user_id=user_id, is_active=True).first()
        today_time = db.session.query(func.sum(LearningSession.duration_minutes))\
            .filter(LearningSession.user_id == user_id,
                   func.date(LearningSession.start_time) == today).scalar() or 0
        
        goal_progress = 0
        if current_goal and current_goal.daily_time_goal_minutes > 0:
            goal_progress = min(100, (today_time / current_goal.daily_time_goal_minutes) * 100)
        
        summary = {
            'learning_time': {
                'total_minutes': total_time,
                'weekly_minutes': weekly_time,
                'monthly_minutes': monthly_time,
                'daily_average': round(weekly_time / 7, 1),
                'monthly_average': round(monthly_time / 30, 1)
            },
            'activities': {
                'total_completed': total_activities,
                'weekly_completed': weekly_activities,
                'average_score': round(avg_score, 1),
                'recent_average_score': round(recent_avg_score, 1),
                'improvement': round(recent_avg_score - avg_score, 1) if avg_score > 0 else 0
            },
            'vocabulary': {
                'total_words': total_vocabulary,
                'mastered_words': mastered_words,
                'weekly_new_words': weekly_new_words,
                'mastery_rate': round((mastered_words / total_vocabulary * 100), 1) if total_vocabulary > 0 else 0
            },
            'streaks_and_goals': {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'today_goal_progress': round(goal_progress, 1),
                'daily_goal_minutes': current_goal.daily_time_goal_minutes if current_goal else 0
            }
        }
        
        return jsonify({
            'message': 'Dashboard summary retrieved successfully!',
            'telugu_message': 'డాష్‌బోర్డ్ సారాంశం విజయవంతంగా తీసుకోబడింది!',
            'summary': summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard summary: {str(e)}")
        return jsonify({
            'error': 'Failed to get dashboard summary',
            'telugu_message': 'డాష్‌బోర్డ్ సారాంశం పొందడంలో విఫలం'
        }), 500

@analytics_bp.route('/learning-trends', methods=['GET'])
@jwt_required()
def get_learning_trends():
    """
    Get learning trends over time with detailed analytics.
    """
    try:
        user_id = int(get_jwt_identity())
        days = request.args.get('days', 30, type=int)
        
        # Validate days parameter
        if days not in [7, 14, 30, 90]:
            days = 30
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Daily learning time trends
        daily_sessions = db.session.query(
            func.date(LearningSession.start_time).label('date'),
            func.sum(LearningSession.duration_minutes).label('total_time'),
            func.count(LearningSession.id).label('session_count')
        ).filter(
            LearningSession.user_id == user_id,
            func.date(LearningSession.start_time) >= start_date
        ).group_by(func.date(LearningSession.start_time)).all()
        
        # Daily activity completion trends
        daily_activities = db.session.query(
            func.date(UserActivityLog.completed_at).label('date'),
            func.count(UserActivityLog.id).label('activities_completed'),
            func.avg(UserActivityLog.score).label('avg_score')
        ).filter(
            UserActivityLog.user_id == user_id,
            func.date(UserActivityLog.completed_at) >= start_date
        ).group_by(func.date(UserActivityLog.completed_at)).all()
        
        # Daily vocabulary learning trends
        daily_vocabulary = db.session.query(
            func.date(VocabularyWord.discovered_at).label('date'),
            func.count(VocabularyWord.id).label('new_words')
        ).filter(
            VocabularyWord.user_id == user_id,
            func.date(VocabularyWord.discovered_at) >= start_date
        ).group_by(func.date(VocabularyWord.discovered_at)).all()
        
        # Create daily data structure
        daily_data = {}
        current_date = start_date
        while current_date <= end_date:
            daily_data[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'learning_time_minutes': 0,
                'session_count': 0,
                'activities_completed': 0,
                'average_score': 0,
                'new_vocabulary': 0
            }
            current_date += timedelta(days=1)
        
        # Populate session data
        for session in daily_sessions:
            date_key = session.date.isoformat()
            if date_key in daily_data:
                daily_data[date_key]['learning_time_minutes'] = session.total_time or 0
                daily_data[date_key]['session_count'] = session.session_count or 0
        
        # Populate activity data
        for activity in daily_activities:
            date_key = activity.date.isoformat()
            if date_key in daily_data:
                daily_data[date_key]['activities_completed'] = activity.activities_completed or 0
                daily_data[date_key]['average_score'] = round(activity.avg_score or 0, 1)
        
        # Populate vocabulary data
        for vocab in daily_vocabulary:
            date_key = vocab.date.isoformat()
            if date_key in daily_data:
                daily_data[date_key]['new_vocabulary'] = vocab.new_words or 0
        
        # Calculate trends and insights
        daily_values = list(daily_data.values())
        total_time = sum(day['learning_time_minutes'] for day in daily_values)
        total_activities = sum(day['activities_completed'] for day in daily_values)
        total_vocabulary = sum(day['new_vocabulary'] for day in daily_values)
        
        # Weekly comparison (last 7 days vs previous 7 days)
        if days >= 14:
            last_week = daily_values[-7:]
            prev_week = daily_values[-14:-7] if days >= 14 else []
            
            last_week_time = sum(day['learning_time_minutes'] for day in last_week)
            prev_week_time = sum(day['learning_time_minutes'] for day in prev_week) if prev_week else 0
            
            time_trend = 'increasing' if last_week_time > prev_week_time else 'decreasing' if last_week_time < prev_week_time else 'stable'
        else:
            time_trend = 'stable'
        
        insights = {
            'total_learning_time': total_time,
            'total_activities': total_activities,
            'total_new_vocabulary': total_vocabulary,
            'daily_average_time': round(total_time / days, 1),
            'most_productive_day': max(daily_values, key=lambda x: x['learning_time_minutes'])['date'] if daily_values else None,
            'consistency_score': len([day for day in daily_values if day['learning_time_minutes'] > 0]) / days * 100,
            'learning_trend': time_trend
        }
        
        return jsonify({
            'message': 'Learning trends retrieved successfully!',
            'telugu_message': 'అభ్యాస ధోరణులు విజయవంతంగా తీసుకోబడ్డాయి!',
            'trends': {
                'period': f'{days} days',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'daily_data': daily_values,
                'insights': insights
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting learning trends: {str(e)}")
        return jsonify({
            'error': 'Failed to get learning trends',
            'telugu_message': 'అభ్యాస ధోరణులు పొందడంలో విఫలం'
        }), 500

@analytics_bp.route('/performance-analysis', methods=['GET'])
@jwt_required()
def get_performance_analysis():
    """
    Get detailed performance analysis by activity type and difficulty.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Performance by activity type
        activity_performance = db.session.query(
            Activity.activity_type,
            func.count(UserActivityLog.id).label('total_attempts'),
            func.avg(UserActivityLog.score).label('avg_score'),
            func.max(UserActivityLog.score).label('best_score'),
            func.sum(UserActivityLog.time_spent_minutes).label('total_time')
        ).join(Activity, UserActivityLog.activity_id == Activity.id).filter(
            UserActivityLog.user_id == user_id
        ).group_by(Activity.activity_type).all()
        
        # Performance by difficulty level
        difficulty_performance = db.session.query(
            Activity.difficulty_level,
            func.count(UserActivityLog.id).label('total_attempts'),
            func.avg(UserActivityLog.score).label('avg_score'),
            func.sum(UserActivityLog.time_spent_minutes).label('total_time')
        ).join(Activity, UserActivityLog.activity_id == Activity.id).filter(
            UserActivityLog.user_id == user_id
        ).group_by(Activity.difficulty_level).all()
        
        # Recent performance trend (last 20 activities)
        recent_activities = UserActivityLog.query.filter_by(user_id=user_id)\
            .order_by(UserActivityLog.completed_at.desc()).limit(20).all()
        
        # Vocabulary mastery breakdown
        vocab_mastery = db.session.query(
            VocabularyWord.mastery_level,
            func.count(VocabularyWord.id).label('word_count')
        ).filter(
            VocabularyWord.user_id == user_id
        ).group_by(VocabularyWord.mastery_level).all()
        
        # Strengths and improvement areas
        activity_scores = {perf.activity_type: perf.avg_score for perf in activity_performance}
        strengths = [activity for activity, score in activity_scores.items() if score >= 80]
        improvement_areas = [activity for activity, score in activity_scores.items() if score < 70]
        
        performance_data = {
            'by_activity_type': [
                {
                    'activity_type': perf.activity_type,
                    'total_attempts': perf.total_attempts,
                    'average_score': round(perf.avg_score, 1),
                    'best_score': perf.best_score,
                    'total_time_minutes': perf.total_time or 0,
                    'performance_level': 'excellent' if perf.avg_score >= 80 else 'good' if perf.avg_score >= 70 else 'needs_improvement'
                } for perf in activity_performance
            ],
            'by_difficulty': [
                {
                    'difficulty_level': perf.difficulty_level,
                    'total_attempts': perf.total_attempts,
                    'average_score': round(perf.avg_score, 1),
                    'total_time_minutes': perf.total_time or 0
                } for perf in difficulty_performance
            ],
            'recent_trend': [
                {
                    'activity_type': activity.activity_type,
                    'score': activity.score,
                    'completed_at': activity.completed_at.isoformat(),
                    'time_spent': activity.time_spent_minutes
                } for activity in recent_activities
            ],
            'vocabulary_mastery': [
                {
                    'mastery_level': mastery.mastery_level,
                    'word_count': mastery.word_count
                } for mastery in vocab_mastery
            ],
            'analysis': {
                'strengths': strengths,
                'improvement_areas': improvement_areas,
                'overall_score': round(sum(perf.avg_score for perf in activity_performance) / len(activity_performance), 1) if activity_performance else 0,
                'most_practiced_activity': max(activity_performance, key=lambda x: x.total_attempts).activity_type if activity_performance else None,
                'recommendations': []
            }
        }
        
        # Generate recommendations
        recommendations = []
        if improvement_areas:
            recommendations.append(f"Focus more practice on: {', '.join(improvement_areas)}")
        if strengths:
            recommendations.append(f"Great job with: {', '.join(strengths)}! Keep it up!")
        
        performance_data['analysis']['recommendations'] = recommendations
        
        return jsonify({
            'message': 'Performance analysis retrieved successfully!',
            'telugu_message': 'పనితీరు విశ్లేషణ విజయవంతంగా తీసుకోబడింది!',
            'performance': performance_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance analysis: {str(e)}")
        return jsonify({
            'error': 'Failed to get performance analysis',
            'telugu_message': 'పనితీరు విశ్లేషణ పొందడంలో విఫలం'
        }), 500

@analytics_bp.route('/vocabulary-analytics', methods=['GET'])
@jwt_required()
def get_vocabulary_analytics():
    """
    Get detailed vocabulary learning analytics.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Overall vocabulary stats
        total_words = VocabularyWord.query.filter_by(user_id=user_id).count()
        mastered_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id, 
            VocabularyWord.mastery_level >= 0.8
        ).count()
        learning_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.mastery_level >= 0.3,
            VocabularyWord.mastery_level < 0.8
        ).count()
        new_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.mastery_level < 0.3
        ).count()
        
        # Words by source/activity type
        words_by_source = db.session.query(
            VocabularyWord.source_activity_type,
            func.count(VocabularyWord.id).label('word_count')
        ).filter(
            VocabularyWord.user_id == user_id
        ).group_by(VocabularyWord.source_activity_type).all()
        
        # Recent vocabulary (last 30 days)
        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.discovered_at >= month_ago
        ).order_by(VocabularyWord.discovered_at.desc()).limit(50).all()
        
        # Practice frequency analysis
        words_needing_practice = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.mastery_level < 0.5,
            or_(
                VocabularyWord.last_practiced.is_(None),
                VocabularyWord.last_practiced < datetime.utcnow() - timedelta(days=7)
            )
        ).limit(20).all()
        
        # Mastery progression over time
        daily_progress = db.session.query(
            func.date(VocabularyWord.discovered_at).label('date'),
            func.count(VocabularyWord.id).label('words_discovered')
        ).filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.discovered_at >= month_ago
        ).group_by(func.date(VocabularyWord.discovered_at)).all()
        
        # Top performing words (most practiced)
        top_practiced_words = VocabularyWord.query.filter_by(user_id=user_id)\
            .filter(VocabularyWord.times_practiced > 0)\
            .order_by(VocabularyWord.times_practiced.desc()).limit(10).all()
        
        vocabulary_analytics = {
            'overview': {
                'total_words': total_words,
                'mastered_words': mastered_words,
                'learning_words': learning_words,
                'new_words': new_words,
                'mastery_rate': round((mastered_words / total_words * 100), 1) if total_words > 0 else 0
            },
            'by_source': [
                {
                    'source': source.source_activity_type,
                    'word_count': source.word_count
                } for source in words_by_source
            ],
            'recent_discoveries': [
                {
                    'english_word': word.english_word,
                    'telugu_translation': word.telugu_translation,
                    'context_sentence': word.context_sentence,
                    'discovered_at': word.discovered_at.isoformat(),
                    'mastery_level': word.mastery_level,
                    'times_practiced': word.times_practiced
                } for word in recent_words[:10]
            ],
            'practice_recommendations': [
                {
                    'english_word': word.english_word,
                    'telugu_translation': word.telugu_translation,
                    'mastery_level': word.mastery_level,
                    'times_practiced': word.times_practiced,
                    'last_practiced': word.last_practiced.isoformat() if word.last_practiced else None,
                    'priority': 'high' if word.times_practiced == 0 else 'medium'
                } for word in words_needing_practice
            ],
            'learning_progress': [
                {
                    'date': progress.date.isoformat(),
                    'words_discovered': progress.words_discovered
                } for progress in daily_progress
            ],
            'top_practiced_words': [
                {
                    'english_word': word.english_word,
                    'telugu_translation': word.telugu_translation,
                    'times_practiced': word.times_practiced,
                    'success_rate': round((word.times_correct / word.times_practiced * 100), 1) if word.times_practiced > 0 else 0,
                    'mastery_level': word.mastery_level
                } for word in top_practiced_words
            ]
        }
        
        return jsonify({
            'message': 'Vocabulary analytics retrieved successfully!',
            'telugu_message': 'పదజాలం విశ్లేషణ విజయవంతంగా తీసుకోబడింది!',
            'vocabulary_analytics': vocabulary_analytics
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting vocabulary analytics: {str(e)}")
        return jsonify({
            'error': 'Failed to get vocabulary analytics',
            'telugu_message': 'పదజాలం విశ్లేషణ పొందడంలో విఫలం'
        }), 500

@analytics_bp.route('/export/progress-report', methods=['GET'])
@jwt_required()
def export_progress_report():
    """
    Generate a comprehensive progress report for export.
    """
    try:
        user_id = int(get_jwt_identity())
        report_type = request.args.get('type', 'summary')  # 'summary', 'detailed', 'vocabulary'
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'User not found',
                'telugu_message': 'వినియోగదారు కనుగొనబడలేదు'
            }), 404
        
        # Generate report based on type
        if report_type == 'summary':
            # Basic summary report
            total_time = db.session.query(func.sum(LearningSession.duration_minutes))\
                .filter(LearningSession.user_id == user_id).scalar() or 0
            
            total_activities = UserActivityLog.query.filter_by(user_id=user_id).count()
            avg_score = db.session.query(func.avg(UserActivityLog.score))\
                .filter(UserActivityLog.user_id == user_id).scalar() or 0
            
            total_vocabulary = VocabularyWord.query.filter_by(user_id=user_id).count()
            
            report = {
                'report_type': 'Learning Progress Summary',
                'user_info': {
                    'username': user.username,
                    'proficiency_level': user.profile.proficiency_level if user.profile else 'beginner',
                    'report_generated': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_learning_time_hours': round(total_time / 60, 2),
                    'total_activities_completed': total_activities,
                    'average_score': round(avg_score, 1),
                    'vocabulary_words_learned': total_vocabulary,
                    'current_streak': user.profile.current_streak if user.profile else 0
                }
            }
        
        elif report_type == 'detailed':
            # Detailed analytics report
            # This would include all the analytics we've calculated above
            report = {
                'report_type': 'Detailed Learning Analytics',
                'generated_at': datetime.utcnow().isoformat(),
                'note': 'This is a comprehensive report. In a real implementation, this would include all detailed analytics.'
            }
        
        else:
            # Vocabulary-focused report
            vocab_words = VocabularyWord.query.filter_by(user_id=user_id)\
                .order_by(VocabularyWord.discovered_at.desc()).all()
            
            report = {
                'report_type': 'Vocabulary Learning Report',
                'vocabulary_summary': {
                    'total_words': len(vocab_words),
                    'mastered': len([w for w in vocab_words if w.mastery_level >= 0.8]),
                    'learning': len([w for w in vocab_words if 0.3 <= w.mastery_level < 0.8]),
                    'new': len([w for w in vocab_words if w.mastery_level < 0.3])
                },
                'vocabulary_list': [
                    {
                        'english_word': word.english_word,
                        'telugu_translation': word.telugu_translation,
                        'mastery_level': word.mastery_level,
                        'times_practiced': word.times_practiced,
                        'discovered_date': word.discovered_at.isoformat()
                    } for word in vocab_words[:100]  # Limit to first 100 words
                ]
            }
        
        return jsonify({
            'message': 'Progress report generated successfully!',
            'telugu_message': 'ప్రగతి నివేదిక విజయవంతంగా రూపొందించబడింది!',
            'report': report,
            'export_info': {
                'format': 'JSON',
                'generated_at': datetime.utcnow().isoformat(),
                'report_type': report_type
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating progress report: {str(e)}")
        return jsonify({
            'error': 'Failed to generate progress report',
            'telugu_message': 'ప్రగతి నివేదిక రూపొందించడంలో విఫలం'
        }), 500

# ===== ADVANCED ACTIVITY ANALYTICS SYSTEM =====

@analytics_bp.route('/activity-performance-analysis', methods=['GET'])
@jwt_required()
def get_activity_performance_analysis():
    """Advanced analytics for activity performance patterns"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        activity_type = request.args.get('activity_type')
        difficulty_level = request.args.get('difficulty_level')
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build base query
        query = UserActivityLog.query.filter_by(user_id=user_id)\
                                   .filter(UserActivityLog.completed_at >= start_date)
        
        # Get all logs in date range
        logs = query.all()
        
        if not logs:
            return jsonify({
                'message': 'No activity data found for analysis',
                'telugu_message': 'విశ్లేషణ కోసం కార్యకలాప డేటా కనుగొనబడలేదు',
                'analysis': {}
            }), 200
        
        # Get activity details
        activity_ids = [log.activity_id for log in logs]
        activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()
        activity_dict = {a.id: a for a in activities}
        
        # Performance analysis by activity type
        type_performance = {}
        difficulty_performance = {}
        time_patterns = {}
        accuracy_trends = []
        
        for log in logs:
            activity = activity_dict.get(log.activity_id)
            if not activity:
                continue
            
            # Activity type analysis
            if activity.activity_type not in type_performance:
                type_performance[activity.activity_type] = {
                    'total_attempts': 0,
                    'total_score': 0,
                    'total_max_score': 0,
                    'total_time': 0,
                    'activities': []
                }
            
            type_perf = type_performance[activity.activity_type]
            type_perf['total_attempts'] += 1
            type_perf['total_score'] += log.score or 0
            type_perf['total_max_score'] += log.max_score or 0
            type_perf['total_time'] += log.time_spent_minutes or 0
            
            # Difficulty level analysis
            if activity.difficulty_level not in difficulty_performance:
                difficulty_performance[activity.difficulty_level] = {
                    'total_attempts': 0,
                    'success_rate': 0,
                    'avg_time': 0,
                    'avg_score': 0
                }
            
            diff_perf = difficulty_performance[activity.difficulty_level]
            diff_perf['total_attempts'] += 1
            
            # Time pattern analysis (hour of day)
            hour = log.completed_at.hour
            if hour not in time_patterns:
                time_patterns[hour] = {'count': 0, 'avg_score': 0, 'total_score': 0, 'total_max': 0}
            
            time_patterns[hour]['count'] += 1
            time_patterns[hour]['total_score'] += log.score or 0
            time_patterns[hour]['total_max'] += log.max_score or 0
            
            # Accuracy trend over time
            if log.score and log.max_score and log.max_score > 0:
                accuracy = (log.score / log.max_score) * 100
                accuracy_trends.append({
                    'date': log.completed_at.date().isoformat(),
                    'accuracy': accuracy,
                    'activity_type': activity.activity_type
                })
        
        # Calculate averages and percentages
        for type_name, data in type_performance.items():
            if data['total_max_score'] > 0:
                data['success_rate'] = (data['total_score'] / data['total_max_score']) * 100
            else:
                data['success_rate'] = 0
            data['avg_time_per_activity'] = data['total_time'] / data['total_attempts'] if data['total_attempts'] > 0 else 0
        
        for level, data in difficulty_performance.items():
            level_logs = [log for log in logs if activity_dict.get(log.activity_id) and activity_dict[log.activity_id].difficulty_level == level]
            if level_logs:
                total_score = sum(log.score or 0 for log in level_logs)
                total_max = sum(log.max_score or 0 for log in level_logs)
                data['success_rate'] = (total_score / total_max * 100) if total_max > 0 else 0
                data['avg_time'] = sum(log.time_spent_minutes or 0 for log in level_logs) / len(level_logs)
                data['avg_score'] = total_score / len(level_logs)
        
        # Time pattern averages
        for hour, data in time_patterns.items():
            if data['total_max'] > 0:
                data['avg_score'] = (data['total_score'] / data['total_max']) * 100
            else:
                data['avg_score'] = 0
        
        # Generate insights using AI
        insights_prompt = f"""
        Analyze learning performance data for a Telugu speaker learning English and provide insights.
        
        Performance Summary:
        - Total Activities: {len(logs)}
        - Activity Types: {', '.join(type_performance.keys())}
        - Difficulty Levels: {', '.join(difficulty_performance.keys())}
        - Date Range: {days} days
        
        Type Performance: {json.dumps(type_performance, indent=2)}
        Difficulty Performance: {json.dumps(difficulty_performance, indent=2)}
        
        Provide insights about:
        1. Strengths and weaknesses
        2. Learning patterns
        3. Recommended improvements
        4. Optimal study times
        
        Return in JSON format:
        ```json
        {{
            "key_insights": [
                "Strong performance in vocabulary activities",
                "Struggles with grammar exercises"
            ],
            "strengths": [
                "Consistent daily practice",
                "High accuracy in flashcards"
            ],
            "improvement_areas": [
                "Grammar understanding needs work",
                "Speaking confidence is low"
            ],
            "recommendations": [
                "Focus more time on grammar exercises",
                "Practice speaking activities daily",
                "Try intermediate level content"
            ],
            "optimal_study_pattern": "Best performance between 9-11 AM",
            "telugu_summary": "మీ అభ్యాసంలో మంచి పురోగతి కనిపిస్తోంది...",
            "next_goals": [
                "Complete 5 grammar activities this week",
                "Improve speaking score by 10%"
            ]
        }}
        ```
        """
        
        from app.services.activity_generator_service import ActivityGeneratorService
        activity_service = ActivityGeneratorService()
        response = activity_service.model.generate_content(insights_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        ai_insights = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Activity performance analysis completed successfully!',
            'telugu_message': 'కార్యకలాప పనితీరు విశ్లేషణ విజయవంతంగా పూర్తయింది!',
            'analysis_period': {
                'days': days,
                'start_date': start_date.date().isoformat(),
                'end_date': datetime.utcnow().date().isoformat(),
                'total_activities': len(logs)
            },
            'performance_by_type': type_performance,
            'performance_by_difficulty': difficulty_performance,
            'time_patterns': time_patterns,
            'accuracy_trends': accuracy_trends[-20:],  # Last 20 activities
            'ai_insights': ai_insights
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze activity performance',
            'telugu_message': 'కార్యకలాప పనితీరు విశ్లేషణలో విఫలం',
            'details': str(e)
        }), 500

@analytics_bp.route('/learning-pattern-recognition', methods=['GET'])
@jwt_required()
def analyze_learning_patterns():
    """Recognize and analyze user's learning patterns using AI"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get comprehensive user data
        user = User.query.get(user_id)
        
        # Get recent activity logs (last 60 days)
        start_date = datetime.utcnow() - timedelta(days=60)
        recent_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                         .filter(UserActivityLog.completed_at >= start_date)\
                                         .order_by(UserActivityLog.completed_at.desc()).all()
        
        # Get learning path progress
        from app.models.course import LearningPath
        enrolled_paths = user.enrolled_paths if hasattr(user, 'enrolled_paths') else []
        
        # Calculate learning metrics
        total_activities = len(recent_logs)
        unique_activity_types = set()
        daily_activity_counts = {}
        weekly_progress = {}
        mistake_patterns = []
        
        for log in recent_logs:
            # Activity type tracking
            activity = Activity.query.get(log.activity_id)
            if activity:
                unique_activity_types.add(activity.activity_type)
            
            # Daily activity tracking
            date_key = log.completed_at.date().isoformat()
            if date_key not in daily_activity_counts:
                daily_activity_counts[date_key] = 0
            daily_activity_counts[date_key] += 1
            
            # Weekly progress tracking
            week_start = (log.completed_at.date() - timedelta(days=log.completed_at.weekday())).isoformat()
            if week_start not in weekly_progress:
                weekly_progress[week_start] = {'activities': 0, 'total_score': 0, 'total_max': 0}
            
            weekly_progress[week_start]['activities'] += 1
            weekly_progress[week_start]['total_score'] += log.score or 0
            weekly_progress[week_start]['total_max'] += log.max_score or 0
            
            # Identify potential mistakes/challenges
            if log.score and log.max_score and log.max_score > 0:
                accuracy = (log.score / log.max_score)
                if accuracy < 0.7:  # Less than 70% accuracy
                    mistake_patterns.append({
                        'activity_type': activity.activity_type if activity else 'unknown',
                        'accuracy': accuracy,
                        'date': log.completed_at.date().isoformat(),
                        'attempts': log.attempt_number or 1
                    })
        
        # Calculate consistency metrics
        active_days = len(daily_activity_counts)
        avg_activities_per_active_day = sum(daily_activity_counts.values()) / active_days if active_days > 0 else 0
        
        # Calculate weekly progress trends
        weekly_trends = []
        for week, data in sorted(weekly_progress.items()):
            accuracy = (data['total_score'] / data['total_max'] * 100) if data['total_max'] > 0 else 0
            weekly_trends.append({
                'week': week,
                'activities': data['activities'],
                'accuracy': accuracy
            })
        
        # Use AI to analyze patterns
        pattern_analysis_prompt = f"""
        Analyze detailed learning patterns for a Telugu speaker learning English.
        
        Learning Data Summary:
        - Total Activities (60 days): {total_activities}
        - Active Days: {active_days}/60
        - Average Activities per Day: {avg_activities_per_active_day:.1f}
        - Activity Types Practiced: {', '.join(unique_activity_types)}
        - Enrolled Learning Paths: {len(enrolled_paths)}
        
        Daily Activity Pattern: {json.dumps(list(daily_activity_counts.values())[-14:])}  # Last 14 days
        Weekly Trends: {json.dumps(weekly_trends[-8:])}  # Last 8 weeks
        Challenge Areas: {len(mistake_patterns)} activities with <70% accuracy
        
        Analyze and identify:
        1. Learning consistency patterns
        2. Peak performance times/periods
        3. Learning style preferences
        4. Areas needing attention
        5. Motivation patterns
        6. Optimal study schedule recommendations
        
        Return detailed analysis in JSON format:
        ```json
        {{
            "learning_style_analysis": {{
                "consistency_score": 85,
                "preferred_activity_types": ["flashcards", "reading"],
                "peak_performance_periods": ["morning", "evening"],
                "learning_streak_pattern": "consistent_daily",
                "challenge_response": "persistent_learner"
            }},
            "behavioral_patterns": {{
                "study_frequency": "daily",
                "session_length_preference": "short_bursts",
                "difficulty_progression": "gradual",
                "mistake_recovery": "quick_adaptation"
            }},
            "strengths_identified": [
                "Strong vocabulary retention",
                "Consistent daily practice",
                "Good at flashcard activities"
            ],
            "growth_opportunities": [
                "Grammar exercises need more focus",
                "Speaking activities avoided",
                "Could handle higher difficulty"
            ],
            "personalized_recommendations": {{
                "optimal_schedule": "20-30 minutes in morning, 15 minutes in evening",
                "focus_areas": ["grammar", "conversation"],
                "motivation_boosters": ["achievement_badges", "progress_visualization"],
                "next_challenge_level": "intermediate"
            }},
            "telugu_insights": "మీ అభ్యాస విధానంలో మంచి క్రమబద్ధత కనిపిస్తోంది...",
            "progress_prediction": {{
                "estimated_mastery_timeline": "3-4 months at current pace",
                "suggested_goals": ["Complete 100 activities", "Master beginner grammar"],
                "potential_challenges": ["May lose motivation without variety"]
            }}
        }}
        ```
        """
        
        from app.services.activity_generator_service import ActivityGeneratorService
        activity_service = ActivityGeneratorService()
        response = activity_service.model.generate_content(pattern_analysis_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        pattern_analysis = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Learning pattern analysis completed successfully!',
            'telugu_message': 'అభ్యాస విధాన విశ్లేషణ విజయవంతంగా పూర్తయింది!',
            'analysis_period': {
                'days_analyzed': 60,
                'total_activities': total_activities,
                'active_days': active_days,
                'consistency_percentage': round((active_days / 60) * 100, 1)
            },
            'learning_metrics': {
                'daily_activity_counts': daily_activity_counts,
                'weekly_progress': weekly_progress,
                'activity_types_practiced': list(unique_activity_types),
                'avg_activities_per_day': round(avg_activities_per_active_day, 1),
                'challenge_activities': len(mistake_patterns)
            },
            'ai_pattern_analysis': pattern_analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze learning patterns',
            'telugu_message': 'అభ్యాస విధానాలు విశ్లేషించడంలో విఫలం',
            'details': str(e)
        }), 500

@analytics_bp.route('/engagement-analytics', methods=['GET'])
@jwt_required()
def get_engagement_analytics():
    """Analyze user engagement metrics and patterns"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get engagement data for different time periods
        now = datetime.utcnow()
        periods = {
            'last_7_days': now - timedelta(days=7),
            'last_30_days': now - timedelta(days=30),
            'last_90_days': now - timedelta(days=90)
        }
        
        engagement_data = {}
        
        for period_name, start_date in periods.items():
            logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                      .filter(UserActivityLog.completed_at >= start_date).all()
            
            # Calculate metrics
            total_sessions = len(logs)
            total_time = sum(log.time_spent_minutes or 0 for log in logs)
            unique_days = len(set(log.completed_at.date() for log in logs))
            
            # Activity completion rate
            completed_activities = len([log for log in logs if log.score and log.max_score and (log.score / log.max_score) >= 0.7])
            completion_rate = (completed_activities / total_sessions * 100) if total_sessions > 0 else 0
            
            # Session length analysis
            session_lengths = [log.time_spent_minutes or 0 for log in logs if log.time_spent_minutes]
            avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
            
            # Streak calculation
            dates = sorted(set(log.completed_at.date() for log in logs))
            current_streak = 0
            max_streak = 0
            temp_streak = 0
            
            for i, date in enumerate(dates):
                if i == 0 or (date - dates[i-1]).days == 1:
                    temp_streak += 1
                else:
                    max_streak = max(max_streak, temp_streak)
                    temp_streak = 1
                    
                if date == now.date():
                    current_streak = temp_streak
            
            max_streak = max(max_streak, temp_streak)
            
            engagement_data[period_name] = {
                'total_sessions': total_sessions,
                'total_time_minutes': total_time,
                'unique_active_days': unique_days,
                'completion_rate': round(completion_rate, 1),
                'avg_session_length': round(avg_session_length, 1),
                'current_streak': current_streak,
                'max_streak': max_streak
            }
        
        # Calculate engagement score (0-100)
        recent_data = engagement_data['last_30_days']
        engagement_score = min(100, (
            (recent_data['unique_active_days'] / 30 * 40) +  # 40% for consistency
            (min(recent_data['completion_rate'], 100) * 0.3) +  # 30% for completion
            (min(recent_data['current_streak'], 10) / 10 * 20) +  # 20% for streak
            (min(recent_data['total_sessions'], 60) / 60 * 10)  # 10% for activity volume
        ))
        
        # Engagement level classification
        if engagement_score >= 80:
            engagement_level = "highly_engaged"
            telugu_level = "అధిక నిమగ్నత"
        elif engagement_score >= 60:
            engagement_level = "moderately_engaged"
            telugu_level = "మధ్యస్థ నిమగ్నత"
        elif engagement_score >= 40:
            engagement_level = "somewhat_engaged"
            telugu_level = "కొంత నిమగ్నత"
        else:
            engagement_level = "low_engagement"
            telugu_level = "తక్కువ నిమగ్నత"
        
        # Generate engagement insights
        insights_prompt = f"""
        Analyze user engagement patterns for a Telugu-English learning platform.
        
        Engagement Data:
        - 7 days: {engagement_data['last_7_days']['total_sessions']} sessions, {engagement_data['last_7_days']['unique_active_days']} active days
        - 30 days: {engagement_data['last_30_days']['total_sessions']} sessions, {engagement_data['last_30_days']['unique_active_days']} active days
        - Current streak: {engagement_data['last_30_days']['current_streak']} days
        - Completion rate: {engagement_data['last_30_days']['completion_rate']}%
        - Engagement score: {engagement_score:.1f}/100
        
        Provide engagement insights and recommendations:
        ```json
        {{
            "engagement_insights": [
                "User shows consistent daily engagement",
                "High completion rate indicates good motivation"
            ],
            "motivational_factors": [
                "Achievement unlocking",
                "Progress visualization",
                "Social features"
            ],
            "risk_factors": [
                "Potential plateau in difficulty",
                "May need variety in activities"
            ],
            "retention_recommendations": [
                "Introduce new challenge types",
                "Add gamification elements",
                "Personalize difficulty progression"
            ],
            "engagement_boost_strategies": [
                "Daily challenges",
                "Achievement badges",
                "Progress sharing"
            ],
            "telugu_motivation_message": "మీ అభ్యాసంలో మంచి క్రమబద్ధత కనిపిస్తోంది!"
        }}
        ```
        """
        
        from app.services.activity_generator_service import ActivityGeneratorService
        activity_service = ActivityGeneratorService()
        response = activity_service.model.generate_content(insights_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        engagement_insights = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Engagement analytics completed successfully!',
            'telugu_message': 'నిమగ్নత విశ్లేషణ విజయవంతంగా పూర్తయింది!',
            'engagement_score': round(engagement_score, 1),
            'engagement_level': engagement_level,
            'telugu_engagement_level': telugu_level,
            'metrics_by_period': engagement_data,
            'insights': engagement_insights
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze engagement',
            'telugu_message': 'నిమగ్నత విశ్లేషణలో విఫలం',
            'details': str(e)
        }), 500

@analytics_bp.route('/predictive-analytics', methods=['GET'])
@jwt_required()
def get_predictive_analytics():
    """Generate predictive analytics for learning outcomes"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get comprehensive user data
        user = User.query.get(user_id)
        
        # Get all user activity logs
        all_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                       .order_by(UserActivityLog.completed_at.desc()).all()
        
        if len(all_logs) < 5:
            return jsonify({
                'message': 'Insufficient data for predictions. Complete more activities.',
                'telugu_message': 'అంచనాలకు తగిన డేటా లేదు. మరింత కార్యకలాపాలు పూర్తి చేయండి.',
                'predictions': {}
            }), 200
        
        # Calculate learning trajectory
        recent_logs = all_logs[:20]  # Last 20 activities
        total_logs = len(all_logs)
        
        # Performance trend analysis
        performance_trend = []
        for i, log in enumerate(recent_logs):
            if log.score and log.max_score and log.max_score > 0:
                accuracy = (log.score / log.max_score) * 100
                performance_trend.append({
                    'activity_index': total_logs - i,
                    'accuracy': accuracy,
                    'date': log.completed_at.date().isoformat()
                })
        
        # Learning velocity (activities per week)
        if len(all_logs) >= 2:
            first_activity = all_logs[-1].completed_at
            last_activity = all_logs[0].completed_at
            weeks_active = (last_activity - first_activity).days / 7
            activities_per_week = total_logs / weeks_active if weeks_active > 0 else 0
        else:
            activities_per_week = 0
        
        # Calculate average scores by difficulty
        difficulty_performance = {}
        for log in recent_logs:
            activity = Activity.query.get(log.activity_id)
            if activity and log.score and log.max_score and log.max_score > 0:
                difficulty = activity.difficulty_level
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = []
                accuracy = (log.score / log.max_score) * 100
                difficulty_performance[difficulty].append(accuracy)
        
        # Average performance by difficulty
        avg_difficulty_performance = {}
        for difficulty, scores in difficulty_performance.items():
            avg_difficulty_performance[difficulty] = sum(scores) / len(scores)
        
        # Generate AI predictions
        prediction_prompt = f"""
        Generate predictive analytics for a Telugu speaker learning English based on their learning data.
        
        Learning Profile:
        - Total Activities Completed: {total_logs}
        - Activities per Week: {activities_per_week:.1f}
        - Recent Performance Trend: {performance_trend[:5]}  # Last 5 activities
        - Performance by Difficulty: {avg_difficulty_performance}
        
        Generate predictions for:
        1. Learning trajectory and completion timelines
        2. Skill mastery predictions
        3. Potential challenges and solutions
        4. Optimal learning path recommendations
        5. Achievement milestones
        
        Return predictions in JSON format:
        ```json
        {{
            "learning_trajectory": {{
                "current_pace": "above_average",
                "predicted_completion_months": 4,
                "confidence_level": 85,
                "trajectory_trend": "improving"
            }},
            "skill_mastery_predictions": {{
                "vocabulary": {{
                    "current_level": "intermediate",
                    "predicted_mastery_weeks": 8,
                    "confidence": 90
                }},
                "grammar": {{
                    "current_level": "beginner",
                    "predicted_mastery_weeks": 12,
                    "confidence": 75
                }}
            }},
            "achievement_predictions": [
                {{
                    "milestone": "Complete 100 activities",
                    "predicted_date": "2024-03-15",
                    "probability": 95
                }},
                {{
                    "milestone": "Reach intermediate level",
                    "predicted_date": "2024-04-01",
                    "probability": 80
                }}
            ],
            "potential_challenges": [
                {{
                    "challenge": "Grammar plateau",
                    "predicted_timeframe": "2-3 weeks",
                    "prevention_strategy": "Increase grammar exercise frequency"
                }}
            ],
            "recommendations": [
                "Maintain current pace - excellent progress!",
                "Focus on speaking activities to balance skills",
                "Consider advancing to intermediate content"
            ],
            "telugu_summary": "మీ అభ్యాస వేగం అద్భుతంగా ఉంది...",
            "success_probability": 88
        }}
        ```
        """
        
        from app.services.activity_generator_service import ActivityGeneratorService
        activity_service = ActivityGeneratorService()
        response = activity_service.model.generate_content(prediction_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        predictions = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Predictive analytics generated successfully!',
            'telugu_message': 'అంచనా విశ్లేషణ విజయవంతంగా రూపొందించబడింది!',
            'user_learning_profile': {
                'total_activities': total_logs,
                'activities_per_week': round(activities_per_week, 1),
                'recent_performance_trend': performance_trend[:10],
                'difficulty_performance': avg_difficulty_performance
            },
            'predictions': predictions,
            'data_confidence': 'high' if total_logs >= 20 else 'medium' if total_logs >= 10 else 'low'
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate predictive analytics',
            'telugu_message': 'అంచనా విశ్లేషణ రూపొందించడంలో విఫలం',
            'details': str(e)
        }), 500