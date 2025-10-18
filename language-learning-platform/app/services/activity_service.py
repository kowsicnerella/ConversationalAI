from app.models import db, User, VocabularyWord, LearningSession
from datetime import datetime
from app.services.llm_config import LLMConfig
import json
import re
import time


class ActivityService:
    """
    Service for generating and evaluating learning activities.
    Supports: Quiz, Flashcards, Conversation Practice, etc.
    ALL content is AI-generated - NO mock data fallbacks.
    Uses centralized LLM config with custom model and Gemini fallback.
    """

    def __init__(self):
        # No need to configure - handled by LLMConfig
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def _generate_ai_content_with_retry(self, prompt, content_type="content"):
        """
        Generate AI content with retry logic - ensures NO mock data fallback.

        Args:
            prompt: The prompt for AI generation
            content_type: Type of content being generated (for logging)

        Returns:
            dict: Parsed JSON response from AI

        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                print(
                    f"Generating {content_type} with AI (attempt {attempt + 1}/{self.max_retries})..."
                )
                result = LLMConfig.generate_text(prompt, json_mode=True)
                
                if not result['success']:
                    last_error = result.get('error', 'Unknown error')
                    print(f"✗ AI returned error: {last_error}")
                else:
                    parsed_result = self._parse_json_response(result['text'])
                    if "error" not in parsed_result:
                        print(f"✓ {content_type} generated successfully!")
                        return parsed_result
                    else:
                        last_error = parsed_result.get("error", "Unknown error")
                        print(f"✗ AI returned error: {last_error}")

            except Exception as e:
                last_error = str(e)
                print(f"✗ Attempt {attempt + 1} failed: {last_error}")

            # Wait before retry (exponential backoff)
            if attempt < self.max_retries - 1:
                wait_time = self.retry_delay * (2**attempt)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        # All retries failed - raise exception instead of returning mock data
        error_msg = f"Failed to generate {content_type} after {self.max_retries} attempts. Last error: {last_error}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

    def generate_quiz(
        self, user_id, topic="daily routine", level="beginner", num_questions=5
    ):
        """
        Generate a multiple-choice quiz using AI.

        Args:
            user_id: User ID for personalization
            topic: Quiz topic (e.g., "daily routine", "food", "travel")
            level: Difficulty level (beginner, intermediate, advanced)
            num_questions: Number of questions to generate

        Returns:
            dict: Quiz data with questions, options, correct answers
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Create AI prompt for quiz generation
            prompt = f"""
Generate a {level}-level English learning quiz about "{topic}" for Telugu speakers.

Create {num_questions} multiple-choice questions with the following JSON format:

{{
  "quiz_title": "Quiz title",
  "quiz_title_telugu": "క్విజ్ శీర్షిక",
  "topic": "{topic}",
  "level": "{level}",
  "questions": [
    {{
      "question_id": 1,
      "question_text": "Question in English",
      "question_telugu": "ప్రశ్న తెలుగులో",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Explanation why this is correct. తెలుగు వివరణ.",
      "points": 8
    }}
  ]
}}

Requirements:
- Questions should be appropriate for {level} level
- Include Telugu translations for questions
- Provide clear explanations with Telugu translations
- 4 options per question
- Questions should test practical English usage
- Focus on common phrases and vocabulary related to "{topic}"

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate quiz using AI with retry logic - NO mock data fallback
            quiz_data = self._generate_ai_content_with_retry(prompt, "quiz")

            # Add metadata
            quiz_data["generated_at"] = datetime.utcnow().isoformat()
            quiz_data["user_id"] = user_id
            quiz_data["total_points"] = sum(
                [q.get("points", 8) for q in quiz_data.get("questions", [])]
            )

            return quiz_data

        except Exception as e:
            print(f"❌ Error generating quiz: {str(e)}")
            # Return error instead of mock data
            return {
                "error": f"Failed to generate quiz: {str(e)}",
                "message": "Unable to generate AI content. Please try again later.",
            }

    def generate_flashcards(
        self, user_id, topic="food", level="beginner", num_cards=10
    ):
        """
        Generate vocabulary flashcards using AI.

        Args:
            user_id: User ID
            topic: Topic for vocabulary (e.g., "food", "travel", "work")
            level: Difficulty level
            num_cards: Number of flashcards

        Returns:
            dict: Flashcard data with English-Telugu pairs
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            prompt = f"""
Generate {num_cards} vocabulary flashcards for {level}-level English learners (Telugu speakers) about "{topic}".

Create flashcards in this JSON format:

{{
  "title": "Flashcard Set Title",
  "title_telugu": "ఫ్లాష్‌కార్డ్ సెట్ శీర్షిక",
  "topic": "{topic}",
  "level": "{level}",
  "flashcards": [
    {{
      "id": 1,
      "front": "English word or phrase",
      "back": "తెలుగు అనువాదం",
      "example_sentence": "Example sentence in English",
      "example_telugu": "ఉదాహరణ వాక్యం తెలుగులో",
      "pronunciation": "Phonetic pronunciation",
      "difficulty": "{level}"
    }}
  ]
}}

Requirements:
- Words/phrases should be {level} level
- Include both Telugu script and English transliteration where helpful
- Provide example sentences for context
- Focus on practical, commonly used vocabulary for "{topic}"
- Include pronunciation hints for difficult words

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate flashcards using AI with retry logic - NO mock data fallback
            flashcard_data = self._generate_ai_content_with_retry(prompt, "flashcards")

            flashcard_data["generated_at"] = datetime.utcnow().isoformat()
            flashcard_data["user_id"] = user_id
            flashcard_data["total_cards"] = len(flashcard_data.get("flashcards", []))

            return flashcard_data

        except Exception as e:
            print(f"❌ Error generating flashcards: {str(e)}")
            # Return error instead of mock data
            return {
                "error": f"Failed to generate flashcards: {str(e)}",
                "message": "Unable to generate AI content. Please try again later.",
            }

    def evaluate_activity_submission(
        self, user_id, activity_type, activity_data, user_answers
    ):
        """
        Evaluate user's activity submission and calculate score.

        Args:
            user_id: User ID
            activity_type: Type of activity ("quiz", "flashcard", "conversation")
            activity_data: Original activity data (questions, flashcards, etc.)
            user_answers: User's responses

        Returns:
            dict: Evaluation results with score, feedback, points earned
        """
        try:
            if activity_type == "quiz":
                return self._evaluate_quiz(user_id, activity_data, user_answers)
            elif activity_type == "flashcard":
                return self._evaluate_flashcards(user_id, activity_data, user_answers)
            elif activity_type == "writing":
                return self.evaluate_writing(
                    user_id, activity_data, user_answers.get("user_text", "")
                )
            else:
                return {"error": f"Unknown activity type: {activity_type}"}

        except Exception as e:
            print(f"Error evaluating activity: {str(e)}")
            return {"error": str(e)}

    def _evaluate_quiz(self, user_id, quiz_data, user_answers):
        """Evaluate quiz submission"""
        questions = quiz_data.get("questions", [])
        total_questions = len(questions)
        correct_count = 0
        feedback_items = []

        for question in questions:
            question_id = question.get("question_id")
            correct_answer = question.get("correct_answer")
            user_answer = user_answers.get(str(question_id))

            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1

            feedback_items.append(
                {
                    "question_id": question_id,
                    "question_text": question.get("question_text"),
                    "user_answer": user_answer,
                    "correct_answer": correct_answer,
                    "is_correct": is_correct,
                    "explanation": question.get("explanation"),
                }
            )

        score_percentage = int((correct_count / total_questions) * 100)
        points_earned = correct_count * 8  # 8 points per correct answer

        # Generate encouraging feedback
        if score_percentage >= 80:
            feedback_message = "Excellent work! మీరు చాలా బాగా చేసారు!"
            feedback_message_telugu = "అద్భుతమైన పని! మీరు చాలా బాగా చేసారు!"
        elif score_percentage >= 60:
            feedback_message = "Good job! Keep practicing. మంచి పని! ప్రాక్టీస్ కొనసాగించండి."
            feedback_message_telugu = "మంచి పని! ప్రాక్టీస్ కొనసాగించండి."
        else:
            feedback_message = "Keep learning! Practice makes perfect. నేర్చుకోండి! ప్రాక్టీస్ పరిపూర్ణతను తెస్తుంది."
            feedback_message_telugu = "నేర్చుకోండి! ప్రాక్టీస్ పరిపూర్ణతను తెస్తుంది."

        # Save vocabulary from quiz
        self._save_vocabulary_from_activity(user_id, questions, "quiz")

        # Update user points
        self._award_points(user_id, points_earned)

        return {
            "success": True,
            "activity_type": "quiz",
            "total_questions": total_questions,
            "correct_answers": correct_count,
            "score_percentage": score_percentage,
            "points_earned": points_earned,
            "feedback_message": feedback_message,
            "feedback_message_telugu": feedback_message_telugu,
            "detailed_feedback": feedback_items,
            "time_spent_minutes": user_answers.get("time_spent_minutes", 5),
        }

    def _evaluate_flashcards(self, user_id, flashcard_data, user_responses):
        """Evaluate flashcard practice session"""
        flashcards = flashcard_data.get("flashcards", [])
        total_cards = len(flashcards)

        known_count = len(
            [r for r in user_responses.get("responses", []) if r.get("marked_as_known")]
        )
        practice_count = total_cards - known_count

        # Award points (1 point per card reviewed)
        points_earned = total_cards

        # Save vocabulary
        self._save_vocabulary_from_flashcards(user_id, flashcards, user_responses)

        # Update user points
        self._award_points(user_id, points_earned)

        return {
            "success": True,
            "activity_type": "flashcard",
            "total_cards": total_cards,
            "cards_known": known_count,
            "cards_to_practice": practice_count,
            "points_earned": points_earned,
            "feedback_message": f"Great job! You reviewed {total_cards} cards. {known_count} marked as known.",
            "feedback_message_telugu": f"బాగుంది! మీరు {total_cards} కార్డులు సమీక్షించారు. {known_count} తెలిసినవిగా గుర్తించబడ్డాయి.",
            "time_spent_minutes": user_responses.get("time_spent_minutes", 3),
        }

    def _save_vocabulary_from_activity(self, user_id, questions, activity_type):
        """Extract and save vocabulary from quiz questions"""
        try:
            for question in questions:
                # Extract key vocabulary from question and correct answer
                text = f"{question.get('question_text', '')} {question.get('correct_answer', '')}"
                words = self._extract_key_words(text)

                for word in words:
                    # Check if word already exists
                    existing = VocabularyWord.query.filter_by(
                        user_id=user_id, english_word=word.lower()
                    ).first()

                    if not existing:
                        vocab = VocabularyWord(
                            user_id=user_id,
                            english_word=word.lower(),
                            telugu_translation="",  # Would need translation
                            context_sentence=question.get("question_text", ""),
                            source_activity=activity_type,
                            discovered_at=datetime.utcnow(),
                        )
                        db.session.add(vocab)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving vocabulary: {str(e)}")

    def _save_vocabulary_from_flashcards(self, user_id, flashcards, user_responses):
        """Save vocabulary from flashcards"""
        try:
            responses_dict = {
                r.get("card_id"): r for r in user_responses.get("responses", [])
            }

            for card in flashcards:
                card_id = card.get("id")
                response = responses_dict.get(card_id, {})

                # Check if word already exists
                english_word = card.get("front", "").lower()
                existing = VocabularyWord.query.filter_by(
                    user_id=user_id, english_word=english_word
                ).first()

                if existing:
                    # Update mastery level if marked as known
                    if response.get("marked_as_known"):
                        existing.mastery_level = min(5, existing.mastery_level + 1)
                else:
                    # Create new vocabulary entry
                    vocab = VocabularyWord(
                        user_id=user_id,
                        english_word=english_word,
                        telugu_translation=card.get("back", ""),
                        context_sentence=card.get("example_sentence", ""),
                        pronunciation=card.get("pronunciation", ""),
                        source_activity="flashcard",
                        discovered_at=datetime.utcnow(),
                        mastery_level=1 if response.get("marked_as_known") else 0,
                    )
                    db.session.add(vocab)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving flashcard vocabulary: {str(e)}")

    def _award_points(self, user_id, points):
        """Award points to user"""
        try:
            user = User.query.get(user_id)
            if user and user.profile:
                user.profile.points = (user.profile.points or 0) + points

                # Level is calculated from points (100 points per level)
                # No need to store level separately - it's derived from points

                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error awarding points: {str(e)}")

    def _extract_key_words(self, text):
        """Extract important words from text"""
        # Simple extraction - remove common words
        common_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "do",
            "does",
            "did",
            "you",
            "i",
            "me",
            "my",
        }
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        return [w for w in words if w not in common_words][:5]  # Top 5 words

    def _parse_json_response(self, text):
        """Parse JSON from AI response"""
        try:
            # Remove markdown code blocks if present
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*", "", text)
            text = text.strip()

            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return {
                "error": "Failed to parse JSON from response.",
                "raw_response": text,
            }

    # ==================== DEPRECATED MOCK DATA METHODS ====================
    # These methods are NO LONGER USED. All content is now AI-generated.
    # Kept commented out for reference only - can be deleted in future cleanup.
    # ======================================================================

    def generate_writing_prompt(self, user_id, topic="family", level="beginner"):
        """
        Generate a writing practice prompt using AI.

        Args:
            user_id: User ID
            topic: Writing topic (e.g., "family", "daily routine", "hobbies")
            level: Difficulty level

        Returns:
            dict: Writing prompt with Telugu translation and guidelines
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Determine sentence count based on level
            sentence_counts = {"beginner": 5, "intermediate": 8, "advanced": 10}
            num_sentences = sentence_counts.get(level, 5)

            prompt = f"""
Generate a writing practice prompt for {level}-level English learners (Telugu speakers) about "{topic}".

Create a prompt in this JSON format:

{{
  "prompt": "Write {num_sentences} sentences about {topic} in English.",
  "prompt_telugu": "Telugu translation of the prompt",
  "topic": "{topic}",
  "level": "{level}",
  "min_sentences": {num_sentences},
  "guidelines": [
    "Guideline 1 in English",
    "Guideline 2 in English"
  ],
  "guidelines_telugu": [
    "మార్గదర్శకం 1 తెలుగులో",
    "మార్గదర్శకం 2 తెలుగులో"
  ],
  "example_sentence": "An example sentence to inspire the user",
  "example_sentence_telugu": "Telugu translation of example"
}}

Requirements:
- Prompt should be clear and specific about "{topic}"
- Appropriate for {level} level (use simple vocabulary for beginner)
- Include 3-4 helpful guidelines (e.g., "Use present tense", "Describe family members")
- Provide one example sentence to inspire the user
- All Telugu translations should be accurate

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate writing prompt using AI with retry logic - NO mock data fallback
            prompt_data = self._generate_ai_content_with_retry(prompt, "writing prompt")

            prompt_data["generated_at"] = datetime.utcnow().isoformat()
            prompt_data["user_id"] = user_id

            return prompt_data

        except Exception as e:
            print(f"❌ Error generating writing prompt: {str(e)}")
            # Return error instead of mock data
            return {
                "error": f"Failed to generate writing prompt: {str(e)}",
                "message": "Unable to generate AI content. Please try again later.",
            }

    def evaluate_writing(self, user_id, writing_data, user_text):
        """
        Evaluate user's writing with AI-powered grammar correction and feedback.

        Args:
            user_id: User ID
            writing_data: Original prompt data
            user_text: User's written text

        Returns:
            dict: Feedback with corrections, explanations, and encouragement
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            topic = writing_data.get("topic", "general")
            level = writing_data.get("level", "beginner")

            # Count sentences
            sentences = [s.strip() for s in re.split(r"[.!?]+", user_text) if s.strip()]
            num_sentences = len(sentences)
            min_required = writing_data.get("min_sentences", 5)

            prompt = f"""
You are an English language teacher for Telugu speakers. Analyze this writing sample and provide detailed feedback.

**Topic:** {topic}
**Level:** {level}
**Minimum sentences required:** {min_required}
**User's writing:**
{user_text}

Provide feedback in this JSON format:

{{
  "corrected_text": "Fully corrected version of the user's writing",
  "sentence_count": {num_sentences},
  "meets_requirement": true/false,
  "errors": [
    {{
      "original_phrase": "phrase with error",
      "correction": "corrected phrase",
      "error_type": "grammar/spelling/punctuation/vocabulary",
      "explanation": "Clear explanation in English why this is wrong and how to fix it",
      "explanation_telugu": "Telugu translation of the explanation"
    }}
  ],
  "strengths": [
    "Positive aspect 1",
    "Positive aspect 2"
  ],
  "improvements": [
    "Suggestion for improvement 1",
    "Suggestion for improvement 2"
  ],
  "encouragement": "Positive, encouraging message in English",
  "encouragement_telugu": "Telugu translation of encouragement",
  "grammar_score": 85,
  "vocabulary_score": 80,
  "overall_score": 82
}}

Requirements:
- Identify ALL grammar, spelling, and punctuation errors
- Provide clear explanations with Telugu translations
- Be encouraging and positive
- Highlight strengths first, then improvements
- Give scores out of 100 for grammar, vocabulary, and overall
- If writing is too short, mention it in improvements

Return ONLY valid JSON, no markdown or extra text.
"""

            result = LLMConfig.generate_text(prompt, json_mode=True)
            if result['success']:
                feedback_data = self._parse_json_response(result['text'])
            else:
                feedback_data = {"error": "Failed to analyze writing. Please try again."}

            if "error" in feedback_data:
                return {"error": "Failed to analyze writing. Please try again."}

            # Calculate points based on quality and length
            base_points = 50  # Base points for completing writing task
            quality_bonus = int(
                (feedback_data.get("overall_score", 0) / 100) * 30
            )  # Up to 30 bonus
            length_bonus = 10 if num_sentences >= min_required else 0
            total_points = base_points + quality_bonus + length_bonus

            feedback_data["points_earned"] = total_points
            feedback_data["activity_type"] = "writing"

            # Award points and save vocabulary
            self._award_points(user_id, total_points)
            self._save_vocabulary_from_writing(user_id, user_text, topic)

            return feedback_data

        except Exception as e:
            print(f"Error evaluating writing: {str(e)}")
            return {"error": str(e)}

    def _save_vocabulary_from_writing(self, user_id, text, topic):
        """Extract and save vocabulary from user's writing"""
        try:
            words = self._extract_key_words(text)

            for word in words:
                # Check if word already exists
                existing = VocabularyWord.query.filter_by(
                    user_id=user_id, english_word=word.lower()
                ).first()

                if not existing:
                    vocab = VocabularyWord(
                        user_id=user_id,
                        english_word=word.lower(),
                        telugu_translation="",
                        context_sentence=text[:200],  # First 200 chars as context
                        source_activity="writing",
                        discovered_at=datetime.utcnow(),
                    )
                    db.session.add(vocab)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving vocabulary from writing: {str(e)}")

    def generate_role_playing_scenario(
        self, user_id, topic="restaurant", level="beginner"
    ):
        """
        Generate a role-playing conversation scenario using AI.

        Args:
            user_id: User ID
            topic: Scenario topic (e.g., "restaurant", "shopping", "interview", "doctor")
            level: Difficulty level

        Returns:
            dict: Scenario setup with setting, goal, and initial AI line
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Map topics to scenario descriptions
            topic_mapping = {
                "restaurant": "ordering food at a restaurant",
                "shopping": "shopping at a store",
                "interview": "job interview",
                "doctor": "visiting a doctor",
                "hotel": "checking into a hotel",
                "airport": "at the airport",
                "bank": "at the bank",
                "phone": "making a phone call",
            }

            scenario_desc = topic_mapping.get(topic.lower(), topic)

            prompt = f"""
