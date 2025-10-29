"""
Phase 6: Intelligent Assessment System - Database Models

This module defines the database models for a comprehensive intelligent assessment system
featuring:
- Multi-stage assessments (placement, progress, mastery, certification)
- Adaptive testing with Item Response Theory (IRT)
- Skill-specific diagnostics
- Comparative analytics
- Progress tracking

Author: AI Learning Platform
Date: October 20, 2025
"""

from datetime import datetime
from app.models import db
import json


class Assessment(db.Model):
    """
    Master assessment template defining structure and configuration.
    Can be used for placement, progress checks, mastery tests, or certification prep.
    """
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assessment_type = db.Column(db.String(50), nullable=False)  # placement, progress, mastery, certification
    target_skill = db.Column(db.String(50))  # null for comprehensive, specific skill for targeted
    difficulty_range = db.Column(db.JSON)  # {"min": "beginner", "max": "advanced"}
    
    # Assessment Configuration
    is_adaptive = db.Column(db.Boolean, default=False)  # Adaptive vs Fixed
    estimated_duration_minutes = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    passing_score_percentage = db.Column(db.Float, default=70.0)
    
    # IRT Parameters for adaptive testing
    use_irt = db.Column(db.Boolean, default=False)  # Use Item Response Theory
    theta_initial = db.Column(db.Float, default=0.0)  # Initial ability estimate
    theta_bounds = db.Column(db.JSON)  # {"min": -3, "max": 3}
    stopping_criterion = db.Column(db.String(50))  # 'fixed_questions', 'precision', 'time'
    stopping_value = db.Column(db.Float)  # Value for stopping criterion
    
    # Metadata
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)
    requires_authentication = db.Column(db.Boolean, default=True)
    max_attempts = db.Column(db.Integer, default=3)  # 0 = unlimited
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('AssessmentQuestion', back_populates='assessment', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('UserAssessmentAttempt', back_populates='assessment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Assessment {self.id}: {self.title} ({self.assessment_type})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'assessment_type': self.assessment_type,
            'target_skill': self.target_skill,
            'difficulty_range': self.difficulty_range,
            'is_adaptive': self.is_adaptive,
            'use_irt': self.use_irt,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'total_questions': self.total_questions,
            'passing_score_percentage': self.passing_score_percentage,
            'is_active': self.is_active,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AssessmentQuestion(db.Model):
    """
    Individual question in an assessment with IRT parameters.
    Supports multiple question types and difficulty calibration.
    """
    __tablename__ = 'assessment_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    
    # Question Content
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, short_answer, essay, etc.
    skill_area = db.Column(db.String(50))  # vocabulary, grammar, reading, writing, listening, speaking
    sub_skill = db.Column(db.String(50))  # more specific: tenses, articles, comprehension, etc.
    
    # Difficulty & Scoring
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    points = db.Column(db.Integer, default=1)
    
    # IRT Parameters (3-Parameter Logistic Model)
    irt_discrimination = db.Column(db.Float)  # a parameter (item discrimination)
    irt_difficulty = db.Column(db.Float)  # b parameter (item difficulty, theta scale)
    irt_guessing = db.Column(db.Float, default=0.0)  # c parameter (pseudo-guessing)
    
    # Question Options/Data
    options = db.Column(db.JSON)  # For multiple choice: [{"text": "...", "is_correct": true/false}]
    correct_answer = db.Column(db.Text)  # For non-multiple choice
    answer_rubric = db.Column(db.JSON)  # Scoring rubric for complex answers
    
    # Hints & Feedback
    hint_text = db.Column(db.Text)
    explanation = db.Column(db.Text)  # Explanation shown after answer
    telugu_translation = db.Column(db.Text)  # Question in Telugu
    
    # Metadata
    order_index = db.Column(db.Integer)  # Display order in fixed tests
    is_active = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)  # How many times used
    avg_correctness = db.Column(db.Float)  # Historical accuracy for calibration
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = db.relationship('Assessment', back_populates='questions')
    responses = db.relationship('QuestionResponse', back_populates='question', lazy='dynamic')
    
    def __repr__(self):
        return f'<AssessmentQuestion {self.id}: {self.skill_area} - {self.difficulty_level}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'skill_area': self.skill_area,
            'sub_skill': self.sub_skill,
            'difficulty_level': self.difficulty_level,
            'points': self.points,
            'options': self.options,
            'hint_text': self.hint_text,
            'telugu_translation': self.telugu_translation,
            'irt_discrimination': self.irt_discrimination,
            'irt_difficulty': self.irt_difficulty
        }


