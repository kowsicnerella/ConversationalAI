"""
Notification Service
Manages user notifications, reminders, and automated alerts
"""

from datetime import datetime, timedelta, time as datetime_time
from app.models import (
    db,
    User,
    Notification,
    NotificationType,
    UserNotificationSettings,
    LearningStreak,
    UserBadge,
    UserEnrollment,
    ChapterProgress,
)
from config import Config


class NotificationService:
    """Service for managing notifications and reminders"""

    # Predefined notification types
    NOTIFICATION_TYPES = {
        "daily_reminder": {
            "display_name": "Daily Practice Reminder",
            "description": "Reminds you to practice English daily",
            "icon": "NotificationsActive",
            "default_enabled": True,
        },
        "streak_alert": {
            "display_name": "Streak Alert",
            "description": "Alerts when your streak is at risk",
            "icon": "Whatshot",
            "default_enabled": True,
        },
        "achievement_unlocked": {
            "display_name": "Achievement Unlocked",
            "description": "Notifies when you unlock new badges or achievements",
            "icon": "EmojiEvents",
            "default_enabled": True,
        },
        "new_content": {
            "display_name": "New Content Available",
            "description": "Notifies when new learning paths or content is available",
            "icon": "NewReleases",
            "default_enabled": True,
        },
        "personalized_tip": {
            "display_name": "Personalized Tip",
            "description": "Daily learning tips based on your progress",
            "icon": "Lightbulb",
            "default_enabled": True,
        },
        "learning_path_update": {
            "display_name": "Learning Path Update",
            "description": "Updates on your enrolled learning paths",
            "icon": "School",
            "default_enabled": True,
        },
        "milestone_achieved": {
            "display_name": "Milestone Achieved",
            "description": "Celebrate when you reach important milestones",
            "icon": "Flag",
            "default_enabled": True,
        },
    }

    @staticmethod
    def initialize_notification_types():
        """Initialize notification types in database if not exists"""
        try:
            for name, data in NotificationService.NOTIFICATION_TYPES.items():
                existing = NotificationType.query.filter_by(name=name).first()

                if not existing:
                    notif_type = NotificationType(
                        name=name,
                        display_name=data["display_name"],
                        description=data["description"],
                        icon=data["icon"],
                        default_enabled=data["default_enabled"],
                    )
                    db.session.add(notif_type)

            db.session.commit()
            return {"success": True, "message": "Notification types initialized"}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to initialize notification types: {str(e)}"}

    @staticmethod
    def create_user_settings(user_id):
        """Create default notification settings for a user"""
        try:
            # Check if settings already exist
            existing = UserNotificationSettings.query.filter_by(user_id=user_id).first()

            if existing:
                return {
                    "success": True,
                    "settings": existing.to_dict(),
                    "message": "Settings already exist",
                }

            # Create default settings
            settings = UserNotificationSettings(user_id=user_id)
            db.session.add(settings)
            db.session.commit()

            return {"success": True, "settings": settings.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create settings: {str(e)}"}

    @staticmethod
    def get_user_settings(user_id):
        """Get notification settings for a user"""
        try:
            settings = UserNotificationSettings.query.filter_by(user_id=user_id).first()

            if not settings:
                # Create default settings
                result = NotificationService.create_user_settings(user_id)
                if "error" in result:
                    return result
                settings = UserNotificationSettings.query.filter_by(
                    user_id=user_id
                ).first()

            return {"success": True, "settings": settings.to_dict()}

        except Exception as e:
            return {"error": f"Failed to get settings: {str(e)}"}

    @staticmethod
    def update_user_settings(user_id, settings_data):
        """Update notification settings for a user"""
        try:
            settings = UserNotificationSettings.query.filter_by(user_id=user_id).first()

            if not settings:
                # Create if doesn't exist
                result = NotificationService.create_user_settings(user_id)
                if "error" in result:
                    return result
                settings = UserNotificationSettings.query.filter_by(
                    user_id=user_id
                ).first()

            # Update settings
            updatable_fields = [
                "daily_reminder_enabled",
                "daily_reminder_time",
                "timezone",
                "streak_alerts",
                "achievement_notifications",
                "new_content_notifications",
                "personalized_tips",
                "learning_path_updates",
                "in_app_notifications",
                "email_notifications",
                "push_notifications",
                "quiet_hours_start",
                "quiet_hours_end",
                "weekend_reminders",
            ]

            for field in updatable_fields:
                if field in settings_data:
                    value = settings_data[field]

                    # Convert time strings to time objects
                    if field in [
                        "daily_reminder_time",
                        "quiet_hours_start",
                        "quiet_hours_end",
                    ]:
                        if value and isinstance(value, str):
                            try:
                                value = datetime.strptime(value, "%H:%M").time()
                            except ValueError:
                                continue

                    setattr(settings, field, value)

            settings.updated_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "settings": settings.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update settings: {str(e)}"}

    @staticmethod
    def create_notification(
        user_id,
        notification_type,
        title,
        message,
        action_url=None,
        action_text=None,
        data=None,
        priority="normal",
    ):
        """
        Create a new notification for a user

        Args:
            user_id (int): User ID
            notification_type (str): Type name (e.g., 'daily_reminder')
            title (str): Notification title
            message (str): Notification message
            action_url (str): Optional URL to navigate
            action_text (str): Optional button text
            data (dict): Optional additional data
            priority (str): Priority level ('low', 'normal', 'high', 'urgent')

        Returns:
            dict: Created notification or error
        """
        try:
            # Get notification type
            notif_type = NotificationType.query.filter_by(
                name=notification_type
            ).first()

            if not notif_type:
                return {"error": f"Notification type {notification_type} not found"}

            # Check user settings
            settings = UserNotificationSettings.query.filter_by(user_id=user_id).first()

            if not settings:
                # Create default settings
                NotificationService.create_user_settings(user_id)
                settings = UserNotificationSettings.query.filter_by(
                    user_id=user_id
                ).first()

            # Check if this notification type is enabled
            type_enabled = True
            if notification_type == "streak_alert":
                type_enabled = settings.streak_alerts
            elif notification_type == "achievement_unlocked":
                type_enabled = settings.achievement_notifications
            elif notification_type == "new_content":
                type_enabled = settings.new_content_notifications
            elif notification_type == "personalized_tip":
                type_enabled = settings.personalized_tips
            elif notification_type == "learning_path_update":
                type_enabled = settings.learning_path_updates

            if not type_enabled:
                return {
                    "success": True,
                    "message": "Notification type disabled for user",
                }

            # Create notification
            notification = Notification(
                user_id=user_id,
                type_id=notif_type.id,
                title=title,
                message=message,
                action_url=action_url,
                action_text=action_text,
                data=data,
                priority=priority,
                in_app=settings.in_app_notifications,
                email=settings.email_notifications,
                push=settings.push_notifications,
            )

            db.session.add(notification)
            db.session.commit()

            return {"success": True, "notification": notification.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create notification: {str(e)}"}

    @staticmethod
    def get_user_notifications(user_id, limit=50, offset=0, unread_only=False):
        """Get notifications for a user"""
        try:
            query = Notification.query.filter_by(user_id=user_id)

            if unread_only:
                query = query.filter_by(is_read=False)

            total = query.count()
            unread_count = Notification.query.filter_by(
                user_id=user_id, is_read=False
            ).count()

            notifications = (
                query.order_by(Notification.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return {
                "success": True,
                "notifications": [n.to_dict() for n in notifications],
                "total": total,
                "unread_count": unread_count,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            return {"error": f"Failed to get notifications: {str(e)}"}

    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a notification as read"""
        try:
            notification = Notification.query.get(notification_id)

            if not notification:
                return {"error": "Notification not found"}

            if notification.user_id != user_id:
                return {"error": "Unauthorized access"}

            notification.is_read = True
            notification.read_at = datetime.utcnow()

            db.session.commit()

            return {"success": True, "notification": notification.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to mark as read: {str(e)}"}

    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id, is_read=False
            ).all()

            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()

            db.session.commit()

            return {
                "success": True,
                "message": f"Marked {len(notifications)} notifications as read",
            }

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to mark all as read: {str(e)}"}

    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete a notification"""
        try:
            notification = Notification.query.get(notification_id)

            if not notification:
                return {"error": "Notification not found"}

            if notification.user_id != user_id:
                return {"error": "Unauthorized access"}

            db.session.delete(notification)
            db.session.commit()

            return {"success": True, "message": "Notification deleted"}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete notification: {str(e)}"}

    @staticmethod
    def clear_all_notifications(user_id):
        """Delete all notifications for a user"""
        try:
            Notification.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            return {"success": True, "message": "All notifications cleared"}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to clear notifications: {str(e)}"}

    # ==================== AUTOMATED NOTIFICATIONS ====================

    @staticmethod
    def send_daily_reminder(user_id):
        """Send daily practice reminder"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Check user's streak
            streak = LearningStreak.query.filter_by(user_id=user_id).first()
            streak_days = streak.current_streak if streak else 0

            title = "Time to practice English! 📚"
            message = (
                f"Your {streak_days}-day streak is waiting! Keep up the great work!"
            )

            if streak_days == 0:
                message = (
                    "Start your learning journey today! Practice makes perfect. 🌟"
                )
            elif streak_days >= 7:
                message = f"Amazing {streak_days}-day streak! Don't break it today! 🔥"

            return NotificationService.create_notification(
                user_id=user_id,
                notification_type="daily_reminder",
                title=title,
                message=message,
                action_url="/dashboard",
                action_text="Practice Now",
                priority="normal",
            )

        except Exception as e:
            return {"error": f"Failed to send daily reminder: {str(e)}"}

    @staticmethod
    def send_streak_alert(user_id):
        """Send streak at risk alert"""
        try:
            streak = LearningStreak.query.filter_by(user_id=user_id).first()

            if not streak or streak.current_streak == 0:
                return {"success": True, "message": "No active streak"}

            title = f"Don't break your {streak.current_streak}-day streak! 🔥"
            message = f"You haven't practiced today. Keep your {streak.current_streak}-day streak alive!"

            return NotificationService.create_notification(
                user_id=user_id,
                notification_type="streak_alert",
                title=title,
                message=message,
                action_url="/activities",
                action_text="Practice Now",
                data={"streak_days": streak.current_streak},
                priority="high",
            )

        except Exception as e:
            return {"error": f"Failed to send streak alert: {str(e)}"}

    @staticmethod
    def send_achievement_notification(user_id, badge_id):
        """Send achievement unlocked notification"""
        try:
            user_badge = UserBadge.query.filter_by(
                user_id=user_id, badge_id=badge_id
            ).first()

            if not user_badge:
                return {"error": "Badge not found"}

            badge = user_badge.badge

            title = f"🎉 You unlocked '{badge.name}' badge!"
            message = f"{badge.description}\n\nReward: {badge.reward_points} points!"

            return NotificationService.create_notification(
                user_id=user_id,
                notification_type="achievement_unlocked",
                title=title,
                message=message,
                action_url="/gamification",
                action_text="View Badges",
                data={
                    "badge_id": badge.id,
                    "badge_name": badge.name,
                    "reward_points": badge.reward_points,
                },
                priority="high",
            )

        except Exception as e:
            return {"error": f"Failed to send achievement notification: {str(e)}"}

    @staticmethod
    def send_personalized_tip(user_id):
        """Send personalized learning tip based on user progress"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Get user's recent progress
            enrollments = UserEnrollment.query.filter_by(user_id=user_id).count()
            completed_chapters = ChapterProgress.query.filter_by(
                user_id=user_id, status="completed"
            ).count()

            # Generate personalized tip
            tips = [
                {
                    "title": "🌟 You're doing great with vocabulary!",
                    "message": "Try role-play scenarios next to practice using these words in context.",
                    "action_url": "/activities/role-play",
                },
                {
                    "title": "💡 Tip: Practice daily for best results",
                    "message": "Just 15 minutes a day can make a huge difference in your English learning journey!",
                    "action_url": "/dashboard",
                },
                {
                    "title": "📚 Explore new learning paths",
                    "message": f"You've completed {completed_chapters} chapters! Check out new learning paths to expand your skills.",
                    "action_url": "/learning-paths",
                },
                {
                    "title": "🎯 Set a learning goal",
                    "message": "Setting goals helps you stay motivated. What do you want to achieve this week?",
                    "action_url": "/goals",
                },
            ]

            # Select tip based on user progress
            import random

            tip = random.choice(tips)

            return NotificationService.create_notification(
                user_id=user_id,
                notification_type="personalized_tip",
                title=tip["title"],
                message=tip["message"],
                action_url=tip.get("action_url"),
                action_text="Learn More",
                priority="normal",
            )

        except Exception as e:
            return {"error": f"Failed to send personalized tip: {str(e)}"}