Generate a role-playing conversation scenario for {level}-level English learners (Telugu speakers).

Scenario: {scenario_desc}

Create a scenario in this JSON format:

{{
  "scenario_id": "unique_id",
  "title": "Scenario title in English",
  "title_telugu": "దృశ్యం శీర్షిక తెలుగులో",
  "topic": "{topic}",
  "level": "{level}",
  "setting": "Description of where the conversation takes place",
  "setting_telugu": "సెట్టింగ్ తెలుగు వివరణ",
  "user_role": "Your role in the scenario (e.g., 'Customer', 'Patient')",
  "user_role_telugu": "మీ పాత్ర తెలుగులో",
  "ai_role": "AI's role (e.g., 'Waiter', 'Doctor')",
  "ai_role_telugu": "AI పాత్ర తెలుగులో",
  "user_goal": "What you need to accomplish in this conversation",
  "user_goal_telugu": "ఈ సంభాషణలో మీరు సాధించాల్సిన లక్ష్యం",
  "initial_line": "AI's opening line to start the conversation",
  "suggested_responses": [
    "Example response 1 the user could say",
    "Example response 2 the user could say"
  ],
  "suggested_responses_telugu": [
    "ఉదాహరణ ప్రతిస్పందన 1",
    "ఉదాహరణ ప్రతిస్పందన 2"
  ],
  "key_vocabulary": [
    {{"english": "word1", "telugu": "పదం1"}},
    {{"english": "word2", "telugu": "పదం2"}}
  ],
  "difficulty_notes": "Tips for the user about this scenario"
}}

