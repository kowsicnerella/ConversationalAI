from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Test blueprint to verify JWT authentication
test_auth_bp = Blueprint("test_auth", __name__)


@test_auth_bp.route("/test-auth", methods=["GET"])
@jwt_required()
def test_auth():
    """Test endpoint to verify JWT authentication is working"""
    try:
        user_id = get_jwt_identity()
        return (
            jsonify(
                {
                    "message": "JWT authentication working!",
                    "user_id": user_id,
                    "user_id_type": type(user_id).__name__,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": "JWT authentication failed", "details": str(e)}), 500


@test_auth_bp.route("/test-no-auth", methods=["GET"])
def test_no_auth():
    """Test endpoint without authentication"""
    return (
        jsonify({"message": "No auth required - this works!", "status": "success"}),
        200,
    )
