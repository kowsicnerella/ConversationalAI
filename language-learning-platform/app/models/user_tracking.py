"""
User Data Tracking Models
Complete tracking of all user-generated and AI-generated content for historical review
"""
from datetime import datetime
from app.models import db


class UserAssessmentHistory(db.Model):
    """
    Complete history of all assessments taken by users
    Allows users to review past assessments and track progress
    """
    __tablename__ = "user_assessment_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("proficiency_assessments.id"), nullable=False)
    
    # Assessment metadata
    assessment_type = db.Column(db.String(50), nullable=False)  # comprehensive, quick, adaptive, skill_specific
    skill_area = db.Column(db.String(50))  # For skill-specific assessments
    
    # Questions and responses (stored as JSON for full detail)
    questions = db.Column(db.JSON, nullable=False)  # All questions asked
    user_answers = db.Column(db.JSON, nullable=False)  # All answers provided
    correct_answers = db.Column(db.JSON)  # Correct answers for review
    
    # Results and evaluation
    score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float)  # score/max_score * 100
    proficiency_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    
    # Detailed breakdown
    skill_breakdown = db.Column(db.JSON)  # Performance by skill area
    strengths = db.Column(db.JSON)  # Areas of strength
    weaknesses = db.Column(db.JSON)  # Areas needing improvement
    recommendations = db.Column(db.JSON)  # Personalized recommendations
    
    # AI evaluation
    ai_feedback = db.Column(db.Text)  # Overall AI feedback
    detailed_evaluation = db.Column(db.JSON)  # Question-by-question evaluation
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False)
    duration_seconds = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("assessment_history", lazy="dynamic"))
    assessment = db.relationship("ProficiencyAssessment")
    
    __table_args__ = (
        db.Index('idx_user_type_date', 'user_id', 'assessment_type', 'completed_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'assessment_type': self.assessment_type,
            'skill_area': self.skill_area,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'proficiency_level': self.proficiency_level,
            'skill_breakdown': self.skill_breakdown,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'recommendations': self.recommendations,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat(),
            'duration_seconds': self.duration_seconds,
            'questions_count': len(self.questions) if self.questions else 0
        }


class UserActivityCompletion(db.Model):
    """
    Track all activities completed by users with full details
    """
    __tablename__ = "user_activity_completions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    
    # Activity details
    activity_type = db.Column(db.String(50), nullable=False)  # quiz, flashcard, reading, writing, role_play
    activity_title = db.Column(db.String(200))
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    topic = db.Column(db.String(100))
    
    # Content and responses
    content = db.Column(db.JSON, nullable=False)  # Full activity content
    user_responses = db.Column(db.JSON, nullable=False)  # All user responses
    correct_answers = db.Column(db.JSON)  # Correct answers for reference
    
    # Performance metrics
    score = db.Column(db.Float, nullable=False, default=0.0)
    max_score = db.Column(db.Float, nullable=False)
    percentage = db.Column(db.Float)
    attempts_count = db.Column(db.Integer, default=1)  # Number of attempts
    
    # AI feedback
    ai_feedback = db.Column(db.Text)  # Overall feedback
    item_feedback = db.Column(db.JSON)  # Feedback for each item/question
    suggestions = db.Column(db.JSON)  # Improvement suggestions
    
    # Engagement metrics
    time_spent_seconds = db.Column(db.Integer)
    items_completed = db.Column(db.Integer)
    items_correct = db.Column(db.Integer)
    
    # Status tracking
    status = db.Column(db.String(20), default='completed')  # started, paused, completed
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime)
    
    # XP and rewards
    xp_earned = db.Column(db.Integer, default=0)
    badges_earned = db.Column(db.JSON)  # List of badge IDs earned
    
    # Relationships
    user = db.relationship("User", backref=db.backref("activity_completions", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_type_completed', 'user_id', 'activity_type', 'completed_at'),
        db.Index('idx_user_activity', 'user_id', 'activity_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'activity_title': self.activity_title,
            'difficulty_level': self.difficulty_level,
            'topic': self.topic,
            'score': self.score,
            'max_score': self.max_score,
            'percentage': self.percentage,
            'attempts_count': self.attempts_count,
            'time_spent_seconds': self.time_spent_seconds,
            'xp_earned': self.xp_earned,
            'completed_at': self.completed_at.isoformat(),
            'status': self.status
        }


class UserPracticeSession(db.Model):
    """
    Track all practice sessions with questions and feedback
    """
    __tablename__ = "user_practice_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    # Session details
    session_type = db.Column(db.String(50), nullable=False)  # grammar, vocabulary, pronunciation, writing
    skill_focus = db.Column(db.String(50))  # Specific skill being practiced
    difficulty_level = db.Column(db.String(20))
    topic = db.Column(db.String(100))
    
    # Questions and responses
    questions = db.Column(db.JSON, nullable=False)  # All questions in session
    user_answers = db.Column(db.JSON, nullable=False)  # User's answers
    correct_answers = db.Column(db.JSON)  # Correct answers
    
    # Performance
    score = db.Column(db.Float, default=0.0)
    max_score = db.Column(db.Float, nullable=False)
    accuracy_percentage = db.Column(db.Float)
    
    # AI feedback
    overall_feedback = db.Column(db.Text)
    question_feedback = db.Column(db.JSON)  # Feedback for each question
    strengths_identified = db.Column(db.JSON)
    areas_for_improvement = db.Column(db.JSON)
    next_steps = db.Column(db.JSON)  # Recommended next practice topics
    
    # Session metrics
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers_count = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer)
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Progress tracking
    xp_earned = db.Column(db.Integer, default=0)
    mastery_gain = db.Column(db.Float)  # Improvement in mastery level
    
    # Relationships
    user = db.relationship("User", backref=db.backref("practice_sessions", lazy="dynamic"))
    
    __table_args__ = (
        db.Index('idx_user_session_type', 'user_id', 'session_type', 'completed_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_type': self.session_type,
            'skill_focus': self.skill_focus,
            'difficulty_level': self.difficulty_level,
            'topic': self.topic,
            'score': self.score,
            'max_score': self.max_score,
            'accuracy_percentage': self.accuracy_percentage,
            'total_questions': self.total_questions,
            'correct_answers_count': self.correct_answers_count,
            'time_spent_seconds': self.time_spent_seconds,
            'xp_earned': self.xp_earned,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat()
        }


class UserLessonProgress(db.Model):
    """
    Track user progress through lessons and learning paths
    """
    __tablename__ = "user_lesson_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"))
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"))
    
    # Lesson details
    lesson_title = db.Column(db.String(200), nullable=False)
    lesson_content = db.Column(db.JSON)  # Store lesson content for historical review
    lesson_type = db.Column(db.String(50))  # video, reading, interactive, quiz
    difficulty_level = db.Column(db.String(20))
    
    # Progress tracking
    status = db.Column(db.String(20), nullable=False)  # not_started, in_progress, completed, reviewed
    progress_percentage = db.Column(db.Float, default=0.0)  # 0-100
    
    # Interaction data
    notes_taken = db.Column(db.Text)  # User's notes
    bookmarks = db.Column(db.JSON)  # Bookmarked sections
    questions_asked = db.Column(db.JSON)  # Questions user asked during lesson
    
    # Comprehension check
    comprehension_score = db.Column(db.Float)
    quiz_results = db.Column(db.JSON)  # If lesson has embedded quiz
    
    # AI insights
    ai_summary = db.Column(db.Text)  # AI-generated lesson summary
    key_takeaways = db.Column(db.JSON)  # Key points learned
    personalized_insights = db.Column(db.JSON)  # Personalized learning insights
    
    # Timing
    started_at = db.Column(db.DateTime)
    last_accessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_spent_seconds = db.Column(db.Integer, default=0)
    
    # Engagement
    revisit_count = db.Column(db.Integer, default=0)  # How many times reviewed
    helpful_rating = db.Column(db.Integer)  # 1-5 user rating
    
    # Relationships
    user = db.relationship("User", backref=db.backref("lesson_progress", lazy="dynamic"))
    learning_path = db.relationship("LearningPath")
    chapter = db.relationship("Chapter")
    
    __table_args__ = (
        db.Index('idx_user_path_status', 'user_id', 'learning_path_id', 'status'),
        db.Index('idx_user_chapter', 'user_id', 'chapter_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'lesson_title': self.lesson_title,
            'lesson_type': self.lesson_type,
            'difficulty_level': self.difficulty_level,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'comprehension_score': self.comprehension_score,
            'time_spent_seconds': self.time_spent_seconds,
            'revisit_count': self.revisit_count,
            'helpful_rating': self.helpful_rating,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed_at': self.last_accessed_at.isoformat()
        }


class UserConversationHistory(db.Model):
    """
    Extended chat history with AI analysis and learning insights
    """
    __tablename__ = "user_conversation_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("chat_conversations.id"))
    
    # Conversation metadata
    conversation_type = db.Column(db.String(50), nullable=False)  # tutoring, roleplay, casual, practice
    topic = db.Column(db.String(100))
    scenario = db.Column(db.String(200))  # For role-play scenarios
    
    # Full conversation data
    messages = db.Column(db.JSON, nullable=False)  # All messages with timestamps
    message_count = db.Column(db.Integer, default=0)
    user_message_count = db.Column(db.Integer, default=0)
    
    # AI analysis
    grammar_corrections = db.Column(db.JSON)  # Grammar mistakes and corrections
    vocabulary_used = db.Column(db.JSON)  # New vocabulary used
    fluency_score = db.Column(db.Float)  # 0-100 fluency rating
    coherence_score = db.Column(db.Float)  # 0-100 coherence rating
    
    # Learning insights
    skills_practiced = db.Column(db.JSON)  # Skills demonstrated
    learning_points = db.Column(db.JSON)  # Key learning moments
    ai_recommendations = db.Column(db.JSON)  # Follow-up recommendations
    
    # Performance metrics
    response_times = db.Column(db.JSON)  # Time taken to respond
    avg_response_time_seconds = db.Column(db.Float)
    engagement_score = db.Column(db.Float)  # 0-100 engagement rating
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds = db.Column(db.Integer)
    
    # Progress tracking
    xp_earned = db.Column(db.Integer, default=0)
    vocabulary_added = db.Column(db.Integer, default=0)  # New words added to user's vocabulary
    
    # Relationships
    user = db.relationship("User", backref=db.backref("conversation_history", lazy="dynamic"))
    conversation = db.relationship("ChatConversation")
    
    __table_args__ = (
        db.Index('idx_user_conv_type', 'user_id', 'conversation_type', 'started_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_type': self.conversation_type,
            'topic': self.topic,
            'scenario': self.scenario,
            'message_count': self.message_count,
            'fluency_score': self.fluency_score,
            'coherence_score': self.coherence_score,
            'duration_seconds': self.duration_seconds,
            'xp_earned': self.xp_earned,
            'vocabulary_added': self.vocabulary_added,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat()
        }