Requirements:
- Scenario should be realistic and practical for {level} level
- Use simple, clear language appropriate for {level} learners
- Initial line should be welcoming and natural
- Provide 2-3 suggested responses to help user start
- Include 5-8 key vocabulary words relevant to the scenario
- All Telugu translations should be accurate

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate scenario using AI with retry logic
            scenario_data = self._generate_ai_content_with_retry(
                prompt, "role-play scenario"
            )

            scenario_data["generated_at"] = datetime.utcnow().isoformat()
            scenario_data["user_id"] = user_id
            scenario_data["conversation_history"] = (
                []
            )  # Initialize empty conversation history

            return scenario_data

        except Exception as e:
            print(f"❌ Error generating role-play scenario: {str(e)}")
            return {
                "error": f"Failed to generate scenario: {str(e)}",
                "message": "Unable to generate AI content. Please try again later.",
            }

    def generate_conversation_response(
        self, user_id, scenario_data, conversation_history, user_message
    ):
        """
        Generate AI response in a role-playing conversation with context awareness.

        Args:
            user_id: User ID
            scenario_data: Original scenario setup
            conversation_history: List of previous messages
            user_message: User's latest message

        Returns:
            dict: AI response with feedback and continuation
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Build conversation context
            context = "\n".join(
                [
                    f"{msg['role']}: {msg['content']}"
                    for msg in conversation_history[
                        -10:
                    ]  # Last 10 messages for context
                ]
            )

            prompt = f"""
