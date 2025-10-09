import json
from typing import Dict, List, Optional
from datetime import datetime
from app.models import db, UserActivityLog, LessonReview, User, Profile
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class LessonReviewService:
    """
    AI-powered service that analyzes user performance on completed lessons/activities
    and provides comprehensive feedback, identifies strengths/weaknesses, and 
    suggests next steps for optimal learning progression.
    """
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Performance thresholds
        self.EXCELLENT_THRESHOLD = 90
        self.GOOD_THRESHOLD = 75
        self.SATISFACTORY_THRESHOLD = 60
        self.NEEDS_IMPROVEMENT_THRESHOLD = 50
        
    def generate_lesson_review(
        self, 
        user_id: int, 
        activity_log_id: int,
        learning_path_id: Optional[int] = None
    ) -> Dict:
        """
        Generate a comprehensive AI-powered review for a completed lesson/activity.
        
        Args:
            user_id: ID of the user
            activity_log_id: ID of the completed activity log
            learning_path_id: Optional ID of the learning path
            
        Returns:
            Dictionary containing review data and next lesson recommendation
        """
        try:
            # Fetch activity log
            activity_log = UserActivityLog.query.get(activity_log_id)
            if not activity_log or activity_log.user_id != user_id:
                return {'error': 'Activity log not found or access denied'}
            
            # Fetch user and profile
            user = User.query.get(user_id)
            profile = Profile.query.filter_by(user_id=user_id).first()
            
            if not user or not profile:
                return {'error': 'User or profile not found'}
            
            # Extract performance data
            score = activity_log.score or 0
            time_spent = activity_log.time_spent or 0
            attempts = activity_log.attempts or 1
            activity_type = activity_log.activity_type
            activity_data = activity_log.activity_data or {}
            
            # Get user's recent performance history (last 10 activities)
            recent_activities = UserActivityLog.query.filter_by(
                user_id=user_id,
                completed=True
            ).order_by(UserActivityLog.completed_at.desc()).limit(10).all()
            
            recent_scores = [log.score for log in recent_activities if log.score is not None]
            avg_recent_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            
            # Build AI prompt for review generation
            review_prompt = f"""
            You are an expert English language teacher providing personalized feedback to a Telugu speaker learning English.
            
            **Student Profile:**
            - Username: {user.username}
            - Proficiency Level: {profile.proficiency_level}
            - Native Language: Telugu
            - Target Language: English
            - Current Mastery Metrics: {json.dumps(profile.mastery_metrics or {})}
            
            **Activity Completed:**
            - Activity Type: {activity_type}
            - Score: {score}%
            - Time Spent: {time_spent} seconds
            - Attempts: {attempts}
            - Activity Details: {json.dumps(activity_data, indent=2)}
            
            **Performance Context:**
            - Recent Average Score: {avg_recent_score:.1f}%
            - Performance Trend: {"Improving" if score > avg_recent_score else "Declining" if score < avg_recent_score else "Stable"}
            
            **Task:**
            Generate a comprehensive, encouraging lesson review that includes:
            
            1. **Performance Analysis**: Detailed analysis of the student's performance
            2. **Strengths**: 2-3 specific things the student did well (be specific, reference actual answers/performance)
            3. **Areas for Improvement**: 2-3 specific areas that need work (constructive and actionable)
            4. **Feedback**: Encouraging, personalized feedback in both English and Telugu
            5. **Next Steps**: Specific recommendations for what to focus on next
            6. **Difficulty Adjustment**: Should difficulty increase, decrease, or stay the same?
            7. **Focus Areas**: Which specific skills need attention (vocabulary, grammar, reading, etc.)
            
            **Important Guidelines:**
            - Be encouraging and positive, even when pointing out areas for improvement
            - Provide specific, actionable advice
            - Reference cultural context when helpful for Telugu speakers
            - Use simple, clear language suitable for the student's proficiency level
            - Include motivational elements
            
            Return your response in the following JSON format:
            ```json
            {{
                "performance_score": {score},
                "performance_category": "excellent/good/satisfactory/needs_improvement",
                "strengths": [
                    "Specific strength 1",
                    "Specific strength 2",
                    "Specific strength 3"
                ],
                "weaknesses": [
                    "Area for improvement 1 (with specific advice)",
                    "Area for improvement 2 (with specific advice)"
                ],
                "feedback_english": "Detailed personalized feedback in English (3-4 sentences, encouraging tone)",
                "feedback_telugu": "Same feedback translated to Telugu",
                "next_lesson_recommendation": {{
                    "recommended_activity_type": "vocabulary/grammar/reading/quiz/flashcard",
                    "difficulty_level": "beginner/intermediate/advanced",
                    "topic_focus": "Specific topic to focus on",
                    "reasoning": "Why this is recommended",
                    "telugu_reasoning": "Reasoning in Telugu"
                }},
                "difficulty_adjustment": "increase/maintain/decrease",
                "focus_areas": ["vocabulary", "grammar", "reading"],
                "motivational_message": "Short encouraging message",
                "telugu_motivational_message": "Same message in Telugu",
                "estimated_time_to_mastery": "X weeks based on current pace"
            }}
            ```
            """
            
            # Generate review using AI
            response = self.model.generate_content(review_prompt)
            review_data = self._extract_json_from_response(response.text)
            
            # Create lesson review record
            lesson_review = LessonReview(
                user_id=user_id,
                activity_log_id=activity_log_id,
                learning_path_id=learning_path_id,
                performance_score=review_data.get('performance_score', score),
                strengths=review_data.get('strengths', []),
                weaknesses=review_data.get('weaknesses', []),
                feedback_english=review_data.get('feedback_english', ''),
                feedback_telugu=review_data.get('feedback_telugu', ''),
                next_lesson_recommendation=review_data.get('next_lesson_recommendation', {}),
                difficulty_adjustment=review_data.get('difficulty_adjustment', 'maintain'),
                focus_areas=review_data.get('focus_areas', []),
                ai_model_used='gemini-2.0-flash-exp'
            )
            
            db.session.add(lesson_review)
            db.session.commit()
            
            # Update mastery metrics based on performance
            self._update_mastery_metrics(user_id, activity_type, score, review_data.get('focus_areas', []))
            
            return {
                'success': True,
                'review': lesson_review.to_dict(),
                'motivational_message': review_data.get('motivational_message', ''),
                'telugu_motivational_message': review_data.get('telugu_motivational_message', ''),
                'estimated_time_to_mastery': review_data.get('estimated_time_to_mastery', '')
            }
            
        except Exception as e:
            print(f"Error generating lesson review: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': f'Failed to generate lesson review: {str(e)}'}
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON from AI response text"""
        try:
            # Try to find JSON in code blocks
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
    
    def _update_mastery_metrics(
        self, 
        user_id: int, 
        activity_type: str, 
        score: float,
        focus_areas: List[str]
    ):
        """Update user's mastery metrics based on activity performance"""
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                return
            
            mastery_metrics = profile.mastery_metrics or {
                'vocabulary': 0, 'grammar': 0, 'reading': 0,
                'writing': 0, 'listening': 0, 'speaking': 0, 'overall': 0
            }
            
            # Map activity types to skill areas
            activity_skill_map = {
                'vocabulary': 'vocabulary',
                'flashcard': 'vocabulary',
                'quiz': 'grammar',
                'grammar': 'grammar',
                'reading': 'reading',
                'writing': 'writing',
                'listening': 'listening',
                'speaking': 'speaking',
                'conversation': 'speaking'
            }
            
            skill_area = activity_skill_map.get(activity_type.lower(), 'overall')
            
            # Weighted update: 80% existing, 20% new score
            if skill_area in mastery_metrics:
                current_mastery = mastery_metrics[skill_area]
                new_mastery = (current_mastery * 0.8) + (score * 0.2)
                mastery_metrics[skill_area] = round(new_mastery, 2)
            
            # Update overall mastery (average of all skills)
            skill_values = [v for k, v in mastery_metrics.items() if k != 'overall']
            mastery_metrics['overall'] = round(sum(skill_values) / len(skill_values), 2) if skill_values else 0
            
            profile.mastery_metrics = mastery_metrics
            db.session.commit()
            
        except Exception as e:
            print(f"Error updating mastery metrics: {str(e)}")
    
    def get_lesson_review(self, review_id: int, user_id: int) -> Optional[Dict]:
        """Retrieve a specific lesson review"""
        review = LessonReview.query.get(review_id)
        if review and review.user_id == user_id:
            return review.to_dict()
        return None
    
    def get_user_reviews(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent lesson reviews for a user"""
        reviews = LessonReview.query.filter_by(user_id=user_id)\
            .order_by(LessonReview.created_at.desc())\
            .limit(limit)\
            .all()
        return [review.to_dict() for review in reviews]