class UserAssessmentAttempt(db.Model):
    """
    Records a user's attempt at an assessment.
    Tracks progress, timing, and final results.
    """
    __tablename__ = 'user_assessment_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    
    # Attempt Status
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    attempt_number = db.Column(db.Integer, default=1)  # Which attempt is this?
    
    # Adaptive Testing State
    current_question_index = db.Column(db.Integer, default=0)
    theta_estimate = db.Column(db.Float, default=0.0)  # Current ability estimate (IRT)
    theta_se = db.Column(db.Float)  # Standard error of theta estimate
    questions_asked = db.Column(db.JSON)  # List of question IDs asked
    
    # Scoring
    total_questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float)
    passed = db.Column(db.Boolean)
    
    # Timing
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    time_taken_seconds = db.Column(db.Integer)
    
    # Results & Analysis
    skill_breakdown = db.Column(db.JSON)  # {"vocabulary": 80, "grammar": 65, ...}
    proficiency_level = db.Column(db.String(20))  # Determined proficiency level
    strengths = db.Column(db.JSON)  # List of strong skill areas
    weaknesses = db.Column(db.JSON)  # List of weak skill areas
    recommendations = db.Column(db.JSON)  # Personalized recommendations
    
    # Metadata
    context = db.Column(db.String(100))  # Where taken: 'onboarding', 'progress_check', etc.
    device_info = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='assessment_attempts')
    assessment = db.relationship('Assessment', back_populates='attempts')
    responses = db.relationship('QuestionResponse', back_populates='attempt', lazy='dynamic', cascade='all, delete-orphan')
    result = db.relationship('AssessmentResult', back_populates='attempt', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UserAssessmentAttempt {self.id}: User {self.user_id} - Assessment {self.assessment_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'assessment_id': self.assessment_id,
            'status': self.status,
            'attempt_number': self.attempt_number,
            'current_question_index': self.current_question_index,
            'theta_estimate': self.theta_estimate,
            'total_questions_answered': self.total_questions_answered,
            'correct_answers': self.correct_answers,
            'score_percentage': self.score_percentage,
            'passed': self.passed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken_seconds': self.time_taken_seconds,
            'proficiency_level': self.proficiency_level
        }


class QuestionResponse(db.Model):
    """
    Individual question response within an assessment attempt.
    Stores answer, correctness, and timing for each question.
    """
    __tablename__ = 'question_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_questions.id'), nullable=False)
    
    # Response Data
    user_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Integer)
    points_possible = db.Column(db.Integer)
    
    # IRT Analysis
    theta_at_response = db.Column(db.Float)  # Ability estimate when question was asked
    probability_correct = db.Column(db.Float)  # IRT-predicted probability
    information_value = db.Column(db.Float)  # How much this response informs ability estimate
    
    # Timing
    time_to_answer_seconds = db.Column(db.Integer)
    viewed_hint = db.Column(db.Boolean, default=False)
    
    # Feedback
    feedback = db.Column(db.Text)  # Immediate feedback given
    correct_answer_shown = db.Column(db.Text)  # What the correct answer was
    
    # Timestamps
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('UserAssessmentAttempt', back_populates='responses')
    question = db.relationship('AssessmentQuestion', back_populates='responses')
    
    def __repr__(self):
        return f'<QuestionResponse {self.id}: Question {self.question_id} - {"Correct" if self.is_correct else "Incorrect"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'points_earned': self.points_earned,
            'points_possible': self.points_possible,
            'time_to_answer_seconds': self.time_to_answer_seconds,
            'feedback': self.feedback,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None
        }


