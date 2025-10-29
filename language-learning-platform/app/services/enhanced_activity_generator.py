"""
Enhanced Activity Generator Service - Phase 2
Adds comprehensive personalization, weak-area detection, vocabulary integration,
and dynamic difficulty adjustment.
"""

import json
from datetime import datetime, timedelta
from app.models.user import User, Profile, db
from app.models.activity import UserActivityLog, Activity
from app.models.curriculum import LearningNode
from app.services.llm_config import LLMConfig
from sqlalchemy import and_, func


class EnhancedActivityGenerator:
    """
    Phase 2 Enhanced Activity Generator with:
    - User context awareness
    - Weak area identification
    - Vocabulary integration
    - Dynamic difficulty calculation
    - Performance-based personalization
    """

    def __init__(self):
        self.llm = LLMConfig()

    def generate_personalized_activity(self, user_id, activity_type=None, focus_skill=None):
        """
        Generate a fully personalized activity with Phase 2 enhancements.
        
        Args:
            user_id: User ID
            activity_type: Optional specific type (quiz, flashcard, etc.)
            focus_skill: Optional skill to focus on (vocabulary, grammar, etc.)
        
        Returns:
            dict: Complete activity with personalized content
        """
        # Step 1: Get comprehensive user profile
        user_profile = self._get_user_profile(user_id)
        
        if not user_profile:
            return {"error": "User profile not found"}
        
        # Step 2: Analyze recent performance
        performance = self._analyze_recent_performance(user_id)
        
        # Step 3: Identify weak areas
        weak_areas = self._identify_weak_areas(user_id, performance)
        
        # Step 4: Get learned vocabulary
        vocabulary = self._get_learned_vocabulary(user_id)
        
        # Step 5: Calculate optimal difficulty
        difficulty = self._calculate_optimal_difficulty(user_profile, performance)
        
        # Step 6: Auto-determine activity type if not specified
        if not activity_type:
            activity_type = self._select_activity_type(weak_areas, performance)
        
        # Step 7: Auto-determine focus skill if not specified
        if not focus_skill:
            focus_skill = weak_areas[0]['skill'] if weak_areas else 'vocabulary'
        
        # Step 8: Build personalized prompt
        prompt = self._build_personalized_prompt(
            user_profile=user_profile,
            activity_type=activity_type,
            focus_skill=focus_skill,
            difficulty=difficulty,
            weak_areas=weak_areas,
            vocabulary=vocabulary,
            performance=performance
        )
        
        # Step 9: Generate with AI
        activity_content = self._generate_with_ai(prompt, activity_type)
        
        # Step 10: Add metadata
        activity_content['metadata'] = {
            'generated_at': datetime.utcnow().isoformat(),
            'personalization_level': 'high',
            'difficulty': difficulty,
            'focus_skill': focus_skill,
            'weak_areas_targeted': [wa['skill'] for wa in weak_areas[:3]],
            'vocabulary_count': len(vocabulary),
            'user_level': user_profile['proficiency_level']
        }
        
        return activity_content

    def _get_user_profile(self, user_id):
        """
        Get comprehensive user profile including all relevant learning data.
        """
        user = User.query.get(user_id)
        if not user:
            return None
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None
        
        return {
            'user_id': user_id,
            'username': user.username,
            'proficiency_level': profile.proficiency_level or 'beginner',
            'native_language': profile.native_language or 'Telugu',
            'target_language': profile.target_language or 'English',
            'learning_goals': profile.learning_goals or [],
            'mastery_metrics': profile.mastery_metrics or {},
            'current_streak': profile.current_streak or 0,
            'total_activities': profile.total_activities_completed or 0,
            'avg_performance': profile.avg_performance_score or 0,
            'preferred_pace': getattr(profile, 'preferred_pace', 'medium'),
            'learning_style': getattr(profile, 'learning_style', 'mixed')
        }

    def _analyze_recent_performance(self, user_id, days=7):
        """
        Analyze user's performance over the last N days.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == user_id,
                UserActivityLog.completed_at >= cutoff_date,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        if not logs:
            return {
                'total_activities': 0,
                'avg_accuracy': 0,
                'avg_time': 0,
                'completion_rate': 0,
                'improvement_trend': 0
            }
        
        # Calculate metrics
        accuracies = [log.accuracy_score for log in logs if log.accuracy_score is not None]
        times = [log.time_spent_minutes for log in logs if log.time_spent_minutes]
        
        # Calculate improvement trend (first half vs second half)
        if len(accuracies) >= 4:
            mid = len(accuracies) // 2
            first_half = sum(accuracies[:mid]) / len(accuracies[:mid])
            second_half = sum(accuracies[mid:]) / len(accuracies[mid:])
            improvement = second_half - first_half
        else:
            improvement = 0
        
        return {
            'total_activities': len(logs),
            'avg_accuracy': round(sum(accuracies) / len(accuracies), 2) if accuracies else 0,
            'avg_time': round(sum(times) / len(times), 1) if times else 0,
            'completion_rate': 100,  # All queried logs are completed
            'improvement_trend': round(improvement, 2),
            'recent_scores': accuracies[-5:] if accuracies else []
        }

    def _identify_weak_areas(self, user_id, performance=None):
        """
        Identify weak areas based on skill-specific performance.
        """
        # Get recent logs grouped by skill area
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        logs = UserActivityLog.query.filter(
            and_(
                UserActivityLog.user_id == user_id,
                UserActivityLog.completed_at >= thirty_days_ago,
                UserActivityLog.is_completed == True
            )
        ).all()
        
        # Group by skill area
        skill_performance = {}
        for log in logs:
            if log.skill_area and log.accuracy_score is not None:
                if log.skill_area not in skill_performance:
                    skill_performance[log.skill_area] = []
                skill_performance[log.skill_area].append(log.accuracy_score)
        
        # Calculate averages and identify weak areas
        weak_areas = []
        for skill, scores in skill_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 70:  # Threshold for weak area
                priority = 'high' if avg_score < 50 else 'medium' if avg_score < 60 else 'low'
                weak_areas.append({
                    'skill': skill,
                    'score': round(avg_score, 1),
                    'priority': priority,
                    'sample_count': len(scores)
                })
        
        # Sort by score (lowest first)
        weak_areas.sort(key=lambda x: x['score'])
        
        return weak_areas

    def _get_learned_vocabulary(self, user_id, limit=50):
        """
        Get vocabulary words the user has learned/encountered.
        Returns most recently learned words.
        """
        # Note: This assumes a VocabularyWord model exists
        # For now, return placeholder - implement when vocabulary tracking is complete
        return []

    def _calculate_optimal_difficulty(self, user_profile, performance):
        """
        Calculate optimal difficulty level (0.0-1.0 scale) based on:
        - User's proficiency level
        - Recent performance
        - Improvement trend
        """
        # Base difficulty from proficiency level
        level_difficulty = {
            'beginner': 0.3,
            'elementary': 0.4,
            'intermediate': 0.5,
            'upper_intermediate': 0.6,
            'advanced': 0.7,
            'proficient': 0.8
        }
        
        base_difficulty = level_difficulty.get(user_profile['proficiency_level'], 0.4)
        
        # Adjust based on recent performance
        if performance['avg_accuracy'] > 0:
            if performance['avg_accuracy'] >= 85:
                base_difficulty += 0.1  # Increase difficulty
            elif performance['avg_accuracy'] < 60:
                base_difficulty -= 0.1  # Decrease difficulty
        
        # Adjust based on improvement trend
        if performance['improvement_trend'] > 10:
            base_difficulty += 0.05  # Doing well, increase slightly
        elif performance['improvement_trend'] < -10:
            base_difficulty -= 0.05  # Struggling, decrease slightly
        
        # Clamp between 0.1 and 0.9
        return max(0.1, min(0.9, base_difficulty))

    def _select_activity_type(self, weak_areas, performance):
        """
        Select optimal activity type based on weak areas and performance.
        """
        # Map skills to activity types
        skill_to_activity = {
            'vocabulary': 'flashcard',
            'grammar': 'quiz',
            'reading': 'reading',
            'writing': 'writing',
            'listening': 'listening',
            'speaking': 'role_play'
        }
        
        # Prioritize weakest area
        if weak_areas:
            weakest = weak_areas[0]['skill']
            return skill_to_activity.get(weakest, 'quiz')
        
        # If no weak areas, vary based on performance
        if performance['total_activities'] % 3 == 0:
            return 'quiz'
        elif performance['total_activities'] % 3 == 1:
            return 'flashcard'
        else:
            return 'reading'

    def _build_personalized_prompt(self, user_profile, activity_type, focus_skill,
                                   difficulty, weak_areas, vocabulary, performance):
        """
        Build a comprehensive AI prompt with all personalization context.
        """
        difficulty_desc = {
            0.1: 'very easy', 0.2: 'very easy', 0.3: 'easy',
            0.4: 'moderate', 0.5: 'moderate', 0.6: 'moderate',
            0.7: 'challenging', 0.8: 'challenging', 0.9: 'very challenging'
        }
        
        diff_level = difficulty_desc.get(round(difficulty, 1), 'moderate')
        
        prompt = f"""Generate a personalized English learning activity.

