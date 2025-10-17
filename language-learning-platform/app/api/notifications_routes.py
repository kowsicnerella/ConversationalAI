from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.services.notification_service import NotificationService
from datetime import datetime
import json

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/", methods=["GET"])
@jwt_required()
def get_notifications():
    """Get user notifications with pagination"""
    try:
        user_id = int(get_jwt_identity())

        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)
        unread_only = request.args.get("unread_only", "false").lower() == "true"

        result = NotificationService.get_user_notifications(
            user_id=user_id, limit=limit, offset=offset, unread_only=unread_only
        )

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/mark-read/<int:notification_id>", methods=["POST"])
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a specific notification as read"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.mark_as_read(notification_id, user_id)

        if "error" in result:
            status_code = 404 if "not found" in result["error"].lower() else 403
            return jsonify(result), status_code

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/mark-all-read", methods=["POST"])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.mark_all_as_read(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error marking all notifications as read: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_notification_preferences():
    """Get user notification preferences"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.get_user_settings(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error getting notification preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/preferences", methods=["POST"])
@jwt_required()
def update_notification_preferences():
    """Update user notification preferences"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        result = NotificationService.update_user_settings(user_id, data)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error updating notification preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_all_notifications():
    """Delete all notifications for current user"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.clear_all_notifications(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error clearing notifications: {str(e)}")
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/<int:notification_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notification_id):
    """Delete a specific notification"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.delete_notification(notification_id, user_id)

        if "error" in result:
            status_code = 404 if "not found" in result["error"].lower() else 403
            return jsonify(result), status_code

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting notification: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Automated notification triggers
@notifications_bp.route("/test/daily-reminder", methods=["POST"])
@jwt_required()
def test_daily_reminder():
    """Test daily reminder notification (for testing)"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.send_daily_reminder(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/test/streak-alert", methods=["POST"])
@jwt_required()
def test_streak_alert():
    """Test streak alert notification (for testing)"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.send_streak_alert(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notifications_bp.route("/test/personalized-tip", methods=["POST"])
@jwt_required()
def test_personalized_tip():
    """Test personalized tip notification (for testing)"""
    try:
        user_id = int(get_jwt_identity())

        result = NotificationService.send_personalized_tip(user_id)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Initialize notification types on first request
@notifications_bp.before_app_request
def initialize_notification_system():
    """Initialize notification types in database"""
    NotificationService.initialize_notification_types()
