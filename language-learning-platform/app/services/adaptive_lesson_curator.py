import json
from typing import Dict, List, Optional
from datetime import datetime
from app.models import db, User, Profile, LearningPath, Activity, UserActivityLog, LessonReview
from app.services.activity_generator_service import ActivityGeneratorService
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class AdaptiveLessonCurator:
    """
    AI-powered service that intelligently selects and curates the next lesson
    based on user performance, learning history, mastery progress, and AI reviews.
    Ensures optimal learning progression toward English mastery.
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.activity_service = ActivityGeneratorService()
        
        # Difficulty adjustment thresholds
        self.EXCELLENT_SCORE = 90
        self.GOOD_SCORE = 75
        self.STRUGGLING_SCORE = 50
        
    def curate_next_lesson(
        self,
        user_id: int,
        learning_path_id: Optional[int] = None,
        completed_activity_id: Optional[int] = None
    ) -> Dict:
        """
        Intelligently select and generate the next lesson for the user.
        
        Args:
            user_id: ID of the user
            learning_path_id: Optional ID of current learning path
            completed_activity_id: Optional ID of just-completed activity
            
        Returns:
            Dictionary containing next lesson details and reasoning
        """
        try:
            # Fetch user data
            user = User.query.get(user_id)
            profile = Profile.query.filter_by(user_id=user_id).first()
            
            if not user or not profile:
                return {'error': 'User or profile not found'}
            
            # Get user's learning history
            recent_activities = UserActivityLog.query.filter_by(
                user_id=user_id,
                completed=True
            ).order_by(UserActivityLog.completed_at.desc()).limit(20).all()
            
            # Get recent lesson reviews
            recent_reviews = LessonReview.query.filter_by(
                user_id=user_id
            ).order_by(LessonReview.created_at.desc()).limit(5).all()
            
            # Analyze performance patterns
            performance_analysis = self._analyze_performance_patterns(recent_activities, recent_reviews)
            
            # Get learning path context if applicable
            learning_path_context = {}
            if learning_path_id:
                learning_path = LearningPath.query.get(learning_path_id)
                if learning_path:
                    learning_path_context = {
                        'title': learning_path.title,
                        'difficulty_level': learning_path.difficulty_level,
                        'path_data': learning_path.path_data or {}
                    }
            
            # Build AI prompt for lesson curation
            curation_prompt = f"""
            You are an expert adaptive learning system curator for English language learning.
            
            **Student Profile:**
            - Proficiency Level: {profile.proficiency_level}
            - Native Language: Telugu
            - Current Mastery Metrics: {json.dumps(profile.mastery_metrics or {})}
            - Learning Phase: {user.current_learning_phase}
            
            **Performance Analysis:**
            {json.dumps(performance_analysis, indent=2)}
            
            **Recent Review Highlights:**
            {self._summarize_recent_reviews(recent_reviews)}
            
            **Learning Path Context:**
            {json.dumps(learning_path_context, indent=2) if learning_path_context else "No active learning path"}
            
            **Task:**
            Based on the student's performance, mastery levels, and recent feedback, determine the OPTIMAL next lesson.
            
            **Considerations:**
            1. **Skill Gap Priority**: Focus on weakest skills first, but maintain engagement
            2. **Progressive Difficulty**: Adjust difficulty based on recent performance
            3. **Spaced Repetition**: Revisit challenging topics after appropriate intervals
            4. **Variety**: Mix different activity types to maintain engagement
            5. **Motivation**: Ensure the next lesson is achievable but challenging
            6. **Cultural Relevance**: Use Telugu-English contexts when helpful
            
            **Decision Rules:**
            - If recent performance < 50%: Provide remedial content, same or lower difficulty
            - If recent performance 50-75%: Reinforce current level, provide practice
            - If recent performance 75-90%: Progress to next topic, maintain difficulty
            - If recent performance > 90%: Increase difficulty or introduce advanced concepts
            - If skill mastery < 60%: Focus on that skill area
            - If all skills > 85%: Introduce challenging integrated activities
            
            Return your response in the following JSON format:
            ```json
            {{
                "next_lesson": {{
                    "activity_type": "vocabulary/grammar/reading/writing/quiz/flashcard/conversation",
                    "difficulty_level": "beginner/intermediate/advanced",
                    "primary_skill_focus": "vocabulary/grammar/reading/writing/listening/speaking",
                    "secondary_skills": ["skill1", "skill2"],
                    "topic": "Specific topic/theme for the lesson",
                    "estimated_duration_minutes": 15,
                    "learning_objectives": [
                        "Objective 1",
                        "Objective 2",
                        "Objective 3"
                    ]
                }},
                "lesson_content_requirements": {{
                    "vocabulary_count": 10,
                    "difficulty_keywords": ["simple", "common", "everyday"],
                    "context_theme": "daily life/business/travel/academic",
                    "include_telugu_support": true,
                    "question_count": 10,
                    "time_limit_seconds": 300
                }},
                "reasoning": {{
                    "english": "Why this lesson is recommended (2-3 sentences)",
                    "telugu": "Same reasoning in Telugu"
                }},
                "pedagogical_strategy": "Review and reinforce/Progressive advancement/Challenge and excel/Remedial support",
                "expected_outcomes": [
                    "What student should achieve from this lesson"
                ],
                "connection_to_mastery": "How this lesson contributes to overall English mastery"
            }}
            ```
            """
            
            # Generate lesson plan using AI
            response = self.model.generate_content(curation_prompt)
            lesson_plan = self._extract_json_from_response(response.text)
            
            # Generate the actual activity content
            next_lesson = lesson_plan.get('next_lesson', {})
            content_requirements = lesson_plan.get('lesson_content_requirements', {})
            
            # Create/fetch the activity
            activity = self._generate_activity_content(
                user_id,
                next_lesson,
                content_requirements
            )
            
            return {
                'success': True,
                'lesson_plan': lesson_plan,
                'activity': activity,
                'performance_context': performance_analysis,
                'message': 'Next lesson curated successfully',
                'telugu_message': 'తదుపరి పాఠం విజయవంతంగా తయారు చేయబడింది'
            }
            
        except Exception as e:
            print(f"Error curating next lesson: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to curate next lesson: {str(e)}'}
    
    def _analyze_performance_patterns(
        self,
        recent_activities: List[UserActivityLog],
        recent_reviews: List[LessonReview]
    ) -> Dict:
        """Analyze user's recent performance to identify patterns"""
        if not recent_activities:
            return {
                'average_score': 0,
                'trend': 'no_data',
                'struggling_areas': [],
                'strong_areas': [],
                'consistency': 'unknown'
            }
        
        scores = [log.score for log in recent_activities if log.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Identify trend
        if len(scores) >= 3:
            recent_avg = sum(scores[:3]) / 3
            older_avg = sum(scores[3:6]) / len(scores[3:6]) if len(scores) > 3 else recent_avg
            trend = 'improving' if recent_avg > older_avg + 5 else 'declining' if recent_avg < older_avg - 5 else 'stable'
        else:
            trend = 'insufficient_data'
        
        # Aggregate struggling and strong areas from reviews
        struggling_areas = []
        strong_areas = []
        
        for review in recent_reviews:
            if review.weaknesses:
                struggling_areas.extend(review.weaknesses)
            if review.strengths:
                strong_areas.extend(review.strengths)
        
        # Determine consistency
        if len(scores) >= 5:
            score_variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
            consistency = 'high' if score_variance < 100 else 'medium' if score_variance < 400 else 'low'
        else:
            consistency = 'unknown'
        
        return {
            'average_score': round(avg_score, 2),
            'recent_scores': scores[:5],
            'trend': trend,
            'struggling_areas': struggling_areas[:3],
            'strong_areas': strong_areas[:3],
            'consistency': consistency,
            'total_activities': len(recent_activities)
        }
    
    def _summarize_recent_reviews(self, reviews: List[LessonReview]) -> str:
        """Create a summary of recent lesson reviews"""
        if not reviews:
            return "No recent reviews available"
        
        summary_parts = []
        for i, review in enumerate(reviews[:3], 1):
            summary_parts.append(
                f"Review {i}: Score {review.performance_score}%, "
                f"Focus areas: {', '.join(review.focus_areas or [])}, "
                f"Adjustment: {review.difficulty_adjustment}"
            )
        
        return "\n".join(summary_parts)
    
    def _generate_activity_content(
        self,
        user_id: int,
        lesson_plan: Dict,
        content_requirements: Dict
    ) -> Dict:
        """Generate or fetch appropriate activity content"""
        try:
            activity_type = lesson_plan.get('activity_type', 'quiz')
            difficulty = lesson_plan.get('difficulty_level', 'intermediate')
            topic = lesson_plan.get('topic', 'General English')
            
            # Use activity generator service to create the content
            activity_data = self.activity_service.generate_activity(
                activity_type=activity_type,
                difficulty_level=difficulty,
                topic=topic,
                options={
                    'count': content_requirements.get('question_count', 10),
                    'time_limit': content_requirements.get('time_limit_seconds', 300),
                    'include_telugu': content_requirements.get('include_telugu_support', True)
                }
            )
            
            return activity_data
            
        except Exception as e:
            print(f"Error generating activity content: {str(e)}")
            return {
                'error': 'Failed to generate activity content',
                'fallback': True
            }
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from AI response text"""
        try:
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from response: {response_text[:200]}")
            return {}
