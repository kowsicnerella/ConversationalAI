
from .user import db
from datetime import datetime

class Badge(db.Model):
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.String(200))
    category = db.Column(db.String(50))  # achievement, streak, skill, milestone
    requirement_type = db.Column(db.String(50))  # activities_completed, streak_days, points_earned, etc.
    requirement_value = db.Column(db.Integer)  # threshold value for earning badge
    points_reward = db.Column(db.Integer, default=50)  # bonus points for earning badge
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_badges = db.relationship('UserBadge', backref='badge', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Badge {self.name}>'

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate badge awards
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)
    
    def __repr__(self):
        return f'<UserBadge {self.user.username} - {self.badge.name}>'

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    achievement_type = db.Column(db.String(50))  # daily, weekly, monthly, milestone
    target_value = db.Column(db.Integer)  # target to achieve
    points_reward = db.Column(db.Integer, default=25)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
