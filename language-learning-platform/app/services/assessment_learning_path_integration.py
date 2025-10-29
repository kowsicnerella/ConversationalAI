"""
Assessment-Learning Path Integration Service

Connects the Intelligent Assessment System with Learning Paths to provide:
- Automated learning path recommendations based on assessment results
- Skill-based path matching
- Progress-aware path suggestions
- Personalized learning journey creation
"""

from app.models.user import db
from app.models.intelligent_assessment import (
    Assessment,
    UserAssessmentAttempt,
    AssessmentResult,
    SkillDiagnostic
)
from app.models.course import LearningPath
from app.models.chapter import Chapter
from app.models.enrollment import UserEnrollment
from app.services.intelligent_assessment_service import IntelligentAssessmentEngine
from sqlalchemy import and_, or_
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AssessmentLearningPathIntegration:
    """Service for integrating assessments with learning paths"""

    @staticmethod
    def recommend_paths_from_assessment(user_id, attempt_id):
        """
        Generate learning path recommendations based on assessment results.
        
        Args:
            user_id: User ID
            attempt_id: Assessment attempt ID
            
        Returns:
            List of recommended learning paths with reasons and priorities
        """
        # Get assessment attempt and results
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return []
            
        result = AssessmentResult.query.filter_by(attempt_id=attempt_id).first()
        if not result:
            return []
            
        # Get skill diagnostics
        diagnostics = SkillDiagnostic.query.filter_by(attempt_id=attempt_id).all()
        
        # Identify weak skills that need improvement
        weak_skills = []
        strong_skills = []
        
        for diag in diagnostics:
            if diag.mastery_level in ['needs_work', 'developing'] or diag.score < 0.6:
                weak_skills.append({
                    'name': diag.skill_name,
                    'score': diag.score,
                    'priority': 'high' if diag.score < 0.4 else 'medium',
                    'sub_skills': diag.sub_skills or []
                })
            elif diag.mastery_level == 'mastered' or diag.score >= 0.8:
                strong_skills.append(diag.skill_name)
        
        # Get user's proficiency level from theta
        proficiency_level = AssessmentLearningPathIntegration._theta_to_proficiency(
            attempt.final_theta
        )
        
        recommendations = []
        
        # Find paths matching weak skills
        for skill in weak_skills:
            paths = AssessmentLearningPathIntegration._find_paths_for_skill(
                skill['name'],
                proficiency_level,
                skill['priority']
            )
            
            for path in paths:
                # Check if already recommended
                if not any(r['path_id'] == path['id'] for r in recommendations):
                    recommendations.append({
                        'path_id': path['id'],
                        'path_title': path['title'],
                        'path_description': path['description'],
                        'difficulty_level': path['difficulty_level'],
                        'category': path['category'],
                        'estimated_duration_hours': path['estimated_duration_hours'],
                        'target_skills': [skill['name']],
                        'priority': skill['priority'],
                        'reason': f"To improve {skill['name']} (current: {skill['score']*100:.0f}%)",
                        'match_score': AssessmentLearningPathIntegration._calculate_match_score(
                            path, skill, proficiency_level
                        )
                    })
                else:
                    # Update existing recommendation
                    rec = next(r for r in recommendations if r['path_id'] == path['id'])
                    rec['target_skills'].append(skill['name'])
                    rec['reason'] += f", {skill['name']}"
        
        # Sort by priority and match score
        recommendations.sort(
            key=lambda x: (
                0 if x['priority'] == 'high' else 1 if x['priority'] == 'medium' else 2,
                -x['match_score']
            )
        )
        
        # Store recommendations in assessment result
        result.recommended_learning_paths = [
            {
                'path_id': rec['path_id'],
                'title': rec['path_title'],
                'priority': rec['priority'],
                'reason': rec['reason'],
                'match_score': rec['match_score']
            }
            for rec in recommendations[:10]  # Top 10 recommendations
        ]
        db.session.commit()
        
        return recommendations[:5]  # Return top 5 for immediate display
    
    @staticmethod
    def _theta_to_proficiency(theta):
        """Convert theta value to proficiency level"""
        if theta < -1.0:
            return 'beginner'
        elif theta < 0.0:
            return 'elementary'
        elif theta < 1.0:
            return 'intermediate'
        elif theta < 2.0:
            return 'advanced'
        else:
            return 'expert'
    
    @staticmethod
    def _find_paths_for_skill(skill_name, proficiency_level, priority):
        """
        Find learning paths that teach a specific skill at the appropriate level.
        
        Args:
            skill_name: Name of skill to find paths for
            proficiency_level: User's current proficiency level
            priority: Priority (high, medium, low)
            
        Returns:
            List of matching learning paths
        """
        # Map proficiency to path difficulty
        difficulty_map = {
            'beginner': ['beginner', 'elementary'],
            'elementary': ['beginner', 'elementary', 'intermediate'],
            'intermediate': ['elementary', 'intermediate'],
            'advanced': ['intermediate', 'advanced'],
            'expert': ['advanced']
        }
        
        target_difficulties = difficulty_map.get(proficiency_level, ['intermediate'])
        
        # Search for paths
        # 1. Exact match in learning objectives
        paths = LearningPath.query.filter(
            and_(
                LearningPath.is_active == True,
                LearningPath.is_adaptive == False,
                LearningPath.difficulty_level.in_(target_difficulties)
            )
        ).all()
        
        matching_paths = []
        skill_lower = skill_name.lower()
        
        for path in paths:
            # Check if skill appears in learning objectives
            objectives = path.learning_objectives or []
            objectives_str = ' '.join(objectives).lower()
            
            # Check title and description
            title_desc = f"{path.title} {path.description}".lower()
            
            if skill_lower in objectives_str or skill_lower in title_desc:
                matching_paths.append({
                    'id': path.id,
                    'title': path.title,
                    'description': path.description,
                    'difficulty_level': path.difficulty_level,
                    'category': path.category,
                    'estimated_duration_hours': path.estimated_duration_hours,
                    'learning_objectives': objectives,
                    'success_rate': path.success_rate or 0.75
                })
        
        return matching_paths
    
    @staticmethod
    def _calculate_match_score(path, skill, proficiency_level):
        """
        Calculate how well a path matches the user's needs.
        
        Returns:
            Float between 0 and 1 (higher is better match)
        """
        score = 0.0
        
        # Base score from success rate
        score += (path.get('success_rate', 0.75) * 0.3)
        
        # Bonus for matching difficulty level
        if path['difficulty_level'] == proficiency_level:
            score += 0.3
        
        # Bonus for shorter duration (faster progress)
        duration = path.get('estimated_duration_hours', 10)
        if duration <= 5:
            score += 0.2
        elif duration <= 10:
            score += 0.1
        
        # Bonus for skill match in objectives
        objectives_str = ' '.join(path.get('learning_objectives', [])).lower()
        if skill['name'].lower() in objectives_str:
            score += 0.2
        
        return min(score, 1.0)
    
    @staticmethod
    def suggest_next_assessment(user_id, current_path_id):
        """
        Suggest assessments to take based on current learning path progress.
        
        Args:
            user_id: User ID
            current_path_id: Current learning path ID
            
        Returns:
            List of suggested assessments with reasons
        """
        # Get path details
        path = LearningPath.query.get(current_path_id)
        if not path:
            return []
        
        # Get user's enrollment and progress
        enrollment = UserEnrollment.query.filter_by(
            user_id=user_id,
            learning_path_id=current_path_id
        ).first()
        
        if not enrollment:
            return []
        
        suggestions = []
        
        # Suggest placement test if just started
        if enrollment.completion_percentage < 10:
            placement_tests = Assessment.query.filter_by(
                assessment_type='placement',
                is_active=True
            ).all()
            
            for test in placement_tests:
                suggestions.append({
                    'assessment_id': test.id,
                    'title': test.title,
                    'type': test.assessment_type,
                    'reason': 'Recommended to assess your starting level',
                    'priority': 'high',
                    'timing': 'now'
                })
        
        # Suggest progress test at milestones
        elif enrollment.completion_percentage in range(25, 35):
            progress_tests = Assessment.query.filter_by(
                assessment_type='progress',
                is_active=True
            ).all()
            
            for test in progress_tests[:2]:  # Top 2
                suggestions.append({
                    'assessment_id': test.id,
                    'title': test.title,
                    'type': test.assessment_type,
                    'reason': 'Track your progress at the 25% milestone',
                    'priority': 'medium',
                    'timing': 'soon'
                })
        
        elif enrollment.completion_percentage in range(50, 60):
            progress_tests = Assessment.query.filter_by(
                assessment_type='progress',
                is_active=True
            ).all()
            
            for test in progress_tests[:2]:
                suggestions.append({
                    'assessment_id': test.id,
                    'title': test.title,
                    'type': test.assessment_type,
                    'reason': 'Mid-path progress check at 50% completion',
                    'priority': 'high',
                    'timing': 'now'
                })
        
        # Suggest mastery test near completion
        elif enrollment.completion_percentage >= 75:
            mastery_tests = Assessment.query.filter_by(
                assessment_type='mastery',
                is_active=True
            ).all()
            
            for test in mastery_tests[:2]:
                suggestions.append({
                    'assessment_id': test.id,
                    'title': test.title,
                    'type': test.assessment_type,
                    'reason': 'Test your mastery before completing the path',
                    'priority': 'high',
                    'timing': 'now'
                })
        
        return suggestions[:3]  # Return top 3 suggestions
    
    @staticmethod
    def create_personalized_path_from_assessment(user_id, attempt_id):
        """
        Create a personalized adaptive learning path based on assessment results.
        
        Args:
            user_id: User ID
            attempt_id: Assessment attempt ID
            
        Returns:
            Created learning path ID or None
        """
        # Get assessment results and diagnostics
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return None
        
        result = AssessmentResult.query.filter_by(attempt_id=attempt_id).first()
        diagnostics = SkillDiagnostic.query.filter_by(attempt_id=attempt_id).all()
        
        if not result or not diagnostics:
            return None
        
        # Extract weak skills for focus
        priority_skills = []
        for diag in diagnostics:
            if diag.score < 0.7:  # Below proficiency
                priority_skills.append({
                    'skill_name': diag.skill_name,
                    'current_score': diag.score,
                    'target_score': 0.8,
                    'priority': 'high' if diag.score < 0.5 else 'medium',
                    'sub_skills': diag.sub_skills or [],
                    'improvement_strategies': diag.improvement_strategies or []
                })
        
        # Sort by priority and score (lowest first)
        priority_skills.sort(
            key=lambda x: (0 if x['priority'] == 'high' else 1, x['current_score'])
        )
        
        # Create personalized path
        proficiency_level = AssessmentLearningPathIntegration._theta_to_proficiency(
            attempt.final_theta
        )
        
        path = LearningPath(
            title=f"Personalized Learning Path for {attempt.user.username}",
            description=f"Custom path created based on assessment results (Theta: {attempt.final_theta:.2f})",
            category='personalized',
            difficulty_level=proficiency_level,
            estimated_duration_hours=len(priority_skills) * 5,  # 5 hours per skill
            learning_objectives=[s['skill_name'] for s in priority_skills],
            is_active=True,
            is_adaptive=True,
            user_id=user_id,
            assessment_id=attempt.assessment_id,
            path_data={
                'source_attempt_id': attempt_id,
                'creation_date': datetime.utcnow().isoformat(),
                'priority_skills': priority_skills,
                'initial_theta': attempt.final_theta,
                'target_theta': attempt.final_theta + 1.0  # Aim to improve by 1 theta
            },
            priority_skills=[s['skill_name'] for s in priority_skills],
            mastery_requirements={
                'min_theta': attempt.final_theta + 0.5,
                'min_score_per_skill': 0.8,
                'completion_criteria': 'all_skills_above_threshold'
            },
            generation_source='assessment',
            generation_metadata={
                'assessment_id': attempt.assessment_id,
                'attempt_id': attempt_id,
                'theta': attempt.final_theta,
                'score': result.score,
                'weak_skills_count': len(priority_skills)
            }
        )
        
        db.session.add(path)
        db.session.commit()
        
        # Auto-enroll user
        enrollment = UserEnrollment(
            user_id=user_id,
            learning_path_id=path.id,
            enrolled_at=datetime.utcnow(),
            completion_percentage=0.0,
            is_completed=False
        )
        db.session.add(enrollment)
        db.session.commit()
        
        logger.info(f"Created personalized path {path.id} for user {user_id} from attempt {attempt_id}")
        
        return path.id
    
    @staticmethod
    def update_path_from_progress_assessment(user_id, path_id, attempt_id):
        """
        Update an adaptive learning path based on progress assessment results.
        
        Args:
            user_id: User ID
            path_id: Learning path ID
            attempt_id: Assessment attempt ID
            
        Returns:
            Updated path data or None
        """
        path = LearningPath.query.get(path_id)
        if not path or not path.is_adaptive or path.user_id != user_id:
            return None
        
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return None
        
        # Get new diagnostics
        diagnostics = SkillDiagnostic.query.filter_by(attempt_id=attempt_id).all()
        
        # Compare with original priority skills
        path_data = path.path_data or {}
        original_skills = path_data.get('priority_skills', [])
        
        # Track improvements
        improvements = []
        still_weak = []
        
        for orig_skill in original_skills:
            # Find corresponding diagnostic
            diag = next(
                (d for d in diagnostics if d.skill_name == orig_skill['skill_name']),
                None
            )
            
            if diag:
                improvement = diag.score - orig_skill['current_score']
                
                if diag.score >= 0.8:
                    # Skill mastered
                    improvements.append({
                        'skill': diag.skill_name,
                        'improvement': improvement,
                        'status': 'mastered'
                    })
                elif improvement > 0.1:
                    # Good progress
                    improvements.append({
                        'skill': diag.skill_name,
                        'improvement': improvement,
                        'status': 'improving'
                    })
                else:
                    # Still needs work
                    still_weak.append({
                        'skill_name': diag.skill_name,
                        'current_score': diag.score,
                        'target_score': 0.8,
                        'priority': 'high'
                    })
        
        # Update path data
        path_data['adaptation_history'] = path_data.get('adaptation_history', [])
        path_data['adaptation_history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'attempt_id': attempt_id,
            'theta': attempt.final_theta,
            'improvements': improvements,
            'remaining_weak_skills': len(still_weak)
        })
        
        # Update priority skills to focus on remaining weak areas
        path.priority_skills = [s['skill_name'] for s in still_weak]
        path.path_data = path_data
        
        # Update enrollment progress
        enrollment = UserEnrollment.query.filter_by(
            user_id=user_id,
            learning_path_id=path_id
        ).first()
        
        if enrollment:
            # Calculate new completion based on skill mastery
            mastered_count = len([i for i in improvements if i['status'] == 'mastered'])
            total_skills = len(original_skills)
            if total_skills > 0:
                enrollment.completion_percentage = (mastered_count / total_skills) * 100
        
        db.session.commit()
        
        return {
            'path_id': path_id,
            'improvements': improvements,
            'remaining_skills': still_weak,
            'completion_percentage': enrollment.completion_percentage if enrollment else 0,
            'recommended_focus': still_weak[:3] if still_weak else []
        }
