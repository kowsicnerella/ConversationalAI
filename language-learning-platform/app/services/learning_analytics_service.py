"""
Learning Analytics Service - Phase 7
Comprehensive analytics and insights generation engine.

This service provides:
1. Weekly Learning Reports with AI insights
2. Progress Visualization Data
3. Predictive Analytics (level completion, skill mastery)
4. Peer Comparison Insights (anonymized)
5. Learning Velocity & Momentum Tracking
6. AI-Generated Personalized Insights
7. Study Session Analytics
8. Progress Snapshot Management

Author: GitHub Copilot
Date: October 20, 2025
Phase: 7 - Learning Analytics & Insights
"""

from datetime import datetime, timedelta, date
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, and_, or_
from app import db
from app.models.learning_analytics import (
    LearningAnalytics,
    WeeklyReport,
    ProgressSnapshot,
    StudySession,
    ComparisonMetric,
    InsightData
)
from app.models.user import User
import statistics
import math


class LearningAnalyticsService:
    """
    Comprehensive learning analytics and insights generation service.
    Provides data for analytics dashboard, predictions, and recommendations.
    """
    
    def __init__(self):
        self.db = db
    
    # ============================================================
    # SECTION 1: WEEKLY REPORTS
    # ============================================================
    
    def generate_weekly_report(self, user_id: int, week_offset: int = 0) -> dict:
        """
        Generate comprehensive weekly learning report.
        
        Args:
            user_id: User ID
            week_offset: 0 for current week, -1 for last week, etc.
        
        Returns:
            dict: Complete weekly report with all metrics
        """
        # Calculate week boundaries
        today = date.today()
        days_since_monday = today.weekday()
        current_week_start = today - timedelta(days=days_since_monday)
        week_start = current_week_start + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)
        
        # Check if report already exists
        existing_report = WeeklyReport.query.filter_by(
            user_id=user_id,
            week_start=datetime.combine(week_start, datetime.min.time())
        ).first()
        
        if existing_report:
            return existing_report.to_dict()
        
        # Calculate metrics for the week
        week_start_dt = datetime.combine(week_start, datetime.min.time())
        week_end_dt = datetime.combine(week_end, datetime.max.time())
        
        # Get study sessions for the week
        sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.session_start >= week_start_dt,
            StudySession.session_start <= week_end_dt
        ).all()
        
        # Calculate summary metrics
        study_time = sum(s.duration_minutes or 0 for s in sessions)
        activities_completed = sum(s.activities_completed for s in sessions)
        points_earned = sum(s.points_earned for s in sessions)
        
        # Get snapshots for skill improvement calculation
        week_start_snapshot = self._get_snapshot_near_date(user_id, week_start)
        week_end_snapshot = self._get_snapshot_near_date(user_id, week_end)
        
        # Calculate skill improvements
        improvements = self._calculate_skill_improvements(
            week_start_snapshot, 
            week_end_snapshot
        )
        
        # Generate AI insights
        ai_insights = self._generate_weekly_insights(
            user_id,
            study_time,
            activities_completed,
            improvements
        )
        
        # Identify strengths and weaknesses
        strengths = self._identify_top_skills(improvements, top=True)
        weaknesses = self._identify_top_skills(improvements, top=False)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            user_id,
            strengths,
            weaknesses,
            study_time
        )
        
        # Create weekly report
        report = WeeklyReport(
            user_id=user_id,
            week_start=week_start_dt,
            week_end=week_end_dt,
            week_number=week_start.isocalendar()[1],
            year=week_start.year,
            study_time_minutes=study_time,
            activities_completed=activities_completed,
            points_earned=points_earned,
            listening_improvement=improvements.get('listening', 0),
            speaking_improvement=improvements.get('speaking', 0),
            reading_improvement=improvements.get('reading', 0),
            writing_improvement=improvements.get('writing', 0),
            grammar_improvement=improvements.get('grammar', 0),
            vocabulary_improvement=improvements.get('vocabulary', 0),
            ai_insights=ai_insights,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            consistency_score=self._calculate_consistency_score(sessions),
            engagement_score=self._calculate_engagement_score(sessions)
        )
        
        db.session.add(report)
        db.session.commit()
        
        return report.to_dict()
    
    def get_weekly_reports(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get historical weekly reports."""
        reports = WeeklyReport.query.filter_by(user_id=user_id)\
            .order_by(WeeklyReport.week_start.desc())\
            .limit(limit)\
            .all()
        
        return [r.to_dict() for r in reports]
    
    # ============================================================
    # SECTION 2: PROGRESS VISUALIZATION
    # ============================================================
    
    def generate_progress_visualization(
        self, 
        user_id: int, 
        time_range: str = '30d'
    ) -> dict:
        """
        Generate data for progress visualization charts.
        
        Args:
            user_id: User ID
            time_range: '7d', '30d', '90d', '1y', 'all'
        
        Returns:
            {
                'timeline': [...],  # Daily snapshots
                'skills': {...},    # Current skill breakdown
                'velocity': [...],  # Learning velocity over time
                'milestones': [...]  # Achievement dates
            }
        """
        start_date, end_date = self._calculate_time_range(time_range)
        
        # Get snapshots for timeline
        snapshots = ProgressSnapshot.query.filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= start_date,
            ProgressSnapshot.snapshot_date <= end_date
        ).order_by(ProgressSnapshot.snapshot_date).all()
        
        timeline = [s.to_dict() for s in snapshots]
        
        # Get current skills
        analytics = self.get_or_create_analytics(user_id)
        skills = {
            'listening': analytics.listening_proficiency,
            'speaking': analytics.speaking_proficiency,
            'reading': analytics.reading_proficiency,
            'writing': analytics.writing_proficiency,
            'grammar': analytics.grammar_proficiency,
            'vocabulary': analytics.vocabulary_proficiency
        }
        
        # Calculate velocity over time
        velocity = self._calculate_velocity_timeline(user_id, snapshots)
        
        # Get milestones (weekly reports with achievements)
        milestones = self._get_milestones(user_id, start_date, end_date)
        
        return {
            'timeline': timeline,
            'skills': skills,
            'velocity': velocity,
            'milestones': milestones,
            'time_range': time_range,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    
    def get_skill_radar_data(self, user_id: int) -> dict:
        """
        Get current skill proficiency for radar chart.
        
        Returns:
            {
                'listening': 75,
                'speaking': 60,
                ...
            }
        """
        analytics = self.get_or_create_analytics(user_id)
        
        return {
            'listening': round(analytics.listening_proficiency, 1),
            'speaking': round(analytics.speaking_proficiency, 1),
            'reading': round(analytics.reading_proficiency, 1),
            'writing': round(analytics.writing_proficiency, 1),
            'grammar': round(analytics.grammar_proficiency, 1),
            'vocabulary': round(analytics.vocabulary_proficiency, 1)
        }
    
    # ============================================================
    # SECTION 3: PREDICTIONS
    # ============================================================
    
    def predict_level_completion(self, user_id: int) -> dict:
        """
        Predict when user will reach next CEFR level.
        
        Returns:
            {
                'current_level': 'A2',
                'next_level': 'B1',
                'current_progress': 67.5,  # %
                'predicted_date': '2025-12-15',
                'confidence': 0.85,
                'days_remaining': 45,
                'required_velocity': 15.3  # points/week
            }
        """
        analytics = self.get_or_create_analytics(user_id)
        
        # CEFR level progression
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        current_level = analytics.current_level or 'A1'
        
        if current_level not in levels:
            current_level = 'A1'
        
        current_index = levels.index(current_level)
        
        if current_index >= len(levels) - 1:
            # Already at max level
            return {
                'current_level': current_level,
                'next_level': None,
                'current_progress': 100,
                'predicted_date': None,
                'confidence': 1.0,
                'days_remaining': 0,
                'required_velocity': 0,
                'message': 'Maximum level achieved!'
            }
        
        next_level = levels[current_index + 1]
        current_progress = analytics.level_progress or 0
        
        # Calculate points needed (assuming 100 points per level)
        points_needed = (100 - current_progress)
        
        # Get current velocity
        velocity = analytics.weekly_velocity or 0
        
        if velocity <= 0:
            # Not enough data for prediction
            return {
                'current_level': current_level,
                'next_level': next_level,
                'current_progress': round(current_progress, 1),
                'predicted_date': None,
                'confidence': 0,
                'days_remaining': None,
                'required_velocity': 10.0,  # Suggested velocity
                'message': 'Not enough data for prediction. Keep learning!'
            }
        
        # Calculate weeks needed
        weeks_needed = points_needed / velocity
        days_remaining = int(weeks_needed * 7)
        predicted_date = date.today() + timedelta(days=days_remaining)
        
        # Calculate confidence based on data consistency
        confidence = self._calculate_prediction_confidence(user_id)
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'current_progress': round(current_progress, 1),
            'predicted_date': predicted_date.isoformat(),
            'confidence': round(confidence, 2),
            'days_remaining': days_remaining,
            'required_velocity': round(velocity, 1)
        }
    
    def predict_skill_mastery(self, user_id: int, skill: str) -> dict:
        """Predict when user will master a specific skill (reach 90%)."""
        analytics = self.get_or_create_analytics(user_id)
        
        # Get current proficiency
        skill_attr = f'{skill}_proficiency'
        current_proficiency = getattr(analytics, skill_attr, 0)
        
        # Mastery threshold
        mastery_threshold = 90.0
        
        if current_proficiency >= mastery_threshold:
            return {
                'skill': skill,
                'current_proficiency': round(current_proficiency, 1),
                'mastery_threshold': mastery_threshold,
                'predicted_date': None,
                'already_mastered': True,
                'message': f'{skill.capitalize()} already mastered!'
            }
        
        # Calculate improvement rate
        improvement_rate = self._calculate_skill_improvement_rate(user_id, skill)
        
        if improvement_rate <= 0:
            return {
                'skill': skill,
                'current_proficiency': round(current_proficiency, 1),
                'mastery_threshold': mastery_threshold,
                'predicted_date': None,
                'confidence': 0,
                'message': 'Not enough data for prediction'
            }
        
        # Calculate weeks needed
        points_needed = mastery_threshold - current_proficiency
        weeks_needed = points_needed / improvement_rate
        days_remaining = int(weeks_needed * 7)
        predicted_date = date.today() + timedelta(days=days_remaining)
        
        confidence = self._calculate_prediction_confidence(user_id)
        
        return {
            'skill': skill,
            'current_proficiency': round(current_proficiency, 1),
            'mastery_threshold': mastery_threshold,
            'predicted_date': predicted_date.isoformat(),
            'confidence': round(confidence, 2),
            'days_remaining': days_remaining,
            'weekly_improvement_rate': round(improvement_rate, 2)
        }
    
    # ============================================================
    # SECTION 4: COMPARISONS
    # ============================================================
    
    def generate_comparison_insights(self, user_id: int) -> dict:
        """
        Generate peer comparison insights (anonymized).
        
        Returns:
            {
                'vs_self': {...},      # Compare to own past
                'vs_peers': {...},     # Compare to similar learners
                'vs_expected': {...}   # Compare to learning curve
            }
        """
        analytics = self.get_or_create_analytics(user_id)
        current_level = analytics.current_level or 'A1'
        
        # Compare to own past (30 days ago)
        vs_self = self._compare_to_past(user_id, days=30)
        
        # Compare to peers at same level
        vs_peers = self._compare_to_peers(user_id, current_level)
        
        # Compare to expected learning curve
        vs_expected = self._compare_to_expected_curve(user_id)
        
        return {
            'vs_self': vs_self,
            'vs_peers': vs_peers,
            'vs_expected': vs_expected,
            'user_level': current_level
        }
    
    def get_percentile_ranking(self, user_id: int, metric: str) -> dict:
        """Get user's percentile ranking for a metric."""
        analytics = self.get_or_create_analytics(user_id)
        current_level = analytics.current_level or 'A1'
        
        # Get user's metric value
        if hasattr(analytics, metric):
            user_value = getattr(analytics, metric)
        else:
            return {'error': f'Invalid metric: {metric}'}
        
        # Get comparison metric
        comparison = ComparisonMetric.query.filter_by(
            level=current_level,
            metric_name=metric
        ).first()
        
        if not comparison:
            return {
                'metric': metric,
                'user_value': user_value,
                'percentile': None,
                'message': 'Not enough peer data for comparison'
            }
        
        # Calculate percentile
        percentile = self._calculate_percentile(
            user_value,
            comparison
        )
        
        return {
            'metric': metric,
            'user_value': round(user_value, 1) if user_value else 0,
            'percentile': round(percentile, 1),
            'cohort_mean': round(comparison.mean_value, 1) if comparison.mean_value else None,
            'cohort_median': round(comparison.median_value, 1) if comparison.median_value else None,
            'level': current_level,
            'sample_size': comparison.sample_size
        }
    
    # ============================================================
    # SECTION 5: VELOCITY & MOMENTUM
    # ============================================================
    
    def calculate_learning_velocity(self, user_id: int, period: str = 'week') -> dict:
        """
        Calculate learning velocity (rate of improvement).
        
        Returns:
            {
                'current_velocity': 12.5,  # points/week
                'average_velocity': 10.2,
                'acceleration': 2.3,       # change in velocity
                'momentum': 'increasing',  # increasing, steady, decreasing
                'trend': 'positive'        # positive, neutral, negative
            }
        """
        analytics = self.get_or_create_analytics(user_id)
        
        # Get velocity based on period
        if period == 'week':
            current_velocity = analytics.weekly_velocity or 0
        elif period == 'month':
            current_velocity = analytics.monthly_velocity or 0
        else:
            current_velocity = analytics.weekly_velocity or 0
        
        # Calculate average velocity over last 90 days
        average_velocity = self._calculate_average_velocity(user_id, days=90)
        
        # Get acceleration
        acceleration = analytics.acceleration or 0
        
        # Determine momentum
        if acceleration > 0.5:
            momentum = 'increasing'
            trend = 'positive'
        elif acceleration < -0.5:
            momentum = 'decreasing'
            trend = 'negative'
        else:
            momentum = 'steady'
            trend = 'neutral'
        
        return {
            'current_velocity': round(current_velocity, 1),
            'average_velocity': round(average_velocity, 1),
            'acceleration': round(acceleration, 2),
            'momentum': momentum,
            'trend': trend,
            'period': period
        }
    
    def get_optimal_study_schedule(self, user_id: int) -> dict:
        """Recommend optimal study times based on historical performance."""
        # Get study sessions for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.session_start >= thirty_days_ago
        ).all()
        
        if not sessions:
            return {
                'message': 'Not enough session data',
                'recommendation': 'Study daily for at least 15 minutes'
            }
        
        # Analyze performance by time of day
        performance_by_hour = {}
        for session in sessions:
            hour = session.session_start.hour
            if hour not in performance_by_hour:
                performance_by_hour[hour] = []
            
            if session.engagement_score:
                performance_by_hour[hour].append(session.engagement_score)
        
        # Find best time slots
        best_hours = []
        for hour, scores in performance_by_hour.items():
            avg_score = statistics.mean(scores) if scores else 0
            best_hours.append({
                'hour': hour,
                'avg_engagement': avg_score,
                'session_count': len(scores)
            })
        
        # Sort by engagement
        best_hours.sort(key=lambda x: x['avg_engagement'], reverse=True)
        
        # Get top 3 time slots
        top_slots = best_hours[:3]
        
        return {
            'optimal_time_slots': [
                {
                    'time': f'{slot["hour"]:02d}:00 - {slot["hour"]+1:02d}:00',
                    'engagement_score': round(slot['avg_engagement'], 2),
                    'session_count': slot['session_count']
                }
                for slot in top_slots
            ],
            'recommendation': f'Your peak learning time is around {top_slots[0]["hour"]:02d}:00' if top_slots else 'Study consistently'
        }
    
    # ============================================================
    # SECTION 6: INSIGHTS
    # ============================================================
    
    def generate_personalized_insights(self, user_id: int) -> List[dict]:
        """
        Generate AI-powered personalized insights.
        
        Returns list of insights with type, category, title, description, etc.
        """
        insights = []
        analytics = self.get_or_create_analytics(user_id)
        
        # Identify strengths
        skills = {
            'listening': analytics.listening_proficiency,
            'speaking': analytics.speaking_proficiency,
            'reading': analytics.reading_proficiency,
            'writing': analytics.writing_proficiency,
            'grammar': analytics.grammar_proficiency,
            'vocabulary': analytics.vocabulary_proficiency
        }
        
        # Find top skill
        top_skill = max(skills.items(), key=lambda x: x[1])
        if top_skill[1] >= 75:
            insights.append({
                'type': 'strength',
                'category': top_skill[0],
                'title': f'{top_skill[0].capitalize()} Excellence',
                'description': f'You\'ve achieved {top_skill[1]:.0f}% proficiency in {top_skill[0]}! Keep up the great work.',
                'priority': 'high',
                'confidence': 0.95
            })
        
        # Find weakest skill
        weak_skill = min(skills.items(), key=lambda x: x[1])
        if weak_skill[1] < 60:
            insights.append({
                'type': 'weakness',
                'category': weak_skill[0],
                'title': f'Focus on {weak_skill[0].capitalize()}',
                'description': f'Your {weak_skill[0]} proficiency is at {weak_skill[1]:.0f}%. Dedicating 15 minutes daily can boost this significantly.',
                'priority': 'high',
                'confidence': 0.90,
                'action_items': [
                    f'Complete 3 {weak_skill[0]} activities daily',
                    f'Review {weak_skill[0]} fundamentals',
                    'Practice with native content'
                ]
            })
        
        # Check study consistency
        if analytics.current_streak >= 7:
            insights.append({
                'type': 'strength',
                'category': 'consistency',
                'title': 'Consistency Champion',
                'description': f'Amazing! You\'ve maintained a {analytics.current_streak}-day streak. Consistency is key to language mastery.',
                'priority': 'medium',
                'confidence': 1.0
            })
        elif analytics.current_streak == 0:
            insights.append({
                'type': 'recommendation',
                'category': 'consistency',
                'title': 'Build a Daily Habit',
                'description': 'Starting a daily learning streak can accelerate your progress. Even 10 minutes daily makes a difference!',
                'priority': 'high',
                'confidence': 0.85,
                'action_items': [
                    'Set a daily reminder',
                    'Start with 10-minute sessions',
                    'Track your streak progress'
                ]
            })
        
        # Check velocity
        if analytics.acceleration and analytics.acceleration > 1.0:
            insights.append({
                'type': 'prediction',
                'category': 'velocity',
                'title': 'Accelerating Progress',
                'description': 'Your learning velocity is increasing! At this rate, you\'ll reach your next milestone ahead of schedule.',
                'priority': 'medium',
                'confidence': 0.80
            })
        
        return insights
    
    def identify_learning_patterns(self, user_id: int) -> dict:
        """Identify patterns in learning behavior."""
        # Get sessions from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.session_start >= thirty_days_ago
        ).all()
        
        if not sessions:
            return {'message': 'Not enough data to identify patterns'}
        
        # Analyze patterns
        patterns = {
            'preferred_study_days': self._identify_preferred_days(sessions),
            'average_session_length': statistics.mean([s.duration_minutes for s in sessions if s.duration_minutes]),
            'most_active_time': self._identify_peak_time(sessions),
            'consistency_level': self._calculate_consistency_level(sessions),
            'engagement_trend': self._calculate_engagement_trend(sessions)
        }
        
        return patterns
    
    # ============================================================
    # SECTION 7: STUDY SESSIONS
    # ============================================================
    
    def track_study_session(
        self,
        user_id: int,
        session_start: datetime,
        session_end: datetime,
        activities: List[int] = None
    ) -> dict:
        """Track a completed study session."""
        duration = int((session_end - session_start).total_seconds() / 60)
        
        session = StudySession(
            user_id=user_id,
            session_start=session_start,
            session_end=session_end,
            duration_minutes=duration,
            activities_completed=len(activities) if activities else 0,
            activity_ids=activities or []
        )
        
        db.session.add(session)
        
        # Update analytics
        self.update_analytics_after_session(user_id, session)
        
        db.session.commit()
        
        return session.to_dict()
    
    def get_study_history(self, user_id: int, days: int = 30) -> List[dict]:
        """Get study session history."""
        start_date = datetime.now() - timedelta(days=days)
        
        sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.session_start >= start_date
        ).order_by(StudySession.session_start.desc()).all()
        
        return [s.to_dict() for s in sessions]
    
    # ============================================================
    # SECTION 8: SNAPSHOTS
    # ============================================================
    
    def create_daily_snapshot(self, user_id: int) -> dict:
        """Create daily progress snapshot."""
        today = date.today()
        
        # Check if snapshot already exists
        existing = ProgressSnapshot.query.filter_by(
            user_id=user_id,
            snapshot_date=today
        ).first()
        
        if existing:
            return existing.to_dict()
        
        # Get current analytics
        analytics = self.get_or_create_analytics(user_id)
        
        # Get today's activity
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_sessions = StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.session_start >= today_start,
            StudySession.session_start <= today_end
        ).all()
        
        study_time_today = sum(s.duration_minutes or 0 for s in today_sessions)
        activities_today = sum(s.activities_completed for s in today_sessions)
        
        # Create snapshot
        snapshot = ProgressSnapshot(
            user_id=user_id,
            snapshot_date=today,
            listening=analytics.listening_proficiency,
            speaking=analytics.speaking_proficiency,
            reading=analytics.reading_proficiency,
            writing=analytics.writing_proficiency,
            grammar=analytics.grammar_proficiency,
            vocabulary=analytics.vocabulary_proficiency,
            overall_level=analytics.current_level,
            total_points=analytics.total_activities_completed * 10,  # Rough estimate
            study_time_today=study_time_today,
            activities_today=activities_today
        )
        
        db.session.add(snapshot)
        db.session.commit()
        
        return snapshot.to_dict()
    
    def get_snapshot_history(self, user_id: int, days: int = 90) -> List[dict]:
        """Get historical snapshots."""
        start_date = date.today() - timedelta(days=days)
        
        snapshots = ProgressSnapshot.query.filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= start_date
        ).order_by(ProgressSnapshot.snapshot_date).all()
        
        return [s.to_dict() for s in snapshots]
    
    # ============================================================
    # SECTION 9: HELPER METHODS
    # ============================================================
    
    def get_or_create_analytics(self, user_id: int) -> LearningAnalytics:
        """Get or create analytics record for user."""
        analytics = LearningAnalytics.query.filter_by(user_id=user_id).first()
        
        if not analytics:
            analytics = LearningAnalytics(user_id=user_id)
            db.session.add(analytics)
            db.session.commit()
        
        return analytics
    
    def update_analytics_after_session(
        self,
        user_id: int,
        session: StudySession
    ) -> None:
        """Update analytics after a study session."""
        analytics = self.get_or_create_analytics(user_id)
        
        # Update time tracking
        analytics.total_study_time += session.duration_minutes or 0
        analytics.last_activity_date = session.session_end or session.session_start
        
        # Update activity count
        analytics.total_activities_completed += session.activities_completed
        
        # Recalculate average session duration
        total_sessions = StudySession.query.filter_by(user_id=user_id).count()
        if total_sessions > 0:
            analytics.average_session_duration = analytics.total_study_time / total_sessions
        
        # Update velocity
        self._update_velocity(analytics, user_id)
        
        db.session.commit()
    
    def _calculate_time_range(self, range_str: str) -> Tuple[date, date]:
        """Convert range string (e.g., '30d') to date range."""
        end_date = date.today()
        
        if range_str == '7d':
            start_date = end_date - timedelta(days=7)
        elif range_str == '30d':
            start_date = end_date - timedelta(days=30)
        elif range_str == '90d':
            start_date = end_date - timedelta(days=90)
        elif range_str == '1y':
            start_date = end_date - timedelta(days=365)
        elif range_str == 'all':
            start_date = date(2020, 1, 1)  # Platform start date
        else:
            start_date = end_date - timedelta(days=30)
        
        return start_date, end_date
    
    def _get_snapshot_near_date(
        self,
        user_id: int,
        target_date: date
    ) -> Optional[ProgressSnapshot]:
        """Get snapshot closest to target date."""
        # Try exact date first
        snapshot = ProgressSnapshot.query.filter_by(
            user_id=user_id,
            snapshot_date=target_date
        ).first()
        
        if snapshot:
            return snapshot
        
        # Try within 3 days
        for offset in range(-3, 4):
            check_date = target_date + timedelta(days=offset)
            snapshot = ProgressSnapshot.query.filter_by(
                user_id=user_id,
                snapshot_date=check_date
            ).first()
            
            if snapshot:
                return snapshot
        
        return None
    
    def _calculate_skill_improvements(
        self,
        start_snapshot: Optional[ProgressSnapshot],
        end_snapshot: Optional[ProgressSnapshot]
    ) -> dict:
        """Calculate skill improvements between two snapshots."""
        if not start_snapshot or not end_snapshot:
            return {
                'listening': 0,
                'speaking': 0,
                'reading': 0,
                'writing': 0,
                'grammar': 0,
                'vocabulary': 0
            }
        
        return {
            'listening': end_snapshot.listening - start_snapshot.listening,
            'speaking': end_snapshot.speaking - start_snapshot.speaking,
            'reading': end_snapshot.reading - start_snapshot.reading,
            'writing': end_snapshot.writing - start_snapshot.writing,
            'grammar': end_snapshot.grammar - start_snapshot.grammar,
            'vocabulary': end_snapshot.vocabulary - start_snapshot.vocabulary
        }
    
    def _generate_weekly_insights(
        self,
        user_id: int,
        study_time: int,
        activities: int,
        improvements: dict
    ) -> str:
        """Generate AI insights for weekly report."""
        # Simple insight generation (can be enhanced with actual AI)
        total_improvement = sum(improvements.values())
        
        if study_time >= 120:  # 2+ hours
            time_feedback = "Excellent study time this week!"
        elif study_time >= 60:
            time_feedback = "Good progress with your study time."
        else:
            time_feedback = "Try to increase your study time next week."
        
        if total_improvement > 10:
            progress_feedback = "Outstanding skill improvements across the board!"
        elif total_improvement > 5:
            progress_feedback = "Solid progress in multiple skill areas."
        else:
            progress_feedback = "Keep practicing to see bigger improvements."
        
        return f"{time_feedback} {progress_feedback} You completed {activities} activities this week."
    
    def _identify_top_skills(
        self,
        improvements: dict,
        top: bool = True
    ) -> List[str]:
        """Identify top 3 skills (improvements or needs work)."""
        sorted_skills = sorted(
            improvements.items(),
            key=lambda x: x[1],
            reverse=top
        )
        
        return [skill for skill, _ in sorted_skills[:3]]
    
    def _generate_recommendations(
        self,
        user_id: int,
        strengths: List[str],
        weaknesses: List[str],
        study_time: int
    ) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Weakness-based recommendations
        if weaknesses:
            recommendations.append(
                f"Focus on {weaknesses[0]} with daily 15-minute practice sessions"
            )
        
        # Time-based recommendations
        if study_time < 60:
            recommendations.append(
                "Try to study at least 60 minutes per week for faster progress"
            )
        
        # Strength-based recommendations
        if strengths:
            recommendations.append(
                f"Leverage your {strengths[0]} strength to boost confidence"
            )
        
        return recommendations[:3]  # Return top 3
    
    def _calculate_consistency_score(self, sessions: List[StudySession]) -> float:
        """Calculate consistency score (0-100) based on session distribution."""
        if not sessions:
            return 0.0
        
        # Group sessions by day
        days_active = set(s.session_start.date() for s in sessions)
        total_days = 7  # Week
        
        # Consistency is % of days with activity
        consistency = (len(days_active) / total_days) * 100
        
        return min(consistency, 100.0)
    
    def _calculate_engagement_score(self, sessions: List[StudySession]) -> float:
        """Calculate engagement score (0-100) based on session quality."""
        if not sessions:
            return 0.0
        
        engagement_scores = [
            s.engagement_score for s in sessions 
            if s.engagement_score is not None
        ]
        
        if not engagement_scores:
            return 50.0  # Default
        
        return statistics.mean(engagement_scores) * 100
    
    def _calculate_velocity_timeline(
        self,
        user_id: int,
        snapshots: List[ProgressSnapshot]
    ) -> List[dict]:
        """Calculate velocity over time from snapshots."""
        if len(snapshots) < 2:
            return []
        
        velocity_data = []
        
        for i in range(1, len(snapshots)):
            prev = snapshots[i-1]
            curr = snapshots[i]
            
            days_diff = (curr.snapshot_date - prev.snapshot_date).days
            if days_diff == 0:
                continue
            
            # Calculate point change (rough estimate)
            point_change = (curr.total_points or 0) - (prev.total_points or 0)
            velocity = (point_change / days_diff) * 7  # Weekly velocity
            
            velocity_data.append({
                'date': curr.snapshot_date.isoformat(),
                'velocity': round(velocity, 1)
            })
        
        return velocity_data
    
    def _get_milestones(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """Get achievement milestones in date range."""
        reports = WeeklyReport.query.filter(
            WeeklyReport.user_id == user_id,
            WeeklyReport.week_start >= datetime.combine(start_date, datetime.min.time()),
            WeeklyReport.week_end <= datetime.combine(end_date, datetime.max.time()),
            WeeklyReport.new_level_reached == True
        ).all()
        
        return [
            {
                'date': r.week_end.date().isoformat(),
                'title': 'New Level Reached!',
                'description': f'Advanced to a new level'
            }
            for r in reports
        ]
    
    def _calculate_prediction_confidence(self, user_id: int) -> float:
        """Calculate confidence in predictions based on data consistency."""
        # Get snapshots from last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        
        snapshots = ProgressSnapshot.query.filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= thirty_days_ago
        ).count()
        
        # Confidence increases with more data
        if snapshots >= 25:
            return 0.95
        elif snapshots >= 15:
            return 0.85
        elif snapshots >= 7:
            return 0.70
        else:
            return 0.50
    
    def _calculate_skill_improvement_rate(
        self,
        user_id: int,
        skill: str
    ) -> float:
        """Calculate weekly improvement rate for a skill."""
        # Get snapshots from last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        
        snapshots = ProgressSnapshot.query.filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= thirty_days_ago
        ).order_by(ProgressSnapshot.snapshot_date).all()
        
        if len(snapshots) < 2:
            return 0.0
        
        first = snapshots[0]
        last = snapshots[-1]
        
        days_diff = (last.snapshot_date - first.snapshot_date).days
        if days_diff == 0:
            return 0.0
        
        # Get skill values
        first_value = getattr(first, skill, 0)
        last_value = getattr(last, skill, 0)
        
        improvement = last_value - first_value
        weekly_rate = (improvement / days_diff) * 7
        
        return weekly_rate
    
    def _compare_to_past(self, user_id: int, days: int = 30) -> dict:
        """Compare current performance to past."""
        analytics = self.get_or_create_analytics(user_id)
        past_date = date.today() - timedelta(days=days)
        
        past_snapshot = self._get_snapshot_near_date(user_id, past_date)
        
        if not past_snapshot:
            return {'message': 'Not enough historical data'}
        
        # Calculate improvements
        improvements = {
            'listening': analytics.listening_proficiency - past_snapshot.listening,
            'speaking': analytics.speaking_proficiency - past_snapshot.speaking,
            'reading': analytics.reading_proficiency - past_snapshot.reading,
            'writing': analytics.writing_proficiency - past_snapshot.writing,
            'grammar': analytics.grammar_proficiency - past_snapshot.grammar,
            'vocabulary': analytics.vocabulary_proficiency - past_snapshot.vocabulary
        }
        
        return {
            'period_days': days,
            'improvements': {k: round(v, 1) for k, v in improvements.items()},
            'overall_trend': 'improving' if sum(improvements.values()) > 0 else 'stable'
        }
    
    def _compare_to_peers(self, user_id: int, level: str) -> dict:
        """Compare to peers at same level."""
        analytics = self.get_or_create_analytics(user_id)
        
        # Get comparison metrics for level
        metrics = ComparisonMetric.query.filter_by(level=level).all()
        
        if not metrics:
            return {'message': 'Not enough peer data'}
        
        comparisons = {}
        
        for metric in metrics:
            user_value = getattr(analytics, metric.metric_name, None)
            if user_value is None:
                continue
            
            percentile = self._calculate_percentile(user_value, metric)
            
            comparisons[metric.metric_name] = {
                'user_value': round(user_value, 1),
                'peer_average': round(metric.mean_value, 1) if metric.mean_value else None,
                'percentile': round(percentile, 1)
            }
        
        return comparisons
    
    def _compare_to_expected_curve(self, user_id: int) -> dict:
        """Compare to expected learning curve."""
        analytics = self.get_or_create_analytics(user_id)
        
        # Simple expected curve based on total study time
        hours_studied = analytics.total_study_time / 60
        
        # Expected proficiency = sqrt(hours) * 10 (simplified model)
        expected_proficiency = min(math.sqrt(hours_studied) * 10, 100)
        
        # Average actual proficiency
        actual_proficiency = statistics.mean([
            analytics.listening_proficiency,
            analytics.speaking_proficiency,
            analytics.reading_proficiency,
            analytics.writing_proficiency,
            analytics.grammar_proficiency,
            analytics.vocabulary_proficiency
        ])
        
        difference = actual_proficiency - expected_proficiency
        
        if difference > 10:
            status = 'ahead'
        elif difference < -10:
            status = 'behind'
        else:
            status = 'on_track'
        
        return {
            'expected_proficiency': round(expected_proficiency, 1),
            'actual_proficiency': round(actual_proficiency, 1),
            'difference': round(difference, 1),
            'status': status
        }
    
    def _calculate_percentile(
        self,
        value: float,
        comparison: ComparisonMetric
    ) -> float:
        """Calculate percentile ranking for a value."""
        # Simple percentile calculation
        if value >= comparison.percentile_95:
            return 95
        elif value >= comparison.percentile_90:
            return 90
        elif value >= comparison.percentile_75:
            return 75
        elif value >= comparison.percentile_50:
            return 50
        elif value >= comparison.percentile_25:
            return 25
        elif value >= comparison.percentile_10:
            return 10
        else:
            return 5
    
    def _calculate_average_velocity(self, user_id: int, days: int) -> float:
        """Calculate average velocity over period."""
        start_date = date.today() - timedelta(days=days)
        
        snapshots = ProgressSnapshot.query.filter(
            ProgressSnapshot.user_id == user_id,
            ProgressSnapshot.snapshot_date >= start_date
        ).order_by(ProgressSnapshot.snapshot_date).all()
        
        if len(snapshots) < 2:
            return 0.0
        
        first = snapshots[0]
        last = snapshots[-1]
        
        days_diff = (last.snapshot_date - first.snapshot_date).days
        if days_diff == 0:
            return 0.0
        
        point_change = (last.total_points or 0) - (first.total_points or 0)
        weekly_velocity = (point_change / days_diff) * 7
        
        return weekly_velocity
    
    def _update_velocity(self, analytics: LearningAnalytics, user_id: int) -> None:
        """Update velocity metrics in analytics."""
        # Calculate weekly velocity
        analytics.weekly_velocity = self._calculate_average_velocity(user_id, days=7)
        
        # Calculate monthly velocity
        analytics.monthly_velocity = self._calculate_average_velocity(user_id, days=30)
        
        # Calculate acceleration (change in weekly velocity)
        prev_week_velocity = self._calculate_average_velocity(user_id, days=14)
        
        if prev_week_velocity > 0:
            analytics.acceleration = analytics.weekly_velocity - prev_week_velocity
    
    def _identify_preferred_days(self, sessions: List[StudySession]) -> List[str]:
        """Identify preferred study days."""
        day_counts = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for session in sessions:
            day = session.session_start.weekday()
            day_counts[day] = day_counts.get(day, 0) + 1
        
        sorted_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [day_names[day] for day, _ in sorted_days[:3]]
    
    def _identify_peak_time(self, sessions: List[StudySession]) -> str:
        """Identify peak study time."""
        hour_counts = {}
        
        for session in sessions:
            hour = session.session_start.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return 'Not enough data'
        
        peak_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
        
        if peak_hour < 12:
            return 'Morning'
        elif peak_hour < 17:
            return 'Afternoon'
        else:
            return 'Evening'
    
    def _calculate_consistency_level(self, sessions: List[StudySession]) -> str:
        """Calculate consistency level."""
        if not sessions:
            return 'No data'
        
        days_active = set(s.session_start.date() for s in sessions)
        consistency_pct = (len(days_active) / 30) * 100
        
        if consistency_pct >= 80:
            return 'Excellent'
        elif consistency_pct >= 60:
            return 'Good'
        elif consistency_pct >= 40:
            return 'Fair'
        else:
            return 'Needs Improvement'
    
    def _calculate_engagement_trend(self, sessions: List[StudySession]) -> str:
        """Calculate engagement trend."""
        sessions_with_scores = [s for s in sessions if s.engagement_score is not None]
        
        if len(sessions_with_scores) < 5:
            return 'Not enough data'
        
        # Split into first half and second half
        mid = len(sessions_with_scores) // 2
        first_half = sessions_with_scores[:mid]
        second_half = sessions_with_scores[mid:]
        
        first_avg = statistics.mean([s.engagement_score for s in first_half])
        second_avg = statistics.mean([s.engagement_score for s in second_half])
        
        if second_avg > first_avg + 0.05:
            return 'Increasing'
        elif second_avg < first_avg - 0.05:
            return 'Decreasing'
        else:
            return 'Stable'
