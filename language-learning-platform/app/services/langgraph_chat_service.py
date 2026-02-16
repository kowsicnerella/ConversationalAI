"""
LangGraph Chat Service
Consolidated conversation service using LangGraph state machine.

Replaces:
    - app/services/chat_service.py (ChatService)
    - app/services/enhanced_chat_service.py (EnhancedChatService)
    - app/services/enhanced_chat_service_v2.py (EnhancedChatServiceV2)

Keeps:
    - SQLAlchemy models (ChatConversation, ChatMessage) for CRUD
    - ChatHistoryService for conversation management
"""

import re
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.models import db, User, ChatConversation, ChatMessage
from app.models import (
    Profile,
    UserActivityLog,
    VocabularyWord,
    MistakePattern,
    ProficiencyAssessment,
)
from app.services.langchain_config import LangChainConfig
from app.services.weaviate_memory_service import weaviate_memory_service
from app.services.chat_history_service import ChatHistoryService

logger = logging.getLogger(__name__)


# ─── LangGraph State Definition ───


class ConversationState(TypedDict):
    """State passed through the LangGraph graph at each node."""

    # Input fields (set before graph invocation)
    user_id: int
    conversation_id: int
    user_message: str
    topic: str
    use_web_search: bool

    # Populated by retrieve_memory node
    user_context: Dict[str, Any]
    relevant_memories: List[Dict[str, Any]]

    # Populated by web_search node (optional)
    web_results: List[Dict[str, str]]

    # Populated by generate_response node
    ai_response_raw: str
    ai_response_parsed: Dict[str, Any]
    model_used: str
    tokens_used: int
    response_time: float

    # Populated by store_memory node
    memory_stored: bool

    # Output
    success: bool
    error: Optional[str]


# ─── System Prompts ───

