from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db,
    User,
    Chapter,
    UserChapterProgress,
    PracticeSession,
    UserNotes,
    TestAssessment,
    AIConversationContext,
    UserPracticeSession,
)
from app.services.activity_generator_service import ActivityGeneratorService, _extract_json_from_response
from app.services.personalization_service import PersonalizationService
from app.services.llm_config import LLMConfig
from datetime import datetime
import json

practice_bp = Blueprint("practice", __name__)
activity_service = ActivityGeneratorService()
personalization_service = PersonalizationService()


@practice_bp.route("/generate-questions", methods=["POST"])
@jwt_required()
def generate_general_questions():
    """
    Generate practice questions without requiring a specific session.

    Expected JSON:
    {
        "topic": "greetings",           // topic or chapter name
        "difficulty": "beginner",      // "beginner", "intermediate", "advanced"
        "num_questions": 5,            // number of questions to generate
        "question_types": ["multiple_choice", "fill_blank", "translation"],
        "language_focus": "vocabulary" // "vocabulary", "grammar", "pronunciation", "mixed"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        topic = data.get("topic", "general")
        difficulty = data.get("difficulty", "beginner")
        num_questions = data.get("num_questions", 5)
        question_types = data.get("question_types", ["multiple_choice"])
        language_focus = data.get("language_focus", "vocabulary")

        # Get user profile for personalization
        user = User.query.get(user_id)
        user_proficiency = (
            user.profile.proficiency_level if user.profile else "beginner"
        )

        # Validate inputs
        if num_questions > 20:
            return (
                jsonify(
                    {
                        "error": "Maximum 20 questions allowed per request",
                        "telugu_message": "ప్రతి అభ్యర్థనకు గరిష్టంగా 20 ప్రశ్నలు అనుమతించబడతాయి",
                    }
                ),
                400,
            )

        valid_types = [
            "multiple_choice",
            "fill_blank",
            "translation",
            "true_false",
            "matching",
        ]
        if not all(qtype in valid_types for qtype in question_types):
            return (
                jsonify(
                    {
                        "error": f'Invalid question types. Valid types: {", ".join(valid_types)}',
                        "telugu_message": "చెల్లని ప్రశ్న రకాలు",
                    }
                ),
                400,
            )

        # Generate ALL questions in a single AI call (much more efficient)
        prompt = f"""
        Generate {num_questions} practice questions for Telugu speakers learning English.
        
        Context:
        - Topic: {topic}
        - Difficulty: {difficulty}
        - User proficiency: {user_proficiency}
        - Language focus: {language_focus}
        - Question types to include: {', '.join(question_types)}
        
        Requirements:
        - Questions should be appropriate for {difficulty} level
        - Include Telugu translations where helpful
        - Focus on {language_focus} skills
        - Make them engaging and practical
        - Distribute question types across {', '.join(question_types)}
        
        Return JSON array with {num_questions} questions in this exact format:
        [
            {{
                "question_id": "q_1",
                "type": "<question_type>",
                "question": "Question text here",
                "telugu_question": "Telugu translation",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "Why this answer is correct",
                "telugu_explanation": "Telugu explanation",
                "difficulty_level": "{difficulty}",
                "topic": "{topic}",
                "points": 10
            }},
            ...
        ]
        """

        try:
            from app.services.llm_config import LLMConfig
            from app.services.activity_generator_service import _extract_json_from_response
            
            result = LLMConfig.generate_text(prompt, json_mode=True)
            if not result['success']:
                current_app.logger.warning(f"LLM generation failed: {result.get('error')}")
                questions = []
            else:
                response_data = _extract_json_from_response(result['text'])
                
                # Check if JSON parsing failed (response contains error key)
                if isinstance(response_data, dict) and 'error' in response_data:
                    current_app.logger.warning(f"JSON parsing error: {response_data.get('error')}")
                    current_app.logger.debug(f"Raw response: {result['text'][:500]}")  # Log first 500 chars
                    questions = []
                # Handle if response is wrapped in a parent object
                elif isinstance(response_data, dict) and 'questions' in response_data:
                    questions = response_data['questions']
                elif isinstance(response_data, list):
                    questions = response_data
                else:
                    current_app.logger.warning(f"Unexpected response format: {type(response_data)}")
                    questions = []
                
                # Filter and validate questions
                valid_questions = []
                for i, q in enumerate(questions):
                    # Only process if q is a dictionary
                    if not isinstance(q, dict):
                        current_app.logger.warning(f"Question {i} is not a dict, skipping: {type(q)}")
                        continue
                    
                    # Ensure each question has proper structure
                    if not q.get("question_id"):
                        q["question_id"] = f"q_{i+1}"
                    if not q.get("type"):
                        q["type"] = question_types[i % len(question_types)]
                    if not q.get("topic"):
                        q["topic"] = topic
                    if not q.get("difficulty_level"):
                        q["difficulty_level"] = difficulty
                    if not q.get("points"):
                        q["points"] = 10
                    
                    valid_questions.append(q)
                
                questions = valid_questions

            # If AI failed or returned no questions, create fallback questions
            if len(questions) < num_questions:
                current_app.logger.warning(
                    f"AI generated only {len(questions)} of {num_questions} questions, adding fallbacks"
                )
                for i in range(len(questions), num_questions):
                    fallback_question = {
                        "question_id": f"q_{i+1}",
                        "type": question_types[i % len(question_types)],
                        "question": f"Choose the correct {language_focus} for {topic}:",
                        "telugu_question": f"{topic} కోసం సరైన {language_focus} ను ఎంచుకోండి:",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "This is the correct answer",
                        "telugu_explanation": "ఇది సరైన సమాధానం",
                        "difficulty_level": difficulty,
                        "topic": topic,
                        "points": 10,
                    }
                    questions.append(fallback_question)

        except Exception as e:
            current_app.logger.warning(
                f"AI question generation failed: {str(e)}, using fallback questions"
            )
            # Create all fallback questions
            questions = []
            for i in range(num_questions):
                fallback_question = {
                    "question_id": f"q_{i+1}",
                    "type": question_types[i % len(question_types)],
                    "question": f"Choose the correct {language_focus} for {topic}:",
                    "telugu_question": f"{topic} కోసం సరైన {language_focus} ను ఎంచుకోండి:",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "This is the correct answer",
                    "telugu_explanation": "ఇది సరైన సమాధానం",
                    "difficulty_level": difficulty,
                    "topic": topic,
                    "points": 10,
                }
                questions.append(fallback_question)

        return (
            jsonify(
                {
                    "message": "Questions generated successfully!",
                    "telugu_message": "ప్రశ్నలు విజయవంతంగా రూపొందించబడ్డాయి!",
                    "questions": questions,
                    "metadata": {
                        "total_questions": len(questions),
                        "topic": topic,
                        "difficulty": difficulty,
                        "question_types": question_types,
                        "language_focus": language_focus,
                        "estimated_time": len(questions) * 2,  # 2 minutes per question
                        "points_possible": sum(q.get("points", 10) for q in questions),
                    },
                    "instructions": {
                        "english": f"Complete {len(questions)} questions about {topic}. Take your time and read carefully.",
                        "telugu": f"{topic} గురించి {len(questions)} ప్రశ్నలను పూర్తి చేయండి. మీ సమయం తీసుకోండి మరియు జాగ్రత్తగా చదవండి.",
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error generating questions: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to generate questions",
                    "telugu_message": "ప్రశ్నలు రూపొందించడంలో విఫలం",
                }
            ),
            500,
        )


@practice_bp.route("/submit-answer", methods=["POST"])
@jwt_required()
def submit_general_answer():
    """
    Submit an answer for evaluation without requiring a specific practice session.

    Expected JSON:
    {
        "question_id": "q_1",
        "question_type": "multiple_choice",
        "user_answer": "Good morning",
        "correct_answer": "Good morning",
        "question_text": "Which greeting is most appropriate for morning?",
        "options": ["Good morning", "Good night", "Good evening", "Good afternoon"]  // for multiple choice
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        question_id = data.get("question_id")
        question_type = data.get("question_type")
        user_answer = data.get("user_answer")
        correct_answer = data.get("correct_answer")
        question_text = data.get("question_text", "")
        options = data.get("options", [])

        if not all(
            [question_id, question_type, user_answer is not None, correct_answer]
        ):
            return (
                jsonify(
                    {
                        "error": "Missing required fields: question_id, question_type, user_answer, correct_answer",
                        "telugu_message": "అవసరమైన ఫీల్డ్‌లు లేవు",
                    }
                ),
                400,
            )

        # Evaluate the answer
        is_correct = False
        score = 0

        if question_type == "multiple_choice":
            is_correct = (
                str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            )
            score = 10 if is_correct else 0
        elif question_type == "fill_blank":
            # For fill in the blank, be more lenient with matching
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(correct_answer).strip().lower()
            is_correct = user_clean == correct_clean or user_clean in correct_clean
            score = 10 if is_correct else 0
        elif question_type == "translation":
            # For translation, use fuzzy matching
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(correct_answer).strip().lower()
            # Simple fuzzy matching - check if most words match
            user_words = set(user_clean.split())
            correct_words = set(correct_clean.split())
            if len(correct_words) > 0:
                match_ratio = len(user_words.intersection(correct_words)) / len(
                    correct_words
                )
                is_correct = match_ratio >= 0.7  # 70% word match threshold
                score = int(10 * match_ratio) if match_ratio >= 0.7 else 0
            else:
                is_correct = user_clean == correct_clean
                score = 10 if is_correct else 0
        elif question_type == "true_false":
            user_bool = str(user_answer).strip().lower() in [
                "true",
                "yes",
                "1",
                "correct",
            ]
            correct_bool = str(correct_answer).strip().lower() in [
                "true",
                "yes",
                "1",
                "correct",
            ]
            is_correct = user_bool == correct_bool
            score = 10 if is_correct else 0
        else:
            # Default exact match for other types
            is_correct = (
                str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            )
            score = 10 if is_correct else 0

        # Generate feedback using AI
        feedback_prompt = f"""
        Provide helpful feedback for this English learning question response.
        
        Question: "{question_text}"
        Question Type: {question_type}
        User Answer: "{user_answer}"
        Correct Answer: "{correct_answer}"
        Is Correct: {is_correct}
        
        Provide feedback in both English and Telugu:
        1. If correct: Encouraging message and why it's right
        2. If incorrect: Gentle correction, explanation, and encouragement
        3. Include a helpful tip for remembering this concept
        
        Return JSON format:
        {{
            "feedback": "English feedback",
            "telugu_feedback": "Telugu feedback",
            "tip": "Learning tip in English",
            "telugu_tip": "Learning tip in Telugu"
        }}
        """

        try:
            result = LLMConfig.generate_text(feedback_prompt, json_mode=True)
            if result['success']:
                feedback_data = _extract_json_from_response(result['text'])
                # Check if JSON parsing failed
                if isinstance(feedback_data, dict) and 'error' in feedback_data:
                    current_app.logger.warning(f"JSON parsing error in feedback: {feedback_data.get('error')}")
                    raise Exception("Failed to parse feedback JSON")
            else:
                raise Exception(result.get('error', 'LLM generation failed'))
        except Exception as e:
            current_app.logger.warning(f"AI feedback generation failed: {str(e)}")
            # Fallback feedback
            if is_correct:
                feedback_data = {
                    "feedback": "Correct! Well done!",
                    "telugu_feedback": "సరైనది! బాగా చేసారు!",
                    "tip": "Keep practicing to build confidence",
                    "telugu_tip": "ఆత్మవిశ్వాసం పెంచుకోవడానికి అభ్యసించడం కొనసాగించండి",
                }
            else:
                feedback_data = {
                    "feedback": f"Not quite right. The correct answer is '{correct_answer}'. Try again!",
                    "telugu_feedback": f"పూర్తిగా సరైనది కాదు. సరైన సమాధానం '{correct_answer}'. మళ్లీ ప్రయత్నించండి!",
                    "tip": "Read the question carefully before answering",
                    "telugu_tip": "సమాధానం ఇవ్వడానికి ముందు ప్రశ్నను జాగ్రత్తగా చదవండి",
                }

        # Calculate performance metrics
        response_time = data.get("response_time", 0)  # Optional field
        difficulty_level = data.get("difficulty_level", "beginner")

        # Store the practice interaction (you might want to create a model for this)
        practice_data = {
            "user_id": user_id,
            "question_id": question_id,
            "question_type": question_type,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "score": score,
            "response_time": response_time,
            "difficulty_level": difficulty_level,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Log the practice interaction
        current_app.logger.info(f"Practice answer submitted: {practice_data}")

        return (
            jsonify(
                {
                    "message": "Answer submitted successfully!",
                    "telugu_message": "సమాధానం విజయవంతంగా సమర్పించబడింది!",
                    "result": {
                        "question_id": question_id,
                        "is_correct": is_correct,
                        "score": score,
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                        "percentage": (score / 10) * 100,
                    },
                    "feedback": feedback_data.get("feedback", "Good effort!"),
                    "telugu_feedback": feedback_data.get(
                        "telugu_feedback", "మంచి ప్రయత్నం!"
                    ),
                    "tip": feedback_data.get("tip", "Keep practicing!"),
                    "telugu_tip": feedback_data.get("telugu_tip", "అభ్యసించడం కొనసాగించండి!"),
                    "performance": {
                        "response_time": response_time,
                        "difficulty_level": difficulty_level,
                        "score_percentage": (score / 10) * 100,
                    },
                    "encouragement": {
                        "english": "Great job practicing! Every answer helps you improve.",
                        "telugu": "అభ్యసించినందుకు అద్భుతం! ప్రతి సమాధానం మిమ్మల్ని మెరుగుపరచుతుంది.",
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error submitting answer: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to submit answer",
                    "telugu_message": "సమాధానం సమర్పించడంలో విఫలం",
                }
            ),
            500,
        )


@practice_bp.route("/<int:session_id>/complete", methods=["POST"])
@jwt_required()
def complete_session_simple(session_id):
    """
    Complete a practice session - simple URL format.
    Same functionality as complete_practice_session() but with simpler URL.
    """
    return complete_practice_session(session_id)


@practice_bp.route("/practice/<int:session_id>/generate-questions", methods=["POST"])
@jwt_required()
def generate_practice_questions(session_id):
    """
    Generate practice questions for a session based on chapter content and user score history.

    Expected JSON:
    {
        "num_questions": 5,
        "question_types": ["multiple_choice", "fill_blank", "translation"]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}

        num_questions = data.get("num_questions", 5)
        question_types = data.get("question_types", ["multiple_choice"])

        # Get practice session
        session = PracticeSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()

        if not session:
            return (
                jsonify(
                    {
                        "error": "Practice session not found",
                        "telugu_message": "అభ్యాస సెషన్ కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        if session.is_completed:
            return (
                jsonify(
                    {
                        "error": "Practice session already completed",
                        "telugu_message": "అభ్యాస సెషన్ ఇప్పటికే పూర్తయింది",
                    }
                ),
                400,
            )

        # Get chapter information
        chapter = Chapter.query.get(session.chapter_id)
        if not chapter:
            return (
                jsonify(
                    {"error": "Chapter not found", "telugu_message": "అధ్యాయం కనుగొనబడలేదు"}
                ),
                404,
            )

        # Get user's previous performance in this chapter
        user_progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=session.chapter_id
        ).first()

        # Determine difficulty based on user's previous scores
        difficulty_level = _determine_adaptive_difficulty(
            user_progress, chapter.difficulty_level
        )

        # Generate questions using AI based on chapter content and user history
        questions = _generate_adaptive_questions(
            chapter, user_progress, num_questions, question_types, difficulty_level
        )

        # Store questions in session
        session.questions_data = questions
        session.total_questions = len(questions)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Practice questions generated successfully!",
                    "telugu_message": "అభ్యాస ప్రశ్నలు విజయవంతంగా రూపొందించబడ్డాయి!",
                    "questions": questions,
                    "session_info": {
                        "id": session.id,
                        "total_questions": session.total_questions,
                        "difficulty_level": difficulty_level,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error generating questions: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to generate questions",
                    "telugu_message": "ప్రశ్నలు రూపొందించడంలో విఫలం",
                }
            ),
            500,
        )


@practice_bp.route("/practice/<int:session_id>/submit-answer", methods=["POST"])
@jwt_required()
def submit_practice_answer(session_id):
    """
    Submit an answer for a practice question and get immediate feedback.

    Expected JSON:
    {
        "question_id": "q_1",
        "user_answer": "The answer text",
        "time_spent_seconds": 45
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        question_id = data.get("question_id")
        user_answer = data.get("user_answer")
        time_spent = data.get("time_spent_seconds", 0)

        if not question_id or not user_answer:
            return (
                jsonify(
                    {
                        "error": "Question ID and answer are required",
                        "telugu_message": "ప్రశ్న ID మరియు సమాధానం అవసరం",
                    }
                ),
                400,
            )

        # Get practice session
        session = PracticeSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()

        if not session:
            return (
                jsonify(
                    {
                        "error": "Practice session not found",
                        "telugu_message": "అభ్యాస సెషన్ కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        # Find the question in session data
        questions = session.questions_data or []
        question = None
        for q in questions:
            if q.get("id") == question_id:
                question = q
                break

        if not question:
            return (
                jsonify(
                    {"error": "Question not found", "telugu_message": "ప్రశ్న కనుగొనబడలేదు"}
                ),
                404,
            )

        # Evaluate the answer
        is_correct, feedback = _evaluate_answer(question, user_answer)

        # Store user response
        user_responses = session.user_responses or []
        response_data = {
            "question_id": question_id,
            "user_answer": user_answer,
            "correct_answer": question.get("correct_answer"),
            "is_correct": is_correct,
            "time_spent_seconds": time_spent,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat(),
        }
        user_responses.append(response_data)
        session.user_responses = user_responses

        # Update session statistics
        if is_correct:
            session.correct_answers = (session.correct_answers or 0) + 1

        # Calculate current score
        total_answered = len(user_responses)
        session.score_percentage = (
            (session.correct_answers / total_answered) * 100
            if total_answered > 0
            else 0
        )

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Answer submitted successfully!",
                    "telugu_message": "సమాధానం విజయవంతంగా సమర్పించబడింది!",
                    "result": {
                        "is_correct": is_correct,
                        "feedback": feedback,
                        "correct_answer": question.get("correct_answer"),
                        "explanation": question.get("explanation"),
                        "current_score": session.score_percentage,
                        "questions_answered": total_answered,
                        "questions_remaining": session.total_questions - total_answered,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting answer: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to submit answer",
                    "telugu_message": "సమాధానం సమర్పించడంలో విఫలం",
                }
            ),
            500,
        )


@practice_bp.route("/practice/<int:session_id>/complete", methods=["POST"])
@jwt_required()
def complete_practice_session(session_id):
    """
    Complete a practice session and update user progress.
    """
    try:
        user_id = int(get_jwt_identity())

        # Get practice session
        session = PracticeSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()

        if not session:
            return (
                jsonify(
                    {
                        "error": "Practice session not found",
                        "telugu_message": "అభ్యాస సెషన్ కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        if session.is_completed:
            return (
                jsonify(
                    {
                        "error": "Session already completed",
                        "telugu_message": "సెషన్ ఇప్పటికే పూర్తయింది",
                    }
                ),
                400,
            )

        # Complete the session
        session.end_time = datetime.utcnow()
        session.duration_minutes = int(
            (session.end_time - session.start_time).total_seconds() / 60
        )
        session.is_completed = True

        # Generate session summary using AI
        session_summary = _generate_session_summary(session)
        session.session_summary = session_summary

        # Update user chapter progress
        progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=session.chapter_id
        ).first()

        if progress:
            # Update best score if this session was better
            if session.score_percentage > progress.best_score:
                progress.best_score = session.score_percentage

            # Update average score
            progress.total_attempts += 1
            if progress.total_attempts == 1:
                progress.average_score = session.score_percentage
            else:
                progress.average_score = (
                    (progress.average_score * (progress.total_attempts - 1))
                    + session.score_percentage
                ) / progress.total_attempts

            # Update time spent
            progress.time_spent_minutes += session.duration_minutes

            # Update status based on score
            chapter = Chapter.query.get(session.chapter_id)
            if chapter and session.score_percentage >= (
                chapter.required_score_to_pass * 100
            ):
                if progress.status in ["not_started", "in_progress"]:
                    progress.status = "completed"
                    progress.completed_at = datetime.utcnow()
                elif session.score_percentage >= 90:  # Mastered if 90%+
                    progress.status = "mastered"

        # Save to UserPracticeSession for complete history tracking
        # Extract questions and answers from session
        questions_list = session.questions_data or []
        answers_list = session.user_responses or []
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        for response in answers_list:
            if response.get("is_correct"):
                question_type = next((q.get("type") for q in questions_list if q.get("id") == response.get("question_id")), None)
                if question_type and question_type not in strengths:
                    strengths.append(question_type)
            else:
                question_type = next((q.get("type") for q in questions_list if q.get("id") == response.get("question_id")), None)
                if question_type and question_type not in weaknesses:
                    weaknesses.append(question_type)
        
        practice_entry = UserPracticeSession(
            user_id=user_id,
            session_id=session.id,
            chapter_id=session.chapter_id,
            practice_type=session.session_type or "practice",
            questions=questions_list,
            user_answers=answers_list,
            score=session.score_percentage,
            total_questions=session.total_questions,
            correct_answers=session.correct_answers,
            ai_feedback=session_summary.get("feedback", "") if session_summary else "",
            strengths=strengths if strengths else None,
            weaknesses=weaknesses if weaknesses else None,
            time_spent_seconds=int(session.duration_minutes * 60),
            recommendations=session_summary.get("recommendations") if session_summary else None,
            completed_at=datetime.utcnow(),
        )
        db.session.add(practice_entry)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Practice session completed successfully!",
                    "telugu_message": "అభ్యాస సెషన్ విజయవంతంగా పూర్తైంది!",
                    "session_results": {
                        "session_id": session.id,
                        "score_percentage": session.score_percentage,
                        "total_questions": session.total_questions,
                        "correct_answers": session.correct_answers,
                        "duration_minutes": session.duration_minutes,
                        "session_summary": session_summary,
                        "progress_updated": {
                            "status": progress.status if progress else "unknown",
                            "best_score": progress.best_score if progress else 0,
                            "total_attempts": (
                                progress.total_attempts if progress else 0
                            ),
                        },
                    },
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing session: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to complete session",
                    "telugu_message": "సెషన్ పూర్తి చేయడంలో విఫలం",
                }
            ),
            500,
        )


def _determine_adaptive_difficulty(user_progress, default_difficulty):
    """
    Determine adaptive difficulty based on user's previous performance.
    """
    if not user_progress:
        return default_difficulty

    avg_score = user_progress.average_score

    if avg_score >= 0.85:  # 85%+ - increase difficulty
        difficulty_levels = ["beginner", "intermediate", "advanced"]
        current_index = difficulty_levels.index(default_difficulty)
        return difficulty_levels[min(current_index + 1, len(difficulty_levels) - 1)]
    elif avg_score <= 0.6:  # 60%- - decrease difficulty
        difficulty_levels = ["beginner", "intermediate", "advanced"]
        current_index = difficulty_levels.index(default_difficulty)
        return difficulty_levels[max(current_index - 1, 0)]

    return default_difficulty


def _generate_adaptive_questions(
    chapter, user_progress, num_questions, question_types, difficulty_level
):
    """
    Generate adaptive questions using AI based on chapter content and user history.
    """
    try:
        # Analyze user's weak areas from previous attempts
        weak_areas = []
        if user_progress and user_progress.total_attempts > 0:
            # This would analyze previous session data to identify weak areas
            weak_areas = _analyze_user_weaknesses(user_progress)

        # Create context for AI question generation
        context = {
            "chapter_topic": chapter.topic,
            "chapter_subtopics": chapter.subtopics,
            "difficulty_level": difficulty_level,
            "user_weak_areas": weak_areas,
            "previous_average_score": (
                user_progress.average_score if user_progress else 0
            ),
            "question_types": question_types,
        }

        # Generate questions using AI
        prompt = f"""
        Generate {num_questions} English learning practice questions for Telugu speakers.
        
        Chapter Context:
        - Topic: {chapter.topic}
        - Subtopics: {chapter.subtopics}
        - Difficulty: {difficulty_level}
        - Question Types: {question_types}
        
        User Context:
        - Previous Average Score: {context['previous_average_score']*100:.1f}%
        - Weak Areas: {weak_areas}
        
        Focus on areas where the user needs improvement. Return JSON format:
        {{
            "questions": [
                {{
                    "id": "q_1",
                    "type": "multiple_choice",
                    "question_text": "What does 'beautiful' mean in Telugu?",
                    "question_telugu": "'beautiful' అంటే తెలుగులో ఏమిటి?",
                    "options": ["అందమైన", "పెద్ద", "చిన్న", "వేగవంతమైన"],
                    "correct_answer": "అందమైన",
                    "explanation": "Beautiful means అందమైన in Telugu",
                    "difficulty": "{difficulty_level}",
                    "skill_tested": "vocabulary"
                }}
            ]
        }}
        """

        result = LLMConfig.generate_text(prompt, json_mode=True)
        if not result['success']:
            current_app.logger.error(f"LLM generation failed: {result.get('error')}")
            return _get_fallback_questions(chapter, num_questions, question_types)
        questions_data = _extract_json_from_response(result['text'])

        return questions_data.get("questions", [])

    except Exception as e:
        current_app.logger.error(f"Error generating adaptive questions: {str(e)}")
        # Return fallback questions
        return _get_fallback_questions(chapter, num_questions, question_types)


def _analyze_user_weaknesses(user_progress):
    """
    Analyze user's previous attempts to identify weak areas.
    """
    # This would analyze session data to identify patterns
    # For now, return common weak areas
    return ["vocabulary", "grammar", "sentence_structure"]


def _get_fallback_questions(chapter, num_questions, question_types):
    """
    Generate fallback questions if AI generation fails.
    """
    return [
        {
            "id": f"fallback_{i}",
            "type": "multiple_choice",
            "question_text": f"Practice question {i+1} for {chapter.topic}",
            "question_telugu": f"{chapter.topic} కోసం అభ్యాస ప్రశ్న {i+1}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "This is a fallback question",
            "difficulty": chapter.difficulty_level,
            "skill_tested": "general",
        }
        for i in range(num_questions)
    ]


def _evaluate_answer(question, user_answer):
    """
    Evaluate user's answer and provide feedback.
    """
    correct_answer = question.get("correct_answer", "").strip().lower()
    user_answer_normalized = user_answer.strip().lower()

    # Simple exact match for now - could be enhanced with fuzzy matching
    is_correct = user_answer_normalized == correct_answer

    if is_correct:
        feedback = {
            "message": "Correct! Well done!",
            "telugu_message": "సరైనది! బాగా చేసారు!",
            "type": "success",
        }
    else:
        feedback = {
            "message": f'Incorrect. The correct answer is: {question.get("correct_answer")}',
            "telugu_message": f'తప్పు. సరైన సమాధానం: {question.get("correct_answer")}',
            "explanation": question.get("explanation", ""),
            "type": "error",
        }

    return is_correct, feedback


def _generate_session_summary(session):
    """
    Generate AI-powered session summary.
    """
    try:
        prompt = f"""
        Generate a learning session summary for a Telugu speaker learning English.
        
        Session Data:
        - Total Questions: {session.total_questions}
        - Correct Answers: {session.correct_answers}
        - Score: {session.score_percentage:.1f}%
        - Duration: {session.duration_minutes} minutes
        
        Provide encouraging feedback and specific recommendations for improvement.
        Include both English and Telugu text.
        """

        result = LLMConfig.generate_text(prompt, json_mode=False)
        if not result['success']:
            current_app.logger.error(f"LLM generation failed: {result.get('error')}")
            return {
                "ai_summary": "Session completed successfully!",
                "score_analysis": _analyze_score_performance(session.score_percentage),
                "recommendations": _get_performance_recommendations(
                    session.score_percentage
                ),
            }
        return {
            "ai_summary": result['text'].strip(),
            "score_analysis": _analyze_score_performance(session.score_percentage),
            "recommendations": _get_performance_recommendations(
                session.score_percentage
            ),
        }

    except Exception as e:
        current_app.logger.error(f"Error generating session summary: {str(e)}")
        return {
            "ai_summary": "Session completed successfully!",
            "score_analysis": "Performance recorded.",
            "recommendations": ["Continue practicing regularly."],
        }


def _analyze_score_performance(score_percentage):
    """
    Analyze score performance and provide categorized feedback.
    """
    if score_percentage >= 90:
        return "Excellent performance! You have mastered this chapter."
    elif score_percentage >= 75:
        return "Good performance! You understand most concepts well."
    elif score_percentage >= 60:
        return "Fair performance. Some concepts need more practice."
    else:
        return "Needs improvement. Consider reviewing the chapter content again."


def _get_performance_recommendations(score_percentage):
    """
    Get performance-based recommendations.
    """
    if score_percentage >= 90:
        return [
            "Move to the next chapter",
            "Help other learners in community forums",
            "Try advanced practice exercises",
        ]
    elif score_percentage >= 75:
        return [
            "Review any incorrect answers",
            "Practice similar questions",
            "Move to next chapter when ready",
        ]
    elif score_percentage >= 60:
        return [
            "Review chapter content again",
            "Focus on areas where you made mistakes",
            "Take more practice sessions before moving on",
        ]
    else:
        return [
            "Re-read the chapter content carefully",
            "Ask for help from AI assistant",
            "Take additional practice sessions",
            "Consider reviewing prerequisite chapters",
        ]


# ============================================================================
# PRACTICE HISTORY - Complete tracking endpoints
# ============================================================================


@practice_bp.route("/history", methods=["GET"])
@jwt_required()
def get_practice_history():
    """
    Get complete practice history from UserPracticeSession table.
    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    - practice_type: Filter by type (optional)
    - chapter_id: Filter by chapter (optional)
    """
    try:
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        practice_type = request.args.get("practice_type")
        chapter_id = request.args.get("chapter_id", type=int)

        # Build query
        query = UserPracticeSession.query.filter_by(user_id=user_id)

        if practice_type:
            query = query.filter_by(practice_type=practice_type)
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)

        # Paginate results
        pagination = query.order_by(
            UserPracticeSession.completed_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        history_items = [item.to_dict() for item in pagination.items]

        return (
            jsonify(
                {
                    "success": True,
                    "history": history_items,
                    "pagination": {
                        "total": pagination.total,
                        "page": page,
                        "per_page": per_page,
                        "pages": pagination.pages,
                        "has_next": pagination.has_next,
                        "has_prev": pagination.has_prev,
                    },
                    "message": f"Retrieved {len(history_items)} practice session records",
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving practice history: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to retrieve practice history",
                    "details": str(e),
                }
            ),
            500,
        )


@practice_bp.route("/history/<int:history_id>", methods=["GET"])
@jwt_required()
def get_practice_history_detail(history_id: int):
    """
    Get detailed view of a specific practice session from history.
    """
    try:
        user_id = get_jwt_identity()

        # Get history entry - ensure it belongs to the user
        history_entry = UserPracticeSession.query.filter_by(
            id=history_id, user_id=user_id
        ).first()

        if not history_entry:
            return (
                jsonify(
                    {
                        "error": "Practice session history not found",
                        "telugu_error": "అభ్యాస సెషన్ చరిత్ర కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "session": history_entry.to_dict(),
                    "message": "Practice session details retrieved successfully",
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error retrieving practice session details: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to retrieve practice session details",
                    "details": str(e),
                }
            ),
            500,
        )


@practice_bp.route("/history/stats", methods=["GET"])
@jwt_required()
def get_practice_statistics():
    """
    Get practice statistics for the user.
    Returns: total sessions, average scores, practice types breakdown, progress over time.
    """
    try:
        user_id = get_jwt_identity()

        # Get all practice sessions
        sessions = UserPracticeSession.query.filter_by(user_id=user_id).order_by(
            UserPracticeSession.completed_at.asc()
        ).all()

        if not sessions:
            return (
                jsonify(
                    {
                        "success": True,
                        "stats": {
                            "total_sessions": 0,
                            "message": "No practice sessions completed yet",
                        },
                    }
                ),
                200,
            )

        # Calculate statistics
        total_sessions = len(sessions)
        total_questions = sum(s.total_questions for s in sessions)
        total_correct = sum(s.correct_answers for s in sessions)
        avg_score = sum(s.score for s in sessions) / total_sessions
        
        # Practice types breakdown
        from collections import Counter
        practice_types = Counter(s.practice_type for s in sessions if s.practice_type)
        
        # Chapter breakdown
        chapters = Counter(s.chapter_id for s in sessions if s.chapter_id)
        
        # Total time spent
        total_time_seconds = sum(s.time_spent_seconds or 0 for s in sessions)
        total_time_minutes = total_time_seconds // 60
        
        # Aggregate strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        for session in sessions:
            if session.strengths:
                all_strengths.extend(session.strengths)
            if session.weaknesses:
                all_weaknesses.extend(session.weaknesses)
        
        strength_counts = Counter(all_strengths)
        weakness_counts = Counter(all_weaknesses)
        
        # Calculate improvement (compare first and last 3 sessions)
        if total_sessions >= 6:
            first_three_avg = sum(s.score for s in sessions[:3]) / 3
            last_three_avg = sum(s.score for s in sessions[-3:]) / 3
            improvement = last_three_avg - first_three_avg
        else:
            improvement = 0

        stats = {
            "total_sessions": total_sessions,
            "total_questions_answered": total_questions,
            "total_correct_answers": total_correct,
            "overall_accuracy": round((total_correct / total_questions * 100), 2) if total_questions > 0 else 0,
            "average_score": round(avg_score, 2),
            "improvement": round(improvement, 2) if improvement else 0,
            "total_time_minutes": total_time_minutes,
            "practice_types_breakdown": [
                {"type": practice_type, "count": count}
                for practice_type, count in practice_types.most_common()
            ],
            "chapters_practiced": [
                {"chapter_id": chapter_id, "sessions": count}
                for chapter_id, count in chapters.most_common()
            ],
            "top_strengths": [
                {"skill": skill, "count": count}
                for skill, count in strength_counts.most_common(5)
            ],
            "top_weaknesses": [
                {"skill": skill, "count": count}
                for skill, count in weakness_counts.most_common(5)
            ],
            "practice_timeline": [
                {
                    "date": s.completed_at.isoformat() if s.completed_at else None,
                    "score": s.score,
                    "questions": s.total_questions,
                    "practice_type": s.practice_type,
                }
                for s in sessions
            ],
            "recent_sessions": [
                {
                    "practice_type": s.practice_type,
                    "score": s.score,
                    "questions": s.total_questions,
                    "date": s.completed_at.isoformat() if s.completed_at else None,
                }
                for s in sessions[-5:]  # Last 5 sessions
            ],
        }

        return (
            jsonify(
                {
                    "success": True,
                    "stats": stats,
                    "message": "Practice statistics calculated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        current_app.logger.error(f"Error calculating practice statistics: {str(e)}")
        return (
            jsonify(
                {
                    "error": "Failed to calculate practice statistics",
                    "details": str(e),
                }
            ),
            500,
        )
