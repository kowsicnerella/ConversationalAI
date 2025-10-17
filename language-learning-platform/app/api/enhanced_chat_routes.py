"""
Enhanced Chat Routes with Mem0 Integration
Provides improved chat accuracy and personalized learning
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, ChatConversation, ChatMessage
from app.services.enhanced_chat_service import enhanced_chat_service
from datetime import datetime
import traceback

enhanced_chat_bp = Blueprint("enhanced_chat", __name__)


@enhanced_chat_bp.route("/conversations", methods=["POST"])
@jwt_required()
def create_conversation():
    """
    Create a new chat conversation

    Expected JSON:
    {
        "title": "Learning Session Title" (optional),
        "topic": "grammar" (optional)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        title = data.get("title")
        topic = data.get("topic", "General Learning")

        result = enhanced_chat_service.create_conversation(
            user_id=user_id, title=title, topic=topic
        )

        if not result.get("success"):
            return (
                jsonify(
                    {
                        "error": result.get("error", "Failed to create conversation"),
                        "telugu_message": "సంభాషణ సృష్టించడం విఫలమైంది",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "message": "Conversation created successfully!",
                    "telugu_message": "సంభాషణ విజయవంతంగా సృష్టించబడింది!",
                    "conversation": result["conversation"],
                }
            ),
            201,
        )

    except Exception as e:
        current_app.logger.error(f"Error creating conversation: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to create conversation",
                    "telugu_message": "సంభాషణ సృష్టించడం విఫలమైంది",
                    "details": str(e),
                }
            ),
            500,
        )


@enhanced_chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def get_conversations():
    """
    Get user's conversation history with pagination
    """
    try:
        user_id = int(get_jwt_identity())
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)
        include_inactive = request.args.get("include_inactive", False, type=bool)

        from app.services.chat_service import ChatService

        result = ChatService.get_user_conversations(
            user_id=user_id,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive,
        )

        if not result.get("success"):
            return (
                jsonify(
                    {
                        "error": result.get("error", "Failed to get conversations"),
                        "telugu_message": "సంభాషణలు పొందడం విఫలమైంది",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "message": "Conversations retrieved successfully!",
                    "telugu_message": "సంభాషణలు విజయవంతంగా తీసుకోబడ్డాయి!",
                    "conversations": result["conversations"],
                    "total": result["total"],
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error getting conversations: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to get conversations",
                    "telugu_message": "సంభాషణలు పొందడం విఫలమైంది",
                }
            ),
            500,
        )


@enhanced_chat_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation(conversation_id):
    """
    Get a specific conversation with all messages
    """
    try:
        user_id = int(get_jwt_identity())

        from app.services.chat_service import ChatService

        result = ChatService.get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        if not result.get("success"):
            return (
                jsonify(
                    {
                        "error": result.get("error", "Conversation not found"),
                        "telugu_message": "సంభాషణ కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "message": "Conversation retrieved successfully!",
                    "telugu_message": "సంభాషణ విజయవంతంగా తీసుకోబడింది!",
                    "conversation": result["conversation"],
                    "messages": result["messages"],
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error getting conversation: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to get conversation",
                    "telugu_message": "సంభాషణ పొందడం విఫలమైంది",
                }
            ),
            500,
        )


