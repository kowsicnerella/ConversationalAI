"""
Adaptive Difficulty Engine - Phase 3 Implementation
Real-time difficulty adjustment based on user performance
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import and_, func, desc
import statistics

from app.models.activity import Activity, UserActivityLog
from app.models.learning_node import (
    UserLearningNodeProgress, UserSkillProfile
)
from app.models.personalization import VocabularyWord
from app import db


class AdaptiveDifficultyEngine:
    """
    Real-time difficulty adjustment based on performance.
    Maintains an optimal challenge zone for each user.
    """

    def __init__(self):
        """Initialize the adaptive difficulty engine"""
        self.TARGET_ACCURACY = 0.75  # 75% is optimal learning zone
        self.DIFFICULTY_STEP = 0.10  # 10% adjustment per step
        self.MIN_DIFFICULTY = 0.10
        self.MAX_DIFFICULTY = 0.95

    def calculate_user_skill_level(
        self,
        user_id: int,
        skill_domain: str = None
    ) -> float:
        """
        Calculate precise skill level (0-100 scale).
        Not just beginner/intermediate/advanced.

        Args:
            user_id: User ID
            skill_domain: Optional specific skill (listening, speaking, etc.)

        Returns:
            Skill level 0-100
        """
        try:
            if skill_domain:
                # Get specific skill level
                skill_profile = UserSkillProfile.query.filter_by(user_id=user_id).first()
                if not skill_profile:
                    return 0

                skill_map = {
                    'listening': skill_profile.listening_level,
                    'speaking': skill_profile.speaking_level,
                    'reading': skill_profile.reading_level,
                    'writing': skill_profile.writing_level,
                    'vocabulary': skill_profile.vocabulary_level,
                    'grammar': skill_profile.grammar_level
                }

                return skill_map.get(skill_domain, 0)

            else:
                # Get overall skill level
                skill_profile = UserSkillProfile.query.filter_by(user_id=user_id).first()
                return skill_profile.overall_level if skill_profile else 0

        except Exception as e:
            print(f"Error calculating skill level: {str(e)}")
            return 0

    def adjust_activity_difficulty(
        self,
        user_id: int,
        activity_id: int,
        current_difficulty: float,
        performance_score: float,
        response_time_seconds: float = 0,
        error_patterns: List[str] = None
    ) -> float:
        """
        Dynamic difficulty adjustment algorithm.

        Rules:
        - If user scores > 85% → increase difficulty
        - If user scores < 60% → decrease difficulty
        - Consider response time and error patterns
        - Maintain challenge zone (70-80% accuracy)

        Args:
            user_id: User ID
            activity_id: Activity ID
            current_difficulty: Current difficulty (0-1)
            performance_score: User performance (0-1)
            response_time_seconds: Time taken (optional)
            error_patterns: Types of errors made (optional)

        Returns:
            Adjusted difficulty (0-1)
        """
        try:
            adjustment = 0.0

            # Primary adjustment based on accuracy
            if performance_score > 0.85:
                # Excellent performance - increase difficulty
                adjustment = self.DIFFICULTY_STEP
            elif performance_score < 0.60:
                # Poor performance - decrease difficulty
                adjustment = -self.DIFFICULTY_STEP
            elif performance_score > 0.80:
                # Good performance - slight increase
                adjustment = self.DIFFICULTY_STEP * 0.5
            elif performance_score < 0.70:
                # Below target - slight decrease
                adjustment = -self.DIFFICULTY_STEP * 0.5

            # Secondary adjustment based on response time
            if response_time_seconds > 0:
                ideal_time_per_question = 45  # seconds
                avg_time = response_time_seconds
                
                if avg_time < ideal_time_per_question * 0.5 and performance_score > 0.80:
                    # Too fast and too easy - increase difficulty more
                    adjustment += self.DIFFICULTY_STEP * 0.3
                elif avg_time > ideal_time_per_question * 2 and performance_score < 0.70:
                    # Too slow and struggling - increase reduction
                    adjustment -= self.DIFFICULTY_STEP * 0.3

            # Tertiary adjustment based on error patterns
            if error_patterns:
                if len(error_patterns) > 3:
                    # Many repeated errors - decrease difficulty to solidify basics
                    adjustment -= self.DIFFICULTY_STEP * 0.2

            # Apply adjustment and clamp to bounds
            new_difficulty = current_difficulty + adjustment
            new_difficulty = max(self.MIN_DIFFICULTY, min(new_difficulty, self.MAX_DIFFICULTY))

            return new_difficulty

        except Exception as e:
            print(f"Error adjusting difficulty: {str(e)}")
            return current_difficulty

    def generate_challenge_curve(
        self,
        user_id: int,
        session_id: str,
        session_duration_minutes: int = 30
    ) -> List[Dict]:
        """
        Create a difficulty progression for a learning session.
        
        Structure:
        - Start: Easy (0.3-0.4) - warm up
        - Middle: Moderate-Hard (0.5-0.7) - main learning
        - End: Medium (0.4-0.5) - cool down
        
        Args:
            user_id: User ID
            session_id: Session identifier
            session_duration_minutes: Total session time

        Returns:
            List of difficulty levels for each activity in session
        """
        try:
            challenge_curve = []

            # Divide session into 3 phases
            total_activities = max(3, session_duration_minutes // 10)  # ~10 min per activity

            warmup_activities = max(1, total_activities // 4)
            main_activities = total_activities - warmup_activities - 1
            cooldown_activities = 1

            # Phase 1: Warm-up (easy)
            for i in range(warmup_activities):
                progress = i / warmup_activities if warmup_activities > 0 else 0
                difficulty = 0.30 + (progress * 0.10)  # 0.30-0.40
                challenge_curve.append({
                    'activity_number': len(challenge_curve) + 1,
                    'phase': 'warmup',
                    'difficulty': difficulty,
                    'target_accuracy': 0.85,
                    'description': 'Warm-up activity to ease into learning'
                })

            # Phase 2: Main learning (moderate to challenging)
            user_skill = self.calculate_user_skill_level(user_id)
            base_difficulty = 0.35 + (user_skill / 100 * 0.40)  # Scale by user skill

            for i in range(main_activities):
                progress = i / main_activities if main_activities > 0 else 0
                # Create an increasing difficulty curve
                difficulty = base_difficulty + (progress * 0.30)
                difficulty = min(difficulty, 0.90)

                challenge_curve.append({
                    'activity_number': len(challenge_curve) + 1,
                    'phase': 'main',
                    'difficulty': difficulty,
                    'target_accuracy': 0.75,
                    'description': f'Main learning activity {i+1} - increasing challenge'
                })

            # Phase 3: Cool-down (moderate)
            cooldown_difficulty = 0.50
            challenge_curve.append({
                'activity_number': len(challenge_curve) + 1,
                'phase': 'cooldown',
                'difficulty': cooldown_difficulty,
                'target_accuracy': 0.80,
                'description': 'Cool-down activity to consolidate learning'
            })

            return challenge_curve

        except Exception as e:
            print(f"Error generating challenge curve: {str(e)}")
            return []

    def estimate_skill_trajectory(
        self,
        user_id: int,
        skill_domain: str,
        days_lookback: int = 30
    ) -> Dict:
        """
        Analyze skill improvement trajectory over time.

        Args:
            user_id: User ID
            skill_domain: Skill to analyze
            days_lookback: Days to look back in history

        Returns:
            Dictionary with trajectory analysis
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_lookback)

            # Get activities for this skill
            activities = db.session.query(UserActivityLog).filter(
                and_(
                    UserActivityLog.user_id == user_id,
                    UserActivityLog.skill_area == skill_domain,
                    UserActivityLog.completed_at >= cutoff_date,
                    UserActivityLog.is_completed == True
                )
            ).order_by(UserActivityLog.completed_at).all()

            if len(activities) < 3:
                return {
                    'sample_size': len(activities),
                    'trend': 'insufficient_data',
                    'current_level': 0,
                    'improvement_rate': 0
                }

            scores = [log.accuracy_score for log in activities if log.accuracy_score]

            if not scores:
                return {
                    'sample_size': len(activities),
                    'trend': 'no_data',
                    'current_level': 0,
                    'improvement_rate': 0
                }

            # Calculate trend
            current_level = scores[-1]  # Most recent
            initial_level = scores[0]  # Oldest

            improvement_rate = (current_level - initial_level) / days_lookback
            average_level = statistics.mean(scores)
            median_level = statistics.median(scores)

            # Determine trend
            if len(scores) > 5:
                recent_avg = statistics.mean(scores[-5:])
                older_avg = statistics.mean(scores[:-5])
                if recent_avg > older_avg + 0.05:
                    trend = 'improving'
                elif recent_avg < older_avg - 0.05:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'unknown'

            return {
                'skill': skill_domain,
                'sample_size': len(activities),
                'current_level': current_level,
                'initial_level': initial_level,
                'average_level': average_level,
                'median_level': median_level,
                'improvement_rate': improvement_rate,
                'trend': trend,
                'estimated_days_to_mastery': max(0, (1.0 - current_level) / improvement_rate) if improvement_rate > 0 else float('inf')
            }

        except Exception as e:
            print(f"Error estimating trajectory: {str(e)}")
            return {'error': str(e)}

    def recommend_difficulty_adjustment(
        self,
        user_id: int,
        current_activity_id: int,
        recent_performance: List[float]
    ) -> Dict:
        """
        Make a recommendation for difficulty adjustment based on recent performance.

        Args:
            user_id: User ID
            current_activity_id: Current activity ID
            recent_performance: List of recent performance scores (0-1)

        Returns:
            Recommendation dictionary
        """
        try:
            if not recent_performance or len(recent_performance) < 2:
                return {'recommendation': 'continue', 'reason': 'Insufficient data'}

            avg_performance = sum(recent_performance) / len(recent_performance)
            latest_performance = recent_performance[-1]

            activity = Activity.query.get(current_activity_id)

            current_difficulty = activity.difficulty_level if isinstance(activity.difficulty_level, (int, float)) else 0.5

            if avg_performance > 0.85:
                new_difficulty = self.adjust_activity_difficulty(
                    user_id, current_activity_id, current_difficulty, avg_performance
                )
                return {
                    'recommendation': 'increase',
                    'reason': 'Excellent performance - ready for more challenge',
                    'current_difficulty': current_difficulty,
                    'suggested_difficulty': new_difficulty,
                    'confidence': 0.95
                }

            elif avg_performance < 0.60:
                new_difficulty = self.adjust_activity_difficulty(
                    user_id, current_activity_id, current_difficulty, avg_performance
                )
                return {
                    'recommendation': 'decrease',
                    'reason': 'Struggling with current difficulty',
                    'current_difficulty': current_difficulty,
                    'suggested_difficulty': new_difficulty,
                    'confidence': 0.90
                }

            elif latest_performance < avg_performance - 0.15:
                return {
                    'recommendation': 'repeat',
                    'reason': 'Recent decline in performance - consolidate',
                    'current_difficulty': current_difficulty,
                    'suggested_difficulty': current_difficulty,
                    'confidence': 0.75
                }

            else:
                return {
                    'recommendation': 'continue',
                    'reason': 'Performance optimal - maintain current difficulty',
                    'current_difficulty': current_difficulty,
                    'confidence': 0.85
                }

        except Exception as e:
            print(f"Error recommending adjustment: {str(e)}")
            return {'error': str(e)}
