
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)  # Increased from 128 to 255 for modern hash algorithms
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Additional user preferences
    timezone = db.Column(db.String(50), default='Asia/Kolkata')
    learning_goals = db.Column(db.Text)  # JSON string for learning goals
    notification_preferences = db.Column(db.Text)  # JSON string for notification settings
    privacy_settings = db.Column(db.Text)  # JSON string for privacy settings
    enrollment_data = db.Column(db.JSON, default=dict)  # JSON for enrollment tracking data
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    activity_logs = db.relationship('UserActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_badges = db.relationship('UserBadge', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Many-to-many relationship with learning paths
    enrolled_paths = db.relationship('LearningPath', 
                                   secondary='user_learning_paths',
                                   backref=db.backref('enrolled_users', lazy='dynamic'),
                                   lazy='dynamic')
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def set_learning_goals(self, goals_list):
        """Set learning goals as JSON string"""
        self.learning_goals = json.dumps(goals_list) if goals_list else None
    
    def get_learning_goals(self):
        """Get learning goals as Python list"""
        return json.loads(self.learning_goals) if self.learning_goals else []
    
    def set_notification_preferences(self, preferences_dict):
        """Set notification preferences as JSON string"""
        self.notification_preferences = json.dumps(preferences_dict) if preferences_dict else None
    
    def get_notification_preferences(self):
        """Get notification preferences as Python dict"""
        return json.loads(self.notification_preferences) if self.notification_preferences else {}
    
    def set_privacy_settings(self, settings_dict):
        """Set privacy settings as JSON string"""
        self.privacy_settings = json.dumps(settings_dict) if settings_dict else None
    
    def get_privacy_settings(self):
        """Get privacy settings as Python dict"""
        return json.loads(self.privacy_settings) if self.privacy_settings else {}
    
    def __repr__(self):
        return f'<User {self.username}>'

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text)  # User biography/description
    native_language = db.Column(db.String(50), default='Telugu')  # For Telugu speakers
    target_language = db.Column(db.String(50), default='English')  # Learning English
    proficiency_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)  # Track longest learning streak
    points = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Profile for {self.user.username}>'
