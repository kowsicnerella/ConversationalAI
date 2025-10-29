"""
Learning Analytics Database Models - Phase 7
Phase 7: Learning Analytics & Insights

New Models for Analytics Dashboard:
1. LearningAnalytics - Aggregate analytics for each user
2. WeeklyReport - Weekly learning summaries
3. ProgressSnapshot - Daily skill proficiency snapshots
4. StudySession - Individual study session tracking
5. ComparisonMetric - Peer comparison data
6. InsightData - AI-generated insights
"""

from datetime import datetime
from app import db


class LearningAnalytics(db.Model):
    """
    Aggregate analytics data for each user.
    Stores comprehensive learning metrics and performance indicators.
    """
    __tablename__ = 'learning_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Time tracking metrics
    total_study_time = db.Column(db.Integer, default=0, comment='Total study time in minutes')
    average_session_duration = db.Column(db.Float, default=0.0, comment='Average session duration in minutes')
    longest_streak = db.Column(db.Integer, default=0, comment='Longest consecutive days streak')
    current_streak = db.Column(db.Integer, default=0, comment='Current consecutive days streak')
    last_activity_date = db.Column(db.DateTime, comment='Last activity timestamp')
    
    # Performance metrics
    overall_accuracy = db.Column(db.Float, default=0.0, comment='Overall accuracy percentage (0-100)')
    current_level = db.Column(db.String(10), default='A1', comment='Current CEFR level (A1-C2)')
    level_progress = db.Column(db.Float, default=0.0, comment='Progress within current level (0-100)')
    
    # Skill-specific proficiency levels (0-100)
    listening_proficiency = db.Column(db.Float, default=0.0)
    speaking_proficiency = db.Column(db.Float, default=0.0)
    reading_proficiency = db.Column(db.Float, default=0.0)
    writing_proficiency = db.Column(db.Float, default=0.0)
    grammar_proficiency = db.Column(db.Float, default=0.0)
    vocabulary_proficiency = db.Column(db.Float, default=0.0)
    
    # Learning velocity metrics
    weekly_velocity = db.Column(db.Float, default=0.0, comment='Points gained per week')
    monthly_velocity = db.Column(db.Float, default=0.0, comment='Points gained per month')
    acceleration = db.Column(db.Float, default=0.0, comment='Change in velocity (acceleration)')
    
    # Activity counts
    total_activities_completed = db.Column(db.Integer, default=0)
    total_assessments_taken = db.Column(db.Integer, default=0)
    total_vocabulary_learned = db.Column(db.Integer, default=0)
    
    # Predictions
    predicted_next_level_date = db.Column(db.DateTime, comment='Predicted date to reach next level')
    predicted_confidence = db.Column(db.Float, comment='Prediction confidence (0-1)')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('analytics', uselist=False))
    
    def __repr__(self):
        return f'<LearningAnalytics user_id={self.user_id} level={self.current_level}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'time_tracking': {
                'total_study_time': self.total_study_time,
                'average_session_duration': round(self.average_session_duration, 1),
                'longest_streak': self.longest_streak,
                'current_streak': self.current_streak,
                'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None
            },
            'performance': {
                'overall_accuracy': round(self.overall_accuracy, 1),
                'current_level': self.current_level,
                'level_progress': round(self.level_progress, 1)
            },
            'skills': {
                'listening': round(self.listening_proficiency, 1),
                'speaking': round(self.speaking_proficiency, 1),
                'reading': round(self.reading_proficiency, 1),
                'writing': round(self.writing_proficiency, 1),
                'grammar': round(self.grammar_proficiency, 1),
                'vocabulary': round(self.vocabulary_proficiency, 1)
            },
            'velocity': {
                'weekly': round(self.weekly_velocity, 1),
                'monthly': round(self.monthly_velocity, 1),
                'acceleration': round(self.acceleration, 2)
            },
            'activity_counts': {
                'activities_completed': self.total_activities_completed,
                'assessments_taken': self.total_assessments_taken,
                'vocabulary_learned': self.total_vocabulary_learned
            },
            'predictions': {
                'next_level_date': self.predicted_next_level_date.isoformat() if self.predicted_next_level_date else None,
                'confidence': round(self.predicted_confidence, 2) if self.predicted_confidence else None
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class WeeklyReport(db.Model):
    """
    Weekly learning summary reports with AI-generated insights.
    Generated automatically at the end of each week.
    """
    __tablename__ = 'weekly_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Report period
    week_start = db.Column(db.DateTime, nullable=False, comment='Start of week (Monday)')
    week_end = db.Column(db.DateTime, nullable=False, comment='End of week (Sunday)')
    week_number = db.Column(db.Integer, comment='ISO week number')
    year = db.Column(db.Integer, comment='Year')
    
    # Summary metrics
    study_time_minutes = db.Column(db.Integer, default=0)
    activities_completed = db.Column(db.Integer, default=0)
    assessments_taken = db.Column(db.Integer, default=0)
    vocabulary_learned = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    
    # Skill improvements (delta from previous week)
    listening_improvement = db.Column(db.Float, default=0.0)
    speaking_improvement = db.Column(db.Float, default=0.0)
    reading_improvement = db.Column(db.Float, default=0.0)
    writing_improvement = db.Column(db.Float, default=0.0)
    grammar_improvement = db.Column(db.Float, default=0.0)
    vocabulary_improvement = db.Column(db.Float, default=0.0)
    
    # Achievements
    achievements_unlocked = db.Column(db.JSON, comment='List of achievement IDs')
    new_level_reached = db.Column(db.Boolean, default=False)
    milestones_achieved = db.Column(db.JSON, comment='List of milestone descriptions')
    
    # AI-generated insights
    ai_insights = db.Column(db.Text, comment='AI-generated summary and insights')
    strengths = db.Column(db.JSON, comment='Top 3 strengths this week')
    weaknesses = db.Column(db.JSON, comment='Top 3 areas needing improvement')
    recommendations = db.Column(db.JSON, comment='Personalized recommendations')
    
    # Week quality metrics
    consistency_score = db.Column(db.Float, comment='Consistency score (0-100)')
    engagement_score = db.Column(db.Float, comment='Engagement score (0-100)')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('weekly_reports', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_weekly_reports_user_week', 'user_id', 'week_start'),
        db.UniqueConstraint('user_id', 'week_start', name='unique_user_week'),
    )
    
    def __repr__(self):
        return f'<WeeklyReport user_id={self.user_id} week={self.week_start.date()}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'period': {
                'week_start': self.week_start.isoformat(),
                'week_end': self.week_end.isoformat(),
                'week_number': self.week_number,
                'year': self.year
            },
            'summary': {
                'study_time_minutes': self.study_time_minutes,
                'activities_completed': self.activities_completed,
                'assessments_taken': self.assessments_taken,
                'vocabulary_learned': self.vocabulary_learned,
                'points_earned': self.points_earned
            },
            'improvements': {
                'listening': round(self.listening_improvement, 1),
                'speaking': round(self.speaking_improvement, 1),
                'reading': round(self.reading_improvement, 1),
                'writing': round(self.writing_improvement, 1),
                'grammar': round(self.grammar_improvement, 1),
                'vocabulary': round(self.vocabulary_improvement, 1)
            },
            'achievements': {
                'unlocked': self.achievements_unlocked or [],
                'new_level_reached': self.new_level_reached,
                'milestones': self.milestones_achieved or []
            },
            'insights': {
                'ai_summary': self.ai_insights,
                'strengths': self.strengths or [],
                'weaknesses': self.weaknesses or [],
                'recommendations': self.recommendations or []
            },
            'quality': {
                'consistency_score': round(self.consistency_score, 1) if self.consistency_score else None,
                'engagement_score': round(self.engagement_score, 1) if self.engagement_score else None
            },
            'created_at': self.created_at.isoformat()
        }


