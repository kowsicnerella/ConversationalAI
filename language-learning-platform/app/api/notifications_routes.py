from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from datetime import datetime
import json

notifications_bp = Blueprint('notifications', __name__)

# In-memory storage for demo (in production, use database table)
user_notifications = {}

@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications with pagination"""
    try:
        user_id = int(get_jwt_identity())
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Get user notifications (demo data)
        notifications = user_notifications.get(str(user_id), [])
        
        if unread_only:
            notifications = [n for n in notifications if not n.get('read', False)]
        
        # Simple pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_notifications = notifications[start:end]
        
        total = len(notifications)
        pages = (total + per_page - 1) // per_page
        
        return jsonify({
            'message': 'Notifications retrieved successfully',
            'telugu_message': 'నోటిఫికేషన్లు విజయవంతంగా పొందబడ్డాయి',
            'notifications': paginated_notifications,
            'pagination': {
                'page': page,
                'pages': pages,
                'per_page': per_page,
                'total': total,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({
            'error': 'Failed to get notifications',
            'telugu_error': 'నోటిఫికేషన్లు పొందడంలో విఫలం'
        }), 500

@notifications_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user_id = int(get_jwt_identity())
        
        notifications = user_notifications.get(str(user_id), [])
        
        for notification in notifications:
            if notification.get('id') == notification_id:
                notification['read'] = True
                notification['read_at'] = datetime.utcnow().isoformat()
                break
        else:
            return jsonify({
                'error': 'Notification not found',
                'telugu_error': 'నోటిఫికేషన్ కనుగొనబడలేదు'
            }), 404
        
        user_notifications[str(user_id)] = notifications
        
        return jsonify({
            'message': 'Notification marked as read',
            'telugu_message': 'నోటిఫికేషన్ చదివినట్లు గుర్తించబడింది'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({
            'error': 'Failed to mark notification as read',
            'telugu_error': 'నోటిఫికేషన్ చదివినట్లు గుర్తించడంలో విఫలం'
        }), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        user_id = int(get_jwt_identity())
        
        notifications = user_notifications.get(str(user_id), [])
        current_time = datetime.utcnow().isoformat()
        
        for notification in notifications:
            if not notification.get('read', False):
                notification['read'] = True
                notification['read_at'] = current_time
        
        user_notifications[str(user_id)] = notifications
        
        return jsonify({
            'message': 'All notifications marked as read',
            'telugu_message': 'అన్ని నోటిఫికేషన్లు చదివినట్లు గుర్తించబడ్డాయి'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
        return jsonify({
            'error': 'Failed to mark all notifications as read',
            'telugu_error': 'అన్ని నోటిఫికేషన్లు చదివినట్లు గుర్తించడంలో విఫలం'
        }), 500

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get user notification preferences"""
    try:
        user_id = int(get_jwt_identity())
        
        # Default preferences (in production, store in database)
        default_preferences = {
            'learning_reminders': True,
            'achievement_alerts': True,
            'daily_challenge': True,
            'weekly_progress': True,
            'new_content': True,
            'social_interactions': False,
            'email_notifications': True,
            'push_notifications': True,
            'reminder_time': '18:00',  # 6 PM
            'reminder_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        }
        
        return jsonify({
            'message': 'Notification preferences retrieved successfully',
            'telugu_message': 'నోటిఫికేషన్ ప్రాధాన్యతలు విజయవంతంగా పొందబడ్డాయి',
            'preferences': default_preferences
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting notification preferences: {str(e)}")
        return jsonify({
            'error': 'Failed to get notification preferences',
            'telugu_error': 'నోటిఫికేషన్ ప్రాధాన్యతలు పొందడంలో విఫలం'
        }), 500

@notifications_bp.route('/preferences', methods=['POST'])
@jwt_required()
def update_notification_preferences():
    """Update user notification preferences"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate preference data
        valid_preferences = [
            'learning_reminders', 'achievement_alerts', 'daily_challenge',
            'weekly_progress', 'new_content', 'social_interactions',
            'email_notifications', 'push_notifications', 'reminder_time',
            'reminder_days'
        ]
        
        preferences = {}
        for key, value in data.items():
            if key in valid_preferences:
                preferences[key] = value
        
        # In production, save to database
        # For now, just return success
        
        return jsonify({
            'message': 'Notification preferences updated successfully',
            'telugu_message': 'నోటిఫికేషన్ ప్రాధాన్యతలు విజయవంతంగా నవీకరించబడ్డాయి',
            'preferences': preferences
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating notification preferences: {str(e)}")
        return jsonify({
            'error': 'Failed to update notification preferences',
            'telugu_error': 'నోటిఫికేషన్ ప్రాధాన్యతలు నవీకరించడంలో విఫలం'
        }), 500

@notifications_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    """Send a notification to user (internal use)"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        title = data.get('title', '')
        message = data.get('message', '')
        type = data.get('type', 'info')  # info, success, warning, error
        action_url = data.get('action_url', '')
        
        if not user_id or not message:
            return jsonify({
                'error': 'user_id and message are required',
                'telugu_error': 'వినియోగదారు ID మరియు సందేశం అవసరం'
            }), 400
        
        # Create notification
        notification = {
            'id': len(user_notifications.get(str(user_id), [])) + 1,
            'title': title,
            'message': message,
            'type': type,
            'action_url': action_url,
            'read': False,
            'created_at': datetime.utcnow().isoformat(),
            'read_at': None
        }
        
        # Add to user notifications
        if str(user_id) not in user_notifications:
            user_notifications[str(user_id)] = []
        
        user_notifications[str(user_id)].insert(0, notification)  # Add to beginning
        
        # Keep only last 100 notifications per user
        user_notifications[str(user_id)] = user_notifications[str(user_id)][:100]
        
        return jsonify({
            'message': 'Notification sent successfully',
            'telugu_message': 'నోటిఫికేషన్ విజయవంతంగా పంపబడింది',
            'notification_id': notification['id']
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error sending notification: {str(e)}")
        return jsonify({
            'error': 'Failed to send notification',
            'telugu_error': 'నోటిఫికేషన్ పంపడంలో విఫలం'
        }), 500

# Helper function to create sample notifications for testing
def create_sample_notifications(user_id):
    """Create sample notifications for testing"""
    sample_notifications = [
        {
            'id': 1,
            'title': 'Daily Challenge Available!',
            'message': 'Your daily Telugu learning challenge is ready. Complete it to maintain your streak!',
            'type': 'info',
            'action_url': '/daily-challenge',
            'read': False,
            'created_at': datetime.utcnow().isoformat(),
            'read_at': None
        },
        {
            'id': 2,
            'title': 'Congratulations!',
            'message': 'You earned the "Word Master" badge for learning 50 new vocabulary words!',
            'type': 'success',
            'action_url': '/profile/badges',
            'read': False,
            'created_at': datetime.utcnow().isoformat(),
            'read_at': None
        },
        {
            'id': 3,
            'title': 'Learning Reminder',
            'message': 'Don\'t forget to practice today! You\'re on a 5-day streak.',
            'type': 'warning',
            'action_url': '/dashboard',
            'read': True,
            'created_at': datetime.utcnow().isoformat(),
            'read_at': datetime.utcnow().isoformat()
        }
    ]
    
    user_notifications[str(user_id)] = sample_notifications

@notifications_bp.route('/create-samples/<int:user_id>', methods=['POST'])
def create_sample_notifications_endpoint(user_id):
    """Create sample notifications for testing (development only)"""
    try:
        create_sample_notifications(user_id)
        return jsonify({
            'message': 'Sample notifications created successfully',
            'telugu_message': 'నమూనా నోటిఫికేషన్లు విజయవంతంగా సృష్టించబడ్డాయి'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating sample notifications: {str(e)}")
        return jsonify({
            'error': 'Failed to create sample notifications',
            'telugu_error': 'నమూనా నోటిఫికేషన్లు సృష్టించడంలో విఫలం'
        }), 500