You are a conversational English teacher helping Telugu speakers practice {scenario_data.get('topic', 'conversation')}.

**Scenario:** {scenario_data.get('setting', '')}
**Your Role:** {scenario_data.get('ai_role', 'Conversation partner')}
**User's Role:** {scenario_data.get('user_role', 'Learner')}
**User's Goal:** {scenario_data.get('user_goal', 'Practice conversation')}

**Conversation so far:**
{context}

**User's latest message:** {user_message}

Generate a response in this JSON format:

{{
  "ai_response": "Your natural, contextual response as the {scenario_data.get('ai_role', 'partner')}",
  "ai_response_telugu": "AI ప్రతిస్పందన తెలుగులో",
  "grammar_correction": {{
    "has_errors": true/false,
    "corrected_version": "Corrected version of user's message (if errors exist)",
    "errors": [
      {{
        "original": "error phrase",
        "correction": "corrected phrase",
        "explanation": "Why this is wrong",
        "explanation_telugu": "తప్పు వివరణ"
      }}
    ]
  }},
  "encouragement": "Brief positive feedback or tip",
  "encouragement_telugu": "ప్రోత్సాహం తెలుగులో",
  "scenario_progress": "beginning/middle/near_end/complete",
  "next_step_hint": "Subtle hint about what to do next (optional)"
}}