USER PROFILE:
- Level: {user_profile['proficiency_level']}
- Native Language: {user_profile['native_language']}
- Learning Goals: {', '.join(user_profile['learning_goals'][:3]) if user_profile['learning_goals'] else 'General English improvement'}
- Current Streak: {user_profile['current_streak']} days
- Total Activities Completed: {user_profile['total_activities']}

RECENT PERFORMANCE:
- Average Accuracy: {performance['avg_accuracy']}%
- Activities (Last 7 days): {performance['total_activities']}
- Improvement Trend: {'↑ Improving' if performance['improvement_trend'] > 0 else '↓ Needs support' if performance['improvement_trend'] < 0 else '→ Stable'}

WEAK AREAS TO TARGET:
{chr(10).join([f"- {wa['skill']}: {wa['score']}% ({wa['priority']} priority)" for wa in weak_areas[:3]]) if weak_areas else '- None identified - well-rounded learner!'}

ACTIVITY REQUIREMENTS:
- Type: {activity_type}
- Focus Skill: {focus_skill}
- Difficulty: {diff_level} ({difficulty:.1f}/1.0)
- Duration: 5-10 minutes
- Include {user_profile['native_language']} translations for key terms

PERSONALIZATION INSTRUCTIONS:
1. Address weak areas: {', '.join([wa['skill'] for wa in weak_areas[:2]]) if weak_areas else 'maintain balanced practice'}
2. Match user's {user_profile['proficiency_level']} level
3. Use engaging, culturally-relevant examples
4. Provide clear instructions in English with {user_profile['native_language']} support
5. Design difficulty to be {diff_level} but achievable
6. Encourage the {user_profile['current_streak']}-day streak