@enhanced_chat_bp.route(
    "/conversations/<int:conversation_id>/message", methods=["POST"]
)
@jwt_required()
def send_message(conversation_id):
    """
    Send a message with enhanced context and Mem0 integration

    Expected JSON:
    {
        "message": "How do I say 'Good morning' in Telugu?",
        "context": "learning" (optional)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        user_message = data.get("message", "").strip()

        if not user_message:
            return (
                jsonify(
                    {"error": "Message is required", "telugu_message": "సందేశం అవసరం"}
                ),
                400,
            )

        # Use enhanced chat service with Mem0 integration
        result = enhanced_chat_service.send_message_with_context(
            conversation_id=conversation_id, user_message=user_message, user_id=user_id
        )

        if not result.get("success"):
            return (
                jsonify(
                    {
                        "error": result.get("error", "Failed to send message"),
                        "telugu_message": "సందేశం పంపడం విఫలమైంది",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "message": "Message sent successfully!",
                    "telugu_message": "సందేశం విజయవంతంగా పంపబడింది!",
                    "user_message": result["user_message"],
                    "ai_response": result["ai_response"],
                    "conversation": result["conversation"],
                    "context_info": {
                        "personalization_used": result.get("context_used", {}),
                        "mem0_enabled": enhanced_chat_service.mem0_service.is_available(),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to send message",
                    "telugu_message": "సందేశం పంపడం విఫలమైంది",
                    "details": str(e),
                }
            ),
            500,
        )


@enhanced_chat_bp.route("/conversations/<int:conversation_id>/summary", methods=["GET"])
@jwt_required()
def get_conversation_summary(conversation_id):
    """
    Get AI-generated conversation summary with key learnings
    """
    try:
        user_id = int(get_jwt_identity())

        result = enhanced_chat_service.get_conversation_summary(
            conversation_id=conversation_id, user_id=user_id
        )

        if not result.get("success"):
            return (
                jsonify(
                    {
                        "error": result.get("error", "Failed to generate summary"),
                        "telugu_message": "సారాంశం సృష్టించడం విఫలమైంది",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "message": "Summary generated successfully!",
                    "telugu_message": "సారాంశం విజయవంతంగా సృష్టించబడింది!",
                    "summary": result["summary"],
                    "message_count": result["message_count"],
                    "conversation_id": conversation_id,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error generating summary: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to generate summary",
                    "telugu_message": "సారాంశం సృష్టించడం విఫలమైంది",
                }
            ),
            500,
        )


@enhanced_chat_bp.route("/test-mem0", methods=["GET"])
@jwt_required()
def test_mem0_integration():
    """
    Test endpoint to verify Mem0 integration
    """
    try:
        user_id = int(get_jwt_identity())

        mem0_available = enhanced_chat_service.mem0_service.is_available()

        test_results = {"mem0_available": mem0_available, "user_id": user_id}

        if mem0_available:
            # Try to get user memories
            memories = enhanced_chat_service.mem0_service.get_user_memories(
                user_id=user_id, limit=5
            )
            test_results["memory_count"] = len(memories)
            test_results["recent_memories"] = memories[:3] if memories else []
        else:
            test_results["error"] = "Mem0 is not configured or unavailable"

        return (
            jsonify(
                {
                    "message": "Mem0 integration test completed",
                    "telugu_message": "Mem0 ఇంటిగ్రేషన్ పరీక్ష పూర్తయింది",
                    "test_results": test_results,
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error testing Mem0: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Mem0 test failed",
                    "telugu_message": "Mem0 పరీక్ష విఫలమైంది",
                    "details": str(e),
                }
            ),
            500,
        )


@enhanced_chat_bp.route("/quick-chat", methods=["POST"])
@jwt_required()
def quick_chat():
    """
    Quick chat endpoint - creates conversation and sends message in one request

    Expected JSON:
    {
        "message": "How do I introduce myself in English?",
        "topic": "grammar" (optional)
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        user_message = data.get("message", "").strip()
        topic = data.get("topic", "Quick Chat")

        if not user_message:
            return (
                jsonify(
                    {"error": "Message is required", "telugu_message": "సందేశం అవసరం"}
                ),
                400,
            )

        # Create conversation
        conv_result = enhanced_chat_service.create_conversation(
            user_id=user_id,
            title=f"Quick Chat - {datetime.now().strftime('%I:%M %p')}",
            topic=topic,
        )

        if not conv_result.get("success"):
            return (
                jsonify(
                    {
                        "error": "Failed to create conversation",
                        "telugu_message": "సంభాషణ సృష్టించడం విఫలమైంది",
                    }
                ),
                400,
            )

        conversation_id = conv_result["conversation"]["id"]

        # Send message
        msg_result = enhanced_chat_service.send_message_with_context(
            conversation_id=conversation_id, user_message=user_message, user_id=user_id
        )

        if not msg_result.get("success"):
            return (
                jsonify(
                    {
                        "error": "Failed to send message",
                        "telugu_message": "సందేశం పంపడం విఫలమైంది",
                    }
                ),
                400,
            )

        return (
            jsonify(
                {
                    "message": "Quick chat completed successfully!",
                    "telugu_message": "త్వరిత చాట్ విజయవంతంగా పూర్తయింది!",
                    "conversation_id": conversation_id,
                    "user_message": msg_result["user_message"],
                    "ai_response": msg_result["ai_response"],
                    "personalization": {
                        "context_used": msg_result.get("context_used", {}),
                        "mem0_enabled": enhanced_chat_service.mem0_service.is_available(),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        current_app.logger.error(f"Error in quick chat: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Quick chat failed",
                    "telugu_message": "త్వరిత చాట్ విఫలమైంది",
                    "details": str(e),
                }
            ),
            500,
        )


# Legacy route for backward compatibility
@enhanced_chat_bp.route("/message", methods=["POST"])
@jwt_required()
def send_message_legacy():
    """
    Legacy chat endpoint - creates conversation on the fly
    Redirects to quick_chat
    """
    return quick_chat()
