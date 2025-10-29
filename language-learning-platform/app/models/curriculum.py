"""
Curriculum Framework Models for AI-Personalized Learning
Based on CEFR (Common European Framework of Reference) standards
"""
from .user import db
from datetime import datetime, date


class CurriculumLevel(db.Model):
    """
    CEFR-based curriculum levels (A1 to C2)
    Represents the structured framework for language learning progression
    """
    __tablename__ = "curriculum_levels"
    
    id = db.Column(db.Integer, primary_key=True)
    cefr_level = db.Column(db.String(2), unique=True, nullable=False)  # A1, A2, B1, B2, C1, C2
    level_name = db.Column(db.String(50), nullable=False)  # Beginner, Elementary, Intermediate, etc.
    description = db.Column(db.Text)
    
    # Requirements for this level
    vocabulary_range_min = db.Column(db.Integer)  # Minimum words needed
    vocabulary_range_max = db.Column(db.Integer)  # Target vocabulary size
    grammar_concepts = db.Column(db.JSON)  # List of grammar concepts to master
    functional_skills = db.Column(db.JSON)  # Can-do statements (e.g., "Can introduce yourself")
    
    # Progression metrics
    estimated_hours = db.Column(db.Integer)  # Estimated hours to complete level
    prerequisite_level_id = db.Column(db.Integer, db.ForeignKey('curriculum_levels.id'), nullable=True)
    
    # NOTE: Relationship to LearningNode removed to avoid conflicts with Phase 3
    # Use direct queries instead: LearningNode.query.filter_by(curriculum_level_id=self.id).all()
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CurriculumLevel {self.cefr_level} - {self.level_name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'cefr_level': self.cefr_level,
            'level_name': self.level_name,
            'description': self.description,
            'vocabulary_range': {
                'min': self.vocabulary_range_min,
                'max': self.vocabulary_range_max
            },
            'grammar_concepts': self.grammar_concepts or [],
            'functional_skills': self.functional_skills or [],
            'estimated_hours': self.estimated_hours
        }


class LearningNode(db.Model):
    """
    Atomic learning unit - the smallest teachable concept
    Each node represents a specific concept or skill to be learned
    """
    __tablename__ = "learning_nodes"
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(100), unique=True, nullable=False)  # e.g., "A1_VOCAB_GREETINGS"
    
    # Classification
    curriculum_level_id = db.Column(db.Integer, db.ForeignKey('curriculum_levels.id'), nullable=False)
    skill_domain = db.Column(db.String(50), nullable=False)  # vocabulary, grammar, listening, speaking, reading, writing
    concept_name = db.Column(db.String(200), nullable=False)  # e.g., "Basic Greetings and Introductions"
    
    # Learning Design
    learning_objectives = db.Column(db.JSON)  # What user should be able to do after completing
    activity_templates = db.Column(db.JSON)  # Types of activities suitable for this concept
    example_content = db.Column(db.JSON)  # Example content/vocabulary for AI generation guidance
    
    # Difficulty & Timing
    difficulty_range_min = db.Column(db.Float, default=0.0)  # 0-1 scale, minimum difficulty
    difficulty_range_max = db.Column(db.Float, default=1.0)  # 0-1 scale, maximum difficulty
    estimated_time_minutes = db.Column(db.Integer, default=15)  # Estimated time to complete
    
    # Mastery
    mastery_threshold = db.Column(db.Float, default=0.8)  # Score threshold to consider mastered (0-1)
    
    # Dependencies
    prerequisites = db.Column(db.JSON)  # List of node_ids that must be completed first
    
    # Metadata
    is_core = db.Column(db.Boolean, default=True)  # Core (required) vs optional node
    tags = db.Column(db.JSON)  # Tags for search/filtering (e.g., ['daily_life', 'conversation'])
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningNode {self.node_id} - {self.concept_name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'curriculum_level_id': self.curriculum_level_id,
            'skill_domain': self.skill_domain,
            'concept_name': self.concept_name,
            'learning_objectives': self.learning_objectives or [],
            'activity_templates': self.activity_templates or [],
            'difficulty_range': {
                'min': self.difficulty_range_min,
                'max': self.difficulty_range_max
            },
            'estimated_time_minutes': self.estimated_time_minutes,
            'mastery_threshold': self.mastery_threshold,
            'prerequisites': self.prerequisites or [],
            'is_core': self.is_core,
            'tags': self.tags or []
        }


