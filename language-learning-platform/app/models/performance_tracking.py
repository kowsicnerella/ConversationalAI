"""
Phase 4: Comprehensive Performance Tracking Models
Multi-dimensional tracking across all skill domains with detailed analytics
"""
from datetime import datetime
from app.models import db


class ListeningPerformance(db.Model):
    """
    Track listening comprehension performance with detailed metrics
    """
    __tablename__ = "listening_performance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    session_id = db.Column(db.String(100))  # For grouping related activities
    
    # Audio characteristics
    audio_duration = db.Column(db.Float, nullable=False)  # Duration in seconds
    audio_url = db.Column(db.String(500))  # Reference to audio file
    accent_type = db.Column(db.String(50))  # american, british, australian, etc.
    speed_factor = db.Column(db.Float, default=1.0)  # 0.5 = slow, 1.0 = normal, 1.5 = fast
    topic = db.Column(db.String(100))
    difficulty_level = db.Column(db.String(20))
    
    # Performance metrics
    comprehension_score = db.Column(db.Float, nullable=False)  # 0-100
    accuracy_percentage = db.Column(db.Float)  # Correct answers / total questions
    playback_count = db.Column(db.Integer, default=1)  # How many times played
    
    # Interaction patterns
    pause_points = db.Column(db.JSON)  # List of timestamps where user paused
    pause_count = db.Column(db.Integer, default=0)
    replay_sections = db.Column(db.JSON)  # Sections that were replayed
    difficult_segments = db.Column(db.JSON)  # Segments user struggled with
    
    # Vocabulary and comprehension
    difficult_words = db.Column(db.JSON)  # Words user didn't understand
    new_vocabulary_encountered = db.Column(db.JSON)  # New words in audio
    context_understanding = db.Column(db.Float)  # 0-100 understanding of context
    inference_ability = db.Column(db.Float)  # 0-100 ability to infer meaning
    
    # Question-level details
    questions_data = db.Column(db.JSON)  # Full question and answer data
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    
    # Timing
    time_to_complete = db.Column(db.Integer)  # Seconds to complete activity
    avg_time_per_question = db.Column(db.Float)  # Average response time
    
    # AI analysis
    weak_phonemes = db.Column(db.JSON)  # Phonemes user struggles to recognize
    accent_adaptation_score = db.Column(db.Float)  # How well user adapts to accent
    ai_feedback = db.Column(db.Text)
    improvement_suggestions = db.Column(db.JSON)
    
    # Progress tracking
    previous_score = db.Column(db.Float)  # Score on similar difficulty/topic
    improvement_rate = db.Column(db.Float)  # Rate of improvement
    mastery_level = db.Column(db.String(20))  # novice, developing, proficient, advanced
    
    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("listening_performances", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_listening_date', 'user_id', 'completed_at'),
        db.Index('idx_user_listening_mastery', 'user_id', 'mastery_level'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'audio_duration': self.audio_duration,
            'accent_type': self.accent_type,
            'speed_factor': self.speed_factor,
            'topic': self.topic,
            'difficulty_level': self.difficulty_level,
            'comprehension_score': self.comprehension_score,
            'accuracy_percentage': self.accuracy_percentage,
            'playback_count': self.playback_count,
            'pause_count': self.pause_count,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'mastery_level': self.mastery_level,
            'improvement_rate': self.improvement_rate,
            'completed_at': self.completed_at.isoformat()
        }


class SpeakingPerformance(db.Model):
    """
    Track speaking performance with pronunciation, fluency, and confidence metrics
    """
    __tablename__ = "speaking_performance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    session_id = db.Column(db.String(100))
    
    # Activity details
    speaking_type = db.Column(db.String(50))  # pronunciation, conversation, presentation, roleplay
    topic = db.Column(db.String(100))
    scenario = db.Column(db.String(200))  # For roleplay scenarios
    difficulty_level = db.Column(db.String(20))
    
    # Recording details
    audio_url = db.Column(db.String(500))  # User's recording
    recording_duration = db.Column(db.Float)  # Seconds
    transcript = db.Column(db.Text)  # What user said (from speech-to-text)
    expected_content = db.Column(db.Text)  # What was expected (if applicable)
    
    # Core performance metrics
    pronunciation_accuracy = db.Column(db.Float, nullable=False)  # 0-100
    fluency_score = db.Column(db.Float, nullable=False)  # 0-100
    grammar_score = db.Column(db.Float)  # 0-100
    vocabulary_richness = db.Column(db.Float)  # 0-100 variety and appropriateness
    overall_score = db.Column(db.Float)  # 0-100 weighted average
    
    # Fluency metrics
    words_per_minute = db.Column(db.Float)
    speaking_rate = db.Column(db.String(20))  # slow, normal, fast
    hesitation_count = db.Column(db.Integer, default=0)  # Number of hesitations
    filler_words = db.Column(db.JSON)  # ["um", "uh", "like", etc.]
    filler_word_count = db.Column(db.Integer, default=0)
    pause_analysis = db.Column(db.JSON)  # Length and frequency of pauses
    
    # Pronunciation details
    mispronounced_words = db.Column(db.JSON)  # Words with pronunciation issues
    phoneme_errors = db.Column(db.JSON)  # Specific phoneme mistakes
    accent_score = db.Column(db.Float)  # How close to target accent
    intonation_score = db.Column(db.Float)  # Pitch and stress patterns
    
    # Grammar and vocabulary
    grammar_errors = db.Column(db.JSON)  # List of grammar mistakes
    grammar_error_count = db.Column(db.Integer, default=0)
    vocabulary_used = db.Column(db.JSON)  # Words used
    advanced_vocabulary_count = db.Column(db.Integer, default=0)
    vocabulary_appropriateness = db.Column(db.Float)  # Context-appropriate usage
    
    # Confidence and expression
    confidence_level = db.Column(db.Float)  # 0-100 based on voice characteristics
    volume_consistency = db.Column(db.Float)  # 0-100
    emotional_expression = db.Column(db.Float)  # 0-100 appropriate emotion
    
    # Content quality (for structured tasks)
    content_relevance = db.Column(db.Float)  # How relevant to topic
    coherence_score = db.Column(db.Float)  # Logical flow
    task_completion = db.Column(db.Float)  # 0-100 did they complete the task
    
    # AI analysis
    ai_feedback = db.Column(db.Text)
    pronunciation_tips = db.Column(db.JSON)
    grammar_corrections = db.Column(db.JSON)
    vocabulary_suggestions = db.Column(db.JSON)
    improvement_areas = db.Column(db.JSON)
    
    # Progress tracking
    previous_score = db.Column(db.Float)
    improvement_rate = db.Column(db.Float)
    mastery_level = db.Column(db.String(20))
    practice_needed = db.Column(db.JSON)  # Specific areas to practice
    
    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("speaking_performances", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_speaking_date', 'user_id', 'completed_at'),
        db.Index('idx_user_speaking_type', 'user_id', 'speaking_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'speaking_type': self.speaking_type,
            'topic': self.topic,
            'difficulty_level': self.difficulty_level,
            'pronunciation_accuracy': self.pronunciation_accuracy,
            'fluency_score': self.fluency_score,
            'grammar_score': self.grammar_score,
            'vocabulary_richness': self.vocabulary_richness,
            'overall_score': self.overall_score,
            'words_per_minute': self.words_per_minute,
            'confidence_level': self.confidence_level,
            'mastery_level': self.mastery_level,
            'completed_at': self.completed_at.isoformat()
        }


class ReadingPerformance(db.Model):
    """
    Track reading comprehension with speed, accuracy, and understanding metrics
    """
    __tablename__ = "reading_performance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    session_id = db.Column(db.String(100))
    
    # Reading material details
    text_title = db.Column(db.String(200))
    text_type = db.Column(db.String(50))  # article, story, academic, business, casual
    topic = db.Column(db.String(100))
    difficulty_level = db.Column(db.String(20))
    word_count = db.Column(db.Integer)
    text_complexity = db.Column(db.Float)  # Flesch-Kincaid or similar metric
    
    # Reading speed metrics
    reading_time_seconds = db.Column(db.Integer, nullable=False)
    reading_speed_wpm = db.Column(db.Float)  # Words per minute
    speed_rating = db.Column(db.String(20))  # slow, average, fast
    target_speed_wpm = db.Column(db.Float)  # Expected speed for this level
    
    # Comprehension metrics
    comprehension_score = db.Column(db.Float, nullable=False)  # 0-100
    accuracy_percentage = db.Column(db.Float)
    literal_comprehension = db.Column(db.Float)  # Understanding explicit information
    inferential_comprehension = db.Column(db.Float)  # Understanding implied meaning
    critical_comprehension = db.Column(db.Float)  # Analysis and evaluation
    
    # Interaction patterns
    vocabulary_lookups = db.Column(db.JSON)  # Words user looked up
    lookup_count = db.Column(db.Integer, default=0)
    re_read_sections = db.Column(db.JSON)  # Sections user re-read
    re_read_count = db.Column(db.Integer, default=0)
    time_per_paragraph = db.Column(db.JSON)  # Reading time distribution
    
    # Question performance
    questions_data = db.Column(db.JSON)  # Full question and answer data
    total_questions = db.Column(db.Integer)
    correct_answers = db.Column(db.Integer)
    time_per_question = db.Column(db.JSON)  # Time spent on each question
    avg_time_per_question = db.Column(db.Float)
    
    # Vocabulary analysis
    new_vocabulary_encountered = db.Column(db.JSON)  # New words in text
    unknown_words = db.Column(db.JSON)  # Words user didn't know
    vocabulary_coverage = db.Column(db.Float)  # % of words user knew
    
    # Comprehension patterns
    main_idea_understanding = db.Column(db.Float)  # 0-100
    detail_retention = db.Column(db.Float)  # 0-100
    inference_ability = db.Column(db.Float)  # 0-100
    context_clue_usage = db.Column(db.Float)  # How well user uses context
    
    # AI analysis
    ai_feedback = db.Column(db.Text)
    reading_strategies_used = db.Column(db.JSON)  # Strategies observed
    improvement_suggestions = db.Column(db.JSON)
    vocabulary_to_study = db.Column(db.JSON)
    
    # Progress tracking
    previous_score = db.Column(db.Float)
    previous_speed_wpm = db.Column(db.Float)
    speed_improvement = db.Column(db.Float)  # % improvement in speed
    comprehension_improvement = db.Column(db.Float)  # % improvement in comprehension
    mastery_level = db.Column(db.String(20))
    
    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("reading_performances", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_reading_date', 'user_id', 'completed_at'),
        db.Index('idx_user_reading_type', 'user_id', 'text_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'text_title': self.text_title,
            'text_type': self.text_type,
            'topic': self.topic,
            'difficulty_level': self.difficulty_level,
            'word_count': self.word_count,
            'reading_speed_wpm': self.reading_speed_wpm,
            'comprehension_score': self.comprehension_score,
            'accuracy_percentage': self.accuracy_percentage,
            'lookup_count': self.lookup_count,
            'mastery_level': self.mastery_level,
            'completed_at': self.completed_at.isoformat()
        }


class WritingPerformance(db.Model):
    """
    Track writing performance with grammar, coherence, and creativity metrics
    """
    __tablename__ = "writing_performance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    session_id = db.Column(db.String(100))
    
    # Writing task details
    writing_type = db.Column(db.String(50))  # essay, email, story, description, report
    topic = db.Column(db.String(200))
    prompt = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))
    target_word_count = db.Column(db.Integer)
    
    # User's writing
    content = db.Column(db.Text, nullable=False)  # What user wrote
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    paragraph_count = db.Column(db.Integer)
    sentence_count = db.Column(db.Integer)
    
    # Core performance metrics
    overall_score = db.Column(db.Float, nullable=False)  # 0-100
    grammar_score = db.Column(db.Float)  # 0-100
    vocabulary_score = db.Column(db.Float)  # 0-100
    coherence_score = db.Column(db.Float)  # 0-100
    task_achievement = db.Column(db.Float)  # 0-100 how well task was completed
    
    # Grammar analysis
    grammar_errors = db.Column(db.JSON)  # Detailed error list
    grammar_error_count = db.Column(db.Integer, default=0)
    error_types = db.Column(db.JSON)  # Categorized errors (tense, agreement, etc.)
    spelling_errors = db.Column(db.JSON)
    spelling_error_count = db.Column(db.Integer, default=0)
    punctuation_errors = db.Column(db.JSON)
    punctuation_error_count = db.Column(db.Integer, default=0)
    
    # Vocabulary analysis
    vocabulary_used = db.Column(db.JSON)  # All words used
    unique_words = db.Column(db.Integer)  # Vocabulary diversity
    advanced_vocabulary = db.Column(db.JSON)  # Advanced words used
    advanced_vocabulary_count = db.Column(db.Integer, default=0)
    vocabulary_diversity = db.Column(db.Float)  # 0-100 range of vocabulary
    vocabulary_appropriateness = db.Column(db.Float)  # 0-100 context fit
    repetitive_words = db.Column(db.JSON)  # Overused words
    
    # Sentence structure
    sentence_lengths = db.Column(db.JSON)  # Length of each sentence
    avg_sentence_length = db.Column(db.Float)
    sentence_variety = db.Column(db.Float)  # 0-100 variety in structure
    simple_sentences = db.Column(db.Integer)
    compound_sentences = db.Column(db.Integer)
    complex_sentences = db.Column(db.Integer)
    sentence_complexity = db.Column(db.Float)  # 0-100
    
    # Coherence and organization
    coherence_score = db.Column(db.Float)  # 0-100 logical flow
    paragraph_organization = db.Column(db.Float)  # 0-100
    transition_usage = db.Column(db.Float)  # Use of connecting words
    topic_consistency = db.Column(db.Float)  # Staying on topic
    argument_development = db.Column(db.Float)  # For argumentative writing
    
    # Content quality
    originality_score = db.Column(db.Float)  # 0-100 creativity
    depth_of_content = db.Column(db.Float)  # 0-100 detail and insight
    relevance_to_prompt = db.Column(db.Float)  # 0-100
    supporting_evidence = db.Column(db.Float)  # Use of examples/evidence
    
    # Writing process metrics
    writing_time_minutes = db.Column(db.Integer)
    revision_count = db.Column(db.Integer, default=0)  # How many times edited
    edit_history = db.Column(db.JSON)  # Major changes made
    planning_time = db.Column(db.Integer)  # Time spent planning (if tracked)
    
    # AI feedback
    ai_feedback = db.Column(db.Text)
    strengths = db.Column(db.JSON)  # What was done well
    areas_for_improvement = db.Column(db.JSON)
    grammar_corrections = db.Column(db.JSON)  # Suggested corrections
    vocabulary_suggestions = db.Column(db.JSON)  # Better word choices
    structural_suggestions = db.Column(db.JSON)  # Organization improvements
    
    # Progress tracking
    previous_score = db.Column(db.Float)
    improvement_rate = db.Column(db.Float)
    mastery_level = db.Column(db.String(20))
    target_skills = db.Column(db.JSON)  # Skills to focus on next
    
    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("writing_performances", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_writing_date', 'user_id', 'completed_at'),
        db.Index('idx_user_writing_type', 'user_id', 'writing_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'writing_type': self.writing_type,
            'topic': self.topic,
            'word_count': self.word_count,
            'overall_score': self.overall_score,
            'grammar_score': self.grammar_score,
            'vocabulary_score': self.vocabulary_score,
            'coherence_score': self.coherence_score,
            'grammar_error_count': self.grammar_error_count,
            'vocabulary_diversity': self.vocabulary_diversity,
            'sentence_complexity': self.sentence_complexity,
            'mastery_level': self.mastery_level,
            'completed_at': self.completed_at.isoformat()
        }


class RealWorldPerformance(db.Model):
    """
    Track performance in practical, real-world language scenarios
    """
    __tablename__ = "real_world_performance"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"))
    session_id = db.Column(db.String(100))
    
    # Scenario details
    scenario_type = db.Column(db.String(50), nullable=False)  # interview, email, presentation, negotiation, meeting
    industry = db.Column(db.String(50))  # business, academic, medical, legal, etc.
    context = db.Column(db.String(200))  # Specific situation
    difficulty_level = db.Column(db.String(20))
    
    # Task description
    task_description = db.Column(db.Text)
    expected_outcomes = db.Column(db.JSON)  # What should be achieved
    user_response = db.Column(db.Text)  # User's output
    response_format = db.Column(db.String(50))  # written, spoken, mixed
    
    # Core performance metrics
    overall_score = db.Column(db.Float, nullable=False)  # 0-100
    task_completion = db.Column(db.Float)  # 0-100 did they complete the task
    appropriateness_score = db.Column(db.Float)  # 0-100 appropriate for context
    professional_language_use = db.Column(db.Float)  # 0-100 formality and tone
    cultural_awareness = db.Column(db.Float)  # 0-100 cultural appropriateness
    
    # Communication effectiveness
    clarity_score = db.Column(db.Float)  # 0-100 how clear the message is
    persuasiveness = db.Column(db.Float)  # 0-100 for negotiations/presentations
    diplomacy_score = db.Column(db.Float)  # 0-100 tactfulness
    engagement_quality = db.Column(db.Float)  # 0-100 ability to engage audience
    
    # Language skills applied
    vocabulary_appropriateness = db.Column(db.Float)  # Context-appropriate words
    grammar_accuracy = db.Column(db.Float)
    register_appropriateness = db.Column(db.Float)  # Formal vs informal
    idiomatic_usage = db.Column(db.Float)  # Use of appropriate expressions
    
    # Specific scenario metrics
    email_etiquette_score = db.Column(db.Float)  # For email scenarios
    presentation_structure = db.Column(db.Float)  # For presentations
    interview_response_quality = db.Column(db.Float)  # For interviews
    negotiation_effectiveness = db.Column(db.Float)  # For negotiations
    meeting_participation = db.Column(db.Float)  # For meeting scenarios
    
    # Time management
    time_management = db.Column(db.Float)  # 0-100 efficiency
    response_time_seconds = db.Column(db.Integer)
    expected_time_seconds = db.Column(db.Integer)
    
    # Detailed analysis
    strengths = db.Column(db.JSON)  # What was done well
    weaknesses = db.Column(db.JSON)  # Areas for improvement
    mistakes_made = db.Column(db.JSON)  # Specific errors
    best_practices_followed = db.Column(db.JSON)
    best_practices_missed = db.Column(db.JSON)
    
    # AI feedback
    ai_feedback = db.Column(db.Text)
    improvement_suggestions = db.Column(db.JSON)
    alternative_approaches = db.Column(db.JSON)  # Better ways to handle scenario
    vocabulary_suggestions = db.Column(db.JSON)  # Better word choices
    phrase_suggestions = db.Column(db.JSON)  # Better phrases for context
    
    # Learning outcomes
    skills_demonstrated = db.Column(db.JSON)  # Skills shown in scenario
    skills_to_develop = db.Column(db.JSON)  # Skills needing work
    real_world_readiness = db.Column(db.Float)  # 0-100 ready for actual situation
    confidence_level = db.Column(db.Float)  # 0-100
    
    # Progress tracking
    previous_score = db.Column(db.Float)
    improvement_rate = db.Column(db.Float)
    mastery_level = db.Column(db.String(20))
    similar_scenarios_completed = db.Column(db.Integer)  # Count of similar scenarios
    
    # Timestamps
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("real_world_performances", lazy="dynamic"))
    activity = db.relationship("Activity")
    
    __table_args__ = (
        db.Index('idx_user_realworld_date', 'user_id', 'completed_at'),
        db.Index('idx_user_scenario_type', 'user_id', 'scenario_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'scenario_type': self.scenario_type,
            'industry': self.industry,
            'context': self.context,
            'difficulty_level': self.difficulty_level,
            'overall_score': self.overall_score,
            'task_completion': self.task_completion,
            'appropriateness_score': self.appropriateness_score,
            'professional_language_use': self.professional_language_use,
            'cultural_awareness': self.cultural_awareness,
            'real_world_readiness': self.real_world_readiness,
            'mastery_level': self.mastery_level,
            'completed_at': self.completed_at.isoformat()
        }


class SkillTrajectory(db.Model):
    """
    Track skill improvement over time with trend analysis
    """
    __tablename__ = "skill_trajectories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    # Skill identification
    skill_domain = db.Column(db.String(50), nullable=False)  # listening, speaking, reading, writing, real_world
    sub_skill = db.Column(db.String(100))  # Specific sub-skill being tracked
    
    # Current status
    current_level = db.Column(db.Float, nullable=False)  # 0-100 current proficiency
    mastery_status = db.Column(db.String(20))  # novice, developing, proficient, advanced, expert
    
    # Historical tracking
    baseline_level = db.Column(db.Float)  # Initial level when tracking started
    peak_level = db.Column(db.Float)  # Highest level achieved
    lowest_level = db.Column(db.Float)  # Lowest level (to detect regression)
    
    # Progression metrics
    total_practice_sessions = db.Column(db.Integer, default=0)
    total_practice_time_minutes = db.Column(db.Integer, default=0)
    improvement_rate = db.Column(db.Float)  # Points per week
    velocity = db.Column(db.String(20))  # slow, steady, fast, accelerating, plateauing
    
    # Performance history (last 30 data points)
    performance_history = db.Column(db.JSON)  # List of {date, score, activity_type}
    trend_direction = db.Column(db.String(20))  # improving, stable, declining
    trend_strength = db.Column(db.Float)  # How strong the trend is
    
    # Consistency metrics
    practice_frequency = db.Column(db.Float)  # Sessions per week
    consistency_score = db.Column(db.Float)  # 0-100 how consistent practice is
    longest_streak_days = db.Column(db.Integer, default=0)
    current_streak_days = db.Column(db.Integer, default=0)
    
    # Predictive analytics
    estimated_time_to_next_level = db.Column(db.Integer)  # Days
    projected_level_30days = db.Column(db.Float)  # Predicted level in 30 days
    confidence_interval = db.Column(db.Float)  # Confidence in prediction
    
    # Patterns identified
    best_learning_time = db.Column(db.String(20))  # morning, afternoon, evening
    optimal_session_length = db.Column(db.Integer)  # Minutes
    preferred_activity_types = db.Column(db.JSON)  # Activities that work best
    struggle_areas = db.Column(db.JSON)  # Specific areas of difficulty
    
    # Milestones
    milestones_achieved = db.Column(db.JSON)  # List of achievement dates
    next_milestone = db.Column(db.String(100))
    next_milestone_progress = db.Column(db.Float)  # 0-100
    
    # AI insights
    ai_analysis = db.Column(db.Text)
    recommendations = db.Column(db.JSON)
    focus_areas = db.Column(db.JSON)  # What to work on next
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tracking_started = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_practice_date = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship("User", backref=db.backref("skill_trajectories", lazy="dynamic"))
    
    __table_args__ = (
        db.Index('idx_user_skill_domain', 'user_id', 'skill_domain'),
        db.UniqueConstraint('user_id', 'skill_domain', 'sub_skill', name='uq_user_skill'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_domain': self.skill_domain,
            'sub_skill': self.sub_skill,
            'current_level': self.current_level,
            'mastery_status': self.mastery_status,
            'improvement_rate': self.improvement_rate,
            'velocity': self.velocity,
            'trend_direction': self.trend_direction,
            'practice_frequency': self.practice_frequency,
            'consistency_score': self.consistency_score,
            'estimated_time_to_next_level': self.estimated_time_to_next_level,
            'last_updated': self.last_updated.isoformat()
        }
