"""
Content Generation Engine - Phase 2 Implementation
Advanced AI content generation with personalization for all activity types.

This module implements the complete Phase 2 of the AI-Personalized Learning Roadmap,
providing 15+ activity type generators with full personalization capabilities.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.services.llm_config import LLMConfig
from app.models.user import User, Profile
from app.models.curriculum import LearningNode, UserLearningPathProgress
from app.models.activity import Activity, UserActivityLog, ConceptMastery
from app.models.personalization import VocabularyWord, MistakePattern
from app import db


class ContentGenerationEngine:
    """
    Advanced AI content generation with full personalization.
    Implements Phase 2: AI Content Generation Engine from the roadmap.
    """
    
    def __init__(self):
        """Initialize the content generation engine."""
        self.llm_config = LLMConfig()
    
    # ==================== Core Personalization Methods ====================
    
    def _get_user_context(self, user_id: int) -> Dict:
        """
        Gather comprehensive user context for personalization.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user's complete learning context
        """
        user = User.query.get(user_id)
        if not user:
            return {}
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        # Get recent performance
        recent_activities = UserActivityLog.query.filter_by(
            user_id=user_id
        ).order_by(UserActivityLog.completed_at.desc()).limit(10).all()
        
        # Get learned vocabulary
        vocabulary = VocabularyWord.query.filter_by(
            user_id=user_id
        ).filter(VocabularyWord.mastery_level >= 0.5).all()
        
        # Get concept mastery
        concepts = ConceptMastery.query.filter_by(user_id=user_id).all()
        
        # Build context dictionary
        context = {
            'user': {
                'id': user_id,
                'username': user.username,
                'native_language': 'Telugu',  # Default for this platform
            },
            'profile': {
                'current_level': profile.proficiency_level if profile else 'beginner',
                'target_level': 'advanced',  # Default target
                'learning_style': 'mixed',  # Default learning style
                'pace': 'medium',  # Default pace
                'mastery_metrics': profile.mastery_metrics if profile else {},
                'weak_areas': [],  # Can be enhanced later
                'strong_areas': []  # Can be enhanced later
            },
            'progress': {
                'current_node': progress.current_node_id if progress else None,
                'nodes_completed': progress.nodes_completed if progress else 0,
                'current_level': progress.current_level if progress else 'A1',
                'weak_areas': progress.weak_areas if progress else [],
                'strong_areas': progress.strong_areas if progress else []
            },
            'recent_performance': [
                {
                    'activity_type': log.activity.activity_type if log.activity else 'unknown',
                    'score': log.score,
                    'time_spent': log.time_spent_minutes,
                    'accuracy': log.accuracy_score
                }
                for log in recent_activities if log.is_completed
            ],
            'vocabulary': {
                'learned_words': [v.word for v in vocabulary],
                'word_count': len(vocabulary)
            },
            'concepts': {
                concept.concept_name: {
                    'mastery_level': concept.mastery_level,
                    'practice_count': concept.practice_count
                }
                for concept in concepts
            }
        }
        
        return context
    
    def _build_generation_prompt(
        self,
        activity_type: str,
        user_context: Dict,
        specific_requirements: Dict
    ) -> str:
        """
        Build a comprehensive prompt for activity generation.
        
        Args:
            activity_type: Type of activity to generate
            user_context: User's learning context
            specific_requirements: Specific requirements for this activity
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert language learning content creator specializing in personalized English education for Telugu speakers.

USER CONTEXT:
- Current Level: {user_context['profile']['current_level']}
- Target Level: {user_context['profile']['target_level']}
- Learning Style: {user_context['profile']['learning_style']}
- Learning Pace: {user_context['profile']['pace']}
- Native Language: Telugu
- Vocabulary Size: {user_context['vocabulary']['word_count']} words
- Weak Areas: {', '.join(user_context['profile']['weak_areas']) if user_context['profile']['weak_areas'] else 'None identified yet'}
- Strong Areas: {', '.join(user_context['profile']['strong_areas']) if user_context['profile']['strong_areas'] else 'None identified yet'}

ACTIVITY TYPE: {activity_type}

SPECIFIC REQUIREMENTS:
{json.dumps(specific_requirements, indent=2)}