class UserLearningPathProgress(db.Model):
    """
    Track user's progress through the curriculum
    Stores individual learning journey and preferences
    """
    __tablename__ = "user_learning_path_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Current Position
    current_level = db.Column(db.String(2), nullable=False, default='A1')  # A1, A2, B1, B2, C1, C2
    current_node_id = db.Column(db.String(100))  # Currently working on this node
    
    # Goals
    target_level = db.Column(db.String(2), default='B2')  # User's goal level
    target_date = db.Column(db.Date)  # Target completion date
    
    # Learning Preferences
    learning_style = db.Column(db.String(50), default='mixed')  # visual, auditory, kinesthetic, mixed
    preferred_pace = db.Column(db.String(20), default='medium')  # slow, medium, fast
    preferred_session_length = db.Column(db.Integer, default=20)  # Preferred session length in minutes
    
    # Skill Focus
    skill_priorities = db.Column(db.JSON)  # Which skills to emphasize (e.g., {'speaking': 0.3, 'listening': 0.3})
    weak_areas = db.Column(db.JSON)  # Areas needing improvement (list of skill domains)
    strong_areas = db.Column(db.JSON)  # Areas of strength (list of skill domains)
    current_focus_skill = db.Column(db.String(50))  # Current primary focus
    
    # Progress Metrics
    nodes_completed = db.Column(db.Integer, default=0)
    nodes_in_progress = db.Column(db.Integer, default=0)
    nodes_mastered = db.Column(db.Integer, default=0)
    
    # Learning Analytics
    learning_velocity = db.Column(db.Float)  # Nodes mastered per week
    average_accuracy = db.Column(db.Float)  # Overall accuracy across all activities
    time_invested_hours = db.Column(db.Float, default=0.0)  # Total time spent learning
    
    # Engagement
    last_activity_date = db.Column(db.DateTime)
    longest_streak_days = db.Column(db.Integer, default=0)
    current_streak_days = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserLearningPathProgress User {self.user_id} - {self.current_level}>"
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'current_level': self.current_level,
            'current_node_id': self.current_node_id,
            'target_level': self.target_level,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'learning_style': self.learning_style,
            'preferred_pace': self.preferred_pace,
            'preferred_session_length': self.preferred_session_length,
            'skill_priorities': self.skill_priorities or {},
            'weak_areas': self.weak_areas or [],
            'strong_areas': self.strong_areas or [],
            'current_focus_skill': self.current_focus_skill,
            'progress': {
                'nodes_completed': self.nodes_completed,
                'nodes_in_progress': self.nodes_in_progress,
                'nodes_mastered': self.nodes_mastered,
                'learning_velocity': self.learning_velocity,
                'average_accuracy': self.average_accuracy,
                'time_invested_hours': self.time_invested_hours
            },
            'engagement': {
                'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
                'longest_streak_days': self.longest_streak_days,
                'current_streak_days': self.current_streak_days
            }
        }


class NodeCompletion(db.Model):
    """
    Track completion of individual learning nodes by users
    Records attempts, scores, and mastery status for each node
    """
    __tablename__ = "node_completions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    node_id = db.Column(db.String(100), nullable=False)
    
    # Performance Tracking
    attempts = db.Column(db.Integer, default=0)  # Number of times attempted
    best_score = db.Column(db.Float)  # Best score achieved (0-1 scale)
    average_score = db.Column(db.Float)  # Average score across all attempts
    last_score = db.Column(db.Float)  # Most recent score
    
    # Status
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, mastered
    mastery_level = db.Column(db.Float, default=0.0)  # Current mastery level (0-1 scale)
    
    # Timing
    first_attempt_date = db.Column(db.DateTime)
    last_attempt_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)  # When status became 'completed'
    mastery_date = db.Column(db.DateTime)  # When status became 'mastered'
    
    # Learning Data
    time_spent_minutes = db.Column(db.Integer, default=0)  # Total time spent on this node
    activities_completed = db.Column(db.Integer, default=0)  # Number of activities completed
    mistakes_made = db.Column(db.JSON)  # Common mistakes (for targeted practice)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'node_id', name='unique_user_node'),
    )
    
    def __repr__(self):
        return f"<NodeCompletion User {self.user_id} - Node {self.node_id} - {self.status}>"
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'node_id': self.node_id,
            'performance': {
                'attempts': self.attempts,
                'best_score': self.best_score,
                'average_score': self.average_score,
                'last_score': self.last_score
            },
            'status': self.status,
            'mastery_level': self.mastery_level,
            'timing': {
                'first_attempt': self.first_attempt_date.isoformat() if self.first_attempt_date else None,
                'last_attempt': self.last_attempt_date.isoformat() if self.last_attempt_date else None,
                'completed': self.completion_date.isoformat() if self.completion_date else None,
                'mastered': self.mastery_date.isoformat() if self.mastery_date else None
            },
            'time_spent_minutes': self.time_spent_minutes,
            'activities_completed': self.activities_completed,
            'mistakes_made': self.mistakes_made or []
        }
    
    def update_with_new_attempt(self, score, time_spent_minutes=0):
        """
        Update completion record with a new attempt
        
        Args:
            score: Score achieved (0-1 scale)
            time_spent_minutes: Time spent on this attempt
        """
        from datetime import datetime
        
        # Update attempts
        self.attempts += 1
        self.last_score = score
        self.last_attempt_date = datetime.utcnow()
        
        if self.attempts == 1:
            self.first_attempt_date = datetime.utcnow()
            self.average_score = score
        else:
            # Calculate new average
            self.average_score = ((self.average_score * (self.attempts - 1)) + score) / self.attempts
        
        # Update best score
        if self.best_score is None or score > self.best_score:
            self.best_score = score
        
        # Update time spent
        if self.time_spent_minutes is None:
            self.time_spent_minutes = 0
        self.time_spent_minutes += time_spent_minutes
        
        if self.activities_completed is None:
            self.activities_completed = 0
        self.activities_completed += 1
        
        # Update status based on score
        if score >= 0.9 and self.average_score >= 0.85:
            self.status = 'mastered'
            self.mastery_level = 1.0
            if not self.mastery_date:
                self.mastery_date = datetime.utcnow()
        elif score >= 0.7 and self.average_score >= 0.65:
            self.status = 'completed'
            self.mastery_level = self.average_score
            if not self.completion_date:
                self.completion_date = datetime.utcnow()
        else:
            self.status = 'in_progress'
            self.mastery_level = self.average_score if self.average_score else score
        
        self.updated_at = datetime.utcnow()
