from .user import db
from datetime import datetime, date

class UserGoal(db.Model):
    __tablename__ = 'user_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    daily_time_goal_minutes = db.Column(db.Integer, default=10)  # 5, 10, 15, 20, 30
    weekly_activity_goal = db.Column(db.Integer, default=5)  # activities per week
    learning_focus = db.Column(db.String(50), default='conversation')  # conversation, vocabulary, grammar, pronunciation
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserGoal {self.user_id}: {self.daily_time_goal_minutes}min/day>'

class ProficiencyAssessment(db.Model):
    __tablename__ = 'proficiency_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assessment_type = db.Column(db.String(50), default='initial')  # initial, periodic, challenge
    questions_asked = db.Column(db.JSON)  # Store the questions asked (legacy - use questions_data instead)
    questions_data = db.Column(db.JSON)  # Store the questions for in-progress assessments
    user_responses = db.Column(db.JSON)  # Store user responses
    ai_evaluation = db.Column(db.JSON)  # Store AI's evaluation (legacy - use evaluation_results instead)
    evaluation_results = db.Column(db.JSON)  # Store detailed evaluation results
    skill_breakdown = db.Column(db.JSON)  # Store skill-wise performance breakdown
    proficiency_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    confidence_score = db.Column(db.Float)  # 0.0 to 1.0
    score = db.Column(db.Float, default=0.0)  # Current score
    max_score = db.Column(db.Float, default=0.0)  # Maximum possible score
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    started_at = db.Column(db.DateTime)  # When assessment was started
    completed_at = db.Column(db.DateTime)  # When assessment was completed
    strengths = db.Column(db.JSON)  # Array of strength areas
    weaknesses = db.Column(db.JSON)  # Array of areas needing improvement
    recommendations = db.Column(db.JSON)  # Personalized learning recommendations
    
    def __repr__(self):
        return f'<Assessment {self.user_id}: {self.proficiency_level}>'

class VocabularyWord(db.Model):
    __tablename__ = 'vocabulary_words'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    english_word = db.Column(db.String(100), nullable=False)
    telugu_translation = db.Column(db.String(200))
    context_sentence = db.Column(db.Text)  # Sentence where it was encountered
    difficulty_level = db.Column(db.String(20), default='beginner')
    category = db.Column(db.String(50))  # food, travel, business, etc.
    times_encountered = db.Column(db.Integer, default=1)
    times_practiced = db.Column(db.Integer, default=0)
    mastery_level = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    last_practiced = db.Column(db.DateTime)
    discovered_at = db.Column(db.DateTime, default=datetime.utcnow)
    source_activity_type = db.Column(db.String(50))  # chat, reading, role_play, etc.
    
    def __repr__(self):
        return f'<VocabularyWord {self.english_word} -> {self.telugu_translation}>'

class MistakePattern(db.Model):
    __tablename__ = 'mistake_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mistake_type = db.Column(db.String(50), nullable=False)  # grammar, vocabulary, pronunciation, etc.
    mistake_category = db.Column(db.String(100))  # verb_tenses, articles, prepositions, etc.
    original_text = db.Column(db.Text)
    corrected_text = db.Column(db.Text)
    explanation = db.Column(db.Text)
    frequency_count = db.Column(db.Integer, default=1)
    last_occurrence = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    practice_activities_completed = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<MistakePattern {self.mistake_category}: {self.frequency_count} times>'

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # chat, guided_conversation, role_play, etc.
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    messages_exchanged = db.Column(db.Integer, default=0)
    new_words_learned = db.Column(db.Integer, default=0)
    mistakes_made = db.Column(db.Integer, default=0)
    corrections_provided = db.Column(db.Integer, default=0)
    session_summary = db.Column(db.JSON)  # AI-generated summary
    user_satisfaction = db.Column(db.Integer)  # 1-5 rating
    goals_achieved = db.Column(db.Boolean, default=False)
    
    # Additional fields for enhanced chat functionality
    conversation_messages = db.Column(db.JSON)  # Store conversation messages
    user_feedback = db.Column(db.JSON)  # Store user feedback
    
    def __repr__(self):
        return f'<LearningSession {self.session_type}: {self.duration_minutes}min>'

class DailyChallenge(db.Model):
    __tablename__ = 'daily_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_date = db.Column(db.Date, default=date.today, unique=True)
    challenge_type = db.Column(db.String(50), nullable=False)  # conversation_starter, vocabulary, grammar
    challenge_content = db.Column(db.JSON, nullable=False)  # The actual challenge data
    difficulty_level = db.Column(db.String(20), default='beginner')
    estimated_time_minutes = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DailyChallenge {self.challenge_date}: {self.challenge_type}>'

class UserDailyChallengeCompletion(db.Model):
    __tablename__ = 'user_daily_challenge_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('daily_challenges.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_minutes = db.Column(db.Integer)
    success_rate = db.Column(db.Float)  # 0.0 to 1.0
    user_response = db.Column(db.JSON)
    
    # Unique constraint to prevent duplicate completions
    __table_args__ = (db.UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge'),)