Generate a {activity_type} activity as JSON:"""

        # Add activity-specific schema
        if activity_type == 'quiz':
            prompt += """
{
  "activity_type": "quiz",
  "title": "Engaging title",
  "description": "Clear description",
  "instructions": "Instructions in English",
  "instructions_native": "Instructions in native language",
  "estimated_time": 7,
  "questions": [
    {
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "explanation": "Why this is correct",
      "difficulty": "moderate"
    }
  ]
}"""
        elif activity_type == 'flashcard':
            prompt += """
{
  "activity_type": "flashcard",
  "title": "Engaging title",
  "description": "Clear description",
  "cards": [
    {
      "front": "English term/phrase",
      "back": "Native language translation",
      "example": "Usage example",
      "pronunciation": "IPA or simplified"
    }
  ]
}"""
        else:
            prompt += """
{
  "activity_type": "general",
  "title": "Title",
  "description": "Description",
  "content": "Activity content"
}"""
        
        return prompt

    def _generate_with_ai(self, prompt, activity_type):
        """
        Generate activity content using AI.
        """
        try:
            response = self.llm.generate_content(prompt)
            
            # Clean and parse JSON
            cleaned = LLMConfig._clean_json_response(response)
            activity = json.loads(cleaned)
            
            return activity
        except Exception as e:
            print(f"Error generating activity: {str(e)}")
            return {
                "error": "Failed to generate activity",
                "activity_type": activity_type,
                "title": f"Sample {activity_type.title()} Activity",
                "description": "An error occurred during generation. Please try again."
            }
