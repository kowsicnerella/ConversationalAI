"""
Learning Node Models for Phase 3 - Curriculum Framework
Implements CEFR-based curriculum system with skill taxonomy
"""

from .user import db
from datetime import datetime


class CurriculumLevel(db.Model):
    """
    CEFR-based curriculum levels (A1-C2)
    Defines learning objectives and vocabulary ranges for each level
    """
    __tablename__ = "phase3_curriculum_levels"

    id = db.Column(db.Integer, primary_key=True)
    cefr_level = db.Column(db.String(2), unique=True, nullable=False)  # A1, A2, B1, B2, C1, C2
    level_name = db.Column(db.String(50), nullable=False)  # Beginner, Elementary, etc.
    description = db.Column(db.Text)
    
    # Vocabulary requirements
    vocabulary_range_min = db.Column(db.Integer, default=0)
    vocabulary_range_max = db.Column(db.Integer, default=500)
    
    # Grammar concepts at this level
    grammar_concepts = db.Column(db.JSON)  # List of grammar topics
    
    # Functional skills at this level
    functional_skills = db.Column(db.JSON)  # List of real-world skills
    
    # Time estimate to complete this level
    estimated_hours = db.Column(db.Integer, default=40)
    
    # Prerequisite level
    prerequisite_level_id = db.Column(db.Integer, db.ForeignKey('phase3_curriculum_levels.id'))
    
    # Order in progression
    level_order = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (using class name directly to avoid ambiguity)
    # Note: Relationships will be set up after all models are defined
    
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
            'estimated_hours': self.estimated_hours,
            'level_order': self.level_order
        }
    
    def get_learning_nodes(self):
        """Get all learning nodes for this curriculum level"""
        return LearningNode.query.filter_by(curriculum_level_id=self.id).all()


class SkillDomain(db.Model):
    """
    Defines the 6 core skill domains and their sub-skills
    """
    __tablename__ = "phase3_skill_domains"

    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(50), unique=True, nullable=False)  # Listening, Speaking, etc.
    description = db.Column(db.Text)
    
    # Sub-skills within this domain (JSON array)
    sub_skills = db.Column(db.JSON)  # e.g., ["phoneme recognition", "word recognition", ...]
    
    # Assessment criteria for this skill
    assessment_criteria = db.Column(db.JSON)  # e.g., {"accuracy": 0.8, "speed": 0.7}
    
    # Mastery thresholds (0-1 scale)
    mastery_thresholds = db.Column(db.JSON)  # {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.8}
    
    # Icon or color for UI
    icon = db.Column(db.String(100))
    color = db.Column(db.String(20))
    
    # Order of display
    order = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships removed to avoid class name conflicts with Phase 1 models
    # Use direct queries: LearningNode.query.filter_by(skill_domain_id=self.id).all()
    
    def __repr__(self):
        return f"<SkillDomain {self.domain_name}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'domain_name': self.domain_name,
            'description': self.description,
            'sub_skills': self.sub_skills or [],
            'assessment_criteria': self.assessment_criteria or {},
            'mastery_thresholds': self.mastery_thresholds or {},
            'icon': self.icon,
            'color': self.color
        }


class LearningNode(db.Model):
    """
    Atomic learning unit in the curriculum
    Each node represents a specific concept/skill to master
    """
    __tablename__ = "phase3_learning_nodes"

    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique identifier (e.g., "A1_GREETING_001")
    
    # Level and skill association
    curriculum_level_id = db.Column(db.Integer, db.ForeignKey('phase3_curriculum_levels.id'), nullable=False)
    skill_domain_id = db.Column(db.Integer, db.ForeignKey('phase3_skill_domains.id'), nullable=False)
    
    # Node information
    concept_name = db.Column(db.String(200), nullable=False)  # e.g., "Present Simple Tense"
    description = db.Column(db.Text)
    
    # Learning objectives at this node
    learning_objectives = db.Column(db.JSON)  # List of specific learning goals
    
    # Prerequisites (list of node IDs that must be completed first)
    prerequisite_node_ids = db.Column(db.JSON, default=list)
    
    # Activity templates for this node (types of activities suitable)
    activity_templates = db.Column(db.JSON)  # e.g., ["quiz", "flashcard", "writing", ...]
    
    # Difficulty range (0-1 continuous scale)
    difficulty_min = db.Column(db.Float, default=0.1)
    difficulty_max = db.Column(db.Float, default=0.9)
    recommended_difficulty = db.Column(db.Float, default=0.5)
    
    # Time to complete
    estimated_time_minutes = db.Column(db.Integer, default=15)
    
    # Mastery threshold (score needed to master this node)
    mastery_threshold = db.Column(db.Float, default=0.8)
    
    # Vocabulary words associated with this node
    vocabulary_ids = db.Column(db.JSON, default=list)  # IDs of vocabulary words
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships removed to avoid class name conflicts
    # Use direct queries: UserLearningNodeProgress.query.filter_by(learning_node_id=self.id).all()
    
    def __repr__(self):
        return f"<LearningNode {self.node_id} - {self.concept_name}>"
    
    def to_dict(self):
        # Manually fetch related objects to avoid relationship conflicts
        curriculum_level = CurriculumLevel.query.get(self.curriculum_level_id)
        skill_domain = SkillDomain.query.get(self.skill_domain_id)
        
        return {
            'id': self.id,
            'node_id': self.node_id,
            'concept_name': self.concept_name,
            'description': self.description,
            'learning_objectives': self.learning_objectives or [],
            'prerequisite_node_ids': self.prerequisite_node_ids or [],
            'activity_templates': self.activity_templates or [],
            'difficulty_range': {
                'min': self.difficulty_min,
                'max': self.difficulty_max,
                'recommended': self.recommended_difficulty
            },
            'estimated_time_minutes': self.estimated_time_minutes,
            'mastery_threshold': self.mastery_threshold,
            'curriculum_level': curriculum_level.cefr_level if curriculum_level else None,
            'skill_domain': skill_domain.domain_name if skill_domain else None
        }


