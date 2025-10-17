"""
Chat Tutor Service
Provides personalized AI tutoring with context awareness, Telugu translations,
grammar explanations, and example generation
"""

import time
from datetime import datetime
from app.models import db, User, ChatConversation, ChatMessage
from app.services.llm_config import LLMConfig
from config import Config


class ChatService:
    """Service for managing chat tutor functionality"""

    # System prompt for the AI tutor
    TUTOR_SYSTEM_PROMPT = """You are a friendly and patient English language tutor for Telugu speakers.
Your role is to:
1. Answer questions about English grammar, vocabulary, and usage in simple, clear language
2. Provide Telugu translations (in Telugu script) when helpful for understanding
3. Give practical examples that Telugu speakers can relate to
4. Correct mistakes gently and explain why the correction is needed
5. Encourage learners and make them feel confident
6. Break down complex concepts into simple steps
7. Use everyday scenarios that Telugu speakers encounter

Guidelines:
- Keep responses concise and easy to understand
- Use simple English when explaining concepts
- Provide 2-3 relevant examples for each explanation
- Include Telugu translations for key words/phrases (using Telugu script: తెలుగు)
- If user makes a mistake, correct it kindly and explain the correct form
- Ask follow-up questions to check understanding
- Be encouraging and positive
- Use emojis sparingly to make responses friendly

Remember: Your goal is to build confidence and make learning English enjoyable!"""

    @staticmethod
    def create_conversation(user_id, title=None, topic=None):
        """
        Create a new chat conversation

        Args:
            user_id (int): ID of the user
            title (str): Optional conversation title
            topic (str): Optional topic category

        Returns:
            dict: New conversation details or error
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Generate title if not provided
            if not title:
                title = f"Conversation {datetime.now().strftime('%b %d, %Y %I:%M %p')}"

            conversation = ChatConversation(
                user_id=user_id, title=title, topic=topic or "General"
            )

            db.session.add(conversation)
            db.session.commit()

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create conversation: {str(e)}"}

    @staticmethod
    def get_user_conversations(user_id, limit=20, offset=0, include_inactive=False):
        """
        Get all conversations for a user

        Args:
            user_id (int): ID of the user
            limit (int): Number of conversations to return
            offset (int): Offset for pagination
            include_inactive (bool): Include inactive conversations

        Returns:
            dict: List of conversations or error
        """
        try:
            query = ChatConversation.query.filter_by(user_id=user_id)

            if not include_inactive:
                query = query.filter_by(is_active=True)

            total = query.count()
            conversations = (
                query.order_by(ChatConversation.updated_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return {
                "success": True,
                "conversations": [c.to_dict() for c in conversations],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            return {"error": f"Failed to get conversations: {str(e)}"}

    @staticmethod
    def get_conversation(conversation_id, user_id=None):
        """
        Get a specific conversation with all messages

        Args:
            conversation_id (int): ID of the conversation
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: Conversation with messages or error
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            return {
                "success": True,
                "conversation": conversation.to_dict(),
                "messages": [m.to_dict() for m in messages],
            }

        except Exception as e:
            return {"error": f"Failed to get conversation: {str(e)}"}

    @staticmethod
    def send_message(conversation_id, user_message, user_id=None):
        """
        Send a message and get AI tutor response

        Args:
            conversation_id (int): ID of the conversation
            user_message (str): User's message
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: User message and AI response or error
        """
        try:
            start_time = time.time()

            # Get conversation
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            # Save user message
            user_msg = ChatMessage(
                conversation_id=conversation_id, role="user", content=user_message
            )
            db.session.add(user_msg)

            # Get conversation history for context
            previous_messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            # Build messages for LLM
            messages = []
            for msg in previous_messages:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_message})

            # Get AI response using LLMConfig
            result = LLMConfig.chat_completion(
                messages=messages,
                system_prompt=ChatService.TUTOR_SYSTEM_PROMPT,
                temperature=0.7,
                max_tokens=1500,
            )

            if not result.get("success"):
                db.session.rollback()
                return {
                    "error": f"AI response failed: {result.get('error', 'Unknown error')}"
                }

            ai_response = result.get("message", "")

            # Parse AI response for Telugu translations, grammar explanations, examples
            parsed_response = ChatService._parse_ai_response(ai_response)

            # Save AI message
            ai_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=parsed_response["content"],
                telugu_translation=parsed_response.get("telugu_translation"),
                grammar_explanation=parsed_response.get("grammar_explanation"),
                examples=parsed_response.get("examples"),
                correction=parsed_response.get("correction"),
                tokens_used=result.get("usage", {}).get("total_tokens"),
                model_used=result.get("model"),
                response_time=time.time() - start_time,
            )
            db.session.add(ai_msg)

            # Update conversation
            conversation.message_count += 2
            conversation.updated_at = datetime.utcnow()

            db.session.commit()

            return {
                "success": True,
                "user_message": user_msg.to_dict(),
                "ai_response": ai_msg.to_dict(),
                "conversation": conversation.to_dict(),
            }

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to send message: {str(e)}"}

    @staticmethod
    def _parse_ai_response(response_text):
        """
        Parse AI response to extract Telugu translations, grammar explanations, and examples

        Args:
            response_text (str): Raw AI response

        Returns:
            dict: Parsed response components
        """
        result = {
            "content": response_text,
            "telugu_translation": None,
            "grammar_explanation": None,
            "examples": [],
            "correction": None,
        }

        # Extract Telugu translations (text in parentheses with Telugu script)
        import re

        telugu_pattern = r"\([^)]*[\u0C00-\u0C7F]+[^)]*\)"
        telugu_matches = re.findall(telugu_pattern, response_text)
        if telugu_matches:
            result["telugu_translation"] = " ".join(telugu_matches)

        # Extract examples (lines starting with "Example:", "-", or numbered)
        example_pattern = r"(?:Example:|-)?\s*(.+?)(?:\n|$)"
        potential_examples = []
        lines = response_text.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith(("Example:", "-", "1.", "2.", "3.", "•")):
                # Clean up the example
                example = line.lstrip("Example:- •123.").strip()
                if example and len(example) > 10:  # Avoid short fragments
                    potential_examples.append(example)

        if potential_examples:
            result["examples"] = potential_examples[:5]  # Max 5 examples

        # Extract grammar explanations (lines with "Grammar:", "Rule:", etc.)
        grammar_keywords = ["Grammar:", "Rule:", "Note:", "Remember:"]
        grammar_lines = []
        for line in lines:
            if any(keyword in line for keyword in grammar_keywords):
                grammar_lines.append(line.strip())

        if grammar_lines:
            result["grammar_explanation"] = "\n".join(grammar_lines)

        # Extract corrections (lines with "Correction:", "Correct form:", etc.)
        correction_keywords = ["Correction:", "Correct form:", "Should be:", "Better:"]
        for line in lines:
            if any(keyword in line for keyword in correction_keywords):
                result["correction"] = line.strip()
                break

        return result

    @staticmethod
    def clear_conversation(conversation_id, user_id=None):
        """
        Clear all messages in a conversation

        Args:
            conversation_id (int): ID of the conversation
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: Success status or error
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            # Delete all messages
            ChatMessage.query.filter_by(conversation_id=conversation_id).delete()

            # Reset conversation
            conversation.message_count = 0
            conversation.updated_at = datetime.utcnow()

            db.session.commit()

            return {"success": True, "message": "Conversation cleared successfully"}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to clear conversation: {str(e)}"}

    @staticmethod
    def delete_conversation(conversation_id, user_id=None):
        """
        Delete a conversation (soft delete by marking inactive)

        Args:
            conversation_id (int): ID of the conversation
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: Success status or error
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            # Soft delete
            conversation.is_active = False
            conversation.updated_at = datetime.utcnow()

            db.session.commit()

            return {"success": True, "message": "Conversation deleted successfully"}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to delete conversation: {str(e)}"}

    @staticmethod
    def update_conversation_title(conversation_id, title, user_id=None):
        """
        Update conversation title

        Args:
            conversation_id (int): ID of the conversation
            title (str): New title
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: Updated conversation or error
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            conversation.title = title
            conversation.updated_at = datetime.utcnow()

            db.session.commit()

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update conversation: {str(e)}"}

    @staticmethod
    def get_conversation_summary(conversation_id, user_id=None):
        """
        Get a summary of the conversation (topics discussed, key concepts)

        Args:
            conversation_id (int): ID of the conversation
            user_id (int): Optional user ID to verify ownership

        Returns:
            dict: Summary or error
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)

            if not conversation:
                return {"error": "Conversation not found"}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access to conversation"}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            if not messages:
                return {"success": True, "summary": "No messages yet"}

            # Build conversation text for summarization
            conversation_text = "\n".join(
                [
                    f"{msg.role.capitalize()}: {msg.content}"
                    for msg in messages[:20]  # Limit to recent 20 messages
                ]
            )

            # Generate summary using LLM
            summary_prompt = f"""Summarize this English learning conversation in 2-3 sentences.
Focus on:
1. Main topics discussed
2. Key grammar/vocabulary concepts
3. User's progress or understanding

Conversation:
{conversation_text}

Summary:"""

            result = LLMConfig.generate_text(
                prompt=summary_prompt, temperature=0.5, max_tokens=200
            )

            if result.get("success"):
                return {
                    "success": True,
                    "summary": result.get("text", "Unable to generate summary"),
                }
            else:
                return {
                    "success": True,
                    "summary": f"Conversation with {len(messages)} messages about {conversation.topic}",
                }

        except Exception as e:
            return {"error": f"Failed to get summary: {str(e)}"}
