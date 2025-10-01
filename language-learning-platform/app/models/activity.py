
from .user import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # quiz, flashcard, reading, writing, role_play, image_recognition
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)  # Enhanced description
    content = db.Column(db.JSON, nullable=False)  # Stores the AI-generated JSON content
    difficulty_level = db.Column(db.String(20), default='beginner')
    order_in_path = db.Column(db.Integer, nullable=False)
    estimated_duration_minutes = db.Column(db.Integer, default=10)  # in minutes
    points_reward = db.Column(db.Integer, default=10)  # points awarded for completion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced adaptive learning fields
    skill_area = db.Column(db.String(50))  # vocabulary, grammar, reading, writing, listening, speaking
    concept_focus = db.Column(db.String(100))  # Specific concept being taught
    is_adaptive = db.Column(db.Boolean, default=False)  # Whether this is an adaptive activity
    prerequisite_concepts = db.Column(db.JSON)  # Required concepts to master first
    mastery_threshold = db.Column(db.Float, default=0.8)  # Threshold for concept mastery
    is_validation = db.Column(db.Boolean, default=False)  # Whether this validates mastery
    is_retry = db.Column(db.Boolean, default=False)  # Whether this is a retry activity
    is_reinforcement = db.Column(db.Boolean, default=False)  # Whether this reinforces learning
    parent_activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))  # For retry/reinforcement activities
    
    # AI-generated metadata
    generation_metadata = db.Column(db.JSON)  # Stores AI generation context and parameters
    adaptation_history = db.Column(db.JSON)  # History of how activity has been adapted
    
    # Relationships
    user_logs = db.relationship('UserActivityLog', backref='activity', lazy='dynamic', cascade='all, delete-orphan')
    child_activities = db.relationship('Activity', backref=db.backref('parent_activity', remote_side=[id]))
    
    def __repr__(self):
        return f'<Activity {self.title} ({self.activity_type})>'

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=True)  # For easier queries
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer)  # Score achieved (e.g., 4/5 for quiz)
    max_score = db.Column(db.Integer)  # Maximum possible score
    time_spent_minutes = db.Column(db.Integer)  # Time spent on activity
    user_response = db.Column(db.JSON)  # User's responses/answers
    feedback_provided = db.Column(db.JSON)  # AI feedback if applicable
    is_completed = db.Column(db.Boolean, default=True)
    
    # Enhanced tracking fields
    attempt_number = db.Column(db.Integer, default=1)
    session_id = db.Column(db.String(100))  # Links to performance monitoring session
    skill_area = db.Column(db.String(50))  # For easier querying
    concept_focus = db.Column(db.String(100))  # For concept mastery tracking
    
    # Performance analytics
    accuracy_score = db.Column(db.Float)  # Normalized score (0-1)
    time_efficiency = db.Column(db.Float)  # Accuracy per minute
    hint_count = db.Column(db.Integer, default=0)  # Number of hints used
    error_patterns = db.Column(db.JSON)  # Specific errors made
    struggle_indicators = db.Column(db.JSON)  # Signs of struggle during activity
    
    # Real-time tracking data
    interaction_timeline = db.Column(db.JSON)  # Timeline of user interactions
    difficulty_adjustments = db.Column(db.JSON)  # Dynamic difficulty changes made
    interventions_triggered = db.Column(db.JSON)  # Interventions provided during activity
    
    # Mastery assessment
    mastery_level = db.Column(db.String(20))  # not_started, learning, proficient, mastered
    confidence_score = db.Column(db.Float)  # Confidence in mastery assessment (0-1)
    needs_review = db.Column(db.Boolean, default=False)  # Whether concept needs review
    next_review_date = db.Column(db.DateTime)  # For spaced repetition
    
    def __repr__(self):
        return f'<UserActivityLog {self.user.username} - {self.activity.title}>'


