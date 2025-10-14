"""
Goal Achievement Service
Handles goal creation, progress tracking, milestone completion, and certificates
"""
from app.models import db
from app.models.goal import GoalType, AchievementGoal, Certificate, LevelProgression
from app.models.milestone import Milestone
from app.models.user import User
from app.models.gamification import Badge
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta
import uuid
import random

class GoalService:
    """Service for managing user goals and milestones"""
    
    # Predefined goal templates
    GOAL_TEMPLATES = {
        'basic_conversation': {
            'name': 'basic_conversation',
            'display_name': 'Basic Conversational English',
            'description': 'Master fundamental English conversation skills',
            'icon': 'Chat',
            'difficulty_level': 'beginner',
            'estimated_duration_days': 30,
            'criteria': {
                'activities_completed': 20,
                'vocabulary_learned': 100,
                'streak_days': 7,
                'assessment_score': 70
            },
            'points_reward': 500,
            'target_level': 'intermediate'
        },
        'workplace_english': {
            'name': 'workplace_english',
            'display_name': 'Workplace English Proficiency',
            'description': 'Develop professional English communication skills',
            'icon': 'BusinessCenter',
            'difficulty_level': 'intermediate',
            'estimated_duration_days': 90,
            'criteria': {
                'learning_path_completed': 'Business English',
                'activities_completed': 50,
                'professional_emails_written': 10,
                'role_play_scenarios': 15,
                'assessment_score': 80
            },
            'points_reward': 1500,
            'target_level': 'advanced'
        },
        'english_fluency': {
            'name': 'english_fluency',
            'display_name': 'English Fluency Mastery',
            'description': 'Achieve complete fluency in English',
            'icon': 'EmojiEvents',
            'difficulty_level': 'advanced',
            'estimated_duration_days': 180,
            'criteria': {
                'activities_completed': 100,
                'vocabulary_mastered': 500,
                'streak_days': 30,
                'assessment_score': 90,
                'all_paths_completed': True
            },
            'points_reward': 5000,
            'target_level': 'expert',
            'certificate': True
        }
    }

    @staticmethod
    def initialize_goal_types():
        """Initialize predefined goal types in database"""
        try:
            for template_key, template in GoalService.GOAL_TEMPLATES.items():
                existing = GoalType.query.filter_by(name=template['name']).first()
                if not existing:
                    goal_type = GoalType(
                        name=template['name'],
                        display_name=template['display_name'],
                        description=template['description'],
                        icon=template['icon'],
                        difficulty_level=template['difficulty_level'],
                        estimated_duration_days=template['estimated_duration_days'],
                        criteria=template['criteria'],
                        points_reward=template['points_reward']
                    )
                    db.session.add(goal_type)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def get_available_goals(user_id):
        """Get all available goal types with user's progress"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            all_goal_types = GoalType.query.filter_by(is_active=True).all()
            user_active_goals = AchievementGoal.query.filter_by(
                user_id=user_id,
                status='active'
            ).all()
            
            active_goal_ids = [g.goal_type_id for g in user_active_goals if g.goal_type_id]
            
            available_goals = []
            for goal_type in all_goal_types:
                goal_dict = goal_type.to_dict()
                goal_dict['is_active'] = goal_type.id in active_goal_ids
                goal_dict['is_recommended'] = GoalService._is_recommended_for_user(user, goal_type)
                available_goals.append(goal_dict)
            
            return available_goals
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def _is_recommended_for_user(user, goal_type):
        """Determine if a goal is recommended for the user"""
        user_level = user.current_level or 'beginner'
        
        # Recommend goals matching or slightly above user's level
        level_progression = {
            'beginner': ['beginner', 'intermediate'],
            'intermediate': ['intermediate', 'advanced'],
            'advanced': ['advanced']
        }
        
        return goal_type.difficulty_level in level_progression.get(user_level, ['beginner'])

    @staticmethod
    def create_goal(user_id, goal_data):
        """Create a new goal for user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Check if using a template or custom goal
            goal_type_id = goal_data.get('goal_type_id')
            is_custom = goal_data.get('is_custom', False)
            
            if goal_type_id and not is_custom:
                goal_type = GoalType.query.get(goal_type_id)
                if not goal_type:
                    return {'error': 'Goal type not found'}
                
                criteria = goal_type.criteria
                title = goal_type.display_name
                description = goal_type.description
            else:
                # Custom goal
                criteria = goal_data.get('criteria', {})
                title = goal_data.get('title')
                description = goal_data.get('description')
                goal_type_id = None
            
            # Calculate target date
            duration_days = goal_data.get('duration_days', 30)
            target_date = datetime.utcnow() + timedelta(days=duration_days)
            
            # Create the goal
            user_goal = AchievementGoal(
                user_id=user_id,
                goal_type_id=goal_type_id,
                title=title,
                description=description,
                is_custom=is_custom,
                target_date=target_date,
                criteria=criteria,
                current_progress=GoalService._initialize_progress(criteria)
            )
            
            db.session.add(user_goal)
            db.session.commit()
            
            # Create milestones for the goal
            GoalService._create_milestones(user_id, user_goal.id, criteria)
            
            # Send notification
            NotificationService.create_notification(
                user_id=user_id,
                type_name='new_goal_set',
                title='New Goal Set!',
                message=f'You\'ve set a new goal: {title}',
                priority='normal'
            )
            
            return user_goal.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def _initialize_progress(criteria):
        """Initialize progress tracking based on criteria"""
        progress = {}
        for key in criteria.keys():
            progress[key] = 0
        return progress

    @staticmethod
    def _create_milestones(user_id, goal_id, criteria):
        """Create milestones for a goal based on criteria"""
        try:
            milestone_order = 1
            
            for criterion_type, target_value in criteria.items():
                # Create milestone for each criterion
                if criterion_type == 'activities_completed':
                    milestone = Milestone(
                        user_id=user_id,
                        user_goal_id=goal_id,
                        title=f'Complete {target_value} Activities',
                        description=f'Complete {target_value} learning activities',
                        icon='Assignment',
                        order_index=milestone_order,
                        criteria_type='activities',
                        criteria_value=target_value,
                        points_reward=target_value * 5
                    )
                elif criterion_type == 'vocabulary_learned' or criterion_type == 'vocabulary_mastered':
                    milestone = Milestone(
                        user_id=user_id,
                        user_goal_id=goal_id,
                        title=f'Learn {target_value} Words',
                        description=f'Master {target_value} vocabulary words',
                        icon='MenuBook',
                        order_index=milestone_order,
                        criteria_type='vocabulary',
                        criteria_value=target_value,
                        points_reward=target_value * 2
                    )
                elif criterion_type == 'streak_days':
                    milestone = Milestone(
                        user_id=user_id,
                        user_goal_id=goal_id,
                        title=f'Maintain {target_value}-Day Streak',
                        description=f'Practice for {target_value} consecutive days',
                        icon='Whatshot',
                        order_index=milestone_order,
                        criteria_type='streak',
                        criteria_value=target_value,
                        points_reward=target_value * 10
                    )
                elif criterion_type == 'assessment_score':
                    milestone = Milestone(
                        user_id=user_id,
                        user_goal_id=goal_id,
                        title=f'Score {target_value}% on Assessment',
                        description=f'Achieve {target_value}% or higher on final assessment',
                        icon='School',
                        order_index=milestone_order,
                        criteria_type='assessment',
                        criteria_value=target_value,
                        points_reward=500
                    )
                else:
                    continue
                
                db.session.add(milestone)
                milestone_order += 1
            
            # Update goal's milestone total
            goal = AchievementGoal.query.get(goal_id)
            if goal:
                goal.milestones_total = milestone_order - 1
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating milestones: {str(e)}")

    @staticmethod
    def update_goal_progress(user_id, progress_data):
        """Update progress for all active goals based on user activity"""
        try:
            active_goals = AchievementGoal.query.filter_by(
                user_id=user_id,
                status='active'
            ).all()
            
            for goal in active_goals:
                updated = False
                current_progress = goal.current_progress or {}
                
                # Update each criterion
                for key, value in progress_data.items():
                    if key in goal.criteria:
                        current_progress[key] = value
                        updated = True
                
                if updated:
                    goal.current_progress = current_progress
                    goal.progress_percentage = GoalService._calculate_progress_percentage(
                        goal.criteria,
                        current_progress
                    )
                    goal.updated_at = datetime.utcnow()
                    
                    # Update milestones
                    GoalService._update_milestones(goal, progress_data)
                    
                    # Check if goal is completed
                    if goal.progress_percentage >= 100:
                        GoalService.complete_goal(goal.id)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def _calculate_progress_percentage(criteria, current_progress):
        """Calculate overall progress percentage"""
        if not criteria:
            return 0.0
        
        total_items = len(criteria)
        completed_items = 0
        
        for key, target_value in criteria.items():
            current_value = current_progress.get(key, 0)
            
            if isinstance(target_value, bool):
                if current_value:
                    completed_items += 1
            elif isinstance(target_value, (int, float)):
                if current_value >= target_value:
                    completed_items += 1
            elif isinstance(target_value, str):
                if current_value == target_value:
                    completed_items += 1
        
        return (completed_items / total_items * 100) if total_items > 0 else 0.0

    @staticmethod
    def _update_milestones(goal, progress_data):
        """Update milestone progress"""
        try:
            milestones = Milestone.query.filter_by(
                user_goal_id=goal.id,
                is_completed=False
            ).all()
            
            for milestone in milestones:
                criterion_key = GoalService._get_criterion_key_for_type(milestone.criteria_type)
                if criterion_key in progress_data:
                    milestone.current_value = progress_data[criterion_key]
                    
                    # Check if milestone is completed
                    if milestone.current_value >= milestone.criteria_value:
                        milestone.is_completed = True
                        milestone.completed_at = datetime.utcnow()
                        goal.milestones_completed += 1
                        
                        # Award points
                        user = User.query.get(goal.user_id)
                        if user and user.profile and milestone.points_reward:
                            user.profile.points = (user.profile.points or 0) + milestone.points_reward
                        
                        # Send notification
                        NotificationService.create_notification(
                            user_id=goal.user_id,
                            type_name='milestone_achieved',
                            title='Milestone Achieved!',
                            message=f'You completed: {milestone.title}',
                            priority='high'
                        )
        except Exception as e:
            print(f"Error updating milestones: {str(e)}")

    @staticmethod
    def _get_criterion_key_for_type(criteria_type):
        """Map milestone criteria type to goal criterion key"""
        mapping = {
            'activities': 'activities_completed',
            'vocabulary': 'vocabulary_learned',
            'streak': 'streak_days',
            'assessment': 'assessment_score'
        }
        return mapping.get(criteria_type, criteria_type)

    @staticmethod
    def complete_goal(goal_id):
        """Mark goal as completed and award rewards"""
        try:
            goal = AchievementGoal.query.get(goal_id)
            if not goal or goal.status == 'completed':
                return {'error': 'Goal not found or already completed'}
            
            user = User.query.get(goal.user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Update goal status
            goal.status = 'completed'
            goal.completed_at = datetime.utcnow()
            goal.progress_percentage = 100.0
            
            # Award points
            if goal.goal_type and goal.goal_type.points_reward:
                goal.points_earned = goal.goal_type.points_reward
                if user.profile:
                    user.profile.points = (user.profile.points or 0) + goal.points_earned
            
            # Check for level progression
            goal_template = GoalService.GOAL_TEMPLATES.get(goal.goal_type.name if goal.goal_type else None)
            if goal_template and 'target_level' in goal_template:
                target_level = goal_template['target_level']
                if target_level != user.current_level:
                    GoalService._level_up(user.id, target_level, 'goal_completion', goal.id)
            
            # Generate certificate if applicable
            if goal_template and goal_template.get('certificate'):
                certificate = GoalService._generate_certificate(user.id, goal.id)
                if certificate and not isinstance(certificate, dict):
                    goal.certificate_url = certificate.pdf_url
            
            db.session.commit()
            
            # Send celebration notification
            NotificationService.create_notification(
                user_id=user.id,
                type_name='achievement_unlocked',
                title='🎉 Goal Completed!',
                message=f'Congratulations! You completed: {goal.title}',
                priority='urgent'
            )
            
            # Suggest next goal
            next_goal = GoalService._suggest_next_goal(user)
            
            return {
                'goal': goal.to_dict(),
                'next_goal_suggestion': next_goal,
                'celebration': True
            }
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def _level_up(user_id, new_level, trigger_type, trigger_id):
        """Process level progression"""
        try:
            user = User.query.get(user_id)
            if not user:
                return
            
            old_level = user.current_level or 'beginner'
            
            # Create progression record
            level_number = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}.get(new_level, 1)
            
            progression = LevelProgression(
                user_id=user_id,
                from_level=old_level,
                to_level=new_level,
                level_number=level_number,
                trigger_type=trigger_type,
                trigger_id=trigger_id,
                requirements_met={'goal_completion': True}
            )
            
            db.session.add(progression)
            
            # Update user level
            user.current_level = new_level
            
            # Send notification
            NotificationService.create_notification(
                user_id=user_id,
                type_name='level_up',
                title=f'🚀 Level Up!',
                message=f'You\'ve advanced from {old_level.title()} to {new_level.title()}!',
                priority='urgent'
            )
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error in level up: {str(e)}")

    @staticmethod
    def _generate_certificate(user_id, goal_id):
        """Generate completion certificate"""
        try:
            user = User.query.get(user_id)
            goal = AchievementGoal.query.get(goal_id)
            
            if not user or not goal:
                return {'error': 'User or goal not found'}
            
            # Generate unique certificate number
            cert_number = f"CERT-{user_id}-{goal_id}-{uuid.uuid4().hex[:8].upper()}"
            
            certificate = Certificate(
                user_id=user_id,
                goal_id=goal_id,
                certificate_type='completion',
                title=f'Certificate of Completion - {goal.title}',
                description=f'This certifies that {user.username} has successfully completed the {goal.title} goal',
                certificate_number=cert_number,
                level_achieved=goal.goal_type.difficulty_level if goal.goal_type else 'beginner',
                skills_mastered=list(goal.criteria.keys()) if goal.criteria else [],
                verification_url=f'/api/goals/certificates/verify/{cert_number}'
            )
            
            db.session.add(certificate)
            db.session.commit()
            
            # TODO: Generate actual PDF certificate
            certificate.pdf_url = f'/api/goals/certificates/{certificate.id}/download'
            certificate.thumbnail_url = f'/api/goals/certificates/{certificate.id}/thumbnail'
            db.session.commit()
            
            return certificate
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}

    @staticmethod
    def _suggest_next_goal(user):
        """Suggest next goal based on user's completed goals"""
        try:
            level_progression = {
                'beginner': 'basic_conversation',
                'intermediate': 'workplace_english',
                'advanced': 'english_fluency'
            }
            
            user_level = user.current_level or 'beginner'
            next_goal_name = level_progression.get(user_level)
            
            if next_goal_name:
                goal_type = GoalType.query.filter_by(name=next_goal_name).first()
                if goal_type:
                    return goal_type.to_dict()
            
            return None
        except Exception as e:
            print(f"Error suggesting next goal: {str(e)}")
            return None

    @staticmethod
    def get_user_goals(user_id, status=None):
        """Get user's goals with optional status filter"""
        try:
            query = AchievementGoal.query.filter_by(user_id=user_id)
            
            if status:
                query = query.filter_by(status=status)
            
            goals = query.order_by(AchievementGoal.created_at.desc()).all()
            return [goal.to_dict() for goal in goals]
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_goal_detail(goal_id, include_milestones=True):
        """Get detailed goal information"""
        try:
            goal = AchievementGoal.query.get(goal_id)
            if not goal:
                return {'error': 'Goal not found'}
            
            goal_dict = goal.to_dict()
            
            if include_milestones:
                milestones = Milestone.query.filter_by(user_goal_id=goal_id)\
                    .order_by(Milestone.order_index).all()
                goal_dict['milestones'] = [m.to_dict() for m in milestones]
            
            return goal_dict
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_user_certificates(user_id):
        """Get all user certificates"""
        try:
            certificates = Certificate.query.filter_by(user_id=user_id)\
                .order_by(Certificate.issued_date.desc()).all()
            return [cert.to_dict() for cert in certificates]
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def get_level_progression_history(user_id):
        """Get user's level progression history"""
        try:
            progressions = LevelProgression.query.filter_by(user_id=user_id)\
                .order_by(LevelProgression.achieved_at.desc()).all()
            return [prog.to_dict() for prog in progressions]
        except Exception as e:
            return {'error': str(e)}
