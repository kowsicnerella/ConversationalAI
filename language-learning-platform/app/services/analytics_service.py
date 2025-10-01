from app.models import (
    db, AssessmentQuestionResponse, ActivityQuestionResponse,
    UserAnalytics, LearningStreak, UserLearningTimeline,
    PerformanceTrend, AIGeneratedContent
)
from datetime import datetime, date, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for handling analytics data generation and management."""
    
    @staticmethod
    def record_assessment_question_response(assessment_id, user_id, question_data, user_answer, is_correct, time_spent=0, confidence_level=None):
        """Record a detailed question response for an assessment."""
        try:
            response = AssessmentQuestionResponse(
                assessment_id=assessment_id,
                user_id=user_id,
                question_id=question_data.get('id'),
                question_text=question_data.get('text'),
                question_type=question_data.get('type'),
                correct_answer=question_data.get('correct_answer'),
                user_answer=user_answer,
                is_correct=is_correct,
                time_spent_seconds=time_spent,
                confidence_level=confidence_level,
                difficulty_level=question_data.get('difficulty_level', 'beginner'),
                skill_area=question_data.get('skill_area'),
                points_earned=question_data.get('points', 0) if is_correct else 0,
                hints_used=question_data.get('hints_used', 0),
                attempts_before_correct=question_data.get('attempts', 1)
            )
            
            db.session.add(response)
            db.session.commit()
            
            # Update analytics
            AnalyticsService.update_skill_analytics(user_id, question_data.get('skill_area'), is_correct, time_spent)
            
            return response
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record assessment question response: {e}")
            return None
    
    @staticmethod
    def record_activity_question_response(activity_log_id, user_id, activity_id, question_index, question_data, user_answer, is_correct, time_spent=0, ai_feedback=None):
        """Record a detailed question response for an activity."""
        try:
            response = ActivityQuestionResponse(
                activity_log_id=activity_log_id,
                user_id=user_id,
                activity_id=activity_id,
                question_index=question_index,
                question_text=question_data.get('text'),
                question_type=question_data.get('type'),
                user_answer=user_answer,
                correct_answer=question_data.get('correct_answer'),
                is_correct=is_correct,
                time_spent_seconds=time_spent,
                hints_used=question_data.get('hints_used', 0),
                difficulty_level=question_data.get('difficulty_level', 'beginner'),
                skill_area=question_data.get('skill_area'),
                points_earned=question_data.get('points', 0) if is_correct else 0,
                ai_feedback=ai_feedback
            )
            
            db.session.add(response)
            db.session.commit()
            
            # Update analytics
            AnalyticsService.update_skill_analytics(user_id, question_data.get('skill_area'), is_correct, time_spent)
            
            return response
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record activity question response: {e}")
            return None
    
    @staticmethod
    def update_skill_analytics(user_id, skill_area, is_correct, time_spent=0):
        """Update skill-based analytics for a user."""
        if not skill_area:
            return
        
        try:
            today = date.today()
            
            # Update accuracy metric
            accuracy_value = 1.0 if is_correct else 0.0
            AnalyticsService._update_or_create_metric(
                user_id, 'accuracy', accuracy_value, today, skill_area=skill_area
            )
            
            # Update speed metric (questions per minute)
            if time_spent > 0:
                speed_value = 60.0 / time_spent  # questions per minute
                AnalyticsService._update_or_create_metric(
                    user_id, 'speed', speed_value, today, skill_area=skill_area
                )
            
        except Exception as e:
            logger.error(f"Failed to update skill analytics: {e}")
    
    @staticmethod
    def _update_or_create_metric(user_id, metric_type, metric_value, date_recorded, activity_type=None, skill_area=None):
        """Update or create a user analytics metric."""
        try:
            # Check if metric exists for today
            existing = UserAnalytics.query.filter_by(
                user_id=user_id,
                metric_type=metric_type,
                date_recorded=date_recorded,
                activity_type=activity_type,
                skill_area=skill_area
            ).first()
            
            if existing:
                # Calculate running average
                new_count = existing.session_count + 1
                existing.metric_value = ((existing.metric_value * existing.session_count) + metric_value) / new_count
                existing.session_count = new_count
            else:
                # Create new metric
                new_metric = UserAnalytics(
                    user_id=user_id,
                    metric_type=metric_type,
                    metric_value=metric_value,
                    date_recorded=date_recorded,
                    activity_type=activity_type,
                    skill_area=skill_area,
                    session_count=1
                )
                db.session.add(new_metric)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update metric: {e}")
    
    @staticmethod
    def update_learning_streaks(user_id, activity_type=None, skill_area=None):
        """Update learning streaks for a user."""
        try:
            today = date.today()
            
            # Update daily streak
            AnalyticsService._update_streak(user_id, 'daily', today, activity_type, skill_area)
            
            # Update activity-specific streak if provided
            if activity_type:
                AnalyticsService._update_streak(user_id, 'activity_specific', today, activity_type, skill_area)
            
            # Update skill-specific streak if provided
            if skill_area:
                AnalyticsService._update_streak(user_id, 'skill_specific', today, activity_type, skill_area)
            
        except Exception as e:
            logger.error(f"Failed to update learning streaks: {e}")
    
    @staticmethod
    def _update_streak(user_id, streak_type, activity_date, activity_type=None, skill_area=None):
        """Update a specific type of learning streak."""
        try:
            streak = LearningStreak.query.filter_by(
                user_id=user_id,
                streak_type=streak_type,
                activity_type=activity_type,
                skill_area=skill_area
            ).first()
            
            if not streak:
                # Create new streak
                streak = LearningStreak(
                    user_id=user_id,
                    streak_type=streak_type,
                    activity_type=activity_type,
                    skill_area=skill_area,
                    current_streak=1,
                    longest_streak=1,
                    last_activity_date=activity_date,
                    streak_start_date=activity_date
                )
                db.session.add(streak)
            else:
                # Update existing streak
                if streak.last_activity_date:
                    days_diff = (activity_date - streak.last_activity_date).days
                    
                    if days_diff == 1:
                        # Continue streak
                        streak.current_streak += 1
                        if streak.current_streak > streak.longest_streak:
                            streak.longest_streak = streak.current_streak
                    elif days_diff == 0:
                        # Same day activity - no change to streak
                        pass
                    else:
                        # Streak broken - restart
                        streak.current_streak = 1
                        streak.streak_start_date = activity_date
                else:
                    # First activity
                    streak.current_streak = 1
                    streak.streak_start_date = activity_date
                
                streak.last_activity_date = activity_date
                streak.updated_at = datetime.utcnow()
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update streak: {e}")
    
    @staticmethod
    def record_learning_event(user_id, event_type, event_subtype=None, event_data=None, 
                             related_id=None, related_type=None, proficiency_change=0.0, 
                             points_earned=0, skill_areas_affected=None, difficulty_level=None, 
                             performance_score=None, time_spent_minutes=None, milestone_achieved=None):
        """Record a learning event in the timeline."""
        try:
            timeline_event = UserLearningTimeline(
                user_id=user_id,
                event_type=event_type,
                event_subtype=event_subtype,
                event_data=event_data,
                related_id=related_id,
                related_type=related_type,
                proficiency_change=proficiency_change,
                points_earned=points_earned,
                skill_areas_affected=skill_areas_affected,
                difficulty_level=difficulty_level,
                performance_score=performance_score,
                time_spent_minutes=time_spent_minutes,
                milestone_achieved=milestone_achieved
            )
            
            db.session.add(timeline_event)
            db.session.commit()
            
            return timeline_event
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to record learning event: {e}")
            return None
    
    @staticmethod
    def track_ai_generated_content(content_type, content_data, generation_parameters=None, 
                                  difficulty_level=None, skill_area=None, created_by_service=None):
        """Track AI-generated content for reuse and quality analysis."""
        try:
            import hashlib
            import json
            
            # Generate content hash for deduplication
            content_str = json.dumps(content_data, sort_keys=True)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Check if content already exists
            existing = AIGeneratedContent.query.filter_by(content_hash=content_hash).first()
            
            if existing:
                # Increment usage count
                existing.usage_count += 1
                existing.last_used_at = datetime.utcnow()
            else:
                # Create new content record
                ai_content = AIGeneratedContent(
                    content_type=content_type,
                    content_data=content_data,
                    generation_parameters=generation_parameters,
                    content_hash=content_hash,
                    usage_count=1,
                    difficulty_level=difficulty_level,
                    skill_area=skill_area,
                    created_by_service=created_by_service,
                    last_used_at=datetime.utcnow()
                )
                db.session.add(ai_content)
            
            db.session.commit()
            return existing or ai_content
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to track AI generated content: {e}")
            return None
    
    @staticmethod
    def calculate_performance_trends(user_id, period='weekly'):
        """Calculate and store performance trends for a user."""
        try:
            today = date.today()
            
            if period == 'daily':
                period_start = today
                period_end = today
            elif period == 'weekly':
                period_start = today - timedelta(days=today.weekday())
                period_end = period_start + timedelta(days=6)
            elif period == 'monthly':
                period_start = today.replace(day=1)
                next_month = period_start.replace(month=period_start.month + 1) if period_start.month < 12 else period_start.replace(year=period_start.year + 1, month=1)
                period_end = next_month - timedelta(days=1)
            else:
                raise ValueError(f"Invalid period: {period}")
            
            # Check if trend already exists
            existing_trend = PerformanceTrend.query.filter_by(
                user_id=user_id,
                trend_period=period,
                period_start=period_start
            ).first()
            
            if existing_trend:
                trend = existing_trend
            else:
                trend = PerformanceTrend(
                    user_id=user_id,
                    trend_period=period,
                    period_start=period_start,
                    period_end=period_end
                )
                db.session.add(trend)
            
            # Calculate metrics from analytics data
            analytics_data = UserAnalytics.query.filter(
                UserAnalytics.user_id == user_id,
                UserAnalytics.date_recorded >= period_start,
                UserAnalytics.date_recorded <= period_end
            ).all()
            
            if analytics_data:
                # Calculate averages
                accuracy_values = [a.metric_value for a in analytics_data if a.metric_type == 'accuracy']
                speed_values = [a.metric_value for a in analytics_data if a.metric_type == 'speed']
                
                if accuracy_values:
                    trend.accuracy_rate = sum(accuracy_values) / len(accuracy_values)
                
                # Calculate skill-specific progress
                skill_data = {}
                for record in analytics_data:
                    if record.skill_area:
                        if record.skill_area not in skill_data:
                            skill_data[record.skill_area] = []
                        skill_data[record.skill_area].append(record.metric_value)
                
                # Update skill progress fields
                if 'vocabulary' in skill_data:
                    trend.vocabulary_progress = sum(skill_data['vocabulary']) / len(skill_data['vocabulary'])
                if 'grammar' in skill_data:
                    trend.grammar_progress = sum(skill_data['grammar']) / len(skill_data['grammar'])
                if 'reading' in skill_data:
                    trend.reading_progress = sum(skill_data['reading']) / len(skill_data['reading'])
                if 'conversation' in skill_data:
                    trend.conversation_progress = sum(skill_data['conversation']) / len(skill_data['conversation'])
            
            trend.updated_at = datetime.utcnow()
            db.session.commit()
            
            return trend
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to calculate performance trends: {e}")
            return None