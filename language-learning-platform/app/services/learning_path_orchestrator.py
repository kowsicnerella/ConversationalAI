"""
Learning Path Orchestrator Service
Determines the next optimal learning activity for each user based on their progress,
performance, weak areas, and curriculum structure.
"""
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.models.user import User, Profile, db
from app.models.curriculum import (
    CurriculumLevel,
    LearningNode,
    UserLearningPathProgress,
    NodeCompletion
)
from app.models.activity import Activity, UserActivityLog
from app.models.course import LearningPath
from app.services.activity_generator_service import ActivityGeneratorService


class LearningPathOrchestrator:
    """
    Orchestrates the learning journey by determining the next best activity
    for each user based on multiple factors:
    1. Spaced repetition for vocabulary
    2. Weak area reinforcement
    3. Natural progression through learning nodes
    4. Mixed review and practice
    """
    
    def __init__(self):
        self.activity_generator = ActivityGeneratorService()
    
    def _save_generated_activity(self, user_id, progress, node, generated_content, profile):
        """
        Save generated activity to database for persistence and analytics.
        
        Args:
            user_id: User ID
            progress: UserLearningPathProgress object
            node: LearningNode object
            generated_content: Dict with AI-generated activity content
            profile: User Profile object
            
        Returns:
            Activity: Saved Activity database record with ID
        """
        try:
            # Get curriculum level info
            level = db.session.get(CurriculumLevel, node.curriculum_level_id)
            
            # Get or create learning path for user
            learning_path = LearningPath.query.filter_by(title='English for Telugu Speakers').first()
            if not learning_path:
                # Create default learning path if it doesn't exist
                learning_path = LearningPath(
                    title='English for Telugu Speakers',
                    description='Comprehensive English learning path tailored for Telugu native speakers',
                    category='general',
                    difficulty_level='beginner',
                    estimated_duration_hours=200,
                    is_active=True,
                    learning_objectives=['Master basic English communication', 'Build vocabulary', 'Understand grammar']
                )
                db.session.add(learning_path)
                db.session.flush()  # Get the ID
            
            # Create Activity record
            activity_record = Activity(
                learning_path_id=learning_path.id,
                activity_type=generated_content.get('activity_type', 'unknown'),
                title=generated_content.get('title', 'Untitled Activity'),
                description=generated_content.get('instructions', generated_content.get('description', '')),
                content=generated_content,  # Store full JSON content
                difficulty_level=level.cefr_level if level else 'A1',
                order_in_path=progress.nodes_completed if progress else 0,
                estimated_duration_minutes=generated_content.get('estimated_time', 15),
                points_reward=generated_content.get('points_reward', 10),
                skill_area=node.skill_domain,
                concept_focus=node.concept_name,
                is_adaptive=True,
                prerequisite_concepts=node.prerequisites,
                generation_metadata={
                    'generated_at': datetime.utcnow().isoformat(),
                    'node_id': node.node_id,
                    'node_name': node.concept_name,
                    'level': level.cefr_level if level else 'A1',
                    'user_id': user_id,
                    'ai_model': generated_content.get('ai_model', 'gemini-pro'),
                    'personalization_context': {
                        'proficiency_level': profile.proficiency_level,
                        'native_language': profile.native_language,
                        'target_language': profile.target_language,
                        'weak_areas': progress.weak_areas if progress else [],
                        'strong_areas': progress.strong_areas if progress else []
                    },
                    'orchestration_reason': generated_content.get('orchestration_reason', 'curriculum_progression'),
                    'priority_level': generated_content.get('priority_level', 3)
                }
            )
            
            db.session.add(activity_record)
            db.session.commit()
            
            return activity_record
            
        except Exception as e:
            print(f"Error saving activity: {str(e)}")
            db.session.rollback()
            return None
    
    def determine_next_activity(self, user_id):
        """
        Determine the next optimal activity for a user.
        
        Priority Logic:
        1. **Vocabulary Review** - If vocabulary is due for review (spaced repetition)
        2. **Weak Area Focus** - If user has weak skills < 40% mastery
        3. **Next Learning Node** - Continue curriculum progression
        4. **Mixed Review** - Random review from completed nodes
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            dict: Contains activity data and metadata about why this activity was chosen
        """
        # Fetch user data
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "User not found"}
        
        profile = Profile.query.filter_by(user_id=user_id).first()
        if not profile:
            return {"error": "User profile not found"}
        
        # Get or create user's learning path progress
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        if not progress:
            progress = self._initialize_user_progress(user_id, profile)
        
        # PRIORITY 1: Vocabulary Review (Spaced Repetition)
        # Note: vocab_due_for_review will be tracked in future update
        # For now, skip directly to weak area or next node
        
        # PRIORITY 2: Weak Area Reinforcement
        weak_areas = self._identify_weak_areas(profile)
        if weak_areas:
            return self._generate_weak_area_activity(user_id, weak_areas, progress, profile)
        
        # PRIORITY 3: Next Learning Node (Curriculum Progression)
        next_node = self._determine_next_node(user_id, progress, profile)
        if next_node:
            return self._generate_node_activity(user_id, next_node, progress)
        
        # PRIORITY 4: Mixed Review (Keep skills sharp)
        return self._generate_mixed_review_activity(user_id, progress, profile)
    
    def _initialize_user_progress(self, user_id, profile):
        """
        Initialize a new UserLearningPathProgress for a user starting their journey.
        Handles the case where progress already exists (idempotent).
        """
        # Check if progress already exists for this user
        existing_progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        if existing_progress:
            return existing_progress
        
        # Determine starting CEFR level based on profile
        proficiency_to_cefr = {
            'beginner': 'A1',
            'elementary': 'A2',
            'intermediate': 'B1',
            'upper_intermediate': 'B2',
            'advanced': 'C1',
            'proficient': 'C2'
        }
        
        cefr_level = proficiency_to_cefr.get(profile.proficiency_level, 'A1')
        
        # Create progress with only fields that exist in the model
        progress = UserLearningPathProgress(
            user_id=user_id,
            current_level=cefr_level,
            target_level='B2',
            learning_style='mixed',
            preferred_pace='medium',
            preferred_session_length=20,
            weak_areas=[],
            strong_areas=[],
            nodes_completed=0,
            nodes_in_progress=0,
            nodes_mastered=0,
            time_invested_hours=0.0,
            longest_streak_days=0,
            current_streak_days=0
        )
        
        from app.models.user import db
        db.session.add(progress)
        db.session.commit()
        
        return progress
    
    def _identify_weak_areas(self, profile):
        """
        Identify skills that need reinforcement (< 40% mastery).
        
        Returns:
            list: Weak skill domains in priority order
        """
        mastery = profile.mastery_metrics or {}
        
        # Filter skills below 40% threshold
        weak_skills = [
            (skill, score) 
            for skill, score in mastery.items() 
            if skill != 'overall' and score < 40
        ]
        
        # Sort by lowest score first (most urgent)
        weak_skills.sort(key=lambda x: x[1])
        
        return [skill for skill, score in weak_skills]
    
    def _get_level_id_from_progress(self, progress):
        """Helper to get curriculum level ID from progress.current_level string"""
        if not progress or not progress.current_level:
            level = CurriculumLevel.query.filter_by(cefr_level='A1').first()
            return level.id if level else None
        
        level = CurriculumLevel.query.filter_by(cefr_level=progress.current_level).first()
        return level.id if level else None
    
    def _generate_vocab_review_activity(self, user_id, progress, profile):
        """
        Generate a vocabulary review activity using spaced repetition.
        """
        # Note: vocab_due_for_review not in current model, will be added in future
        # For now, just generate a vocabulary review activity
        vocab_to_review = []
        
        # Get current level ID
        current_level_id = self._get_level_id_from_progress(progress)
        
        # Find a vocabulary-focused learning node at user's level
        vocab_node = LearningNode.query.filter(
            and_(
                LearningNode.skill_domain == 'vocabulary',
                LearningNode.curriculum_level_id == current_level_id
            )
        ).first()
        
        if not vocab_node:
            # Fallback: find any vocabulary node
            vocab_node = LearningNode.query.filter_by(skill_domain='vocabulary').first()
        
        if not vocab_node:
            # No vocabulary nodes available, move to next priority
            return self._generate_weak_area_activity(
                user_id, 
                self._identify_weak_areas(profile), 
                progress, 
                profile
            )
        
        # Generate flashcard activity for vocabulary review
        activity = self.activity_generator.generate_personalized_activity(
            user_id=user_id,
            learning_node_id=vocab_node.node_id,
            activity_type='flashcard'
        )
        
        # Add orchestration metadata
        activity['orchestration_reason'] = 'vocab_review'
        activity['orchestration_message'] = f"Time to review {len(vocab_to_review)} vocabulary words!"
        activity['priority_level'] = 1
        activity['vocab_items_reviewed'] = vocab_to_review
        
        return activity
    
    def _generate_weak_area_activity(self, user_id, weak_areas, progress, profile):
        """
        Generate an activity focusing on the weakest skill area.
        """
        if not weak_areas:
            # No weak areas, continue to next node
            next_node = self._determine_next_node(user_id, progress, profile)
            if next_node:
                return self._generate_node_activity(user_id, next_node, progress)
            else:
                return self._generate_mixed_review_activity(user_id, progress, profile)
        
        # Focus on the weakest skill
        weakest_skill = weak_areas[0]
        
        # Get current level ID
        current_level_id = self._get_level_id_from_progress(progress)
        
        # Find a learning node that targets this skill at user's level
        target_node = LearningNode.query.filter(
            and_(
                LearningNode.skill_domain == weakest_skill,
                LearningNode.curriculum_level_id == current_level_id
            )
        ).first()
        
        if not target_node:
            # Try to find any node with this skill domain
            target_node = LearningNode.query.filter_by(skill_domain=weakest_skill).first()
        
        if not target_node:
            # No node found for this skill, try next weak area
            if len(weak_areas) > 1:
                return self._generate_weak_area_activity(user_id, weak_areas[1:], progress, profile)
            else:
                # Continue to next node
                next_node = self._determine_next_node(user_id, progress, profile)
                if next_node:
                    return self._generate_node_activity(user_id, next_node, progress)
                else:
                    return self._generate_mixed_review_activity(user_id, progress, profile)
        
        # Generate activity for weak area
        activity = self.activity_generator.generate_personalized_activity(
            user_id=user_id,
            learning_node_id=target_node.node_id
        )
        
        # Add orchestration metadata
        mastery_score = profile.mastery_metrics.get(weakest_skill, 0)
        activity['orchestration_reason'] = 'weak_area_focus'
        activity['orchestration_message'] = f"Let's work on {weakest_skill} (current: {mastery_score}%)"
        activity['priority_level'] = 2
        activity['target_skill'] = weakest_skill
        
        # Save activity to database
        activity_record = self._save_generated_activity(
            user_id=user_id,
            progress=progress,
            node=target_node,
            generated_content=activity,
            profile=profile
        )
        
        # Add activity ID to response
        if activity_record:
            activity['activity_id'] = activity_record.id
            activity['can_resume'] = True
        
        return activity
    
    def _determine_next_node(self, user_id, progress, profile):
        """
        Determine the next learning node in the curriculum progression.
        
        Logic:
        1. Get all nodes at user's current level
        2. Filter out completed nodes
        3. Find nodes with satisfied prerequisites
        4. Prioritize core nodes over optional
        5. Sort by difficulty (easier first)
        
        Returns:
            LearningNode or None
        """
        # Get current level ID
        current_level_id = self._get_level_id_from_progress(progress)
        
        # Get all nodes at current level
        current_level_nodes = LearningNode.query.filter_by(
            curriculum_level_id=current_level_id
        ).all()
        
        # Get completed node IDs for this user
        completed_nodes = NodeCompletion.query.filter_by(user_id=user_id).all()
        completed_node_ids = {nc.node_id for nc in completed_nodes if nc.mastery_level >= 0.7}
        
        # Filter nodes
        available_nodes = []
        for node in current_level_nodes:
            # Skip completed nodes
            if node.node_id in completed_node_ids:
                continue
            
            # Check prerequisites
            prerequisites_met = all(
                prereq_id in completed_node_ids 
                for prereq_id in (node.prerequisites or [])
            )
            
            if prerequisites_met:
                available_nodes.append(node)
        
        # If no nodes available at current level, check if user should level up
        if not available_nodes:
            # Check if user has completed enough of current level
            level_completion = self._calculate_level_completion(user_id, current_level_id)
            if level_completion >= 0.8:  # 80% completion threshold
                # Try to advance to next level
                next_level_str = self._get_next_level(progress.current_level)
                if next_level_str:
                    progress.current_level = next_level_str
                    from app.models.user import db
                    db.session.commit()
                    # Recursively call to get next node at new level
                    return self._determine_next_node(user_id, progress, profile)
            
            # If can't level up, return None (will trigger mixed review)
            return None
        
        # Sort by priority: core nodes first, then by difficulty
        available_nodes.sort(key=lambda n: (not n.is_core, n.difficulty_range_min))
        
        return available_nodes[0]
    
    def _generate_node_activity(self, user_id, node, progress):
        """
        Generate an activity for a specific learning node.
        """
        # Get user profile for metadata
        profile = Profile.query.filter_by(user_id=user_id).first()
        
        # Generate activity content
        activity = self.activity_generator.generate_personalized_activity(
            user_id=user_id,
            learning_node_id=node.node_id
        )
        
        # Add orchestration metadata
        activity['orchestration_reason'] = 'curriculum_progression'
        activity['orchestration_message'] = f"Let's learn: {node.concept_name}"
        activity['priority_level'] = 3
        activity['learning_node'] = node.to_dict()
        
        # Save activity to database
        activity_record = self._save_generated_activity(
            user_id=user_id,
            progress=progress,
            node=node,
            generated_content=activity,
            profile=profile
        )
        
        # Add activity ID to response
        if activity_record:
            activity['activity_id'] = activity_record.id
            activity['can_resume'] = True
        
        return activity
    
    def _generate_mixed_review_activity(self, user_id, progress, profile):
        """
        Generate a mixed review activity from previously completed nodes.
        """
        # Get completed nodes
        completed_nodes = NodeCompletion.query.filter_by(user_id=user_id).all()
        
        if not completed_nodes:
            # No completed nodes, start with first node
            current_level_id = self._get_level_id_from_progress(progress)
            first_node = LearningNode.query.filter_by(
                curriculum_level_id=current_level_id
            ).order_by(LearningNode.difficulty_range_min).first()
            
            if not first_node:
                # Fallback to any A1 node
                first_node = LearningNode.query.filter_by(node_id='A1_VOCAB_GREETINGS').first()
            
            if first_node:
                activity = self.activity_generator.generate_personalized_activity(
                    user_id=user_id,
                    learning_node_id=first_node.node_id
                )
                activity['orchestration_reason'] = 'first_activity'
                activity['orchestration_message'] = "Welcome! Let's start your learning journey!"
                activity['priority_level'] = 4
                
                # Save activity to database
                activity_record = self._save_generated_activity(
                    user_id=user_id,
                    progress=progress,
                    node=first_node,
                    generated_content=activity,
                    profile=profile
                )
                
                # Add activity ID to response
                if activity_record:
                    activity['activity_id'] = activity_record.id
                    activity['can_resume'] = True
                
                return activity
            else:
                return {"error": "No learning nodes available"}
        
        # Select a random completed node with lower mastery for review
        # Prioritize nodes with mastery between 0.5 and 0.8 (needs reinforcement)
        review_candidates = [
            nc for nc in completed_nodes 
            if 0.5 <= nc.mastery_level < 0.8
        ]
        
        if not review_candidates:
            # All nodes are either mastered or struggling, review recent ones
            review_candidates = sorted(
                completed_nodes, 
                key=lambda nc: nc.last_attempted_at, 
                reverse=True
            )[:5]
        
        if not review_candidates:
            review_candidates = completed_nodes
        
        # Pick the node with lowest mastery from candidates
        target_completion = min(review_candidates, key=lambda nc: nc.mastery_level)
        
        # Get the node details
        review_node = LearningNode.query.filter_by(node_id=target_completion.node_id).first()
        
        if not review_node:
            return {"error": "Review node not found"}
        
        # Generate review activity
        activity = self.activity_generator.generate_personalized_activity(
            user_id=user_id,
            learning_node_id=target_completion.node_id
        )
        
        # Add orchestration metadata
        activity['orchestration_reason'] = 'mixed_review'
        activity['orchestration_message'] = "Let's review and strengthen your skills!"
        activity['priority_level'] = 4
        activity['review_node_mastery'] = target_completion.mastery_level
        
        # Save activity to database
        activity_record = self._save_generated_activity(
            user_id=user_id,
            progress=progress,
            node=review_node,
            generated_content=activity,
            profile=profile
        )
        
        # Add activity ID to response
        if activity_record:
            activity['activity_id'] = activity_record.id
            activity['can_resume'] = True
        
        return activity
    
    def _calculate_level_completion(self, user_id, level_id):
        """
        Calculate what percentage of a curriculum level has been completed.
        """
        # Get all nodes at this level
        level_nodes = LearningNode.query.filter_by(curriculum_level_id=level_id).all()
        
        if not level_nodes:
            return 0.0
        
        # Get completed nodes
        completed_nodes = NodeCompletion.query.filter_by(user_id=user_id).all()
        completed_node_ids = {nc.node_id for nc in completed_nodes if nc.mastery_level >= 0.7}
        
        # Count core nodes (more weight)
        core_nodes = [n for n in level_nodes if n.is_core]
        optional_nodes = [n for n in level_nodes if not n.is_core]
        
        completed_core = len([n for n in core_nodes if n.node_id in completed_node_ids])
        completed_optional = len([n for n in optional_nodes if n.node_id in completed_node_ids])
        
        # Weight core nodes as 70% of completion, optional as 30%
        if core_nodes:
            core_completion = completed_core / len(core_nodes)
        else:
            core_completion = 1.0
        
        if optional_nodes:
            optional_completion = completed_optional / len(optional_nodes)
        else:
            optional_completion = 1.0
        
        total_completion = (core_completion * 0.7) + (optional_completion * 0.3)
        
        return total_completion
    
    def _get_next_level(self, current_level_str):
        """
        Get the next CEFR level string.
        
        Args:
            current_level_str: Current CEFR level string (e.g., 'A1')
            
        Returns:
            str: Next CEFR level or None
        """
        # CEFR progression order
        cefr_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        
        try:
            current_index = cefr_order.index(current_level_str)
            if current_index < len(cefr_order) - 1:
                return cefr_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        
        return None
    
    def complete_activity(self, user_id, learning_node_id, performance_score, time_spent_seconds, 
                         activity_id=None, user_responses=None):
        """
        Record activity completion and update user progress.
        
        Args:
            user_id (int): User ID
            learning_node_id (str): Learning node ID
            performance_score (float): Score from 0.0 to 1.0
            time_spent_seconds (int): Time spent on activity
            activity_id (int, optional): Activity database ID
            user_responses (dict, optional): User's answers/responses
            
        Returns:
            dict: Updated progress information
        """
        from app.models.user import db
        
        # Get or create NodeCompletion
        node_completion = NodeCompletion.query.filter_by(
            user_id=user_id,
            node_id=learning_node_id
        ).first()
        
        if not node_completion:
            node_completion = NodeCompletion(
                user_id=user_id,
                node_id=learning_node_id,
                mastery_level=0.0,
                attempts=0
            )
            db.session.add(node_completion)
        
        # Update with new attempt
        node_completion.update_with_new_attempt(performance_score, time_spent_seconds)
        
        # Save detailed activity log if activity_id provided
        if activity_id:
            activity_log = self._create_activity_log(
                user_id=user_id,
                activity_id=activity_id,
                learning_node_id=learning_node_id,
                performance_score=performance_score,
                time_spent_seconds=time_spent_seconds,
                user_responses=user_responses,
                attempts=node_completion.attempts
            )
            db.session.add(activity_log)
        
        # Update user's learning path progress
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        if progress:
            # Update activity tracking (use existing fields)
            progress.last_activity_date = datetime.utcnow()
            
            # Update nodes count
            if node_completion.mastery_level >= 0.7:
                progress.nodes_mastered = NodeCompletion.query.filter(
                    NodeCompletion.user_id == user_id,
                    NodeCompletion.mastery_level >= 0.7
                ).count()
            
            progress.nodes_completed = NodeCompletion.query.filter_by(user_id=user_id).count()
            
            # Update weak/strong areas based on node's skill domain
            node = LearningNode.query.filter_by(node_id=learning_node_id).first()
            if node:
                self._update_skill_areas(progress, node.skill_domain, performance_score)
        
        db.session.commit()
        
        return {
            "success": True,
            "node_id": learning_node_id,
            "mastery_level": node_completion.mastery_level,
            "attempts": node_completion.attempts,
            "performance_score": performance_score,
            "activity_logged": activity_id is not None
        }
    
    def _create_activity_log(self, user_id, activity_id, learning_node_id, performance_score, 
                            time_spent_seconds, user_responses, attempts):
        """
        Create a detailed UserActivityLog entry.
        
        Args:
            user_id: User ID
            activity_id: Activity database ID
            learning_node_id: Learning node ID
            performance_score: Performance score (0.0-1.0)
            time_spent_seconds: Time spent
            user_responses: User's answers
            attempts: Attempt number
            
        Returns:
            UserActivityLog: Created log entry
        """
        # Get activity and node details
        activity = Activity.query.get(activity_id) if activity_id else None
        node = LearningNode.query.filter_by(node_id=learning_node_id).first()
        
        # Get user progress for learning_path_id
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        # Determine mastery level
        mastery_level = 'not_started'
        if performance_score >= 0.9:
            mastery_level = 'mastered'
        elif performance_score >= 0.7:
            mastery_level = 'proficient'
        elif performance_score >= 0.4:
            mastery_level = 'learning'
        
        # Calculate next review date (spaced repetition)
        if performance_score >= 0.8:
            review_interval_hours = 168  # 1 week
        elif performance_score >= 0.6:
            review_interval_hours = 72   # 3 days
        else:
            review_interval_hours = 24   # 1 day
        
        next_review_date = datetime.utcnow() + timedelta(hours=review_interval_hours)
        
        # Create log entry
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_id=activity_id,
            learning_path_id=progress.id if progress else None,
            completed_at=datetime.utcnow(),
            score=int(performance_score * 100),  # Convert to percentage
            max_score=100,
            time_spent_minutes=time_spent_seconds / 60,
            user_response=user_responses or {},
            is_completed=True,
            attempt_number=attempts,
            skill_area=node.skill_domain if node else None,
            concept_focus=node.name if node else None,
            accuracy_score=performance_score,
            mastery_level=mastery_level,
            needs_review=performance_score < 0.7,
            next_review_date=next_review_date,
            confidence_score=min(performance_score + 0.1, 1.0)  # Slightly higher than performance
        )
        
        return activity_log
    
    def _update_skill_areas(self, progress, skill_domain, performance_score):
        """
        Update user's weak and strong areas based on performance.
        """
        if not progress.weak_areas:
            progress.weak_areas = []
        if not progress.strong_areas:
            progress.strong_areas = []
        
        # If performance is poor (< 0.6), add to weak areas
        if performance_score < 0.6 and skill_domain not in progress.weak_areas:
            progress.weak_areas.append(skill_domain)
            # Remove from strong areas if present
            if skill_domain in progress.strong_areas:
                progress.strong_areas.remove(skill_domain)
        
        # If performance is good (>= 0.8), add to strong areas
        elif performance_score >= 0.8 and skill_domain not in progress.strong_areas:
            progress.strong_areas.append(skill_domain)
            # Remove from weak areas if present
            if skill_domain in progress.weak_areas:
                progress.weak_areas.remove(skill_domain)
