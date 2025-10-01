from .user import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class Chapter(db.Model):
    """
    Model representing a learning chapter in the language learning journey.
    Each chapter contains structured content and tracks user progress.
    """
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    chapter_number = db.Column(db.Integer, nullable=False)  # Sequential ordering
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    topic = db.Column(db.String(100), nullable=False)  # Main topic of the chapter
    subtopics = db.Column(db.JSON)  # List of subtopics covered
    estimated_duration_minutes = db.Column(db.Integer, default=30)
    required_score_to_pass = db.Column(db.Float, default=0.7)  # 70% to pass
    prerequisites = db.Column(db.JSON)  # List of chapter IDs that must be completed first
    content = db.Column(db.JSON)  # Chapter content including initial explanation
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_progress = db.relationship('UserChapterProgress', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    practice_sessions = db.relationship('PracticeSession', backref='chapter', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Chapter {self.chapter_number}: {self.title}>'

class UserChapterProgress(db.Model):
    """
    Tracks user progress through each chapter including scores and completion status.
    """
    __tablename__ = 'user_chapter_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, mastered
    best_score = db.Column(db.Float, default=0.0)  # Best score achieved in this chapter
    average_score = db.Column(db.Float, default=0.0)  # Average score across all attempts
    total_attempts = db.Column(db.Integer, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # User notes for this chapter
    
    # Unique constraint to ensure one progress record per user per chapter
    __table_args__ = (UniqueConstraint('user_id', 'chapter_id', name='unique_user_chapter_progress'),)
    
    def __repr__(self):
        return f'<UserChapterProgress User:{self.user_id} Chapter:{self.chapter_id} Status:{self.status}>'

class PracticeSession(db.Model):
    """
    Individual practice sessions within a chapter with detailed score tracking.
    """
    __tablename__ = 'practice_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    session_type = db.Column(db.String(50), default='practice')  # practice, test, review
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    # Score tracking
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    
    # Session details
    questions_data = db.Column(db.JSON)  # All questions asked with answers
    user_responses = db.Column(db.JSON)  # User's responses
    ai_feedback = db.Column(db.JSON)  # AI feedback for each question
    session_summary = db.Column(db.JSON)  # Overall session summary
    
    # Chat/conversation during practice
    conversation_messages = db.Column(db.JSON)  # Chat messages with AI during practice
    
    is_completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<PracticeSession User:{self.user_id} Chapter:{self.chapter_id} Score:{self.score_percentage}%>'

class UserNotes(db.Model):
    """
    User notes taken during practice sessions and chapters.
    """
    __tablename__ = 'user_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    practice_session_id = db.Column(db.Integer, db.ForeignKey('practice_sessions.id'), nullable=True)
    
    note_content = db.Column(db.Text, nullable=False)
    note_type = db.Column(db.String(50), default='general')  # general, vocabulary, grammar, mistake
    tags = db.Column(db.JSON)  # User-defined tags for organization
    is_important = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserNote User:{self.user_id} Type:{self.note_type}>'

class TestAssessment(db.Model):
    """
    Comprehensive tests that assess user knowledge across multiple chapters.
    """
    __tablename__ = 'test_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # chapter_test, comprehensive_test, placement_test
    chapter_ids = db.Column(db.JSON)  # Chapters being tested
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    
    # Test results
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    score_percentage = db.Column(db.Float)
    grade = db.Column(db.String(10))  # A, B, C, D, F
    
    # Detailed results
    questions_data = db.Column(db.JSON)  # All questions with correct answers
    user_responses = db.Column(db.JSON)  # User's responses
    detailed_analysis = db.Column(db.JSON)  # Per-topic/skill analysis
    recommendations = db.Column(db.JSON)  # AI recommendations based on performance
    
    is_completed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<TestAssessment User:{self.user_id} Type:{self.test_type} Score:{self.score_percentage}%>'

class ChapterDependency(db.Model):
    """
    Manages the dependency graph between chapters for learning path progression.
    """
    __tablename__ = 'chapter_dependencies'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    prerequisite_chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    is_strict = db.Column(db.Boolean, default=True)  # Must complete prerequisite vs recommended
    
    # Unique constraint to prevent duplicate dependencies
    __table_args__ = (UniqueConstraint('chapter_id', 'prerequisite_chapter_id', name='unique_chapter_dependency'),)
    
    def __repr__(self):
        return f'<ChapterDependency Chapter:{self.chapter_id} requires Chapter:{self.prerequisite_chapter_id}>'

class AIConversationContext(db.Model):
    """
    Maintains conversation context with AI assistant throughout learning sessions.
    """
    __tablename__ = 'ai_conversation_contexts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=True)
    practice_session_id = db.Column(db.Integer, db.ForeignKey('practice_sessions.id'), nullable=True)
    
    context_type = db.Column(db.String(50), default='practice_assistance')  # practice_assistance, general_help, explanation
    conversation_history = db.Column(db.JSON)  # Complete conversation history
    current_topic = db.Column(db.String(200))  # Current topic being discussed
    user_learning_state = db.Column(db.JSON)  # User's current learning state for context
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AIConversationContext User:{self.user_id} Type:{self.context_type}>'