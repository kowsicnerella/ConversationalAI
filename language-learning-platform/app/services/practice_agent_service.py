from app.models import (
    db, Chapter, UserChapterProgress, PracticeSession, 
    TestAssessment, VocabularyWord, MistakePattern
)
from app.services.activity_generator_service import ActivityGeneratorService
from datetime import datetime, timedelta
from sqlalchemy import func
import json
import random

class PracticeAgentService:
    """
    AI-powered service that generates adaptive practice questions based on user scores,
    learning patterns, and chapter content.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
    
    def generate_adaptive_practice_questions(self, user_id, chapter_id, num_questions=5, session_type='practice'):
        """
        Generate adaptive practice questions based on user's learning history and current performance.
        """
        try:
            # Get user's learning context
            learning_context = self._analyze_user_learning_context(user_id, chapter_id)
            
            # Get chapter content
            chapter = Chapter.query.get(chapter_id)
            if not chapter:
                raise ValueError("Chapter not found")
            
            # Determine adaptive parameters
            adaptive_params = self._calculate_adaptive_parameters(learning_context, chapter)
            
            # Generate questions using AI with adaptive parameters
            questions = self._generate_ai_questions(
                chapter, learning_context, adaptive_params, num_questions, session_type
            )
            
            return {
                'questions': questions,
                'adaptive_info': {
                    'difficulty_level': adaptive_params['difficulty_level'],
                    'focus_areas': adaptive_params['focus_areas'],
                    'question_distribution': adaptive_params['question_distribution'],
                    'estimated_time_minutes': adaptive_params['estimated_time']
                },
                'learning_context': learning_context
            }
            
        except Exception as e:
            raise e
    
    def _analyze_user_learning_context(self, user_id, chapter_id):
        """
        Analyze user's learning context including scores, weaknesses, and learning patterns.
        """
        context = {
            'user_id': user_id,
            'chapter_id': chapter_id,
            'current_chapter_progress': None,
            'previous_chapters_performance': [],
            'identified_weaknesses': [],
            'vocabulary_gaps': [],
            'mistake_patterns': [],
            'learning_velocity': 'medium',
            'preferred_question_types': []
        }
        
        # Get current chapter progress
        current_progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).first()
        
        if current_progress:
            context['current_chapter_progress'] = {
                'status': current_progress.status,
                'best_score': current_progress.best_score,
                'average_score': current_progress.average_score,
                'total_attempts': current_progress.total_attempts,
                'time_spent_minutes': current_progress.time_spent_minutes
            }
        
        # Get performance in previous chapters
        previous_progress = UserChapterProgress.query.filter(
            UserChapterProgress.user_id == user_id,
            UserChapterProgress.chapter_id < chapter_id
        ).order_by(UserChapterProgress.chapter_id.desc()).limit(5).all()
        
        context['previous_chapters_performance'] = [
            {
                'chapter_id': prog.chapter_id,
                'best_score': prog.best_score,
                'average_score': prog.average_score,
                'total_attempts': prog.total_attempts,
                'status': prog.status
            } for prog in previous_progress
        ]
        
        # Analyze mistake patterns
        recent_mistakes = MistakePattern.query.filter_by(
            user_id=user_id, is_resolved=False
        ).order_by(MistakePattern.frequency_count.desc()).limit(10).all()
        
        context['mistake_patterns'] = [
            {
                'mistake_type': mistake.mistake_type,
                'mistake_category': mistake.mistake_category,
                'frequency_count': mistake.frequency_count,
                'last_occurrence': mistake.last_occurrence.isoformat()
            } for mistake in recent_mistakes
        ]
        
        # Get vocabulary gaps
        weak_vocabulary = VocabularyWord.query.filter_by(
            user_id=user_id
        ).filter(VocabularyWord.mastery_level < 0.7).order_by(
            VocabularyWord.mastery_level.asc()
        ).limit(15).all()
        
        context['vocabulary_gaps'] = [
            {
                'english_word': vocab.english_word,
                'telugu_translation': vocab.telugu_translation,
                'mastery_level': vocab.mastery_level,
                'times_practiced': vocab.times_practiced
            } for vocab in weak_vocabulary
        ]
        
        # Calculate learning velocity
        context['learning_velocity'] = self._calculate_learning_velocity(user_id)
        
        # Identify preferred question types from recent sessions
        context['preferred_question_types'] = self._identify_preferred_question_types(user_id)
        
        return context
    
    def _calculate_adaptive_parameters(self, learning_context, chapter):
        """
        Calculate adaptive parameters for question generation based on learning context.
        """
        params = {
            'difficulty_level': chapter.difficulty_level,
            'focus_areas': [],
            'question_distribution': {},
            'estimated_time': 15,
            'reinforcement_needed': [],
            'challenge_level': 'moderate'
        }
        
        # Adjust difficulty based on previous performance
        current_progress = learning_context.get('current_chapter_progress')
        if current_progress:
            avg_score = current_progress.get('average_score', 0)
            attempts = current_progress.get('total_attempts', 0)
            
            if attempts > 0:
                if avg_score >= 0.85:
                    params['difficulty_level'] = self._increase_difficulty(chapter.difficulty_level)
                    params['challenge_level'] = 'high'
                elif avg_score <= 0.6:
                    params['difficulty_level'] = self._decrease_difficulty(chapter.difficulty_level)
                    params['challenge_level'] = 'low'
        
        # Identify focus areas based on mistake patterns
        mistake_patterns = learning_context.get('mistake_patterns', [])
        focus_areas = []
        
        for mistake in mistake_patterns[:5]:  # Top 5 mistake categories
            focus_areas.append(mistake['mistake_category'])
        
        if not focus_areas:
            # Default focus areas for the chapter
            focus_areas = chapter.subtopics or [chapter.topic]
        
        params['focus_areas'] = focus_areas
        
        # Calculate question distribution
        total_questions = 5  # default
        if learning_context.get('vocabulary_gaps'):
            params['question_distribution']['vocabulary'] = max(1, total_questions // 3)
        if mistake_patterns:
            params['question_distribution']['grammar'] = max(1, total_questions // 3)
        
        params['question_distribution']['comprehension'] = max(1, 
            total_questions - sum(params['question_distribution'].values())
        )
        
        # Adjust estimated time based on learning velocity
        velocity = learning_context.get('learning_velocity', 'medium')
        if velocity == 'fast':
            params['estimated_time'] = 12
        elif velocity == 'slow':
            params['estimated_time'] = 20
        
        return params
    
    def _generate_ai_questions(self, chapter, learning_context, adaptive_params, num_questions, session_type):
        """
        Generate AI-powered questions using the adaptive parameters.
        """
        try:
            # Prepare context for AI
            ai_context = self._prepare_ai_context(chapter, learning_context, adaptive_params)
            
            prompt = f"""
            Generate {num_questions} adaptive English learning questions for a Telugu speaker.
            
            Chapter Information:
            - Title: {chapter.title}
            - Topic: {chapter.topic}
            - Subtopics: {chapter.subtopics}
            - Default Difficulty: {chapter.difficulty_level}
            
            Adaptive Parameters:
            - Adjusted Difficulty: {adaptive_params['difficulty_level']}
            - Focus Areas: {adaptive_params['focus_areas']}
            - Challenge Level: {adaptive_params['challenge_level']}
            - Question Distribution: {adaptive_params['question_distribution']}
            
            User Learning Context:
            - Previous Mistakes: {[m['mistake_category'] for m in learning_context.get('mistake_patterns', [])[:3]]}
            - Vocabulary Gaps: {[v['english_word'] for v in learning_context.get('vocabulary_gaps', [])[:5]]}
            - Learning Velocity: {learning_context.get('learning_velocity')}
            
            Session Type: {session_type}
            
            Instructions:
            1. Focus on the identified weak areas and mistake patterns
            2. Include vocabulary from the gaps list
            3. Adjust difficulty to match the adaptive level
            4. Provide clear Telugu hints and explanations
            5. Include diverse question types (multiple choice, fill blanks, translation)
            
            Return in JSON format:
            {{
                "questions": [
                    {{
                        "id": "adaptive_q_1",
                        "type": "multiple_choice",
                        "question_text": "Choose the correct English translation for 'నేను పాఠశాలకు వెళ్తాను'",
                        "question_telugu": "సరైన ఇంగ్లీష్ అనువాదం ఎంచుకోండి",
                        "options": ["I go to school", "I went to school", "I will go to school", "I am going to school"],
                        "correct_answer": "I go to school",
                        "explanation": "Present tense is used for habitual actions. Telugu: ప్రస్తుత కాలం అలవాటు చర్యలకు ఉపయోగించబడుతుంది.",
                        "difficulty": "{adaptive_params['difficulty_level']}",
                        "skill_tested": "grammar",
                        "focus_area": "verb_tenses",
                        "telugu_hint": "ప్రస్తుత కాల వాక్యం",
                        "adaptive_reasoning": "Targeting user's grammar weakness in verb tenses"
                    }}
                ]
            }}
            """
            
            response = self.activity_service.model.generate_content(prompt)
            questions_data = self.activity_service._extract_json_from_response(response.text)
            
            questions = questions_data.get('questions', [])
            
            # Enhance questions with adaptive metadata
            for question in questions:
                question['adaptive_metadata'] = {
                    'generated_for_user': learning_context['user_id'],
                    'based_on_performance': learning_context.get('current_chapter_progress', {}),
                    'addresses_weaknesses': adaptive_params['focus_areas'],
                    'difficulty_adjustment': adaptive_params['difficulty_level'],
                    'generation_timestamp': datetime.utcnow().isoformat()
                }
            
            return questions
            
        except Exception as e:
            # Return fallback questions if AI generation fails
            return self._generate_fallback_questions(chapter, num_questions, adaptive_params)
    
    def _prepare_ai_context(self, chapter, learning_context, adaptive_params):
        """
        Prepare comprehensive context for AI question generation.
        """
        return {
            'chapter_content': {
                'topic': chapter.topic,
                'subtopics': chapter.subtopics,
                'difficulty': chapter.difficulty_level,
                'content': chapter.content
            },
            'user_performance': learning_context.get('current_chapter_progress', {}),
            'learning_patterns': {
                'mistakes': learning_context.get('mistake_patterns', []),
                'vocabulary_gaps': learning_context.get('vocabulary_gaps', []),
                'previous_performance': learning_context.get('previous_chapters_performance', [])
            },
            'adaptive_settings': adaptive_params
        }
    
    def _calculate_learning_velocity(self, user_id):
        """
        Calculate user's learning velocity based on recent activity.
        """
        try:
            # Get recent practice sessions
            recent_sessions = PracticeSession.query.filter_by(
                user_id=user_id, is_completed=True
            ).filter(
                PracticeSession.start_time >= datetime.utcnow() - timedelta(days=7)
            ).all()
            
            if not recent_sessions:
                return 'medium'
            
            # Calculate average time per question
            total_time = sum(s.duration_minutes for s in recent_sessions)
            total_questions = sum(s.total_questions for s in recent_sessions)
            
            if total_questions == 0:
                return 'medium'
            
            avg_time_per_question = total_time / total_questions
            
            # Classify velocity
            if avg_time_per_question < 1.5:  # Less than 1.5 minutes per question
                return 'fast'
            elif avg_time_per_question > 3.0:  # More than 3 minutes per question
                return 'slow'
            else:
                return 'medium'
                
        except Exception:
            return 'medium'
    
    def _identify_preferred_question_types(self, user_id):
        """
        Identify user's preferred question types based on performance.
        """
        try:
            # This would analyze recent sessions to find question types where user performs better
            # For now, return default preferences
            return ['multiple_choice', 'translation', 'vocabulary']
        except Exception:
            return ['multiple_choice']
    
    def _increase_difficulty(self, current_difficulty):
        """
        Increase difficulty level appropriately.
        """
        difficulty_map = {
            'beginner': 'intermediate',
            'intermediate': 'advanced',
            'advanced': 'advanced'  # Stay at advanced
        }
        return difficulty_map.get(current_difficulty, current_difficulty)
    
    def _decrease_difficulty(self, current_difficulty):
        """
        Decrease difficulty level appropriately.
        """
        difficulty_map = {
            'advanced': 'intermediate',
            'intermediate': 'beginner',
            'beginner': 'beginner'  # Stay at beginner
        }
        return difficulty_map.get(current_difficulty, current_difficulty)
    
    def _generate_fallback_questions(self, chapter, num_questions, adaptive_params):
        """
        Generate fallback questions if AI generation fails.
        """
        fallback_questions = []
        
        for i in range(num_questions):
            question = {
                'id': f'fallback_adaptive_{i+1}',
                'type': 'multiple_choice',
                'question_text': f'Practice question {i+1} for {chapter.topic}',
                'question_telugu': f'{chapter.topic} కోసం అభ్యాస ప్రశ్న {i+1}',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct_answer': 'Option A',
                'explanation': f'This is a fallback question for {chapter.topic}',
                'difficulty': adaptive_params['difficulty_level'],
                'skill_tested': 'general',
                'focus_area': chapter.topic,
                'telugu_hint': 'ఈ ప్రశ్న అభ్యాసం కోసం',
                'adaptive_reasoning': 'Fallback question due to AI generation failure'
            }
            fallback_questions.append(question)
        
        return fallback_questions
    
    def analyze_practice_session(self, session_id):
        """
        Analyze completed practice session to update user learning profile.
        """
        try:
            session = PracticeSession.query.get(session_id)
            if not session or not session.is_completed:
                return None
            
            analysis = {
                'session_id': session_id,
                'performance_analysis': {},
                'learning_insights': {},
                'recommendations': {},
                'skill_progress': {}
            }
            
            # Analyze performance by skill type
            questions = session.questions_data or []
            responses = session.user_responses or []
            
            skill_performance = {}
            for question, response in zip(questions, responses):
                skill = question.get('skill_tested', 'general')
                if skill not in skill_performance:
                    skill_performance[skill] = {'correct': 0, 'total': 0}
                
                skill_performance[skill]['total'] += 1
                if response.get('is_correct'):
                    skill_performance[skill]['correct'] += 1
            
            # Calculate skill scores
            for skill, stats in skill_performance.items():
                score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                analysis['skill_progress'][skill] = {
                    'score_percentage': score,
                    'questions_answered': stats['total'],
                    'correct_answers': stats['correct'],
                    'needs_practice': score < 70
                }
            
            # Generate learning insights
            analysis['learning_insights'] = self._generate_learning_insights(session, skill_performance)
            
            # Generate recommendations for next practice
            analysis['recommendations'] = self._generate_practice_recommendations(session, analysis)
            
            return analysis
            
        except Exception as e:
            raise e
    
    def _generate_learning_insights(self, session, skill_performance):
        """
        Generate insights from practice session performance.
        """
        insights = {
            'strengths': [],
            'weaknesses': [],
            'improvement_areas': [],
            'learning_pattern': 'consistent'
        }
        
        # Identify strengths and weaknesses
        for skill, stats in skill_performance.items():
            score = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
            
            if score >= 80:
                insights['strengths'].append(skill)
            elif score < 60:
                insights['weaknesses'].append(skill)
            else:
                insights['improvement_areas'].append(skill)
        
        # Analyze learning pattern
        if session.score_percentage >= 85:
            insights['learning_pattern'] = 'excellent'
        elif session.score_percentage >= 70:
            insights['learning_pattern'] = 'good'
        elif session.score_percentage >= 50:
            insights['learning_pattern'] = 'improving'
        else:
            insights['learning_pattern'] = 'needs_support'
        
        return insights
    
    def _generate_practice_recommendations(self, session, analysis):
        """
        Generate personalized recommendations for next practice session.
        """
        recommendations = {
            'focus_areas': [],
            'suggested_question_types': [],
            'difficulty_adjustment': 'maintain',
            'practice_frequency': 'daily',
            'specific_actions': []
        }
        
        # Focus on weak areas
        weak_skills = [skill for skill, data in analysis['skill_progress'].items() 
                      if data['score_percentage'] < 70]
        recommendations['focus_areas'] = weak_skills
        
        # Adjust difficulty based on performance
        if session.score_percentage >= 90:
            recommendations['difficulty_adjustment'] = 'increase'
        elif session.score_percentage < 60:
            recommendations['difficulty_adjustment'] = 'decrease'
        
        # Suggest specific actions
        insights = analysis['learning_insights']
        if 'vocabulary' in insights['weaknesses']:
            recommendations['specific_actions'].append('Practice vocabulary flashcards')
        if 'grammar' in insights['weaknesses']:
            recommendations['specific_actions'].append('Review grammar rules')
        
        return recommendations