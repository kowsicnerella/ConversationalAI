
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    activity_logs = db.relationship('UserActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    learning_paths = db.relationship('LearningPath', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    user_badges = db.relationship('UserBadge', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    native_language = db.Column(db.String(50), default='Telugu')  # For Telugu speakers
    target_language = db.Column(db.String(50), default='English')  # Learning English
    proficiency_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    current_streak = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Profile for {self.user.username}>'
