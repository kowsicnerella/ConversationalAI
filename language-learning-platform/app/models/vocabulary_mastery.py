"""
Vocabulary Mastery Models - Phase 5
Comprehensive vocabulary learning with spaced repetition (SM-2 algorithm)
"""
from datetime import datetime, timedelta
from app.models import db


class VocabularyItem(db.Model):
    """
    Individual vocabulary item with comprehensive tracking
    Stores word/phrase with learning metadata
    """
    __tablename__ = 'vocabulary_items'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Word Information
    word = db.Column(db.String(200), nullable=False, index=True)
    word_type = db.Column(db.String(50))  # noun, verb, adjective, phrase, idiom, etc.
    difficulty_level = db.Column(db.String(20))  # A1, A2, B1, B2, C1, C2
    
    # Definitions and Translations
    english_definition = db.Column(db.Text)
    telugu_translation = db.Column(db.String(500))
    pronunciation_ipa = db.Column(db.String(200))  # International Phonetic Alphabet
    pronunciation_guide = db.Column(db.String(200))  # Simple pronunciation
    
    # Usage Context
    example_sentences = db.Column(db.JSON)  # List of example sentences
    common_collocations = db.Column(db.JSON)  # Words commonly used with this word
    usage_notes = db.Column(db.Text)  # Special usage considerations
    formality_level = db.Column(db.String(50))  # formal, informal, neutral, slang
    
    # Categorization
    topic_categories = db.Column(db.JSON)  # business, travel, academic, daily life, etc.
    frequency_rank = db.Column(db.Integer)  # 1-10000 (most common to rare)
    is_high_priority = db.Column(db.Boolean, default=False)
    
    # Audio/Media
    audio_url = db.Column(db.String(500))  # Link to pronunciation audio
    image_url = db.Column(db.String(500))  # Visual aid
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source = db.Column(db.String(100))  # Where this word came from (activity, manual, etc.)
    
    # Relationships
    user_vocabulary = db.relationship('UserVocabulary', back_populates='vocabulary_item', lazy='dynamic')
    word_relationships = db.relationship('WordRelationship', 
                                        foreign_keys='WordRelationship.word_id',
                                        back_populates='word', 
                                        lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_word_difficulty', 'word', 'difficulty_level'),
        db.Index('idx_difficulty_priority', 'difficulty_level', 'is_high_priority'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'word': self.word,
            'word_type': self.word_type,
            'difficulty_level': self.difficulty_level,
            'english_definition': self.english_definition,
            'telugu_translation': self.telugu_translation,
            'pronunciation_ipa': self.pronunciation_ipa,
            'pronunciation_guide': self.pronunciation_guide,
            'example_sentences': self.example_sentences or [],
            'common_collocations': self.common_collocations or [],
            'usage_notes': self.usage_notes,
            'formality_level': self.formality_level,
            'topic_categories': self.topic_categories or [],
            'frequency_rank': self.frequency_rank,
            'is_high_priority': self.is_high_priority,
            'audio_url': self.audio_url,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserVocabulary(db.Model):
    """
    User's personal vocabulary with spaced repetition tracking
    Implements SM-2 algorithm for optimal review scheduling
    """
    __tablename__ = 'user_vocabulary'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocabulary_item_id = db.Column(db.Integer, db.ForeignKey('vocabulary_items.id'), nullable=False)
    
    # Learning Progress
    mastery_level = db.Column(db.String(20), default='new')  # new, learning, familiar, mastered
    confidence_score = db.Column(db.Float, default=0.0)  # 0-100
    
    # SM-2 Spaced Repetition Parameters
    repetition_number = db.Column(db.Integer, default=0)  # How many times reviewed
    easiness_factor = db.Column(db.Float, default=2.5)  # SM-2 easiness factor (1.3-2.5)
    interval_days = db.Column(db.Integer, default=1)  # Days until next review
    next_review_date = db.Column(db.DateTime)  # When to review next
    last_review_date = db.Column(db.DateTime)  # When last reviewed
    
    # Exposure Tracking
    times_seen = db.Column(db.Integer, default=0)  # Total exposures across all activities
    times_used_correctly = db.Column(db.Integer, default=0)  # Successful usage
    times_struggled = db.Column(db.Integer, default=0)  # Failed attempts
    
    # Context Tracking
    first_encountered_activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    contexts_encountered = db.Column(db.JSON)  # List of contexts where word appeared
    
    # Performance Metrics
    average_response_time_seconds = db.Column(db.Float)  # How quickly user recognizes
    recognition_accuracy = db.Column(db.Float)  # % of times correctly recognized
    production_accuracy = db.Column(db.Float)  # % of times correctly used in production
    
    # Learning Velocity
    days_to_familiar = db.Column(db.Integer)  # Days from new to familiar
    days_to_mastered = db.Column(db.Integer)  # Days from new to mastered
    total_practice_time_seconds = db.Column(db.Integer, default=0)
    
    # Retention Tracking
    longest_streak_days = db.Column(db.Integer, default=0)  # Consecutive successful reviews
    current_streak_days = db.Column(db.Integer, default=0)
    last_forgotten_date = db.Column(db.DateTime)  # When user last forgot this word
    times_forgotten = db.Column(db.Integer, default=0)
    
    # User Personalization
    difficulty_rating = db.Column(db.Integer)  # User's subjective difficulty (1-5)
    personal_notes = db.Column(db.Text)  # User's own notes
    is_favorite = db.Column(db.Boolean, default=False)
    mnemonic_device = db.Column(db.Text)  # Memory trick
    
    # Status
    is_active = db.Column(db.Boolean, default=True)  # Still learning this word
    is_archived = db.Column(db.Boolean, default=False)  # User archived this word
    needs_review = db.Column(db.Boolean, default=True)  # Currently due for review
    
    # Timestamps
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    mastered_at = db.Column(db.DateTime)  # When reached mastered status
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('vocabulary_items', lazy='dynamic'))
    vocabulary_item = db.relationship('VocabularyItem', back_populates='user_vocabulary')
    review_history = db.relationship('VocabularyReview', back_populates='user_vocabulary', lazy='dynamic')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_next_review', 'user_id', 'next_review_date'),
        db.Index('idx_user_mastery', 'user_id', 'mastery_level'),
        db.Index('idx_user_needs_review', 'user_id', 'needs_review'),
        db.UniqueConstraint('user_id', 'vocabulary_item_id', name='unique_user_vocabulary'),
    )
    
    def calculate_next_review(self, quality: int):
        """
        SM-2 Algorithm for spaced repetition
        Quality: 0-5 (0=complete failure, 5=perfect recall)
        
        Algorithm:
        - If quality < 3: restart repetition, interval = 1 day
        - If quality >= 3: increase interval based on easiness factor
        - Easiness factor adjusts based on quality
        """
        if quality < 3:
            # Failed recall - restart
            self.repetition_number = 0
            self.interval_days = 1
            self.easiness_factor = max(1.3, self.easiness_factor - 0.2)
            self.times_forgotten += 1
            self.last_forgotten_date = datetime.utcnow()
            self.current_streak_days = 0
        else:
            # Successful recall
            if self.repetition_number == 0:
                self.interval_days = 1
            elif self.repetition_number == 1:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.easiness_factor)
            
            # Update easiness factor
            ef_change = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            self.easiness_factor = max(1.3, self.easiness_factor + ef_change)
            
            self.repetition_number += 1
            self.current_streak_days += 1
            self.longest_streak_days = max(self.longest_streak_days, self.current_streak_days)
        
        # Set next review date
        self.next_review_date = datetime.utcnow() + timedelta(days=self.interval_days)
        self.last_review_date = datetime.utcnow()
        self.needs_review = False
        
        # Update mastery level
        self._update_mastery_level()
        
        return self.next_review_date
    
    def _update_mastery_level(self):
        """Update mastery level based on performance"""
        if self.repetition_number == 0:
            self.mastery_level = 'new'
        elif self.repetition_number < 3:
            self.mastery_level = 'learning'
        elif self.repetition_number < 6 and self.confidence_score > 60:
            self.mastery_level = 'familiar'
        elif self.repetition_number >= 6 and self.confidence_score > 80:
            self.mastery_level = 'mastered'
            if not self.mastered_at:
                self.mastered_at = datetime.utcnow()
                if self.added_at:
                    self.days_to_mastered = (datetime.utcnow() - self.added_at).days
    
    def mark_as_seen(self, context: str = None):
        """Mark word as seen in an activity"""
        self.times_seen += 1
        if context and self.contexts_encountered:
            if context not in self.contexts_encountered:
                self.contexts_encountered.append(context)
        elif context:
            self.contexts_encountered = [context]
    
    def mark_as_used(self, correct: bool, response_time_seconds: float = None):
        """Mark word as used in production (speaking/writing)"""
        if correct:
            self.times_used_correctly += 1
        else:
            self.times_struggled += 1
        
        if response_time_seconds:
            if self.average_response_time_seconds:
                # Moving average
                self.average_response_time_seconds = (
                    self.average_response_time_seconds * 0.8 + response_time_seconds * 0.2
                )
            else:
                self.average_response_time_seconds = response_time_seconds
        
        # Update accuracies
        total_production = self.times_used_correctly + self.times_struggled
        if total_production > 0:
            self.production_accuracy = (self.times_used_correctly / total_production) * 100
    
    def to_dict(self, include_item=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'vocabulary_item_id': self.vocabulary_item_id,
            'mastery_level': self.mastery_level,
            'confidence_score': self.confidence_score,
            'repetition_number': self.repetition_number,
            'easiness_factor': self.easiness_factor,
            'interval_days': self.interval_days,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None,
            'last_review_date': self.last_review_date.isoformat() if self.last_review_date else None,
            'times_seen': self.times_seen,
            'times_used_correctly': self.times_used_correctly,
            'times_struggled': self.times_struggled,
            'recognition_accuracy': self.recognition_accuracy,
            'production_accuracy': self.production_accuracy,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'needs_review': self.needs_review,
            'is_favorite': self.is_favorite,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'mastered_at': self.mastered_at.isoformat() if self.mastered_at else None
        }
        
        if include_item and self.vocabulary_item:
            data['vocabulary_item'] = self.vocabulary_item.to_dict()
        
        return data