class ProgressSnapshot(db.Model):
    """
    Daily snapshots of user progress for trend analysis.
    Created automatically once per day.
    """
    __tablename__ = 'progress_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    snapshot_date = db.Column(db.Date, nullable=False, comment='Date of snapshot')
    
    # Proficiency levels at snapshot time (0-100)
    listening = db.Column(db.Float, default=0.0)
    speaking = db.Column(db.Float, default=0.0)
    reading = db.Column(db.Float, default=0.0)
    writing = db.Column(db.Float, default=0.0)
    grammar = db.Column(db.Float, default=0.0)
    vocabulary = db.Column(db.Float, default=0.0)
    
    # Overall metrics
    overall_level = db.Column(db.String(10), comment='CEFR level at snapshot')
    total_points = db.Column(db.Integer, default=0, comment='Total points at snapshot')
    study_time_today = db.Column(db.Integer, default=0, comment='Study time on this day (minutes)')
    activities_today = db.Column(db.Integer, default=0, comment='Activities completed on this day')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('progress_snapshots', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_snapshots_user_date', 'user_id', 'snapshot_date'),
        db.UniqueConstraint('user_id', 'snapshot_date', name='unique_user_date'),
    )
    
    def __repr__(self):
        return f'<ProgressSnapshot user_id={self.user_id} date={self.snapshot_date}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'snapshot_date': self.snapshot_date.isoformat(),
            'skills': {
                'listening': round(self.listening, 1),
                'speaking': round(self.speaking, 1),
                'reading': round(self.reading, 1),
                'writing': round(self.writing, 1),
                'grammar': round(self.grammar, 1),
                'vocabulary': round(self.vocabulary, 1)
            },
            'overall': {
                'level': self.overall_level,
                'total_points': self.total_points
            },
            'daily_activity': {
                'study_time_minutes': self.study_time_today,
                'activities_completed': self.activities_today
            },
            'created_at': self.created_at.isoformat()
        }