class ConceptMastery(db.Model):
    """
    Track user mastery of specific concepts across different skill areas.
    """
    __tablename__ = 'concept_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_area = db.Column(db.String(50), nullable=False)  # vocabulary, grammar, etc.
    concept = db.Column(db.String(100), nullable=False)  # Specific concept
    proficiency_level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    
    # Mastery tracking
    mastery_status = db.Column(db.String(20), default='not_started')  # not_started, learning, proficient, mastered
    confidence_score = db.Column(db.Float, default=0.0)  # 0-1 confidence in mastery
    average_score = db.Column(db.Float, default=0.0)  # Average performance score
    consistency_score = db.Column(db.Float, default=0.0)  # Consistency of performance
    
    # Activity tracking
    activities_completed = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    successful_attempts = db.Column(db.Integer, default=0)
    
    # Temporal tracking
    first_attempt_date = db.Column(db.DateTime)
    last_activity_date = db.Column(db.DateTime)
    mastery_achieved_date = db.Column(db.DateTime)
    
    # Spaced repetition
    next_review_date = db.Column(db.DateTime)
    review_interval_hours = db.Column(db.Integer, default=24)
    review_count = db.Column(db.Integer, default=0)
    
    # Performance history
    performance_history = db.Column(db.JSON)  # Detailed performance over time
    learning_difficulties = db.Column(db.JSON)  # Identified learning challenges
    intervention_history = db.Column(db.JSON)  # Interventions applied
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_area', 'concept', 'proficiency_level'),)
    
    def __repr__(self):
        return f'<ConceptMastery {self.user.username} - {self.skill_area}:{self.concept}>'


class AdaptiveLearningSession(db.Model):
    """
    Track real-time learning sessions for performance monitoring and adaptation.
    """
    __tablename__ = 'adaptive_learning_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'))
    
    # Session timing
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_duration_minutes = db.Column(db.Float)
    
    # Real-time performance tracking
    interaction_count = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    incorrect_answers = db.Column(db.Integer, default=0)
    hint_requests = db.Column(db.Integer, default=0)
    
    # Performance metrics
    final_accuracy = db.Column(db.Float)
    average_response_time = db.Column(db.Float)
    time_efficiency = db.Column(db.Float)  # Accuracy per minute
    consistency_score = db.Column(db.Float)
    
    # Adaptive features used
    difficulty_adjustments = db.Column(db.JSON)  # Dynamic difficulty changes
    interventions_provided = db.Column(db.JSON)  # Real-time interventions
    content_adaptations = db.Column(db.JSON)  # Content modifications made
    
    # Learning analytics
    error_patterns = db.Column(db.JSON)  # Patterns in mistakes
    struggle_indicators = db.Column(db.JSON)  # Signs of learning difficulties
    engagement_metrics = db.Column(db.JSON)  # Attention and engagement data
    
    # Session outcomes
    session_status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    completion_reason = db.Column(db.String(50))  # natural, break_suggested, time_limit, etc.
    user_satisfaction_rating = db.Column(db.Integer)  # 1-5 rating if provided
    generated_recommendations = db.Column(db.JSON)  # Next session recommendations
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdaptiveLearningSession {self.session_id} - {self.user.username}>'


class AdaptiveLearningPathProgress(db.Model):
    """
    Track detailed progress through adaptive learning paths.
    """
    __tablename__ = 'adaptive_learning_path_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    
    # Path progression
    current_skill_focus = db.Column(db.String(50))  # Current primary skill being worked on
    current_concept = db.Column(db.String(100))  # Current concept within skill
    current_difficulty = db.Column(db.String(20))  # Current difficulty level
    
    # Overall progress metrics
    total_concepts = db.Column(db.Integer, default=0)
    concepts_mastered = db.Column(db.Integer, default=0)
    concepts_proficient = db.Column(db.Integer, default=0)
    concepts_learning = db.Column(db.Integer, default=0)
    concepts_struggling = db.Column(db.Integer, default=0)
    
    # Skill-specific progress
    skill_progress = db.Column(db.JSON)  # Progress breakdown by skill area
    mastery_timeline = db.Column(db.JSON)  # Timeline of concept mastery
    
    # Adaptive features
    path_adaptations = db.Column(db.JSON)  # How path has been adapted over time
    difficulty_adjustments = db.Column(db.JSON)  # Difficulty changes made
    focus_shifts = db.Column(db.JSON)  # Changes in skill focus based on performance
    
    # Learning analytics
    average_performance = db.Column(db.Float)
    learning_velocity = db.Column(db.Float)  # Rate of concept mastery
    retention_rate = db.Column(db.Float)  # How well concepts are retained
    
    # Engagement and motivation
    session_count = db.Column(db.Integer, default=0)
    total_time_spent_hours = db.Column(db.Float, default=0.0)
    longest_streak_days = db.Column(db.Integer, default=0)
    engagement_score = db.Column(db.Float)  # Overall engagement metric
    
    # Predictive analytics
    estimated_completion_date = db.Column(db.DateTime)
    predicted_final_level = db.Column(db.String(20))
    confidence_in_prediction = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'learning_path_id'),)
    
    def __repr__(self):
        return f'<AdaptiveLearningPathProgress {self.user.username} - Path {self.learning_path_id}>'
