from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.activity_service import ActivityService
from app.services.gamification_service import GamificationService
from app.models import db, User, LearningSession
from datetime import datetime

activities_bp = Blueprint("activities", __name__)
activity_service = ActivityService()
gamification_service = GamificationService()


@activities_bp.route("/generate-quiz", methods=["POST"])
@jwt_required()
def generate_quiz():
    """
    Generate a quiz activity based on topic and level.

    Request Body:
        {
            "topic": "daily routine",
            "level": "beginner",
            "num_questions": 5
        }

    Returns:
        Quiz data with questions, options, and metadata
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        topic = data.get("topic", "daily routine")
        level = data.get("level", "beginner")
        num_questions = data.get("num_questions", 5)

        # Validate level
        if level not in ["beginner", "intermediate", "advanced"]:
            return (
                jsonify(
                    {
                        "error": "Invalid level. Must be beginner, intermediate, or advanced."
                    }
                ),
                400,
            )

        # Validate num_questions
        if (
            not isinstance(num_questions, int)
            or num_questions < 1
            or num_questions > 20
        ):
            return jsonify({"error": "num_questions must be between 1 and 20"}), 400

        # Generate quiz
        quiz_data = activity_service.generate_quiz(
            user_id=current_user_id,
            topic=topic,
            level=level,
            num_questions=num_questions,
        )

        # Check for AI generation errors
        if "error" in quiz_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": quiz_data.get("error"),
                        "message": quiz_data.get(
                            "message",
                            "Failed to generate AI content. Please try again.",
                        ),
                    }
                ),
                500,
            )

        # Create learning session
        session = LearningSession(
            user_id=current_user_id,
            activity_type="quiz",
            topic=topic,
            level=level,
            activity_data=quiz_data,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()

        quiz_data["session_id"] = session.id

        return (
            jsonify(
                {
                    "success": True,
                    "data": quiz_data,
                    "message": "Quiz generated successfully using AI!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error generating quiz: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/generate-flashcards", methods=["POST"])
@jwt_required()
def generate_flashcards():
    """
    Generate flashcard activity based on topic and level.

    Request Body:
        {
            "topic": "food",
            "level": "beginner",
            "num_cards": 10
        }

    Returns:
        Flashcard data with English-Telugu pairs
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        topic = data.get("topic", "food")
        level = data.get("level", "beginner")
        num_cards = data.get("num_cards", 10)

        # Validate level
        if level not in ["beginner", "intermediate", "advanced"]:
            return (
                jsonify(
                    {
                        "error": "Invalid level. Must be beginner, intermediate, or advanced."
                    }
                ),
                400,
            )

        # Validate num_cards
        if not isinstance(num_cards, int) or num_cards < 1 or num_cards > 30:
            return jsonify({"error": "num_cards must be between 1 and 30"}), 400

        # Generate flashcards
        flashcard_data = activity_service.generate_flashcards(
            user_id=current_user_id, topic=topic, level=level, num_cards=num_cards
        )

        # Check for AI generation errors
        if "error" in flashcard_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": flashcard_data.get("error"),
                        "message": flashcard_data.get(
                            "message",
                            "Failed to generate AI content. Please try again.",
                        ),
                    }
                ),
                500,
            )

        # Create learning session
        session = LearningSession(
            user_id=current_user_id,
            activity_type="flashcard",
            topic=topic,
            level=level,
            activity_data=flashcard_data,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()

        flashcard_data["session_id"] = session.id

        return (
            jsonify(
                {
                    "success": True,
                    "data": flashcard_data,
                    "message": "Flashcards generated successfully using AI!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error generating flashcards: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/generate-writing-prompt", methods=["POST"])
@jwt_required()
def generate_writing_prompt():
    """
    Generate a writing practice prompt.

    Request Body:
        {
            "topic": "family",
            "level": "beginner"
        }

    Returns:
        Writing prompt with guidelines and example
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        topic = data.get("topic", "family")
        level = data.get("level", "beginner")

        # Validate level
        if level not in ["beginner", "intermediate", "advanced"]:
            return (
                jsonify(
                    {
                        "error": "Invalid level. Must be beginner, intermediate, or advanced."
                    }
                ),
                400,
            )

        # Generate writing prompt
        prompt_data = activity_service.generate_writing_prompt(
            user_id=current_user_id, topic=topic, level=level
        )

        # Check for AI generation errors
        if "error" in prompt_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": prompt_data.get("error"),
                        "message": prompt_data.get(
                            "message",
                            "Failed to generate AI content. Please try again.",
                        ),
                    }
                ),
                500,
            )

        # Create learning session
        session = LearningSession(
            user_id=current_user_id,
            activity_type="writing",
            topic=topic,
            level=level,
            activity_data=prompt_data,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "session_id": session.id,
                    "prompt_data": prompt_data,
                    "message": "Writing prompt generated successfully using AI!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error generating writing prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_activity():
    """
    Submit activity answers for evaluation.

    Request Body:
        {
            "session_id": 123,
            "activity_type": "quiz",
            "activity_data": {...},
            "user_answers": {
                "1": "Option A",
                "2": "Option B",
                ...
            },
            "time_spent_minutes": 5
        }

    Returns:
        Evaluation results with score, feedback, and points earned
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        session_id = data.get("session_id")
        activity_type = data.get("activity_type")
        activity_data = data.get("activity_data")
        user_answers = data.get("user_answers")
        time_spent = data.get("time_spent_minutes", 0)

        if not all([session_id, activity_type, activity_data, user_answers]):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate activity type
        if activity_type not in ["quiz", "flashcard", "writing"]:
            return jsonify({"error": "Invalid activity type"}), 400

        # Add time spent to user answers
        user_answers["time_spent_minutes"] = time_spent

        # Evaluate activity
        evaluation_result = activity_service.evaluate_activity_submission(
            user_id=current_user_id,
            activity_type=activity_type,
            activity_data=activity_data,
            user_answers=user_answers,
        )

        if "error" in evaluation_result:
            return jsonify(evaluation_result), 400

        # Update learning session
        session = LearningSession.query.filter_by(
            id=session_id, user_id=current_user_id
        ).first()

        if session:
            session.completed_at = datetime.utcnow()
            session.status = "completed"
            # For writing, use overall_score; for others use score_percentage
            session.score = evaluation_result.get(
                "overall_score"
            ) or evaluation_result.get("score_percentage", 0)
            session.points_earned = evaluation_result.get("points_earned", 0)
            session.time_spent_minutes = time_spent
            db.session.commit()

            # Award gamification points
            gamification_result = None
            if activity_type == "quiz":
                # Count correct answers
                correct_answers = sum(
                    1
                    for item in evaluation_result.get("details", [])
                    if item.get("is_correct", False)
                )
                gamification_result = gamification_service.award_activity_points(
                    user_id=current_user_id,
                    activity_type="quiz",
                    session_data={"correct_answers": correct_answers},
                )
            elif activity_type == "flashcard":
                # Count cards reviewed
                cards_reviewed = len(evaluation_result.get("flashcards_reviewed", []))
                gamification_result = gamification_service.award_activity_points(
                    user_id=current_user_id,
                    activity_type="flashcard",
                    session_data={"cards_reviewed": cards_reviewed},
                )
            elif activity_type == "writing":
                gamification_result = gamification_service.award_activity_points(
                    user_id=current_user_id, activity_type="writing", session_data={}
                )

        response_data = {"success": True, "evaluation": evaluation_result}

        # Add gamification data if available
        if gamification_result and gamification_result.get("success"):
            response_data["gamification"] = {
                "points_awarded": gamification_result.get("points_awarded", 0),
                "total_points": gamification_result.get("total_points", 0),
                "new_badges": gamification_result.get("new_badges", []),
            }

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting activity: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/topics", methods=["GET"])
@jwt_required()
def get_available_topics():
    """
    Get list of available activity topics.

    Returns:
        List of topics with descriptions
    """
    topics = [
        {
            "id": "daily_routine",
            "name": "Daily Routine",
            "name_telugu": "రోజువారీ దినచర్య",
            "description": "Learn words and phrases for daily activities",
            "icon": "☀️",
        },
        {
            "id": "food",
            "name": "Food & Cooking",
            "name_telugu": "ఆహారం మరియు వంట",
            "description": "Vocabulary for food, meals, and cooking",
            "icon": "🍽️",
        },
        {
            "id": "travel",
            "name": "Travel & Transportation",
            "name_telugu": "ప్రయాణం మరియు రవాణా",
            "description": "Essential phrases for travel and getting around",
            "icon": "✈️",
        },
        {
            "id": "work",
            "name": "Work & Office",
            "name_telugu": "పని మరియు కార్యాలయం",
            "description": "Professional vocabulary and workplace communication",
            "icon": "💼",
        },
        {
            "id": "shopping",
            "name": "Shopping",
            "name_telugu": "షాపింగ్",
            "description": "Shopping vocabulary and asking for items",
            "icon": "🛍️",
        },
        {
            "id": "family",
            "name": "Family & Relationships",
            "name_telugu": "కుటుంబం మరియు సంబంధాలు",
            "description": "Talking about family members and relationships",
            "icon": "👨‍👩‍👧‍👦",
        },
        {
            "id": "health",
            "name": "Health & Wellness",
            "name_telugu": "ఆరోగ్యం మరియు శ్రేయస్సు",
            "description": "Medical vocabulary and health-related phrases",
            "icon": "🏥",
        },
        {
            "id": "hobbies",
            "name": "Hobbies & Interests",
            "name_telugu": "హాబీలు మరియు ఆసక్తులు",
            "description": "Talk about activities you enjoy",
            "icon": "🎨",
        },
    ]

    return jsonify({"success": True, "topics": topics}), 200


@activities_bp.route("/history", methods=["GET"])
@jwt_required()
def get_activity_history():
    """
    Get user's activity history.

    Query Parameters:
        - activity_type: Filter by type (quiz, flashcard)
        - limit: Number of records (default: 10)

    Returns:
        List of completed activities
    """
    try:
        current_user_id = get_jwt_identity()

        # Get query parameters
        activity_type = request.args.get("activity_type")
        limit = int(request.args.get("limit", 10))

        # Build query
        query = LearningSession.query.filter_by(user_id=current_user_id)

        if activity_type:
            query = query.filter_by(activity_type=activity_type)

        # Get recent sessions
        sessions = (
            query.order_by(LearningSession.completed_at.desc()).limit(limit).all()
        )

        history = []
        for session in sessions:
            if session.completed_at:  # Only completed sessions
                history.append(
                    {
                        "id": session.id,
                        "activity_type": session.activity_type,
                        "topic": session.topic,
                        "level": session.level,
                        "score": session.score,
                        "points_earned": session.points_earned,
                        "time_spent_minutes": session.time_spent_minutes,
                        "completed_at": (
                            session.completed_at.isoformat()
                            if session.completed_at
                            else None
                        ),
                    }
                )

        return (
            jsonify({"success": True, "history": history, "total_count": len(history)}),
            200,
        )

    except Exception as e:
        print(f"Error getting activity history: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/generate-role-play", methods=["POST"])
@jwt_required()
def generate_role_play():
    """
    Generate a role-playing conversation scenario.

    Request Body:
        {
            "topic": "restaurant",
            "level": "beginner"
        }

    Returns:
        Scenario data with setting, roles, goal, and initial AI line
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        topic = data.get("topic", "restaurant")
        level = data.get("level", "beginner")

        # Validate level
        if level not in ["beginner", "intermediate", "advanced"]:
            return (
                jsonify(
                    {
                        "error": "Invalid level. Must be beginner, intermediate, or advanced."
                    }
                ),
                400,
            )

        # Generate role-play scenario
        scenario_data = activity_service.generate_role_playing_scenario(
            user_id=current_user_id, topic=topic, level=level
        )

        # Check for AI generation errors
        if "error" in scenario_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": scenario_data.get("error"),
                        "message": scenario_data.get(
                            "message",
                            "Failed to generate AI content. Please try again.",
                        ),
                    }
                ),
                500,
            )

        # Create learning session
        session = LearningSession(
            user_id=current_user_id,
            activity_type="roleplay",
            topic=topic,
            level=level,
            activity_data=scenario_data,
            status="in_progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(session)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "session_id": session.id,
                    "scenario_data": scenario_data,
                    "message": "Role-play scenario generated successfully using AI!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error generating role-play scenario: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/conversation", methods=["POST"])
@jwt_required()
def continue_conversation():
    """
    Continue role-playing conversation with AI response.

    Request Body:
        {
            "session_id": 123,
            "scenario_data": {...},
            "conversation_history": [...],
            "user_message": "I want chicken biryani please"
        }

    Returns:
        AI response with grammar feedback and conversation continuation
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        session_id = data.get("session_id")
        scenario_data = data.get("scenario_data", {})
        conversation_history = data.get("conversation_history", [])
        user_message = data.get("user_message", "").strip()

        if not session_id:
            return jsonify({"error": "session_id is required"}), 400

        if not user_message:
            return jsonify({"error": "user_message cannot be empty"}), 400

        # Verify session belongs to user
        session = LearningSession.query.get(session_id)
        if not session or session.user_id != current_user_id:
            return jsonify({"error": "Invalid session"}), 404

        # Add user message to history
        conversation_history.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Generate AI response
        response_data = activity_service.generate_conversation_response(
            user_id=current_user_id,
            scenario_data=scenario_data,
            conversation_history=conversation_history,
            user_message=user_message,
        )

        # Check for AI generation errors
        if "error" in response_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": response_data.get("error"),
                        "message": response_data.get(
                            "message", "Failed to generate AI response."
                        ),
                    }
                ),
                500,
            )

        # Add AI response to history
        conversation_history.append(
            {
                "role": "ai",
                "content": response_data.get("ai_response", ""),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Update session with conversation history
        session.user_input = conversation_history  # Store full conversation
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "response_data": response_data,
                    "conversation_history": conversation_history,
                    "message": "Response generated successfully!",
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        print(f"Error in conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/complete-roleplay", methods=["POST"])
@jwt_required()
def complete_roleplay():
    """
    Complete role-playing session and get evaluation.

    Request Body:
        {
            "session_id": 123,
            "scenario_data": {...},
            "conversation_history": [...]
        }

    Returns:
        Session evaluation with feedback and points earned
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        session_id = data.get("session_id")
        scenario_data = data.get("scenario_data", {})
        conversation_history = data.get("conversation_history", [])

        if not session_id:
            return jsonify({"error": "session_id is required"}), 400

        # Verify session belongs to user
        session = LearningSession.query.get(session_id)
        if not session or session.user_id != current_user_id:
            return jsonify({"error": "Invalid session"}), 404

        # Calculate time spent
        time_spent = (datetime.utcnow() - session.started_at).total_seconds() / 60

        # Get evaluation from AI
        evaluation = activity_service.complete_role_play_session(
            user_id=current_user_id,
            scenario_data=scenario_data,
            conversation_history=conversation_history,
        )

        # Check for errors
        if "error" in evaluation:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": evaluation.get("error"),
                        "message": evaluation.get(
                            "message", "Failed to evaluate session."
                        ),
                    }
                ),
                500,
            )

        # Update session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.score = evaluation.get("overall_score", 0)
        session.points_earned = evaluation.get("points_earned", 30)
        session.time_spent_minutes = int(time_spent)
        session.ai_feedback = evaluation
        session.user_input = conversation_history

        db.session.commit()

        # Award gamification points
        gamification_result = gamification_service.award_activity_points(
            user_id=current_user_id, activity_type="roleplay", session_data={}
        )

        response_data = {
            "success": True,
            "message": "Role-playing session completed successfully",
            "evaluation": evaluation,
            "time_spent_minutes": int(time_spent),
        }

        # Add gamification data if available
        if gamification_result and gamification_result.get("success"):
            response_data["gamification"] = {
                "points_awarded": gamification_result.get("points_awarded", 0),
                "total_points": gamification_result.get("total_points", 0),
                "new_badges": gamification_result.get("new_badges", []),
            }

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error completing roleplay: {str(e)}")
        return jsonify({"error": str(e)}), 500


@activities_bp.route("/complete-reading", methods=["POST"])
@jwt_required()
def complete_reading():
    """
    Complete reading activity.

    Request Body:
        {
            "session_id": 123,
            "time_spent_minutes": 10
        }

    Returns:
        Completion confirmation with points earned
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate inputs
        session_id = data.get("session_id")
        time_spent = data.get("time_spent_minutes", 0)

        if not session_id:
            return jsonify({"error": "session_id is required"}), 400

        # Verify session belongs to user
        session = LearningSession.query.get(session_id)
        if not session or session.user_id != current_user_id:
            return jsonify({"error": "Invalid session"}), 404

        # Update session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        session.score = 100  # Reading completion counts as 100% completion
        session.points_earned = 20  # Fixed 20 points for reading
        session.time_spent_minutes = int(time_spent)

        db.session.commit()

        # Award gamification points
        gamification_result = gamification_service.award_activity_points(
            user_id=current_user_id, activity_type="reading", session_data={}
        )

        response_data = {
            "success": True,
            "message": "Reading activity completed successfully",
            "telugu_message": "చదవడం కార్యకలాపం విజయవంతంగా పూర్తయింది",
            "time_spent_minutes": int(time_spent),
        }

        # Add gamification data if available
        if gamification_result and gamification_result.get("success"):
            response_data["gamification"] = {
                "points_awarded": gamification_result.get("points_awarded", 0),
                "total_points": gamification_result.get("total_points", 0),
                "new_badges": gamification_result.get("new_badges", []),
            }

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error completing reading: {str(e)}")
        return jsonify({"error": str(e)}), 500