class StudySession(db.Model):
    """
    Individual study session tracking for detailed analytics.
    """
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session timing
    session_start = db.Column(db.DateTime, nullable=False)
    session_end = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, comment='Session duration in minutes')
    
    # Activities during session
    activities_completed = db.Column(db.Integer, default=0)
    activity_ids = db.Column(db.JSON, comment='List of activity IDs completed')
    activity_types = db.Column(db.JSON, comment='Types of activities completed')
    
    # Performance during session
    average_accuracy = db.Column(db.Float, comment='Average accuracy in session (0-100)')
    points_earned = db.Column(db.Integer, default=0)
    
    # Session quality metrics
    focus_score = db.Column(db.Float, comment='Focus score based on time between actions (0-1)')
    engagement_score = db.Column(db.Float, comment='Engagement score (0-1)')
    completion_rate = db.Column(db.Float, comment='Activity completion rate (0-1)')
    
    # Session context
    device_type = db.Column(db.String(50), comment='Device used (mobile/tablet/desktop)')
    session_type = db.Column(db.String(50), comment='Type of session (practice/assessment/review)')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('study_sessions', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_sessions_user_start', 'user_id', 'session_start'),
    )
    
    def __repr__(self):
        return f'<StudySession user_id={self.user_id} start={self.session_start}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timing': {
                'session_start': self.session_start.isoformat(),
                'session_end': self.session_end.isoformat() if self.session_end else None,
                'duration_minutes': self.duration_minutes
            },
            'activities': {
                'completed': self.activities_completed,
                'activity_ids': self.activity_ids or [],
                'activity_types': self.activity_types or []
            },
            'performance': {
                'average_accuracy': round(self.average_accuracy, 1) if self.average_accuracy else None,
                'points_earned': self.points_earned
            },
            'quality': {
                'focus_score': round(self.focus_score, 2) if self.focus_score else None,
                'engagement_score': round(self.engagement_score, 2) if self.engagement_score else None,
                'completion_rate': round(self.completion_rate, 2) if self.completion_rate else None
            },
            'context': {
                'device_type': self.device_type,
                'session_type': self.session_type
            },
            'created_at': self.created_at.isoformat()
        }