SYSTEM_PROMPTS = {
    "general": """You are an expert English language tutor specializing in teaching Telugu speakers.

Your teaching approach:
1. ASSESS: Understand the learner's current level and specific needs
2. EXPLAIN: Break down concepts into simple, digestible parts
3. DEMONSTRATE: Provide clear, practical examples from everyday life
4. PRACTICE: Give opportunities to apply what they learned
5. REINFORCE: Summarize key points and encourage continued learning

Communication guidelines:
- Use simple, clear English appropriate for the learner's level
- Provide Telugu translations (తెలుగు లిపి) for complex words and phrases
- Give 2-3 relevant examples for each concept
- Use everyday scenarios familiar to Telugu speakers
- Correct mistakes gently with explanations
- Be encouraging and build confidence
- Ask follow-up questions to ensure understanding
- Use structured formatting for clarity

Response structure:
1. Direct answer to the question
2. Grammar/vocabulary explanation if relevant
3. Telugu translation (తెలుగు) for key terms
4. 2-3 practical examples
5. Helpful tip or cultural note if applicable
6. Encouraging closing remark

Remember: Your goal is effective learning through clear communication and personalization.""",
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


class LangGraphChatService:
    """
    Consolidated chat service using LangGraph.

    Usage:
        service = LangGraphChatService()
        result = service.send_message(
            conversation_id=123,
            user_message="How do I use past tense?",
            user_id=1,
            use_web_search=False,
            topic="grammar"
        )
    """

    def __init__(self):
        self._graph = None
        self._compiled = False

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        graph = StateGraph(ConversationState)

        graph.add_node("retrieve_memory", self._node_retrieve_memory)
        graph.add_node("web_search", self._node_web_search)
        graph.add_node("generate_response", self._node_generate_response)
        graph.add_node("store_memory", self._node_store_memory)

        graph.set_entry_point("retrieve_memory")
        graph.add_conditional_edges(
            "retrieve_memory",
            self._should_web_search,
            {
                "search": "web_search",
                "skip": "generate_response",
            },
        )
        graph.add_edge("web_search", "generate_response")
        graph.add_edge("generate_response", "store_memory")
        graph.add_edge("store_memory", END)

        return graph

    @property
    def graph(self):
        """Lazy-compile the graph on first use."""
        if not self._compiled:
            self._graph = self._build_graph().compile()
            self._compiled = True
        return self._graph

    # ─── Graph Nodes ───

    def _node_retrieve_memory(self, state: ConversationState) -> Dict[str, Any]:
        """
        Node 1: Retrieve user context and relevant memories.

        - Loads Profile, ProficiencyAssessment, MistakePattern from DB
        - Semantic search in Weaviate for memories relevant to user_message
        """
        user_id = state["user_id"]
        user_message = state["user_message"]

        user_context = self._build_user_context(user_id)

        relevant_memories = []
        if weaviate_memory_service.is_available:
            try:
                memory_context = weaviate_memory_service.get_conversation_context(
                    user_id=user_id, query=user_message, limit=5
                )
                relevant_memories = memory_context.get("relevant_memories", [])
                user_context["recent_memories"] = memory_context.get(
                    "recent_memories", []
                )
                user_context["mistake_memories"] = memory_context.get(
                    "mistake_patterns", []
                )
            except Exception as e:
                logger.warning(f"Memory retrieval failed: {e}")

        return {
            "user_context": user_context,
            "relevant_memories": relevant_memories,
        }

    def _should_web_search(self, state: ConversationState) -> str:
        """Conditional edge: decide whether to do web search."""
        return "search" if state.get("use_web_search", False) else "skip"

    def _node_web_search(self, state: ConversationState) -> Dict[str, Any]:
        """
        Node 2 (optional): DuckDuckGo web search.
        Ported from EnhancedChatServiceV2.search_web()
        """
        try:
            from duckduckgo_search import DDGS

            ddgs = DDGS()
            results = []
            for r in ddgs.text(state["user_message"], max_results=3):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "body": r.get("body", ""),
                        "link": r.get("href", ""),
                        "source": "DuckDuckGo",
                    }
                )
            return {"web_results": results}
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return {"web_results": []}

    def _node_generate_response(self, state: ConversationState) -> Dict[str, Any]:
        """
        Node 3: Build system prompt with context and call LLM.

        - Selects topic-based system prompt
        - Injects user_context, memories, web results
        - Loads last 10 messages from DB as conversation history
        - Calls LLM via LangChainConfig.get_llm_with_fallback()
        - Parses response
        """
        start_time = time.time()
        conversation_id = state["conversation_id"]
        topic = state.get("topic", "general")

        # Build system prompt
        system_prompt = self._build_system_prompt(
            topic=topic,
            user_context=state.get("user_context", {}),
            relevant_memories=state.get("relevant_memories", []),
            web_results=state.get("web_results", []),
        )

        # Load conversation history from DB
        previous_messages = (
            ChatMessage.query.filter_by(conversation_id=conversation_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )
        previous_messages.reverse()

        # Build LangChain message list
        lc_messages = [SystemMessage(content=system_prompt)]
        for msg in previous_messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            else:
                lc_messages.append(AIMessage(content=msg.content))
        lc_messages.append(HumanMessage(content=state["user_message"]))

        # Invoke LLM with fallback
        try:
            llm = LangChainConfig.get_llm_with_fallback()
            response = llm.invoke(lc_messages)

            ai_text = response.content
            resp_meta = getattr(response, "response_metadata", {}) or {}
            model_name = resp_meta.get("model_name", resp_meta.get("model", "unknown"))
            token_usage = resp_meta.get("token_usage", resp_meta.get("usage", {})) or {}

            parsed = self._parse_response(ai_text)

            return {
                "ai_response_raw": ai_text,
                "ai_response_parsed": parsed,
                "model_used": model_name,
                "tokens_used": token_usage.get("total_tokens", 0),
                "response_time": time.time() - start_time,
            }

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return {
                "ai_response_raw": "",
                "ai_response_parsed": {"content": "I'm sorry, I encountered an error. Please try again."},
                "model_used": "error",
                "tokens_used": 0,
                "response_time": time.time() - start_time,
                "success": False,
                "error": str(e),
            }

    def _node_store_memory(self, state: ConversationState) -> Dict[str, Any]:
        """
        Node 4: Persist interaction to Weaviate memory + save to SQLAlchemy DB.

        - Saves user and assistant ChatMessages
        - Updates ChatConversation
        - Stores interaction summary in Weaviate
        - Extracts and saves vocabulary
        """
        try:
            conversation_id = state["conversation_id"]
            user_id = state["user_id"]
            parsed = state.get("ai_response_parsed", {})

            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                return {
                    "memory_stored": False,
                    "success": False,
                    "error": "Conversation not found during storage",
                }

            # Save user message
            user_msg = ChatMessage(
                conversation_id=conversation_id,
                role="user",
                content=state["user_message"],
            )
            db.session.add(user_msg)

            # Save AI message
            content = parsed.get("content", state.get("ai_response_raw", ""))
            ai_msg = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=content,
                telugu_translation=parsed.get("telugu_translation"),
                grammar_explanation=parsed.get("grammar_explanation"),
                examples=json.dumps(parsed.get("examples", []))
                if parsed.get("examples")
                else None,
                correction=parsed.get("correction"),
                tokens_used=state.get("tokens_used"),
                model_used=state.get("model_used"),
                response_time=state.get("response_time"),
            )
            db.session.add(ai_msg)

            # Update conversation
            conversation.message_count = (conversation.message_count or 0) + 2
            conversation.updated_at = datetime.utcnow()

            db.session.commit()

            # Store in Weaviate memory (non-blocking, graceful failure)
            if weaviate_memory_service.is_available:
                try:
                    memory_content = f"User asked: {state['user_message']}"
                    if parsed.get("vocabulary_words"):
                        memory_content += (
                            f"\nVocabulary: {', '.join(parsed['vocabulary_words'][:5])}"
                        )
                    if parsed.get("grammar_explanation"):
                        memory_content += (
                            f"\nGrammar: {parsed['grammar_explanation'][:100]}"
                        )

                    weaviate_memory_service.add_memory(
                        user_id=user_id,
                        content=memory_content,
                        memory_type="interaction",
                        metadata={
                            "conversation_id": str(conversation_id),
                            "topic": state.get("topic", "general"),
                            "has_correction": str(bool(parsed.get("correction"))),
                        },
                    )
                except Exception as e:
                    logger.warning(f"Weaviate memory storage failed: {e}")

            # Extract and save vocabulary
            self._extract_and_save_vocabulary(
                user_id,
                state["user_message"],
                state.get("ai_response_raw", ""),
                parsed,
            )

            return {
                "memory_stored": True,
                "success": True,
                "error": None,
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"store_memory failed: {e}")
            return {
                "memory_stored": False,
                "success": False,
                "error": str(e),
            }

    # ─── Public API Methods ───

    def send_message(
        self,
        conversation_id: int,
        user_message: str,
        user_id: int,
        use_web_search: bool = False,
        topic: str = "general",
    ) -> Dict[str, Any]:
        """
        Main entry point. Runs the LangGraph graph.

        Args:
            conversation_id: Conversation ID
            user_message: User's message text
            user_id: User ID
            use_web_search: Whether to enable DuckDuckGo search
            topic: Learning topic category

        Returns:
            Dict with success, user_message, ai_response, conversation, etc.
        """
        # Verify conversation ownership
        conversation = ChatConversation.query.get(conversation_id)
        if not conversation:
            return {"error": "Conversation not found", "success": False}
        if conversation.user_id != user_id:
            return {"error": "Unauthorized access", "success": False}

        if not user_message or not user_message.strip():
            return {"error": "Message cannot be empty", "success": False}

        # Build initial state
        initial_state: ConversationState = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "user_message": user_message.strip(),
            "topic": topic,
            "use_web_search": use_web_search,
            "user_context": {},
            "relevant_memories": [],
            "web_results": [],
            "ai_response_raw": "",
            "ai_response_parsed": {},
            "model_used": "",
            "tokens_used": 0,
            "response_time": 0.0,
            "memory_stored": False,
            "success": False,
            "error": None,
        }

        # Run graph
        try:
            final_state = self.graph.invoke(initial_state)
        except Exception as e:
            logger.error(f"Graph execution failed: {e}")
            return {"error": f"Chat service error: {str(e)}", "success": False}

        if not final_state.get("success"):
            return {
                "error": final_state.get("error", "Unknown error"),
                "success": False,
            }

        # Fetch saved messages from DB for response
        conversation = ChatConversation.query.get(conversation_id)
        user_msg_db = (
            ChatMessage.query.filter_by(conversation_id=conversation_id, role="user")
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        ai_msg_db = (
            ChatMessage.query.filter_by(
                conversation_id=conversation_id, role="assistant"
            )
            .order_by(ChatMessage.created_at.desc())
            .first()
        )

        return {
            "success": True,
            "user_message": user_msg_db.to_dict() if user_msg_db else {},
            "ai_response": ai_msg_db.to_dict() if ai_msg_db else {},
            "conversation": conversation.to_dict() if conversation else {},
            "web_search_used": use_web_search,
            "web_results": final_state.get("web_results", []),
            "context_used": {
                "proficiency_level": final_state.get("user_context", {}).get(
                    "proficiency_level"
                ),
                "memories_used": len(final_state.get("relevant_memories", [])),
                "learning_style": final_state.get("user_context", {}).get(
                    "learning_style"
                ),
            },
            "response_time": final_state.get("response_time", 0),
        }

    def create_conversation(
        self,
        user_id: int,
        title: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new conversation."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found", "success": False}

            if not title:
                title = f"Learning Session - {datetime.now().strftime('%b %d, %I:%M %p')}"

            conversation = ChatConversation(
                user_id=user_id,
                title=title,
                topic=topic or "General Learning",
            )
            db.session.add(conversation)
            db.session.commit()

            # Store conversation start in Weaviate
            if weaviate_memory_service.is_available:
                try:
                    weaviate_memory_service.add_memory(
                        user_id=user_id,
                        content=f"Started new {topic or 'general'} learning conversation",
                        memory_type="interaction",
                        metadata={
                            "conversation_id": str(conversation.id),
                            "interaction_type": "conversation_start",
                        },
                    )
                except Exception as e:
                    logger.warning(f"Failed to store conversation start: {e}")

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {
                "error": f"Failed to create conversation: {str(e)}",
                "success": False,
            }

    def get_conversation(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Get conversation with messages."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            return {
                "success": True,
                "conversation": conversation.to_dict(),
                "messages": [m.to_dict() for m in messages],
                "message_count": len(messages),
            }

        except Exception as e:
            return {"error": f"Failed to get conversation: {str(e)}", "success": False}

    def get_user_conversations(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> Dict[str, Any]:
        """Get all conversations for a user."""
        try:
            query = (
                ChatConversation.query.filter_by(user_id=user_id, is_active=True)
                .order_by(ChatConversation.updated_at.desc())
            )
            total = query.count()
            conversations = query.offset(offset).limit(limit).all()

            return {
                "success": True,
                "conversations": [c.to_dict() for c in conversations],
                "total": total,
                "limit": limit,
                "offset": offset,
            }

        except Exception as e:
            return {
                "error": f"Failed to get conversations: {str(e)}",
                "success": False,
            }

    def delete_conversation(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Soft-delete a conversation."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            conversation.is_active = False
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "message": "Conversation deleted"}

        except Exception as e:
            db.session.rollback()
            return {
                "error": f"Failed to delete conversation: {str(e)}",
                "success": False,
            }

    def update_conversation_title(
        self, conversation_id: int, user_id: int, title: str
    ) -> Dict[str, Any]:
        """Update conversation title."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            db.session.commit()

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to update title: {str(e)}", "success": False}

    def generate_summary(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Generate AI-powered conversation summary."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            if not messages:
                return {"error": "No messages in conversation", "success": False}

            conversation_text = "\n".join(
                [
                    f"{'User' if msg.role == 'user' else 'Tutor'}: {msg.content}"
                    for msg in messages[:20]
                ]
            )

            summary_prompt = f"""Analyze this learning conversation and provide a structured summary:

{conversation_text}

Provide:
1. Main topics discussed
2. Key vocabulary learned
3. Grammar concepts covered
4. Mistakes corrected
5. Learning progress assessment
6. Recommended next steps

Format as clear, concise bullet points."""

            try:
                llm = LangChainConfig.get_llm_with_fallback()
                response = llm.invoke(
                    [
                        SystemMessage(
                            content="You are an expert language learning analyst."
                        ),
                        HumanMessage(content=summary_prompt),
                    ]
                )

                return {
                    "success": True,
                    "summary": response.content,
                    "message_count": len(messages),
                    "conversation_id": conversation_id,
                }
            except Exception as e:
                logger.error(f"Summary LLM call failed: {e}")
                return {
                    "success": True,
                    "summary": f"Conversation with {len(messages)} messages about {conversation.topic}",
                    "message_count": len(messages),
                    "conversation_id": conversation_id,
                }

        except Exception as e:
            return {
                "error": f"Summary generation failed: {str(e)}",
                "success": False,
            }

    def get_learning_insights(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive learning insights from chat history.
        Ported from EnhancedChatServiceV2.get_learning_insights()
        """
        try:
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
                topic = conv.topic or "General"
                topics_discussed[topic] = topics_discussed.get(topic, 0) + 1

                messages = ChatMessage.query.filter_by(
                    conversation_id=conv.id
                ).all()
                total_messages += len(messages)

                for msg in messages:
                    if msg.tokens_used:
                        total_tokens += msg.tokens_used

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
                    "start": (
                        conversations[-1].created_at.isoformat()
                        if conversations
                        else None
                    ),
                    "end": (
                        conversations[0].created_at.isoformat()
                        if conversations
                        else None
                    ),
                },
            }

        except Exception as e:
            return {
                "error": f"Failed to get learning insights: {str(e)}",
                "success": False,
            }

    def get_conversation_analytics(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific conversation.
        Ported from EnhancedChatServiceV2.get_conversation_with_context()
        """
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            assistant_messages = [m for m in messages if m.role == "assistant"]
            user_messages = [m for m in messages if m.role == "user"]

            avg_response_time = 0.0
            if assistant_messages:
                response_times = [
                    m.response_time for m in assistant_messages if m.response_time
                ]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)

            total_tokens = sum(
                m.tokens_used for m in assistant_messages if m.tokens_used
            )

            duration = 0
            if messages and len(messages) > 1:
                duration = (
                    messages[-1].created_at - messages[0].created_at
                ).total_seconds()

            return {
                "success": True,
                "conversation": conversation.to_dict(),
                "statistics": {
                    "total_messages": len(messages),
                    "assistant_messages": len(assistant_messages),
                    "user_messages": len(user_messages),
                    "avg_response_time": round(avg_response_time, 2),
                    "total_tokens_used": total_tokens,
                    "conversation_duration": duration,
                },
            }

        except Exception as e:
            return {"error": f"Failed to get analytics: {str(e)}", "success": False}

    def search_user_memories(
        self, user_id: int, query: str, limit: int = 5
    ) -> List[Dict]:
        """Public API for memory search."""
        if weaviate_memory_service.is_available:
            return weaviate_memory_service.search_memories(user_id, query, limit)
        return []

    def search_conversations(
        self, user_id: int, query: str, limit: int = 10
    ) -> Dict[str, Any]:
        """Search conversations by topic."""
        try:
            conversations = (
                ChatConversation.query.filter(
                    ChatConversation.user_id == user_id,
                    ChatConversation.topic.ilike(f"%{query}%"),
                    ChatConversation.is_active == True,
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
            return {
                "error": f"Failed to search conversations: {str(e)}",
                "success": False,
            }

    def export_conversation(
        self, conversation_id: int, user_id: int, export_format: str = "json"
    ) -> Dict[str, Any]:
        """Export conversation in specified format."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return {"error": "Conversation not found", "success": False}

            messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.asc())
                .all()
            )

            if export_format == "markdown":
                md_lines = [f"# {conversation.title}\n"]
                md_lines.append(f"**Topic:** {conversation.topic}")
                md_lines.append(
                    f"**Date:** {conversation.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                )
                md_lines.append("---\n")
                for msg in messages:
                    role = "**You:**" if msg.role == "user" else "**Tutor:**"
                    md_lines.append(f"{role} {msg.content}\n")
                data = "\n".join(md_lines)
            else:
                data = {
                    "conversation": conversation.to_dict(),
                    "messages": [m.to_dict() for m in messages],
                }

            return {
                "success": True,
                "data": data,
                "format": export_format,
                "message_count": len(messages),
            }

        except Exception as e:
            return {"error": f"Export failed: {str(e)}", "success": False}

    # ─── Private Helpers ───

    def _build_user_context(self, user_id: int) -> Dict[str, Any]:
        """
        Build comprehensive user context from SQLAlchemy models.
        Merged from EnhancedChatService._build_user_context()
        """
        context = {
            "user_id": user_id,
            "proficiency_level": "beginner",
            "learning_style": "visual",
            "common_mistakes": [],
            "vocabulary_level": "basic",
            "recent_topics": [],
        }

        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                context.update(
                    {
                        "proficiency_level": profile.proficiency_level or "beginner",
                        "learning_style": profile.learning_style or "visual",
                        "native_language": profile.native_language or "Telugu",
                        "study_hours_per_week": profile.study_hours_per_week or 5,
                        "preferred_difficulty": profile.preferred_difficulty
                        or "intermediate",
                    }
                )
        except Exception as e:
            logger.debug(f"Profile lookup failed: {e}")

        try:
            latest_assessment = (
                ProficiencyAssessment.query.filter_by(user_id=user_id)
                .order_by(ProficiencyAssessment.assessment_date.desc())
                .first()
            )
            if latest_assessment:
                context["vocabulary_level"] = (
                    latest_assessment.vocabulary_level or "basic"
                )
                context["grammar_level"] = latest_assessment.grammar_level or "basic"
        except Exception as e:
            logger.debug(f"Assessment lookup failed: {e}")

        try:
            recent_mistakes = (
                MistakePattern.query.filter_by(user_id=user_id)
                .order_by(MistakePattern.last_occurrence.desc())
                .limit(5)
                .all()
            )
            context["common_mistakes"] = [
                {
                    "type": m.mistake_type,
                    "pattern": m.pattern_description,
                    "frequency": m.frequency,
                }
                for m in recent_mistakes
            ]
        except Exception as e:
            logger.debug(f"Mistake pattern lookup failed: {e}")

        try:
            recent_activities = (
                UserActivityLog.query.filter_by(user_id=user_id)
                .order_by(UserActivityLog.timestamp.desc())
                .limit(10)
                .all()
            )
            topics = set()
            for activity in recent_activities:
                if hasattr(activity, "topic") and activity.topic:
                    topics.add(activity.topic)
            context["recent_topics"] = list(topics)[:5]
        except Exception as e:
            logger.debug(f"Activity lookup failed: {e}")

        return context

    def _build_system_prompt(
        self,
        topic: str,
        user_context: Dict[str, Any],
        relevant_memories: List[Dict],
        web_results: List[Dict],
    ) -> str:
        """
        Build the full system prompt with context.
        Merged from EnhancedChatService._build_enhanced_prompt() +
        EnhancedChatServiceV2._get_system_prompt() + web results formatting.
        """
        # Select base prompt by topic
        topic_lower = topic.lower()
        prompt = SYSTEM_PROMPTS.get("general")
        for key in SYSTEM_PROMPTS:
            if key in topic_lower:
                prompt = SYSTEM_PROMPTS[key]
                break

        # Add user context (from EnhancedChatService._build_enhanced_prompt)
        prompt += f"\n\n=== LEARNER PROFILE ===\n"
        prompt += f"Current Level: {user_context.get('proficiency_level', 'beginner').upper()}\n"
        prompt += f"Learning Style: {user_context.get('learning_style', 'visual').title()}\n"
        prompt += f"Vocabulary Level: {user_context.get('vocabulary_level', 'basic').title()}\n"

        if user_context.get("study_hours_per_week"):
            prompt += f"Study Time: {user_context['study_hours_per_week']} hours/week\n"

        # Add common mistakes
        if user_context.get("common_mistakes"):
            prompt += "\nCommon Mistakes to Address:\n"
            for mistake in user_context["common_mistakes"][:3]:
                prompt += f"- {mistake.get('type', '')}: {mistake.get('pattern', '')}\n"

        # Add recent topics
        if user_context.get("recent_topics"):
            prompt += f"\nRecent Learning Topics: {', '.join(user_context['recent_topics'])}\n"

        # Add relevant memories from Weaviate
        if relevant_memories:
            prompt += "\n=== RELEVANT LEARNING HISTORY ===\n"
            for i, memory in enumerate(relevant_memories[:3], 1):
                memory_text = memory.get("memory", memory.get("content", ""))
                if memory_text:
                    prompt += f"{i}. {memory_text}\n"

        # Add web search results
        if web_results:
            prompt += "\n=== WEB SEARCH RESULTS ===\n"
            for i, result in enumerate(web_results[:3], 1):
                prompt += f"\n{i}. {result.get('title', '')}\n"
                body = result.get("body", "")
                if body:
                    prompt += f"   {body[:200]}...\n"
                link = result.get("link", "")
                if link:
                    prompt += f"   Source: {link}\n"

        prompt += "\n=== TEACHING INSTRUCTIONS ===\n"
        prompt += "Use this context to provide highly personalized, relevant responses.\n"
        prompt += f"Adjust language complexity for {user_context.get('proficiency_level', 'beginner')} level.\n"
        prompt += "Reference past learning when relevant.\n"
        prompt += "Be aware of common mistakes and address them proactively.\n"

        return prompt

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response into structured components.
        Ported from EnhancedChatService._parse_enhanced_response() (most complete version).
        """
        result = {
            "content": response_text,
            "telugu_translation": None,
            "grammar_explanation": None,
            "examples": [],
            "correction": None,
            "vocabulary_words": [],
            "tips": [],
        }

        if not response_text:
            return result

        # Extract Telugu translations
        telugu_pattern = r"\([^)]*[\u0C00-\u0C7F]+[^)]*\)|[\u0C00-\u0C7F]+[^a-zA-Z\n]*[\u0C00-\u0C7F]*"
        telugu_matches = re.findall(telugu_pattern, response_text)
        if telugu_matches:
            result["telugu_translation"] = " ".join(set(telugu_matches))

        lines = response_text.split("\n")
        examples = []
        vocabulary = []
        tips = []
        grammar_lines = []

        for i, line in enumerate(lines):
            line = line.strip()

            # Examples
            if any(
                marker in line.lower()
                for marker in ["example:", "e.g.", "for instance"]
            ):
                example = re.sub(
                    r"^(example|e\.g\.|for instance)[:\s]*", "", line, flags=re.I
                ).strip()
                if example and len(example) > 10:
                    examples.append(example)
                if len(example) < 10 and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(
                        kw in next_line.lower()
                        for kw in ["example", "tip", "note", "grammar"]
                    ):
                        examples.append(next_line)

            # Numbered or bulleted examples
            elif re.match(r"^[\d\u2022\-\*]\s*\.?\s+", line) and len(line) > 15:
                example = re.sub(r"^[\d\u2022\-\*]\s*\.?\s+", "", line).strip()
                if not any(
                    kw in example.lower() for kw in ["tip:", "note:", "grammar:"]
                ):
                    examples.append(example)

            # Grammar explanations
            if any(
                kw in line.lower()
                for kw in ["grammar:", "rule:", "structure:", "form:"]
            ):
                grammar_lines.append(line)

            # Tips
            if any(
                kw in line.lower()
                for kw in ["tip:", "remember:", "note:", "important:"]
            ):
                tip = re.sub(
                    r"^(tip|remember|note|important)[:\s]*", "", line, flags=re.I
                ).strip()
                if tip:
                    tips.append(tip)

            # Vocabulary (words in bold or with Telugu translations)
            vocab_pattern = r"\*\*([a-zA-Z\s]+)\*\*|\b([A-Z][a-z]+)\s*\([^\)]*[\u0C00-\u0C7F]+[^\)]*\)"
            vocab_matches = re.findall(vocab_pattern, line)
            for match in vocab_matches:
                word = match[0] or match[1]
                if word and len(word.strip()) > 2:
                    vocabulary.append(word.strip())

        result["examples"] = examples[:5]
        result["vocabulary_words"] = list(set(vocabulary))[:10]
        result["tips"] = tips[:3]

        if grammar_lines:
            result["grammar_explanation"] = "\n".join(grammar_lines)

        # Detect corrections
        correction_keywords = [
            "correct",
            "should be",
            "better to say",
            "instead of",
            "correction:",
            "correct form:",
        ]
        for line in lines:
            if any(kw in line.lower() for kw in correction_keywords):
                result["correction"] = line.strip()
                break

        return result

    def _extract_and_save_vocabulary(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        parsed_data: Dict[str, Any],
    ) -> None:
        """
        Extract and save new vocabulary words.
        Ported from EnhancedChatService._extract_and_save_vocabulary()
        """
        try:
            vocabulary_words = parsed_data.get("vocabulary_words", [])

            for word in vocabulary_words[:5]:
                existing = VocabularyWord.query.filter_by(
                    user_id=user_id, english_word=word.lower()
                ).first()

                if not existing:
                    telugu_trans = None
                    word_pattern = (
                        rf"\b{re.escape(word)}\b[^\n]*\([^)]*[\u0C00-\u0C7F]+[^)]*\)"
                    )
                    match = re.search(word_pattern, ai_response, re.I)
                    if match:
                        telugu_match = re.search(
                            r"\([^)]*[\u0C00-\u0C7F]+[^)]*\)", match.group()
                        )
                        if telugu_match:
                            telugu_trans = telugu_match.group().strip("()")

                    vocab_entry = VocabularyWord(
                        user_id=user_id,
                        english_word=word.lower(),
                        telugu_translation=telugu_trans,
                        context=ai_response[:200],
                        source="chat_tutor",
                        proficiency_level="learning",
                    )
                    db.session.add(vocab_entry)

            db.session.commit()
        except Exception as e:
            logger.debug(f"Failed to save vocabulary: {e}")
            db.session.rollback()


# Singleton instance
langgraph_chat_service = LangGraphChatService()
