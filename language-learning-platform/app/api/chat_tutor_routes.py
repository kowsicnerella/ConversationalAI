"""
AI Chat Tutor API Routes
Handles personalized AI tutoring conversations
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.chat_service import ChatService

chat_tutor_bp = Blueprint('chat_tutor', __name__, url_prefix='/api/chat-tutor')


@chat_tutor_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Create a new chat conversation"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        result = ChatService.create_conversation(
            user_id=current_user_id,
            title=data.get('title'),
            topic=data.get('topic')
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """Get all conversations for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        include_inactive = request.args.get('include_inactive', False, type=bool)
        
        result = ChatService.get_user_conversations(
            user_id=current_user_id,
            limit=limit,
            offset=offset,
            include_inactive=include_inactive
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    try:
        current_user_id = get_jwt_identity()
        
        result = ChatService.get_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Send a message and get AI tutor response"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        result = ChatService.send_message(
            conversation_id=conversation_id,
            user_message=data['message'],
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>/clear', methods=['DELETE'])
@jwt_required()
def clear_conversation(conversation_id):
    """Clear all messages in a conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        result = ChatService.clear_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>', methods=['DELETE'])
@jwt_required()
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        result = ChatService.delete_conversation(
            conversation_id=conversation_id,
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>', methods=['PUT'])
@jwt_required()
def update_conversation(conversation_id):
    """Update conversation title"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        result = ChatService.update_conversation_title(
            conversation_id=conversation_id,
            title=data['title'],
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_tutor_bp.route('/conversations/<int:conversation_id>/summary', methods=['GET'])
@jwt_required()
def get_conversation_summary(conversation_id):
    """Get AI-generated summary of the conversation"""
    try:
        current_user_id = get_jwt_identity()
        
        result = ChatService.get_conversation_summary(
            conversation_id=conversation_id,
            user_id=current_user_id
        )
        
        if 'error' in result:
            status_code = 404 if 'not found' in result['error'].lower() else 403
            return jsonify(result), status_code
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Quick access endpoint - create conversation and send first message in one request
@chat_tutor_bp.route('/quick-chat', methods=['POST'])
@jwt_required()
def quick_chat():
    """Create a new conversation and send the first message"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create conversation
        conv_result = ChatService.create_conversation(
            user_id=current_user_id,
            title=data.get('title'),
            topic=data.get('topic', 'General')
        )
        
        if 'error' in conv_result:
            return jsonify(conv_result), 400
        
        conversation_id = conv_result['conversation']['id']
        
        # Send message
        msg_result = ChatService.send_message(
            conversation_id=conversation_id,
            user_message=data['message'],
            user_id=current_user_id
        )
        
        if 'error' in msg_result:
            return jsonify(msg_result), 400
        
        return jsonify(msg_result), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
