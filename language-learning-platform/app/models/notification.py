"""
Notification System Models
Manages user notifications, preferences, and reminders
"""
from datetime import datetime
from .user import db

class NotificationType(db.Model):
    """Defines different types of notifications"""
    __tablename__ = 'notification_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "daily_reminder", "streak_alert"
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Material-UI icon name
    default_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    notifications = db.relationship('Notification', backref='type', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'default_enabled': self.default_enabled
        }
    
    def __repr__(self):
        return f'<NotificationType {self.name}>'


class Notification(db.Model):
    """Represents a notification sent to a user"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('notification_types.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_url = db.Column(db.String(500))  # URL to navigate when clicked
    action_text = db.Column(db.String(100))  # Button text (e.g., "Practice Now")
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Delivery channels
    in_app = db.Column(db.Boolean, default=True)
    email = db.Column(db.Boolean, default=False)
    push = db.Column(db.Boolean, default=False)
    
    # Metadata
    data = db.Column(db.JSON)  # Additional notification data (badge info, streak count, etc.)
    priority = db.Column(db.String(20), default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.to_dict() if self.type else None,
            'title': self.title,
            'message': self.message,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'is_read': self.is_read,
            'is_sent': self.is_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat(),
            'in_app': self.in_app,
            'email': self.email,
            'push': self.push,
            'data': self.data,
            'priority': self.priority
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'


class UserNotificationSettings(db.Model):
    """User preferences for notifications"""
    __tablename__ = 'user_notification_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Daily reminder settings
    daily_reminder_enabled = db.Column(db.Boolean, default=True)
    daily_reminder_time = db.Column(db.Time, default=datetime.strptime('19:00', '%H:%M').time())  # 7 PM
    timezone = db.Column(db.String(50), default='Asia/Kolkata')
    
    # Notification type preferences
    streak_alerts = db.Column(db.Boolean, default=True)
    achievement_notifications = db.Column(db.Boolean, default=True)
    new_content_notifications = db.Column(db.Boolean, default=True)
    personalized_tips = db.Column(db.Boolean, default=True)
    learning_path_updates = db.Column(db.Boolean, default=True)
    
    # Delivery channel preferences
    in_app_notifications = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=False)
    
    # Advanced settings
    quiet_hours_start = db.Column(db.Time)  # No notifications during these hours
    quiet_hours_end = db.Column(db.Time)
    weekend_reminders = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('notification_settings', uselist=False))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'daily_reminder_enabled': self.daily_reminder_enabled,
            'daily_reminder_time': self.daily_reminder_time.strftime('%H:%M') if self.daily_reminder_time else None,
            'timezone': self.timezone,
            'streak_alerts': self.streak_alerts,
            'achievement_notifications': self.achievement_notifications,
            'new_content_notifications': self.new_content_notifications,
            'personalized_tips': self.personalized_tips,
            'learning_path_updates': self.learning_path_updates,
            'in_app_notifications': self.in_app_notifications,
            'email_notifications': self.email_notifications,
            'push_notifications': self.push_notifications,
            'quiet_hours_start': self.quiet_hours_start.strftime('%H:%M') if self.quiet_hours_start else None,
            'quiet_hours_end': self.quiet_hours_end.strftime('%H:%M') if self.quiet_hours_end else None,
            'weekend_reminders': self.weekend_reminders,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<UserNotificationSettings for User {self.user_id}>'
