"""
Enhanced Chat Service V2
Complete AI chat with web search, memory management, vector DB, and learning tracking
Features:
- DuckDuckGo web search integration
- Vector database support for semantic search
- Mem0 memory integration
- Chat history and analytics
- Learning context management
- Personalized responses based on user history
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from ddgs import DDGS
from app.models import db, User, ChatConversation, ChatMessage
from app.services.llm_config import LLMConfig
from app.services.mem0_service import mem0_service
from config import Config


class EnhancedChatServiceV2:
    """Enhanced chat service with web search, memory, and vector DB support"""

    # System prompts for different learning contexts
    SYSTEM_PROMPTS = {
        "general": """You are a friendly and patient English language tutor for Telugu speakers.
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
- Be encouraging and positive""",
        
        "grammar": """You are an expert English grammar tutor. 
Focus on:
1. Explaining grammar rules clearly with Telugu context
2. Providing examples of correct and incorrect usage
3. Explaining when and why to use certain grammatical structures
4. Breaking down complex rules into understandable parts
5. Providing practice exercises when asked

Include relevant web search results if applicable to provide current examples.""",
        
        "vocabulary": """You are a vocabulary building expert.
Focus on:
1. Explaining word meanings and usage
2. Providing synonyms and antonyms
3. Showing example sentences with context
4. Explaining word origins and related words
5. Teaching word collocations and phrases

Include pronunciation guides and Telugu translations.""",
        
        "conversation": """You are a conversational English expert.
Focus on:
1. Teaching natural conversation patterns
2. Providing realistic dialogue examples
3. Explaining cultural nuances in communication
4. Teaching phrases for different social situations
5. Building confidence in English speakers

