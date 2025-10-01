import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.models import (
    db, User, Activity, UserActivityLog, LearningPath,
    ProficiencyAssessment
)
from app.services.adaptive_learning_service import AdaptiveLearningAlgorithm
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class RealTimePerformanceMonitor:
    """
    Real-time performance monitoring system that tracks user behavior patterns,
    identifies struggling points, and triggers adaptive interventions.
    """
    
    def __init__(self):
        self.adaptive_algorithm = AdaptiveLearningAlgorithm()
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Performance thresholds
        self.STRUGGLE_THRESHOLD = 0.5
        self.ATTENTION_THRESHOLD = 0.3  # Time without activity
        self.ERROR_PATTERN_THRESHOLD = 3  # Consecutive errors
        self.DIFFICULTY_SPIKE_THRESHOLD = 0.3  # Performance drop
        
        # Intervention triggers
        self.HINT_TRIGGER_SCORE = 0.4
        self.METHOD_SWITCH_TRIGGER = 3  # Consecutive poor performances
        self.BREAK_SUGGESTION_TIME = 30  # Minutes of continuous struggle
        
        # Real-time tracking state
        self.active_sessions = {}  # user_id -> session_data

    def start_learning_session(self, user_id: int, activity_id: int) -> Dict:
        """
        Start monitoring a learning session for real-time adaptation.
        """
        try:
            activity = Activity.query.get(activity_id)
            if not activity:
                return {'error': 'Activity not found'}
            
            session_data = {
                'user_id': user_id,
                'activity_id': activity_id,
                'start_time': datetime.utcnow(),
                'interaction_count': 0,
                'correct_answers': 0,
                'incorrect_answers': 0,
                'hint_requests': 0,
                'time_spent_per_question': [],
                'error_patterns': [],
                'struggle_indicators': [],
                'last_interaction': datetime.utcnow(),
                'performance_history': []
            }
            
            self.active_sessions[user_id] = session_data
            
            return {
                'session_id': f"{user_id}_{activity_id}_{int(datetime.utcnow().timestamp())}",
                'monitoring_active': True,
                'adaptive_features_enabled': True,
                'initial_difficulty': activity.difficulty_level
            }
            
        except Exception as e:
            return {'error': f'Session monitoring failed: {str(e)}'}

    def track_user_interaction(self, user_id: int, interaction_data: Dict) -> Dict:
        """
        Track user interaction and provide real-time feedback/adaptation.
        """
        try:
            if user_id not in self.active_sessions:
                return {'error': 'No active monitoring session'}
            
            session = self.active_sessions[user_id]
            current_time = datetime.utcnow()
            
            # Update session data
            session['interaction_count'] += 1
            session['last_interaction'] = current_time
            
            # Track response data
            is_correct = interaction_data.get('is_correct', False)
            response_time = interaction_data.get('response_time_seconds', 0)
            difficulty = interaction_data.get('difficulty_level', 'medium')
            
            if is_correct:
                session['correct_answers'] += 1
            else:
                session['incorrect_answers'] += 1
                self._track_error_pattern(session, interaction_data)
            
            session['time_spent_per_question'].append(response_time)
            
            # Calculate current performance metrics
            current_accuracy = session['correct_answers'] / session['interaction_count']
            avg_response_time = sum(session['time_spent_per_question']) / len(session['time_spent_per_question'])
            
            # Real-time analysis and interventions
            interventions = self._analyze_and_intervene(session, current_accuracy, avg_response_time)
            
            # Update performance history
            session['performance_history'].append({
                'timestamp': current_time.isoformat(),
                'accuracy': current_accuracy,
                'response_time': response_time,
                'is_correct': is_correct
            })
            
            return {
                'session_performance': {
                    'current_accuracy': round(current_accuracy, 2),
                    'average_response_time': round(avg_response_time, 2),
                    'total_interactions': session['interaction_count'],
                    'correct_answers': session['correct_answers'],
                    'incorrect_answers': session['incorrect_answers']
                },
                'interventions': interventions,
                'continue_monitoring': True
            }
            
        except Exception as e:
            return {'error': f'Interaction tracking failed: {str(e)}'}

    def _track_error_pattern(self, session: Dict, interaction_data: Dict):
        """
        Track patterns in user errors for targeted intervention.
        """
        error_type = interaction_data.get('error_type', 'unknown')
        question_type = interaction_data.get('question_type', 'general')
        skill_area = interaction_data.get('skill_area', 'general')
        
        error_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': error_type,
            'question_type': question_type,
            'skill_area': skill_area,
            'user_answer': interaction_data.get('user_answer', ''),
            'correct_answer': interaction_data.get('correct_answer', '')
        }
        
        session['error_patterns'].append(error_info)
        
        # Detect consecutive errors in same area
        recent_errors = session['error_patterns'][-3:]  # Last 3 errors
        if len(recent_errors) == 3:
            if all(error['skill_area'] == skill_area for error in recent_errors):
                session['struggle_indicators'].append({
                    'type': 'consecutive_errors_same_skill',
                    'skill_area': skill_area,
                    'timestamp': datetime.utcnow().isoformat()
                })

    def _analyze_and_intervene(self, session: Dict, current_accuracy: float, 
                             avg_response_time: float) -> List[Dict]:
        """
        Analyze current performance and trigger appropriate interventions.
        """
        interventions = []
        
        # Check for struggle indicators
        if current_accuracy < self.STRUGGLE_THRESHOLD:
            interventions.extend(self._handle_performance_struggle(session, current_accuracy))
        
        # Check for excessive response time
        if avg_response_time > 60:  # More than 1 minute average
            interventions.append(self._suggest_hints_or_simplification(session))
        
        # Check for consecutive errors
        if len(session['error_patterns']) >= self.ERROR_PATTERN_THRESHOLD:
            recent_errors = session['error_patterns'][-self.ERROR_PATTERN_THRESHOLD:]
            if all(not self._is_correct_pattern(error) for error in recent_errors):
                interventions.append(self._suggest_method_change(session))
        
        # Check for attention/engagement issues
        time_since_last = (datetime.utcnow() - session['last_interaction']).total_seconds() / 60
        if time_since_last > self.ATTENTION_THRESHOLD:
            interventions.append(self._suggest_engagement_boost(session))
        
        # Check for fatigue indicators
        session_duration = (datetime.utcnow() - session['start_time']).total_seconds() / 60
        if session_duration > self.BREAK_SUGGESTION_TIME and current_accuracy < 0.6:
            interventions.append(self._suggest_break(session))
        
        return interventions

    def _handle_performance_struggle(self, session: Dict, accuracy: float) -> List[Dict]:
        """
        Handle performance struggles with targeted interventions.
        """
        interventions = []
        
        # Analyze error patterns to identify specific issues
        if session['error_patterns']:
            common_errors = self._identify_common_error_patterns(session['error_patterns'])
            
            for error_pattern in common_errors:
                if error_pattern['frequency'] >= 2:  # Appears at least twice
                    interventions.append({
                        'type': 'targeted_explanation',
                        'skill_area': error_pattern['skill_area'],
                        'error_type': error_pattern['error_type'],
                        'explanation': self._generate_targeted_explanation(error_pattern),
                        'priority': 'high'
                    })
        
        # Suggest difficulty reduction
        if accuracy < 0.3:
            interventions.append({
                'type': 'difficulty_reduction',
                'current_difficulty': 'high',
                'suggested_difficulty': 'low',
                'reason': 'Performance indicates current level is too challenging',
                'priority': 'high'
            })
        
        # Provide encouraging feedback
        interventions.append({
            'type': 'encouragement',
            'message': "Learning is a process! Let's try a different approach to help you succeed.",
            'telugu_message': "నేర్చుకోవడం ఒక ప్రక్రియ! మీరు విజయం సాధించడానికి వేరే మార్గం ప్రయత్నిద్దాం.",
            'priority': 'medium'
        })
        
        return interventions

    def _suggest_hints_or_simplification(self, session: Dict) -> Dict:
        """
        Suggest hints or simplification based on response time analysis.
        """
        return {
            'type': 'hint_suggestion',
            'reason': 'Extended thinking time detected',
            'suggestion': 'Would you like a hint to help you move forward?',
            'telugu_suggestion': 'మీకు సహాయం చేయడానికి సూచన కావాలా?',
            'hint_available': True,
            'priority': 'medium'
        }

    def _suggest_method_change(self, session: Dict) -> Dict:
        """
        Suggest changing teaching method after repeated failures.
        """
        session['hint_requests'] += 1
        
        return {
            'type': 'method_change',
            'current_method': 'current_activity_type',
            'suggested_method': 'visual_learning',  # Could be determined by AI
            'reason': 'Multiple incorrect attempts detected',
            'message': "Let's try a different way to learn this concept!",
            'telugu_message': "ఈ భావనను నేర్చుకోవడానికి వేరే మార్గం ప్రయత్నిద్దాం!",
            'priority': 'high'
        }

    def _suggest_engagement_boost(self, session: Dict) -> Dict:
        """
        Suggest engagement boosting activities for attention issues.
        """
        return {
            'type': 'engagement_boost',
            'reason': 'Reduced activity detected',
            'suggestions': [
                'Take a 2-minute break',
                'Try a quick vocabulary game',
                'Switch to a different activity type'
            ],
            'priority': 'medium'
        }

    def _suggest_break(self, session: Dict) -> Dict:
        """
        Suggest taking a break for sustained learning.
        """
        return {
            'type': 'break_suggestion',
            'reason': 'Extended learning session with declining performance',
            'message': 'Great effort! Consider taking a 10-15 minute break to recharge.',
            'telugu_message': 'మంచి కృషి! తాజాగా ఉండేందుకు 10-15 నిమిషాల విరామం తీసుకోండి.',
            'suggested_break_duration': 15,
            'priority': 'high'
        }

    def _identify_common_error_patterns(self, error_patterns: List[Dict]) -> List[Dict]:
        """
        Identify common error patterns from user mistakes.
        """
        error_counts = {}
        
        for error in error_patterns:
            key = f"{error['skill_area']}_{error['error_type']}"
            if key not in error_counts:
                error_counts[key] = {
                    'skill_area': error['skill_area'],
                    'error_type': error['error_type'],
                    'frequency': 0,
                    'examples': []
                }
            error_counts[key]['frequency'] += 1
            error_counts[key]['examples'].append({
                'user_answer': error.get('user_answer', ''),
                'correct_answer': error.get('correct_answer', '')
            })
        
        # Return patterns sorted by frequency
        return sorted(error_counts.values(), key=lambda x: x['frequency'], reverse=True)

    def _generate_targeted_explanation(self, error_pattern: Dict) -> str:
        """
        Generate targeted explanation for specific error patterns.
        """
        skill_area = error_pattern['skill_area']
        error_type = error_pattern['error_type']
        
        explanations = {
            'grammar_tense': 'Remember to match the tense with the time indicator in the sentence.',
            'vocabulary_meaning': 'Try to understand the context to determine the correct word meaning.',
            'reading_comprehension': 'Read the passage carefully and look for key information.',
            'writing_structure': 'Focus on proper sentence structure: Subject + Verb + Object.'
        }
        
        key = f"{skill_area}_{error_type}"
        return explanations.get(key, f"Let's review the basics of {skill_area} to strengthen your understanding.")

    def _is_correct_pattern(self, error: Dict) -> bool:
        """
        Check if an error entry actually represents a correct response.
        """
        # This would be used to filter out correct responses from error patterns
        return False  # For now, assume all entries in error_patterns are actual errors

    def generate_adaptive_content(self, user_id: int, performance_data: Dict) -> Dict:
        """
        Generate adaptive content based on real-time performance analysis.
        """
        try:
            if user_id not in self.active_sessions:
                return {'error': 'No active session to adapt content'}
            
            session = self.active_sessions[user_id]
            current_accuracy = performance_data.get('accuracy', 0.5)
            common_errors = self._identify_common_error_patterns(session['error_patterns'])
            
            # Determine content adaptation strategy
            if current_accuracy < 0.4:
                # Significant struggle - simplify and provide foundation
                adaptation_strategy = 'simplify_and_reinforce'
            elif current_accuracy < 0.7:
                # Moderate struggle - provide targeted practice
                adaptation_strategy = 'targeted_practice'
            else:
                # Good performance - can increase challenge
                adaptation_strategy = 'progressive_challenge'
            
            # Generate adapted content using AI
            content_prompt = self._create_content_adaptation_prompt(
                session, adaptation_strategy, common_errors
            )
            
            # For now, return structured adaptation without AI call
            adapted_content = self._generate_structured_adaptation(
                adaptation_strategy, common_errors, session
            )
            
            return {
                'adaptation_strategy': adaptation_strategy,
                'adapted_content': adapted_content,
                'reasoning': f"Based on {current_accuracy:.1%} accuracy and error patterns",
                'confidence': 0.8
            }
            
        except Exception as e:
            return {'error': f'Adaptive content generation failed: {str(e)}'}

    def _create_content_adaptation_prompt(self, session: Dict, strategy: str, 
                                        common_errors: List[Dict]) -> str:
        """
        Create AI prompt for content adaptation.
        """
        return f"""
        Adapt learning content based on the following user performance data:
        
        Session Summary:
        - Total interactions: {session['interaction_count']}
        - Correct answers: {session['correct_answers']}
        - Incorrect answers: {session['incorrect_answers']}
        - Common errors: {[error['error_type'] for error in common_errors[:3]]}
        
        Adaptation Strategy: {strategy}
        
        Generate appropriate learning content that addresses the identified issues
        and follows the specified adaptation strategy. Include:
        1. Modified questions or explanations
        2. Additional practice exercises
        3. Hints or scaffolding
        4. Motivational messaging
        """

    def _generate_structured_adaptation(self, strategy: str, common_errors: List[Dict], 
                                      session: Dict) -> Dict:
        """
        Generate structured content adaptation without AI.
        """
        adaptations = {
            'simplify_and_reinforce': {
                'difficulty_adjustment': 'reduce',
                'content_modifications': [
                    'Break complex questions into smaller parts',
                    'Provide more examples and explanations',
                    'Add visual aids and context clues'
                ],
                'scaffolding': [
                    'Step-by-step guidance',
                    'Multiple choice instead of open-ended',
                    'Immediate feedback after each response'
                ]
            },
            'targeted_practice': {
                'difficulty_adjustment': 'maintain',
                'content_modifications': [
                    'Focus on specific error patterns',
                    'Provide targeted explanations',
                    'Include similar problems for practice'
                ],
                'scaffolding': [
                    'Hints available on request',
                    'Show examples of correct responses',
                    'Explain why wrong answers are incorrect'
                ]
            },
            'progressive_challenge': {
                'difficulty_adjustment': 'increase',
                'content_modifications': [
                    'Introduce more complex scenarios',
                    'Reduce scaffolding gradually',
                    'Add time challenges or bonus questions'
                ],
                'scaffolding': [
                    'Minimal hints',
                    'Encourage independent problem-solving',
                    'Provide advanced explanations'
                ]
            }
        }
        
        return adaptations.get(strategy, adaptations['targeted_practice'])

    def end_learning_session(self, user_id: int) -> Dict:
        """
        End the monitoring session and provide summary analytics.
        """
        try:
            if user_id not in self.active_sessions:
                return {'error': 'No active session to end'}
            
            session = self.active_sessions[user_id]
            end_time = datetime.utcnow()
            total_duration = (end_time - session['start_time']).total_seconds() / 60
            
            # Calculate final metrics
            final_accuracy = session['correct_answers'] / session['interaction_count'] if session['interaction_count'] > 0 else 0
            avg_response_time = sum(session['time_spent_per_question']) / len(session['time_spent_per_question']) if session['time_spent_per_question'] else 0
            
            # Generate session summary
            session_summary = {
                'duration_minutes': round(total_duration, 2),
                'total_interactions': session['interaction_count'],
                'final_accuracy': round(final_accuracy, 2),
                'average_response_time': round(avg_response_time, 2),
                'correct_answers': session['correct_answers'],
                'incorrect_answers': session['incorrect_answers'],
                'hint_requests': session['hint_requests'],
                'error_patterns_identified': len(session['error_patterns']),
                'struggle_indicators': len(session['struggle_indicators'])
            }
            
            # Clean up session
            del self.active_sessions[user_id]
            
            return {
                'session_ended': True,
                'session_summary': session_summary,
                'performance_insights': self._generate_performance_insights(session),
                'recommendations_for_next_session': self._generate_next_session_recommendations(session)
            }
            
        except Exception as e:
            return {'error': f'Session ending failed: {str(e)}'}

    def _generate_performance_insights(self, session: Dict) -> Dict:
        """
        Generate insights from the completed session.
        """
        insights = []
        
        accuracy = session['correct_answers'] / session['interaction_count'] if session['interaction_count'] > 0 else 0
        
        if accuracy >= 0.8:
            insights.append("Excellent performance! You're mastering this concept.")
        elif accuracy >= 0.6:
            insights.append("Good progress! A bit more practice will help you master this.")
        else:
            insights.append("This concept needs more attention. Let's review the fundamentals.")
        
        if session['hint_requests'] > session['interaction_count'] * 0.5:
            insights.append("You requested many hints - consider reviewing the basics.")
        
        if session['struggle_indicators']:
            insights.append(f"Identified {len(session['struggle_indicators'])} areas needing focused practice.")
        
        return {
            'performance_level': 'excellent' if accuracy >= 0.8 else ('good' if accuracy >= 0.6 else 'needs_improvement'),
            'insights': insights,
            'confidence_score': accuracy
        }

    def _generate_next_session_recommendations(self, session: Dict) -> List[str]:
        """
        Generate recommendations for the next learning session.
        """
        recommendations = []
        
        accuracy = session['correct_answers'] / session['interaction_count'] if session['interaction_count'] > 0 else 0
        
        if accuracy < 0.5:
            recommendations.append("Review fundamental concepts before attempting new material")
            recommendations.append("Consider shorter practice sessions with immediate feedback")
        elif accuracy < 0.7:
            recommendations.append("Practice similar problems to reinforce learning")
            recommendations.append("Focus on areas where errors occurred most frequently")
        else:
            recommendations.append("Ready for more challenging material")
            recommendations.append("Consider exploring advanced concepts in this area")
        
        if session['error_patterns']:
            common_error_areas = list(set([error['skill_area'] for error in session['error_patterns']]))
            recommendations.append(f"Focus extra attention on: {', '.join(common_error_areas)}")
        
        return recommendations