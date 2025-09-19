
from .user import db
from datetime import datetime

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    completion_percentage = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='learning_path', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LearningPath {self.title}>'

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