Make responses feel like natural conversations.""",
    }

    def __init__(self):
        self.ddgs = DDGS()
        self.max_search_results = 5
        self.search_timeout = 10

    def _get_system_prompt(self, topic: str) -> str:
        """Get appropriate system prompt based on topic"""
        topic_lower = topic.lower()
        for key in self.SYSTEM_PROMPTS:
            if key in topic_lower:
                return self.SYSTEM_PROMPTS[key]
        return self.SYSTEM_PROMPTS["general"]

    def search_web(
        self, query: str, max_results: int = 5, region: str = "en-US"
    ) -> List[Dict[str, str]]:
        """
        Search the web using DuckDuckGo

        Args:
            query: Search query
            max_results: Maximum number of results
            region: Region for search results

        Returns:
            List of search results with title, body, and link
        """
        try:
            results = []
            for result in self.ddgs.text(query, max_results=max_results, region=region):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "body": result.get("body", ""),
                        "link": result.get("href", ""),
                        "source": "DuckDuckGo",
                    }
                )
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def _format_web_search_results(self, results: List[Dict[str, str]]) -> str:
        """Format web search results for inclusion in AI response"""
        if not results:
            return ""

        formatted = "\n\n📚 **Relevant Information from Web:**\n"
        for i, result in enumerate(results[:3], 1):
            formatted += f"\n{i}. **{result['title']}**\n"
            formatted += f"   {result['body'][:200]}...\n"
            if result["link"]:
                formatted += f"   🔗 [Read more]({result['link']})\n"
        return formatted

    def search_user_memories(self, user_id: int, query: str, limit: int = 5) -> List[Dict]:
        """Search user's memory for relevant past interactions"""
        if mem0_service.is_available():
            return mem0_service.search_user_memories(query, user_id, limit)
        return []

    def get_user_learning_context(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive learning context for the user

        Args:
            user_id: User ID

        Returns:
            Dictionary with learning context, preferences, and history
        """
        context = {"user_id": user_id, "timestamp": datetime.utcnow().isoformat()}

        # Get recent conversations
        try:
            recent_convs = (
                ChatConversation.query.filter_by(user_id=user_id, is_active=True)
                .order_by(ChatConversation.updated_at.desc())
                .limit(3)
                .all()
            )

            context["recent_topics"] = [c.topic for c in recent_convs]
            context["conversation_count"] = len(recent_convs)
        except Exception as e:
            print(f"Error getting recent conversations: {e}")

        # Get memories from Mem0
        if mem0_service.is_available():
            mem_context = mem0_service.get_user_context_for_conversation(user_id)
            context["memories"] = mem_context

        return context

    def send_message_with_web_search(
        self,
        conversation_id: int,
        user_message: str,
        user_id: int,
        use_web_search: bool = False,
        topic: str = "general",
    ) -> Dict[str, Any]:
        """
        Send message with optional web search and memory integration

        Args:
            conversation_id: ID of the conversation
            user_message: User's message
            user_id: User ID for memory
            use_web_search: Whether to search the web for additional info
            topic: Learning topic (grammar, vocabulary, conversation, etc.)

        Returns:
            Dictionary with user message, AI response, and metadata
        """
        try:
            start_time = time.time()

            # Get conversation
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                return {"error": "Conversation not found"}

            if conversation.user_id != user_id:
                return {"error": "Unauthorized access"}

            # Get learning context
            learning_context = self.get_user_learning_context(user_id)

            # Search web if requested
            web_results = []
            web_search_context = ""
            if use_web_search:
                web_results = self.search_web(user_message, max_results=3)
                web_search_context = self._format_web_search_results(web_results)

            # Save user message
            user_msg = ChatMessage(
                conversation_id=conversation_id, role="user", content=user_message
            )
            db.session.add(user_msg)

            # Get previous messages for context
            previous_messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(10)  # Last 10 messages for context
                .all()
            )

            # Build messages for LLM
            messages = []
            for msg in previous_messages:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_message})

            # Build enhanced system prompt
            system_prompt = self._get_system_prompt(topic)
            if web_search_context:
                system_prompt += f"\n\nRecent Web Search Information Available:\n{web_search_context}"

            if learning_context.get("recent_topics"):
                system_prompt += (
                    f"\n\nUser's recent learning topics: {', '.join(learning_context['recent_topics'])}"
                )

            # Get AI response
            result = LLMConfig.chat_completion(
                messages=messages,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1500,
            )

            if not result.get("success"):
                db.session.rollback()
                return {
                    "error": f"AI response failed: {result.get('error', 'Unknown error')}"
                }

            ai_response = result.get("message", "")

            # Append web search results if included
            if web_results:
                ai_response += web_search_context

            # Parse AI response
            parsed_response = self._parse_ai_response(ai_response)

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

            # Save to Mem0
            if mem0_service.is_available():
                mem0_service.add_user_interaction(
                    user_id=user_id,
                    message=f"User asked: {user_message}\nAI responded about: {topic}",
                    context={
                        "type": "chat",
                        "topic": topic,
                        "web_search_used": use_web_search,
                        "conversation_id": conversation_id,
                    },
                )

            db.session.commit()

            return {
                "success": True,
                "user_message": user_msg.to_dict(),
                "ai_response": ai_msg.to_dict(),
                "conversation": conversation.to_dict(),
                "web_search_used": use_web_search,
                "web_results": web_results,
                "learning_context": learning_context,
                "response_time": time.time() - start_time,
            }

        except Exception as e:
            db.session.rollback()
            print(f"Error in send_message_with_web_search: {e}")
            return {"error": f"Failed to send message: {str(e)}"}

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response to extract components"""
        result = {
            "content": response_text,
            "telugu_translation": None,
            "grammar_explanation": None,
            "examples": [],
            "correction": None,
        }

        import re

        # Extract Telugu translations
        telugu_pattern = r"\([^)]*[\u0C00-\u0C7F]+[^)]*\)"
        telugu_matches = re.findall(telugu_pattern, response_text)
        if telugu_matches:
            result["telugu_translation"] = " ".join(telugu_matches)

        # Extract examples
        lines = response_text.split("\n")
        examples = []
        for line in lines:
            line = line.strip()
            if line.startswith(("Example:", "-", "1.", "2.", "3.", "•")):
                example = line.lstrip("Example:- •123.").strip()
                if example and len(example) > 10:
                    examples.append(example)

        if examples:
            result["examples"] = examples[:5]

        # Extract grammar explanations
        grammar_keywords = ["Grammar:", "Rule:", "Note:", "Remember:"]
        grammar_lines = []
        for line in lines:
            if any(keyword in line for keyword in grammar_keywords):
                grammar_lines.append(line.strip())

        if grammar_lines:
            result["grammar_explanation"] = "\n".join(grammar_lines)

        # Extract corrections
        correction_keywords = ["Correction:", "Correct form:", "Should be:", "Better:"]
        for line in lines:
            if any(keyword in line for keyword in correction_keywords):
                result["correction"] = line.strip()
                break

        return result

    def get_conversation_with_context(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Get conversation with full context and metadata"""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found or unauthorized"}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            # Calculate statistics
            total_messages = len(messages)
            assistant_messages = [m for m in messages if m.role == "assistant"]
            avg_response_time = (
                sum(m.response_time for m in assistant_messages if m.response_time)
                / len(assistant_messages)
                if assistant_messages
                else 0
            )
            total_tokens = sum(m.tokens_used for m in assistant_messages if m.tokens_used)

            return {
                "success": True,
                "conversation": conversation.to_dict(),
                "messages": [m.to_dict() for m in messages],
                "statistics": {
                    "total_messages": total_messages,
                    "assistant_messages": len(assistant_messages),
                    "user_messages": len([m for m in messages if m.role == "user"]),
                    "avg_response_time": avg_response_time,
                    "total_tokens_used": total_tokens,
                    "conversation_duration": (
                        messages[-1].created_at - messages[0].created_at
                    ).total_seconds() if messages else 0,
                },
            }
        except Exception as e:
            return {"error": f"Failed to get conversation: {str(e)}"}

    def search_conversations_by_topic(
        self, user_id: int, topic: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Search conversations by topic"""
        try:
            conversations = (
                ChatConversation.query.filter(
                    ChatConversation.user_id == user_id,
                    ChatConversation.topic.ilike(f"%{topic}%"),
                    ChatConversation.is_active == True,
                )
                .order_by(ChatConversation.updated_at.desc())
                .limit(limit)
                .all()
            )

            return {
                "success": True,
                "topic": topic,
                "conversations": [c.to_dict() for c in conversations],
                "count": len(conversations),
            }
        except Exception as e:
            return {"error": f"Failed to search conversations: {str(e)}"}

    def generate_conversation_summary(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Generate a summary of the conversation"""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found"}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(20)
                .all()
            )

            if not messages:
                return {"summary": "No messages in conversation"}

            # Build conversation text
            conversation_text = "\n".join(
                [f"{msg.role.capitalize()}: {msg.content[:200]}" for msg in messages]
            )

            # Generate summary
            summary_prompt = f"""Summarize this English learning conversation in 2-3 sentences.
Focus on:
1. Main topics discussed
2. Key grammar/vocabulary concepts learned
3. User's learning progress

Conversation:
{conversation_text}

Summary:"""

            result = LLMConfig.generate_text(
                prompt=summary_prompt, temperature=0.5, max_tokens=200
            )

            if result.get("success"):
                return {
                    "success": True,
                    "summary": result.get("text", ""),
                    "conversation_id": conversation_id,
                }
            else:
                return {
                    "success": True,
                    "summary": f"Conversation with {len(messages)} messages about {conversation.topic}",
                }

        except Exception as e:
            return {"error": f"Failed to generate summary: {str(e)}"}

    def get_learning_insights(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive learning insights from chat history"""
        try:
            # Get recent conversations
            conversations = (
                ChatConversation.query.filter_by(user_id=user_id, is_active=True)
                .order_by(ChatConversation.updated_at.desc())
                .limit(20)
                .all()
            )

            topics_discussed = {}
            total_messages = 0
            total_tokens = 0

            for conv in conversations:
                # Count topic
                topic = conv.topic or "General"
                topics_discussed[topic] = topics_discussed.get(topic, 0) + 1

                # Get messages for this conversation
                messages = ChatMessage.query.filter_by(
                    conversation_id=conv.id
                ).all()
                total_messages += len(messages)

                # Sum tokens
                for msg in messages:
                    if msg.tokens_used:
                        total_tokens += msg.tokens_used

            # Get most discussed topic
            most_discussed_topic = (
                max(topics_discussed, key=topics_discussed.get)
                if topics_discussed
                else "General"
            )

            return {
                "success": True,
                "user_id": user_id,
                "total_conversations": len(conversations),
                "total_messages": total_messages,
                "topics_discussed": topics_discussed,
                "most_discussed_topic": most_discussed_topic,
                "total_tokens_used": total_tokens,
                "learning_period": {
                    "start": conversations[-1].created_at.isoformat() if conversations else None,
                    "end": conversations[0].created_at.isoformat() if conversations else None,
                },
            }

        except Exception as e:
            return {"error": f"Failed to get learning insights: {str(e)}"}


# Singleton instance
enhanced_chat_service = EnhancedChatServiceV2()