Guidelines:
- Respond naturally as your role ({scenario_data.get('ai_role', 'partner')})
- Keep conversation flowing toward the goal
- If user makes grammar errors, note them but don't break immersion
- Be encouraging and supportive
- Use {scenario_data.get('level', 'beginner')}-appropriate language
- Progress the conversation logically
- Signal completion when goal is achieved

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate response using AI with retry logic
            response_data = self._generate_ai_content_with_retry(
                prompt, "conversation response"
            )

            response_data["timestamp"] = datetime.utcnow().isoformat()

            # Extract vocabulary from user's message
            self._save_vocabulary_from_conversation(
                user_id, user_message, scenario_data.get("topic", "")
            )

            return response_data

        except Exception as e:
            print(f"❌ Error generating conversation response: {str(e)}")
            return {
                "error": f"Failed to generate response: {str(e)}",
                "message": "Unable to generate AI content. Please try again later.",
            }

    def complete_role_play_session(self, user_id, scenario_data, conversation_history):
        """
        Evaluate completed role-play session and provide feedback.

        Args:
            user_id: User ID
            scenario_data: Original scenario
            conversation_history: Full conversation

        Returns:
            dict: Session evaluation with feedback and points
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            # Count conversation turns
            user_messages = [
                msg for msg in conversation_history if msg.get("role") == "user"
            ]
            num_turns = len(user_messages)

            # Extract all user messages
            user_text = " ".join([msg.get("content", "") for msg in user_messages])

            prompt = f"""
