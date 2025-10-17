"""
Chat Tutor Models
Stores chat conversations and messages for personalized AI tutoring
"""

from datetime import datetime
from .user import db


class ChatConversation(db.Model):
    """Represents a chat conversation session with the AI tutor"""

    __tablename__ = "chat_conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), default="New Conversation")
    topic = db.Column(db.String(100))  # e.g., "Grammar", "Vocabulary", "General"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active = db.Column(db.Boolean, default=True)
    message_count = db.Column(db.Integer, default=0)

    # Relationships
    user = db.relationship(
        "User", backref=db.backref("chat_conversations", lazy="dynamic")
    )
    messages = db.relationship(
        "ChatMessage",
        backref="conversation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def to_dict(self):
        """Convert conversation to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "topic": self.topic,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "message_count": self.message_count,
            "last_message": (
                self.messages.order_by(ChatMessage.created_at.desc()).first().to_dict()
                if self.messages.count() > 0
                else None
            ),
        }

    def __repr__(self):
        return f"<ChatConversation {self.id}: {self.title}>"


class ChatMessage(db.Model):
    """Represents a single message in a chat conversation"""

    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer, db.ForeignKey("chat_conversations.id"), nullable=False
    )
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    telugu_translation = db.Column(db.Text)  # Telugu translation of AI responses
    grammar_explanation = db.Column(db.Text)  # Grammar explanation if provided
    examples = db.Column(db.JSON)  # Array of example sentences
    correction = db.Column(db.Text)  # Correction if user made mistakes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Metadata
    tokens_used = db.Column(db.Integer)  # Tokens used for AI generation
    model_used = db.Column(db.String(50))  # AI model used
    response_time = db.Column(db.Float)  # Response time in seconds

    def to_dict(self):
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "telugu_translation": self.telugu_translation,
            "grammar_explanation": self.grammar_explanation,
            "examples": self.examples,
            "correction": self.correction,
            "created_at": self.created_at.isoformat(),
            "tokens_used": self.tokens_used,
            "model_used": self.model_used,
            "response_time": self.response_time,
        }

    def __repr__(self):
        return f"<ChatMessage {self.id}: {self.role}>"
