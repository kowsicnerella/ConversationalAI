import json
import re
from datetime import datetime
from app.services.llm_config import LLMConfig
from app.models import db
from app.models.user import User, Profile
from app.models.curriculum import LearningNode, UserLearningPathProgress, NodeCompletion


def _extract_json_from_response(text):
    """
    Extracts a JSON object from a string response, handling markdown code blocks and partial responses.
    """
    # Use the centralized JSON cleaning method
    text = LLMConfig._clean_json_response(text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from partial responses or fix common issues
        try:
            # Look for JSON-like content between curly braces
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_candidate = text[start_idx:end_idx+1]
                return json.loads(json_candidate)
        except json.JSONDecodeError:
            pass
        
        # If all else fails, return error with raw response
        return {"error": "Failed to parse JSON from response.", "raw_response": text}


class ActivityGeneratorService:
    """
    A service class to generate various learning activities using centralized LLM config.
    Uses custom model with Gemini as fallback.
    """

    def __init__(self):
        # No need to initialize models - handled by LLMConfig
        pass

    def generate_personalized_activity(self, user_id, learning_node_id, activity_type=None):
        """
        Generate a fully personalized activity based on user's profile, progress, and target learning node.
        
        Args:
            user_id (int): The user's ID
            learning_node_id (str): The learning node ID (e.g., 'A1_VOCAB_GREETINGS')
            activity_type (str, optional): Specific activity type to generate (flashcard, quiz, etc.)
                                          If None, automatically chooses based on user's weak areas
        
        Returns:
            dict: Generated activity with personalized content
        """
        # Fetch user data
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "User not found"}
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {"error": "User profile not found"}
        
        # Fetch learning node
        node = LearningNode.query.filter_by(node_id=learning_node_id).first()
        if not node:
            return {"error": f"Learning node {learning_node_id} not found"}
        
        # Fetch user's learning path progress
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        # Determine activity type based on user's weak areas if not specified
        if not activity_type:
            activity_type = self._choose_activity_type(profile, node, progress)
        
        # Build personalization context
        context = self._build_personalization_context(user, profile, node, progress)
        
        # Generate the activity with full personalization
        return self._generate_activity_with_context(
            activity_type=activity_type,
            node=node,
            context=context,
            profile=profile
        )
    
    def _choose_activity_type(self, profile, node, progress):
        """
        Intelligently choose activity type based on user's weak areas and node type.
        """
        # Get weak areas from profile mastery metrics
        mastery = profile.mastery_metrics or {}
        weak_skills = [
            skill for skill, score in mastery.items() 
            if score < 50 and skill != 'overall'
        ]
        
        # Map skills to activity types
        skill_to_activity = {
            'vocabulary': 'flashcard',
            'grammar': 'sentence_construction',
            'reading': 'reading_comprehension',
            'writing': 'writing_practice',
            'listening': 'audio_exercise',
            'speaking': 'role_play'
        }
        
        # Prioritize weak skills
        if weak_skills and weak_skills[0] in skill_to_activity:
            return skill_to_activity[weak_skills[0]]
        
        # Fall back to node's activity templates
        if node.activity_templates:
            return node.activity_templates[0]
        
        # Default to quiz
        return 'quiz'
    
    def _build_personalization_context(self, user, profile, node, progress):
        """
        Build a comprehensive context dictionary for personalization.
        """
        context = {
            'user_name': user.username,
            'proficiency_level': profile.proficiency_level or 'beginner',
            'native_language': profile.native_language or 'Telugu',
            'target_language': profile.target_language or 'English',
            'current_streak': profile.current_streak or 0,
            'mastery_metrics': profile.mastery_metrics or {},
            'node_concept': node.concept_name,
            'node_domain': node.skill_domain,
            'learning_objectives': node.learning_objectives,
            'difficulty_range': f"{node.difficulty_range_min}-{node.difficulty_range_max}",
            'cefr_level': self._get_cefr_level_for_node(node)
        }
        
        # Add progress-specific context if available
        if progress:
            context['learned_vocabulary'] = []  # TODO: Track in future update
            context['weak_areas'] = progress.weak_areas or []
            context['strong_areas'] = progress.strong_areas or []
            context['learning_preferences'] = {
                'learning_style': getattr(progress, 'learning_style', 'mixed'),
                'preferred_pace': getattr(progress, 'preferred_pace', 'medium')
            }
            context['vocab_due_for_review'] = []  # TODO: Track in future update
        else:
            context['learned_vocabulary'] = []
            context['weak_areas'] = []
            context['strong_areas'] = []
            context['learning_preferences'] = {}
            context['vocab_due_for_review'] = []
        
        return context
    
    def _get_cefr_level_for_node(self, node):
        """
        Get CEFR level for a learning node by querying the CurriculumLevel relationship.
        Handles the case where the relationship might not be loaded.
        """
        try:
            from app.models.curriculum import CurriculumLevel
            
            if node.curriculum_level_id:
                level = db.session.get(CurriculumLevel, node.curriculum_level_id)
                if level:
                    return level.cefr_level
            
            return 'A1'  # Default fallback
        except Exception as e:
            print(f"Error getting CEFR level for node: {str(e)}")
            return 'A1'
    
    def _generate_activity_with_context(self, activity_type, node, context, profile):
        """
        Generate activity content using AI with full personalization context.
        """
        # Build a comprehensive prompt with personalization
        prompt = f"""
        Generate a personalized English learning activity for a {context['native_language']} speaker.
        
        USER PROFILE:
        - Name: {context['user_name']}
        - Proficiency Level: {context['proficiency_level']}
        - CEFR Level: {context['cefr_level']}
        - Current Streak: {context['current_streak']} days
        - Mastery Metrics: {json.dumps(context['mastery_metrics'], indent=2)}
        
        LEARNING NODE:
        - Concept: {context['node_concept']}
        - Skill Domain: {context['node_domain']}
        - Learning Objectives: {json.dumps(context['learning_objectives'], indent=2)}
        - Difficulty Range: {context['difficulty_range']}
        - Example Content: {json.dumps(node.example_content or {}, indent=2)}
        
        PERSONALIZATION:
        - Learned Vocabulary: {json.dumps(context['learned_vocabulary'][:20], indent=2)} (showing first 20)
        - Weak Areas: {json.dumps(context['weak_areas'], indent=2)}
        - Strong Areas: {json.dumps(context['strong_areas'], indent=2)}
        - Vocabulary Due for Review: {json.dumps(context['vocab_due_for_review'][:10], indent=2)} (showing first 10)
        
        ACTIVITY TYPE: {activity_type}
        
        INSTRUCTIONS:
        1. Generate content that DIRECTLY addresses the learning objectives
        2. Use vocabulary the user has already learned where appropriate
        3. Focus on weak areas: {', '.join(context['weak_areas'][:3]) if context['weak_areas'] else 'all skills'}
        4. Incorporate vocabulary due for review when possible
        5. Adjust difficulty to match user's proficiency level
        6. Provide {context['native_language']} translations where helpful
        7. Make the activity engaging and encourage the user's {context['current_streak']}-day streak
        
        Generate a {activity_type} activity and return as JSON with the following structure:
        """
        
        # Add activity-type-specific JSON schema
        if activity_type == 'quiz':
            prompt += """
        ```json
        {
            "activity_type": "quiz",
            "title": "Activity title in English",
            "description": "Brief description",
            "instructions": "Clear instructions in English",
            "instructions_telugu": "Telugu translation of instructions",
            "estimated_time": 10,
            "questions": [
                {
                    "question_text": "Question in English",
                    "question_telugu": "Telugu translation",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": "Correct option text",
                    "explanation": "Why this is correct (English + Telugu)"
                }
            ]
        }
        ```
        """
        elif activity_type == 'flashcard':
            prompt += """
        ```json
        {
            "activity_type": "flashcard",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Instructions in English",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 10,
            "flashcards": [
                {
                    "front": "English word/phrase",
                    "back": "Telugu translation",
                    "example_sentence": "Example usage in English",
                    "example_sentence_telugu": "Telugu translation"
                }
            ]
        }
        ```
        """
        elif activity_type == 'sentence_construction' or activity_type == 'error_correction':
            prompt += """
        ```json
        {
            "activity_type": "sentence_construction",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Instructions in English",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 15,
            "exercises": [
                {
                    "prompt": "Exercise prompt in English",
                    "prompt_telugu": "Telugu translation",
                    "jumbled_words": ["word1", "word2", "word3"],
                    "correct_sentence": "Correct sentence",
                    "hint": "Helpful hint (optional)"
                }
            ]
        }
        ```
        """
        elif activity_type == 'role_play':
            prompt += """
        ```json
        {
            "activity_type": "role_play",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Instructions in English",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 15,
            "scenario": {
                "setting": "Description of the scene",
                "setting_telugu": "Telugu translation",
                "user_role": "Your role in the conversation",
                "user_role_telugu": "Telugu translation",
                "conversation_goal": "What you need to accomplish",
                "conversation_goal_telugu": "Telugu translation",
                "initial_dialogue": [
                    {
                        "speaker": "Other Character",
                        "text": "First line in English",
                        "text_telugu": "Telugu translation"
                    }
                ],
                "suggested_responses": ["Response 1", "Response 2", "Response 3"]
            }
        }
        ```
        """
        elif activity_type == 'reading_comprehension' or activity_type == 'reading':
            prompt += """
        ```json
        {
            "activity_type": "reading_comprehension",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Instructions in English",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 15,
            "reading_text": "The full reading passage in English (100-150 words)",
            "vocabulary_help": [
                {
                    "word": "difficult word",
                    "meaning": "Telugu translation",
                    "example": "Example usage"
                }
            ],
            "comprehension_questions": [
                {
                    "question": "Question about the text",
                    "question_telugu": "Telugu translation",
                    "answer_type": "multiple_choice or short_answer",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": "Correct answer"
                }
            ]
        }
        ```
        """
        elif activity_type == 'writing_practice' or activity_type == 'writing':
            prompt += """
        ```json
        {
            "activity_type": "writing_practice",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Instructions in English",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 20,
            "writing_prompt": {
                "prompt": "Write about... (clear prompt in English)",
                "prompt_telugu": "Telugu translation",
                "minimum_sentences": 5,
                "suggested_structure": ["Point 1 to cover", "Point 2 to cover"],
                "vocabulary_to_use": ["word1", "word2", "word3"],
                "grammar_focus": "Present simple tense"
            }
        }
        ```
        """
        else:
            # Generic activity structure
            prompt += """
        ```json
        {
            "activity_type": "general",
            "title": "Activity title",
            "description": "Brief description",
            "instructions": "Clear instructions",
            "instructions_telugu": "Telugu instructions",
            "estimated_time": 15,
            "content": {
                "main_content": "Activity content here"
            }
        }
        ```
        """
        
        # Generate using LLM
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            activity_data = _extract_json_from_response(result['text'])
            
            # Add AI generation metadata
            activity_data['learning_node_id'] = node.node_id
            activity_data['personalized_for_user'] = context['user_name']
            activity_data['generated_at'] = datetime.now().isoformat()
            activity_data['is_ai_generated'] = True
            activity_data['ai_model'] = result.get('model', 'unknown')
            activity_data['generation_metadata'] = {
                'provider': 'HPC_inference' if 'sarvam' in result.get('model', '').lower() else 'gemini_fallback',
                'model': result.get('model'),
                'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                'generated_at': datetime.now().isoformat()
            }
            
            # Enhance with vocabulary tracking
            try:
                from app.services.vocabulary_integration_service import VocabularyIntegrationService
                vocab_service = VocabularyIntegrationService()
                
                # Get target vocabulary for this activity
                user_id = User.query.filter_by(username=context['user_name']).first().id
                target_words = vocab_service.get_target_vocabulary_for_activity(
                    user_id=user_id,
                    activity_type=activity_type,
                    difficulty_level=context['proficiency_level'],
                    count=5
                )
                
                # Enhance activity with vocabulary
                if target_words:
                    activity_data = vocab_service.enhance_activity_with_vocabulary(
                        activity_data,
                        target_words,
                        activity_type
                    )
            except Exception as e:
                print(f"Error enhancing activity with vocabulary: {e}")
            
            return activity_data
        else:
            return {"error": result.get('error', 'Failed to generate personalized activity')}

    def generate_quiz(self, topic, level="beginner"):
        """
        Generates a multiple-choice quiz for Telugu speakers learning English.
        """
        prompt = f"""
        Generate a 5-question multiple-choice quiz for a Telugu speaker learning English at '{level}' level on the topic of '{topic}'.
        The questions should be in English and test English vocabulary, grammar, or comprehension.
        Provide Telugu translations or explanations where helpful for better understanding.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object should have a single key "questions", which is a list of question objects.
        Each question object must have the following keys:
        - "question_text": The question in English.
        - "question_telugu": Optional Telugu translation/explanation of the question.
        - "options": A list of 4 English strings representing the possible answers.
        - "correct_answer": The string from the "options" list that is the correct answer.
        - "explanation": Brief explanation in English with Telugu translation if needed.

        Example format:
        ```json
        {{
            "questions": [
                {{
                    "question_text": "What does 'apple' mean?",
                    "question_telugu": "'apple' అంటే ఏమిటి?",
                    "options": ["A fruit", "A vegetable", "A color", "An animal"],
                    "correct_answer": "A fruit",
                    "explanation": "Apple is a fruit. Telugu: యాపిల్ ఒక పండు."
                }}
            ]
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            quiz_data = _extract_json_from_response(result['text'])
            # Add AI generation metadata
            quiz_data['is_ai_generated'] = True
            quiz_data['ai_model'] = result.get('model', 'unknown')
            quiz_data['generated_at'] = datetime.now().isoformat()
            quiz_data['topic'] = topic
            quiz_data['level'] = level
            return quiz_data
        else:
            return {"error": result.get('error', 'Failed to generate quiz')}

    def generate_flashcards(self, topic, level="beginner"):
        """
        Generates English flashcards with Telugu translations for Telugu speakers.
        """
        prompt = f"""
        Generate a set of 10 English flashcards for a Telugu speaker at '{level}' level on the topic of '{topic}'.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object should have a single key "flashcards", which is a list of flashcard objects.
        Each flashcard object must have "front" (English word/phrase) and "back" (Telugu translation).

        Example format:
        ```json
        {{
            "flashcards": [
                {{
                    "front": "Hello",
                    "back": "హలో / నమస్కారం"
                }},
                {{
                    "front": "Goodbye",
                    "back": "వీడ్కోలు"
                }}
            ]
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            flashcard_data = _extract_json_from_response(result['text'])
            # Add AI generation metadata
            flashcard_data['is_ai_generated'] = True
            flashcard_data['ai_model'] = result.get('model', 'unknown')
            flashcard_data['generated_at'] = datetime.now().isoformat()
            flashcard_data['topic'] = topic
            flashcard_data['level'] = level
            return flashcard_data
        else:
            return {"error": result.get('error', 'Failed to generate flashcards')}

    def generate_general_chat_response(self, message_history, user_message):
        """
        Generates a response for English learning chat for Telugu speakers.
        """
        system_prompt = "You are a friendly English tutor helping Telugu speakers learn English. Respond in English but provide Telugu translations when helpful. Keep responses simple and encouraging."
        
        # Format messages for chat completion
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(message_history)
        messages.append({"role": "user", "content": user_message})
        
        result = LLMConfig.chat_completion(messages, stream=False)
        if result['success']:
            return result['message']
        else:
            return f"Error: {result.get('error', 'Failed to generate response')}"

    def generate_text_reading(self, topic, level="beginner"):
        """
        Generates English reading practice for Telugu speakers.
        """
        prompt = f"""
        Write a short paragraph (approx. 100 words) in English for a Telugu speaker at '{level}' level about '{topic}'.
        The paragraph should introduce 5 new English vocabulary words.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have two keys:
        - "reading_text": The full paragraph in English.
        - "vocabulary": A list of objects, where each object has "word" (the new English word) and "telugu_translation" (its Telugu meaning).

        Example format:
        ```json
        {{
            "reading_text": "...",
            "vocabulary": [
                {{
                    "word": "beautiful",
                    "telugu_translation": "అందమైన"
                }}
            ]
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            reading_data = _extract_json_from_response(result['text'])
            # Add AI generation metadata
            reading_data['is_ai_generated'] = True
            reading_data['ai_model'] = result.get('model', 'unknown')
            reading_data['generated_at'] = datetime.now().isoformat()
            reading_data['topic'] = topic
            reading_data['level'] = level
            reading_data['activity_type'] = 'reading'
            return reading_data
        else:
            return {"error": result.get('error', 'Failed to generate reading text')}

    def generate_writing_practice_prompt(self, topic, level="beginner"):
        """
        Generates English writing practice prompts for Telugu speakers.
        """
        prompt = f"""
        Create a writing prompt for a Telugu speaker learning English at '{level}' level. The prompt should be about '{topic}'.
        Ask the user to write at least 5 sentences in English.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have two keys:
        - "prompt": The writing prompt in English.
        - "prompt_telugu": Telugu translation of the prompt for better understanding.

        Example format:
        ```json
        {{
            "prompt": "Describe your daily routine in English.",
            "prompt_telugu": "మీ రోజువారీ క్రమం కురిత్తే ఇంగ్లీష్ లో వర్ణించండి."
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            writing_data = _extract_json_from_response(result['text'])
            # Add AI generation metadata
            writing_data['is_ai_generated'] = True
            writing_data['ai_model'] = result.get('model', 'unknown')
            writing_data['generated_at'] = datetime.now().isoformat()
            writing_data['topic'] = topic
            writing_data['level'] = level
            writing_data['activity_type'] = 'writing'
            return writing_data
        else:
            return {"error": result.get('error', 'Failed to generate writing prompt')}

    def generate_role_playing_scenario(self, topic, level="beginner"):
        """
        Generates English role-playing scenarios for Telugu speakers.
        """
        prompt = f"""
        Create a role-playing scenario for a Telugu speaker learning English at '{level}' level where the user needs to '{topic}'.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have the following keys:
        - "setting": A brief description of the scene in English.
        - "setting_telugu": Telugu translation of the setting.
        - "user_goal": What the user needs to accomplish in English.
        - "user_goal_telugu": Telugu translation of the goal.
        - "initial_line": The first line from the other character in English.

        Example format:
        ```json
        {{
            "setting": "At a local grocery store.",
            "setting_telugu": "కిరాణా దుకానం లో",
            "user_goal": "Buy fruits and vegetables.",
            "user_goal_telugu": "పండ్లు మరియు కూరగాయలు కొనడం",
            "initial_line": "Good morning! How can I help you today?"
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            roleplay_data = _extract_json_from_response(result['text'])
            # Add AI generation metadata
            roleplay_data['is_ai_generated'] = True
            roleplay_data['ai_model'] = result.get('model', 'unknown')
            roleplay_data['generated_at'] = datetime.now().isoformat()
            roleplay_data['topic'] = topic
            roleplay_data['level'] = level
            roleplay_data['activity_type'] = 'role_play'
            return roleplay_data
        else:
            return {"error": result.get('error', 'Failed to generate role-playing scenario')}

    def analyze_image_for_learning(self, image):
        """
        Analyzes an image for English learning activities for Telugu speakers.
        """
        prompt = f"""
        This user is a Telugu speaker learning English. Identify the main object in this image.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have the following keys:
        - "object_name_english": The name of the object in English.
        - "object_name_telugu": The Telugu translation of the object's name.
        - "sample_sentence": A simple sentence in English using the object's name.
        - "sentence_telugu": Telugu translation of the sample sentence.

        Example format:
        ```json
        {{
            "object_name_english": "apple",
            "object_name_telugu": "పెప్పండు",
            "sample_sentence": "I eat an apple every day.",
            "sentence_telugu": "నేను ప్రతి రోజు ఒక ఆపిల్ తిన్నడి."
        }}
        ```
        """
        result = LLMConfig.analyze_image(image, prompt, json_mode=True)
        if result['success']:
            return _extract_json_from_response(result['analysis'])
        else:
            return {"error": result.get('error', 'Failed to analyze image')}

    def get_feedback_on_writing(self, user_writing):
        """
        Provides structured feedback on English writing for Telugu speakers.
        """
        prompt = f"""
        The user is a Telugu speaker practicing English writing. Here is their writing: '{user_writing}'.
        Review it for grammatical errors and suggest improvements.
        Return the output as a JSON object enclosed in a ```json code block.
        The JSON object must have three keys:
        - "corrected_text": The full text with corrections applied.
        - "errors": A list of error objects, where each object has "original_phrase", "correction", and "explanation".
        - "encouragement": A positive message in both English and Telugu to motivate the learner.

        Example format:
        ```json
        {{
            "corrected_text": "I go to school every day.",
            "errors": [
                {{
                    "original_phrase": "I goes to school",
                    "correction": "I go to school",
                    "explanation": "Use 'go' not 'goes' with 'I'. Telugu: 'నేను' తో 'go' వాడాలి, 'goes' కాదు."
                }}
            ],
            "encouragement": "Great effort! Keep practicing! Telugu: బాగా రాశారు! అభ్యసించడం కొనసాగించండి!"
        }}
        ```
        """
        result = LLMConfig.generate_text(prompt, json_mode=True)
        if result['success']:
            return _extract_json_from_response(result['text'])
        else:
            return {"error": result.get('error', 'Failed to generate feedback')}

    def evaluate_activity_submission(
        self, activity_content, user_answers, activity_type
    ):
        """
        Evaluate user's submitted answers for an activity and provide feedback.

        Args:
            activity_content (dict): The original activity content with questions/tasks
            user_answers (dict): User's responses to the activity
            activity_type (str): Type of activity (quiz, flashcard, etc.)

        Returns:
            dict: Evaluation results with score, feedback, and explanations
        """
        prompt = f"""
        Evaluate the user's answers for a Telugu-English learning activity.
        
        Activity Type: {activity_type}
        Activity Content: {json.dumps(activity_content, indent=2)}
        User Answers: {json.dumps(user_answers, indent=2)}
        
        Please evaluate the answers and provide:
        1. Score achieved (number correct)
        2. Maximum possible score
        3. Detailed feedback for each answer
        4. Encouragement in both English and Telugu
        5. Suggestions for improvement
        
        Return the response in JSON format:
        ```json
        {{
            "score": 4,
            "max_score": 5,
            "feedback": {{
                "question_1": {{
                    "correct": true,
                    "user_answer": "book",
                    "correct_answer": "book", 
                    "explanation": "Correct! Telugu: సరైనది!"
                }},
                "question_2": {{
                    "correct": false,
                    "user_answer": "goes",
                    "correct_answer": "go",
                    "explanation": "Incorrect. Use 'go' with 'I'. Telugu: 'నేను' తో 'go' వాడాలి."
                }}
            }},
            "overall_feedback": "Good job! You got 4 out of 5 correct.",
            "telugu_feedback": "బాగుంది! మీరు 5లో 4 సరిగా చేశారు.",
            "suggestions": [
                "Practice subject-verb agreement",
                "Review basic verb forms"
            ],
            "encouragement": "Keep practicing! You're making great progress!",
            "telugu_encouragement": "అభ్యసించడం కొనసాగించండి! మీరు బాగా పురోగతి సాధిస్తున్నారు!"
        }}
        ```
        """

        try:
            result = LLMConfig.generate_text(prompt, json_mode=True)
            if not result['success']:
                raise Exception(result.get('error', 'Failed to generate evaluation'))
            
            evaluation_result = _extract_json_from_response(result['text'])

            # Ensure required fields exist
            if "score" not in evaluation_result:
                evaluation_result["score"] = 0
            if "max_score" not in evaluation_result:
                evaluation_result["max_score"] = (
                    len(user_answers) if user_answers else 1
                )
            if "feedback" not in evaluation_result:
                evaluation_result["feedback"] = {}

            return evaluation_result

        except Exception as e:
            # Fallback evaluation if AI fails
            return {
                "score": 0,
                "max_score": len(user_answers) if user_answers else 1,
                "feedback": {},
                "overall_feedback": "Unable to evaluate at this time. Please try again.",
                "telugu_feedback": "ప్రస్తుతం మూల్యాంకనం చేయలేకపోతున్నాము. దయచేసి మళ్లీ ప్రయత్నించండి.",
                "error": str(e),
            }
