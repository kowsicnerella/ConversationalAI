"""
User Status Routes
Handles user onboarding status, learning phase, and navigation guards
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, Profile, ProficiencyAssessment

user_status_bp = Blueprint("user_status", __name__)


@user_status_bp.route("/user/status", methods=["GET"])
@jwt_required()
def get_user_status():
    """
    Get comprehensive user status for navigation and routing decisions.
    Returns user's onboarding status, learning phase, and required next steps.
    """
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        profile = Profile.query.filter_by(user_id=user_id).first()
        
        # Check assessment status
        assessment = None
        assessment_completed = False
        if user.initial_assessment_id:
            assessment = db.session.get(ProficiencyAssessment, user.initial_assessment_id)
            if assessment:
                assessment_completed = assessment.completed_at is not None

        # Determine required action and redirect path
        required_action = None
        redirect_to = None
        show_navbar = True
        
        if not user.onboarding_completed:
            show_navbar = False
            
            if user.needs_initial_assessment and not assessment_completed:
                required_action = "take_assessment"
                redirect_to = "/assessment"
            elif assessment_completed and user.current_learning_phase == "assessment":
                required_action = "complete_onboarding"
                redirect_to = "/onboarding"
            elif user.current_learning_phase == "onboarding":
                required_action = "complete_onboarding"
                redirect_to = "/onboarding"
            else:
                required_action = "complete_onboarding"
                redirect_to = "/onboarding"
        else:
            show_navbar = True
            required_action = "none"
            redirect_to = "/dashboard"

        return jsonify({
            "success": True,
            "user_status": {
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                
                # Onboarding status
                "onboarding_completed": user.onboarding_completed,
                "needs_initial_assessment": user.needs_initial_assessment,
                "current_learning_phase": user.current_learning_phase,
                
                # Assessment status
                "assessment": {
                    "taken": user.initial_assessment_id is not None,
                    "completed": assessment_completed,
                    "assessment_id": user.initial_assessment_id,
                    "proficiency_level": assessment.proficiency_level if assessment else None,
                },
                
                # Profile info
                "profile": {
                    "native_language": profile.native_language if profile else "Telugu",
                    "target_language": profile.target_language if profile else "English",
                    "proficiency_level": profile.proficiency_level if profile else "beginner",
                    "points": profile.points if profile else 0,
                    "current_streak": profile.current_streak if profile else 0,
                } if profile else None,
                
                # Navigation control
                "navigation": {
                    "show_navbar": show_navbar,
                    "required_action": required_action,
                    "redirect_to": redirect_to,
                    "can_access_dashboard": user.onboarding_completed,
                    "can_access_activities": user.onboarding_completed,
                    "can_access_learning_paths": user.onboarding_completed,
                }
            }
        }), 200

    except Exception as e:
        print(f"Error getting user status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to get user status: {str(e)}"}), 500


@user_status_bp.route("/user/can-access/<path:route_path>", methods=["GET"])
@jwt_required()
def can_access_route(route_path):
    """
    Check if user can access a specific route based on their onboarding status.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Public routes (always accessible)
        public_routes = [
            "onboarding",
            "assessment",
            "assessment-results",
            "profile",
            "settings"
        ]

        # Protected routes (need onboarding completion)
        protected_routes = [
            "dashboard",
            "learning-paths",
            "activities",
            "vocabulary",
            "goals",
            "practice",
            "chat",
            "chat-tutor",
            "analytics",
            "leaderboard",
            "image-learning"
        ]

        # Check if route is public
        if any(route in route_path for route in public_routes):
            can_access = True
            reason = "Public route"
        # Check if route is protected and user completed onboarding
        elif any(route in route_path for route in protected_routes):
            can_access = user.onboarding_completed
            reason = "Onboarding completed" if can_access else "Onboarding required"
        else:
            # Unknown route - allow by default
            can_access = True
            reason = "Unknown route - allowing access"

        return jsonify({
            "success": True,
            "can_access": can_access,
            "reason": reason,
            "redirect_to": "/onboarding" if not can_access else None,
            "user_status": {
                "onboarding_completed": user.onboarding_completed,
                "current_learning_phase": user.current_learning_phase,
            }
        }), 200

    except Exception as e:
        print(f"Error checking route access: {str(e)}")
        return jsonify({"error": f"Failed to check route access: {str(e)}"}), 500
