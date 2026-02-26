"""
Unified Chat Routes (v3)
Consolidates all chat endpoints into a single blueprint.
Uses LangGraphChatService for all operations.

Blueprint prefix: /api/v3/chat
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.langgraph_chat_service import langgraph_chat_service
from app.services.weaviate_memory_service import weaviate_memory_service
from app.services.langchain_config import LangChainConfig

unified_chat_bp = Blueprint("unified_chat", __name__)


def _get_user_id():
    """Extract user ID from JWT token."""
    return int(get_jwt_identity())


# ═══════════════ CONVERSATION CRUD ═══════════════


@unified_chat_bp.route("/conversations", methods=["POST"])
@jwt_required()
def create_conversation():
    """
    POST /api/v3/chat/conversations
    Body: { title?, topic? }
    """
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}

        result = langgraph_chat_service.create_conversation(
            user_id=user_id,
            title=data.get("title"),
            topic=data.get("topic"),
        )

        status = 201 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def list_conversations():
    """
    GET /api/v3/chat/conversations?limit=20&offset=0
    """
    try:
        user_id = _get_user_id()
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)

        result = langgraph_chat_service.get_user_conversations(
            user_id=user_id, limit=limit, offset=offset
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/conversations/<int:conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation(conversation_id):
    """
    GET /api/v3/chat/conversations/<id>
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.get_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        status = 200 if result.get("success") else 404
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/conversations/<int:conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conversation_id):
    """
    DELETE /api/v3/chat/conversations/<id>
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.delete_conversation(
            conversation_id=conversation_id, user_id=user_id
        )

        status = 200 if result.get("success") else 404
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/title", methods=["PATCH"]
)
@jwt_required()
def update_title(conversation_id):
    """
    PATCH /api/v3/chat/conversations/<id>/title
    Body: { title }
    """
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}

        title = data.get("title")
        if not title:
            return jsonify({"error": "Title is required", "success": False}), 400

        result = langgraph_chat_service.update_conversation_title(
            conversation_id=conversation_id, user_id=user_id, title=title
        )

        status = 200 if result.get("success") else 404
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ MESSAGING (CORE) ═══════════════


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/messages", methods=["POST"]
)
@jwt_required()
def send_message(conversation_id):
    """
    POST /api/v3/chat/conversations/<id>/messages
    Body: {
        message: str,
        use_web_search: bool (default false),
        topic: str (default "general")
    }

    This single endpoint replaces:
    - POST /api/chat-tutor/conversations/<id>/messages
    - POST /api/enhanced-chat/conversations/<id>/send
    - POST /api/chat-v2/conversations/<id>/messages
    """
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}

        message = data.get("message", "").strip()
        if not message:
            return (
                jsonify({"error": "Message cannot be empty", "success": False}),
                400,
            )

        result = langgraph_chat_service.send_message(
            conversation_id=conversation_id,
            user_message=message,
            user_id=user_id,
            use_web_search=data.get("use_web_search", False),
            topic=data.get("topic", "general"),
        )

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/messages", methods=["GET"]
)
@jwt_required()
def get_messages(conversation_id):
    """
    GET /api/v3/chat/conversations/<id>/messages?limit=50&offset=0
    """
    try:
        user_id = _get_user_id()
        limit = request.args.get("limit", 50, type=int)
        offset = request.args.get("offset", 0, type=int)

        from app.models import db, ChatConversation, ChatMessage

        conversation = db.session.get(ChatConversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            return (
                jsonify({"error": "Conversation not found", "success": False}),
                404,
            )

        query = (
            ChatMessage.query.filter_by(conversation_id=conversation_id)
            .order_by(ChatMessage.created_at.asc())
        )
        total = query.count()
        messages = query.offset(offset).limit(limit).all()

        return (
            jsonify(
                {
                    "success": True,
                    "messages": [m.to_dict() for m in messages],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ ANALYTICS & SUMMARIES ═══════════════


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/summary", methods=["GET"]
)
@jwt_required()
def get_summary(conversation_id):
    """
    GET /api/v3/chat/conversations/<id>/summary
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.generate_summary(
            conversation_id=conversation_id, user_id=user_id
        )

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/analytics", methods=["GET"]
)
@jwt_required()
def get_analytics(conversation_id):
    """
    GET /api/v3/chat/conversations/<id>/analytics
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.get_conversation_analytics(
            conversation_id=conversation_id, user_id=user_id
        )

        status = 200 if result.get("success") else 404
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route(
    "/conversations/<int:conversation_id>/export", methods=["GET"]
)
@jwt_required()
def export_conversation(conversation_id):
    """
    GET /api/v3/chat/conversations/<id>/export?format=json|markdown
    """
    try:
        user_id = _get_user_id()
        export_format = request.args.get("format", "json")

        result = langgraph_chat_service.export_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
            export_format=export_format,
        )

        status = 200 if result.get("success") else 404
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_learning_insights():
    """
    GET /api/v3/chat/insights
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.get_learning_insights(user_id=user_id)

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/statistics", methods=["GET"])
@jwt_required()
def get_statistics():
    """
    GET /api/v3/chat/statistics
    Alias for insights (same data, different endpoint name).
    """
    try:
        user_id = _get_user_id()

        result = langgraph_chat_service.get_learning_insights(user_id=user_id)

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ CONVERSATION SEARCH ═══════════════