Evaluate this role-playing conversation practice session.

**Scenario:** {scenario_data.get('title', '')}
**Goal:** {scenario_data.get('user_goal', '')}
**Difficulty:** {scenario_data.get('level', 'beginner')}
**Number of turns:** {num_turns}

**User's messages:**
{user_text}

Provide evaluation in this JSON format:

{{
  "goal_achieved": true/false,
  "conversation_quality": "excellent/good/fair/needs_improvement",
  "strengths": [
    "Strength 1",
    "Strength 2"
  ],
  "improvements": [
    "Area to improve 1",
    "Area to improve 2"
  ],
  "vocabulary_used": [
    "word1",
    "word2"
  ],
  "grammar_score": 0-100,
  "fluency_score": 0-100,
  "overall_score": 0-100,
  "encouragement": "Motivational message for the learner",
  "encouragement_telugu": "ప్రోత్సాహక సందేశం"
}}

Evaluation criteria:
- Did user achieve the scenario goal?
- Quality of grammar and vocabulary usage
- Conversation flow and naturalness
- Number of turns (more is better)
- Appropriate responses to context

Return ONLY valid JSON, no markdown or extra text.
"""

            # Generate evaluation using AI
            evaluation = self._generate_ai_content_with_retry(
                prompt, "role-play evaluation"
            )

            # Calculate points: base 30 + quality bonus
            base_points = 30
            quality_bonus = int(
                (evaluation.get("overall_score", 70) / 100) * 20
            )  # 0-20 bonus
            turn_bonus = min(num_turns * 2, 10)  # 2 points per turn, max 10

            total_points = base_points + quality_bonus + turn_bonus
            evaluation["points_earned"] = total_points
            evaluation["num_turns"] = num_turns

            # Award points to user
            if user.profile:
                user.profile.points = (user.profile.points or 0) + total_points
                db.session.commit()

            return evaluation

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error completing role-play session: {str(e)}")
            return {
                "error": f"Failed to evaluate session: {str(e)}",
                "message": "Unable to generate AI evaluation. Please try again later.",
            }

    def _save_vocabulary_from_conversation(self, user_id, text, topic):
        """Save new vocabulary from user's conversation messages"""
        try:
            words = self._extract_key_words(text)

            for word in words:
                existing = VocabularyWord.query.filter_by(
                    user_id=user_id, english_word=word
                ).first()

                if not existing:
                    vocab = VocabularyWord(
                        user_id=user_id,
                        english_word=word,
                        telugu_translation="",  # Can be filled later
                        context_sentence=text[:200],  # Save context
                        source_activity=f"roleplay_{topic}",
                        discovered_at=datetime.utcnow(),
                        mastery_level=0,
                    )
                    db.session.add(vocab)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving conversation vocabulary: {str(e)}")
