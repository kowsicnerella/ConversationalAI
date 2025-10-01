import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.models import (
    db, User, Profile, LearningPath, Activity, 
    ProficiencyAssessment, UserActivityLog
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.services.comprehensive_assessment_service import ComprehensiveAssessmentService
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class AdaptiveLearningPathGenerator:
    """
    AI-driven service that generates personalized learning paths based on comprehensive assessment results
    and continuously adapts based on user performance and mastery validation.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
        self.assessment_service = ComprehensiveAssessmentService()
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Learning path configuration
        self.MASTERY_THRESHOLD = 0.85
        self.PROFICIENCY_THRESHOLD = 0.70
        self.STRUGGLE_THRESHOLD = 0.50
        self.MIN_ACTIVITIES_FOR_MASTERY = 3
        self.MAX_RETRIES_PER_CONCEPT = 5
        
        # Learning progression templates
        self.SKILL_PROGRESSION = {
            'beginner': {
                'vocabulary': ['basic_greetings', 'family_members', 'daily_activities', 'numbers', 'colors'],
                'grammar': ['present_tense', 'articles', 'basic_sentence_structure', 'pronouns', 'plural_forms'],
                'reading': ['simple_sentences', 'short_paragraphs', 'basic_comprehension'],
                'writing': ['sentence_formation', 'basic_paragraph', 'personal_information'],
                'listening': ['basic_conversations', 'simple_instructions', 'everyday_situations'],
                'speaking': ['pronunciation', 'basic_greetings', 'simple_conversations']
            },
            'intermediate': {
                'vocabulary': ['workplace_terms', 'technology', 'travel', 'food', 'hobbies'],
                'grammar': ['past_tense', 'future_tense', 'conditionals', 'passive_voice', 'reported_speech'],
                'reading': ['news_articles', 'short_stories', 'technical_texts'],
                'writing': ['essay_writing', 'formal_emails', 'reports', 'creative_writing'],
                'listening': ['news_broadcasts', 'interviews', 'lectures', 'movies'],
                'speaking': ['presentations', 'debates', 'phone_conversations', 'professional_discussions']
            },
            'advanced': {
                'vocabulary': ['academic_terms', 'business_language', 'idioms', 'phrasal_verbs'],
                'grammar': ['advanced_conditionals', 'subjunctive', 'complex_sentences', 'discourse_markers'],
                'reading': ['academic_papers', 'literature', 'complex_analysis'],
                'writing': ['research_papers', 'professional_proposals', 'literary_analysis'],
                'listening': ['academic_lectures', 'complex_discussions', 'accents_varieties'],
                'speaking': ['public_speaking', 'academic_presentations', 'professional_negotiations']
            }
        }

    def generate_personalized_learning_path(self, user_id: int, assessment_id: int) -> Dict:
        """
        Generate a comprehensive personalized learning path based on assessment results.
        """
        try:
            # Get assessment results
            assessment = ProficiencyAssessment.query.get(assessment_id)
            if not assessment or assessment.user_id != user_id:
                return {'error': 'Assessment not found or access denied'}
            
            if not assessment.completed_at:
                return {'error': 'Assessment not completed yet'}
            
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Analyze assessment results
            proficiency_level = assessment.proficiency_level
            strengths = assessment.strengths or []
            weaknesses = assessment.weaknesses or []
            skill_scores = assessment.assessment_data.get('skill_scores', {})
            
            # Generate learning path structure
            learning_path_data = self._create_adaptive_learning_structure(
                proficiency_level, strengths, weaknesses, skill_scores
            )
            
            # Create learning path record
            learning_path = LearningPath(
                title=f"Personalized {proficiency_level.title()} English Learning Path",
                description=learning_path_data['description'],
                difficulty_level=proficiency_level,
                is_adaptive=True,
                user_id=user_id,
                assessment_id=assessment_id
            )
            
            db.session.add(learning_path)
            db.session.flush()
            
            # Generate first chapter/activity based on priority weakness
            first_activity = self._generate_first_activity(
                learning_path.id, proficiency_level, weaknesses, strengths
            )
            
            # Store learning path metadata
            learning_path.path_data = {
                'structure': learning_path_data['structure'],
                'priority_skills': learning_path_data['priority_skills'],
                'mastery_tracking': {},
                'current_focus': learning_path_data['priority_skills'][0] if learning_path_data['priority_skills'] else 'vocabulary',
                'generated_activities': [first_activity['id']] if first_activity.get('id') else []
            }
            
            db.session.commit()
            
            return {
                'learning_path_id': learning_path.id,
                'title': learning_path.title,
                'description': learning_path.description,
                'proficiency_level': proficiency_level,
                'priority_skills': learning_path_data['priority_skills'],
                'first_activity': first_activity,
                'estimated_completion_weeks': learning_path_data['estimated_weeks'],
                'next_steps': 'Complete the first activity to unlock adaptive learning progression'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Learning path generation failed: {str(e)}'}

    def _create_adaptive_learning_structure(self, proficiency_level: str, 
                                          strengths: List[str], weaknesses: List[str], 
                                          skill_scores: Dict) -> Dict:
        """
        Create an adaptive learning structure based on assessment results.
        """
        # Prioritize skills based on weaknesses and importance
        priority_skills = self._prioritize_skills(weaknesses, strengths, skill_scores)
        
        # Create learning modules for each priority skill
        learning_modules = []
        for skill in priority_skills:
            concepts = self.SKILL_PROGRESSION[proficiency_level].get(skill, [])
            
            module = {
                'skill_area': skill,
                'concepts': concepts,
                'current_concept_index': 0,
                'mastery_status': {concept: 'not_started' for concept in concepts},
                'retry_counts': {concept: 0 for concept in concepts},
                'estimated_hours': len(concepts) * 2  # 2 hours per concept
            }
            learning_modules.append(module)
        
        # Estimate completion time
        total_concepts = sum(len(module['concepts']) for module in learning_modules)
        estimated_weeks = max(4, total_concepts // 3)  # At least 4 weeks, roughly 3 concepts per week
        
        return {
            'structure': learning_modules,
            'priority_skills': priority_skills,
            'description': self._generate_path_description(proficiency_level, priority_skills),
            'estimated_weeks': estimated_weeks
        }

    def _prioritize_skills(self, weaknesses: List[str], strengths: List[str], 
                          skill_scores: Dict) -> List[str]:
        """
        Prioritize skills based on assessment results and learning effectiveness.
        """
        # Base priority on weaknesses
        priority_skills = weaknesses.copy()
        
        # Add skills that are close to the struggle threshold
        for skill, score in skill_scores.items():
            if score is not None and score < 0.6 and skill not in priority_skills:
                priority_skills.append(skill)
        
        # Ensure we have at least 3 skills to work on
        remaining_skills = [s for s in self.assessment_service.SKILL_AREAS 
                          if s not in priority_skills]
        while len(priority_skills) < 3 and remaining_skills:
            priority_skills.append(remaining_skills.pop(0))
        
        # Order by importance and learning dependency
        skill_order = ['vocabulary', 'grammar', 'reading', 'writing', 'listening', 'speaking']
        priority_skills.sort(key=lambda x: skill_order.index(x) if x in skill_order else 999)
        
        return priority_skills[:4]  # Focus on top 4 skills

    def _generate_path_description(self, proficiency_level: str, priority_skills: List[str]) -> str:
        """
        Generate a personalized description for the learning path.
        """
        skill_names = ', '.join(priority_skills)
        return f"""
        This personalized {proficiency_level}-level learning path focuses on improving your 
        {skill_names} skills through adaptive, AI-powered activities. The path adjusts based 
        on your performance, ensuring you master each concept before progressing to the next.
        """

    def _generate_first_activity(self, learning_path_id: int, proficiency_level: str, 
                               weaknesses: List[str], strengths: List[str]) -> Dict:
        """
        Generate the first activity based on the highest priority weakness.
        """
        try:
            # Determine the first skill to focus on
            first_skill = weaknesses[0] if weaknesses else 'vocabulary'
            
            # Get the first concept for this skill
            concepts = self.SKILL_PROGRESSION[proficiency_level].get(first_skill, [])
            first_concept = concepts[0] if concepts else 'basic_introduction'
            
            # Generate activity based on skill and concept
            activity_data = self._create_concept_activity(first_skill, first_concept, proficiency_level)
            
            # Create activity record
            activity = Activity(
                title=activity_data['title'],
                description=activity_data['description'],
                activity_type=activity_data['type'],
                difficulty_level=proficiency_level,
                content=activity_data['content'],
                learning_path_id=learning_path_id,
                order_in_path=1,
                points_reward=activity_data.get('points', 50),
                is_adaptive=True,
                concept_focus=first_concept,
                skill_area=first_skill
            )
            
            db.session.add(activity)
            db.session.flush()
            
            return {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'type': activity.activity_type,
                'skill_area': first_skill,
                'concept': first_concept,
                'difficulty': proficiency_level,
                'points_reward': activity.points_reward
            }
            
        except Exception as e:
            return {'error': f'First activity generation failed: {str(e)}'}

    def _create_concept_activity(self, skill_area: str, concept: str, difficulty: str) -> Dict:
        """
        Create an activity for a specific concept within a skill area.
        """
        activity_templates = {
            'vocabulary': {
                'basic_greetings': {
                    'title': 'Master Basic English Greetings',
                    'description': 'Learn essential greetings and polite expressions',
                    'type': 'flashcard',
                    'content': {
                        'words': ['Hello', 'Good morning', 'Thank you', 'Please', 'Excuse me'],
                        'contexts': ['Meeting someone new', 'Starting your day', 'Being polite']
                    }
                },
                'family_members': {
                    'title': 'Family Vocabulary',
                    'description': 'Learn words for family relationships',
                    'type': 'quiz',
                    'content': {
                        'words': ['Mother', 'Father', 'Sister', 'Brother', 'Grandmother'],
                        'practice_sentences': True
                    }
                }
            },
            'grammar': {
                'present_tense': {
                    'title': 'Present Tense Mastery',
                    'description': 'Master present tense verb forms and usage',
                    'type': 'grammar_exercise',
                    'content': {
                        'rules': ['Subject + Verb + Object', 'Third person singular adds -s'],
                        'examples': ['I eat breakfast', 'She works in an office']
                    }
                }
            },
            'reading': {
                'simple_sentences': {
                    'title': 'Reading Simple Sentences',
                    'description': 'Practice reading and understanding basic sentences',
                    'type': 'reading',
                    'content': {
                        'passages': ['My name is John. I live in Chennai.'],
                        'questions': ['What is the person\'s name?']
                    }
                }
            },
            'writing': {
                'sentence_formation': {
                    'title': 'Form Complete Sentences',
                    'description': 'Practice writing grammatically correct sentences',
                    'type': 'writing',
                    'content': {
                        'prompts': ['Write about your daily routine'],
                        'guidelines': ['Use present tense', 'Include at least 3 sentences']
                    }
                }
            }
        }
        
        # Get template or create generic one
        template = activity_templates.get(skill_area, {}).get(concept)
        if not template:
            template = {
                'title': f'Practice {concept.replace("_", " ").title()}',
                'description': f'Improve your {skill_area} skills with {concept.replace("_", " ")}',
                'type': 'quiz',
                'content': {'topic': concept, 'skill': skill_area}
            }
        
        template['points'] = 50 if difficulty == 'beginner' else (75 if difficulty == 'intermediate' else 100)
        return template

    def get_next_adaptive_activity(self, user_id: int, learning_path_id: int, 
                                 last_activity_performance: Optional[Dict] = None) -> Dict:
        """
        Generate the next activity based on user's performance and mastery status.
        """
        try:
            learning_path = LearningPath.query.get(learning_path_id)
            if not learning_path or learning_path.user_id != user_id:
                return {'error': 'Learning path not found or access denied'}
            
            path_data = learning_path.path_data or {}
            current_focus = path_data.get('current_focus', 'vocabulary')
            mastery_tracking = path_data.get('mastery_tracking', {})
            
            # Analyze last performance if provided
            if last_activity_performance:
                self._update_mastery_tracking(learning_path, last_activity_performance)
                db.session.flush()
                path_data = learning_path.path_data  # Refresh data
            
            # Determine next activity type and difficulty
            next_activity_plan = self._plan_next_activity(learning_path, path_data)
            
            if next_activity_plan['action'] == 'retry_concept':
                # User needs to retry the same concept with different approach
                activity = self._generate_retry_activity(
                    learning_path_id, next_activity_plan['skill'], 
                    next_activity_plan['concept'], next_activity_plan['difficulty']
                )
            elif next_activity_plan['action'] == 'next_concept':
                # User mastered current concept, move to next
                activity = self._generate_next_concept_activity(
                    learning_path_id, next_activity_plan['skill'], 
                    next_activity_plan['concept'], next_activity_plan['difficulty']
                )
            elif next_activity_plan['action'] == 'reinforcement':
                # User needs reinforcement before moving on
                activity = self._generate_reinforcement_activity(
                    learning_path_id, next_activity_plan['skill'], 
                    next_activity_plan['concept'], next_activity_plan['difficulty']
                )
            else:
                # Complete learning path or switch focus
                return self._handle_path_completion_or_switch(learning_path)
            
            # Update path data with new activity
            if 'generated_activities' not in path_data:
                path_data['generated_activities'] = []
            path_data['generated_activities'].append(activity.get('id'))
            learning_path.path_data = path_data
            
            db.session.commit()
            
            return {
                'activity': activity,
                'progress_status': self._calculate_progress_status(learning_path),
                'mastery_status': mastery_tracking,
                'next_milestone': next_activity_plan.get('milestone', 'Continue learning')
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Next activity generation failed: {str(e)}'}

    def _update_mastery_tracking(self, learning_path: LearningPath, performance: Dict):
        """
        Update mastery tracking based on user performance.
        """
        path_data = learning_path.path_data
        mastery_tracking = path_data.get('mastery_tracking', {})
        
        skill = performance.get('skill_area')
        concept = performance.get('concept')
        score = performance.get('score', 0)
        
        if not skill or not concept:
            return
        
        # Initialize tracking for skill/concept if not exists
        if skill not in mastery_tracking:
            mastery_tracking[skill] = {}
        if concept not in mastery_tracking[skill]:
            mastery_tracking[skill][concept] = {
                'attempts': 0, 'scores': [], 'status': 'learning', 'retry_count': 0
            }
        
        # Update tracking
        concept_tracking = mastery_tracking[skill][concept]
        concept_tracking['attempts'] += 1
        concept_tracking['scores'].append(score)
        concept_tracking['last_attempt'] = datetime.utcnow().isoformat()
        
        # Calculate running average
        avg_score = sum(concept_tracking['scores']) / len(concept_tracking['scores'])
        
        # Determine mastery status
        if avg_score >= self.MASTERY_THRESHOLD and concept_tracking['attempts'] >= self.MIN_ACTIVITIES_FOR_MASTERY:
            concept_tracking['status'] = 'mastered'
        elif avg_score >= self.PROFICIENCY_THRESHOLD:
            concept_tracking['status'] = 'proficient'
        elif avg_score < self.STRUGGLE_THRESHOLD:
            concept_tracking['status'] = 'struggling'
            concept_tracking['retry_count'] = concept_tracking.get('retry_count', 0) + 1
        else:
            concept_tracking['status'] = 'learning'
        
        # Update path data
        path_data['mastery_tracking'] = mastery_tracking
        learning_path.path_data = path_data

    def _plan_next_activity(self, learning_path: LearningPath, path_data: Dict) -> Dict:
        """
        Plan the next activity based on current progress and mastery status.
        """
        current_focus = path_data.get('current_focus', 'vocabulary')
        mastery_tracking = path_data.get('mastery_tracking', {})
        learning_structure = path_data.get('structure', [])
        
        # Find current module
        current_module = None
        for module in learning_structure:
            if module['skill_area'] == current_focus:
                current_module = module
                break
        
        if not current_module:
            return {'action': 'complete', 'message': 'Learning path completed'}
        
        # Get current concept
        concepts = current_module['concepts']
        current_index = current_module.get('current_concept_index', 0)
        
        if current_index >= len(concepts):
            # Move to next skill
            return self._plan_next_skill(learning_path, path_data)
        
        current_concept = concepts[current_index]
        concept_status = mastery_tracking.get(current_focus, {}).get(current_concept, {})
        
        # Decide action based on concept status
        if concept_status.get('status') == 'mastered':
            # Move to next concept
            current_module['current_concept_index'] = current_index + 1
            return {
                'action': 'next_concept',
                'skill': current_focus,
                'concept': concepts[current_index + 1] if current_index + 1 < len(concepts) else None,
                'difficulty': learning_path.difficulty_level
            }
        elif concept_status.get('status') == 'struggling':
            # Retry with different approach
            retry_count = concept_status.get('retry_count', 0)
            if retry_count >= self.MAX_RETRIES_PER_CONCEPT:
                # Move on despite struggles
                current_module['current_concept_index'] = current_index + 1
                return {
                    'action': 'next_concept',
                    'skill': current_focus,
                    'concept': concepts[current_index + 1] if current_index + 1 < len(concepts) else None,
                    'difficulty': 'beginner'  # Lower difficulty
                }
            else:
                return {
                    'action': 'retry_concept',
                    'skill': current_focus,
                    'concept': current_concept,
                    'difficulty': learning_path.difficulty_level,
                    'retry_count': retry_count
                }
        elif concept_status.get('status') == 'proficient':
            # Provide reinforcement before moving on
            return {
                'action': 'reinforcement',
                'skill': current_focus,
                'concept': current_concept,
                'difficulty': learning_path.difficulty_level
            }
        else:
            # Continue with current concept
            return {
                'action': 'continue_concept',
                'skill': current_focus,
                'concept': current_concept,
                'difficulty': learning_path.difficulty_level
            }

    def _plan_next_skill(self, learning_path: LearningPath, path_data: Dict) -> Dict:
        """
        Plan transition to next skill area.
        """
        learning_structure = path_data.get('structure', [])
        current_focus = path_data.get('current_focus', 'vocabulary')
        
        # Find next skill module
        current_skill_index = None
        for i, module in enumerate(learning_structure):
            if module['skill_area'] == current_focus:
                current_skill_index = i
                break
        
        if current_skill_index is not None and current_skill_index + 1 < len(learning_structure):
            next_module = learning_structure[current_skill_index + 1]
            path_data['current_focus'] = next_module['skill_area']
            
            return {
                'action': 'next_concept',
                'skill': next_module['skill_area'],
                'concept': next_module['concepts'][0] if next_module['concepts'] else None,
                'difficulty': learning_path.difficulty_level
            }
        else:
            return {'action': 'complete', 'message': 'All skills completed'}

    def _calculate_progress_status(self, learning_path: LearningPath) -> Dict:
        """
        Calculate overall progress status for the learning path.
        """
        path_data = learning_path.path_data or {}
        mastery_tracking = path_data.get('mastery_tracking', {})
        learning_structure = path_data.get('structure', [])
        
        total_concepts = sum(len(module['concepts']) for module in learning_structure)
        mastered_concepts = 0
        proficient_concepts = 0
        
        for skill_tracking in mastery_tracking.values():
            for concept_data in skill_tracking.values():
                if concept_data.get('status') == 'mastered':
                    mastered_concepts += 1
                elif concept_data.get('status') == 'proficient':
                    proficient_concepts += 1
        
        progress_percentage = ((mastered_concepts + proficient_concepts * 0.7) / total_concepts * 100) if total_concepts > 0 else 0
        
        return {
            'total_concepts': total_concepts,
            'mastered_concepts': mastered_concepts,
            'proficient_concepts': proficient_concepts,
            'progress_percentage': round(progress_percentage, 2),
            'current_focus': path_data.get('current_focus', 'vocabulary')
        }

    def validate_concept_mastery(self, user_id: int, learning_path_id: int, 
                               skill_area: str, concept: str) -> Dict:
        """
        Validate if user has truly mastered a concept through multiple assessment methods.
        """
        try:
            # Generate validation activities
            validation_activities = []
            
            # Create different types of validation activities
            for activity_type in ['quiz', 'writing', 'practical_application']:
                validation_activity = self._create_validation_activity(
                    skill_area, concept, activity_type, learning_path_id
                )
                validation_activities.append(validation_activity)
            
            return {
                'validation_activities': validation_activities,
                'instructions': f'Complete these activities to demonstrate mastery of {concept}',
                'passing_score': self.MASTERY_THRESHOLD,
                'required_activities': len(validation_activities)
            }
            
        except Exception as e:
            return {'error': f'Mastery validation failed: {str(e)}'}

    def _create_validation_activity(self, skill_area: str, concept: str, 
                                  activity_type: str, learning_path_id: int) -> Dict:
        """
        Create a validation activity for concept mastery.
        """
        activity_data = self._create_concept_activity(skill_area, concept, 'intermediate')
        activity_data['type'] = activity_type
        activity_data['is_validation'] = True
        activity_data['title'] = f"Mastery Check: {activity_data['title']}"
        
        return activity_data

    def _generate_retry_activity(self, learning_path_id: int, skill: str, 
                               concept: str, difficulty: str) -> Dict:
        """
        Generate a retry activity with different approach for struggling concepts.
        """
        # Use different activity type or teaching method
        activity_data = self._create_concept_activity(skill, concept, difficulty)
        activity_data['title'] = f"Review & Practice: {activity_data['title']}"
        activity_data['is_retry'] = True
        
        return activity_data

    def _generate_next_concept_activity(self, learning_path_id: int, skill: str, 
                                      concept: str, difficulty: str) -> Dict:
        """
        Generate activity for the next concept in progression.
        """
        if not concept:
            return {'message': 'Skill area completed'}
        
        activity_data = self._create_concept_activity(skill, concept, difficulty)
        return activity_data

    def _generate_reinforcement_activity(self, learning_path_id: int, skill: str, 
                                       concept: str, difficulty: str) -> Dict:
        """
        Generate reinforcement activity for proficient but not mastered concepts.
        """
        activity_data = self._create_concept_activity(skill, concept, difficulty)
        activity_data['title'] = f"Reinforce: {activity_data['title']}"
        activity_data['is_reinforcement'] = True
        
        return activity_data

    def _handle_path_completion_or_switch(self, learning_path: LearningPath) -> Dict:
        """
        Handle learning path completion or skill focus switching.
        """
        return {
            'message': 'Congratulations! You have completed this learning path.',
            'telugu_message': 'అభినందనలు! మీరు ఈ అభ్యాస మార్గాన్ని పూర్తి చేసారు.',
            'next_steps': 'Ready for the next level or specialized learning path',
            'completion_status': 'completed'
        }