class AssessmentResult(db.Model):
    """
    Comprehensive analysis and results for a completed assessment.
    Includes detailed breakdown, comparisons, and recommendations.
    """
    __tablename__ = 'assessment_results'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempts.id'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Overall Performance
    final_score_percentage = db.Column(db.Float)
    final_theta = db.Column(db.Float)  # Final ability estimate
    final_theta_se = db.Column(db.Float)  # Final standard error
    proficiency_level = db.Column(db.String(20))
    proficiency_confidence = db.Column(db.Float)  # Confidence in proficiency determination
    
    # Skill Breakdown
    skill_scores = db.Column(db.JSON)  # {"vocabulary": {"correct": 8, "total": 10, "percentage": 80}, ...}
    strongest_skills = db.Column(db.JSON)  # Top 3 skills
    weakest_skills = db.Column(db.JSON)  # Bottom 3 skills
    
    # Comparative Analysis
    percentile_rank = db.Column(db.Float)  # Percentile vs all users
    grade_equivalent = db.Column(db.String(10))  # e.g., "B1", "B2"
    comparative_data = db.Column(db.JSON)  # Comparison with cohorts
    
    # Diagnostic Information
    learning_gaps = db.Column(db.JSON)  # Identified gaps: [{"skill": "...", "severity": "high"}]
    mastered_concepts = db.Column(db.JSON)  # What they know well
    ready_for_advancement = db.Column(db.Boolean)
    
    # Recommendations
    next_steps = db.Column(db.JSON)  # Recommended actions
    recommended_learning_paths = db.Column(db.JSON)  # Path IDs and reasons
    study_plan = db.Column(db.JSON)  # Suggested study schedule
    
    # Certification Readiness (if applicable)
    certification_ready = db.Column(db.Boolean)
    certification_gaps = db.Column(db.JSON)
    estimated_study_time_hours = db.Column(db.Integer)
    
    # Report Generation
    detailed_report = db.Column(db.JSON)  # Complete analysis report
    report_generated_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('UserAssessmentAttempt', back_populates='result')
    user = db.relationship('User', backref='assessment_results')
    diagnostics = db.relationship('SkillDiagnostic', back_populates='result', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AssessmentResult {self.id}: User {self.user_id} - {self.proficiency_level}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'final_score_percentage': self.final_score_percentage,
            'proficiency_level': self.proficiency_level,
            'proficiency_confidence': self.proficiency_confidence,
            'skill_scores': self.skill_scores,
            'strongest_skills': self.strongest_skills,
            'weakest_skills': self.weakest_skills,
            'percentile_rank': self.percentile_rank,
            'grade_equivalent': self.grade_equivalent,
            'learning_gaps': self.learning_gaps,
            'ready_for_advancement': self.ready_for_advancement,
            'next_steps': self.next_steps,
            'certification_ready': self.certification_ready,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SkillDiagnostic(db.Model):
    """
    Detailed diagnostic information for a specific skill area.
    Provides granular analysis of performance within each skill.
    """
    __tablename__ = 'skill_diagnostics'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('assessment_results.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Skill Information
    skill_area = db.Column(db.String(50), nullable=False)
    sub_skills_tested = db.Column(db.JSON)  # List of sub-skills assessed
    
    # Performance Metrics
    questions_attempted = db.Column(db.Integer)
    questions_correct = db.Column(db.Integer)
    accuracy_percentage = db.Column(db.Float)
    skill_theta = db.Column(db.Float)  # IRT ability estimate for this skill
    skill_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    
    # Sub-skill Breakdown
    sub_skill_performance = db.Column(db.JSON)  # {"tenses": 80, "articles": 60, ...}
    concept_mastery = db.Column(db.JSON)  # Which concepts mastered vs struggling
    
    # Error Analysis
    common_errors = db.Column(db.JSON)  # Patterns in mistakes
    misconceptions = db.Column(db.JSON)  # Identified misconceptions
    
    # Progress Tracking
    previous_skill_level = db.Column(db.String(20))  # From last assessment
    improvement_percentage = db.Column(db.Float)
    trend = db.Column(db.String(20))  # improving, stable, declining
    
    # Recommendations
    focus_areas = db.Column(db.JSON)  # What to work on
    recommended_activities = db.Column(db.JSON)  # Specific activity recommendations
    estimated_practice_hours = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    result = db.relationship('AssessmentResult', back_populates='diagnostics')
    user = db.relationship('User', backref='skill_diagnostics')
    
    def __repr__(self):
        return f'<SkillDiagnostic {self.id}: {self.skill_area} - {self.accuracy_percentage}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'skill_area': self.skill_area,
            'sub_skills_tested': self.sub_skills_tested,
            'questions_attempted': self.questions_attempted,
            'questions_correct': self.questions_correct,
            'accuracy_percentage': self.accuracy_percentage,
            'skill_level': self.skill_level,
            'sub_skill_performance': self.sub_skill_performance,
            'common_errors': self.common_errors,
            'focus_areas': self.focus_areas,
            'improvement_percentage': self.improvement_percentage,
            'trend': self.trend,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AdaptiveTestSession(db.Model):
    """
    Tracks the state of an adaptive test session using IRT.
    Stores the dynamic state as the test progresses.
    """
    __tablename__ = 'adaptive_test_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('user_assessment_attempts.id'), nullable=False)
    
    # IRT State
    current_theta = db.Column(db.Float, default=0.0)  # Current ability estimate
    current_theta_se = db.Column(db.Float)  # Current standard error
    theta_history = db.Column(db.JSON)  # History of theta estimates
    
    # Question Selection
    questions_asked = db.Column(db.JSON)  # List of question IDs
    questions_pool = db.Column(db.JSON)  # Available questions
    next_question_id = db.Column(db.Integer)  # Computed next question
    
    # Stopping Criteria Progress
    questions_asked_count = db.Column(db.Integer, default=0)
    target_se = db.Column(db.Float)  # Target standard error for stopping
    se_achieved = db.Column(db.Boolean, default=False)
    
    # Session Metadata
    algorithm = db.Column(db.String(50))  # 'max_information', 'bayesian', etc.
    parameters = db.Column(db.JSON)  # Algorithm-specific parameters
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attempt = db.relationship('UserAssessmentAttempt', backref='adaptive_session', uselist=False)
    
    def __repr__(self):
        return f'<AdaptiveTestSession {self.id}: Attempt {self.attempt_id} - θ={self.current_theta:.2f}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'attempt_id': self.attempt_id,
            'current_theta': self.current_theta,
            'current_theta_se': self.current_theta_se,
            'questions_asked_count': self.questions_asked_count,
            'next_question_id': self.next_question_id,
            'se_achieved': self.se_achieved,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
