"""
Chat History Service
Manages chat history, analytics, learning tracking, and persistence
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.models import db, ChatConversation, ChatMessage, User


class ChatHistoryService:
    """Service for managing chat history and learning analytics"""

    @staticmethod
    def create_conversation(
        user_id: int, title: Optional[str] = None, topic: str = "General"
    ) -> Dict[str, Any]:
        """Create a new chat conversation"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found", "success": False}

            if not title:
                title = f"Conversation {datetime.utcnow().strftime('%b %d, %Y')}"

            conversation = ChatConversation(
                user_id=user_id, title=title, topic=topic, message_count=0
            )

            db.session.add(conversation)
            db.session.commit()

            return {
                "success": True,
                "conversation": conversation.to_dict(),
            }

        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "success": False}

    @staticmethod
    def get_user_conversations(
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        include_inactive: bool = False,
        sort_by: str = "updated_at",
    ) -> Dict[str, Any]:
        """Get all conversations for a user with pagination"""
        try:
            query = ChatConversation.query.filter_by(user_id=user_id)

            if not include_inactive:
                query = query.filter_by(is_active=True)

            total = query.count()

            # Sort by specified field
            if sort_by == "updated_at":
                query = query.order_by(ChatConversation.updated_at.desc())
            elif sort_by == "created_at":
                query = query.order_by(ChatConversation.created_at.desc())
            elif sort_by == "message_count":
                query = query.order_by(ChatConversation.message_count.desc())

            conversations = query.limit(limit).offset(offset).all()

            return {
                "success": True,
                "conversations": [c.to_dict() for c in conversations],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def get_conversation(
        conversation_id: int, user_id: int, include_messages: bool = True
    ) -> Dict[str, Any]:
        """Get a specific conversation"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            result = {"success": True, "conversation": conversation.to_dict()}

            if include_messages:
                messages = (
                    ChatMessage.query.filter_by(conversation_id=conversation_id)
                    .order_by(ChatMessage.created_at.asc())
                    .all()
                )
                result["messages"] = [m.to_dict() for m in messages]
                result["message_count"] = len(messages)

            return result

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def delete_conversation(conversation_id: int, user_id: int) -> Dict[str, Any]:
        """Soft delete a conversation (mark as inactive)"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            conversation.is_active = False
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "message": "Conversation deleted"}

        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "success": False}

    @staticmethod
    def update_conversation_title(
        conversation_id: int, user_id: int, title: str
    ) -> Dict[str, Any]:
        """Update conversation title"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "success": False}

    @staticmethod
    def get_conversation_messages(
        conversation_id: int, user_id: int, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """Get messages from a conversation with pagination"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            query = ChatMessage.query.filter_by(conversation_id=conversation_id)
            total = query.count()

            messages = (
                query.order_by(ChatMessage.created_at.asc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return {
                "success": True,
                "messages": [m.to_dict() for m in messages],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def get_conversation_analytics(
        conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Get detailed analytics for a conversation"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).all()

            # Calculate statistics
            total_messages = len(messages)
            user_messages = [m for m in messages if m.role == "user"]
            assistant_messages = [m for m in messages if m.role == "assistant"]

            total_tokens = sum(m.tokens_used for m in assistant_messages if m.tokens_used)
            avg_response_time = (
                sum(m.response_time for m in assistant_messages if m.response_time)
                / len(assistant_messages)
                if assistant_messages
                else 0
            )

            # Calculate conversation duration
            duration = (
                (messages[-1].created_at - messages[0].created_at).total_seconds()
                if messages
                else 0
            )

            # Average message length
            avg_user_msg_len = (
                sum(len(m.content) for m in user_messages) / len(user_messages)
                if user_messages
                else 0
            )
            avg_assistant_msg_len = (
                sum(len(m.content) for m in assistant_messages)
                / len(assistant_messages)
                if assistant_messages
                else 0
            )

            return {
                "success": True,
                "conversation_id": conversation_id,
                "analytics": {
                    "total_messages": total_messages,
                    "user_messages": len(user_messages),
                    "assistant_messages": len(assistant_messages),
                    "total_tokens_used": total_tokens,
                    "avg_response_time": avg_response_time,
                    "conversation_duration_seconds": duration,
                    "avg_user_message_length": avg_user_msg_len,
                    "avg_assistant_message_length": avg_assistant_msg_len,
                    "topic": conversation.topic,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                },
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def get_user_learning_statistics(user_id: int) -> Dict[str, Any]:
        """Get comprehensive learning statistics for a user"""
        try:
            conversations = ChatConversation.query.filter_by(
                user_id=user_id, is_active=True
            ).all()

            if not conversations:
                return {
                    "success": True,
                    "user_id": user_id,
                    "statistics": {
                        "total_conversations": 0,
                        "total_messages": 0,
                        "topics": {},
                        "total_learning_time": 0,
                    },
                }

            # Collect statistics
            topics_count = {}
            total_messages = 0
            total_tokens = 0
            all_messages = []

            for conv in conversations:
                topic = conv.topic or "General"
                topics_count[topic] = topics_count.get(topic, 0) + 1

                messages = ChatMessage.query.filter_by(
                    conversation_id=conv.id
                ).all()
                total_messages += len(messages)
                all_messages.extend(messages)

                for msg in messages:
                    if msg.tokens_used:
                        total_tokens += msg.tokens_used

            # Calculate total learning time
            total_learning_time = 0
            for conv in conversations:
                messages = ChatMessage.query.filter_by(
                    conversation_id=conv.id
                ).all()
                if messages:
                    duration = (messages[-1].created_at - messages[0].created_at).total_seconds()
                    total_learning_time += duration

            # Find most active learning period
            if all_messages:
                dates = [m.created_at.date() for m in all_messages]
                from collections import Counter
                most_active_date = Counter(dates).most_common(1)[0][0] if dates else None
            else:
                most_active_date = None

            return {
                "success": True,
                "user_id": user_id,
                "statistics": {
                    "total_conversations": len(conversations),
                    "total_messages": total_messages,
                    "topics": topics_count,
                    "most_discussed_topic": (
                        max(topics_count, key=topics_count.get)
                        if topics_count
                        else "General"
                    ),
                    "total_tokens_used": total_tokens,
                    "total_learning_time_seconds": int(total_learning_time),
                    "avg_messages_per_conversation": (
                        total_messages / len(conversations) if conversations else 0
                    ),
                    "most_active_date": most_active_date.isoformat() if most_active_date else None,
                },
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def search_conversations(
        user_id: int, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Search conversations by title or topic"""
        try:
            conversations = (
                ChatConversation.query.filter(
                    ChatConversation.user_id == user_id,
                    ChatConversation.is_active == True,
                )
                .filter(
                    (ChatConversation.title.ilike(f"%{query}%"))
                    | (ChatConversation.topic.ilike(f"%{query}%"))
                )
                .order_by(ChatConversation.updated_at.desc())
                .limit(limit)
                .all()
            )

            return {
                "success": True,
                "query": query,
                "conversations": [c.to_dict() for c in conversations],
                "count": len(conversations),
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def export_conversation(
        conversation_id: int, user_id: int, format: str = "json"
    ) -> Dict[str, Any]:
        """Export a conversation in specified format"""
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).all()

            export_data = {
                "conversation": conversation.to_dict(),
                "messages": [m.to_dict() for m in messages],
                "exported_at": datetime.utcnow().isoformat(),
            }

            if format == "json":
                return {
                    "success": True,
                    "data": export_data,
                    "format": "json",
                }
            elif format == "markdown":
                md_content = f"# {conversation.title}\n\n"
                md_content += f"**Topic:** {conversation.topic}\n"
                md_content += f"**Created:** {conversation.created_at}\n\n"

                for msg in messages:
                    role = "👤 User" if msg.role == "user" else "🤖 AI"
                    md_content += f"\n## {role}\n{msg.content}\n"

                return {
                    "success": True,
                    "data": md_content,
                    "format": "markdown",
                }

            return {"error": "Unsupported format", "success": False}

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def get_recent_conversations(user_id: int, days: int = 7, limit: int = 5) -> Dict[str, Any]:
        """Get conversations from the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            conversations = (
                ChatConversation.query.filter(
                    ChatConversation.user_id == user_id,
                    ChatConversation.is_active == True,
                    ChatConversation.updated_at >= cutoff_date,
                )
                .order_by(ChatConversation.updated_at.desc())
                .limit(limit)
                .all()
            )

            return {
                "success": True,
                "days": days,
                "conversations": [c.to_dict() for c in conversations],
                "count": len(conversations),
            }

        except Exception as e:
            return {"error": str(e), "success": False}

    @staticmethod
    def merge_conversations(
        source_conversation_id: int, target_conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Merge messages from source conversation into target"""
        try:
            source_conv = ChatConversation.query.get(source_conversation_id)
            target_conv = ChatConversation.query.get(target_conversation_id)

            if not source_conv or not target_conv:
                return {"error": "Conversation not found", "success": False}

            if source_conv.user_id != user_id or target_conv.user_id != user_id:
                return {"error": "Unauthorized", "success": False}

            # Move messages from source to target
            messages = ChatMessage.query.filter_by(
                conversation_id=source_conversation_id
            ).all()

            for msg in messages:
                msg.conversation_id = target_conversation_id

            # Update target conversation stats
            target_conv.message_count += source_conv.message_count
            target_conv.updated_at = datetime.utcnow()

            # Mark source as inactive
            source_conv.is_active = False

            db.session.commit()

            return {
                "success": True,
                "message": f"Merged {len(messages)} messages",
                "target_conversation": target_conv.to_dict(),
            }

        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "success": False}

    @staticmethod
    def clear_conversation_history(user_id: int, days_old: int = 30) -> Dict[str, Any]:
        """Clear old conversations for a user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            conversations = ChatConversation.query.filter(
                ChatConversation.user_id == user_id,
                ChatConversation.updated_at < cutoff_date,
            ).all()

            count = len(conversations)

            for conv in conversations:
                conv.is_active = False
                conv.updated_at = datetime.utcnow()

            db.session.commit()

            return {
                "success": True,
                "message": f"Marked {count} conversations as inactive",
                "count": count,
            }

        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "success": False}


# Singleton instance
chat_history_service = ChatHistoryService()
