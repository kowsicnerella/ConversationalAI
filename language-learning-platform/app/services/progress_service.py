
from app.models import db, User, Profile, UserActivityLog, LearningPath, Activity
from datetime import datetime, date
from sqlalchemy import func

class ProgressService:
    """
    A service class to manage user progress in the Telugu-English learning platform.
    """

    def update_user_activity_log(self, user_id, activity_id, score, max_score, user_response, time_spent_minutes=None, feedback_provided=None):
        """
        Updates the user's activity log upon completion of an activity.
        """
        try:
            # Check if user has already completed this activity
            existing_log = UserActivityLog.query.filter_by(
                user_id=user_id, 
                activity_id=activity_id
            ).order_by(UserActivityLog.attempt_number.desc()).first()
            
            attempt_number = 1
            if existing_log:
                attempt_number = existing_log.attempt_number + 1
            
            # Create new activity log entry
            activity_log = UserActivityLog(
                user_id=user_id,
                activity_id=activity_id,
                score=score,
                max_score=max_score,
                time_spent_minutes=time_spent_minutes,
                user_response=user_response,
                feedback_provided=feedback_provided,
                attempt_number=attempt_number,
                completed_at=datetime.utcnow()
            )
            
            db.session.add(activity_log)
            
            # Update user points and streak
            self._update_user_points_and_streak(user_id, activity_id, score, max_score)
            
            db.session.commit()
            return activity_log
            
        except Exception as e:
            db.session.rollback()
            raise e

    def _update_user_points_and_streak(self, user_id, activity_id, score, max_score):
        """
        Updates user points and daily streak.
        """
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return
        
        # Calculate points based on score
        activity = Activity.query.get(activity_id)
        if activity:
            # Award full points if score is 80% or above, proportional otherwise
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            if percentage >= 80:
                points_earned = activity.points_reward
            else:
                points_earned = int((percentage / 100) * activity.points_reward)
            
            profile.points += points_earned
        
        # Update streak
        today = date.today()
        if profile.last_activity_date:
            if profile.last_activity_date == today:
                # Already completed activity today, don't update streak
                pass
            elif profile.last_activity_date == date.fromordinal(today.toordinal() - 1):
                # Completed activity yesterday, increment streak
                profile.current_streak += 1
                profile.last_activity_date = today
            else:
                # Gap in activities, reset streak
                profile.current_streak = 1
                profile.last_activity_date = today
        else:
            # First activity ever
            profile.current_streak = 1
            profile.last_activity_date = today

    def get_learning_path_progress(self, user_id, path_id):
        """
        Calculates the completion percentage for a given learning path.
        """
        try:
            # Get all activities in the learning path
            activities = Activity.query.filter_by(path_id=path_id).all()
            if not activities:
                return {'completion_percentage': 0, 'completed_activities': 0, 'total_activities': 0}
            
            # Get completed activities by the user
            completed_activity_ids = db.session.query(UserActivityLog.activity_id).filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.activity_id.in_([a.id for a in activities])
            ).distinct().all()
            
            completed_count = len(completed_activity_ids)
            total_count = len(activities)
            completion_percentage = (completed_count / total_count) * 100 if total_count > 0 else 0
            
            # Update learning path completion percentage
            learning_path = LearningPath.query.get(path_id)
            if learning_path and learning_path.user_id == user_id:
                learning_path.completion_percentage = completion_percentage
                learning_path.is_completed = completion_percentage == 100
                db.session.commit()
            
            return {
                'completion_percentage': round(completion_percentage, 2),
                'completed_activities': completed_count,
                'total_activities': total_count,
                'is_completed': completion_percentage == 100
            }
            
        except Exception as e:
            return {'error': str(e)}

    def get_user_profile(self, user_id):
        """
        Fetches the user's profile information with statistics.
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.profile:
                return None
            
            profile = user.profile
            
            # Get additional statistics
            total_activities = UserActivityLog.query.filter_by(user_id=user_id).count()
            avg_score = db.session.query(func.avg(UserActivityLog.score)).filter_by(user_id=user_id).scalar() or 0
            total_time_spent = db.session.query(func.sum(UserActivityLog.time_spent_minutes)).filter_by(user_id=user_id).scalar() or 0
            
            return {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'native_language': profile.native_language,
                'target_language': profile.target_language,
                'proficiency_level': profile.proficiency_level,
                'current_streak': profile.current_streak,
                'points': profile.points,
                'last_activity_date': profile.last_activity_date.isoformat() if profile.last_activity_date else None,
                'total_activities_completed': total_activities,
                'average_score': round(avg_score, 2),
                'total_time_spent_minutes': total_time_spent,
                'member_since': user.created_at.isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}

    def get_activity_history(self, user_id, limit=50):
        """
        Fetches the user's recent activity history.
        """
        try:
            activity_logs = UserActivityLog.query.filter_by(user_id=user_id)\
                .join(Activity)\
                .order_by(UserActivityLog.completed_at.desc())\
                .limit(limit).all()
            
            history = []
            for log in activity_logs:
                history.append({
                    'id': log.id,
                    'activity_title': log.activity.title,
                    'activity_type': log.activity.activity_type,
                    'score': log.score,
                    'max_score': log.max_score,
                    'percentage': round((log.score / log.max_score) * 100, 2) if log.max_score > 0 else 0,
                    'time_spent_minutes': log.time_spent_minutes,
                    'completed_at': log.completed_at.isoformat(),
                    'attempt_number': log.attempt_number
                })
            
            return history
            
        except Exception as e:
            return {'error': str(e)}

    def get_user_learning_paths(self, user_id):
        """
        Fetches all learning paths for a user with their progress.
        """
        try:
            # Get user's enrolled learning paths through the many-to-many relationship
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            learning_paths = user.enrolled_paths.all()
            
            paths_with_progress = []
            for path in learning_paths:
                progress = self.get_learning_path_progress(user_id, path.id)
                paths_with_progress.append({
                    'id': path.id,
                    'title': path.title,
                    'description': path.description,
                    'difficulty_level': path.difficulty_level,
                    'is_active': path.is_active,
                    'is_completed': path.is_completed,
                    'completion_percentage': progress.get('completion_percentage', 0),
                    'completed_activities': progress.get('completed_activities', 0),
                    'total_activities': progress.get('total_activities', 0),
                    'created_at': path.created_at.isoformat()
                })
            
            return paths_with_progress
            
        except Exception as e:
            return {'error': str(e)}

    def create_learning_path(self, user_id, title, description, difficulty_level='beginner'):
        """
        Creates a new learning path for a user.
        """
        try:
            # Create the learning path
            learning_path = LearningPath(
                title=title,
                description=description,
                difficulty_level=difficulty_level
            )
            
            db.session.add(learning_path)
            db.session.flush()  # Get the ID without committing
            
            # Enroll the user in this learning path
            user = User.query.get(user_id)
            if user:
                user.enrolled_paths.append(learning_path)
            
            db.session.commit()
            
            return learning_path
            
        except Exception as e:
            db.session.rollback()
            raise e