class ComparisonMetric(db.Model):
    """
    Anonymized peer comparison data for benchmarking.
    Aggregated statistics for each level and metric.
    """
    __tablename__ = 'comparison_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Cohort definition
    level = db.Column(db.String(10), nullable=False, comment='CEFR level (A1-C2)')
    metric_name = db.Column(db.String(100), nullable=False, comment='Name of metric')
    metric_category = db.Column(db.String(50), comment='Category (skill/time/performance)')
    
    # Statistical data
    mean_value = db.Column(db.Float, comment='Mean value')
    median_value = db.Column(db.Float, comment='Median value')
    std_deviation = db.Column(db.Float, comment='Standard deviation')
    
    # Percentiles
    percentile_10 = db.Column(db.Float)
    percentile_25 = db.Column(db.Float)
    percentile_50 = db.Column(db.Float)
    percentile_75 = db.Column(db.Float)
    percentile_90 = db.Column(db.Float)
    percentile_95 = db.Column(db.Float)
    
    # Data metadata
    sample_size = db.Column(db.Integer, comment='Number of users in sample')
    min_value = db.Column(db.Float, comment='Minimum value')
    max_value = db.Column(db.Float, comment='Maximum value')
    
    # Data freshness
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('level', 'metric_name', name='unique_level_metric'),
        db.Index('idx_comparison_level_metric', 'level', 'metric_name'),
    )
    
    def __repr__(self):
        return f'<ComparisonMetric level={self.level} metric={self.metric_name}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'cohort': {
                'level': self.level,
                'metric_name': self.metric_name,
                'metric_category': self.metric_category,
                'sample_size': self.sample_size
            },
            'statistics': {
                'mean': round(self.mean_value, 2) if self.mean_value else None,
                'median': round(self.median_value, 2) if self.median_value else None,
                'std_deviation': round(self.std_deviation, 2) if self.std_deviation else None,
                'min': round(self.min_value, 2) if self.min_value else None,
                'max': round(self.max_value, 2) if self.max_value else None
            },
            'percentiles': {
                'p10': round(self.percentile_10, 2) if self.percentile_10 else None,
                'p25': round(self.percentile_25, 2) if self.percentile_25 else None,
                'p50': round(self.percentile_50, 2) if self.percentile_50 else None,
                'p75': round(self.percentile_75, 2) if self.percentile_75 else None,
                'p90': round(self.percentile_90, 2) if self.percentile_90 else None,
                'p95': round(self.percentile_95, 2) if self.percentile_95 else None
            },
            'last_updated': self.last_updated.isoformat()
        }


class InsightData(db.Model):
    """
    AI-generated personalized insights and recommendations.
    """
    __tablename__ = 'insight_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Insight classification
    insight_type = db.Column(db.String(50), nullable=False, comment='Type: strength/weakness/recommendation/prediction')
    category = db.Column(db.String(50), comment='Category: listening/speaking/reading/writing/grammar/vocabulary')
    subcategory = db.Column(db.String(50), comment='Subcategory for detailed classification')
    
    # Insight content
    title = db.Column(db.String(200), nullable=False, comment='Short title')
    description = db.Column(db.Text, comment='Detailed description')
    priority = db.Column(db.String(20), default='medium', comment='Priority: high/medium/low')
    
    # Supporting data
    evidence = db.Column(db.JSON, comment='Data points supporting this insight')
    confidence = db.Column(db.Float, comment='AI confidence score (0-1)')
    impact_score = db.Column(db.Float, comment='Potential impact if acted upon (0-1)')
    
    # Actionability
    action_items = db.Column(db.JSON, comment='Suggested next steps')
    expected_impact = db.Column(db.String(200), comment='Expected outcome if acted upon')
    difficulty = db.Column(db.String(20), comment='Implementation difficulty: easy/medium/hard')
    
    # Lifecycle
    is_active = db.Column(db.Boolean, default=True)
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, comment='Expiration date for time-sensitive insights')
    
    # Relationships
    user = db.relationship('User', backref=db.backref('insights', lazy='dynamic'))
    
    __table_args__ = (
        db.Index('idx_insights_user_type', 'user_id', 'insight_type', 'is_active'),
    )
    
    def __repr__(self):
        return f'<InsightData user_id={self.user_id} type={self.insight_type}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'classification': {
                'type': self.insight_type,
                'category': self.category,
                'subcategory': self.subcategory,
                'priority': self.priority
            },
            'content': {
                'title': self.title,
                'description': self.description,
                'confidence': round(self.confidence, 2) if self.confidence else None,
                'impact_score': round(self.impact_score, 2) if self.impact_score else None
            },
            'evidence': self.evidence or {},
            'actions': {
                'action_items': self.action_items or [],
                'expected_impact': self.expected_impact,
                'difficulty': self.difficulty
            },
            'status': {
                'is_active': self.is_active,
                'is_acknowledged': self.is_acknowledged,
                'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
            },
            'timestamps': {
                'created_at': self.created_at.isoformat(),
                'expires_at': self.expires_at.isoformat() if self.expires_at else None
            }
        }
