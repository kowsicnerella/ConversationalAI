import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm.attributes import flag_modified
from app.models import (
    User,
    Activity,
    UserActivityLog,
    LearningPath,
    ProficiencyAssessment,
    UserAssessmentHistory,
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db
from app.services.llm_config import LLMConfig
from config import Config


class InitialAssessmentService:
    """
    Comprehensive initial assessment service for new users to determine their English proficiency level,
    learning preferences, and optimal learning path placement.
    Enhanced with comprehensive multi-skill assessment and adaptive learning path generation.
    Uses centralized LLM config with custom model and Gemini fallback.
    """

    def __init__(self):
        self.activity_service = ActivityGeneratorService()

        # Assessment configuration
        self.ASSESSMENT_LEVELS = ["beginner", "intermediate", "advanced"]
        self.SKILL_AREAS = [
            "vocabulary",
            "grammar",
            "reading",
            "listening",
            "writing",
            "speaking",
        ]
        self.QUESTIONS_PER_SKILL = 3
        self.QUESTIONS_PER_LEVEL = 2
        self.PASSING_THRESHOLD = 0.7

        # Enhanced scoring weights for different skill areas
        self.SKILL_WEIGHTS = {
            "vocabulary": 0.20,
            "grammar": 0.25,
            "reading": 0.20,
            "listening": 0.15,
            "writing": 0.15,
            "speaking": 0.05,
        }

        # Mastery thresholds
        self.MASTERY_THRESHOLD = 0.85
        self.PROFICIENT_THRESHOLD = 0.70
        self.NEEDS_WORK_THRESHOLD = 0.50

    def conduct_comprehensive_initial_assessment(
        self, user_id: int, assessment_type: str = "comprehensive"
    ) -> Dict:
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

        # Check if user has an incomplete assessment of this type
        existing_assessment = ProficiencyAssessment.query.filter_by(
            user_id=user_id,
            assessment_type=assessment_type,
            completed_at=None  # Not completed yet
        ).order_by(ProficiencyAssessment.id.desc()).first()

        if existing_assessment:
            print(f"Found existing incomplete assessment {existing_assessment.id} for user {user_id}")
            
            # Count how many questions have been answered
            # user_responses might be a dict with various keys, so we need to count actual question responses
            user_responses = existing_assessment.user_responses or {}
            questions_asked = existing_assessment.questions_asked or []
            
            # Count only responses that match actual question IDs
            question_ids = {q.get("id") or q.get("question_id") for q in questions_asked}
            answered_count = len([qid for qid in user_responses.keys() if qid in question_ids])
            
            # Ensure answered_count doesn't exceed total questions
            answered_count = min(answered_count, len(questions_asked))
            
            print(f"User has already answered {answered_count} out of {len(questions_asked)} questions")
            print(f"User responses keys: {list(user_responses.keys())[:5]}")  # Show first 5 keys
            print(f"Question IDs: {list(question_ids)[:5]}")  # Show first 5 question IDs
            
            # Return existing assessment instead of creating a new one
            return {
                "assessment_id": existing_assessment.id,
                "assessment_type": assessment_type,
                "questions": questions_asked,
                "current_question_index": answered_count,  # Tell frontend where to resume
                "metadata": {
                    "total_questions": len(questions_asked),
                    "max_score": sum(q.get("points", 2) for q in questions_asked),
                    "estimated_duration_minutes": 45 if assessment_type == "comprehensive" else 30 if assessment_type == "adaptive" else 15,
                    "skill_areas_covered": list(set(q.get("skill_area") for q in questions_asked if q.get("skill_area"))),
                    "answered_questions": answered_count,  # Add this for clarity
                },
                "instructions": {
                    "english": self._get_assessment_instructions(assessment_type),
                    "telugu": self._get_telugu_instructions(assessment_type),
                },
                "assessment_structure": {
                    "type": assessment_type,
                    "resuming": True
                },
            }

        # Generate assessment questions based on type
        print(f"Generating new {assessment_type} assessment for user {user_id}")
        if assessment_type == "quick":
            assessment_data = self._generate_quick_assessment()
        elif assessment_type == "adaptive":
            assessment_data = self._generate_adaptive_assessment()
        else:  # comprehensive
            assessment_data = self._generate_comprehensive_assessment()

        # Create assessment record
        assessment = ProficiencyAssessment(
            user_id=user_id,
            assessment_type=assessment_type,
            questions_asked=assessment_data["questions"],
        )

        db.session.add(assessment)
        db.session.commit()
        
        print(f"✅ Created new assessment ID={assessment.id} for user {user_id}, type={assessment_type}")

        return {
            "assessment_id": assessment.id,
            "assessment_type": assessment_type,
            "questions": assessment_data["questions"],
            "metadata": {
                "total_questions": len(assessment_data["questions"]),
                "max_score": assessment_data["max_score"],
                "estimated_duration_minutes": assessment_data["estimated_duration"],
                "skill_areas_covered": assessment_data["skill_areas"],
            },
            "instructions": {
                "english": assessment_data["instructions"],
                "telugu": assessment_data["telugu_instructions"],
            },
            "assessment_structure": assessment_data["structure"],
        }

    def submit_assessment_answers(self, assessment_id: int, answers: Dict, force_re_evaluate: bool = False) -> Dict:
        """
        Submit and evaluate assessment answers.

        Args:
            assessment_id: Assessment ID
            answers: Dictionary of question_id -> answer mappings
            force_re_evaluate: If True, allow re-evaluation of already-completed assessments
        """
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")

        # Check if assessment is already completed
        # Allow re-evaluation if force_re_evaluate is True (for auto-evaluation of already-completed but not-evaluated assessments)
        if assessment.user_responses and not force_re_evaluate:
            raise ValueError("Assessment is already completed")

        # Load questions data
        questions = assessment.questions_asked if assessment.questions_asked else []

        # Evaluate answers
        evaluation_result = self._evaluate_assessment_answers(questions, answers)

        # Calculate proficiency level and recommendations
        proficiency_analysis = self._analyze_proficiency_level(evaluation_result)

        # Generate learning path recommendations
        learning_path_recommendations = self._recommend_learning_paths(
            proficiency_analysis
        )

        # Update assessment record
        assessment.user_responses = answers
        assessment.ai_evaluation = evaluation_result
        assessment.proficiency_level = proficiency_analysis["overall_level"]
        assessment.strengths = proficiency_analysis.get("strengths", [])
        assessment.weaknesses = proficiency_analysis.get("weaknesses", [])
        assessment.recommendations = learning_path_recommendations
        assessment.confidence_score = proficiency_analysis.get("confidence", 0.5)
        assessment.completed_at = datetime.utcnow()

        # Save to user assessment history for complete tracking
        history_entry = UserAssessmentHistory(
            user_id=assessment.user_id,
            assessment_id=assessment_id,
            assessment_type=assessment.assessment_type,
            questions=questions,
            user_answers=answers,
            correct_answers={
                (q.get("id") or q.get("question_id")): q.get("correct_answer", q.get("sample_answer"))
                for q in questions
            },
            score=evaluation_result["total_score"],
            max_score=evaluation_result.get("max_score", assessment.max_score),
            proficiency_level=proficiency_analysis["overall_level"],
            skill_breakdown=proficiency_analysis.get("skill_breakdown", {}),
            strengths=proficiency_analysis.get("strengths", []),
            weaknesses=proficiency_analysis.get("weaknesses", []),
            ai_feedback=evaluation_result.get("feedback", ""),
            recommendations=learning_path_recommendations,
            duration_seconds=int(
                (datetime.utcnow() - assessment.started_at).total_seconds()
            )
            if assessment.started_at
            else None,
            started_at=assessment.started_at or datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        db.session.add(history_entry)

        db.session.commit()

        # Generate personalized report
        assessment_report = self._generate_assessment_report(
            assessment,
            evaluation_result,
            proficiency_analysis,
            learning_path_recommendations,
        )

        # Calculate max score from questions
        max_score = sum(q.get("points", 2) for q in questions) if questions else 1

        return {
            "assessment_completed": True,
            "assessment_id": assessment_id,
            "results": {
                "overall_score": evaluation_result["total_score"],
                "max_score": max_score,
                "percentage": (
                    (evaluation_result["total_score"] / max_score) * 100
                    if max_score > 0
                    else 0
                ),
                "proficiency_level": proficiency_analysis["overall_level"],
                "skill_breakdown": proficiency_analysis["skill_breakdown"],
            },
            "recommendations": learning_path_recommendations,
            "detailed_report": assessment_report,
            "next_steps": self._generate_next_steps(
                proficiency_analysis, learning_path_recommendations
            ),
        }

    def get_assessment_history(self, user_id: int) -> List[Dict]:
        """
        Get assessment history for a user.
        """
        assessments = (
            ProficiencyAssessment.query.filter_by(user_id=user_id)
            .order_by(ProficiencyAssessment.completed_at.desc())
            .all()
        )

        history = []
        for assessment in assessments:
            # Calculate max score from questions if available
            max_score = 0
            if assessment.questions_asked:
                max_score = sum(q.get("points", 2) for q in assessment.questions_asked)

            assessment_data = {
                "assessment_id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "status": "completed" if assessment.user_responses else "in_progress",
                "completed_at": (
                    assessment.completed_at.isoformat()
                    if assessment.completed_at
                    else None
                ),
                "proficiency_level": assessment.proficiency_level,
            }

            if assessment.completed_at and assessment.ai_evaluation:
                total_score = assessment.ai_evaluation.get("total_score", 0)
                assessment_data["score"] = total_score
                assessment_data["max_score"] = max_score
                assessment_data["percentage"] = (
                    (total_score / max_score * 100) if max_score > 0 else 0
                )
                assessment_data["skill_breakdown"] = assessment.ai_evaluation.get(
                    "skill_scores", {}
                )

            history.append(assessment_data)

        return history

    def submit_single_answer(
        self, assessment_id: int, question_id: str, answer: str
    ) -> Dict:
        """
        Submit a single answer for adaptive assessment and get the next question.
        Used for step-by-step assessment progression.

        Args:
            assessment_id: Assessment ID
            question_id: ID of the question being answered
            answer: User's answer

        Returns:
            Dictionary with evaluation and next question (if available)
        """
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")

        # Initialize or load current responses
        current_responses = (
            assessment.user_responses if assessment.user_responses else {}
        )
        
        print(f"🔍 Loading responses from DB for assessment {assessment_id}")
        print(f"Current responses in DB: {list(current_responses.keys())}")

        # Find the question in the assessment
        questions = assessment.questions_asked if assessment.questions_asked else []
        current_question = None
        for q in questions:
            if q.get("question_id") == question_id:
                current_question = q
                break

        if not current_question:
            raise ValueError(f"Question {question_id} not found in assessment")

        # Evaluate the answer
        evaluation = self._evaluate_single_answer(current_question, answer)

        # Store the answer and evaluation
        print(f"Storing answer for question_id: {question_id}, answer: {answer}")
        
        # Add new answer to responses
        current_responses[question_id] = {
            "answer": answer,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        print(f"In-memory responses now has {len(current_responses)} answers: {list(current_responses.keys())}")

        # CRITICAL FIX: Create a NEW dict object so SQLAlchemy detects the change
        # Simply modifying the existing dict doesn't trigger SQLAlchemy's change detection
        assessment.user_responses = dict(current_responses)  # Create new dict
        
        # Also mark it as modified to be extra sure
        flag_modified(assessment, "user_responses")
        
        db.session.commit()
        
        # Verify what was actually saved
        db.session.refresh(assessment)
        saved_keys = list(assessment.user_responses.keys()) if assessment.user_responses else []
        print(f"✅ Saved to DB. Verifying: {saved_keys} ({len(saved_keys)} answers)")

        # Check if this was the last question
        answered_count = len(current_responses)
        total_questions = len(questions)
        
        print(f"📊 Progress: {answered_count}/{total_questions} questions answered")
        print(f"Question asked: {current_question.get('question_text', '')[:80]}...")

        response = {
            "evaluation": evaluation,
            "progress": {
                "answered": answered_count,
                "total": total_questions,
                "percentage": (
                    (answered_count / total_questions) * 100
                    if total_questions > 0
                    else 0
                ),
            },
        }

        # If there are more questions, return the next one
        if answered_count < total_questions:
            # Find next unanswered question
            answered_ids = set(current_responses.keys())
            print(f"Answered question IDs: {answered_ids}")
            
            for idx, q in enumerate(questions):
                q_id = q.get("question_id")
                if q_id not in current_responses:
                    print(f"Next unanswered question: Index {idx}, ID {q_id}, Text: {q.get('question_text', '')[:50]}...")
                    response["next_question"] = q
                    response["is_complete"] = False
                    break
        else:
            response["is_complete"] = True
            response["message"] = (
                "All questions answered. Call complete endpoint to get final results."
            )

        return response

    def retake_assessment(self, user_id: int, previous_assessment_id: int) -> Dict:
        """
        Allow user to retake assessment with adaptive difficulty.
        """
        previous_assessment = ProficiencyAssessment.query.get(previous_assessment_id)
        if not previous_assessment or previous_assessment.user_id != user_id:
            raise ValueError("Previous assessment not found or unauthorized")

        # Analyze previous performance to adapt new assessment
        if previous_assessment.ai_evaluation:
            adaptive_config = self._generate_adaptive_config(
                previous_assessment.ai_evaluation
            )
        else:
            adaptive_config = {
                "focus_areas": ["vocabulary", "grammar"],
                "difficulty": "intermediate",
            }

        # Generate new adaptive assessment
        return self.generate_placement_assessment(user_id, "adaptive")

    def generate_skill_specific_assessment(self, user_id: int, skill_area: str) -> Dict:
        """
        Generate assessment focused on a specific skill area.
        """
        if skill_area not in self.SKILL_AREAS:
            raise ValueError(
                f"Invalid skill area. Must be one of: {', '.join(self.SKILL_AREAS)}"
            )

        assessment_data = self._generate_skill_focused_assessment(skill_area)

        # Create assessment record
        assessment = ProficiencyAssessment(
            user_id=user_id,
            assessment_type=f"skill_{skill_area}",
            questions_asked=assessment_data["questions"],
        )

        db.session.add(assessment)
        db.session.commit()

        return {
            "assessment_id": assessment.id,
            "skill_area": skill_area,
            "questions": assessment_data["questions"],
            "metadata": assessment_data["metadata"],
            "instructions": assessment_data["instructions"],
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
                skill_questions = self._generate_skill_level_questions(
                    skill_area, level, self.QUESTIONS_PER_LEVEL
                )
                # Ensure all questions have points field
                for question in skill_questions:
                    if "points" not in question:
                        question["points"] = self._get_points_for_level(level)
                questions.extend(skill_questions)
                total_score += sum(q["points"] for q in skill_questions)

        structure = {
            "total_sections": len(self.SKILL_AREAS),
            "questions_per_skill": self.QUESTIONS_PER_SKILL
            * len(self.ASSESSMENT_LEVELS),
            "levels_tested": self.ASSESSMENT_LEVELS,
            "skills_tested": self.SKILL_AREAS,
        }

        return {
            "questions": questions,
            "max_score": total_score,
            "estimated_duration": 45,  # 45 minutes
            "skill_areas": skill_areas,
            "structure": structure,
            "instructions": self._get_assessment_instructions("comprehensive"),
            "telugu_instructions": self._get_telugu_instructions("comprehensive"),
        }

    def _generate_quick_assessment(self) -> Dict:
        """Generate quick 15-minute assessment."""
        questions = []
        total_score = 0

        # Select key skill areas for quick assessment
        key_skills = ["vocabulary", "grammar", "reading"]

        for skill_area in key_skills:
            # One question per level for quick assessment
            for level in self.ASSESSMENT_LEVELS:
                skill_questions = self._generate_skill_level_questions(
                    skill_area, level, 1
                )
                questions.extend(skill_questions)
                total_score += sum(q["points"] for q in skill_questions)

        structure = {
            "total_sections": len(key_skills),
            "questions_per_skill": len(self.ASSESSMENT_LEVELS),
            "levels_tested": self.ASSESSMENT_LEVELS,
            "skills_tested": key_skills,
        }

        return {
            "questions": questions,
            "max_score": total_score,
            "estimated_duration": 15,
            "skill_areas": key_skills,
            "structure": structure,
            "instructions": self._get_assessment_instructions("quick"),
            "telugu_instructions": self._get_telugu_instructions("quick"),
        }

    def _generate_adaptive_assessment(self) -> Dict:
        """Generate adaptive assessment that adjusts based on user responses."""
        # Start with intermediate level questions
        questions = []
        total_score = 0

        # Generate starter questions
        for skill_area in ["vocabulary", "grammar"]:
            skill_questions = self._generate_skill_level_questions(
                skill_area, "intermediate", 2
            )
            # Ensure all questions have points field
            for question in skill_questions:
                if "points" not in question:
                    question["points"] = self._get_points_for_level("intermediate")
            questions.extend(skill_questions)
            total_score += sum(q["points"] for q in skill_questions)

        structure = {
            "adaptive": True,
            "initial_questions": len(questions),
            "max_additional_questions": 20,
            "adaptation_logic": "performance_based",
        }

        return {
            "questions": questions,
            "max_score": total_score,
            "estimated_duration": 30,
            "skill_areas": ["vocabulary", "grammar"],
            "structure": structure,
            "instructions": self._get_assessment_instructions("adaptive"),
            "telugu_instructions": self._get_telugu_instructions("adaptive"),
        }

    def _generate_skill_level_questions(
        self, skill_area: str, level: str, count: int
    ) -> List[Dict]:
        """Generate questions for a specific skill area and level."""
        # For comprehensive assessments, use pre-generated questions to avoid multiple LLM calls
        # This prevents timeout issues when generating many questions at once
        
        print(f"Generating {count} questions for {skill_area} - {level}")
        
        # Use fallback questions directly for faster, more reliable generation
        processed_questions = self._generate_fallback_questions(
            skill_area, level, count
        )
        
        # Ensure all questions have required fields
        for i, question in enumerate(processed_questions):
            if "question_id" not in question:
                question["question_id"] = f"q_{skill_area}_{level}_{i+1}"
            if "points" not in question:
                question["points"] = self._get_points_for_level(level)
            if "skill_area" not in question:
                question["skill_area"] = skill_area
            if "difficulty_level" not in question:
                question["difficulty_level"] = level
            if "question_type" not in question:
                question["question_type"] = "multiple_choice"

        return processed_questions

    def _get_points_for_level(self, level: str) -> int:
        """Get points value for difficulty level."""
        points_map = {"beginner": 2, "intermediate": 3, "advanced": 4}
        return points_map.get(level, 2)

    def _generate_fallback_questions(
        self, skill_area: str, level: str, count: int
    ) -> List[Dict]:
        """Generate comprehensive fallback questions for all skill areas and levels."""
        
        # Comprehensive question bank for all skill areas and levels
        question_bank = {
            "vocabulary": {
                "beginner": [
                    {
                        "question_text": 'What does "hello" mean in Telugu?',
                        "options": ["నమస్కారం", "వీడ్కోలు", "ధన్యవాదాలు", "క్షమించండి"],
                        "correct_answer": "A",
                        "explanation": "'Hello' is a greeting that means నమస్కారం in Telugu.",
                        "telugu_hint": "శుభాకాంక్షల పదం"
                    },
                    {
                        "question_text": 'Choose the meaning of "book":',
                        "options": ["పుస్తకం", "కలం", "బల్ల", "కుర్చీ"],
                        "correct_answer": "A",
                        "explanation": "A book (పుస్తకం) is something we read.",
                        "telugu_hint": "మనం చదివే వస్తువు"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": 'Choose the synonym for "happy":',
                        "options": ["Sad", "Joyful", "Angry", "Tired"],
                        "correct_answer": "B",
                        "explanation": "Joyful means happy or filled with joy.",
                        "telugu_hint": "సంతోషంగా అనే అర్థం"
                    },
                    {
                        "question_text": 'What does "purchase" mean?',
                        "options": ["Sell", "Buy", "Return", "Exchange"],
                        "correct_answer": "B",
                        "explanation": "Purchase means to buy something.",
                        "telugu_hint": "కొనుగోలు చేయడం"
                    },
                ],
                "advanced": [
                    {
                        "question_text": 'What does "ubiquitous" mean?',
                        "options": ["Rare", "Present everywhere", "Ancient", "Mysterious"],
                        "correct_answer": "B",
                        "explanation": "Ubiquitous means existing or being everywhere at the same time.",
                        "telugu_hint": "సర్వవ్యాప్తం"
                    },
                    {
                        "question_text": 'Choose the synonym for "ephemeral":',
                        "options": ["Permanent", "Temporary", "Eternal", "Lasting"],
                        "correct_answer": "B",
                        "explanation": "Ephemeral means lasting for a very short time; temporary.",
                        "telugu_hint": "తాత్కాలికమైన"
                    },
                ],
            },
            "grammar": {
                "beginner": [
                    {
                        "question_text": "Choose the correct sentence:",
                        "options": ["I am student", "I am a student", "I be student", "I student"],
                        "correct_answer": "B",
                        "explanation": "We use 'a' before singular countable nouns.",
                        "telugu_hint": "నేను ఒక విద్యార్థిని"
                    },
                    {
                        "question_text": "Complete: She ___ to school every day.",
                        "options": ["go", "goes", "going", "gone"],
                        "correct_answer": "B",
                        "explanation": "For third person singular (she/he/it), we add 's' to the verb.",
                        "telugu_hint": "ప్రతిదినం అనే అర్థం - ప్రస్తుత కాలం"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": "Choose the correct tense: I ___ this book for two hours.",
                        "options": ["read", "am reading", "have been reading", "was reading"],
                        "correct_answer": "C",
                        "explanation": "Present perfect continuous is used for actions that started in the past and continue to the present.",
                        "telugu_hint": "గతంలో మొదలై ఇంకా కొనసాగుతోంది"
                    },
                    {
                        "question_text": "Which sentence is correct?",
                        "options": [
                            "The teacher told us to studied hard",
                            "The teacher told us studying hard",
                            "The teacher told us to study hard",
                            "The teacher told us study hard"
                        ],
                        "correct_answer": "C",
                        "explanation": "After 'tell someone to', we use base form of verb.",
                        "telugu_hint": "ఉపదేశించడం - తర్వాత base form"
                    },
                ],
                "advanced": [
                    {
                        "question_text": "Identify the correct sentence:",
                        "options": [
                            "Had I known earlier, I would have attended",
                            "Had I knew earlier, I would have attended",
                            "If I had known earlier, I will have attended",
                            "Have I known earlier, I would attended"
                        ],
                        "correct_answer": "A",
                        "explanation": "Inversion in third conditional: Had + subject + past participle = If + subject + had + past participle.",
                        "telugu_hint": "మూడవ షరతు - గతంలో జరగని పరిస్థితి"
                    },
                    {
                        "question_text": "Choose the grammatically correct sentence:",
                        "options": [
                            "Neither the students nor the teacher were present",
                            "Neither the students nor the teacher was present",
                            "Neither the students nor the teacher are present",
                            "Neither the students nor the teacher is present"
                        ],
                        "correct_answer": "B",
                        "explanation": "With 'neither...nor', the verb agrees with the nearest subject (teacher = singular).",
                        "telugu_hint": "దగ్గరగా ఉన్న subject తో agree అవాలి"
                    },
                ],
            },
            "reading": {
                "beginner": [
                    {
                        "question_text": 'Read: "The cat is on the mat." Where is the cat?',
                        "options": ["Under the mat", "On the mat", "Near the mat", "Behind the mat"],
                        "correct_answer": "B",
                        "explanation": "The sentence clearly states 'on the mat'.",
                        "telugu_hint": "పై అనే అర్థం"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": 'Read: "She enjoys reading books in her free time." What does she do?',
                        "options": ["Watches TV", "Reads books", "Plays games", "Cooks food"],
                        "correct_answer": "B",
                        "explanation": "The sentence states she enjoys reading books.",
                        "telugu_hint": "ఖాళీ సమయంలో చేసే పని"
                    },
                ],
                "advanced": [
                    {
                        "question_text": "Read: \"Despite the torrential rain, the match continued unabated.\" What happened?",
                        "options": [
                            "The match was cancelled",
                            "The match was postponed",
                            "The match continued",
                            "The match was delayed"
                        ],
                        "correct_answer": "C",
                        "explanation": "'Despite' indicates contrast; 'unabated' means without stopping.",
                        "telugu_hint": "ఆగకుండా కొనసాగింది"
                    },
                ],
            },
            "listening": {
                "beginner": [
                    {
                        "question_text": "Listen: 'How are you?' What is the correct response?",
                        "options": ["I am fine", "Yes, I am", "No, thank you", "Goodbye"],
                        "correct_answer": "A",
                        "explanation": "'How are you?' asks about your well-being.",
                        "telugu_hint": "మీ పరిస్థితి గురించి అడుగుతున్నారు"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": "Listen: 'Could you please pass the salt?' What is being requested?",
                        "options": ["To buy salt", "To pass the salt", "To taste salt", "To remove salt"],
                        "correct_answer": "B",
                        "explanation": "'Pass' means to hand over or give something to someone.",
                        "telugu_hint": "ఇవ్వమని అడుగుతున్నారు"
                    },
                ],
                "advanced": [
                    {
                        "question_text": "Listen: 'I'd appreciate it if you could expedite the process.' What is the speaker asking?",
                        "options": [
                            "To delay the process",
                            "To cancel the process",
                            "To speed up the process",
                            "To document the process"
                        ],
                        "correct_answer": "C",
                        "explanation": "'Expedite' means to make something happen more quickly.",
                        "telugu_hint": "త్వరగా చేయమని అడుగుతున్నారు"
                    },
                ],
            },
            "writing": {
                "beginner": [
                    {
                        "question_text": "Which sentence is correctly written?",
                        "options": [
                            "i like apples",
                            "I like apples",
                            "i Like Apples",
                            "I Like apples"
                        ],
                        "correct_answer": "B",
                        "explanation": "Sentences start with capital letter. 'I' is always capitalized.",
                        "telugu_hint": "వాక్యం మొదలు పెద్ద అక్షరం"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": "Choose the correctly punctuated sentence:",
                        "options": [
                            "She said I am tired",
                            "She said, I am tired",
                            'She said, "I am tired"',
                            'She said: I am tired'
                        ],
                        "correct_answer": "C",
                        "explanation": "Direct quotes need quotation marks and comma before the quote.",
                        "telugu_hint": "ప్రత్యక్ష మాటలు కొటేషన్ లో"
                    },
                ],
                "advanced": [
                    {
                        "question_text": "Identify the sentence with correct parallel structure:",
                        "options": [
                            "She likes swimming, to dance, and reading",
                            "She likes to swim, dancing, and to read",
                            "She likes swimming, dancing, and reading",
                            "She likes to swim, to dance, and reading"
                        ],
                        "correct_answer": "C",
                        "explanation": "Parallel structure means using the same grammatical form (all -ing forms).",
                        "telugu_hint": "ఒకే రూపంలో రాయాలి"
                    },
                ],
            },
            "speaking": {
                "beginner": [
                    {
                        "question_text": "What is the best response to 'What's your name?'",
                        "options": [
                            "I am fine",
                            "My name is...",
                            "Yes, please",
                            "Nice to meet you"
                        ],
                        "correct_answer": "B",
                        "explanation": "When asked about your name, you respond with 'My name is...'",
                        "telugu_hint": "పేరు చెప్పాలి"
                    },
                ],
                "intermediate": [
                    {
                        "question_text": "How would you politely disagree in a conversation?",
                        "options": [
                            "You are wrong",
                            "I don't agree",
                            "I see your point, but I have a different view",
                            "That's not true"
                        ],
                        "correct_answer": "C",
                        "explanation": "Polite disagreement acknowledges the other person's view first.",
                        "telugu_hint": "మర్యాదగా భిన్నాభిప్రాయం"
                    },
                ],
                "advanced": [
                    {
                        "question_text": "In a formal presentation, how should you transition between topics?",
                        "options": [
                            "Now I'll talk about something else",
                            "Let's move on to the next thing",
                            "Having examined X, let us now turn our attention to Y",
                            "Okay, next topic"
                        ],
                        "correct_answer": "C",
                        "explanation": "Formal presentations require sophisticated transitional phrases.",
                        "telugu_hint": "అధికారిక ప్రసంగం - సంక్లిష్ట భాష"
                    },
                ],
            },
        }

        points_map = {"beginner": 2, "intermediate": 3, "advanced": 4}

        # Get questions from the bank
        questions = []
        question_list = question_bank.get(skill_area, {}).get(level, [])
        
        # If we don't have enough questions, repeat them with different IDs
        for i in range(count):
            if question_list:
                template = question_list[i % len(question_list)]  # Cycle through available questions
                question = {
                    "question_id": f"q_{skill_area}_{level}_{i+1}",
                    "question_text": template["question_text"],
                    "options": template["options"],
                    "correct_answer": template["correct_answer"],
                    "points": points_map[level],
                    "skill_area": skill_area,
                    "difficulty_level": level,
                    "telugu_hint": template.get("telugu_hint", "సూచన అందుబాటులో లేదు"),
                    "explanation": template.get("explanation", "Standard assessment question"),
                    "question_type": "multiple_choice",
                }
                questions.append(question)

        return questions

    def _evaluate_assessment_answers(
        self, questions: List[Dict], answers: Dict
    ) -> Dict:
        """Evaluate user answers against correct answers."""
        evaluation = {
            "total_score": 0,
            "max_possible_score": 0,
            "skill_scores": {},
            "level_scores": {},
            "question_results": [],
        }

        # Initialize skill and level tracking
        for skill in self.SKILL_AREAS:
            evaluation["skill_scores"][skill] = {
                "score": 0,
                "max_score": 0,
                "questions": 0,
            }

        for level in self.ASSESSMENT_LEVELS:
            evaluation["level_scores"][level] = {
                "score": 0,
                "max_score": 0,
                "questions": 0,
            }

        # Evaluate each question
        for question in questions:
            question_id = question["question_id"]
            correct_answer = question["correct_answer"]
            points = question["points"]
            skill_area = question["skill_area"]
            difficulty_level = question["difficulty_level"]

            user_answer = answers.get(question_id, "").strip().upper()
            is_correct = user_answer == correct_answer.upper()

            # Update totals
            evaluation["max_possible_score"] += points
            if is_correct:
                evaluation["total_score"] += points

            # Update skill scores
            evaluation["skill_scores"][skill_area]["max_score"] += points
            evaluation["skill_scores"][skill_area]["questions"] += 1
            if is_correct:
                evaluation["skill_scores"][skill_area]["score"] += points

            # Update level scores
            evaluation["level_scores"][difficulty_level]["max_score"] += points
            evaluation["level_scores"][difficulty_level]["questions"] += 1
            if is_correct:
                evaluation["level_scores"][difficulty_level]["score"] += points

            # Track individual question result
            question_result = {
                "question_id": question_id,
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "points_earned": points if is_correct else 0,
                "points_possible": points,
                "skill_area": skill_area,
                "difficulty_level": difficulty_level,
            }
            evaluation["question_results"].append(question_result)

        # Calculate percentages
        for skill in evaluation["skill_scores"]:
            skill_data = evaluation["skill_scores"][skill]
            if skill_data["max_score"] > 0:
                skill_data["percentage"] = (
                    skill_data["score"] / skill_data["max_score"]
                ) * 100
            else:
                skill_data["percentage"] = 0

        for level in evaluation["level_scores"]:
            level_data = evaluation["level_scores"][level]
            if level_data["max_score"] > 0:
                level_data["percentage"] = (
                    level_data["score"] / level_data["max_score"]
                ) * 100
            else:
                level_data["percentage"] = 0

        return evaluation

    def _evaluate_single_answer(self, question: Dict, answer: str) -> Dict:
        """
        Evaluate a single answer for real-time feedback.

        Args:
            question: Question dictionary
            answer: User's answer

        Returns:
            Dictionary with evaluation results
        """
        correct_answer = question.get("correct_answer", "").strip().upper()
        user_answer = answer.strip().upper()
        points = question.get("points", 2)

        # Check if answer is correct
        is_correct = user_answer == correct_answer

        evaluation = {
            "correct": is_correct,
            "user_answer": answer,
            "correct_answer": question.get("correct_answer"),
            "points_earned": points if is_correct else 0,
            "points_possible": points,
            "skill_area": question.get("skill_area"),
            "difficulty_level": question.get("difficulty_level"),
            "explanation": question.get("explanation", "Answer recorded."),
        }

        # Add feedback message
        if is_correct:
            evaluation["feedback"] = "✅ Correct! Well done!"
            evaluation["feedback_telugu"] = "✅ సరైనది! మంచిది!"
        else:
            evaluation["feedback"] = (
                f'❌ Incorrect. The correct answer is: {question.get("correct_answer")}'
            )
            evaluation["feedback_telugu"] = (
                f'❌ తప్పు. సరైన సమాధానం: {question.get("correct_answer")}'
            )

        return evaluation

    def _analyze_proficiency_level(self, evaluation_result: Dict) -> Dict:
        """Analyze overall proficiency level based on evaluation results."""
        total_percentage = (
            evaluation_result["total_score"] / evaluation_result["max_possible_score"]
        ) * 100

        # Determine overall level
        if total_percentage >= 80:
            overall_level = "advanced"
        elif total_percentage >= 60:
            overall_level = "intermediate"
        else:
            overall_level = "beginner"

        # Analyze skill breakdown
        skill_breakdown = {}
        strengths = []
        weaknesses = []

        for skill, data in evaluation_result["skill_scores"].items():
            percentage = data["percentage"]

            if percentage >= 75:
                skill_level = "strong"
                strengths.append(skill)
            elif percentage >= 50:
                skill_level = "developing"
            else:
                skill_level = "needs_improvement"
                weaknesses.append(skill)

            skill_breakdown[skill] = {
                "level": skill_level,
                "percentage": percentage,
                "score": data["score"],
                "max_score": data["max_score"],
            }

        # Analyze level performance
        level_analysis = {}
        for level, data in evaluation_result["level_scores"].items():
            level_analysis[level] = {
                "percentage": data["percentage"],
                "ready_for_next": data["percentage"] >= 70,
            }

        return {
            "overall_level": overall_level,
            "overall_percentage": total_percentage,
            "skill_breakdown": skill_breakdown,
            "level_analysis": level_analysis,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "confidence_score": min(total_percentage / 100, 1.0),
        }

    def _recommend_learning_paths(self, proficiency_analysis: Dict) -> Dict:
        """Recommend appropriate learning paths based on proficiency analysis."""
        overall_level = proficiency_analysis["overall_level"]
        strengths = proficiency_analysis["strengths"]
        weaknesses = proficiency_analysis["weaknesses"]

        # Get available learning paths
        available_paths = LearningPath.query.filter_by(
            difficulty_level=overall_level, is_active=True
        ).all()

        recommendations = {
            "primary_path": None,
            "alternative_paths": [],
            "skill_specific_paths": [],
            "custom_path_suggestions": [],
        }

        # Recommend primary path
        if available_paths:
            primary_path = available_paths[0]
            recommendations["primary_path"] = {
                "id": primary_path.id,
                "title": primary_path.title,
                "description": primary_path.description,
                "difficulty_level": primary_path.difficulty_level,
                "estimated_duration_hours": primary_path.estimated_duration_hours,
                "match_reason": f"Matches your {overall_level} proficiency level",
            }

            # Add alternative paths
            for path in available_paths[1:3]:  # Up to 2 alternatives
                recommendations["alternative_paths"].append(
                    {
                        "id": path.id,
                        "title": path.title,
                        "description": path.description,
                        "difficulty_level": path.difficulty_level,
                    }
                )

        # Recommend skill-specific focus areas
        for weakness in weaknesses[:2]:  # Top 2 weaknesses
            recommendations["skill_specific_paths"].append(
                {
                    "skill_area": weakness,
                    "focus_type": "remedial",
                    "recommended_activities": [
                        f"Daily {weakness} practice",
                        f"{weakness.title()} fundamentals course",
                        f"Interactive {weakness} exercises",
                    ],
                    "estimated_improvement_time": "2-4 weeks",
                }
            )

        # Custom path suggestions based on analysis
        custom_suggestions = self._generate_custom_path_suggestions(
            proficiency_analysis
        )
        recommendations["custom_path_suggestions"] = custom_suggestions

        return recommendations

    def _generate_custom_path_suggestions(
        self, proficiency_analysis: Dict
    ) -> List[Dict]:
        """Generate custom learning path suggestions."""
        suggestions = []

        overall_level = proficiency_analysis["overall_level"]
        weaknesses = proficiency_analysis["weaknesses"]
        strengths = proficiency_analysis["strengths"]

        # Balanced approach suggestion
        suggestions.append(
            {
                "path_type": "balanced",
                "title": "Comprehensive English Mastery",
                "description": "Balanced approach covering all skill areas with emphasis on weak points",
                "focus_areas": weaknesses + strengths[:2],
                "weekly_structure": {
                    "skill_practice": "3 days/week",
                    "conversation": "2 days/week",
                    "review": "1 day/week",
                    "assessment": "1 day/week",
                },
                "estimated_duration": "8-12 weeks",
            }
        )

        # Intensive improvement suggestion
        if weaknesses:
            suggestions.append(
                {
                    "path_type": "intensive",
                    "title": "Targeted Skill Improvement",
                    "description": f'Intensive focus on {", ".join(weaknesses)} with rapid improvement goals',
                    "focus_areas": weaknesses,
                    "weekly_structure": {
                        "intensive_practice": "5 days/week",
                        "application": "1 day/week",
                        "assessment": "1 day/week",
                    },
                    "estimated_duration": "4-6 weeks",
                }
            )

        # Strength-based suggestion
        if strengths:
            suggestions.append(
                {
                    "path_type": "advanced",
                    "title": "Advanced Application Path",
                    "description": f'Build on your strengths in {", ".join(strengths)} for advanced applications',
                    "focus_areas": strengths,
                    "weekly_structure": {
                        "advanced_practice": "3 days/week",
                        "real_world_application": "2 days/week",
                        "creative_exercises": "2 days/week",
                    },
                    "estimated_duration": "6-8 weeks",
                }
            )

        return suggestions

    def _generate_assessment_report(
        self,
        assessment: ProficiencyAssessment,
        evaluation_result: Dict,
        proficiency_analysis: Dict,
        learning_path_recommendations: Dict,
    ) -> Dict:
        """Generate comprehensive assessment report."""
        report = {
            "assessment_summary": {
                "assessment_id": assessment.id,
                "assessment_type": assessment.assessment_type,
                "completion_date": assessment.completed_at.isoformat(),
                "duration_minutes": self._calculate_assessment_duration(assessment),
                "overall_score": f"{evaluation_result['total_score']}/{evaluation_result['max_possible_score']}",
                "percentage": round(
                    (
                        evaluation_result["total_score"]
                        / evaluation_result["max_possible_score"]
                    )
                    * 100,
                    1,
                ),
            },
            "proficiency_analysis": proficiency_analysis,
            "skill_performance": self._format_skill_performance(
                evaluation_result["skill_scores"]
            ),
            "level_readiness": self._format_level_readiness(
                evaluation_result["level_scores"]
            ),
            "strengths_and_weaknesses": {
                "top_strengths": proficiency_analysis["strengths"][:3],
                "improvement_areas": proficiency_analysis["weaknesses"][:3],
                "overall_assessment": self._generate_overall_assessment_text(
                    proficiency_analysis
                ),
            },
            "learning_recommendations": learning_path_recommendations,
            "next_steps": self._generate_detailed_next_steps(
                proficiency_analysis, learning_path_recommendations
            ),
            "telugu_summary": self._generate_telugu_report_summary(
                proficiency_analysis
            ),
            "progress_tracking": {
                "baseline_established": True,
                "recommended_reassessment": "4-6 weeks",
                "key_metrics_to_track": self._get_tracking_metrics(
                    proficiency_analysis
                ),
            },
        }

        return report

    def _generate_next_steps(
        self, proficiency_analysis: Dict, learning_path_recommendations: Dict
    ) -> List[Dict]:
        """Generate immediate next steps for the user."""
        next_steps = []

        # Step 1: Choose learning path
        if learning_path_recommendations.get("primary_path"):
            next_steps.append(
                {
                    "step": 1,
                    "action": "Choose Your Learning Path",
                    "description": "Select a learning path that matches your goals and schedule",
                    "options": [
                        learning_path_recommendations["primary_path"]["title"],
                        "Custom path based on your specific needs",
                        "Skill-specific focus areas",
                    ],
                    "estimated_time": "5 minutes",
                    "telugu_action": "మీ అభ్యాస మార్గాన్ని ఎంచుకోండి",
                }
            )

        # Step 2: Start with weak areas
        if proficiency_analysis["weaknesses"]:
            next_steps.append(
                {
                    "step": 2,
                    "action": "Begin Focused Practice",
                    "description": f"Start with {proficiency_analysis['weaknesses'][0]} exercises to build foundation",
                    "specific_activities": [
                        f"Complete 3 {proficiency_analysis['weaknesses'][0]} exercises",
                        "Review fundamental concepts",
                        "Practice daily for 15-20 minutes",
                    ],
                    "estimated_time": "20 minutes daily",
                    "telugu_action": "దృష్టి కేంద్రీకృత అభ్యాసం ప్రారంభించండి",
                }
            )

        # Step 3: Set goals and tracking
        next_steps.append(
            {
                "step": 3,
                "action": "Set Learning Goals",
                "description": "Define specific, measurable goals for your English learning journey",
                "goal_suggestions": [
                    "Improve vocabulary by 50 words/week",
                    "Achieve 80% accuracy in grammar exercises",
                    "Complete 5 reading comprehension activities/week",
                ],
                "estimated_time": "10 minutes",
                "telugu_action": "అభ్యాస లక్ష్యాలను నిర్ణయించండి",
            }
        )

        return next_steps

    def _get_assessment_instructions(self, assessment_type: str) -> str:
        """Get English instructions for assessment."""
        instructions = {
            "comprehensive": """
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
            "quick": """
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
            "adaptive": """
                Adaptive English Assessment
                
                This assessment adapts to your responses, providing questions that match your skill level.
                
                Instructions:
                1. Start with the given questions
                2. Additional questions may be presented based on your answers
                3. Take your time with each question
                4. The assessment ends when we have enough information about your level
                
                Expected duration: 20-30 minutes.
            """,
        }

        return instructions.get(assessment_type, instructions["comprehensive"])

    def _get_telugu_instructions(self, assessment_type: str) -> str:
        """Get Telugu instructions for assessment."""
        instructions = {
            "comprehensive": """
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
            "quick": """
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
            "adaptive": """
                అనుకూల ఇంగ్లీష్ మూల్యాంకనం
                
                ఈ మూల్యాంకనం మీ స్పందనలకు అనుగుణంగా మారుతుంది, మీ నైపుణ్య స్థాయికి సరిపోలే ప్రశ్నలను అందిస్తుంది.
                
                సూచనలు:
                1. ఇవ్వబడిన ప్రశ్నలతో ప్రారంభించండి
                2. మీ సమాధానాల ఆధారంగా అదనపు ప్రశ్నలు అందించవచ్చు
                3. ప్రతి ప్రశ్నతో మీ సమయాన్ని తీసుకోండి
                4. మీ స్థాయి గురించి తగినంత సమాచారం వచ్చినప్పుడు మూల్యాంకనం ముగుస్తుంది
                
                అంచనా వ్యవధి: 20-30 నిమిషాలు.
            """,
        }

        return instructions.get(assessment_type, instructions["comprehensive"])

    def _calculate_assessment_duration(
        self, assessment: ProficiencyAssessment
    ) -> Optional[int]:
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
                "percentage": round(data["percentage"], 1),
                "score": f"{data['score']}/{data['max_score']}",
                "level": (
                    "Strong"
                    if data["percentage"] >= 75
                    else (
                        "Developing"
                        if data["percentage"] >= 50
                        else "Needs Improvement"
                    )
                ),
                "questions_answered": data["questions"],
            }
        return formatted

    def _format_level_readiness(self, level_scores: Dict) -> Dict:
        """Format level readiness information."""
        formatted = {}
        for level, data in level_scores.items():
            formatted[level] = {
                "percentage": round(data["percentage"], 1),
                "ready": data["percentage"] >= 70,
                "confidence": (
                    "High"
                    if data["percentage"] >= 80
                    else "Medium" if data["percentage"] >= 60 else "Low"
                ),
            }
        return formatted

    def _generate_overall_assessment_text(self, proficiency_analysis: Dict) -> str:
        """Generate overall assessment text."""
        level = proficiency_analysis["overall_level"]
        percentage = proficiency_analysis["overall_percentage"]

        if level == "advanced":
            return f"Excellent performance with {percentage:.1f}% overall accuracy. You demonstrate strong command of English across multiple skill areas."
        elif level == "intermediate":
            return f"Good performance with {percentage:.1f}% overall accuracy. You have a solid foundation with room for targeted improvement."
        else:
            return f"Developing skills with {percentage:.1f}% overall accuracy. Focus on building fundamental skills will help you progress quickly."

    def _generate_detailed_next_steps(
        self, proficiency_analysis: Dict, learning_path_recommendations: Dict
    ) -> List[str]:
        """Generate detailed next steps list."""
        steps = []

        # Immediate actions based on level
        level = proficiency_analysis["overall_level"]
        if level == "beginner":
            steps.extend(
                [
                    "Start with vocabulary building exercises daily",
                    "Focus on basic grammar patterns",
                    "Practice simple reading comprehension",
                    "Use Telugu-English translation exercises",
                ]
            )
        elif level == "intermediate":
            steps.extend(
                [
                    "Expand vocabulary with topic-specific words",
                    "Practice complex sentence structures",
                    "Engage in conversation practice",
                    "Work on listening comprehension skills",
                ]
            )
        else:  # advanced
            steps.extend(
                [
                    "Focus on nuanced vocabulary and idioms",
                    "Practice advanced writing techniques",
                    "Engage in debates and discussions",
                    "Read advanced texts and literature",
                ]
            )

        # Add weakness-specific steps
        for weakness in proficiency_analysis["weaknesses"][:2]:
            steps.append(f"Dedicate extra time to {weakness} practice sessions")

        return steps

    def _generate_telugu_report_summary(self, proficiency_analysis: Dict) -> str:
        """Generate Telugu summary of the report."""
        level = proficiency_analysis["overall_level"]
        percentage = proficiency_analysis["overall_percentage"]

        level_telugu = {
            "beginner": "ప్రాథమిక",
            "intermediate": "మధ్యస్థ",
            "advanced": "ఉన్నత",
        }

        summary = f"""
        మీ ఇంగ్లీష్ ప్రావీణ్య స్థాయి: {level_telugu.get(level, level)}
        మొత్తం స్కోర్: {percentage:.1f}%
        
        """

        if proficiency_analysis["strengths"]:
            summary += f"మీ బలాలు: {', '.join(proficiency_analysis['strengths'])}\n"

        if proficiency_analysis["weaknesses"]:
            summary += (
                f"మెరుగుపరచవలసిన రంగాలు: {', '.join(proficiency_analysis['weaknesses'])}\n"
            )

        summary += "\nమీ అభ్యాస ప్రయాణం కోసం వ్యక్తిగతీకరించిన సిఫార్సులు తయారు చేయబడ్డాయి."

        return summary

    def _get_tracking_metrics(self, proficiency_analysis: Dict) -> List[str]:
        """Get key metrics to track progress."""
        metrics = [
            "Overall accuracy percentage",
            "Vocabulary acquisition rate",
            "Grammar accuracy improvement",
            "Reading comprehension speed",
        ]

        # Add weakness-specific metrics
        for weakness in proficiency_analysis["weaknesses"]:
            metrics.append(f"{weakness.title()} skill improvement")

        return metrics

    def _generate_adaptive_config(self, previous_results: Dict) -> Dict:
        """Generate adaptive configuration based on previous assessment."""
        # Analyze previous weak areas for focused assessment
        skill_scores = previous_results.get("skill_scores", {})
        focus_areas = []

        for skill, data in skill_scores.items():
            if data.get("percentage", 0) < 60:
                focus_areas.append(skill)

        # Determine starting difficulty
        overall_percentage = (
            previous_results.get("total_score", 0)
            / previous_results.get("max_possible_score", 1)
        ) * 100

        if overall_percentage >= 70:
            difficulty = "intermediate"
        elif overall_percentage >= 40:
            difficulty = "beginner_plus"
        else:
            difficulty = "beginner"

        return {
            "focus_areas": focus_areas[:3],  # Top 3 weak areas
            "difficulty": difficulty,
            "questions_per_area": 3,
        }

    def _generate_skill_focused_assessment(self, skill_area: str) -> Dict:
        """Generate assessment focused on specific skill area."""
        questions = []
        total_score = 0

        # Generate questions across levels for the specific skill
        for level in self.ASSESSMENT_LEVELS:
            skill_questions = self._generate_skill_level_questions(skill_area, level, 2)
            questions.extend(skill_questions)
            total_score += sum(q["points"] for q in skill_questions)

        return {
            "questions": questions,
            "max_score": total_score,
            "metadata": {
                "skill_focus": skill_area,
                "total_questions": len(questions),
                "levels_covered": self.ASSESSMENT_LEVELS,
                "estimated_duration": 20,
            },
            "instructions": {
                "english": f"This assessment focuses specifically on {skill_area} skills. Complete all questions to get an accurate assessment of your {skill_area} proficiency.",
                "telugu": f"ఈ మూల్యాంకనం ప్రత్యేకంగా {skill_area} నైపుణ్యాలపై దృష్టి పెడుతుంది। మీ {skill_area} ప్రావీణ్యం యొక్క ఖచ్చితమైన మూల్యాంకనం పొందడానికి అన్ని ప్రశ్నలను పూర్తి చేయండి।",
            },
        }
