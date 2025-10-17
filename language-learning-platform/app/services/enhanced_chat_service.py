"""
Enhanced Chat Service with Mem0 Integration
Provides personalized AI tutoring with context awareness, memory, and improved accuracy
"""

import time
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.models import db, User, ChatConversation, ChatMessage
from app.services.llm_config import LLMConfig
from app.services.mem0_service import Mem0Service
from app.models import (
    Profile,
    UserActivityLog,
    VocabularyWord,
    MistakePattern,
    ProficiencyAssessment,
)
from config import Config


class EnhancedChatService:
    """Enhanced chat service with Mem0 integration for personalized learning"""

    def __init__(self):
        self.mem0_service = Mem0Service()

    # Enhanced system prompt with better structure and guidance
    ENHANCED_TUTOR_PROMPT = """You are an expert English language tutor specializing in teaching Telugu speakers.

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

Remember: Your goal is effective learning through clear communication and personalization."""

    def create_conversation(
        self, user_id: int, title: Optional[str] = None, topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new chat conversation with Mem0 context initialization

        Args:
            user_id: User ID
            title: Optional conversation title
            topic: Optional topic category

        Returns:
            dict: New conversation details or error
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found", "success": False}

            # Get user profile for context
            profile = Profile.query.filter_by(user_id=user_id).first()

            # Generate contextual title if not provided
            if not title:
                title = (
                    f"Learning Session - {datetime.now().strftime('%b %d, %I:%M %p')}"
                )

            conversation = ChatConversation(
                user_id=user_id, title=title, topic=topic or "General Learning"
            )

            db.session.add(conversation)
            db.session.commit()

            # Initialize conversation context in Mem0
            if self.mem0_service.is_available():
                context_message = (
                    f"Started new {topic or 'general'} learning conversation"
                )
                self.mem0_service.add_user_interaction(
                    user_id=user_id,
                    message=context_message,
                    context={
                        "conversation_id": conversation.id,
                        "topic": topic or "general",
                        "proficiency_level": (
                            profile.proficiency_level if profile else "beginner"
                        ),
                        "interaction_type": "conversation_start",
                    },
                )

            return {"success": True, "conversation": conversation.to_dict()}

        except Exception as e:
            db.session.rollback()
            return {
                "error": f"Failed to create conversation: {str(e)}",
                "success": False,
            }

    def send_message_with_context(
        self, conversation_id: int, user_message: str, user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send message with full context awareness using Mem0

        Args:
            conversation_id: ID of the conversation
            user_message: User's message
            user_id: Optional user ID for verification

        Returns:
            dict: Enhanced response with context
        """
        try:
            start_time = time.time()

            # Get conversation
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                return {"error": "Conversation not found", "success": False}

            if user_id and conversation.user_id != user_id:
                return {"error": "Unauthorized access", "success": False}

            # Get user profile and learning context
            user = User.query.get(conversation.user_id)
            profile = Profile.query.filter_by(user_id=conversation.user_id).first()

            # Save user message
            user_msg = ChatMessage(
                conversation_id=conversation_id, role="user", content=user_message
            )
            db.session.add(user_msg)

            # Build enhanced context
            context = self._build_user_context(conversation.user_id, profile)

            # Get relevant memories from Mem0
            relevant_memories = []
            if self.mem0_service.is_available():
                relevant_memories = self.mem0_service.search_user_memories(
                    query=user_message, user_id=conversation.user_id, limit=5
                )

            # Get conversation history
            previous_messages = (
                ChatMessage.query.filter_by(conversation_id=conversation_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(10)
                .all()
            )
            previous_messages.reverse()  # Chronological order

            # Build enhanced system prompt with context
            enhanced_system_prompt = self._build_enhanced_prompt(
                context, relevant_memories
            )

            # Build message history
            messages = []
            for msg in previous_messages:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_message})

            # Get AI response with enhanced context
            result = LLMConfig.chat_completion(
                messages=messages,
                system_prompt=enhanced_system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            if not result.get("success"):
                db.session.rollback()
                return {
                    "error": f"AI response failed: {result.get('error')}",
                    "success": False,
                }

            ai_response = result.get("message", "")

            # Parse and structure the response
            parsed_response = self._parse_enhanced_response(ai_response)

            # Save AI message with metadata
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

            # Store interaction in Mem0
            if self.mem0_service.is_available():
                self._store_interaction_in_memory(
                    user_id=conversation.user_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    conversation_id=conversation_id,
                    parsed_data=parsed_response,
                )

            # Extract and save new vocabulary
            self._extract_and_save_vocabulary(
                conversation.user_id, user_message, ai_response, parsed_response
            )

            return {
                "success": True,
                "user_message": user_msg.to_dict(),
                "ai_response": ai_msg.to_dict(),
                "conversation": conversation.to_dict(),
                "context_used": {
                    "proficiency_level": context.get("proficiency_level"),
                    "memories_used": len(relevant_memories),
                    "learning_style": context.get("learning_style"),
                },
            }

        except Exception as e:
            db.session.rollback()
            import traceback

            traceback.print_exc()
            return {"error": f"Failed to send message: {str(e)}", "success": False}

    def _build_user_context(
        self, user_id: int, profile: Optional[Profile]
    ) -> Dict[str, Any]:
        """Build comprehensive user context for personalization"""
        context = {
            "user_id": user_id,
            "proficiency_level": "beginner",
            "learning_style": "visual",
            "common_mistakes": [],
            "vocabulary_level": "basic",
            "recent_topics": [],
        }

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

        # Get recent assessment data
        latest_assessment = (
            ProficiencyAssessment.query.filter_by(user_id=user_id)
            .order_by(ProficiencyAssessment.assessment_date.desc())
            .first()
        )

        if latest_assessment:
            context["vocabulary_level"] = latest_assessment.vocabulary_level or "basic"
            context["grammar_level"] = latest_assessment.grammar_level or "basic"

        # Get common mistakes
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

        # Get recent topics from activities
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

        return context

    def _build_enhanced_prompt(
        self, context: Dict[str, Any], memories: List[Dict[str, Any]]
    ) -> str:
        """Build enhanced system prompt with user context and memories"""

        # Base prompt
        prompt = self.ENHANCED_TUTOR_PROMPT

        # Add user context
        prompt += f"\n\n=== LEARNER PROFILE ===\n"
        prompt += (
            f"Current Level: {context.get('proficiency_level', 'beginner').upper()}\n"
        )
        prompt += f"Learning Style: {context.get('learning_style', 'visual').title()}\n"
        prompt += (
            f"Vocabulary Level: {context.get('vocabulary_level', 'basic').title()}\n"
        )

        if context.get("study_hours_per_week"):
            prompt += f"Study Time: {context['study_hours_per_week']} hours/week\n"

        # Add common mistakes awareness
        if context.get("common_mistakes"):
            prompt += f"\nCommon Mistakes to Address:\n"
            for mistake in context["common_mistakes"][:3]:
                prompt += f"- {mistake['type']}: {mistake['pattern']}\n"

        # Add recent topics
        if context.get("recent_topics"):
            prompt += (
                f"\nRecent Learning Topics: {', '.join(context['recent_topics'])}\n"
            )

        # Add relevant memories
        if memories:
            prompt += f"\n=== RELEVANT LEARNING HISTORY ===\n"
            for i, memory in enumerate(memories[:3], 1):
                memory_text = memory.get("memory", memory.get("text", ""))
                if memory_text:
                    prompt += f"{i}. {memory_text}\n"

        prompt += "\n=== TEACHING INSTRUCTIONS ===\n"
        prompt += (
            "Use this context to provide highly personalized, relevant responses.\n"
        )
        prompt += f"Adjust language complexity for {context.get('proficiency_level', 'beginner')} level.\n"
        prompt += "Reference past learning when relevant.\n"
        prompt += "Be aware of common mistakes and address them proactively.\n"

        return prompt

    def _parse_enhanced_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response with improved extraction"""
        result = {
            "content": response_text,
            "telugu_translation": None,
            "grammar_explanation": None,
            "examples": [],
            "correction": None,
            "vocabulary_words": [],
            "tips": [],
        }

        # Extract Telugu translations (improved pattern)
        telugu_pattern = r"\([^)]*[\u0C00-\u0C7F]+[^)]*\)|[\u0C00-\u0C7F]+[^a-zA-Z\n]*[\u0C00-\u0C7F]*"
        telugu_matches = re.findall(telugu_pattern, response_text)
        if telugu_matches:
            result["telugu_translation"] = " ".join(set(telugu_matches))

        # Extract examples with better pattern matching
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
                # Check next line if current is just label
                if len(example) < 10 and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not any(
                        kw in next_line.lower()
                        for kw in ["example", "tip", "note", "grammar"]
                    ):
                        examples.append(next_line)

            # Numbered or bulleted examples
            elif re.match(r"^[\d•\-\*]\s*\.?\s+", line) and len(line) > 15:
                example = re.sub(r"^[\d•\-\*]\s*\.?\s+", "", line).strip()
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

            # Vocabulary (words in bold or explained)
            vocab_pattern = r"\*\*([a-zA-Z\s]+)\*\*|\b([A-Z][a-z]+)\s*\([^\)]*[\u0C00-\u0C7F]+[^\)]*\)"
            vocab_matches = re.findall(vocab_pattern, line)
            for match in vocab_matches:
                word = match[0] or match[1]
                if word and len(word.strip()) > 2:
                    vocabulary.append(word.strip())

        result["examples"] = examples[:5]  # Top 5 examples
        result["vocabulary_words"] = list(set(vocabulary))[:10]  # Unique words
        result["tips"] = tips[:3]  # Top 3 tips

        if grammar_lines:
            result["grammar_explanation"] = "\n".join(grammar_lines)

        # Detect corrections
        correction_keywords = ["correct", "should be", "better to say", "instead of"]
        for line in lines:
            if any(kw in line.lower() for kw in correction_keywords):
                result["correction"] = line.strip()
                break

        return result

    def _store_interaction_in_memory(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        conversation_id: int,
        parsed_data: Dict[str, Any],
    ) -> None:
        """Store interaction in Mem0 for future context"""
        try:
            # Create structured memory entry
            memory_content = f"User asked: {user_message}\n"

            if parsed_data.get("vocabulary_words"):
                memory_content += f"Learned vocabulary: {', '.join(parsed_data['vocabulary_words'][:5])}\n"

            if parsed_data.get("grammar_explanation"):
                memory_content += (
                    f"Grammar topic: {parsed_data['grammar_explanation'][:100]}\n"
                )

            self.mem0_service.add_user_interaction(
                user_id=user_id,
                message=memory_content,
                context={
                    "conversation_id": conversation_id,
                    "interaction_type": "chat_message",
                    "has_examples": bool(parsed_data.get("examples")),
                    "has_correction": bool(parsed_data.get("correction")),
                    "vocabulary_count": len(parsed_data.get("vocabulary_words", [])),
                },
            )
        except Exception as e:
            print(f"Failed to store in Mem0: {e}")

    def _extract_and_save_vocabulary(
        self,
        user_id: int,
        user_message: str,
        ai_response: str,
        parsed_data: Dict[str, Any],
    ) -> None:
        """Extract and save new vocabulary words"""
        try:
            vocabulary_words = parsed_data.get("vocabulary_words", [])

            for word in vocabulary_words[:5]:  # Limit to 5 per interaction
                # Check if word already exists
                existing = VocabularyWord.query.filter_by(
                    user_id=user_id, english_word=word.lower()
                ).first()

                if not existing:
                    # Extract Telugu translation if available
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
            print(f"Failed to save vocabulary: {e}")
            db.session.rollback()

    def get_conversation_summary(
        self, conversation_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Generate an AI-powered conversation summary"""
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

            # Build summary prompt
            conversation_text = "\n".join(
                [
                    f"{'User' if msg.role == 'user' else 'Tutor'}: {msg.content}"
                    for msg in messages
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

            result = LLMConfig.chat_completion(
                messages=[{"role": "user", "content": summary_prompt}],
                system_prompt="You are an expert language learning analyst.",
                temperature=0.5,
                max_tokens=1000,
            )

            if result.get("success"):
                return {
                    "success": True,
                    "summary": result.get("message"),
                    "message_count": len(messages),
                    "conversation_id": conversation_id,
                }

            return {"error": "Failed to generate summary", "success": False}

        except Exception as e:
            return {"error": f"Summary generation failed: {str(e)}", "success": False}


# Global instance
enhanced_chat_service = EnhancedChatService()