@unified_chat_bp.route("/conversations/search", methods=["GET"])
@jwt_required()
def search_conversations():
    """
    GET /api/v3/chat/conversations/search?query=&limit=10
    """
    try:
        user_id = _get_user_id()
        query = request.args.get("query", "")
        limit = request.args.get("limit", 10, type=int)

        if not query:
            return (
                jsonify({"error": "Query parameter is required", "success": False}),
                400,
            )

        result = langgraph_chat_service.search_conversations(
            user_id=user_id, query=query, limit=limit
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ MEMORY MANAGEMENT ═══════════════


@unified_chat_bp.route("/memories/search", methods=["POST"])
@jwt_required()
def search_memories():
    """
    POST /api/v3/chat/memories/search
    Body: { query, limit? }
    """
    try:
        user_id = _get_user_id()
        data = request.get_json() or {}

        query = data.get("query", "")
        limit = data.get("limit", 5)

        if not query:
            return (
                jsonify({"error": "Query is required", "success": False}),
                400,
            )

        memories = langgraph_chat_service.search_user_memories(
            user_id=user_id, query=query, limit=limit
        )

        return jsonify({"success": True, "memories": memories, "count": len(memories)}), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/memories", methods=["GET"])
@jwt_required()
def get_memories():
    """
    GET /api/v3/chat/memories?limit=10
    """
    try:
        user_id = _get_user_id()
        limit = request.args.get("limit", 10, type=int)

        if not weaviate_memory_service.is_available:
            return (
                jsonify(
                    {"success": True, "memories": [], "message": "Memory service not available"}
                ),
                200,
            )

        memories = weaviate_memory_service.get_user_memories(
            user_id=user_id, limit=limit
        )

        return jsonify({"success": True, "memories": memories, "count": len(memories)}), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


@unified_chat_bp.route("/memories/<document_id>", methods=["DELETE"])
@jwt_required()
def delete_memory(document_id):
    """
    DELETE /api/v3/chat/memories/<document_id>
    """
    try:
        user_id = _get_user_id()

        if not weaviate_memory_service.is_available:
            return (
                jsonify({"error": "Memory service not available", "success": False}),
                503,
            )

        result = weaviate_memory_service.delete_memory(
            document_id=document_id, user_id=user_id
        )

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ WEB SEARCH (STANDALONE) ═══════════════


@unified_chat_bp.route("/web-search", methods=["POST"])
@jwt_required()
def web_search():
    """
    POST /api/v3/chat/web-search
    Body: { query, max_results? }
    """
    try:
        data = request.get_json() or {}
        query = data.get("query", "")
        max_results = data.get("max_results", 5)

        if not query:
            return (
                jsonify({"error": "Query is required", "success": False}),
                400,
            )

        from ddgs import DDGS

        ddgs = DDGS()
        results = []
        for r in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "link": r.get("href", ""),
                    "source": "DuckDuckGo",
                }
            )

        return jsonify({"success": True, "results": results, "count": len(results)}), 200

    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500


# ═══════════════ HEALTH CHECK ═══════════════


@unified_chat_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/v3/chat/health
    No auth required - service health check.
    """
    try:
        providers = LangChainConfig.get_available_providers()

        return (
            jsonify(
                {
                    "status": "healthy",
                    "weaviate_available": weaviate_memory_service.is_available,
                    "llm_providers": providers.get("llm_providers", []),
                    "embedding_providers": providers.get("embedding_providers", []),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"status": "degraded", "error": str(e)}),
            200,
        )