class VocabularyReview(db.Model):
    """
    Individual review session for a vocabulary item
    Tracks each practice attempt
    """
    __tablename__ = 'vocabulary_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_vocabulary_id = db.Column(db.Integer, db.ForeignKey('user_vocabulary.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Review Details
    review_type = db.Column(db.String(50))  # flashcard, quiz, usage, recognition, production
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))  # If part of activity
    
    # Performance
    quality_rating = db.Column(db.Integer)  # 0-5 for SM-2 algorithm
    was_correct = db.Column(db.Boolean)
    response_time_seconds = db.Column(db.Float)
    
    # User Feedback
    difficulty_felt = db.Column(db.Integer)  # 1-5 subjective difficulty
    hints_used = db.Column(db.Integer, default=0)
    
    # Context
    context_type = db.Column(db.String(100))  # scheduled_review, activity_practice, etc.
    question_asked = db.Column(db.Text)  # What was asked
    user_response = db.Column(db.Text)  # What user answered
    correct_answer = db.Column(db.Text)  # Correct answer
    
    # Metadata
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user_vocabulary = db.relationship('UserVocabulary', back_populates='review_history')
    user = db.relationship('User', backref=db.backref('vocabulary_reviews', lazy='dynamic'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_review_date', 'user_id', 'reviewed_at'),
        db.Index('idx_vocab_review_date', 'user_vocabulary_id', 'reviewed_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_vocabulary_id': self.user_vocabulary_id,
            'review_type': self.review_type,
            'quality_rating': self.quality_rating,
            'was_correct': self.was_correct,
            'response_time_seconds': self.response_time_seconds,
            'difficulty_felt': self.difficulty_felt,
            'hints_used': self.hints_used,
            'context_type': self.context_type,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }


class WordRelationship(db.Model):
    """
    Relationships between words (synonyms, antonyms, collocations, word families)
    Enables semantic network visualization and contextual learning
    """
    __tablename__ = 'word_relationships'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('vocabulary_items.id'), nullable=False)
    related_word_id = db.Column(db.Integer, db.ForeignKey('vocabulary_items.id'), nullable=False)
    
    # Relationship Type
    relationship_type = db.Column(db.String(50), nullable=False)  
    # synonym, antonym, collocation, derivative, compound, idiom_variant, etc.
    
    # Relationship Strength
    strength = db.Column(db.Float, default=1.0)  # 0-1 (how strong the relationship)
    frequency = db.Column(db.Integer)  # How often they appear together
    
    # Context
    example_usage = db.Column(db.Text)  # Example of relationship
    usage_notes = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_bidirectional = db.Column(db.Boolean, default=True)  # Does the relationship work both ways
    
    # Relationships
    word = db.relationship('VocabularyItem', foreign_keys=[word_id], back_populates='word_relationships')
    related_word = db.relationship('VocabularyItem', foreign_keys=[related_word_id])
    
    # Indexes
    __table_args__ = (
        db.Index('idx_word_relationship', 'word_id', 'relationship_type'),
        db.Index('idx_related_word', 'related_word_id'),
    )
    
    def to_dict(self, include_related_word=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'word_id': self.word_id,
            'related_word_id': self.related_word_id,
            'relationship_type': self.relationship_type,
            'strength': self.strength,
            'frequency': self.frequency,
            'example_usage': self.example_usage,
            'is_bidirectional': self.is_bidirectional
        }
        
        if include_related_word and self.related_word:
            data['related_word'] = self.related_word.to_dict()
        
        return data


class VocabularyPracticeSession(db.Model):
    """
    Tracks focused vocabulary practice sessions
    Groups multiple vocabulary reviews together
    """
    __tablename__ = 'vocabulary_practice_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session Details
    session_type = db.Column(db.String(50))  # daily_review, targeted_practice, mastery_test
    focus_area = db.Column(db.String(100))  # Topic or category focus
    target_mastery_level = db.Column(db.String(20))  # Which level words to practice
    
    # Performance
    words_reviewed = db.Column(db.Integer, default=0)
    words_correct = db.Column(db.Integer, default=0)
    words_incorrect = db.Column(db.Integer, default=0)
    average_quality_rating = db.Column(db.Float)
    session_score = db.Column(db.Float)  # 0-100
    
    # Time Tracking
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer)
    
    # Word List
    words_practiced = db.Column(db.JSON)  # List of vocabulary_item_ids
    
    # Metadata
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('vocabulary_practice_sessions', lazy='dynamic'))
    
    # Indexes
    __table_args__ = (
        db.Index('idx_user_session_date', 'user_id', 'started_at'),
        db.Index('idx_session_type', 'session_type', 'is_completed'),
    )
    
    def complete_session(self):
        """Mark session as complete and calculate final stats"""
        self.completed_at = datetime.utcnow()
        self.is_completed = True
        if self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        
        # Calculate session score
        if self.words_reviewed > 0:
            self.session_score = (self.words_correct / self.words_reviewed) * 100
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'focus_area': self.focus_area,
            'words_reviewed': self.words_reviewed,
            'words_correct': self.words_correct,
            'words_incorrect': self.words_incorrect,
            'session_score': self.session_score,
            'duration_seconds': self.duration_seconds,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_completed': self.is_completed
        }
