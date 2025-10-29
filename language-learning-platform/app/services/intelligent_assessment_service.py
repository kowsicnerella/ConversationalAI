"""
Intelligent Assessment Engine Service

Implements comprehensive assessment system with:
- IRT (Item Response Theory) 3-Parameter Logistic Model
- Adaptive question selection based on ability estimation
- Multi-stage assessment orchestration
- Skill diagnostics and gap analysis
- Comparative analytics and percentile rankings
- Certification readiness determination

Author: AI Learning Platform
Date: October 20, 2025
"""

import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from sqlalchemy import func, and_, or_
from app.models import db
from app.models.intelligent_assessment import (
    Assessment,
    AssessmentQuestion,
    UserAssessmentAttempt,
    QuestionResponse,
    AssessmentResult,
    SkillDiagnostic,
    AdaptiveTestSession
)
from app.models.user import User
from app.services.llm_service import LLMService


class IntelligentAssessmentEngine:
    """
    Core engine for intelligent assessment system with IRT-based adaptive testing.
    """
    
    def __init__(self):
        self.llm_service = LLMService()
        
        # IRT Constants
        self.DEFAULT_THETA = 0.0  # Average ability
        self.THETA_MIN = -3.0  # Beginner
        self.THETA_MAX = 3.0   # Expert
        self.THETA_SD = 1.0    # Standard deviation for ability distribution
        
        # Adaptive Testing Parameters
        self.DEFAULT_SE_THRESHOLD = 0.3  # Standard error threshold for stopping
        self.MIN_QUESTIONS = 5  # Minimum questions before stopping
        self.MAX_QUESTIONS = 50  # Maximum questions regardless of precision
        
        # IRT 3PL Model defaults
        self.DEFAULT_DISCRIMINATION = 1.0  # 'a' parameter
        self.DEFAULT_DIFFICULTY = 0.0      # 'b' parameter
        self.DEFAULT_GUESSING = 0.2        # 'c' parameter (20% guessing chance)
        
        # Skill categorization
        self.PROFICIENCY_LEVELS = {
            'beginner': (-3.0, -1.0),
            'elementary': (-1.0, 0.0),
            'intermediate': (0.0, 1.0),
            'advanced': (1.0, 2.0),
            'expert': (2.0, 3.0)
        }
    
    # ================================================================
    # ASSESSMENT CREATION AND MANAGEMENT
    # ================================================================
    
    def create_assessment(
        self,
        title: str,
        description: str,
        assessment_type: str,
        target_language: str = 'Telugu',
        proficiency_level: Optional[str] = None,
        skill_areas: Optional[List[str]] = None,
        is_adaptive: bool = True,
        duration_minutes: Optional[int] = None,
        passing_score: Optional[float] = None,
        certification_name: Optional[str] = None,
        irt_config: Optional[Dict] = None,
        created_by: Optional[int] = None
    ) -> Assessment:
        """
        Create a new assessment template.
        
        Args:
            title: Assessment title
            description: Detailed description
            assessment_type: 'placement', 'progress', 'mastery', 'certification'
            target_language: Language being assessed
            proficiency_level: Target proficiency (if applicable)
            skill_areas: List of skill areas to assess
            is_adaptive: Whether to use adaptive testing
            duration_minutes: Time limit (optional)
            passing_score: Minimum passing percentage (optional)
            certification_name: Certificate name (for certification type)
            irt_config: IRT-specific configuration
            created_by: User ID who created this assessment
            
        Returns:
            Created Assessment object
        """
        assessment = Assessment(
            title=title,
            description=description,
            assessment_type=assessment_type,
            target_language=target_language,
            proficiency_level=proficiency_level,
            skill_areas=skill_areas or [],
            is_adaptive=is_adaptive,
            duration_minutes=duration_minutes,
            passing_score=passing_score,
            certification_name=certification_name,
            irt_config=irt_config or {},
            created_by=created_by
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return assessment
    
    def add_question_to_assessment(
        self,
        assessment_id: int,
        question_text: str,
        question_type: str,
        correct_answer: str,
        options: Optional[List[str]] = None,
        skill_area: Optional[str] = None,
        sub_skills: Optional[List[str]] = None,
        difficulty_level: Optional[str] = None,
        irt_params: Optional[Dict] = None,
        explanation: Optional[str] = None,
        context: Optional[str] = None
    ) -> AssessmentQuestion:
        """
        Add a question to an assessment with IRT parameters.
        
        Args:
            assessment_id: Assessment to add question to
            question_text: The question text
            question_type: Type of question
            correct_answer: Correct answer
            options: Answer options (for multiple choice)
            skill_area: Primary skill being tested
            sub_skills: Sub-skills tested
            difficulty_level: Human-readable difficulty
            irt_params: IRT parameters (a, b, c)
            explanation: Answer explanation
            context: Additional context
            
        Returns:
            Created AssessmentQuestion object
        """
        # Set default IRT parameters if not provided
        if not irt_params:
            irt_params = {
                'discrimination': self.DEFAULT_DISCRIMINATION,
                'difficulty': self.DEFAULT_DIFFICULTY,
                'guessing': self.DEFAULT_GUESSING
            }
        
        question = AssessmentQuestion(
            assessment_id=assessment_id,
            question_text=question_text,
            question_type=question_type,
            correct_answer=correct_answer,
            options=options or [],
            skill_area=skill_area,
            sub_skills=sub_skills or [],
            difficulty_level=difficulty_level,
            irt_discrimination=irt_params.get('discrimination', self.DEFAULT_DISCRIMINATION),
            irt_difficulty=irt_params.get('difficulty', self.DEFAULT_DIFFICULTY),
            irt_guessing=irt_params.get('guessing', self.DEFAULT_GUESSING),
            explanation=explanation,
            context=context
        )
        
        db.session.add(question)
        db.session.commit()
        
        return question
    
    # ================================================================
    # IRT 3-PARAMETER LOGISTIC MODEL
    # ================================================================
    
    def calculate_probability_correct(
        self,
        theta: float,
        discrimination: float,
        difficulty: float,
        guessing: float
    ) -> float:
        """
        Calculate probability of correct response using 3PL IRT model.
        
        P(θ) = c + (1-c) / (1 + e^(-a(θ-b)))
        
        where:
        θ = ability (theta)
        a = discrimination
        b = difficulty
        c = guessing parameter
        
        Args:
            theta: Examinee's ability level
            discrimination: Item discrimination parameter (a)
            difficulty: Item difficulty parameter (b)
            guessing: Pseudo-guessing parameter (c)
            
        Returns:
            Probability of correct response (0-1)
        """
        try:
            exponent = -discrimination * (theta - difficulty)
            probability = guessing + (1 - guessing) / (1 + math.exp(exponent))
            return max(0.0, min(1.0, probability))  # Clamp to [0, 1]
        except (OverflowError, ValueError):
            # Handle extreme values
            if exponent > 20:
                return guessing
            else:
                return 1.0
    
    def calculate_information(
        self,
        theta: float,
        discrimination: float,
        difficulty: float,
        guessing: float
    ) -> float:
        """
        Calculate Fisher information for an item at given ability level.
        
        Information indicates how well the item discriminates at this ability level.
        Higher information = better measurement precision.
        
        I(θ) = a² * P'(θ)² / (P(θ) * (1 - P(θ)))
        
        Args:
            theta: Ability level
            discrimination: Item discrimination (a)
            difficulty: Item difficulty (b)
            guessing: Guessing parameter (c)
            
        Returns:
            Information value (higher = more informative)
        """
        prob = self.calculate_probability_correct(theta, discrimination, difficulty, guessing)
        
        # Derivative of probability function
        exponent = -discrimination * (theta - difficulty)
        try:
            exp_val = math.exp(exponent)
            denominator = (1 + exp_val) ** 2
            
            prob_prime = discrimination * (1 - guessing) * exp_val / denominator
            
            # Calculate information
            if prob > 0.01 and prob < 0.99:  # Avoid division by zero
                information = (prob_prime ** 2) / (prob * (1 - prob))
                return information
            else:
                return 0.0
        except (OverflowError, ValueError):
            return 0.0
    
    def estimate_theta_eap(
        self,
        responses: List[Tuple[float, float, float, bool]],
        prior_mean: float = 0.0,
        prior_sd: float = 1.0
    ) -> Tuple[float, float]:
        """
        Estimate ability (theta) using Expected A Posteriori (EAP) method.
        
        EAP is more stable than MLE for small sample sizes and provides
        posterior standard deviation as precision measure.
        
        Args:
            responses: List of (discrimination, difficulty, guessing, is_correct) tuples
            prior_mean: Prior distribution mean
            prior_sd: Prior distribution standard deviation
            
        Returns:
            Tuple of (theta_estimate, standard_error)
        """
        # Quadrature points for numerical integration
        num_points = 40
        theta_points = [
            self.THETA_MIN + (self.THETA_MAX - self.THETA_MIN) * i / (num_points - 1)
            for i in range(num_points)
        ]
        
        # Calculate posterior at each point
        posteriors = []
        for theta in theta_points:
            # Prior probability (normal distribution)
            prior_prob = math.exp(-0.5 * ((theta - prior_mean) / prior_sd) ** 2)
            
            # Likelihood (product of response probabilities)
            likelihood = 1.0
            for disc, diff, guess, correct in responses:
                prob = self.calculate_probability_correct(theta, disc, diff, guess)
                likelihood *= prob if correct else (1 - prob)
            
            posteriors.append(prior_prob * likelihood)
        
        # Normalize posteriors
        total = sum(posteriors)
        if total == 0:
            return (prior_mean, prior_sd)
        
        posteriors = [p / total for p in posteriors]
        
        # Calculate EAP estimate (expected value)
        theta_eap = sum(theta * post for theta, post in zip(theta_points, posteriors))
        
        # Calculate standard error (posterior standard deviation)
        variance = sum(
            ((theta - theta_eap) ** 2) * post
            for theta, post in zip(theta_points, posteriors)
        )
        standard_error = math.sqrt(variance)
        
        return (theta_eap, standard_error)
    
    # ================================================================
    # ADAPTIVE QUESTION SELECTION
    # ================================================================
    
    def select_next_question(
        self,
        assessment_id: int,
        current_theta: float,
        answered_question_ids: List[int],
        skill_coverage: Optional[Dict[str, int]] = None
    ) -> Optional[AssessmentQuestion]:
        """
        Select next question using maximum information criterion.
        
        Balances information maximization with skill coverage requirements.
        
        Args:
            assessment_id: Assessment being taken
            current_theta: Current ability estimate
            answered_question_ids: Questions already answered
            skill_coverage: Dict of skill_area -> num_questions answered
            
        Returns:
            Next question to present, or None if no suitable questions
        """
        # Get all unanswered questions for this assessment
        query = AssessmentQuestion.query.filter(
            AssessmentQuestion.assessment_id == assessment_id,
            AssessmentQuestion.is_active == True
        )
        
        if answered_question_ids:
            query = query.filter(
                ~AssessmentQuestion.id.in_(answered_question_ids)
            )
        
        available_questions = query.all()
        
        if not available_questions:
            return None
        
        # Calculate information for each question
        question_info = []
        for question in available_questions:
            information = self.calculate_information(
                current_theta,
                question.irt_discrimination,
                question.irt_difficulty,
                question.irt_guessing
            )
            
            # Apply skill coverage bonus
            coverage_bonus = 1.0
            if skill_coverage and question.skill_area:
                coverage_count = skill_coverage.get(question.skill_area, 0)
                # Prefer under-covered skills
                coverage_bonus = 1.0 + (1.0 / (1.0 + coverage_count))
            
            adjusted_info = information * coverage_bonus
            question_info.append((question, adjusted_info))
        
        # Sort by information (descending)
        question_info.sort(key=lambda x: x[1], reverse=True)
        
        # Select from top 3 questions (add some randomness)
        top_candidates = question_info[:min(3, len(question_info))]
        selected_question = random.choice(top_candidates)[0]
        
        return selected_question
    
    # ================================================================
    # ASSESSMENT SESSION MANAGEMENT
    # ================================================================
    
    def start_assessment(
        self,
        user_id: int,
        assessment_id: int,
        initial_theta: Optional[float] = None
    ) -> Tuple[UserAssessmentAttempt, AdaptiveTestSession]:
        """
        Start a new assessment attempt for a user.
        
        Args:
            user_id: User taking the assessment
            assessment_id: Assessment being taken
            initial_theta: Starting ability estimate (uses default if None)
            
        Returns:
            Tuple of (UserAssessmentAttempt, AdaptiveTestSession)
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        # Use provided initial theta or default
        if initial_theta is None:
            # Check user's previous assessments for better initial estimate
            previous_attempts = UserAssessmentAttempt.query.filter_by(
                user_id=user_id
            ).order_by(UserAssessmentAttempt.completed_at.desc()).first()
            
            if previous_attempts and previous_attempts.final_theta_estimate:
                initial_theta = previous_attempts.final_theta_estimate
            else:
                initial_theta = self.DEFAULT_THETA
        
        # Create attempt record
        attempt = UserAssessmentAttempt(
            user_id=user_id,
            assessment_id=assessment_id,
            status='in_progress',
            current_theta_estimate=initial_theta,
            theta_standard_error=self.THETA_SD,
            questions_answered=0,
            correct_count=0
        )
        
        db.session.add(attempt)
        db.session.flush()  # Get attempt ID
        
        # Create adaptive session if adaptive mode
        adaptive_session = None
        if assessment.is_adaptive:
            adaptive_session = AdaptiveTestSession(
                attempt_id=attempt.id,
                current_theta=initial_theta,
                theta_se=self.THETA_SD,
                questions_administered=0
            )
            db.session.add(adaptive_session)
        
        db.session.commit()
        
        return (attempt, adaptive_session)
    
    def get_next_question_for_attempt(
        self,
        attempt_id: int
    ) -> Optional[Dict]:
        """
        Get the next question for an ongoing assessment attempt.
        
        Args:
            attempt_id: Assessment attempt ID
            
        Returns:
            Question data dict or None if assessment complete
        """
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.status != 'in_progress':
            return None
        
        assessment = Assessment.query.get(attempt.assessment_id)
        if not assessment:
            return None
        
        # Get answered questions
        answered_responses = QuestionResponse.query.filter_by(
            attempt_id=attempt_id
        ).all()
        answered_ids = [r.question_id for r in answered_responses]
        
        # Calculate skill coverage
        skill_coverage = {}
        for response in answered_responses:
            if response.question.skill_area:
                skill_coverage[response.question.skill_area] = \
                    skill_coverage.get(response.question.skill_area, 0) + 1
        
        # Check stopping criteria for adaptive tests
        if assessment.is_adaptive:
            adaptive_session = AdaptiveTestSession.query.filter_by(
                attempt_id=attempt_id
            ).first()
            
            if adaptive_session:
                # Check if we should stop
                if self._should_stop_adaptive_test(attempt, adaptive_session, assessment):
                    return None
        else:
            # Fixed test - check if all questions answered
            total_questions = AssessmentQuestion.query.filter_by(
                assessment_id=assessment.id,
                is_active=True
            ).count()
            
            if len(answered_ids) >= total_questions:
                return None
        
        # Select next question
        if assessment.is_adaptive:
            next_question = self.select_next_question(
                assessment.id,
                attempt.current_theta_estimate,
                answered_ids,
                skill_coverage
            )
        else:
            # Fixed order - get next unanswered question
            next_question = AssessmentQuestion.query.filter(
                AssessmentQuestion.assessment_id == assessment.id,
                AssessmentQuestion.is_active == True,
                ~AssessmentQuestion.id.in_(answered_ids) if answered_ids else True
            ).order_by(AssessmentQuestion.order_index).first()
        
        if not next_question:
            return None
        
        # Return question without revealing correct answer
        return {
            'question_id': next_question.id,
            'question_text': next_question.question_text,
            'question_type': next_question.question_type,
            'options': next_question.options,
            'skill_area': next_question.skill_area,
            'context': next_question.context,
            'difficulty_level': next_question.difficulty_level
        }
    
    def submit_response(
        self,
        attempt_id: int,
        question_id: int,
        user_answer: str,
        time_spent_seconds: Optional[int] = None,
        hints_used: Optional[List[str]] = None
    ) -> Dict:
        """
        Submit a response to an assessment question.
        
        Updates ability estimate if adaptive testing.
        
        Args:
            attempt_id: Assessment attempt ID
            question_id: Question being answered
            user_answer: User's submitted answer
            time_spent_seconds: Time taken to answer
            hints_used: Any hints that were viewed
            
        Returns:
            Response result dict with feedback and updated stats
        """
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        question = AssessmentQuestion.query.get(question_id)
        
        if not attempt or not question:
            raise ValueError("Invalid attempt or question ID")
        
        # Check if already answered
        existing = QuestionResponse.query.filter_by(
            attempt_id=attempt_id,
            question_id=question_id
        ).first()
        
        if existing:
            raise ValueError("Question already answered")
        
        # Evaluate response
        is_correct = self._evaluate_response(
            user_answer,
            question.correct_answer,
            question.question_type
        )
        
        # Calculate IRT-based metrics
        prob_correct = self.calculate_probability_correct(
            attempt.current_theta_estimate,
            question.irt_discrimination,
            question.irt_difficulty,
            question.irt_guessing
        )
        
        information = self.calculate_information(
            attempt.current_theta_estimate,
            question.irt_discrimination,
            question.irt_difficulty,
            question.irt_guessing
        )
        
        # Create response record
        response = QuestionResponse(
            attempt_id=attempt_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent_seconds,
            hints_used=hints_used or [],
            theta_at_response=attempt.current_theta_estimate,
            probability_correct=prob_correct,
            information=information
        )
        
        db.session.add(response)
        
        # Update attempt statistics
        attempt.questions_answered += 1
        if is_correct:
            attempt.correct_count += 1
        
        # Update skill breakdown
        if question.skill_area:
            skill_breakdown = attempt.skill_breakdown or {}
            if question.skill_area not in skill_breakdown:
                skill_breakdown[question.skill_area] = {'correct': 0, 'total': 0}
            
            skill_breakdown[question.skill_area]['total'] += 1
            if is_correct:
                skill_breakdown[question.skill_area]['correct'] += 1
            
            attempt.skill_breakdown = skill_breakdown
        
        # Update theta estimate if adaptive
        assessment = Assessment.query.get(attempt.assessment_id)
        if assessment and assessment.is_adaptive:
            self._update_theta_estimate(attempt, response)
        
        db.session.commit()
        
        # Prepare feedback
        feedback = {
            'is_correct': is_correct,
            'explanation': question.explanation,
            'correct_answer': question.correct_answer if not is_correct else None,
            'current_theta': attempt.current_theta_estimate,
            'theta_se': attempt.theta_standard_error,
            'probability_correct': prob_correct,
            'information': information,
            'questions_answered': attempt.questions_answered,
            'correct_count': attempt.correct_count
        }
        
        return feedback
    
    def _evaluate_response(
        self,
        user_answer: str,
        correct_answer: str,
        question_type: str
    ) -> bool:
        """
        Evaluate if user's answer is correct.
        
        Args:
            user_answer: User's submitted answer
            correct_answer: Correct answer
            question_type: Type of question
            
        Returns:
            True if correct, False otherwise
        """
        # Normalize for comparison
        user_normalized = user_answer.strip().lower()
        correct_normalized = correct_answer.strip().lower()
        
        if question_type == 'multiple_choice':
            return user_normalized == correct_normalized
        elif question_type == 'fill_in_blank':
            # Allow minor variations
            return user_normalized in correct_normalized or correct_normalized in user_normalized
        elif question_type == 'true_false':
            return user_normalized == correct_normalized
        elif question_type == 'short_answer':
            # Use LLM for semantic matching
            try:
                prompt = f"""
                Question Type: Short Answer
                User Answer: {user_answer}
                Correct Answer: {correct_answer}
                
                Determine if the user's answer is semantically correct.
                Consider synonyms, paraphrasing, and minor grammatical differences.
                
                Respond with only 'CORRECT' or 'INCORRECT'.
                """
                
                result = self.llm_service.generate_text(prompt)
                return 'CORRECT' in result.upper()
            except:
                # Fallback to exact match
                return user_normalized == correct_normalized
        else:
            return user_normalized == correct_normalized
    
    def _update_theta_estimate(
        self,
        attempt: UserAssessmentAttempt,
        latest_response: QuestionResponse
    ):
        """
        Update theta estimate based on latest response using EAP method.
        
        Args:
            attempt: Current assessment attempt
            latest_response: Most recent question response
        """
        # Get all responses for this attempt
        responses = QuestionResponse.query.filter_by(
            attempt_id=attempt.id
        ).all()
        
        # Prepare response data for EAP estimation
        response_data = []
        for resp in responses:
            question = resp.question
            response_data.append((
                question.irt_discrimination,
                question.irt_difficulty,
                question.irt_guessing,
                resp.is_correct
            ))
        
        # Estimate new theta
        new_theta, new_se = self.estimate_theta_eap(
            response_data,
            prior_mean=self.DEFAULT_THETA,
            prior_sd=self.THETA_SD
        )
        
        # Update attempt
        attempt.current_theta_estimate = new_theta
        attempt.theta_standard_error = new_se
        
        # Update adaptive session if exists
        adaptive_session = AdaptiveTestSession.query.filter_by(
            attempt_id=attempt.id
        ).first()
        
        if adaptive_session:
            adaptive_session.current_theta = new_theta
            adaptive_session.theta_se = new_se
            adaptive_session.questions_administered = len(responses)
            
            # Update theta history
            history = adaptive_session.theta_history or []
            history.append({
                'question_num': len(responses),
                'theta': new_theta,
                'se': new_se,
                'is_correct': latest_response.is_correct
            })
            adaptive_session.theta_history = history
    
    def _should_stop_adaptive_test(
        self,
        attempt: UserAssessmentAttempt,
        adaptive_session: AdaptiveTestSession,
        assessment: Assessment
    ) -> bool:
        """
        Determine if adaptive test should stop based on stopping criteria.
        
        Args:
            attempt: Current assessment attempt
            adaptive_session: Adaptive testing session
            assessment: Assessment configuration
            
        Returns:
            True if should stop, False to continue
        """
        # Minimum questions requirement
        if adaptive_session.questions_administered < self.MIN_QUESTIONS:
            return False
        
        # Maximum questions limit
        if adaptive_session.questions_administered >= self.MAX_QUESTIONS:
            return True
        
        # Precision-based stopping
        irt_config = assessment.irt_config or {}
        se_threshold = irt_config.get('se_threshold', self.DEFAULT_SE_THRESHOLD)
        
        if adaptive_session.theta_se <= se_threshold:
            return True
        
        # Custom stopping criteria from assessment config
        stopping_criteria = irt_config.get('stopping_criteria', {})
        
        # Check minimum precision
        if 'min_precision' in stopping_criteria:
            if adaptive_session.theta_se <= stopping_criteria['min_precision']:
                return True
        
        # Check confidence level
        if 'confidence_level' in stopping_criteria:
            # Calculate confidence interval width
            z_score = 1.96  # 95% confidence
            ci_width = 2 * z_score * adaptive_session.theta_se
            
            if ci_width <= stopping_criteria.get('max_ci_width', 1.0):
                return True
        
        return False
    
    # ================================================================
    # ASSESSMENT COMPLETION AND RESULTS
    # ================================================================
    
    def complete_assessment(
        self,
        attempt_id: int
    ) -> AssessmentResult:
        """
        Complete an assessment and generate comprehensive results.
        
        Args:
            attempt_id: Assessment attempt to complete
            
        Returns:
            AssessmentResult object with complete analysis
        """
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt:
            raise ValueError(f"Attempt {attempt_id} not found")
        
        if attempt.status == 'completed':
            # Already completed - return existing result
            result = AssessmentResult.query.filter_by(attempt_id=attempt_id).first()
            if result:
                return result
        
        assessment = Assessment.query.get(attempt.assessment_id)
        responses = QuestionResponse.query.filter_by(attempt_id=attempt_id).all()
        
        # Calculate final theta if not already set
        if not attempt.final_theta_estimate:
            attempt.final_theta_estimate = attempt.current_theta_estimate
        
        # Mark attempt as completed
        attempt.status = 'completed'
        attempt.completed_at = datetime.utcnow()
        
        # Calculate overall score
        total_questions = len(responses)
        correct_count = sum(1 for r in responses if r.is_correct)
        overall_score = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
        
        # Calculate skill scores
        skill_scores = self._calculate_skill_scores(responses)
        
        # Determine proficiency level
        proficiency_level = self._determine_proficiency_level(attempt.final_theta_estimate)
        
        # Calculate percentile rank
        percentile_rank = self._calculate_percentile_rank(
            attempt.final_theta_estimate,
            assessment.id
        )
        
        # Identify strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(skill_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            weaknesses,
            attempt.final_theta_estimate,
            assessment
        )
        
        # Identify learning gaps
        learning_gaps = self._identify_learning_gaps(responses, skill_scores)
        
        # Create result record
        result = AssessmentResult(
            attempt_id=attempt_id,
            overall_score=overall_score,
            skill_scores=skill_scores,
            proficiency_level=proficiency_level,
            theta_estimate=attempt.final_theta_estimate,
            theta_se=attempt.theta_standard_error,
            percentile_rank=percentile_rank,
            strengths=strengths,
            weaknesses=weaknesses,
            learning_gaps=learning_gaps,
            recommendations=recommendations,
            passed=overall_score >= (assessment.passing_score or 0.0) if assessment.passing_score else None
        )
        
        db.session.add(result)
        
        # Create detailed skill diagnostics
        self._create_skill_diagnostics(attempt_id, responses, skill_scores)
        
        db.session.commit()
        
        return result
    
    def _calculate_skill_scores(
        self,
        responses: List[QuestionResponse]
    ) -> Dict[str, float]:
        """
        Calculate scores for each skill area.
        
        Args:
            responses: List of question responses
            
        Returns:
            Dict of skill_area -> score (0-100)
        """
        skill_data = {}
        
        for response in responses:
            if response.question.skill_area:
                skill = response.question.skill_area
                if skill not in skill_data:
                    skill_data[skill] = {'correct': 0, 'total': 0}
                
                skill_data[skill]['total'] += 1
                if response.is_correct:
                    skill_data[skill]['correct'] += 1
        
        # Calculate percentages
        skill_scores = {}
        for skill, data in skill_data.items():
            skill_scores[skill] = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0.0
        
        return skill_scores
    
    def _determine_proficiency_level(self, theta: float) -> str:
        """
        Determine proficiency level from theta estimate.
        
        Args:
            theta: Ability estimate
            
        Returns:
            Proficiency level string
        """
        for level, (min_theta, max_theta) in self.PROFICIENCY_LEVELS.items():
            if min_theta <= theta < max_theta:
                return level
        
        # Handle edge cases
        if theta >= 2.0:
            return 'expert'
        else:
            return 'beginner'
    
    def _calculate_percentile_rank(
        self,
        theta: float,
        assessment_id: int
    ) -> Optional[float]:
        """
        Calculate percentile rank compared to other test takers.
        
        Args:
            theta: User's ability estimate
            assessment_id: Assessment ID
            
        Returns:
            Percentile rank (0-100) or None if insufficient data
        """
        # Get all completed attempts for this assessment
        completed_attempts = UserAssessmentAttempt.query.filter(
            UserAssessmentAttempt.assessment_id == assessment_id,
            UserAssessmentAttempt.status == 'completed',
            UserAssessmentAttempt.final_theta_estimate.isnot(None)
        ).all()
        
        if len(completed_attempts) < 10:
            return None  # Need at least 10 attempts for meaningful percentile
        
        # Count how many have lower theta
        lower_count = sum(
            1 for attempt in completed_attempts
            if attempt.final_theta_estimate < theta
        )
        
        percentile = (lower_count / len(completed_attempts)) * 100
        return percentile
    
    def _identify_strengths_weaknesses(
        self,
        skill_scores: Dict[str, float],
        threshold: float = 70.0
    ) -> Tuple[List[str], List[str]]:
        """
        Identify strengths and weaknesses from skill scores.
        
        Args:
            skill_scores: Dict of skill -> score
            threshold: Score threshold for strength/weakness (default 70%)
            
        Returns:
            Tuple of (strengths, weaknesses)
        """
        strengths = [skill for skill, score in skill_scores.items() if score >= threshold]
        weaknesses = [skill for skill, score in skill_scores.items() if score < threshold]
        
        return (strengths, weaknesses)
    
    def _identify_learning_gaps(
        self,
        responses: List[QuestionResponse],
        skill_scores: Dict[str, float]
    ) -> List[Dict]:
        """
        Identify specific learning gaps from incorrect responses.
        
        Args:
            responses: All question responses
            skill_scores: Skill-level scores
            
        Returns:
            List of learning gap dicts
        """
        gaps = []
        
        # Group incorrect responses by skill
        skill_errors = {}
        for response in responses:
            if not response.is_correct and response.question.skill_area:
                skill = response.question.skill_area
                if skill not in skill_errors:
                    skill_errors[skill] = []
                skill_errors[skill].append(response)
        
        # Analyze each skill with errors
        for skill, error_responses in skill_errors.items():
            # Find common sub-skills in errors
            sub_skill_counts = {}
            for response in error_responses:
                for sub_skill in response.question.sub_skills:
                    sub_skill_counts[sub_skill] = sub_skill_counts.get(sub_skill, 0) + 1
            
            # Identify most problematic sub-skills
            if sub_skill_counts:
                most_common = max(sub_skill_counts.items(), key=lambda x: x[1])
                
                gaps.append({
                    'skill_area': skill,
                    'sub_skill': most_common[0],
                    'error_count': most_common[1],
                    'score': skill_scores.get(skill, 0.0),
                    'severity': 'high' if skill_scores.get(skill, 0.0) < 50 else 'medium'
                })
        
        # Sort by severity and error count
        gaps.sort(key=lambda x: (x['severity'] == 'high', x['error_count']), reverse=True)
        
        return gaps
    
    def _generate_recommendations(
        self,
        weaknesses: List[str],
        theta: float,
        assessment: Assessment
    ) -> List[str]:
        """
        Generate personalized learning recommendations.
        
        Args:
            weaknesses: List of weak skill areas
            theta: Current ability estimate
            assessment: Assessment object
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Recommendations based on weaknesses
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            recommendations.append(
                f"Focus on improving {weakness} through targeted practice"
            )
        
        # Recommendations based on proficiency level
        proficiency = self._determine_proficiency_level(theta)
        
        if proficiency in ['beginner', 'elementary']:
            recommendations.append(
                "Start with foundational exercises and gradually increase difficulty"
            )
        elif proficiency == 'intermediate':
            recommendations.append(
                "Challenge yourself with advanced materials while reinforcing basics"
            )
        else:
            recommendations.append(
                "Maintain skills through regular practice and explore specialized topics"
            )
        
        # Assessment-specific recommendations
        if assessment.assessment_type == 'placement':
            recommendations.append(
                f"Your current level is {proficiency}. Begin learning path at appropriate difficulty."
            )
        elif assessment.assessment_type == 'progress':
            recommendations.append(
                "Review areas of weakness before progressing to next module"
            )
        elif assessment.assessment_type == 'mastery':
            if len(weaknesses) == 0:
                recommendations.append(
                    "Congratulations! You've mastered this topic. Ready for certification."
                )
            else:
                recommendations.append(
                    "Complete additional practice in weak areas before attempting certification"
                )
        
        return recommendations
    
    def _create_skill_diagnostics(
        self,
        attempt_id: int,
        responses: List[QuestionResponse],
        skill_scores: Dict[str, float]
    ):
        """
        Create detailed skill diagnostic records.
        
        Args:
            attempt_id: Assessment attempt ID
            responses: All question responses
            skill_scores: Overall skill scores
        """
        # Group responses by skill
        skill_responses = {}
        for response in responses:
            if response.question.skill_area:
                skill = response.question.skill_area
                if skill not in skill_responses:
                    skill_responses[skill] = []
                skill_responses[skill].append(response)
        
        # Create diagnostic for each skill
        for skill, skill_resp in skill_responses.items():
            # Calculate sub-skill performance
            sub_skill_scores = {}
            for response in skill_resp:
                for sub_skill in response.question.sub_skills:
                    if sub_skill not in sub_skill_scores:
                        sub_skill_scores[sub_skill] = {'correct': 0, 'total': 0}
                    
                    sub_skill_scores[sub_skill]['total'] += 1
                    if response.is_correct:
                        sub_skill_scores[sub_skill]['correct'] += 1
            
            # Calculate percentages
            sub_skill_percentages = {
                sub: (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0.0
                for sub, data in sub_skill_scores.items()
            }
            
            # Identify error patterns
            error_patterns = self._analyze_error_patterns(
                [r for r in skill_resp if not r.is_correct]
            )
            
            # Generate improvement strategies
            improvement_strategies = self._generate_improvement_strategies(
                skill,
                sub_skill_percentages,
                error_patterns
            )
            
            # Create diagnostic record
            diagnostic = SkillDiagnostic(
                attempt_id=attempt_id,
                skill_area=skill,
                score=skill_scores.get(skill, 0.0),
                questions_attempted=len(skill_resp),
                correct_count=sum(1 for r in skill_resp if r.is_correct),
                sub_skill_scores=sub_skill_percentages,
                error_patterns=error_patterns,
                improvement_strategies=improvement_strategies
            )
            
            db.session.add(diagnostic)
    
    def _analyze_error_patterns(
        self,
        incorrect_responses: List[QuestionResponse]
    ) -> List[Dict]:
        """
        Analyze patterns in incorrect responses.
        
        Args:
            incorrect_responses: List of incorrect responses
            
        Returns:
            List of error pattern dicts
        """
        if not incorrect_responses:
            return []
        
        patterns = []
        
        # Pattern 1: Difficulty level issues
        difficulty_counts = {}
        for response in incorrect_responses:
            diff = response.question.difficulty_level or 'unknown'
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
        
        if difficulty_counts:
            most_common_diff = max(difficulty_counts.items(), key=lambda x: x[1])
            patterns.append({
                'pattern_type': 'difficulty',
                'description': f"Most errors on {most_common_diff[0]} questions",
                'count': most_common_diff[1]
            })
        
        # Pattern 2: Question type issues
        type_counts = {}
        for response in incorrect_responses:
            qtype = response.question.question_type
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        if type_counts:
            most_common_type = max(type_counts.items(), key=lambda x: x[1])
            patterns.append({
                'pattern_type': 'question_type',
                'description': f"Struggles with {most_common_type[0]} questions",
                'count': most_common_type[1]
            })
        
        # Pattern 3: Time pressure (if timing data available)
        timed_responses = [r for r in incorrect_responses if r.time_spent_seconds]
        if timed_responses:
            avg_time = sum(r.time_spent_seconds for r in timed_responses) / len(timed_responses)
            if avg_time < 30:  # Quick responses might indicate guessing
                patterns.append({
                    'pattern_type': 'time_pressure',
                    'description': 'Many quick incorrect answers (possible rushing)',
                    'average_time': avg_time
                })
        
        return patterns
    
    def _generate_improvement_strategies(
        self,
        skill_area: str,
        sub_skill_scores: Dict[str, float],
        error_patterns: List[Dict]
    ) -> List[str]:
        """
        Generate specific improvement strategies for a skill.
        
        Args:
            skill_area: Skill being analyzed
            sub_skill_scores: Sub-skill performance
            error_patterns: Identified error patterns
            
        Returns:
            List of strategy strings
        """
        strategies = []
        
        # Strategies based on sub-skill weaknesses
        weak_sub_skills = [
            skill for skill, score in sub_skill_scores.items()
            if score < 60.0
        ]
        
        for sub_skill in weak_sub_skills[:2]:  # Top 2 weaknesses
            strategies.append(
                f"Practice {sub_skill} with focused exercises"
            )
        
        # Strategies based on error patterns
        for pattern in error_patterns:
            if pattern['pattern_type'] == 'difficulty':
                strategies.append(
                    f"Gradually build up to harder {skill_area} questions"
                )
            elif pattern['pattern_type'] == 'question_type':
                strategies.append(
                    f"Practice more {pattern['description'].split('with ')[1]}"
                )
            elif pattern['pattern_type'] == 'time_pressure':
                strategies.append(
                    "Take more time to carefully read and think through questions"
                )
        
        # General strategies
        if not strategies:
            strategies.append(
                f"Review {skill_area} concepts and complete practice exercises"
            )
        
        return strategies
    
    # ================================================================
    # ANALYTICS AND REPORTING
    # ================================================================
    
    def get_user_assessment_history(
        self,
        user_id: int,
        assessment_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get user's assessment history with results.
        
        Args:
            user_id: User ID
            assessment_id: Optional specific assessment
            
        Returns:
            List of assessment attempt dicts with results
        """
        query = UserAssessmentAttempt.query.filter_by(
            user_id=user_id,
            status='completed'
        )
        
        if assessment_id:
            query = query.filter_by(assessment_id=assessment_id)
        
        attempts = query.order_by(
            UserAssessmentAttempt.completed_at.desc()
        ).all()
        
        history = []
        for attempt in attempts:
            result = AssessmentResult.query.filter_by(
                attempt_id=attempt.id
            ).first()
            
            assessment = Assessment.query.get(attempt.assessment_id)
            
            history.append({
                'attempt_id': attempt.id,
                'assessment_title': assessment.title if assessment else 'Unknown',
                'assessment_type': assessment.assessment_type if assessment else None,
                'completed_at': attempt.completed_at.isoformat(),
                'overall_score': result.overall_score if result else None,
                'proficiency_level': result.proficiency_level if result else None,
                'theta_estimate': attempt.final_theta_estimate,
                'questions_answered': attempt.questions_answered,
                'correct_count': attempt.correct_count,
                'passed': result.passed if result else None
            })
        
        return history
    
    def get_assessment_analytics(
        self,
        assessment_id: int
    ) -> Dict:
        """
        Get analytics for an assessment.
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Analytics dict with aggregate statistics
        """
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        # Get all completed attempts
        attempts = UserAssessmentAttempt.query.filter_by(
            assessment_id=assessment_id,
            status='completed'
        ).all()
        
        if not attempts:
            return {
                'assessment_title': assessment.title,
                'total_attempts': 0,
                'message': 'No completed attempts yet'
            }
        
        # Calculate statistics
        theta_estimates = [a.final_theta_estimate for a in attempts if a.final_theta_estimate]
        avg_theta = sum(theta_estimates) / len(theta_estimates) if theta_estimates else 0.0
        
        scores = []
        pass_count = 0
        for attempt in attempts:
            result = AssessmentResult.query.filter_by(attempt_id=attempt.id).first()
            if result:
                scores.append(result.overall_score)
                if result.passed:
                    pass_count += 1
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        pass_rate = (pass_count / len(attempts) * 100) if attempts else 0.0
        
        # Proficiency distribution
        proficiency_dist = {}
        for attempt in attempts:
            result = AssessmentResult.query.filter_by(attempt_id=attempt.id).first()
            if result and result.proficiency_level:
                level = result.proficiency_level
                proficiency_dist[level] = proficiency_dist.get(level, 0) + 1
        
        # Question difficulty analysis
        questions = AssessmentQuestion.query.filter_by(
            assessment_id=assessment_id,
            is_active=True
        ).all()
        
        question_stats = []
        for question in questions:
            responses = QuestionResponse.query.filter_by(
                question_id=question.id
            ).all()
            
            if responses:
                correct = sum(1 for r in responses if r.is_correct)
                difficulty = 1.0 - (correct / len(responses))  # Higher = more difficult
                
                question_stats.append({
                    'question_id': question.id,
                    'skill_area': question.skill_area,
                    'difficulty_level': question.difficulty_level,
                    'irt_difficulty': question.irt_difficulty,
                    'empirical_difficulty': difficulty,
                    'times_answered': len(responses),
                    'correct_rate': correct / len(responses) * 100
                })
        
        return {
            'assessment_title': assessment.title,
            'assessment_type': assessment.assessment_type,
            'total_attempts': len(attempts),
            'average_score': avg_score,
            'average_theta': avg_theta,
            'pass_rate': pass_rate,
            'proficiency_distribution': proficiency_dist,
            'question_statistics': question_stats[:10],  # Top 10
            'total_questions': len(questions)
        }
    
    def get_skill_diagnostics(
        self,
        attempt_id: int
    ) -> List[Dict]:
        """
        Get detailed skill diagnostics for an assessment attempt.
        
        Args:
            attempt_id: Assessment attempt ID
            
        Returns:
            List of skill diagnostic dicts
        """
        diagnostics = SkillDiagnostic.query.filter_by(
            attempt_id=attempt_id
        ).all()
        
        return [diag.to_dict() for diag in diagnostics]
    
    def compare_attempts(
        self,
        attempt_id_1: int,
        attempt_id_2: int
    ) -> Dict:
        """
        Compare two assessment attempts to show improvement.
        
        Args:
            attempt_id_1: First attempt (earlier)
            attempt_id_2: Second attempt (later)
            
        Returns:
            Comparison dict with improvements and changes
        """
        attempt1 = UserAssessmentAttempt.query.get(attempt_id_1)
        attempt2 = UserAssessmentAttempt.query.get(attempt_id_2)
        
        if not attempt1 or not attempt2:
            raise ValueError("Invalid attempt IDs")
        
        result1 = AssessmentResult.query.filter_by(attempt_id=attempt_id_1).first()
        result2 = AssessmentResult.query.filter_by(attempt_id=attempt_id_2).first()
        
        comparison = {
            'attempt1': {
                'date': attempt1.completed_at.isoformat() if attempt1.completed_at else None,
                'score': result1.overall_score if result1 else None,
                'theta': attempt1.final_theta_estimate,
                'proficiency': result1.proficiency_level if result1 else None
            },
            'attempt2': {
                'date': attempt2.completed_at.isoformat() if attempt2.completed_at else None,
                'score': result2.overall_score if result2 else None,
                'theta': attempt2.final_theta_estimate,
                'proficiency': result2.proficiency_level if result2 else None
            },
            'improvements': {}
        }
        
        # Calculate improvements
        if result1 and result2:
            score_change = result2.overall_score - result1.overall_score
            theta_change = attempt2.final_theta_estimate - attempt1.final_theta_estimate
            
            comparison['improvements'] = {
                'score_change': score_change,
                'score_change_percent': (score_change / result1.overall_score * 100) if result1.overall_score > 0 else 0,
                'theta_change': theta_change,
                'proficiency_improved': result2.proficiency_level != result1.proficiency_level
            }
            
            # Skill-level improvements
            skill_improvements = {}
            for skill, score2 in result2.skill_scores.items():
                score1 = result1.skill_scores.get(skill, 0.0)
                skill_improvements[skill] = {
                    'before': score1,
                    'after': score2,
                    'change': score2 - score1
                }
            
            comparison['skill_improvements'] = skill_improvements
        
        return comparison