class UserLearningNodeProgress(db.Model):
    """
    Track user's progress through individual learning nodes
    """
    __tablename__ = "phase3_user_learning_node_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_node_id = db.Column(db.Integer, db.ForeignKey('phase3_learning_nodes.id'), nullable=False)
    
    # Progress status
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, mastered
    
    # Performance metrics
    attempts = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Float)  # Best performance score
    average_score = db.Column(db.Float)  # Average across all attempts
    current_score = db.Column(db.Float)  # Most recent attempt
    
    # Mastery assessment
    mastery_level = db.Column(db.String(20))  # beginner, learning, proficient, mastered
    confidence_score = db.Column(db.Float)  # Confidence in user's mastery (0-1)
    
    # Time tracking
    total_time_minutes = db.Column(db.Integer, default=0)
    first_attempt_date = db.Column(db.DateTime)
    last_attempt_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    mastery_date = db.Column(db.DateTime)
    
    # Learning patterns
    struggle_indicators = db.Column(db.JSON)  # Areas of difficulty
    common_errors = db.Column(db.JSON)  # Frequently made mistakes
    hint_count = db.Column(db.Integer, default=0)  # Hints used
    
    # Scheduling
    needs_review = db.Column(db.Boolean, default=False)
    next_review_date = db.Column(db.DateTime)  # For spaced repetition
    review_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserLearningNodeProgress User:{self.user_id} Node:{self.learning_node_id}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'learning_node_id': self.learning_node_id,
            'status': self.status,
            'attempts': self.attempts,
            'best_score': self.best_score,
            'average_score': self.average_score,
            'current_score': self.current_score,
            'mastery_level': self.mastery_level,
            'confidence_score': self.confidence_score,
            'total_time_minutes': self.total_time_minutes,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'needs_review': self.needs_review,
            'next_review_date': self.next_review_date.isoformat() if self.next_review_date else None
        }


class UserSkillProfile(db.Model):
    """
    Aggregated skill proficiency across all 6 skill domains
    Updated after each activity completion
    """
    __tablename__ = "phase3_user_skill_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Skill levels (0-100 scale for each domain)
    listening_level = db.Column(db.Float, default=0)
    speaking_level = db.Column(db.Float, default=0)
    reading_level = db.Column(db.Float, default=0)
    writing_level = db.Column(db.Float, default=0)
    vocabulary_level = db.Column(db.Float, default=0)
    grammar_level = db.Column(db.Float, default=0)
    
    # Overall level (average of all 6)
    overall_level = db.Column(db.Float, default=0)
    
    # Trends (improvement/decline)
    listening_trend = db.Column(db.String(20), default='stable')  # improving, stable, declining
    speaking_trend = db.Column(db.String(20), default='stable')
    reading_trend = db.Column(db.String(20), default='stable')
    writing_trend = db.Column(db.String(20), default='stable')
    vocabulary_trend = db.Column(db.String(20), default='stable')
    grammar_trend = db.Column(db.String(20), default='stable')
    
    # Weak and strong areas
    weak_areas = db.Column(db.JSON)  # Skills needing improvement
    strong_areas = db.Column(db.JSON)  # Skills excelling in
    focus_area = db.Column(db.String(50))  # Current focus (primary weak area)
    
    # Last updated
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserSkillProfile User:{self.user_id} Overall:{self.overall_level:.1f}>"
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'skill_levels': {
                'listening': self.listening_level,
                'speaking': self.speaking_level,
                'reading': self.reading_level,
                'writing': self.writing_level,
                'vocabulary': self.vocabulary_level,
                'grammar': self.grammar_level,
                'overall': self.overall_level
            },
            'trends': {
                'listening': self.listening_trend,
                'speaking': self.speaking_trend,
                'reading': self.reading_trend,
                'writing': self.writing_trend,
                'vocabulary': self.vocabulary_trend,
                'grammar': self.grammar_trend
            },
            'weak_areas': self.weak_areas or [],
            'strong_areas': self.strong_areas or [],
            'focus_area': self.focus_area
        }