Generate a highly personalized {activity_type} activity that:
1. Matches the user's current level ({user_context['profile']['current_level']})
2. Addresses their weak areas while building on strengths
3. Uses vocabulary appropriate for their level
4. Includes Telugu translations/explanations where helpful
5. Is culturally relevant and engaging
6. Provides clear learning objectives
7. Includes detailed feedback and explanations

Return the response as a valid JSON object with the following structure:
{{
    "activity_type": "{activity_type}",
    "title": "Activity Title",
    "description": "Brief description",
    "difficulty": "beginner/intermediate/advanced",
    "estimated_time_minutes": <number>,
    "learning_objectives": ["objective1", "objective2"],
    "content": {{ /* activity-specific content */ }},
    "instructions": "Clear step-by-step instructions",
    "target_skills": ["skill1", "skill2"],
    "success_criteria": {{ "criteria": "description" }}
}}

Ensure the JSON is properly formatted and valid."""
        
        return prompt
    
    # ==================== Main Activity Generation Method ====================
    
    def generate_personalized_activity(
        self,
        user_id: int,
        learning_node: Optional[LearningNode] = None,
        difficulty: str = 'medium',
        activity_type: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Generate a fully personalized activity based on user's complete context.
        
        This is the main entry point for activity generation that considers:
        - User's current level and performance history
        - Specific learning objective (from learning node)
        - User's learning style and preferences
        - Recent mistakes and weak areas
        - Vocabulary already learned
        - Cultural context (Telugu background)
        
        Args:
            user_id: User ID
            learning_node: Optional learning node to focus on
            difficulty: Difficulty level (easy/medium/hard or 0-1 scale)
            activity_type: Optional specific activity type
            user_context: Optional pre-loaded user context
            
        Returns:
            Dictionary containing the generated activity
        """
        # Get user context if not provided
        if not user_context:
            user_context = self._get_user_context(user_id)
        
        if not user_context:
            return {"error": "Unable to load user context"}
        
        # Determine activity type if not specified
        if not activity_type:
            activity_type = self._determine_optimal_activity_type(user_context, learning_node)
        
        # Map difficulty string to numeric if needed
        difficulty_map = {'easy': 0.3, 'medium': 0.5, 'hard': 0.8}
        numeric_difficulty = difficulty_map.get(difficulty.lower(), 0.5) if isinstance(difficulty, str) else difficulty
        
        # Route to specific generator based on activity type
        generators = {
            'quiz': self.generate_adaptive_quiz,
            'flashcard': self.generate_contextual_flashcards,
            'reading': self.generate_reading_passage,
            'writing': self.generate_writing_prompt,
            'listening': self.generate_listening_exercise,
            'speaking': self.generate_speaking_scenario,
            'real_world': self.generate_real_world_task,
            'pronunciation': self.generate_pronunciation_practice,
            'sentence_construction': self.generate_sentence_construction,
            'dialogue_completion': self.generate_dialogue_completion,
            'error_correction': self.generate_error_correction,
            'story_sequencing': self.generate_story_sequencing,
            'synonym_antonym': self.generate_synonym_antonym,
            'dictation': self.generate_dictation_exercise,
            'translation': self.generate_translation_challenge
        }
        
        generator = generators.get(activity_type)
        if not generator:
            return {"error": f"Unknown activity type: {activity_type}"}
        
        # Generate the activity
        try:
            activity_data = generator(
                user_id=user_id,
                user_context=user_context,
                difficulty=numeric_difficulty,
                learning_node=learning_node
            )
            
            # Add metadata
            activity_data['generated_at'] = datetime.utcnow().isoformat()
            activity_data['user_id'] = user_id
            activity_data['personalization_applied'] = True
            
            return activity_data
            
        except Exception as e:
            return {"error": f"Activity generation failed: {str(e)}"}
    
    def _determine_optimal_activity_type(
        self,
        user_context: Dict,
        learning_node: Optional[LearningNode]
    ) -> str:
        """
        Determine the best activity type based on user context and learning objectives.
        
        Args:
            user_context: User's learning context
            learning_node: Optional learning node
            
        Returns:
            Optimal activity type string
        """
        # If learning node specifies preferred activity templates
        if learning_node and learning_node.activity_templates:
            return learning_node.activity_templates[0]
        
        # Check weak areas and map to activity types
        weak_areas = user_context['profile'].get('weak_areas', [])
        
        if 'vocabulary' in weak_areas:
            return 'flashcard'
        elif 'grammar' in weak_areas:
            return 'sentence_construction'
        elif 'reading' in weak_areas:
            return 'reading'
        elif 'writing' in weak_areas:
            return 'writing'
        elif 'listening' in weak_areas:
            return 'listening'
        elif 'speaking' in weak_areas:
            return 'speaking'
        else:
            # Default to quiz for mixed practice
            return 'quiz'
    
    # ==================== Specific Activity Type Generators ====================
    
    def generate_adaptive_quiz(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        concept: str = None,
        question_count: int = 10,
        focus_areas: List[str] = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate an adaptive quiz with dynamic difficulty.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level (0-1 scale)
            concept: Specific concept to focus on
            question_count: Number of questions
            focus_areas: Specific areas to test
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing the quiz
        """
        # Determine concept from learning node if not specified
        if not concept and learning_node:
            concept = learning_node.concept_name
        
        specific_requirements = {
            'concept': concept or 'Mixed topics',
            'difficulty': difficulty,
            'question_count': question_count,
            'focus_areas': focus_areas or ['vocabulary', 'grammar', 'comprehension'],
            'question_types': ['multiple_choice', 'fill_in_blank', 'true_false'],
            'include_explanations': True,
            'progressive_difficulty': True,
            'learned_vocabulary': user_context['vocabulary']['learned_words'][:50]  # Limit for prompt size
        }
        
        prompt = self._build_generation_prompt('adaptive_quiz', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            quiz_data = LLMConfig._clean_and_parse_json(response)
            
            # Validate and structure
            return {
                'activity_type': 'quiz',
                'title': quiz_data.get('title', f'Quiz on {concept}'),
                'description': quiz_data.get('description', 'Test your knowledge'),
                'difficulty_level': difficulty,
                'questions': quiz_data.get('content', {}).get('questions', []),
                'total_questions': question_count,
                'estimated_time_minutes': quiz_data.get('estimated_time_minutes', question_count * 2),
                'learning_objectives': quiz_data.get('learning_objectives', []),
                'scoring': {
                    'total_points': question_count * 10,
                    'passing_score': question_count * 6,
                    'time_bonus': True
                }
            }
        except Exception as e:
            return self._generate_fallback_quiz(concept, difficulty, question_count)
    
    def generate_contextual_flashcards(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        vocabulary_list: List[str] = None,
        context_theme: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate flashcards with rich contextual examples.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            vocabulary_list: Optional list of words to include
            context_theme: Theme for the flashcards
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing flashcard set
        """
        # Determine theme from learning node
        if not context_theme and learning_node:
            context_theme = learning_node.concept_name
        
        # Generate new vocabulary if list not provided
        if not vocabulary_list:
            vocabulary_list = []  # Will be generated by AI
        
        specific_requirements = {
            'vocabulary_list': vocabulary_list,
            'context_theme': context_theme or 'Daily conversation',
            'difficulty': difficulty,
            'card_count': 15 if not vocabulary_list else len(vocabulary_list),
            'include_examples': True,
            'include_telugu_translation': True,
            'include_pronunciation': True,
            'include_usage_notes': True,
            'avoid_words': user_context['vocabulary']['learned_words'][:100]
        }
        
        prompt = self._build_generation_prompt('contextual_flashcards', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            flashcard_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'flashcard',
                'title': flashcard_data.get('title', f'Flashcards: {context_theme}'),
                'description': flashcard_data.get('description', 'Learn new vocabulary'),
                'theme': context_theme,
                'difficulty_level': difficulty,
                'cards': flashcard_data.get('content', {}).get('cards', []),
                'total_cards': len(flashcard_data.get('content', {}).get('cards', [])),
                'learning_objectives': flashcard_data.get('learning_objectives', []),
                'review_strategy': 'spaced_repetition'
            }
        except Exception as e:
            return self._generate_fallback_flashcards(context_theme, difficulty)
    
    def generate_reading_passage(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        topic: str = None,
        level: str = None,
        target_vocabulary: List[str] = None,
        length_words: int = 300,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate reading comprehension passage with questions.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            topic: Topic for the passage
            level: CEFR level
            target_vocabulary: Words to include
            length_words: Length of passage
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing reading activity
        """
        if not level:
            level = user_context['profile']['current_level']
        
        if not topic and learning_node:
            topic = learning_node.concept_name
        
        specific_requirements = {
            'topic': topic or 'Interesting story',
            'cefr_level': level,
            'difficulty': difficulty,
            'length_words': length_words,
            'target_vocabulary': target_vocabulary or [],
            'include_comprehension_questions': True,
            'question_count': 8,
            'question_types': ['multiple_choice', 'short_answer', 'inference'],
            'include_vocabulary_notes': True,
            'cultural_context': 'Telugu'
        }
        
        prompt = self._build_generation_prompt('reading_passage', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            reading_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'reading',
                'title': reading_data.get('title', 'Reading Comprehension'),
                'description': reading_data.get('description', 'Read and answer questions'),
                'passage': reading_data.get('content', {}).get('passage', ''),
                'passage_length': length_words,
                'difficulty_level': difficulty,
                'questions': reading_data.get('content', {}).get('questions', []),
                'vocabulary_notes': reading_data.get('content', {}).get('vocabulary_notes', {}),
                'learning_objectives': reading_data.get('learning_objectives', []),
                'estimated_time_minutes': reading_data.get('estimated_time_minutes', 15)
            }
        except Exception as e:
            return self._generate_fallback_reading(topic, difficulty, length_words)
    
    def generate_writing_prompt(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        writing_type: str = 'essay',
        target_grammar: List[str] = None,
        word_count_range: Tuple[int, int] = (100, 200),
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate writing practice prompt with guidelines.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            writing_type: Type of writing (essay, email, story, description)
            target_grammar: Grammar structures to practice
            word_count_range: Min and max word count
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing writing activity
        """
        specific_requirements = {
            'writing_type': writing_type,
            'difficulty': difficulty,
            'word_count_min': word_count_range[0],
            'word_count_max': word_count_range[1],
            'target_grammar': target_grammar or ['present_tense', 'proper_punctuation'],
            'include_outline': True,
            'include_vocabulary_suggestions': True,
            'include_grammar_tips': True,
            'rubric_included': True
        }
        
        prompt = self._build_generation_prompt('writing_prompt', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            writing_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'writing',
                'title': writing_data.get('title', f'{writing_type.title()} Writing'),
                'description': writing_data.get('description', 'Practice your writing skills'),
                'prompt': writing_data.get('content', {}).get('prompt', ''),
                'writing_type': writing_type,
                'difficulty_level': difficulty,
                'word_count_range': word_count_range,
                'guidelines': writing_data.get('content', {}).get('guidelines', []),
                'vocabulary_suggestions': writing_data.get('content', {}).get('vocabulary_suggestions', []),
                'grammar_focus': target_grammar,
                'rubric': writing_data.get('content', {}).get('rubric', {}),
                'learning_objectives': writing_data.get('learning_objectives', []),
                'estimated_time_minutes': writing_data.get('estimated_time_minutes', 20)
            }
        except Exception as e:
            return self._generate_fallback_writing(writing_type, difficulty, word_count_range)
    
    def generate_listening_exercise(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        topic: str = None,
        level: str = None,
        duration_seconds: int = 120,
        focus_phonemes: List[str] = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate listening comprehension exercise.
        
        Note: This generates the script and questions. Text-to-speech would be 
        handled by a separate audio service.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            topic: Topic for the audio
            level: CEFR level
            duration_seconds: Length of audio
            focus_phonemes: Specific sounds to practice
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing listening activity
        """
        if not level:
            level = user_context['profile']['current_level']
        
        specific_requirements = {
            'topic': topic or 'Conversation',
            'cefr_level': level,
            'difficulty': difficulty,
            'duration_seconds': duration_seconds,
            'focus_phonemes': focus_phonemes or [],
            'include_transcript': True,
            'include_questions': True,
            'question_count': 6,
            'accent': 'neutral',
            'speed': 'normal' if difficulty < 0.7 else 'fast'
        }
        
        prompt = self._build_generation_prompt('listening_exercise', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            listening_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'listening',
                'title': listening_data.get('title', 'Listening Comprehension'),
                'description': listening_data.get('description', 'Listen and answer questions'),
                'audio_script': listening_data.get('content', {}).get('script', ''),
                'transcript_available': True,
                'difficulty_level': difficulty,
                'duration_seconds': duration_seconds,
                'questions': listening_data.get('content', {}).get('questions', []),
                'focus_phonemes': focus_phonemes,
                'learning_objectives': listening_data.get('learning_objectives', []),
                'estimated_time_minutes': listening_data.get('estimated_time_minutes', 10),
                'audio_generation_required': True  # Flag for TTS service
            }
        except Exception as e:
            return self._generate_fallback_listening(topic, difficulty)
    
    def generate_speaking_scenario(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        scenario_type: str = 'conversation',
        target_phrases: List[str] = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate speaking practice scenario (role-play).
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            scenario_type: Type of scenario (conversation, interview, shopping, etc.)
            target_phrases: Specific phrases to practice
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing speaking activity
        """
        specific_requirements = {
            'scenario_type': scenario_type,
            'difficulty': difficulty,
            'target_phrases': target_phrases or [],
            'include_vocabulary_prep': True,
            'include_sample_responses': True,
            'include_pronunciation_tips': True,
            'roles': 2,
            'turns': 8
        }
        
        prompt = self._build_generation_prompt('speaking_scenario', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            speaking_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'speaking',
                'title': speaking_data.get('title', 'Speaking Practice'),
                'description': speaking_data.get('description', 'Practice speaking in a realistic scenario'),
                'scenario_type': scenario_type,
                'difficulty_level': difficulty,
                'scenario': speaking_data.get('content', {}).get('scenario', ''),
                'your_role': speaking_data.get('content', {}).get('your_role', ''),
                'conversation_flow': speaking_data.get('content', {}).get('conversation_flow', []),
                'target_phrases': target_phrases,
                'vocabulary_prep': speaking_data.get('content', {}).get('vocabulary_prep', []),
                'sample_responses': speaking_data.get('content', {}).get('sample_responses', []),
                'learning_objectives': speaking_data.get('learning_objectives', []),
                'estimated_time_minutes': speaking_data.get('estimated_time_minutes', 10)
            }
        except Exception as e:
            return self._generate_fallback_speaking(scenario_type, difficulty)
    
    def generate_real_world_task(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        task_type: str = 'email',
        industry: str = 'general',
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """
        Generate practical real-world task.
        
        Args:
            user_id: User ID
            user_context: User's learning context
            difficulty: Difficulty level
            task_type: Type of task (email, presentation, negotiation, etc.)
            industry: Industry context
            learning_node: Optional learning node
            
        Returns:
            Dictionary containing real-world task
        """
        specific_requirements = {
            'task_type': task_type,
            'difficulty': difficulty,
            'industry': industry,
            'include_context': True,
            'include_templates': True,
            'include_best_practices': True,
            'evaluation_criteria': True
        }
        
        prompt = self._build_generation_prompt('real_world_task', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            task_data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'real_world',
                'title': task_data.get('title', f'{task_type.title()} Task'),
                'description': task_data.get('description', 'Complete a practical task'),
                'task_type': task_type,
                'industry': industry,
                'difficulty_level': difficulty,
                'task_context': task_data.get('content', {}).get('context', ''),
                'task_instructions': task_data.get('content', {}).get('instructions', ''),
                'templates': task_data.get('content', {}).get('templates', []),
                'best_practices': task_data.get('content', {}).get('best_practices', []),
                'evaluation_criteria': task_data.get('content', {}).get('evaluation_criteria', {}),
                'learning_objectives': task_data.get('learning_objectives', []),
                'estimated_time_minutes': task_data.get('estimated_time_minutes', 25)
            }
        except Exception as e:
            return self._generate_fallback_real_world(task_type, difficulty)
    
    # ==================== NEW Activity Type Generators (8 types) ====================
    
    def generate_pronunciation_practice(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        focus_sounds: List[str] = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate pronunciation practice for specific phonemes."""
        specific_requirements = {
            'focus_sounds': focus_sounds or ['th', 'r', 'v', 'w'],
            'difficulty': difficulty,
            'include_minimal_pairs': True,
            'include_tongue_twisters': True,
            'exercise_count': 10
        }
        
        prompt = self._build_generation_prompt('pronunciation_practice', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'pronunciation',
                'title': data.get('title', 'Pronunciation Practice'),
                'focus_sounds': focus_sounds,
                'exercises': data.get('content', {}).get('exercises', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'pronunciation', 'error': str(e)}
    
    def generate_sentence_construction(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        grammar_focus: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate sentence construction exercises."""
        specific_requirements = {
            'grammar_focus': grammar_focus or 'present_tense',
            'difficulty': difficulty,
            'sentence_count': 12,
            'include_word_bank': True
        }
        
        prompt = self._build_generation_prompt('sentence_construction', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'sentence_construction',
                'title': data.get('title', 'Build Sentences'),
                'grammar_focus': grammar_focus,
                'exercises': data.get('content', {}).get('exercises', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'sentence_construction', 'error': str(e)}
    
    def generate_dialogue_completion(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        context: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate dialogue completion exercises."""
        specific_requirements = {
            'context': context or 'everyday_conversation',
            'difficulty': difficulty,
            'dialogue_count': 5,
            'blank_count_per_dialogue': 4
        }
        
        prompt = self._build_generation_prompt('dialogue_completion', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'dialogue_completion',
                'title': data.get('title', 'Complete the Dialogue'),
                'dialogues': data.get('content', {}).get('dialogues', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'dialogue_completion', 'error': str(e)}
    
    def generate_error_correction(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        error_types: List[str] = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate error correction exercises based on common mistakes."""
        specific_requirements = {
            'error_types': error_types or ['grammar', 'spelling', 'word_choice'],
            'difficulty': difficulty,
            'sentence_count': 15
        }
        
        prompt = self._build_generation_prompt('error_correction', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'error_correction',
                'title': data.get('title', 'Find and Fix Errors'),
                'exercises': data.get('content', {}).get('exercises', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'error_correction', 'error': str(e)}
    
    def generate_story_sequencing(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        theme: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate story sequencing exercise."""
        specific_requirements = {
            'theme': theme or 'daily_life',
            'difficulty': difficulty,
            'sentence_count': 8,
            'include_images_description': True
        }
        
        prompt = self._build_generation_prompt('story_sequencing', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'story_sequencing',
                'title': data.get('title', 'Order the Story'),
                'story_parts': data.get('content', {}).get('story_parts', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'story_sequencing', 'error': str(e)}
    
    def generate_synonym_antonym(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        vocabulary_level: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate synonym/antonym matching exercise."""
        specific_requirements = {
            'vocabulary_level': vocabulary_level or user_context['profile']['current_level'],
            'difficulty': difficulty,
            'word_count': 20,
            'include_both': True
        }
        
        prompt = self._build_generation_prompt('synonym_antonym_matching', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'synonym_antonym',
                'title': data.get('title', 'Match Synonyms & Antonyms'),
                'exercises': data.get('content', {}).get('exercises', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'synonym_antonym', 'error': str(e)}
    
    def generate_dictation_exercise(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        topic: str = None,
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate dictation exercise (listening + writing)."""
        specific_requirements = {
            'topic': topic or 'general',
            'difficulty': difficulty,
            'sentence_count': 10,
            'include_audio_script': True
        }
        
        prompt = self._build_generation_prompt('dictation_exercise', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'dictation',
                'title': data.get('title', 'Dictation Practice'),
                'sentences': data.get('content', {}).get('sentences', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', []),
                'audio_generation_required': True
            }
        except Exception as e:
            return {'activity_type': 'dictation', 'error': str(e)}
    
    def generate_translation_challenge(
        self,
        user_id: int,
        user_context: Dict,
        difficulty: float,
        direction: str = 'telugu_to_english',
        learning_node: Optional[LearningNode] = None
    ) -> Dict:
        """Generate translation exercises (Telugu ↔ English)."""
        specific_requirements = {
            'direction': direction,
            'difficulty': difficulty,
            'sentence_count': 10,
            'include_cultural_notes': True
        }
        
        prompt = self._build_generation_prompt('translation_challenge', user_context, specific_requirements)
        
        try:
            response = LLMConfig.generate_content(prompt)
            data = LLMConfig._clean_and_parse_json(response)
            
            return {
                'activity_type': 'translation',
                'title': data.get('title', 'Translation Practice'),
                'direction': direction,
                'exercises': data.get('content', {}).get('exercises', []),
                'difficulty_level': difficulty,
                'learning_objectives': data.get('learning_objectives', [])
            }
        except Exception as e:
            return {'activity_type': 'translation', 'error': str(e)}
    
    # ==================== Fallback Generators ====================
    
    def _generate_fallback_quiz(self, concept: str, difficulty: float, question_count: int) -> Dict:
        """Generate a basic quiz when AI generation fails."""
        return {
            'activity_type': 'quiz',
            'title': f'Quiz on {concept}',
            'description': 'Test your knowledge',
            'difficulty_level': difficulty,
            'questions': [
                {
                    'question': f'Sample question {i+1} about {concept}',
                    'type': 'multiple_choice',
                    'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'correct_answer': 0,
                    'explanation': 'This is a fallback question.'
                }
                for i in range(min(question_count, 5))
            ],
            'fallback': True
        }
    
    def _generate_fallback_flashcards(self, theme: str, difficulty: float) -> Dict:
        """Generate basic flashcards when AI generation fails."""
        return {
            'activity_type': 'flashcard',
            'title': f'Flashcards: {theme}',
            'description': 'Learn new vocabulary',
            'theme': theme,
            'difficulty_level': difficulty,
            'cards': [
                {
                    'front': 'Sample word',
                    'back': 'Definition',
                    'example': 'Example sentence',
                    'translation_telugu': 'తెలుగు అనువాదం'
                }
            ],
            'fallback': True
        }
    
    def _generate_fallback_reading(self, topic: str, difficulty: float, length: int) -> Dict:
        """Generate basic reading when AI generation fails."""
        return {
            'activity_type': 'reading',
            'title': f'Reading: {topic}',
            'description': 'Read and answer questions',
            'passage': f'This is a sample passage about {topic}. ' * (length // 10),
            'difficulty_level': difficulty,
            'questions': [],
            'fallback': True
        }
    
    def _generate_fallback_writing(self, writing_type: str, difficulty: float, word_range: Tuple) -> Dict:
        """Generate basic writing prompt when AI generation fails."""
        return {
            'activity_type': 'writing',
            'title': f'{writing_type.title()} Writing',
            'description': 'Practice your writing',
            'prompt': f'Write a {writing_type} about a topic of your choice.',
            'writing_type': writing_type,
            'difficulty_level': difficulty,
            'word_count_range': word_range,
            'fallback': True
        }
    
    def _generate_fallback_listening(self, topic: str, difficulty: float) -> Dict:
        """Generate basic listening when AI generation fails."""
        return {
            'activity_type': 'listening',
            'title': f'Listening: {topic}',
            'description': 'Listen and answer questions',
            'audio_script': f'Sample audio script about {topic}.',
            'difficulty_level': difficulty,
            'questions': [],
            'fallback': True
        }
    
    def _generate_fallback_speaking(self, scenario_type: str, difficulty: float) -> Dict:
        """Generate basic speaking scenario when AI generation fails."""
        return {
            'activity_type': 'speaking',
            'title': f'Speaking: {scenario_type}',
            'description': 'Practice speaking',
            'scenario_type': scenario_type,
            'difficulty_level': difficulty,
            'scenario': f'Practice a {scenario_type} scenario.',
            'fallback': True
        }
    
    def _generate_fallback_real_world(self, task_type: str, difficulty: float) -> Dict:
        """Generate basic real-world task when AI generation fails."""
        return {
            'activity_type': 'real_world',
            'title': f'{task_type.title()} Task',
            'description': 'Complete a practical task',
            'task_type': task_type,
            'difficulty_level': difficulty,
            'task_instructions': f'Complete a {task_type} task.',
            'fallback': True
        }


# ==================== Helper function for backward compatibility ====================

def generate_activity(user_id: int, activity_type: str, **kwargs) -> Dict:
    """
    Convenience function for generating activities.
    Maintains backward compatibility with existing code.
    """
    engine = ContentGenerationEngine()
    return engine.generate_personalized_activity(
        user_id=user_id,
        activity_type=activity_type,
        **kwargs
    )
