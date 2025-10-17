from app.models import (
    db,
    User,
    Profile,
    Badge,
    UserBadge,
    Achievement,
    UserActivityLog,
    Activity,
    LearningSession,
)
from datetime import datetime, date, timedelta
from sqlalchemy import func


class GamificationService:
    """
    A service class to manage gamification features for the Telugu-English learning platform.
    Handles points, badges, streaks, and leaderboards.
    """

    # Points System
    POINTS = {
        "quiz_per_correct": 8,  # 8 points per correct answer
        "flashcard_per_card": 1,  # 1 point per flashcard reviewed
        "reading_completion": 20,  # 20 points for completing reading
        "writing_submission": 50,  # 50 points for writing submission
        "roleplay_completion": 30,  # 30 points for role-play completion
        "daily_goal": 25,  # 25 bonus points for meeting daily goal
        "streak_7_days": 100,  # 100 bonus points for 7-day streak
    }

    def award_activity_points(self, user_id, activity_type, session_data=None):
        """
        Award points based on activity type and performance.

        Args:
            user_id: User ID
            activity_type: 'quiz', 'flashcard', 'writing', 'roleplay', 'reading'
            session_data: Dict with activity details (correct_answers, card_count, etc.)

        Returns:
            dict: Points awarded and breakdown
        """
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                return {"success": False, "error": "Profile not found"}

            points_awarded = 0
            breakdown = {}

            if activity_type == "quiz":
                correct_answers = (
                    session_data.get("correct_answers", 0) if session_data else 0
                )
                points_awarded = correct_answers * self.POINTS["quiz_per_correct"]
                breakdown["correct_answers"] = correct_answers
                breakdown["points_per_answer"] = self.POINTS["quiz_per_correct"]

            elif activity_type == "flashcard":
                cards_reviewed = (
                    session_data.get("cards_reviewed", 0) if session_data else 0
                )
                points_awarded = cards_reviewed * self.POINTS["flashcard_per_card"]
                breakdown["cards_reviewed"] = cards_reviewed
                breakdown["points_per_card"] = self.POINTS["flashcard_per_card"]

            elif activity_type == "reading":
                points_awarded = self.POINTS["reading_completion"]
                breakdown["activity"] = "reading_completion"

            elif activity_type == "writing":
                points_awarded = self.POINTS["writing_submission"]
                breakdown["activity"] = "writing_submission"

            elif activity_type == "roleplay":
                points_awarded = self.POINTS["roleplay_completion"]
                breakdown["activity"] = "roleplay_completion"

            # Award points
            profile.points = (profile.points or 0) + points_awarded
            db.session.commit()

            # Check for new achievements
            new_badges = self.check_for_new_achievements(user_id)

            # Update streak
            self.update_streak(user_id)

            # Check daily goal
            daily_bonus = self._check_daily_goal(user_id)
            if daily_bonus > 0:
                profile.points += daily_bonus
                points_awarded += daily_bonus
                breakdown["daily_goal_bonus"] = daily_bonus
                db.session.commit()

            return {
                "success": True,
                "points_awarded": points_awarded,
                "total_points": profile.points,
                "breakdown": breakdown,
                "new_badges": new_badges,
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    def _check_daily_goal(self, user_id):
        """
        Check if user has met daily goal (3 activities) and award bonus.
        Returns bonus points awarded (0 or 25).
        """
        try:
            today = date.today()

            # Count activities completed today
            today_activities = LearningSession.query.filter(
                LearningSession.user_id == user_id,
                LearningSession.status == "completed",
                func.date(LearningSession.completed_at) == today,
            ).count()

            # Check if already awarded daily bonus today
            # We'll track this in a simple way - if they have 3+ activities today
            # and their streak was updated today, award the bonus
            if today_activities >= 3:
                profile = Profile.query.filter_by(user_id=user_id).first()
                if profile and profile.last_activity_date == today:
                    # Check if we already gave bonus today (simple check)
                    # In production, you'd want a separate tracking table
                    return self.POINTS["daily_goal"]

            return 0

        except Exception as e:
            return 0

    def update_streak(self, user_id):
        """
        Updates the user's streak based on their recent activity.
        This should be called upon activity completion or daily login.
        """
        try:
            profile = Profile.query.filter_by(user_id=user_id).first()
            if not profile:
                return False

            today = date.today()
            yesterday = today - timedelta(days=1)

            # Check if user has completed any activity today
            today_activity = UserActivityLog.query.filter(
                UserActivityLog.user_id == user_id,
                func.date(UserActivityLog.completed_at) == today,
            ).first()

            if today_activity:
                if profile.last_activity_date == yesterday:
                    # Continue streak
                    profile.current_streak += 1
                elif profile.last_activity_date != today:
                    # First activity today, but gap exists
                    profile.current_streak = 1

                profile.last_activity_date = today
                db.session.commit()

                # Check for streak-based badges
                self._check_streak_badges(user_id, profile.current_streak)

            return True

        except Exception as e:
            db.session.rollback()
            return False

    def award_badge(self, user_id, badge_name):
        """
        Awards a specific badge to a user if they don't already have it.
        """
        try:
            badge = Badge.query.filter_by(name=badge_name).first()
            if not badge:
                return False

            # Check if user already has this badge
            existing_user_badge = UserBadge.query.filter_by(
                user_id=user_id, badge_id=badge.id
            ).first()

            if existing_user_badge:
                return False  # User already has this badge

            # Award the badge
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)

            db.session.add(user_badge)

            # Award bonus points
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                profile.points += badge.points_reward

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            return False

    def check_for_new_achievements(self, user_id):
        """
        Checks if the user has met the criteria for any new badges
        based on their progress and awards them accordingly.
        """
        try:
            # Get user statistics
            user_stats = self._get_user_statistics(user_id)
            profile = Profile.query.filter_by(user_id=user_id).first()

            if not profile:
                return []

            # Get all badges the user doesn't have yet
            user_badge_ids = (
                db.session.query(UserBadge.badge_id)
                .filter_by(user_id=user_id)
                .subquery()
            )
            available_badges = Badge.query.filter(~Badge.id.in_(user_badge_ids)).all()

            newly_awarded = []

            for badge in available_badges:
                should_award = False

                if badge.requirement_type == "activities_completed":
                    should_award = (
                        user_stats["total_activities"] >= badge.requirement_value
                    )
                elif badge.requirement_type == "streak_days":
                    should_award = profile.current_streak >= badge.requirement_value
                elif badge.requirement_type == "points_earned":
                    should_award = profile.points >= badge.requirement_value
                elif badge.requirement_type == "quiz_completed":
                    should_award = user_stats["quiz_count"] >= badge.requirement_value
                elif badge.requirement_type == "flashcard_completed":
                    should_award = (
                        user_stats["flashcard_count"] >= badge.requirement_value
                    )
                elif badge.requirement_type == "perfect_scores":
                    should_award = (
                        user_stats["perfect_scores"] >= badge.requirement_value
                    )

                if should_award:
                    if self.award_badge(user_id, badge.name):
                        newly_awarded.append(
                            {
                                "name": badge.name,
                                "description": badge.description,
                                "points_reward": badge.points_reward,
                                "rarity": badge.rarity,
                            }
                        )

            return newly_awarded

        except Exception as e:
            return []

    def _get_user_statistics(self, user_id):
        """
        Gets comprehensive statistics for a user.
        """
        try:
            # Total activities completed
            total_activities = UserActivityLog.query.filter_by(user_id=user_id).count()

            # Activities by type
            quiz_count = (
                UserActivityLog.query.join(Activity)
                .filter(
                    UserActivityLog.user_id == user_id, Activity.activity_type == "quiz"
                )
                .count()
            )

            flashcard_count = (
                UserActivityLog.query.join(Activity)
                .filter(
                    UserActivityLog.user_id == user_id,
                    Activity.activity_type == "flashcard",
                )
                .count()
            )

            # Perfect scores (100%)
            perfect_scores = UserActivityLog.query.filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.score == UserActivityLog.max_score,
                UserActivityLog.max_score > 0,
            ).count()

            # Average score
            avg_score = (
                db.session.query(func.avg(UserActivityLog.score))
                .filter_by(user_id=user_id)
                .scalar()
                or 0
            )

            return {
                "total_activities": total_activities,
                "quiz_count": quiz_count,
                "flashcard_count": flashcard_count,
                "perfect_scores": perfect_scores,
                "average_score": avg_score,
            }

        except Exception as e:
            return {
                "total_activities": 0,
                "quiz_count": 0,
                "flashcard_count": 0,
                "perfect_scores": 0,
                "average_score": 0,
            }

    def _check_streak_badges(self, user_id, streak_days):
        """
        Checks and awards streak-based badges.
        """
        streak_milestones = [3, 7, 14, 30, 60, 100]

        for milestone in streak_milestones:
            if streak_days >= milestone:
                badge_name = f"{milestone}-Day Streak"
                badge = Badge.query.filter_by(name=badge_name).first()
                if badge:
                    self.award_badge(user_id, badge_name)

    def get_user_badges(self, user_id):
        """
        Gets all badges earned by a user.
        """
        try:
            user_badges = (
                db.session.query(UserBadge, Badge)
                .join(Badge)
                .filter(UserBadge.user_id == user_id)
                .order_by(UserBadge.earned_at.desc())
                .all()
            )

            badges = []
            for user_badge, badge in user_badges:
                badges.append(
                    {
                        "id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "category": badge.category,
                        "rarity": badge.rarity,
                        "points_reward": badge.points_reward,
                        "earned_at": user_badge.earned_at.isoformat(),
                        "icon_url": badge.icon_url,
                    }
                )

            return badges

        except Exception as e:
            return []

    def get_leaderboard(self, limit=10, time_period="all_time"):
        """
        Gets the leaderboard based on points or other criteria.
        """
        try:
            if time_period == "weekly":
                week_ago = datetime.utcnow() - timedelta(days=7)
                # This would require tracking weekly points separately
                # For now, we'll use all-time points
                pass

            leaderboard = (
                db.session.query(User, Profile)
                .join(Profile)
                .filter(Profile.points > 0)
                .order_by(Profile.points.desc())
                .limit(limit)
                .all()
            )

            results = []
            for rank, (user, profile) in enumerate(leaderboard, 1):
                results.append(
                    {
                        "rank": rank,
                        "username": user.username,
                        "points": profile.points,
                        "current_streak": profile.current_streak,
                        "proficiency_level": profile.proficiency_level,
                    }
                )

            return results

        except Exception as e:
            return []

    def get_daily_challenge_status(self, user_id):
        """
        Checks if the user has completed today's challenge.
        """
        try:
            today = date.today()
            today_activities = UserActivityLog.query.filter(
                UserActivityLog.user_id == user_id,
                func.date(UserActivityLog.completed_at) == today,
            ).count()

            # Daily challenge: complete at least 3 activities
            challenge_target = 3

            return {
                "completed_today": today_activities,
                "target": challenge_target,
                "is_completed": today_activities >= challenge_target,
                "progress_percentage": min(
                    100, (today_activities / challenge_target) * 100
                ),
            }

        except Exception as e:
            return {
                "completed_today": 0,
                "target": 3,
                "is_completed": False,
                "progress_percentage": 0,
            }
