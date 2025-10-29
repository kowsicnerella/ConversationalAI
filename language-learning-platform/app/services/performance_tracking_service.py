"""
Phase 4: Performance Tracking Engine
Comprehensive performance monitoring and analysis across all skill dimensions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import func, and_, desc
import statistics
import json

from app.models import db
from app.models.performance_tracking import (
    ListeningPerformance,
    SpeakingPerformance,
    ReadingPerformance,
    WritingPerformance,
    RealWorldPerformance,
    SkillTrajectory
)
from app.models.user_tracking import UserActivityCompletion


class PerformanceTrackingEngine:
    """
    Advanced performance tracking and analysis engine
    """
    
    def __init__(self):
        self._llm_service = None
    
    @property
    def llm_service(self):
        """Lazy load LLMService only when needed"""
        if self._llm_service is None:
            from app.services.llm_service import LLMService
            self._llm_service = LLMService()
        return self._llm_service
        
    # ================== CORE TRACKING METHODS ==================
    
    def track_listening_performance(
        self,
        user_id: int,
        activity_id: int,
        performance_data: Dict[str, Any]
    ) -> ListeningPerformance:
        """
        Track listening comprehension performance
        
        Args:
            user_id: User ID
            activity_id: Activity ID
            performance_data: Dictionary containing performance metrics
        
        Returns:
            ListeningPerformance record
        """
        # Get previous performance for comparison
        previous = db.session.query(ListeningPerformance).filter_by(
            user_id=user_id
        ).order_by(desc(ListeningPerformance.completed_at)).first()
        
        previous_score = previous.comprehension_score if previous else None
        
        # Calculate improvement rate
        improvement_rate = 0.0
        if previous_score and performance_data.get('comprehension_score'):
            improvement_rate = ((performance_data['comprehension_score'] - previous_score) / 
                              previous_score * 100)
        
        # Determine mastery level
        mastery_level = self._determine_mastery_level(
            performance_data.get('comprehension_score', 0)
        )
        
        # Generate AI feedback if not provided
        if not performance_data.get('ai_feedback'):
            try:
                ai_analysis = self.llm_service.generate_improvement_suggestions(
                    skill_type='listening',
                    performance_data=performance_data,
                    difficulty_level=performance_data.get('difficulty_level', 'intermediate')
                )
                performance_data['ai_feedback'] = ai_analysis.get('feedback', '')
                performance_data['improvement_suggestions'] = ai_analysis.get('specific_suggestions', [])
            except Exception as e:
                print(f"AI feedback generation failed: {e}")
                # Continue without AI feedback
        
        # Create performance record
        performance = ListeningPerformance(
            user_id=user_id,
            activity_id=activity_id,
            session_id=performance_data.get('session_id'),
            audio_duration=performance_data.get('audio_duration', 0),
            audio_url=performance_data.get('audio_url'),
            accent_type=performance_data.get('accent_type', 'american'),
            speed_factor=performance_data.get('speed_factor', 1.0),
            topic=performance_data.get('topic'),
            difficulty_level=performance_data.get('difficulty_level', 'intermediate'),
            comprehension_score=performance_data.get('comprehension_score', 0),
            accuracy_percentage=performance_data.get('accuracy_percentage', 0),
            playback_count=performance_data.get('playback_count', 1),
            pause_points=performance_data.get('pause_points', []),
            pause_count=len(performance_data.get('pause_points', [])),
            replay_sections=performance_data.get('replay_sections', []),
            difficult_segments=performance_data.get('difficult_segments', []),
            difficult_words=performance_data.get('difficult_words', []),
            new_vocabulary_encountered=performance_data.get('new_vocabulary', []),
            context_understanding=performance_data.get('context_understanding', 0),
            inference_ability=performance_data.get('inference_ability', 0),
            questions_data=performance_data.get('questions_data', {}),
            total_questions=performance_data.get('total_questions', 0),
            correct_answers=performance_data.get('correct_answers', 0),
            time_to_complete=performance_data.get('time_to_complete', 0),
            avg_time_per_question=performance_data.get('avg_time_per_question', 0),
            weak_phonemes=performance_data.get('weak_phonemes', []),
            accent_adaptation_score=performance_data.get('accent_adaptation', 0),
            ai_feedback=performance_data.get('ai_feedback'),
            improvement_suggestions=performance_data.get('improvement_suggestions', []),
            previous_score=previous_score,
            improvement_rate=improvement_rate,
            mastery_level=mastery_level
        )
        
        db.session.add(performance)
        db.session.commit()
        
        # Update skill trajectory
        self._update_skill_trajectory(
            user_id=user_id,
            skill_domain='listening',
            performance_score=performance_data.get('comprehension_score', 0),
            activity_type='listening'
        )
        
        return performance
    
    def track_speaking_performance(
        self,
        user_id: int,
        activity_id: int,
        performance_data: Dict[str, Any]
    ) -> SpeakingPerformance:
        """Track speaking performance with detailed metrics"""
        
        previous = db.session.query(SpeakingPerformance).filter_by(
            user_id=user_id
        ).order_by(desc(SpeakingPerformance.completed_at)).first()
        
        previous_score = previous.overall_score if previous else None
        improvement_rate = 0.0
        if previous_score and performance_data.get('overall_score'):
            improvement_rate = ((performance_data['overall_score'] - previous_score) / 
                              previous_score * 100)
        
        mastery_level = self._determine_mastery_level(
            performance_data.get('overall_score', 0)
        )
        
        performance = SpeakingPerformance(
            user_id=user_id,
            activity_id=activity_id,
            session_id=performance_data.get('session_id'),
            speaking_type=performance_data.get('speaking_type', 'conversation'),
            topic=performance_data.get('topic'),
            scenario=performance_data.get('scenario'),
            difficulty_level=performance_data.get('difficulty_level', 'intermediate'),
            audio_url=performance_data.get('audio_url'),
            recording_duration=performance_data.get('recording_duration', 0),
            transcript=performance_data.get('transcript'),
            expected_content=performance_data.get('expected_content'),
            pronunciation_accuracy=performance_data.get('pronunciation_accuracy', 0),
            fluency_score=performance_data.get('fluency_score', 0),
            grammar_score=performance_data.get('grammar_score', 0),
            vocabulary_richness=performance_data.get('vocabulary_richness', 0),
            overall_score=performance_data.get('overall_score', 0),
            words_per_minute=performance_data.get('words_per_minute', 0),
            speaking_rate=performance_data.get('speaking_rate', 'normal'),
            hesitation_count=performance_data.get('hesitation_count', 0),
            filler_words=performance_data.get('filler_words', []),
            filler_word_count=len(performance_data.get('filler_words', [])),
            pause_analysis=performance_data.get('pause_analysis', {}),
            mispronounced_words=performance_data.get('mispronounced_words', []),
            phoneme_errors=performance_data.get('phoneme_errors', []),
            accent_score=performance_data.get('accent_score', 0),
            intonation_score=performance_data.get('intonation_score', 0),
            grammar_errors=performance_data.get('grammar_errors', []),
            grammar_error_count=len(performance_data.get('grammar_errors', [])),
            vocabulary_used=performance_data.get('vocabulary_used', []),
            advanced_vocabulary_count=performance_data.get('advanced_vocabulary_count', 0),
            vocabulary_appropriateness=performance_data.get('vocabulary_appropriateness', 0),
            confidence_level=performance_data.get('confidence_level', 0),
            volume_consistency=performance_data.get('volume_consistency', 0),
            emotional_expression=performance_data.get('emotional_expression', 0),
            content_relevance=performance_data.get('content_relevance', 0),
            coherence_score=performance_data.get('coherence_score', 0),
            task_completion=performance_data.get('task_completion', 0),
            ai_feedback=performance_data.get('ai_feedback'),
            pronunciation_tips=performance_data.get('pronunciation_tips', []),
            grammar_corrections=performance_data.get('grammar_corrections', []),
            vocabulary_suggestions=performance_data.get('vocabulary_suggestions', []),
            improvement_areas=performance_data.get('improvement_areas', []),
            previous_score=previous_score,
            improvement_rate=improvement_rate,
            mastery_level=mastery_level,
            practice_needed=performance_data.get('practice_needed', [])
        )
        
        db.session.add(performance)
        db.session.commit()
        
        self._update_skill_trajectory(
            user_id=user_id,
            skill_domain='speaking',
            performance_score=performance_data.get('overall_score', 0),
            activity_type='speaking'
        )
        
        return performance
    
    def track_reading_performance(
        self,
        user_id: int,
        activity_id: int,
        performance_data: Dict[str, Any]
    ) -> ReadingPerformance:
        """Track reading comprehension performance"""
        
        previous = db.session.query(ReadingPerformance).filter_by(
            user_id=user_id
        ).order_by(desc(ReadingPerformance.completed_at)).first()
        
        previous_score = previous.comprehension_score if previous else None
        previous_speed = previous.reading_speed_wpm if previous else None
        
        # Calculate improvements
        comprehension_improvement = 0.0
        speed_improvement = 0.0
        
        if previous_score and performance_data.get('comprehension_score'):
            comprehension_improvement = ((performance_data['comprehension_score'] - previous_score) / 
                                        previous_score * 100)
        
        if previous_speed and performance_data.get('reading_speed_wpm'):
            speed_improvement = ((performance_data['reading_speed_wpm'] - previous_speed) / 
                               previous_speed * 100)
        
        mastery_level = self._determine_mastery_level(
            performance_data.get('comprehension_score', 0)
        )
        
        performance = ReadingPerformance(
            user_id=user_id,
            activity_id=activity_id,
            session_id=performance_data.get('session_id'),
            text_title=performance_data.get('text_title'),
            text_type=performance_data.get('text_type', 'article'),
            topic=performance_data.get('topic'),
            difficulty_level=performance_data.get('difficulty_level', 'intermediate'),
            word_count=performance_data.get('word_count', 0),
            text_complexity=performance_data.get('text_complexity', 0),
            reading_time_seconds=performance_data.get('reading_time_seconds', 0),
            reading_speed_wpm=performance_data.get('reading_speed_wpm', 0),
            speed_rating=performance_data.get('speed_rating', 'average'),
            target_speed_wpm=performance_data.get('target_speed_wpm', 200),
            comprehension_score=performance_data.get('comprehension_score', 0),
            accuracy_percentage=performance_data.get('accuracy_percentage', 0),
            literal_comprehension=performance_data.get('literal_comprehension', 0),
            inferential_comprehension=performance_data.get('inferential_comprehension', 0),
            critical_comprehension=performance_data.get('critical_comprehension', 0),
            vocabulary_lookups=performance_data.get('vocabulary_lookups', []),
            lookup_count=len(performance_data.get('vocabulary_lookups', [])),
            re_read_sections=performance_data.get('re_read_sections', []),
            re_read_count=len(performance_data.get('re_read_sections', [])),
            time_per_paragraph=performance_data.get('time_per_paragraph', []),
            questions_data=performance_data.get('questions_data', {}),
            total_questions=performance_data.get('total_questions', 0),
            correct_answers=performance_data.get('correct_answers', 0),
            time_per_question=performance_data.get('time_per_question', []),
            avg_time_per_question=performance_data.get('avg_time_per_question', 0),
            new_vocabulary_encountered=performance_data.get('new_vocabulary', []),
            unknown_words=performance_data.get('unknown_words', []),
            vocabulary_coverage=performance_data.get('vocabulary_coverage', 0),
            main_idea_understanding=performance_data.get('main_idea_understanding', 0),
            detail_retention=performance_data.get('detail_retention', 0),
            inference_ability=performance_data.get('inference_ability', 0),
            context_clue_usage=performance_data.get('context_clue_usage', 0),
            ai_feedback=performance_data.get('ai_feedback'),
            reading_strategies_used=performance_data.get('reading_strategies', []),
            improvement_suggestions=performance_data.get('improvement_suggestions', []),
            vocabulary_to_study=performance_data.get('vocabulary_to_study', []),
            previous_score=previous_score,
            previous_speed_wpm=previous_speed,
            speed_improvement=speed_improvement,
            comprehension_improvement=comprehension_improvement,
            mastery_level=mastery_level
        )
        
        db.session.add(performance)
        db.session.commit()
        
        self._update_skill_trajectory(
            user_id=user_id,
            skill_domain='reading',
            performance_score=performance_data.get('comprehension_score', 0),
            activity_type='reading'
        )
        
        return performance
    
    def track_writing_performance(
        self,
        user_id: int,
        activity_id: int,
        performance_data: Dict[str, Any]
    ) -> WritingPerformance:
        """Track writing performance"""
        
        previous = db.session.query(WritingPerformance).filter_by(
            user_id=user_id
        ).order_by(desc(WritingPerformance.completed_at)).first()
        
        previous_score = previous.overall_score if previous else None
        improvement_rate = 0.0
        if previous_score and performance_data.get('overall_score'):
            improvement_rate = ((performance_data['overall_score'] - previous_score) / 
                              previous_score * 100)
        
        mastery_level = self._determine_mastery_level(
            performance_data.get('overall_score', 0)
        )
        
        performance = WritingPerformance(
            user_id=user_id,
            activity_id=activity_id,
            session_id=performance_data.get('session_id'),
            writing_type=performance_data.get('writing_type', 'essay'),
            topic=performance_data.get('topic'),
            prompt=performance_data.get('prompt'),
            difficulty_level=performance_data.get('difficulty_level', 'intermediate'),
            target_word_count=performance_data.get('target_word_count', 0),
            content=performance_data.get('content', ''),
            word_count=performance_data.get('word_count', 0),
            character_count=performance_data.get('character_count', 0),
            paragraph_count=performance_data.get('paragraph_count', 0),
            sentence_count=performance_data.get('sentence_count', 0),
            overall_score=performance_data.get('overall_score', 0),
            grammar_score=performance_data.get('grammar_score', 0),
            vocabulary_score=performance_data.get('vocabulary_score', 0),
            coherence_score=performance_data.get('coherence_score', 0),
            task_achievement=performance_data.get('task_achievement', 0),
            grammar_errors=performance_data.get('grammar_errors', []),
            grammar_error_count=len(performance_data.get('grammar_errors', [])),
            error_types=performance_data.get('error_types', {}),
            spelling_errors=performance_data.get('spelling_errors', []),
            spelling_error_count=len(performance_data.get('spelling_errors', [])),
            punctuation_errors=performance_data.get('punctuation_errors', []),
            punctuation_error_count=len(performance_data.get('punctuation_errors', [])),
            vocabulary_used=performance_data.get('vocabulary_used', []),
            unique_words=performance_data.get('unique_words', 0),
            advanced_vocabulary=performance_data.get('advanced_vocabulary', []),
            advanced_vocabulary_count=len(performance_data.get('advanced_vocabulary', [])),
            vocabulary_diversity=performance_data.get('vocabulary_diversity', 0),
            vocabulary_appropriateness=performance_data.get('vocabulary_appropriateness', 0),
            repetitive_words=performance_data.get('repetitive_words', []),
            sentence_lengths=performance_data.get('sentence_lengths', []),
            avg_sentence_length=performance_data.get('avg_sentence_length', 0),
            sentence_variety=performance_data.get('sentence_variety', 0),
            simple_sentences=performance_data.get('simple_sentences', 0),
            compound_sentences=performance_data.get('compound_sentences', 0),
            complex_sentences=performance_data.get('complex_sentences', 0),
            sentence_complexity=performance_data.get('sentence_complexity', 0),
            paragraph_organization=performance_data.get('paragraph_organization', 0),
            transition_usage=performance_data.get('transition_usage', 0),
            topic_consistency=performance_data.get('topic_consistency', 0),
            argument_development=performance_data.get('argument_development', 0),
            originality_score=performance_data.get('originality_score', 0),
            depth_of_content=performance_data.get('depth_of_content', 0),
            relevance_to_prompt=performance_data.get('relevance_to_prompt', 0),
            supporting_evidence=performance_data.get('supporting_evidence', 0),
            writing_time_minutes=performance_data.get('writing_time_minutes', 0),
            revision_count=performance_data.get('revision_count', 0),
            edit_history=performance_data.get('edit_history', []),
            planning_time=performance_data.get('planning_time', 0),
            ai_feedback=performance_data.get('ai_feedback'),
            strengths=performance_data.get('strengths', []),
            areas_for_improvement=performance_data.get('areas_for_improvement', []),
            grammar_corrections=performance_data.get('grammar_corrections', []),
            vocabulary_suggestions=performance_data.get('vocabulary_suggestions', []),
            structural_suggestions=performance_data.get('structural_suggestions', []),
            previous_score=previous_score,
            improvement_rate=improvement_rate,
            mastery_level=mastery_level,
            target_skills=performance_data.get('target_skills', [])
        )
        
        db.session.add(performance)
        db.session.commit()
        
        self._update_skill_trajectory(
            user_id=user_id,
            skill_domain='writing',
            performance_score=performance_data.get('overall_score', 0),
            activity_type='writing'
        )
        
        return performance
    
    def track_real_world_performance(
        self,
        user_id: int,
        activity_id: int,
        performance_data: Dict[str, Any]
    ) -> RealWorldPerformance:
        """Track real-world scenario performance"""
        
        previous = db.session.query(RealWorldPerformance).filter_by(
            user_id=user_id,
            scenario_type=performance_data.get('scenario_type')
        ).order_by(desc(RealWorldPerformance.completed_at)).first()
        
        previous_score = previous.overall_score if previous else None
        improvement_rate = 0.0
        if previous_score and performance_data.get('overall_score'):
            improvement_rate = ((performance_data['overall_score'] - previous_score) / 
                              previous_score * 100)
        
        # Count similar scenarios completed
        similar_count = db.session.query(func.count(RealWorldPerformance.id)).filter_by(
            user_id=user_id,
            scenario_type=performance_data.get('scenario_type')
        ).scalar()
        
        mastery_level = self._determine_mastery_level(
            performance_data.get('overall_score', 0)
        )
        
        performance = RealWorldPerformance(
            user_id=user_id,
            activity_id=activity_id,
            session_id=performance_data.get('session_id'),
            scenario_type=performance_data.get('scenario_type', 'email'),
            industry=performance_data.get('industry'),
            context=performance_data.get('context'),
            difficulty_level=performance_data.get('difficulty_level', 'intermediate'),
            task_description=performance_data.get('task_description'),
            expected_outcomes=performance_data.get('expected_outcomes', []),
            user_response=performance_data.get('user_response'),
            response_format=performance_data.get('response_format', 'written'),
            overall_score=performance_data.get('overall_score', 0),
            task_completion=performance_data.get('task_completion', 0),
            appropriateness_score=performance_data.get('appropriateness_score', 0),
            professional_language_use=performance_data.get('professional_language_use', 0),
            cultural_awareness=performance_data.get('cultural_awareness', 0),
            clarity_score=performance_data.get('clarity_score', 0),
            persuasiveness=performance_data.get('persuasiveness', 0),
            diplomacy_score=performance_data.get('diplomacy_score', 0),
            engagement_quality=performance_data.get('engagement_quality', 0),
            vocabulary_appropriateness=performance_data.get('vocabulary_appropriateness', 0),
            grammar_accuracy=performance_data.get('grammar_accuracy', 0),
            register_appropriateness=performance_data.get('register_appropriateness', 0),
            idiomatic_usage=performance_data.get('idiomatic_usage', 0),
            email_etiquette_score=performance_data.get('email_etiquette_score'),
            presentation_structure=performance_data.get('presentation_structure'),
            interview_response_quality=performance_data.get('interview_response_quality'),
            negotiation_effectiveness=performance_data.get('negotiation_effectiveness'),
            meeting_participation=performance_data.get('meeting_participation'),
            time_management=performance_data.get('time_management', 0),
            response_time_seconds=performance_data.get('response_time_seconds', 0),
            expected_time_seconds=performance_data.get('expected_time_seconds', 0),
            strengths=performance_data.get('strengths', []),
            weaknesses=performance_data.get('weaknesses', []),
            mistakes_made=performance_data.get('mistakes_made', []),
            best_practices_followed=performance_data.get('best_practices_followed', []),
            best_practices_missed=performance_data.get('best_practices_missed', []),
            ai_feedback=performance_data.get('ai_feedback'),
            improvement_suggestions=performance_data.get('improvement_suggestions', []),
            alternative_approaches=performance_data.get('alternative_approaches', []),
            vocabulary_suggestions=performance_data.get('vocabulary_suggestions', []),
            phrase_suggestions=performance_data.get('phrase_suggestions', []),
            skills_demonstrated=performance_data.get('skills_demonstrated', []),
            skills_to_develop=performance_data.get('skills_to_develop', []),
            real_world_readiness=performance_data.get('real_world_readiness', 0),
            confidence_level=performance_data.get('confidence_level', 0),
            previous_score=previous_score,
            improvement_rate=improvement_rate,
            mastery_level=mastery_level,
            similar_scenarios_completed=similar_count
        )
        
        db.session.add(performance)
        db.session.commit()
        
        self._update_skill_trajectory(
            user_id=user_id,
            skill_domain='real_world',
            performance_score=performance_data.get('overall_score', 0),
            activity_type=performance_data.get('scenario_type')
        )
        
        return performance
    
    # ================== ANALYSIS METHODS ==================
    
    def analyze_skill_trajectory(
        self,
        user_id: int,
        skill_domain: str,
        time_window_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze skill improvement trajectory over time
        
        Returns comprehensive analysis including trends, patterns, and predictions
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Get trajectory record
        trajectory = db.session.query(SkillTrajectory).filter_by(
            user_id=user_id,
            skill_domain=skill_domain
        ).first()
        
        if not trajectory:
            return {
                'error': 'No trajectory data found',
                'skill_domain': skill_domain
            }
        
        # Get performance history
        performance_history = trajectory.performance_history or []
        recent_history = [
            p for p in performance_history
            if datetime.fromisoformat(p['date']) >= cutoff_date
        ]
        
        if not recent_history:
            return {
                'skill_domain': skill_domain,
                'current_level': trajectory.current_level,
                'mastery_status': trajectory.mastery_status,
                'message': 'No recent performance data'
            }
        
        # Calculate statistics
        scores = [p['score'] for p in recent_history]
        avg_score = statistics.mean(scores)
        score_trend = self._calculate_trend(scores)
        
        # Determine velocity
        velocity = self._determine_velocity(scores)
        
        # Predict future performance
        prediction = self._predict_future_performance(scores, days_ahead=30)
        
        return {
            'skill_domain': skill_domain,
            'time_window_days': time_window_days,
            'current_level': trajectory.current_level,
            'mastery_status': trajectory.mastery_status,
            'baseline_level': trajectory.baseline_level,
            'peak_level': trajectory.peak_level,
            'statistics': {
                'average_score': round(avg_score, 2),
                'min_score': min(scores),
                'max_score': max(scores),
                'score_range': max(scores) - min(scores),
                'std_deviation': round(statistics.stdev(scores), 2) if len(scores) > 1 else 0
            },
            'trend': {
                'direction': score_trend['direction'],
                'strength': score_trend['strength'],
                'velocity': velocity
            },
            'practice_metrics': {
                'total_sessions': len(recent_history),
                'practice_frequency': trajectory.practice_frequency,
                'consistency_score': trajectory.consistency_score,
                'current_streak_days': trajectory.current_streak_days
            },
            'prediction': {
                'projected_score_30days': round(prediction['score'], 2),
                'confidence': prediction['confidence'],
                'estimated_days_to_mastery': trajectory.estimated_time_to_next_level
            },
            'performance_history': recent_history[-10:]  # Last 10 data points
        }
    
    def identify_learning_patterns(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Identify user's learning patterns and preferences
        
        Analyzes when they learn best, optimal session length, etc.
        """
        # Get all activity completions from last 60 days
        cutoff_date = datetime.utcnow() - timedelta(days=60)
        
        activities = db.session.query(UserActivityCompletion).filter(
            and_(
                UserActivityCompletion.user_id == user_id,
                UserActivityCompletion.completed_at >= cutoff_date
            )
        ).all()
        
        if not activities:
            return {'message': 'Not enough data to identify patterns'}
        
        # Analyze time-of-day patterns
        time_performance = self._analyze_time_patterns(activities)
        
        # Analyze session length patterns
        session_patterns = self._analyze_session_length(activities)
        
        # Analyze activity type preferences
        activity_preferences = self._analyze_activity_preferences(activities)
        
        # Identify struggle patterns
        struggle_patterns = self._identify_struggle_patterns(user_id)
        
        # Identify breakthrough moments
        breakthroughs = self._identify_breakthroughs(activities)
        
        return {
            'time_patterns': time_performance,
            'session_patterns': session_patterns,
            'activity_preferences': activity_preferences,
            'struggle_patterns': struggle_patterns,
            'breakthrough_moments': breakthroughs,
            'recommendations': self._generate_pattern_recommendations(
                time_performance,
                session_patterns,
                activity_preferences
            )
        }
    
    def predict_mastery_timeline(
        self,
        user_id: int,
        skill_domain: str
    ) -> Dict[str, Any]:
        """
        Predict when user will master a skill based on current trajectory
        """
        trajectory = db.session.query(SkillTrajectory).filter_by(
            user_id=user_id,
            skill_domain=skill_domain
        ).first()
        
        if not trajectory or not trajectory.performance_history:
            return {
                'error': 'Insufficient data for prediction',
                'skill_domain': skill_domain
            }
        
        current_level = trajectory.current_level
        mastery_threshold = 85.0  # 85% is considered mastery
        
        if current_level >= mastery_threshold:
            return {
                'skill_domain': skill_domain,
                'status': 'already_mastered',
                'current_level': current_level,
                'mastery_threshold': mastery_threshold
            }
        
        # Get improvement rate
        scores = [p['score'] for p in trajectory.performance_history[-20:]]
        improvement_per_session = self._calculate_improvement_rate(scores)
        
        # Estimate sessions needed
        points_needed = mastery_threshold - current_level
        sessions_needed = int(points_needed / improvement_per_session) if improvement_per_session > 0 else 0
        
        # Convert to days based on practice frequency
        practice_frequency = trajectory.practice_frequency or 3  # Default 3 times per week
        days_per_session = 7 / practice_frequency
        estimated_days = int(sessions_needed * days_per_session)
        
        # Calculate confidence based on consistency
        confidence = self._calculate_prediction_confidence(trajectory)
        
        return {
            'skill_domain': skill_domain,
            'current_level': current_level,
            'mastery_threshold': mastery_threshold,
            'points_needed': round(points_needed, 2),
            'estimated_sessions_needed': sessions_needed,
            'estimated_days': estimated_days,
            'estimated_date': (datetime.utcnow() + timedelta(days=estimated_days)).isoformat(),
            'confidence_level': confidence,
            'improvement_rate': round(improvement_per_session, 3),
            'practice_frequency_per_week': practice_frequency,
            'recommendations': self._generate_mastery_recommendations(
                current_level,
                improvement_per_session,
                practice_frequency
            )
        }
    
    # ================== HELPER METHODS ==================
    
    def _update_skill_trajectory(
        self,
        user_id: int,
        skill_domain: str,
        performance_score: float,
        activity_type: str
    ):
        """Update or create skill trajectory record"""
        
        trajectory = db.session.query(SkillTrajectory).filter_by(
            user_id=user_id,
            skill_domain=skill_domain
        ).first()
        
        if not trajectory:
            # Create new trajectory
            trajectory = SkillTrajectory(
                user_id=user_id,
                skill_domain=skill_domain,
                current_level=performance_score,
                baseline_level=performance_score,
                peak_level=performance_score,
                lowest_level=performance_score,
                total_practice_sessions=1,
                performance_history=[{
                    'date': datetime.utcnow().isoformat(),
                    'score': performance_score,
                    'activity_type': activity_type
                }],
                mastery_status=self._determine_mastery_level(performance_score)
            )
            db.session.add(trajectory)
        else:
            # Update existing trajectory
            trajectory.current_level = performance_score
            trajectory.peak_level = max(trajectory.peak_level or 0, performance_score)
            trajectory.lowest_level = min(trajectory.lowest_level or 100, performance_score)
            trajectory.total_practice_sessions += 1
            
            # Update performance history (keep last 30)
            history = trajectory.performance_history or []
            history.append({
                'date': datetime.utcnow().isoformat(),
                'score': performance_score,
                'activity_type': activity_type
            })
            trajectory.performance_history = history[-30:]
            
            # Update trend
            scores = [p['score'] for p in trajectory.performance_history]
            trend = self._calculate_trend(scores)
            trajectory.trend_direction = trend['direction']
            trajectory.trend_strength = trend['strength']
            trajectory.velocity = self._determine_velocity(scores)
            
            # Update mastery status
            trajectory.mastery_status = self._determine_mastery_level(performance_score)
            trajectory.last_updated = datetime.utcnow()
            trajectory.last_practice_date = datetime.utcnow()
        
        db.session.commit()
    
    def _determine_mastery_level(self, score: float) -> str:
        """Determine mastery level based on score"""
        if score >= 85:
            return 'expert'
        elif score >= 75:
            return 'advanced'
        elif score >= 60:
            return 'proficient'
        elif score >= 40:
            return 'developing'
        else:
            return 'novice'
    
    def _calculate_trend(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate trend direction and strength from scores"""
        if len(scores) < 3:
            return {'direction': 'stable', 'strength': 0.0}
        
        # Simple linear regression
        n = len(scores)
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(scores)
        
        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Determine direction
        if slope > 0.5:
            direction = 'improving'
        elif slope < -0.5:
            direction = 'declining'
        else:
            direction = 'stable'
        
        # Strength is absolute value of slope
        strength = abs(slope)
        
        return {'direction': direction, 'strength': round(strength, 3)}
    
    def _determine_velocity(self, scores: List[float]) -> str:
        """Determine learning velocity"""
        if len(scores) < 5:
            return 'insufficient_data'
        
        # Compare first half to second half
        mid = len(scores) // 2
        first_half_avg = statistics.mean(scores[:mid])
        second_half_avg = statistics.mean(scores[mid:])
        
        improvement = second_half_avg - first_half_avg
        
        if improvement > 10:
            return 'accelerating'
        elif improvement > 5:
            return 'fast'
        elif improvement > 0:
            return 'steady'
        elif improvement == 0:
            return 'plateauing'
        else:
            return 'slow'
    
    def _predict_future_performance(
        self,
        scores: List[float],
        days_ahead: int = 30
    ) -> Dict[str, Any]:
        """Predict future performance using simple linear extrapolation"""
        if len(scores) < 3:
            return {'score': scores[-1], 'confidence': 'low'}
        
        # Linear regression
        n = len(scores)
        x = list(range(n))
        
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(scores)
        
        numerator = sum((x[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        intercept = y_mean - slope * x_mean
        
        # Predict future score
        future_x = n + (days_ahead / 7)  # Assuming weekly sessions
        predicted_score = min(100, max(0, slope * future_x + intercept))
        
        # Calculate R-squared for confidence
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_res = sum((scores[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((scores[i] - y_mean) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        confidence = 'high' if r_squared > 0.7 else 'medium' if r_squared > 0.4 else 'low'
        
        return {
            'score': predicted_score,
            'confidence': confidence,
            'r_squared': round(r_squared, 3)
        }
    
    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate average improvement per session"""
        if len(scores) < 2:
            return 0.0
        
        improvements = [scores[i] - scores[i-1] for i in range(1, len(scores))]
        return statistics.mean(improvements)
    
    def _calculate_prediction_confidence(self, trajectory: SkillTrajectory) -> str:
        """Calculate confidence level for predictions"""
        factors = []
        
        # Factor 1: Consistency score
        if trajectory.consistency_score:
            factors.append(trajectory.consistency_score / 100)
        
        # Factor 2: Data points
        history_length = len(trajectory.performance_history or [])
        factors.append(min(1.0, history_length / 20))
        
        # Factor 3: Trend stability
        if trajectory.trend_strength:
            factors.append(min(1.0, trajectory.trend_strength))
        
        avg_confidence = statistics.mean(factors) if factors else 0
        
        if avg_confidence > 0.75:
            return 'high'
        elif avg_confidence > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_time_patterns(self, activities: List) -> Dict[str, Any]:
        """Analyze which times of day user performs best"""
        time_buckets = {'morning': [], 'afternoon': [], 'evening': [], 'night': []}
        
        for activity in activities:
            hour = activity.completed_at.hour
            score = activity.percentage or 0
            
            if 5 <= hour < 12:
                time_buckets['morning'].append(score)
            elif 12 <= hour < 17:
                time_buckets['afternoon'].append(score)
            elif 17 <= hour < 22:
                time_buckets['evening'].append(score)
            else:
                time_buckets['night'].append(score)
        
        averages = {
            time: statistics.mean(scores) if scores else 0
            for time, scores in time_buckets.items()
        }
        
        best_time = max(averages, key=averages.get)
        
        return {
            'averages': averages,
            'best_time': best_time,
            'best_time_avg_score': round(averages[best_time], 2)
        }
    
    def _analyze_session_length(self, activities: List) -> Dict[str, Any]:
        """Analyze optimal session length"""
        sessions = {}
        current_session = []
        last_time = None
        
        for activity in sorted(activities, key=lambda x: x.completed_at):
            if last_time and (activity.completed_at - last_time).seconds > 3600:
                # New session (gap > 1 hour)
                if current_session:
                    session_time = sum(a.time_spent_seconds or 0 for a in current_session)
                    avg_score = statistics.mean(a.percentage or 0 for a in current_session)
                    sessions[session_time] = avg_score
                current_session = []
            
            current_session.append(activity)
            last_time = activity.completed_at
        
        if not sessions:
            return {'message': 'Insufficient session data'}
        
        # Find optimal session length
        optimal_length = max(sessions, key=sessions.get)
        
        return {
            'optimal_length_minutes': round(optimal_length / 60, 1),
            'optimal_length_avg_score': round(sessions[optimal_length], 2),
            'total_sessions_analyzed': len(sessions)
        }
    
    def _analyze_activity_preferences(self, activities: List) -> Dict[str, Any]:
        """Analyze which activity types user performs best in"""
        type_performance = {}
        
        for activity in activities:
            activity_type = activity.activity_type
            score = activity.percentage or 0
            
            if activity_type not in type_performance:
                type_performance[activity_type] = []
            type_performance[activity_type].append(score)
        
        averages = {
            atype: {
                'avg_score': round(statistics.mean(scores), 2),
                'count': len(scores)
            }
            for atype, scores in type_performance.items()
        }
        
        best_type = max(averages, key=lambda x: averages[x]['avg_score'])
        
        return {
            'by_type': averages,
            'best_performing_type': best_type,
            'best_type_avg_score': averages[best_type]['avg_score']
        }
    
    def _identify_struggle_patterns(self, user_id: int) -> Dict[str, Any]:
        """Identify areas where user consistently struggles"""
        struggles = {
            'listening': [],
            'speaking': [],
            'reading': [],
            'writing': []
        }
        
        # Check each skill domain
        for domain in struggles.keys():
            trajectory = db.session.query(SkillTrajectory).filter_by(
                user_id=user_id,
                skill_domain=domain
            ).first()
            
            if trajectory and trajectory.current_level < 60:
                struggles[domain].append({
                    'current_level': trajectory.current_level,
                    'mastery_status': trajectory.mastery_status,
                    'focus_areas': trajectory.focus_areas or []
                })
        
        return struggles
    
    def _identify_breakthroughs(self, activities: List) -> List[Dict[str, Any]]:
        """Identify significant performance breakthroughs"""
        breakthroughs = []
        
        for i in range(1, len(activities)):
            prev_score = activities[i-1].percentage or 0
            curr_score = activities[i].percentage or 0
            
            # Breakthrough is 20+ point improvement
            if curr_score - prev_score >= 20:
                breakthroughs.append({
                    'date': activities[i].completed_at.isoformat(),
                    'activity_type': activities[i].activity_type,
                    'improvement': round(curr_score - prev_score, 2),
                    'score': curr_score
                })
        
        return breakthroughs
    
    def _generate_pattern_recommendations(
        self,
        time_patterns: Dict,
        session_patterns: Dict,
        activity_preferences: Dict
    ) -> List[str]:
        """Generate recommendations based on identified patterns"""
        recommendations = []
        
        if time_patterns.get('best_time'):
            recommendations.append(
                f"Practice during {time_patterns['best_time']} for best results "
                f"(avg score: {time_patterns['best_time_avg_score']}%)"
            )
        
        if session_patterns.get('optimal_length_minutes'):
            recommendations.append(
                f"Aim for {session_patterns['optimal_length_minutes']}-minute sessions"
            )
        
        if activity_preferences.get('best_performing_type'):
            recommendations.append(
                f"Continue focusing on {activity_preferences['best_performing_type']} activities"
            )
        
        return recommendations
    
    def _generate_mastery_recommendations(
        self,
        current_level: float,
        improvement_rate: float,
        practice_frequency: float
    ) -> List[str]:
        """Generate recommendations for achieving mastery"""
        recommendations = []
        
        if current_level < 50:
            recommendations.append("Focus on fundamentals and consistent practice")
        elif current_level < 70:
            recommendations.append("Increase difficulty level to accelerate progress")
        else:
            recommendations.append("Focus on advanced scenarios and real-world applications")
        
        if improvement_rate < 1:
            recommendations.append("Try varying your practice activities for better results")
        
        if practice_frequency < 3:
            recommendations.append("Increase practice frequency to 3-4 times per week")
        
        return recommendations
