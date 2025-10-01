from .user import db
from datetime import datetime

class AssessmentQuestionResponse(db.Model):
    """
    Detailed tracking of individual question responses in assessments.
    Provides granular analytics for each question attempt.
    """
    __tablename__ = 'assessment_question_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('proficiency_assessments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.String(50), nullable=False)  # Unique identifier for the question
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30))  # multiple_choice, fill_blank, essay, etc.
    correct_answer = db.Column(db.Text)
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean, nullable=False)
    time_spent_seconds = db.Column(db.Integer, default=0)
    confidence_level = db.Column(db.Integer)  # 1-5 scale
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    skill_area = db.Column(db.String(50))  # vocabulary, grammar, reading, etc.
    points_earned = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    attempts_before_correct = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = db.relationship('ProficiencyAssessment', backref='question_responses')
    
    # Indexes will be added via migrations
    
    def __repr__(self):
        return f'<AssessmentQuestionResponse User:{self.user_id} Q:{self.question_id} Correct:{self.is_correct}>'

class ActivityQuestionResponse(db.Model):
    """
    Detailed tracking of individual question responses in activities.
    Similar to assessment responses but for general activities.
    """
    __tablename__ = 'activity_question_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_log_id = db.Column(db.Integer, db.ForeignKey('user_activity_logs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    question_index = db.Column(db.Integer, nullable=False)  # Order within the activity
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30))  # multiple_choice, fill_blank, essay, etc.
    user_answer = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    time_spent_seconds = db.Column(db.Integer, default=0)
    hints_used = db.Column(db.Integer, default=0)
    difficulty_level = db.Column(db.String(20))
    skill_area = db.Column(db.String(50))
    points_earned = db.Column(db.Integer, default=0)
    ai_feedback = db.Column(db.Text)  # AI-generated feedback for this specific question
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activity_log = db.relationship('UserActivityLog', backref='question_responses')
    activity = db.relationship('Activity', backref='question_responses')
    
    # Indexes will be added via migrations
    
    def __repr__(self):
        return f'<ActivityQuestionResponse User:{self.user_id} Activity:{self.activity_id} Q:{self.question_index}>'

class UserAnalytics(db.Model):
    """
    Stores various analytics metrics for users over time.
    Enables tracking of learning progress and performance trends.
    """
    __tablename__ = 'user_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # accuracy, speed, consistency, improvement_rate
    metric_value = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(50))  # quiz, chat, assessment, etc.
    skill_area = db.Column(db.String(50))  # vocabulary, grammar, reading, etc.
    difficulty_level = db.Column(db.String(20))
    session_count = db.Column(db.Integer, default=1)  # Number of sessions included in this metric
    additional_data = db.Column(db.JSON)  # Store additional context data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes will be added via migrations
    
    def __repr__(self):
        return f'<UserAnalytics User:{self.user_id} {self.metric_type}:{self.metric_value}>'

class LearningStreak(db.Model):
    """
    Tracks various types of learning streaks for gamification and motivation.
    """
    __tablename__ = 'learning_streaks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    streak_type = db.Column(db.String(30), nullable=False)  # daily, weekly, activity_specific, skill_specific
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    streak_start_date = db.Column(db.Date)
    activity_type = db.Column(db.String(50))  # For activity-specific streaks
    skill_area = db.Column(db.String(50))  # For skill-specific streaks
    milestone_reached = db.Column(db.JSON)  # Track milestone achievements
    is_active = db.Column(db.Boolean, default=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint for streak types per user
    __table_args__ = (
        db.UniqueConstraint('user_id', 'streak_type', 'activity_type', 'skill_area', 
                          name='unique_user_streak'),
    )
    
    def __repr__(self):
        return f'<LearningStreak User:{self.user_id} {self.streak_type}:{self.current_streak}>'

class AIGeneratedContent(db.Model):
    """
    Tracks AI-generated content for reuse, analytics, and quality improvement.
    """
    __tablename__ = 'ai_generated_content'
    
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)  # question, feedback, explanation, activity
    content_data = db.Column(db.JSON, nullable=False)  # The actual generated content
    generation_parameters = db.Column(db.JSON)  # Parameters used for generation
    content_hash = db.Column(db.String(64))  # Hash for deduplication
    usage_count = db.Column(db.Integer, default=0)
    effectiveness_score = db.Column(db.Float)  # Based on user performance
    user_ratings = db.Column(db.JSON)  # User feedback on content quality
    difficulty_level = db.Column(db.String(20))
    skill_area = db.Column(db.String(50))
    language_pair = db.Column(db.String(20), default='telugu-english')
    is_approved = db.Column(db.Boolean, default=False)  # Manual approval for quality content
    created_by_service = db.Column(db.String(50))  # Which service generated this
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    
    # Indexes will be added via migrations
    
    def __repr__(self):
        return f'<AIGeneratedContent {self.content_type} Usage:{self.usage_count}>'

class UserLearningTimeline(db.Model):
    """
    Comprehensive timeline of user's learning journey across all activities.
    """
    __tablename__ = 'user_learning_timeline'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # activity_completed, assessment_taken, badge_earned, streak_achieved
    event_subtype = db.Column(db.String(50))  # specific type like quiz_completed, vocabulary_mastered
    event_data = db.Column(db.JSON)  # Detailed event information
    related_id = db.Column(db.Integer)  # ID of related record (activity_id, assessment_id, etc.)
    related_type = db.Column(db.String(30))  # Type of related record
    proficiency_change = db.Column(db.Float)  # Change in proficiency level
    points_earned = db.Column(db.Integer, default=0)
    skill_areas_affected = db.Column(db.JSON)  # List of skill areas impacted
    difficulty_level = db.Column(db.String(20))
    performance_score = db.Column(db.Float)  # Score for this event
    time_spent_minutes = db.Column(db.Integer)
    milestone_achieved = db.Column(db.String(100))  # Any milestone reached
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes will be added via migrations
    
    def __repr__(self):
        return f'<UserLearningTimeline User:{self.user_id} {self.event_type}>'

class PerformanceTrend(db.Model):
    """
    Aggregated performance trends for efficient dashboard queries.
    """
    __tablename__ = 'performance_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trend_period = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Performance metrics
    activities_completed = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    total_time_minutes = db.Column(db.Integer, default=0)
    accuracy_rate = db.Column(db.Float, default=0.0)
    improvement_rate = db.Column(db.Float, default=0.0)  # Compared to previous period
    
    # Skill breakdown
    vocabulary_progress = db.Column(db.Float, default=0.0)
    grammar_progress = db.Column(db.Float, default=0.0)
    reading_progress = db.Column(db.Float, default=0.0)
    conversation_progress = db.Column(db.Float, default=0.0)
    
    # Engagement metrics
    streak_count = db.Column(db.Integer, default=0)
    badges_earned = db.Column(db.Integer, default=0)
    challenges_completed = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint for periods
    __table_args__ = (
        db.UniqueConstraint('user_id', 'trend_period', 'period_start', 
                          name='unique_user_trend_period'),
    )
    
    def __repr__(self):
        return f'<PerformanceTrend User:{self.user_id} {self.trend_period} {self.period_start}>'