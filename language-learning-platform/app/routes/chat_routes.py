"""
Enhanced Chat Routes
API endpoints for AI chat, web search, memory, and learning management
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.enhanced_chat_service_v2 import enhanced_chat_service
from app.services.chat_history_service import chat_history_service
from app.services.mem0_service import mem0_service
from app.services.vector_db_service import vector_db_service
from app.models import db, ChatConversation, ChatMessage, User
from datetime import datetime

# Create blueprint
chat_bp = Blueprint("chat_v2", __name__, url_prefix="/chat-v2")


def get_user_id_from_token():
    """Extract user ID from JWT token"""
    return get_jwt_identity()


# ============ CONVERSATION MANAGEMENT ============


@chat_bp.route("/conversations", methods=["POST"])
@jwt_required()
def create_conversation():
    """Create a new chat conversation"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()

        result = chat_history_service.create_conversation(
            user_id=user_id,
            title=data.get("title"),
            topic=data.get("topic", "General"),
        )

        if result.get("success"):
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def get_conversations():
    """Get all conversations for the user"""
    try:
        user_id = int(get_user_id_from_token())
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)
        sort_by = request.args.get("sort_by", "updated_at")

        result = chat_history_service.get_user_conversations(
            user_id=user_id, limit=limit, offset=offset, sort_by=sort_by
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation(conversation_id):
    """Get a specific conversation with messages"""
    try:
        user_id = int(get_user_id_from_token())

        result = chat_history_service.get_conversation(
            conversation_id=conversation_id, user_id=user_id, include_messages=True
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations/<int:conversation_id>", methods=["PUT"])
@jwt_required()
def update_conversation(conversation_id):
    """Update conversation title"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()

        result = chat_history_service.update_conversation_title(
            conversation_id=conversation_id,
            user_id=user_id,
            title=data.get("title"),
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        user_id = int(get_user_id_from_token())

        result = chat_history_service.delete_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ MESSAGE SENDING ============


@chat_bp.route("/conversations/<int:conversation_id>/messages", methods=["POST"])
@jwt_required()
def send_message(conversation_id):
    """Send a message and get AI response with optional web search"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()

        user_message = data.get("message", "").strip()
        use_web_search = data.get("use_web_search", False)
        topic = data.get("topic", "general")

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        result = enhanced_chat_service.send_message_with_web_search(
            conversation_id=conversation_id,
            user_message=user_message,
            user_id=user_id,
            use_web_search=use_web_search,
            topic=topic,
        )

        if result.get("success"):
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(conversation_id):
    """Get messages from a conversation"""
    try:
        user_id = int(get_user_id_from_token())
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        result = chat_history_service.get_conversation_messages(
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ WEB SEARCH ============


@chat_bp.route("/web-search", methods=["POST"])
@jwt_required()
def web_search():
    """Perform a web search"""
    try:
        data = request.get_json()
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        results = enhanced_chat_service.search_web(
            query=query, max_results=data.get("max_results", 5)
        )

        return jsonify({"success": True, "query": query, "results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ LEARNING CONTEXT & MEMORY ============


@chat_bp.route("/user-learning-context", methods=["GET"])
@jwt_required()
def get_learning_context():
    """Get user's learning context"""
    try:
        user_id = int(get_user_id_from_token())

        context = enhanced_chat_service.get_user_learning_context(user_id)

        return jsonify({"success": True, "context": context}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/user-memories", methods=["GET"])
@jwt_required()
def get_user_memories():
    """Get user's stored memories"""
    try:
        user_id = int(get_user_id_from_token())
        limit = request.args.get("limit", 10, type=int)

        if mem0_service.is_available():
            memories = mem0_service.get_user_memories(user_id, limit=limit)
            return (
                jsonify(
                    {
                        "success": True,
                        "memories": memories,
                        "count": len(memories),
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Memory service not available",
                    }
                ),
                503,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/search-memories", methods=["POST"])
@jwt_required()
def search_memories():
    """Search user's memories"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()
        query = data.get("query", "").strip()
        limit = data.get("limit", 5)

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        if mem0_service.is_available():
            results = mem0_service.search_user_memories(query, user_id, limit)
            return (
                jsonify({"success": True, "query": query, "results": results}),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Memory service not available",
                    }
                ),
                503,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/personalized-suggestions", methods=["GET"])
@jwt_required()
def get_personalized_suggestions():
    """Get personalized learning suggestions based on memory and context"""
    try:
        user_id = int(get_user_id_from_token())
        proficiency = request.args.get("proficiency", "beginner")

        if mem0_service.is_available():
            suggestions = mem0_service.get_personalized_suggestions(user_id, proficiency)
            return jsonify({"success": True, "suggestions": suggestions}), 200
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Memory service not available",
                    }
                ),
                503,
            )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ ANALYTICS & INSIGHTS ============


@chat_bp.route("/conversations/<int:conversation_id>/analytics", methods=["GET"])
@jwt_required()
def get_conversation_analytics(conversation_id):
    """Get analytics for a conversation"""
    try:
        user_id = int(get_user_id_from_token())

        result = chat_history_service.get_conversation_analytics(
            conversation_id=conversation_id, user_id=user_id
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/learning-statistics", methods=["GET"])
@jwt_required()
def get_learning_statistics():
    """Get comprehensive learning statistics for user"""
    try:
        user_id = int(get_user_id_from_token())

        result = chat_history_service.get_user_learning_statistics(user_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/learning-insights", methods=["GET"])
@jwt_required()
def get_learning_insights():
    """Get learning insights from chat history"""
    try:
        user_id = int(get_user_id_from_token())

        result = enhanced_chat_service.get_learning_insights(user_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ SEARCH & DISCOVERY ============


@chat_bp.route("/search-conversations", methods=["POST"])
@jwt_required()
def search_conversations():
    """Search conversations by title or topic"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()
        query = data.get("query", "").strip()
        limit = data.get("limit", 10)

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        result = chat_history_service.search_conversations(
            user_id=user_id, query=query, limit=limit
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/search-similar", methods=["POST"])
@jwt_required()
def search_similar_conversations():
    """Find conversations similar to the given one"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()
        conversation_id = data.get("conversation_id")
        limit = data.get("limit", 5)

        if not conversation_id:
            return jsonify({"error": "Conversation ID required"}), 400

        # Verify ownership
        conv = ChatConversation.query.get(conversation_id)
        if not conv or conv.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        similar = vector_db_service.find_similar_conversations(
            conversation_id, user_id, limit
        )

        return jsonify({"success": True, "similar": similar}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ EXPORT & DATA ============


@chat_bp.route("/conversations/<int:conversation_id>/export", methods=["GET"])
@jwt_required()
def export_conversation(conversation_id):
    """Export a conversation"""
    try:
        user_id = int(get_user_id_from_token())
        format = request.args.get("format", "json")

        result = chat_history_service.export_conversation(
            conversation_id=conversation_id, user_id=user_id, format=format
        )

        if result.get("success"):
            if format == "markdown":
                return result["data"], 200, {"Content-Type": "text/markdown"}
            else:
                return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/recent-conversations", methods=["GET"])
@jwt_required()
def get_recent_conversations():
    """Get recent conversations"""
    try:
        user_id = int(get_user_id_from_token())
        days = request.args.get("days", 7, type=int)
        limit = request.args.get("limit", 5, type=int)

        result = chat_history_service.get_recent_conversations(
            user_id=user_id, days=days, limit=limit
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ VECTOR DATABASE ============


@chat_bp.route("/semantic-search", methods=["POST"])
@jwt_required()
def semantic_search():
    """Perform semantic search on chat history"""
    try:
        user_id = int(get_user_id_from_token())
        data = request.get_json()
        query = data.get("query", "").strip()
        limit = data.get("limit", 5)

        if not query:
            return jsonify({"error": "Query cannot be empty"}), 400

        results = vector_db_service.semantic_search(query, user_id, limit)

        return jsonify({"success": True, "query": query, "results": results}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/conversations/<int:conversation_id>/embed", methods=["POST"])
@jwt_required()
def embed_conversation(conversation_id):
    """Embed all messages in a conversation for vector search"""
    try:
        user_id = int(get_user_id_from_token())

        # Verify ownership
        conv = ChatConversation.query.get(conversation_id)
        if not conv or conv.user_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

        result = vector_db_service.batch_embed_messages(conversation_id)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============ STATUS & HEALTH ============


@chat_bp.route("/health", methods=["GET"])
def health_check():
    """Check service health"""
    return (
        jsonify(
            {
                "success": True,
                "status": "healthy",
                "mem0_available": mem0_service.is_available(),
                "vector_db_enabled": vector_db_service.use_weaviate,
            }
        ),
        200,
    )


# Register blueprint (this is done in the app factory)
