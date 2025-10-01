
from .user import db
from datetime import datetime

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')  # vocabulary, grammar, conversation, etc.
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    estimated_duration_hours = db.Column(db.Integer, default=1)  # in hours
    prerequisites = db.Column(db.JSON, default=list)  # List of prerequisite learning path IDs or skills
    learning_objectives = db.Column(db.JSON, default=list)  # List of learning objectives
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Enhanced adaptive learning fields
    is_adaptive = db.Column(db.Boolean, default=False)  # Whether this is an adaptive path
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # For personalized paths
    assessment_id = db.Column(db.Integer, db.ForeignKey('proficiency_assessments.id'))  # Source assessment
    
    # Adaptive learning configuration
    path_data = db.Column(db.JSON)  # Stores adaptive path structure and metadata
    adaptation_history = db.Column(db.JSON)  # History of how path has adapted
    priority_skills = db.Column(db.JSON)  # Ordered list of priority skills
    mastery_requirements = db.Column(db.JSON)  # Requirements for progression
    
    # AI generation metadata
    generation_source = db.Column(db.String(50))  # assessment, manual, template, etc.
    generation_metadata = db.Column(db.JSON)  # AI generation parameters and context
    
    # Performance tracking
    success_rate = db.Column(db.Float)  # Overall success rate of users on this path
    average_completion_time = db.Column(db.Float)  # Average time to complete (hours)
    difficulty_rating = db.Column(db.Float)  # User-reported difficulty rating
    
    # Relationships
    activities = db.relationship('Activity', backref='learning_path', lazy='dynamic', cascade='all, delete-orphan')
    created_by_user = db.relationship('User', foreign_keys=[user_id], backref='created_learning_paths')
    source_assessment = db.relationship('ProficiencyAssessment', backref='generated_learning_paths')
    
    def __repr__(self):
        return f'<LearningPath {self.title}>'

# User enrollment in learning paths (many-to-many relationship)
user_learning_paths = db.Table('user_learning_paths',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('learning_path_id', db.Integer, db.ForeignKey('learning_paths.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow),
    db.Column('completion_percentage', db.Float, default=0.0),
    db.Column('is_completed', db.Boolean, default=False)
)

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20), nullable=False)
    estimated_duration_hours = db.Column(db.Integer)  # in hours
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # This can be used for pre-defined courses
    def __repr__(self):
        return f'<Course {self.title}>'
