
from .user import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # quiz, flashcard, reading, writing, role_play, image_recognition
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.JSON, nullable=False)  # Stores the AI-generated JSON content
    difficulty_level = db.Column(db.String(20), default='beginner')
    order_in_path = db.Column(db.Integer, nullable=False)
    estimated_duration_minutes = db.Column(db.Integer, default=10)  # in minutes
    points_reward = db.Column(db.Integer, default=10)  # points awarded for completion
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_logs = db.relationship('UserActivityLog', backref='activity', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Activity {self.title} ({self.activity_type})>'

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer)  # Score achieved (e.g., 4/5 for quiz)
    max_score = db.Column(db.Integer)  # Maximum possible score
    time_spent_minutes = db.Column(db.Integer)  # Time spent on activity
    user_response = db.Column(db.JSON)  # User's responses/answers
    feedback_provided = db.Column(db.JSON)  # AI feedback if applicable
    is_completed = db.Column(db.Boolean, default=True)
    
    # For tracking attempts
    attempt_number = db.Column(db.Integer, default=1)
    
    def __repr__(self):
        return f'<UserActivityLog {self.user.username} - {self.activity.title}>'
