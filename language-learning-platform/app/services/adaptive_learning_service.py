import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from app.models import User, Activity, UserActivityLog, LearningPath
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db


class AdaptiveLearningAlgorithm:
    """
    Intelligent adaptive learning algorithm that personalizes the learning experience
    based on user performance, learning patterns, and preferences.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
        
        # Learning algorithm parameters
        self.DIFFICULTY_ADJUSTMENT_THRESHOLD = 0.75  # 75% accuracy threshold
        self.MASTERY_THRESHOLD = 0.85  # 85% accuracy for mastery
        self.STRUGGLE_THRESHOLD = 0.5   # 50% accuracy indicates struggle
        self.MIN_ACTIVITIES_FOR_ASSESSMENT = 3
        self.PERFORMANCE_WINDOW_DAYS = 7
        
        # Difficulty progression weights
        self.DIFFICULTY_WEIGHTS = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.0,
            'expert': 2.5
        }
        
        # Activity type preferences and effectiveness
        self.ACTIVITY_TYPE_EFFECTIVENESS = {
            'quiz': {'retention': 0.8, 'engagement': 0.7, 'speed': 0.9},
            'flashcard': {'retention': 0.9, 'engagement': 0.6, 'speed': 0.8},
            'reading': {'retention': 0.7, 'engagement': 0.8, 'speed': 0.6},
            'writing': {'retention': 0.8, 'engagement': 0.7, 'speed': 0.5},
            'listening': {'retention': 0.7, 'engagement': 0.8, 'speed': 0.7},
            'speaking': {'retention': 0.6, 'engagement': 0.9, 'speed': 0.4},
            'role_play': {'retention': 0.7, 'engagement': 0.9, 'speed': 0.5},
            'image_recognition': {'retention': 0.8, 'engagement': 0.8, 'speed': 0.7}
        }

    def analyze_user_performance(self, user_id: int, days: int = 7) -> Dict:
        """
        Analyze user's recent performance across multiple dimensions.
        """
        # Get recent activity logs
        start_date = datetime.utcnow() - timedelta(days=days)
        recent_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                         .filter(UserActivityLog.completed_at >= start_date)\
                                         .order_by(UserActivityLog.completed_at.desc()).all()
        
        if not recent_logs:
            return self._get_default_performance_profile()
        
        # Get activity details
        activity_ids = [log.activity_id for log in recent_logs]
        activities = Activity.query.filter(Activity.id.in_(activity_ids)).all()
        activity_dict = {a.id: a for a in activities}
        
        # Calculate performance metrics
        total_activities = len(recent_logs)
        total_score = 0
        total_max_score = 0
        activity_type_performance = {}
        difficulty_performance = {}
        time_efficiency = []
        consistency_scores = []
        
        for log in recent_logs:
            activity = activity_dict.get(log.activity_id)
            if not activity or not log.score or not log.max_score:
                continue
            
            # Overall performance
            total_score += log.score
            total_max_score += log.max_score
            accuracy = log.score / log.max_score
            
            # Performance by activity type
            activity_type = activity.activity_type
            if activity_type not in activity_type_performance:
                activity_type_performance[activity_type] = []
            activity_type_performance[activity_type].append(accuracy)
            
            # Performance by difficulty
            difficulty = activity.difficulty_level
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = []
            difficulty_performance[difficulty].append(accuracy)
            
            # Time efficiency (accuracy per minute)
            if log.time_spent_minutes and log.time_spent_minutes > 0:
                efficiency = accuracy / log.time_spent_minutes
                time_efficiency.append(efficiency)
            
            # Consistency (daily performance variation)
            consistency_scores.append(accuracy)
        
        # Calculate averages
        overall_accuracy = total_score / total_max_score if total_max_score > 0 else 0
        
        avg_type_performance = {}
        for activity_type, scores in activity_type_performance.items():
            avg_type_performance[activity_type] = sum(scores) / len(scores)
        
        avg_difficulty_performance = {}
        for difficulty, scores in difficulty_performance.items():
            avg_difficulty_performance[difficulty] = sum(scores) / len(scores)
        
        avg_efficiency = sum(time_efficiency) / len(time_efficiency) if time_efficiency else 0
        
        # Calculate consistency (lower standard deviation = more consistent)
        if len(consistency_scores) > 1:
            mean_score = sum(consistency_scores) / len(consistency_scores)
            variance = sum((x - mean_score) ** 2 for x in consistency_scores) / len(consistency_scores)
            consistency = 1 - min(math.sqrt(variance), 1)  # Convert to 0-1 scale
        else:
            consistency = 1.0
        
        return {
            'overall_accuracy': overall_accuracy,
            'total_activities': total_activities,
            'activity_type_performance': avg_type_performance,
            'difficulty_performance': avg_difficulty_performance,
            'time_efficiency': avg_efficiency,
            'consistency': consistency,
            'analysis_period_days': days,
            'performance_trend': self._calculate_performance_trend(recent_logs, activity_dict)
        }

    def recommend_next_activities(self, user_id: int, learning_path_id: Optional[int] = None, 
                                count: int = 5) -> List[Dict]:
        """
        Recommend the next best activities for the user based on adaptive learning algorithm.
        """
        # Analyze current performance
        performance = self.analyze_user_performance(user_id)
        
        # Get user's learning preferences and goals
        user = User.query.get(user_id)
        user_preferences = self._extract_user_preferences(user)
        
        # Identify knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(user_id, performance)
        
        # Determine optimal difficulty level
        optimal_difficulty = self._calculate_optimal_difficulty(performance)
        
        # Get available activities (or generate new ones)
        if learning_path_id:
            available_activities = self._get_learning_path_activities(learning_path_id, user_id)
        else:
            available_activities = self._get_general_activities(user_id)
        
        # Score and rank activities
        scored_activities = []
        for activity in available_activities:
            score = self._score_activity_recommendation(
                activity, performance, knowledge_gaps, optimal_difficulty, user_preferences
            )
            scored_activities.append((activity, score))
        
        # Sort by score and return top recommendations
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for activity, score in scored_activities[:count]:
            recommendation = {
                'activity_id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'recommendation_score': round(score, 2),
                'recommendation_reasons': self._get_recommendation_reasons(
                    activity, performance, knowledge_gaps, optimal_difficulty
                ),
                'learning_path_id': activity.learning_path_id
            }
            recommendations.append(recommendation)
        
        return recommendations

    def assess_concept_mastery(self, user_id: int, skill_area: str, concept: str) -> Dict:
        """
        Assess if user has mastered a concept through comprehensive evaluation.
        """
        try:
            # Get recent activities for this concept
            recent_logs = UserActivityLog.query.join(Activity)\
                .filter(UserActivityLog.user_id == user_id)\
                .filter(Activity.skill_area == skill_area)\
                .filter(Activity.concept_focus == concept)\
                .order_by(UserActivityLog.completed_at.desc())\
                .limit(10).all()
            
            if len(recent_logs) < self.MIN_ACTIVITIES_FOR_ASSESSMENT:
                return {
                    'mastery_status': 'insufficient_data',
                    'confidence': 0.0,
                    'recommendation': 'Complete more activities to assess mastery',
                    'activities_needed': self.MIN_ACTIVITIES_FOR_ASSESSMENT - len(recent_logs)
                }
            
            # Calculate mastery metrics
            scores = [log.score / log.max_score for log in recent_logs if log.max_score > 0]
            if not scores:
                return {'mastery_status': 'no_valid_scores', 'confidence': 0.0}
            
            avg_score = sum(scores) / len(scores)
            consistency = self._calculate_score_consistency(scores)
            recent_trend = self._calculate_recent_trend(scores)
            
            # Determine mastery level
            if avg_score >= self.MASTERY_THRESHOLD and consistency >= 0.8 and recent_trend >= 0:
                mastery_status = 'mastered'
                confidence = min(0.95, avg_score * consistency)
            elif avg_score >= self.DIFFICULTY_ADJUSTMENT_THRESHOLD and consistency >= 0.6:
                mastery_status = 'proficient'
                confidence = avg_score * consistency * 0.8
            elif avg_score < self.STRUGGLE_THRESHOLD:
                mastery_status = 'struggling'
                confidence = 1.0 - avg_score
            else:
                mastery_status = 'learning'
                confidence = avg_score * 0.7
            
            return {
                'mastery_status': mastery_status,
                'confidence': round(confidence, 2),
                'average_score': round(avg_score, 2),
                'consistency': round(consistency, 2),
                'recent_trend': round(recent_trend, 2),
                'activities_completed': len(recent_logs),
                'recommendation': self._get_mastery_recommendation(mastery_status, avg_score)
            }
            
        except Exception as e:
            return {'error': f'Mastery assessment failed: {str(e)}'}

    def _calculate_score_consistency(self, scores: List[float]) -> float:
        """Calculate consistency of scores (lower variance = higher consistency)."""
        if len(scores) < 2:
            return 1.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = math.sqrt(variance)
        
        # Convert to 0-1 scale where 1 is most consistent
        consistency = max(0, 1 - std_dev)
        return consistency

    def _calculate_recent_trend(self, scores: List[float]) -> float:
        """Calculate if recent scores are improving (positive) or declining (negative)."""
        if len(scores) < 3:
            return 0.0
        
        # Compare recent half vs earlier half
        mid_point = len(scores) // 2
        recent_avg = sum(scores[:mid_point]) / mid_point
        earlier_avg = sum(scores[mid_point:]) / (len(scores) - mid_point)
        
        return recent_avg - earlier_avg

    def _get_mastery_recommendation(self, mastery_status: str, avg_score: float) -> str:
        """Get recommendation based on mastery status."""
        recommendations = {
            'mastered': 'Excellent! Ready to move to the next concept.',
            'proficient': 'Good progress! Consider one more practice session before advancing.',
            'learning': 'Keep practicing! You\'re making good progress.',
            'struggling': 'Let\'s try a different approach or review fundamentals.'
        }
        return recommendations.get(mastery_status, 'Continue practicing to improve.')

    def implement_spaced_repetition(self, user_id: int, concept: str) -> Dict:
        """
        Implement spaced repetition algorithm for concept reinforcement.
        """
        try:
            # Get the last time this concept was practiced
            last_activity = UserActivityLog.query.join(Activity)\
                .filter(UserActivityLog.user_id == user_id)\
                .filter(Activity.concept_focus == concept)\
                .order_by(UserActivityLog.completed_at.desc())\
                .first()
            
            if not last_activity:
                return {'next_review': 'now', 'interval_hours': 0}
            
            # Calculate time since last practice
            time_since_last = datetime.utcnow() - last_activity.completed_at
            hours_since = time_since_last.total_seconds() / 3600
            
            # Get performance level for spacing calculation
            performance_level = last_activity.score / last_activity.max_score if last_activity.max_score > 0 else 0.5
            
            # Calculate optimal spacing interval based on performance
            if performance_level >= 0.9:
                base_interval = 72  # 3 days for excellent performance  
            elif performance_level >= 0.8:
                base_interval = 48  # 2 days for good performance
            elif performance_level >= 0.7:
                base_interval = 24  # 1 day for fair performance
            else:
                base_interval = 8   # 8 hours for poor performance
            
            # Adjust interval based on previous intervals (expanding)
            concept_history = UserActivityLog.query.join(Activity)\
                .filter(UserActivityLog.user_id == user_id)\
                .filter(Activity.concept_focus == concept)\
                .count()
            
            # Increase interval with each successful repetition
            adjusted_interval = base_interval * (1.5 ** max(0, concept_history - 3))
            
            if hours_since >= adjusted_interval:
                return {
                    'next_review': 'now',
                    'interval_hours': 0,
                    'last_practiced': last_activity.completed_at.isoformat(),
                    'performance_level': round(performance_level, 2)
                }
            else:
                next_review_time = last_activity.completed_at + timedelta(hours=adjusted_interval)
                return {
                    'next_review': next_review_time.isoformat(),
                    'interval_hours': round(adjusted_interval - hours_since, 1),
                    'last_practiced': last_activity.completed_at.isoformat(),
                    'performance_level': round(performance_level, 2)
                }
                
        except Exception as e:
            return {'error': f'Spaced repetition calculation failed: {str(e)}'}

    def detect_learning_difficulties(self, user_id: int, skill_area: str = None) -> Dict:
        """
        Detect learning difficulties and suggest interventions.
        """
        try:
            # Get recent performance data
            query = UserActivityLog.query.filter_by(user_id=user_id)
            if skill_area:
                query = query.join(Activity).filter(Activity.skill_area == skill_area)
                
            recent_logs = query.order_by(UserActivityLog.completed_at.desc()).limit(20).all()
            
            if not recent_logs:
                return {'difficulties_detected': False, 'message': 'Insufficient data'}
            
            difficulties = []
            interventions = []
            
            # Analyze performance patterns
            scores = [log.score / log.max_score for log in recent_logs if log.max_score > 0]
            
            # Check for consistent low performance
            if scores and sum(scores) / len(scores) < self.STRUGGLE_THRESHOLD:
                difficulties.append('consistently_low_scores')
                interventions.append('review_fundamentals')
            
            # Check for declining performance
            if len(scores) >= 5:
                recent_avg = sum(scores[:5]) / 5
                earlier_avg = sum(scores[5:10]) / min(5, len(scores) - 5) if len(scores) > 5 else recent_avg
                
                if recent_avg < earlier_avg - 0.2:  # Significant decline
                    difficulties.append('declining_performance')
                    interventions.append('reduce_difficulty')
            
            # Check for high variability (inconsistent performance)
            if scores:
                consistency = self._calculate_score_consistency(scores)
                if consistency < 0.5:
                    difficulties.append('inconsistent_performance')
                    interventions.append('focus_on_weak_areas')
            
            # Check for time efficiency issues
            time_spent = [log.time_spent_minutes for log in recent_logs if log.time_spent_minutes]
            if time_spent:
                avg_time = sum(time_spent) / len(time_spent)
                if avg_time > 30:  # Taking too long
                    difficulties.append('excessive_time_needed')
                    interventions.append('provide_hints_and_guidance')
            
            return {
                'difficulties_detected': len(difficulties) > 0,
                'difficulties': difficulties,
                'recommended_interventions': interventions,
                'support_message': self._generate_support_message(difficulties),
                'confidence': min(1.0, len(difficulties) * 0.3)
            }
            
        except Exception as e:
            return {'error': f'Difficulty detection failed: {str(e)}'}

    def _generate_support_message(self, difficulties: List[str]) -> str:
        """Generate supportive message based on detected difficulties."""
        if not difficulties:
            return "You're doing great! Keep up the excellent work!"
        
        messages = {
            'consistently_low_scores': "Don't worry about the scores - learning takes time! Let's review some basics.",
            'declining_performance': "It seems like you might be feeling challenged. Let's slow down and practice more.",
            'inconsistent_performance': "Your performance varies - let's focus on your strong areas first.",
            'excessive_time_needed': "Take your time! Quality learning is more important than speed."
        }
        
        primary_difficulty = difficulties[0]
        return messages.get(primary_difficulty, "We're here to help you succeed! Let's adjust your learning plan.")

    def adjust_difficulty_dynamically(self, user_id: int, activity_id: int, 
                                   user_performance: Dict) -> Dict:
        """
        Dynamically adjust difficulty based on real-time performance with mastery validation.
        """
        activity = Activity.query.get(activity_id)
        if not activity:
            return {'error': 'Activity not found'}
        
        # Get user's performance on this specific activity type
        performance_analysis = self.analyze_user_performance(user_id)
        activity_type_performance = performance_analysis['activity_type_performance'].get(
            activity.activity_type, 0.5
        )
        
        current_difficulty = activity.difficulty_level
        user_accuracy = user_performance.get('accuracy', 0)
        
        # Determine if adjustment is needed
        adjustment_needed = False
        new_difficulty = current_difficulty
        adjustment_reason = ""
        
        if user_accuracy >= self.MASTERY_THRESHOLD and activity_type_performance >= self.MASTERY_THRESHOLD:
            # User is mastering this level - increase difficulty
            if current_difficulty == 'beginner':
                new_difficulty = 'intermediate'
                adjustment_needed = True
                adjustment_reason = "Mastery demonstrated - ready for intermediate level"
            elif current_difficulty == 'intermediate':
                new_difficulty = 'advanced'
                adjustment_needed = True
                adjustment_reason = "Excellent performance - advancing to advanced level"
            elif current_difficulty == 'advanced':
                new_difficulty = 'expert'
                adjustment_needed = True
                adjustment_reason = "Outstanding mastery - ready for expert challenges"
        
        elif user_accuracy <= self.STRUGGLE_THRESHOLD:
            # User is struggling - decrease difficulty or provide support
            if current_difficulty == 'expert':
                new_difficulty = 'advanced'
                adjustment_needed = True
                adjustment_reason = "Providing more foundation - moving to advanced level"
            elif current_difficulty == 'advanced':
                new_difficulty = 'intermediate'
                adjustment_needed = True
                adjustment_reason = "Building confidence - returning to intermediate level"
            elif current_difficulty == 'intermediate':
                new_difficulty = 'beginner'
                adjustment_needed = True
                adjustment_reason = "Strengthening basics - focusing on beginner level"
        
        # Generate adaptive content if adjustment is needed
        adaptive_suggestions = []
        if adjustment_needed:
            adaptive_suggestions = self._generate_adaptive_content_suggestions(
                user_id, activity, new_difficulty, user_performance
            )
        
        return {
            'adjustment_needed': adjustment_needed,
            'current_difficulty': current_difficulty,
            'recommended_difficulty': new_difficulty,
            'adjustment_reason': adjustment_reason,
            'adaptive_content_suggestions': adaptive_suggestions,
            'telugu_explanation': self._get_telugu_difficulty_explanation(
                adjustment_needed, current_difficulty, new_difficulty
            )
        }

    def identify_learning_gaps(self, user_id: int) -> Dict:
        """
        Identify specific learning gaps and recommend targeted interventions.
        """
        # Get comprehensive performance data
        performance = self.analyze_user_performance(user_id, days=30)
        
        # Analyze gaps by skill area
        skill_gaps = {
            'vocabulary': self._analyze_vocabulary_gaps(user_id),
            'grammar': self._analyze_grammar_gaps(user_id),
            'reading': self._analyze_reading_gaps(user_id),
            'writing': self._analyze_writing_gaps(user_id),
            'speaking': self._analyze_speaking_gaps(user_id),
            'listening': self._analyze_listening_gaps(user_id)
        }
        
        # Prioritize gaps by severity and impact
        prioritized_gaps = self._prioritize_learning_gaps(skill_gaps, performance)
        
        # Generate targeted interventions
        interventions = []
        for gap in prioritized_gaps[:3]:  # Top 3 priority gaps
            intervention = self._generate_gap_intervention(user_id, gap)
            interventions.append(intervention)
        
        return {
            'identified_gaps': skill_gaps,
            'prioritized_gaps': prioritized_gaps,
            'recommended_interventions': interventions,
            'overall_assessment': self._generate_overall_gap_assessment(skill_gaps, performance)
        }

    def personalize_learning_pace(self, user_id: int) -> Dict:
        """
        Personalize learning pace based on user's learning patterns and performance.
        """
        # Analyze learning patterns
        user = User.query.get(user_id)
        performance = self.analyze_user_performance(user_id, days=21)  # 3 weeks
        
        # Get learning frequency and session patterns
        recent_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                                         .filter(UserActivityLog.completed_at >= datetime.utcnow() - timedelta(days=21))\
                                         .order_by(UserActivityLog.completed_at.desc()).all()
        
        # Analyze session patterns
        daily_sessions = {}
        session_lengths = []
        
        for log in recent_logs:
            date_key = log.completed_at.date()
            if date_key not in daily_sessions:
                daily_sessions[date_key] = 0
            daily_sessions[date_key] += 1
            
            if log.time_spent_minutes:
                session_lengths.append(log.time_spent_minutes)
        
        # Calculate optimal pace metrics
        avg_sessions_per_day = len(recent_logs) / 21 if recent_logs else 0
        avg_session_length = sum(session_lengths) / len(session_lengths) if session_lengths else 0
        consistency = performance.get('consistency', 0.5)
        
        # Determine optimal pace
        optimal_pace = self._calculate_optimal_learning_pace(
            avg_sessions_per_day, avg_session_length, consistency, performance
        )
        
        return {
            'current_pace_analysis': {
                'avg_sessions_per_day': round(avg_sessions_per_day, 1),
                'avg_session_length_minutes': round(avg_session_length, 1),
                'consistency_score': round(consistency, 2),
                'overall_accuracy': round(performance.get('overall_accuracy', 0), 2)
            },
            'optimal_pace_recommendation': optimal_pace,
            'pace_adjustments': self._generate_pace_adjustments(optimal_pace, performance),
            'motivation_strategies': self._suggest_motivation_strategies(user_id, optimal_pace)
        }

    def generate_adaptive_exercise(self, user_id: int, topic: str, skill_area: str) -> Dict:
        """
        Generate a custom exercise adapted to the user's current skill level and learning needs.
        """
        # Analyze user's current level
        performance = self.analyze_user_performance(user_id)
        optimal_difficulty = self._calculate_optimal_difficulty(performance)
        
        # Get user's specific performance in this skill area
        skill_performance = performance['activity_type_performance'].get(skill_area, 0.5)
        
        # Generate adaptive prompt
        adaptive_prompt = f"""
        Generate a personalized English learning exercise for a Telugu speaker.
        
        User Profile:
        - Overall Accuracy: {performance.get('overall_accuracy', 0.5):.1%}
        - Skill Area Performance ({skill_area}): {skill_performance:.1%}
        - Optimal Difficulty: {optimal_difficulty}
        - Recent Activity Count: {performance.get('total_activities', 0)}
        
        Exercise Requirements:
        - Topic: {topic}
        - Skill Area: {skill_area}
        - Difficulty: {optimal_difficulty}
        - Adaptive to user's performance level
        
        Generate an exercise that:
        1. Matches the user's current skill level
        2. Provides appropriate challenge
        3. Includes Telugu support where helpful
        4. Has clear assessment criteria
        
        Return in JSON format:
        ```json
        {{
            "exercise": {{
                "title": "Adaptive {skill_area.title()} Exercise: {topic}",
                "instructions": "Complete the following tasks...",
                "telugu_instructions": "కింది కార్యాలను పూర్తి చేయండి...",
                "content": {{
                    "questions": [
                        {{
                            "question": "Exercise question",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": "A",
                            "telugu_hint": "సూచన..."
                        }}
                    ]
                }},
                "difficulty_adaptations": [
                    "Simplified vocabulary for current level",
                    "Extra Telugu explanations provided"
                ],
                "success_criteria": {{
                    "minimum_score": 70,
                    "time_limit_minutes": 15
                }}
            }},
            "adaptive_features": [
                "Difficulty matched to user performance",
                "Telugu support based on needs",
                "Progressive challenge structure"
            ]
        }}
        ```
        """
        
        response = self.activity_service.model.generate_content(adaptive_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        adaptive_exercise = _extract_json_from_response(response.text)
        
        return {
            'adaptive_exercise': adaptive_exercise,
            'user_performance_context': {
                'overall_accuracy': performance.get('overall_accuracy', 0),
                'skill_area_performance': skill_performance,
                'optimal_difficulty': optimal_difficulty
            },
            'adaptation_notes': {
                'difficulty_reasoning': f"Set to {optimal_difficulty} based on {performance.get('overall_accuracy', 0):.1%} accuracy",
                'support_level': 'high' if skill_performance < 0.6 else 'medium' if skill_performance < 0.8 else 'low'
            }
        }

    # Private helper methods
    
    def _get_default_performance_profile(self) -> Dict:
        """Return default performance profile for new users."""
        return {
            'overall_accuracy': 0.5,
            'total_activities': 0,
            'activity_type_performance': {},
            'difficulty_performance': {'beginner': 0.5},
            'time_efficiency': 0.5,
            'consistency': 0.5,
            'analysis_period_days': 7,
            'performance_trend': 'stable'
        }

    def _calculate_performance_trend(self, logs: List, activity_dict: Dict) -> str:
        """Calculate if performance is improving, declining, or stable."""
        if len(logs) < 3:
            return 'insufficient_data'
        
        # Compare recent performance to older performance
        recent_logs = logs[:len(logs)//2]
        older_logs = logs[len(logs)//2:]
        
        recent_avg = self._calculate_average_accuracy(recent_logs, activity_dict)
        older_avg = self._calculate_average_accuracy(older_logs, activity_dict)
        
        if recent_avg > older_avg + 0.1:
            return 'improving'
        elif recent_avg < older_avg - 0.1:
            return 'declining'
        else:
            return 'stable'

    def _calculate_average_accuracy(self, logs: List, activity_dict: Dict) -> float:
        """Calculate average accuracy for a set of logs."""
        total_score = 0
        total_max = 0
        
        for log in logs:
            if log.score and log.max_score:
                total_score += log.score
                total_max += log.max_score
        
        return total_score / total_max if total_max > 0 else 0.5

    def _extract_user_preferences(self, user: User) -> Dict:
        """Extract user preferences from user profile and enrollment data."""
        preferences = {
            'preferred_difficulty': 'beginner',
            'preferred_activity_types': ['quiz', 'flashcard'],
            'learning_goals': ['conversation'],
            'time_availability': 30  # minutes per day
        }
        
        if hasattr(user, 'enrollment_data') and user.enrollment_data:
            enrollment_data = user.enrollment_data
            if isinstance(enrollment_data, dict):
                preferences.update({
                    'preferred_difficulty': enrollment_data.get('difficulty_preference', 'beginner'),
                    'learning_goals': enrollment_data.get('learning_goals', ['conversation']),
                    'time_availability': enrollment_data.get('time_available_minutes', 30)
                })
        
        return preferences

    def _identify_knowledge_gaps(self, user_id: int, performance: Dict) -> List[Dict]:
        """Identify specific knowledge gaps based on performance analysis."""
        gaps = []
        
        # Check activity type performance
        for activity_type, avg_score in performance.get('activity_type_performance', {}).items():
            if avg_score < self.STRUGGLE_THRESHOLD:
                gaps.append({
                    'type': 'activity_type',
                    'area': activity_type,
                    'severity': 'high' if avg_score < 0.3 else 'medium',
                    'performance': avg_score
                })
        
        # Check difficulty level performance
        for difficulty, avg_score in performance.get('difficulty_performance', {}).items():
            if avg_score < self.STRUGGLE_THRESHOLD:
                gaps.append({
                    'type': 'difficulty_level',
                    'area': difficulty,
                    'severity': 'high' if avg_score < 0.3 else 'medium',
                    'performance': avg_score
                })
        
        return gaps

    def _calculate_optimal_difficulty(self, performance: Dict) -> str:
        """Calculate the optimal difficulty level for the user."""
        overall_accuracy = performance.get('overall_accuracy', 0.5)
        
        if overall_accuracy >= 0.85:
            return 'advanced'
        elif overall_accuracy >= 0.7:
            return 'intermediate'
        else:
            return 'beginner'

    def _get_learning_path_activities(self, learning_path_id: int, user_id: int) -> List:
        """Get available activities from a specific learning path."""
        # Get activities user hasn't completed yet
        completed_activity_ids = [
            log.activity_id for log in 
            UserActivityLog.query.filter_by(user_id=user_id, learning_path_id=learning_path_id).all()
        ]
        
        activities = Activity.query.filter_by(learning_path_id=learning_path_id)\
                                 .filter(~Activity.id.in_(completed_activity_ids))\
                                 .order_by(Activity.order_in_path).limit(10).all()
        
        return activities

    def _get_general_activities(self, user_id: int) -> List:
        """Get general activities suitable for the user."""
        # Get activities user hasn't completed
        completed_activity_ids = [
            log.activity_id for log in UserActivityLog.query.filter_by(user_id=user_id).all()
        ]
        
        activities = Activity.query.filter(~Activity.id.in_(completed_activity_ids))\
                                 .limit(20).all()
        
        return activities

    def _score_activity_recommendation(self, activity: Activity, performance: Dict, 
                                     knowledge_gaps: List, optimal_difficulty: str, 
                                     preferences: Dict) -> float:
        """Score an activity for recommendation based on multiple factors."""
        score = 0.0
        
        # Difficulty match (30% weight)
        if activity.difficulty_level == optimal_difficulty:
            score += 30
        elif activity.difficulty_level == preferences.get('preferred_difficulty'):
            score += 20
        
        # Activity type preference and performance (25% weight)
        activity_type_performance = performance['activity_type_performance'].get(activity.activity_type, 0.5)
        if activity_type_performance < 0.6:  # Needs improvement
            score += 25
        elif activity.activity_type in preferences.get('preferred_activity_types', []):
            score += 15
        
        # Knowledge gap addressing (25% weight)
        for gap in knowledge_gaps:
            if (gap['type'] == 'activity_type' and gap['area'] == activity.activity_type) or \
               (gap['type'] == 'difficulty_level' and gap['area'] == activity.difficulty_level):
                score += 25
                break
        
        # Time availability match (10% weight)
        if activity.estimated_duration_minutes <= preferences.get('time_availability', 30):
            score += 10
        
        # Variety bonus (10% weight) - encourage trying different types
        if activity.activity_type not in performance.get('activity_type_performance', {}):
            score += 10
        
        return score

    def _get_recommendation_reasons(self, activity: Activity, performance: Dict, 
                                  knowledge_gaps: List, optimal_difficulty: str) -> List[str]:
        """Generate human-readable reasons for recommending this activity."""
        reasons = []
        
        if activity.difficulty_level == optimal_difficulty:
            reasons.append(f"Matches your optimal difficulty level ({optimal_difficulty})")
        
        activity_type_performance = performance['activity_type_performance'].get(activity.activity_type, 0.5)
        if activity_type_performance < 0.6:
            reasons.append(f"Helps improve {activity.activity_type} skills (current: {activity_type_performance:.1%})")
        
        for gap in knowledge_gaps:
            if gap['area'] == activity.activity_type:
                reasons.append(f"Addresses identified weakness in {activity.activity_type}")
                break
        
        if not reasons:
            reasons.append("Good practice activity for continued learning")
        
        return reasons

    def _generate_adaptive_content_suggestions(self, user_id: int, activity: Activity, 
                                             new_difficulty: str, user_performance: Dict) -> List[Dict]:
        """Generate suggestions for adaptive content modifications."""
        suggestions = []
        
        current_accuracy = user_performance.get('accuracy', 0.5)
        
        if current_accuracy < 0.5:
            suggestions.append({
                'type': 'support_enhancement',
                'description': 'Add more Telugu explanations and hints',
                'implementation': 'Include Telugu translations for key terms'
            })
            suggestions.append({
                'type': 'complexity_reduction',
                'description': 'Simplify vocabulary and sentence structure',
                'implementation': 'Use more common words and shorter sentences'
            })
        
        elif current_accuracy > 0.8:
            suggestions.append({
                'type': 'challenge_increase',
                'description': 'Add more complex scenarios and edge cases',
                'implementation': 'Include advanced vocabulary and grammar patterns'
            })
            suggestions.append({
                'type': 'application_focus',
                'description': 'Emphasize practical application and real-world usage',
                'implementation': 'Create contextual scenarios and conversations'
            })
        
        return suggestions

    def _get_telugu_difficulty_explanation(self, adjustment_needed: bool, 
                                         current_difficulty: str, new_difficulty: str) -> str:
        """Generate Telugu explanation for difficulty adjustments."""
        if not adjustment_needed:
            return "మీ ప్రస్తుత స్థాయి సరైనది - అదే స్థాయిలో కొనసాగండి"
        
        if new_difficulty > current_difficulty:
            return f"మీ పనితీరు అద్భుతంగా ఉంది! {new_difficulty} స్థాయికి ముందుకు వెళ్తున్నాము"
        else:
            return f"మరింత అభ్యాసం కోసం {new_difficulty} స్థాయికి తిరిగి వెళ్తున్నాము"

    def _analyze_vocabulary_gaps(self, user_id: int) -> Dict:
        """Analyze vocabulary-specific learning gaps."""
        # This would analyze vocabulary-related activities
        return {'gap_level': 'medium', 'areas': ['business_terms', 'daily_conversation']}

    def _analyze_grammar_gaps(self, user_id: int) -> Dict:
        """Analyze grammar-specific learning gaps."""
        return {'gap_level': 'high', 'areas': ['verb_tenses', 'sentence_structure']}

    def _analyze_reading_gaps(self, user_id: int) -> Dict:
        """Analyze reading comprehension gaps."""
        return {'gap_level': 'low', 'areas': ['comprehension_speed']}

    def _analyze_writing_gaps(self, user_id: int) -> Dict:
        """Analyze writing skill gaps."""
        return {'gap_level': 'medium', 'areas': ['essay_structure', 'formal_writing']}

    def _analyze_speaking_gaps(self, user_id: int) -> Dict:
        """Analyze speaking skill gaps."""
        return {'gap_level': 'high', 'areas': ['pronunciation', 'fluency']}

    def _analyze_listening_gaps(self, user_id: int) -> Dict:
        """Analyze listening comprehension gaps."""
        return {'gap_level': 'medium', 'areas': ['accent_recognition', 'fast_speech']}

    def _prioritize_learning_gaps(self, skill_gaps: Dict, performance: Dict) -> List[Dict]:
        """Prioritize learning gaps by importance and urgency."""
        prioritized = []
        
        for skill, gap_data in skill_gaps.items():
            priority_score = 0
            
            # High gap level = higher priority
            if gap_data['gap_level'] == 'high':
                priority_score += 3
            elif gap_data['gap_level'] == 'medium':
                priority_score += 2
            else:
                priority_score += 1
            
            # Foundation skills get higher priority
            if skill in ['vocabulary', 'grammar']:
                priority_score += 2
            
            prioritized.append({
                'skill': skill,
                'gap_data': gap_data,
                'priority_score': priority_score
            })
        
        return sorted(prioritized, key=lambda x: x['priority_score'], reverse=True)

    def _generate_gap_intervention(self, user_id: int, gap: Dict) -> Dict:
        """Generate targeted intervention for a specific gap."""
        skill = gap['skill']
        gap_data = gap['gap_data']
        
        intervention = {
            'skill_area': skill,
            'intervention_type': 'focused_practice',
            'recommended_activities': [
                f"Daily {skill} exercises (10 minutes)",
                f"Targeted {skill} challenges",
                f"Progressive {skill} skill building"
            ],
            'duration_weeks': 2 if gap_data['gap_level'] == 'high' else 1,
            'success_metrics': [
                f"Improve {skill} accuracy to 70%+",
                f"Complete 10 {skill} activities",
                f"Demonstrate consistent progress"
            ]
        }
        
        return intervention

    def _generate_overall_gap_assessment(self, skill_gaps: Dict, performance: Dict) -> Dict:
        """Generate overall assessment of learning gaps."""
        high_gaps = [skill for skill, data in skill_gaps.items() if data['gap_level'] == 'high']
        medium_gaps = [skill for skill, data in skill_gaps.items() if data['gap_level'] == 'medium']
        
        assessment = {
            'overall_level': 'needs_attention' if high_gaps else 'progressing_well',
            'priority_areas': high_gaps[:2],  # Top 2 high priority areas
            'estimated_improvement_time': f"{len(high_gaps) * 2 + len(medium_gaps)} weeks",
            'confidence_level': 'high' if performance.get('total_activities', 0) > 20 else 'medium'
        }
        
        return assessment

    def _calculate_optimal_learning_pace(self, avg_sessions: float, avg_length: float, 
                                       consistency: float, performance: Dict) -> Dict:
        """Calculate optimal learning pace based on user patterns."""
        # Determine optimal sessions per day
        if consistency > 0.8 and performance.get('overall_accuracy', 0) > 0.7:
            optimal_sessions = min(avg_sessions * 1.2, 3)  # Can handle slight increase
        elif consistency < 0.5 or performance.get('overall_accuracy', 0) < 0.5:
            optimal_sessions = max(avg_sessions * 0.8, 1)  # Reduce to build confidence
        else:
            optimal_sessions = avg_sessions  # Maintain current pace
        
        # Determine optimal session length
        if avg_length > 0:
            if performance.get('time_efficiency', 0) > 0.8:
                optimal_length = min(avg_length * 1.1, 45)  # Can handle longer sessions
            elif performance.get('time_efficiency', 0) < 0.5:
                optimal_length = max(avg_length * 0.9, 10)  # Shorter, focused sessions
            else:
                optimal_length = avg_length
        else:
            optimal_length = 20  # Default 20 minutes
        
        return {
            'optimal_sessions_per_day': round(optimal_sessions, 1),
            'optimal_session_length_minutes': round(optimal_length),
            'weekly_time_commitment': round(optimal_sessions * optimal_length * 7),
            'pace_intensity': 'moderate' if optimal_sessions <= 2 else 'intensive'
        }

    def _generate_pace_adjustments(self, optimal_pace: Dict, performance: Dict) -> List[Dict]:
        """Generate specific pace adjustment recommendations."""
        adjustments = []
        
        current_intensity = performance.get('total_activities', 0) / 7  # Activities per day
        optimal_intensity = optimal_pace.get('optimal_sessions_per_day', 1)
        
        if optimal_intensity > current_intensity:
            adjustments.append({
                'type': 'increase_frequency',
                'description': f"Increase to {optimal_intensity} activities per day",
                'reason': 'You can handle more challenge based on your performance'
            })
        elif optimal_intensity < current_intensity:
            adjustments.append({
                'type': 'reduce_frequency',
                'description': f"Reduce to {optimal_intensity} activities per day",
                'reason': 'Focus on quality over quantity for better retention'
            })
        
        return adjustments

    def _suggest_motivation_strategies(self, user_id: int, optimal_pace: Dict) -> List[str]:
        """Suggest motivation strategies based on learning pace."""
        strategies = []
        
        pace_intensity = optimal_pace.get('pace_intensity', 'moderate')
        
        if pace_intensity == 'intensive':
            strategies.extend([
                "Set daily achievement goals",
                "Track weekly progress milestones",
                "Use gamification elements for engagement"
            ])
        else:
            strategies.extend([
                "Focus on consistent daily habits",
                "Celebrate small wins",
                "Join community challenges"
            ])
        
        strategies.append("Regular progress reviews with positive reinforcement")
        
        return strategies