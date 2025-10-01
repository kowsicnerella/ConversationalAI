import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from app.models import User, Activity, UserActivityLog, LearningPath, ProficiencyAssessment
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class InitialAssessmentService:
    """
    Comprehensive initial assessment service for new users to determine their English proficiency level,
    learning preferences, and optimal learning path placement.
    Enhanced with comprehensive multi-skill assessment and adaptive learning path generation.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Assessment configuration
        self.ASSESSMENT_LEVELS = ['beginner', 'intermediate', 'advanced']
        self.SKILL_AREAS = ['vocabulary', 'grammar', 'reading', 'listening', 'writing', 'speaking']
        self.QUESTIONS_PER_SKILL = 3
        self.QUESTIONS_PER_LEVEL = 2
        self.PASSING_THRESHOLD = 0.7
        
        # Enhanced scoring weights for different skill areas
        self.SKILL_WEIGHTS = {
            'vocabulary': 0.20,
            'grammar': 0.25,
            'reading': 0.20,
            'listening': 0.15,
            'writing': 0.15,
            'speaking': 0.05
        }
        
        # Mastery thresholds
        self.MASTERY_THRESHOLD = 0.85
        self.PROFICIENT_THRESHOLD = 0.70
        self.NEEDS_WORK_THRESHOLD = 0.50

    def conduct_comprehensive_initial_assessment(self, user_id: int, assessment_type: str = 'comprehensive') -> Dict:
        """
        Conduct a comprehensive initial assessment for a new user.
        
        Args:
            user_id: The ID of the user to assess
            assessment_type: Type of assessment ('quick', 'adaptive', 'comprehensive')
            
        Returns:
            Dict containing assessment results and recommendations
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Generate assessment questions based on type
        if assessment_type == 'quick':
            assessment_data = self._generate_quick_assessment()
        elif assessment_type == 'adaptive':
            assessment_data = self._generate_adaptive_assessment()
        else:  # comprehensive
            assessment_data = self._generate_comprehensive_assessment()
        
        # Create assessment record
        assessment = ProficiencyAssessment(
            user_id=user_id,
            assessment_type=assessment_type,
            questions_asked=assessment_data['questions']
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return {
            'assessment_id': assessment.id,
            'assessment_type': assessment_type,
            'questions': assessment_data['questions'],
            'metadata': {
                'total_questions': len(assessment_data['questions']),
                'max_score': assessment_data['max_score'],
                'estimated_duration_minutes': assessment_data['estimated_duration'],
                'skill_areas_covered': assessment_data['skill_areas']
            },
            'instructions': {
                'english': assessment_data['instructions'],
                'telugu': assessment_data['telugu_instructions']
            },
            'assessment_structure': assessment_data['structure']
        }

    def submit_assessment_answers(self, assessment_id: int, answers: Dict) -> Dict:
        """
        Submit and evaluate assessment answers.
        
        Args:
            assessment_id: Assessment ID
            answers: Dictionary of question_id -> answer mappings
        """
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")
        
        # Check if assessment is already completed
        if assessment.user_responses:
            raise ValueError("Assessment is already completed")
        
        # Load questions data
        questions = assessment.questions_asked if assessment.questions_asked else []
        
        # Evaluate answers
        evaluation_result = self._evaluate_assessment_answers(questions, answers)
        
        # Calculate proficiency level and recommendations
        proficiency_analysis = self._analyze_proficiency_level(evaluation_result)
        
        # Generate learning path recommendations
        learning_path_recommendations = self._recommend_learning_paths(proficiency_analysis)
        
        # Update assessment record
        assessment.user_responses = answers
        assessment.ai_evaluation = evaluation_result
        assessment.proficiency_level = proficiency_analysis['overall_level']
        assessment.strengths = proficiency_analysis.get('strengths', [])
        assessment.weaknesses = proficiency_analysis.get('weaknesses', [])
        assessment.recommendations = learning_path_recommendations
        assessment.confidence_score = proficiency_analysis.get('confidence', 0.5)
        assessment.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Generate personalized report
        assessment_report = self._generate_assessment_report(
            assessment, evaluation_result, proficiency_analysis, learning_path_recommendations
        )
        
        # Calculate max score from questions
        max_score = sum(q.get('points', 2) for q in questions) if questions else 1
        
        return {
            'assessment_completed': True,
            'assessment_id': assessment_id,
            'results': {
                'overall_score': evaluation_result['total_score'],
                'max_score': max_score,
                'percentage': (evaluation_result['total_score'] / max_score) * 100 if max_score > 0 else 0,
                'proficiency_level': proficiency_analysis['overall_level'],
                'skill_breakdown': proficiency_analysis['skill_breakdown']
            },
            'recommendations': learning_path_recommendations,
            'detailed_report': assessment_report,
            'next_steps': self._generate_next_steps(proficiency_analysis, learning_path_recommendations)
        }

    def get_assessment_history(self, user_id: int) -> List[Dict]:
        """
        Get assessment history for a user.
        """
        assessments = ProficiencyAssessment.query.filter_by(user_id=user_id)\
                                                .order_by(ProficiencyAssessment.completed_at.desc()).all()
        
        history = []
        for assessment in assessments:
            # Calculate max score from questions if available
            max_score = 0
            if assessment.questions_asked:
                max_score = sum(q.get('points', 2) for q in assessment.questions_asked)
            
            assessment_data = {
                'assessment_id': assessment.id,
                'assessment_type': assessment.assessment_type,
                'status': 'completed' if assessment.user_responses else 'in_progress',
                'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None,
                'proficiency_level': assessment.proficiency_level
            }
            
            if assessment.completed_at and assessment.ai_evaluation:
                total_score = assessment.ai_evaluation.get('total_score', 0)
                assessment_data['score'] = total_score
                assessment_data['max_score'] = max_score
                assessment_data['percentage'] = (total_score / max_score * 100) if max_score > 0 else 0
                assessment_data['skill_breakdown'] = assessment.ai_evaluation.get('skill_scores', {})
            
            history.append(assessment_data)
        
        return history

    def retake_assessment(self, user_id: int, previous_assessment_id: int) -> Dict:
        """
        Allow user to retake assessment with adaptive difficulty.
        """
        previous_assessment = ProficiencyAssessment.query.get(previous_assessment_id)
        if not previous_assessment or previous_assessment.user_id != user_id:
            raise ValueError("Previous assessment not found or unauthorized")
        
        # Analyze previous performance to adapt new assessment
        if previous_assessment.ai_evaluation:
            adaptive_config = self._generate_adaptive_config(previous_assessment.ai_evaluation)
        else:
            adaptive_config = {'focus_areas': ['vocabulary', 'grammar'], 'difficulty': 'intermediate'}
        
        # Generate new adaptive assessment
        return self.generate_placement_assessment(user_id, 'adaptive')

    def generate_skill_specific_assessment(self, user_id: int, skill_area: str) -> Dict:
        """
        Generate assessment focused on a specific skill area.
        """
        if skill_area not in self.SKILL_AREAS:
            raise ValueError(f"Invalid skill area. Must be one of: {', '.join(self.SKILL_AREAS)}")
        
        assessment_data = self._generate_skill_focused_assessment(skill_area)
        
        # Create assessment record
        assessment = ProficiencyAssessment(
            user_id=user_id,
            assessment_type=f'skill_{skill_area}',
            questions_asked=assessment_data['questions']
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return {
            'assessment_id': assessment.id,
            'skill_area': skill_area,
            'questions': assessment_data['questions'],
            'metadata': assessment_data['metadata'],
            'instructions': assessment_data['instructions']
        }

    # Private helper methods
    
    def _generate_comprehensive_assessment(self) -> Dict:
        """Generate comprehensive assessment covering all skill areas."""
        questions = []
        total_score = 0
        skill_areas = []
        
        # Generate questions for each skill area and level
        for skill_area in self.SKILL_AREAS:
            skill_areas.append(skill_area)
            for level in self.ASSESSMENT_LEVELS:
                skill_questions = self._generate_skill_level_questions(skill_area, level, self.QUESTIONS_PER_LEVEL)
                # Ensure all questions have points field
                for question in skill_questions:
                    if 'points' not in question:
                        question['points'] = self._get_points_for_level(level)
                questions.extend(skill_questions)
                total_score += sum(q['points'] for q in skill_questions)
        
        structure = {
            'total_sections': len(self.SKILL_AREAS),
            'questions_per_skill': self.QUESTIONS_PER_SKILL * len(self.ASSESSMENT_LEVELS),
            'levels_tested': self.ASSESSMENT_LEVELS,
            'skills_tested': self.SKILL_AREAS
        }
        
        return {
            'questions': questions,
            'max_score': total_score,
            'estimated_duration': 45,  # 45 minutes
            'skill_areas': skill_areas,
            'structure': structure,
            'instructions': self._get_assessment_instructions('comprehensive'),
            'telugu_instructions': self._get_telugu_instructions('comprehensive')
        }

    def _generate_quick_assessment(self) -> Dict:
        """Generate quick 15-minute assessment."""
        questions = []
        total_score = 0
        
        # Select key skill areas for quick assessment
        key_skills = ['vocabulary', 'grammar', 'reading']
        
        for skill_area in key_skills:
            # One question per level for quick assessment
            for level in self.ASSESSMENT_LEVELS:
                skill_questions = self._generate_skill_level_questions(skill_area, level, 1)
                questions.extend(skill_questions)
                total_score += sum(q['points'] for q in skill_questions)
        
        structure = {
            'total_sections': len(key_skills),
            'questions_per_skill': len(self.ASSESSMENT_LEVELS),
            'levels_tested': self.ASSESSMENT_LEVELS,
            'skills_tested': key_skills
        }
        
        return {
            'questions': questions,
            'max_score': total_score,
            'estimated_duration': 15,
            'skill_areas': key_skills,
            'structure': structure,
            'instructions': self._get_assessment_instructions('quick'),
            'telugu_instructions': self._get_telugu_instructions('quick')
        }

    def _generate_adaptive_assessment(self) -> Dict:
        """Generate adaptive assessment that adjusts based on user responses."""
        # Start with intermediate level questions
        questions = []
        total_score = 0
        
        # Generate starter questions
        for skill_area in ['vocabulary', 'grammar']:
            skill_questions = self._generate_skill_level_questions(skill_area, 'intermediate', 2)
            # Ensure all questions have points field
            for question in skill_questions:
                if 'points' not in question:
                    question['points'] = self._get_points_for_level('intermediate')
            questions.extend(skill_questions)
            total_score += sum(q['points'] for q in skill_questions)
        
        structure = {
            'adaptive': True,
            'initial_questions': len(questions),
            'max_additional_questions': 20,
            'adaptation_logic': 'performance_based'
        }
        
        return {
            'questions': questions,
            'max_score': total_score,
            'estimated_duration': 30,
            'skill_areas': ['vocabulary', 'grammar'],
            'structure': structure,
            'instructions': self._get_assessment_instructions('adaptive'),
            'telugu_instructions': self._get_telugu_instructions('adaptive')
        }

    def _generate_skill_level_questions(self, skill_area: str, level: str, count: int) -> List[Dict]:
        """Generate questions for a specific skill area and level."""
        prompt = f"""
        Generate {count} English proficiency assessment questions for Telugu speakers.
        
        Requirements:
        - Skill Area: {skill_area}
        - Difficulty Level: {level}
        - Target Language: English (for Telugu speakers)
        
        For each question, provide:
        1. Clear question text
        2. Multiple choice options (4 options)
        3. Correct answer
        4. Points value (beginner: 2, intermediate: 3, advanced: 4)
        5. Telugu hint/translation if helpful
        6. Explanation for the correct answer
        
        Question types by skill area:
        - vocabulary: Word meaning, synonyms, usage in context
        - grammar: Sentence structure, tenses, prepositions
        - reading: Comprehension, inference, main ideas
        - listening: Audio comprehension (text-based simulation)
        - writing: Sentence formation, error correction
        
        Return in JSON format:
        ```json
        [
            {{
                "question_id": "q_{skill_area}_{level}_1",
                "question_text": "Choose the correct meaning of 'abundant':",
                "options": [
                    "Very little",
                    "More than enough", 
                    "Exactly right",
                    "Not available"
                ],
                "correct_answer": "B",
                "points": 2,
                "skill_area": "{skill_area}",
                "difficulty_level": "{level}",
                "telugu_hint": "సమృద్ధిగా అని అర్థం",
                "explanation": "Abundant means existing in large quantities; more than enough.",
                "question_type": "multiple_choice"
            }}
        ]
        ```
        """
        
        response = self.model.generate_content(prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        questions = _extract_json_from_response(response.text)
        
        # Ensure we have the right number of questions and add missing fields
        if isinstance(questions, list) and len(questions) >= count:
            processed_questions = questions[:count]
        elif isinstance(questions, dict):
            processed_questions = [questions]
        else:
            # Fallback questions if AI generation fails
            processed_questions = self._generate_fallback_questions(skill_area, level, count)
        
        # Ensure all questions have required fields
        for question in processed_questions:
            if 'points' not in question:
                question['points'] = self._get_points_for_level(level)
            if 'skill_area' not in question:
                question['skill_area'] = skill_area
            if 'difficulty_level' not in question:
                question['difficulty_level'] = level
                
        return processed_questions

    def _get_points_for_level(self, level: str) -> int:
        """Get points value for difficulty level."""
        points_map = {
            'beginner': 2,
            'intermediate': 3,
            'advanced': 4
        }
        return points_map.get(level, 2)

    def _generate_fallback_questions(self, skill_area: str, level: str, count: int) -> List[Dict]:
        """Generate fallback questions if AI generation fails."""
        fallback_questions = {
            'vocabulary': {
                'beginner': {
                    'question_text': 'What does "hello" mean in Telugu?',
                    'options': ['నమస్కారం', 'వీడ్కోలు', 'ధన్యవాదాలు', 'క్షమించండి'],
                    'correct_answer': 'A'
                },
                'intermediate': {
                    'question_text': 'Choose the synonym for "happy":',
                    'options': ['Sad', 'Joyful', 'Angry', 'Tired'], 
                    'correct_answer': 'B'
                },
                'advanced': {
                    'question_text': 'What does "ubiquitous" mean?',
                    'options': ['Rare', 'Present everywhere', 'Ancient', 'Mysterious'],
                    'correct_answer': 'B'
                }
            }
        }
        
        points_map = {'beginner': 2, 'intermediate': 3, 'advanced': 4}
        
        questions = []
        for i in range(count):
            template = fallback_questions.get(skill_area, {}).get(level)
            if template:
                question = {
                    'question_id': f'fallback_{skill_area}_{level}_{i+1}',
                    'question_text': template['question_text'],
                    'options': template['options'],
                    'correct_answer': template['correct_answer'],
                    'points': points_map[level],
                    'skill_area': skill_area,
                    'difficulty_level': level,
                    'telugu_hint': 'సూచన అందుబాటులో లేదు',
                    'explanation': 'Standard assessment question',
                    'question_type': 'multiple_choice'
                }
                questions.append(question)
        
        return questions

    def _evaluate_assessment_answers(self, questions: List[Dict], answers: Dict) -> Dict:
        """Evaluate user answers against correct answers."""
        evaluation = {
            'total_score': 0,
            'max_possible_score': 0,
            'skill_scores': {},
            'level_scores': {},
            'question_results': []
        }
        
        # Initialize skill and level tracking
        for skill in self.SKILL_AREAS:
            evaluation['skill_scores'][skill] = {'score': 0, 'max_score': 0, 'questions': 0}
        
        for level in self.ASSESSMENT_LEVELS:
            evaluation['level_scores'][level] = {'score': 0, 'max_score': 0, 'questions': 0}
        
        # Evaluate each question
        for question in questions:
            question_id = question['question_id']
            correct_answer = question['correct_answer']
            points = question['points']
            skill_area = question['skill_area']
            difficulty_level = question['difficulty_level']
            
            user_answer = answers.get(question_id, '').strip().upper()
            is_correct = user_answer == correct_answer.upper()
            
            # Update totals
            evaluation['max_possible_score'] += points
            if is_correct:
                evaluation['total_score'] += points
            
            # Update skill scores
            evaluation['skill_scores'][skill_area]['max_score'] += points
            evaluation['skill_scores'][skill_area]['questions'] += 1
            if is_correct:
                evaluation['skill_scores'][skill_area]['score'] += points
            
            # Update level scores
            evaluation['level_scores'][difficulty_level]['max_score'] += points
            evaluation['level_scores'][difficulty_level]['questions'] += 1
            if is_correct:
                evaluation['level_scores'][difficulty_level]['score'] += points
            
            # Track individual question result
            question_result = {
                'question_id': question_id,
                'correct': is_correct,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'points_earned': points if is_correct else 0,
                'points_possible': points,
                'skill_area': skill_area,
                'difficulty_level': difficulty_level
            }
            evaluation['question_results'].append(question_result)
        
        # Calculate percentages
        for skill in evaluation['skill_scores']:
            skill_data = evaluation['skill_scores'][skill]
            if skill_data['max_score'] > 0:
                skill_data['percentage'] = (skill_data['score'] / skill_data['max_score']) * 100
            else:
                skill_data['percentage'] = 0
        
        for level in evaluation['level_scores']:
            level_data = evaluation['level_scores'][level]
            if level_data['max_score'] > 0:
                level_data['percentage'] = (level_data['score'] / level_data['max_score']) * 100
            else:
                level_data['percentage'] = 0
        
        return evaluation

    def _analyze_proficiency_level(self, evaluation_result: Dict) -> Dict:
        """Analyze overall proficiency level based on evaluation results."""
        total_percentage = (evaluation_result['total_score'] / evaluation_result['max_possible_score']) * 100
        
        # Determine overall level
        if total_percentage >= 80:
            overall_level = 'advanced'
        elif total_percentage >= 60:
            overall_level = 'intermediate'
        else:
            overall_level = 'beginner'
        
        # Analyze skill breakdown
        skill_breakdown = {}
        strengths = []
        weaknesses = []
        
        for skill, data in evaluation_result['skill_scores'].items():
            percentage = data['percentage']
            
            if percentage >= 75:
                skill_level = 'strong'
                strengths.append(skill)
            elif percentage >= 50:
                skill_level = 'developing'
            else:
                skill_level = 'needs_improvement'
                weaknesses.append(skill)
            
            skill_breakdown[skill] = {
                'level': skill_level,
                'percentage': percentage,
                'score': data['score'],
                'max_score': data['max_score']
            }
        
        # Analyze level performance
        level_analysis = {}
        for level, data in evaluation_result['level_scores'].items():
            level_analysis[level] = {
                'percentage': data['percentage'],
                'ready_for_next': data['percentage'] >= 70
            }
        
        return {
            'overall_level': overall_level,
            'overall_percentage': total_percentage,
            'skill_breakdown': skill_breakdown,
            'level_analysis': level_analysis,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'confidence_score': min(total_percentage / 100, 1.0)
        }

    def _recommend_learning_paths(self, proficiency_analysis: Dict) -> Dict:
        """Recommend appropriate learning paths based on proficiency analysis."""
        overall_level = proficiency_analysis['overall_level']
        strengths = proficiency_analysis['strengths']
        weaknesses = proficiency_analysis['weaknesses']
        
        # Get available learning paths
        available_paths = LearningPath.query.filter_by(difficulty_level=overall_level, is_active=True).all()
        
        recommendations = {
            'primary_path': None,
            'alternative_paths': [],
            'skill_specific_paths': [],
            'custom_path_suggestions': []
        }
        
        # Recommend primary path
        if available_paths:
            primary_path = available_paths[0]
            recommendations['primary_path'] = {
                'id': primary_path.id,
                'title': primary_path.title,
                'description': primary_path.description,
                'difficulty_level': primary_path.difficulty_level,
                'estimated_duration_weeks': primary_path.estimated_duration_weeks,
                'match_reason': f'Matches your {overall_level} proficiency level'
            }
            
            # Add alternative paths
            for path in available_paths[1:3]:  # Up to 2 alternatives
                recommendations['alternative_paths'].append({
                    'id': path.id,
                    'title': path.title,
                    'description': path.description,
                    'difficulty_level': path.difficulty_level
                })
        
        # Recommend skill-specific focus areas
        for weakness in weaknesses[:2]:  # Top 2 weaknesses
            recommendations['skill_specific_paths'].append({
                'skill_area': weakness,
                'focus_type': 'remedial',
                'recommended_activities': [
                    f'Daily {weakness} practice',
                    f'{weakness.title()} fundamentals course',
                    f'Interactive {weakness} exercises'
                ],
                'estimated_improvement_time': '2-4 weeks'
            })
        
        # Custom path suggestions based on analysis
        custom_suggestions = self._generate_custom_path_suggestions(proficiency_analysis)
        recommendations['custom_path_suggestions'] = custom_suggestions
        
        return recommendations

    def _generate_custom_path_suggestions(self, proficiency_analysis: Dict) -> List[Dict]:
        """Generate custom learning path suggestions."""
        suggestions = []
        
        overall_level = proficiency_analysis['overall_level']
        weaknesses = proficiency_analysis['weaknesses']
        strengths = proficiency_analysis['strengths']
        
        # Balanced approach suggestion
        suggestions.append({
            'path_type': 'balanced',
            'title': 'Comprehensive English Mastery',
            'description': 'Balanced approach covering all skill areas with emphasis on weak points',
            'focus_areas': weaknesses + strengths[:2],
            'weekly_structure': {
                'skill_practice': '3 days/week',
                'conversation': '2 days/week',
                'review': '1 day/week',
                'assessment': '1 day/week'
            },
            'estimated_duration': '8-12 weeks'
        })
        
        # Intensive improvement suggestion
        if weaknesses:
            suggestions.append({
                'path_type': 'intensive',
                'title': 'Targeted Skill Improvement',
                'description': f'Intensive focus on {", ".join(weaknesses)} with rapid improvement goals',
                'focus_areas': weaknesses,
                'weekly_structure': {
                    'intensive_practice': '5 days/week',
                    'application': '1 day/week',
                    'assessment': '1 day/week'
                },
                'estimated_duration': '4-6 weeks'
            })
        
        # Strength-based suggestion
        if strengths:
            suggestions.append({
                'path_type': 'advanced',
                'title': 'Advanced Application Path',
                'description': f'Build on your strengths in {", ".join(strengths)} for advanced applications',
                'focus_areas': strengths,
                'weekly_structure': {
                    'advanced_practice': '3 days/week',
                    'real_world_application': '2 days/week',
                    'creative_exercises': '2 days/week'
                },
                'estimated_duration': '6-8 weeks'
            })
        
        return suggestions

    def _generate_assessment_report(self, assessment: ProficiencyAssessment, 
                                  evaluation_result: Dict, proficiency_analysis: Dict, 
                                  learning_path_recommendations: Dict) -> Dict:
        """Generate comprehensive assessment report."""
        report = {
            'assessment_summary': {
                'assessment_id': assessment.id,
                'assessment_type': assessment.assessment_type,
                'completion_date': assessment.completed_at.isoformat(),
                'duration_minutes': self._calculate_assessment_duration(assessment),
                'overall_score': f"{evaluation_result['total_score']}/{evaluation_result['max_possible_score']}",
                'percentage': round((evaluation_result['total_score'] / evaluation_result['max_possible_score']) * 100, 1)
            },
            'proficiency_analysis': proficiency_analysis,
            'skill_performance': self._format_skill_performance(evaluation_result['skill_scores']),
            'level_readiness': self._format_level_readiness(evaluation_result['level_scores']),
            'strengths_and_weaknesses': {
                'top_strengths': proficiency_analysis['strengths'][:3],
                'improvement_areas': proficiency_analysis['weaknesses'][:3],
                'overall_assessment': self._generate_overall_assessment_text(proficiency_analysis)
            },
            'learning_recommendations': learning_path_recommendations,
            'next_steps': self._generate_detailed_next_steps(proficiency_analysis, learning_path_recommendations),
            'telugu_summary': self._generate_telugu_report_summary(proficiency_analysis),
            'progress_tracking': {
                'baseline_established': True,
                'recommended_reassessment': '4-6 weeks',
                'key_metrics_to_track': self._get_tracking_metrics(proficiency_analysis)
            }
        }
        
        return report

    def _generate_next_steps(self, proficiency_analysis: Dict, 
                           learning_path_recommendations: Dict) -> List[Dict]:
        """Generate immediate next steps for the user."""
        next_steps = []
        
        # Step 1: Choose learning path
        if learning_path_recommendations.get('primary_path'):
            next_steps.append({
                'step': 1,
                'action': 'Choose Your Learning Path',
                'description': 'Select a learning path that matches your goals and schedule',
                'options': [
                    learning_path_recommendations['primary_path']['title'],
                    'Custom path based on your specific needs',
                    'Skill-specific focus areas'
                ],
                'estimated_time': '5 minutes',
                'telugu_action': 'మీ అభ్యాస మార్గాన్ని ఎంచుకోండి'
            })
        
        # Step 2: Start with weak areas
        if proficiency_analysis['weaknesses']:
            next_steps.append({
                'step': 2,
                'action': 'Begin Focused Practice',
                'description': f"Start with {proficiency_analysis['weaknesses'][0]} exercises to build foundation",
                'specific_activities': [
                    f"Complete 3 {proficiency_analysis['weaknesses'][0]} exercises",
                    "Review fundamental concepts",
                    "Practice daily for 15-20 minutes"
                ],
                'estimated_time': '20 minutes daily',
                'telugu_action': 'దృష్టి కేంద్రీకృత అభ్యాసం ప్రారంభించండి'
            })
        
        # Step 3: Set goals and tracking
        next_steps.append({
            'step': 3,
            'action': 'Set Learning Goals',
            'description': 'Define specific, measurable goals for your English learning journey',
            'goal_suggestions': [
                'Improve vocabulary by 50 words/week',
                'Achieve 80% accuracy in grammar exercises',
                'Complete 5 reading comprehension activities/week'
            ],
            'estimated_time': '10 minutes',
            'telugu_action': 'అభ్యాస లక్ష్యాలను నిర్ణయించండి'
        })
        
        return next_steps

    def _get_assessment_instructions(self, assessment_type: str) -> str:
        """Get English instructions for assessment."""
        instructions = {
            'comprehensive': """
                Welcome to your English Proficiency Assessment!
                
                This comprehensive assessment will evaluate your English skills across multiple areas:
                - Vocabulary and word knowledge
                - Grammar and sentence structure  
                - Reading comprehension
                - Listening skills
                - Writing abilities
                
                Instructions:
                1. Read each question carefully
                2. Choose the best answer from the given options
                3. Take your time - there's no strict time limit
                4. If unsure, make your best guess
                5. You can use Telugu hints when provided
                
                The assessment takes approximately 45 minutes to complete.
                Your results will help us create a personalized learning path for you.
            """,
            'quick': """
                Quick English Proficiency Check
                
                This is a shortened assessment focusing on key English skills:
                - Essential vocabulary
                - Basic grammar
                - Reading comprehension
                
                Instructions:
                1. Answer all questions to the best of your ability
                2. Choose one option for each question
                3. This should take about 15 minutes
                
                Your results will give us a general idea of your English level.
            """,
            'adaptive': """
                Adaptive English Assessment
                
                This assessment adapts to your responses, providing questions that match your skill level.
                
                Instructions:
                1. Start with the given questions
                2. Additional questions may be presented based on your answers
                3. Take your time with each question
                4. The assessment ends when we have enough information about your level
                
                Expected duration: 20-30 minutes.
            """
        }
        
        return instructions.get(assessment_type, instructions['comprehensive'])

    def _get_telugu_instructions(self, assessment_type: str) -> str:
        """Get Telugu instructions for assessment."""
        instructions = {
            'comprehensive': """
                మీ ఇంగ్లీష్ ప్రావీణ్య మూల్యాంకనకు స్వాగతం!
                
                ఈ సమగ్ర మూల్యాంకనం మీ ఇంగ్లీష్ నైపుణ్యాలను అనేక రంగాలలో అంచనా వేస్తుంది:
                - పదజాలం మరియు పద జ్ఞానం
                - వ్యాకరణం మరియు వాక్య నిర్మాణం
                - పఠన గ్రహణ
                - వినికిడి నైపుణ్యాలు
                - రచనా సామర్థ్యాలు
                
                సూచనలు:
                1. ప్రతి ప్రశ్నను జాగ్రత్తగా చదవండి
                2. ఇవ్వబడిన ఎంపికలలో నుండి ఉత్తమ సమాధానాన్ని ఎంచుకోండి
                3. మీ సమయాన్ని తీసుకోండి - కఠినమైన సమయ పరిమితి లేదు
                4. ఖచ్చితంగా తెలియకపోతే, మీ ఉత్తమ అంచనా వేయండి
                5. అందించినప్పుడు తెలుగు సూచనలను ఉపయోగించవచ్చు
                
                మూల్యాంకనం పూర్తి చేయడానికి సుమారు 45 నిమిషాలు పడుతుంది.
                మీ ఫలితాలు మీ కోసం వ్యక్తిగతీకరించిన అభ్యాస మార్గాన్ని రూపొందించడంలో సహాయపడతాయి.
            """,
            'quick': """
                త్వరిత ఇంగ్లీష్ ప్రావీణ్య తనిఖీ
                
                ఇది కీలకమైన ఇంగ్లీష్ నైపుణ్యాలపై దృష్టి సారించే సంక్షిప్త మూల్యాంకనం:
                - అవసరమైన పదజాలం
                - ప్రాథమిక వ్యాకరణం
                - పఠన గ్రహణ
                
                సూచనలు:
                1. మీ సామర్థ్యానుసారం అన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి
                2. ప్రతి ప్రశ్నకు ఒక ఎంపికను ఎంచుకోండి
                3. ఇది సుమారు 15 నిమిషాలు పట్టాలి
                
                మీ ఫలితాలు మీ ఇంగ్లీష్ స్థాయి గురించి సాధారణ ఆలోచనను ఇస్తాయి.
            """,
            'adaptive': """
                అనుకూల ఇంగ్లీష్ మూల్యాంకనం
                
                ఈ మూల్యాంకనం మీ స్పందనలకు అనుగుణంగా మారుతుంది, మీ నైపుణ్య స్థాయికి సరిపోలే ప్రశ్నలను అందిస్తుంది.
                
                సూచనలు:
                1. ఇవ్వబడిన ప్రశ్నలతో ప్రారంభించండి
                2. మీ సమాధానాల ఆధారంగా అదనపు ప్రశ్నలు అందించవచ్చు
                3. ప్రతి ప్రశ్నతో మీ సమయాన్ని తీసుకోండి
                4. మీ స్థాయి గురించి తగినంత సమాచారం వచ్చినప్పుడు మూల్యాంకనం ముగుస్తుంది
                
                అంచనా వ్యవధి: 20-30 నిమిషాలు.
            """
        }
        
        return instructions.get(assessment_type, instructions['comprehensive'])

    def _calculate_assessment_duration(self, assessment: ProficiencyAssessment) -> Optional[int]:
        """Calculate assessment duration in minutes."""
        if assessment.started_at and assessment.completed_at:
            duration = assessment.completed_at - assessment.started_at
            return int(duration.total_seconds() / 60)
        return None

    def _format_skill_performance(self, skill_scores: Dict) -> Dict:
        """Format skill performance for report."""
        formatted = {}
        for skill, data in skill_scores.items():
            formatted[skill] = {
                'percentage': round(data['percentage'], 1),
                'score': f"{data['score']}/{data['max_score']}",
                'level': 'Strong' if data['percentage'] >= 75 else 'Developing' if data['percentage'] >= 50 else 'Needs Improvement',
                'questions_answered': data['questions']
            }
        return formatted

    def _format_level_readiness(self, level_scores: Dict) -> Dict:
        """Format level readiness information."""
        formatted = {}
        for level, data in level_scores.items():
            formatted[level] = {
                'percentage': round(data['percentage'], 1),
                'ready': data['percentage'] >= 70,
                'confidence': 'High' if data['percentage'] >= 80 else 'Medium' if data['percentage'] >= 60 else 'Low'
            }
        return formatted

    def _generate_overall_assessment_text(self, proficiency_analysis: Dict) -> str:
        """Generate overall assessment text."""
        level = proficiency_analysis['overall_level']
        percentage = proficiency_analysis['overall_percentage']
        
        if level == 'advanced':
            return f"Excellent performance with {percentage:.1f}% overall accuracy. You demonstrate strong command of English across multiple skill areas."
        elif level == 'intermediate':
            return f"Good performance with {percentage:.1f}% overall accuracy. You have a solid foundation with room for targeted improvement."
        else:
            return f"Developing skills with {percentage:.1f}% overall accuracy. Focus on building fundamental skills will help you progress quickly."

    def _generate_detailed_next_steps(self, proficiency_analysis: Dict, 
                                    learning_path_recommendations: Dict) -> List[str]:
        """Generate detailed next steps list."""
        steps = []
        
        # Immediate actions based on level
        level = proficiency_analysis['overall_level']
        if level == 'beginner':
            steps.extend([
                "Start with vocabulary building exercises daily",
                "Focus on basic grammar patterns",
                "Practice simple reading comprehension",
                "Use Telugu-English translation exercises"
            ])
        elif level == 'intermediate':
            steps.extend([
                "Expand vocabulary with topic-specific words",
                "Practice complex sentence structures",
                "Engage in conversation practice",
                "Work on listening comprehension skills"
            ])
        else:  # advanced
            steps.extend([
                "Focus on nuanced vocabulary and idioms",
                "Practice advanced writing techniques", 
                "Engage in debates and discussions",
                "Read advanced texts and literature"
            ])
        
        # Add weakness-specific steps
        for weakness in proficiency_analysis['weaknesses'][:2]:
            steps.append(f"Dedicate extra time to {weakness} practice sessions")
        
        return steps

    def _generate_telugu_report_summary(self, proficiency_analysis: Dict) -> str:
        """Generate Telugu summary of the report."""
        level = proficiency_analysis['overall_level']
        percentage = proficiency_analysis['overall_percentage']
        
        level_telugu = {
            'beginner': 'ప్రాథమిక',
            'intermediate': 'మధ్యస్థ', 
            'advanced': 'ఉన్నత'
        }
        
        summary = f"""
        మీ ఇంగ్లీష్ ప్రావీణ్య స్థాయి: {level_telugu.get(level, level)}
        మొత్తం స్కోర్: {percentage:.1f}%
        
        """
        
        if proficiency_analysis['strengths']:
            summary += f"మీ బలాలు: {', '.join(proficiency_analysis['strengths'])}\n"
        
        if proficiency_analysis['weaknesses']:
            summary += f"మెరుగుపరచవలసిన రంగాలు: {', '.join(proficiency_analysis['weaknesses'])}\n"
        
        summary += "\nమీ అభ్యాస ప్రయాణం కోసం వ్యక్తిగతీకరించిన సిఫార్సులు తయారు చేయబడ్డాయి."
        
        return summary

    def _get_tracking_metrics(self, proficiency_analysis: Dict) -> List[str]:
        """Get key metrics to track progress."""
        metrics = [
            'Overall accuracy percentage',
            'Vocabulary acquisition rate',
            'Grammar accuracy improvement',
            'Reading comprehension speed'
        ]
        
        # Add weakness-specific metrics
        for weakness in proficiency_analysis['weaknesses']:
            metrics.append(f'{weakness.title()} skill improvement')
        
        return metrics

    def _generate_adaptive_config(self, previous_results: Dict) -> Dict:
        """Generate adaptive configuration based on previous assessment."""
        # Analyze previous weak areas for focused assessment
        skill_scores = previous_results.get('skill_scores', {})
        focus_areas = []
        
        for skill, data in skill_scores.items():
            if data.get('percentage', 0) < 60:
                focus_areas.append(skill)
        
        # Determine starting difficulty
        overall_percentage = (previous_results.get('total_score', 0) / 
                            previous_results.get('max_possible_score', 1)) * 100
        
        if overall_percentage >= 70:
            difficulty = 'intermediate'
        elif overall_percentage >= 40:
            difficulty = 'beginner_plus'
        else:
            difficulty = 'beginner'
        
        return {
            'focus_areas': focus_areas[:3],  # Top 3 weak areas
            'difficulty': difficulty,
            'questions_per_area': 3
        }

    def _generate_skill_focused_assessment(self, skill_area: str) -> Dict:
        """Generate assessment focused on specific skill area."""
        questions = []
        total_score = 0
        
        # Generate questions across levels for the specific skill
        for level in self.ASSESSMENT_LEVELS:
            skill_questions = self._generate_skill_level_questions(skill_area, level, 2)
            questions.extend(skill_questions)
            total_score += sum(q['points'] for q in skill_questions)
        
        return {
            'questions': questions,
            'max_score': total_score,
            'metadata': {
                'skill_focus': skill_area,
                'total_questions': len(questions),
                'levels_covered': self.ASSESSMENT_LEVELS,
                'estimated_duration': 20
            },
            'instructions': {
                'english': f"This assessment focuses specifically on {skill_area} skills. Complete all questions to get an accurate assessment of your {skill_area} proficiency.",
                'telugu': f"ఈ మూల్యాంకనం ప్రత్యేకంగా {skill_area} నైపుణ్యాలపై దృష్టి పెడుతుంది। మీ {skill_area} ప్రావీణ్యం యొక్క ఖచ్చితమైన మూల్యాంకనం పొందడానికి అన్ని ప్రశ్నలను పూర్తి చేయండి।"
            }
        }