from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.initial_assessment_service import InitialAssessmentService
from app.models import User, ProficiencyAssessment, UserAssessmentHistory
from app.models import db
from typing import Dict, List
from datetime import datetime
import traceback

assessment_routes = Blueprint("assessment", __name__)
assessment_service = InitialAssessmentService()


@assessment_routes.route("/api/assessment/generate", methods=["POST"])
@jwt_required()
def generate_assessment():
    """
    Generate a new placement assessment for the user.
    Expected JSON body:
    {
        "assessment_type": "comprehensive" | "quick" | "adaptive" | "skill_specific",
        "skill_area": "vocabulary" (required only for skill_specific)
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}

        assessment_type = data.get("assessment_type", "comprehensive")
        skill_area = data.get("skill_area")

        # Validate assessment type
        valid_types = ["comprehensive", "quick", "adaptive", "skill_specific"]
        if assessment_type not in valid_types:
            return (
                jsonify(
                    {
                        "error": f'Invalid assessment type. Must be one of: {", ".join(valid_types)}',
                        "telugu_error": "చెల్లని మూల్యాంకన రకం",
                    }
                ),
                400,
            )

        # Validate skill area for skill-specific assessment
        if assessment_type == "skill_specific":
            if not skill_area:
                return (
                    jsonify(
                        {
                            "error": "skill_area is required for skill_specific assessment",
                            "telugu_error": "నైపుణ్య రంగం అవసరం",
                        }
                    ),
                    400,
                )

            valid_skills = ["vocabulary", "grammar", "reading", "listening", "writing"]
            if skill_area not in valid_skills:
                return (
                    jsonify(
                        {
                            "error": f'Invalid skill area. Must be one of: {", ".join(valid_skills)}',
                            "telugu_error": "చెల్లని నైపుణ్య రంగం",
                        }
                    ),
                    400,
                )

            assessment_data = assessment_service.generate_skill_specific_assessment(
                user_id, skill_area
            )
        else:
            # Use the correct method name: conduct_comprehensive_initial_assessment
            assessment_data = assessment_service.conduct_comprehensive_initial_assessment(
                user_id, assessment_type
            )

        return (
            jsonify(
                {
                    "success": True,
                    "assessment": assessment_data,
                    "message": f"{assessment_type.title()} assessment generated successfully",
                    "telugu_message": f"{assessment_type} మూల్యాంకనం విజయవంతంగా రూపొందించబడింది",
                }
            ),
            200,
        )

    except ValueError as e:
        return (
            jsonify({"error": str(e), "telugu_error": "మూల్యాంకనం రూపొందించడంలో లోపం"}),
            400,
        )
    except Exception as e:
        print(f"Error in assessment generation: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate assessment",
                    "telugu_error": "మూల్యాంకనం రూపొందించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/<int:assessment_id>/regenerate", methods=["POST"])
@jwt_required()
def regenerate_assessment(assessment_id):
    """
    Delete an incomplete assessment and generate a fresh one with unique questions.
    This is useful when an assessment has duplicate questions due to old code.
    """
    try:
        user_id = get_jwt_identity()
        
        # Find the assessment
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return jsonify({
                "error": "Assessment not found or unauthorized",
                "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు"
            }), 404
        
        # Check if it's incomplete
        if assessment.completed_at:
            return jsonify({
                "error": "Cannot regenerate a completed assessment",
                "telugu_error": "పూర్తయిన మూల్యాంకనాన్ని మళ్లీ రూపొందించలేము"
            }), 400
        
        # Store the assessment type
        assessment_type = assessment.assessment_type
        
        # Delete the old assessment
        db.session.delete(assessment)
        db.session.commit()
        
        # Generate a new assessment
        new_assessment_data = assessment_service.conduct_comprehensive_initial_assessment(
            user_id, assessment_type
        )
        
        return jsonify({
            "success": True,
            "message": "Assessment regenerated successfully with unique questions",
            "telugu_message": "ప్రత్యేక ప్రశ్నలతో మూల్యాంకనం మళ్లీ రూపొందించబడింది",
            "assessment": new_assessment_data
        }), 200
        
    except Exception as e:
        print(f"Error regenerating assessment: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": "Failed to regenerate assessment",
            "telugu_error": "మూల్యాంకనం మళ్లీ రూపొందించడంలో వైఫల్యం",
            "details": str(e)
        }), 500


@assessment_routes.route("/api/assessment/<int:assessment_id>/submit", methods=["POST"])
@jwt_required()
def submit_assessment(assessment_id):
    """
    Submit answers for an assessment.
    Expected JSON body:
    {
        "answers": {
            "question_id_1": "A",
            "question_id_2": "B",
            ...
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or "answers" not in data:
            return (
                jsonify(
                    {"error": "Answers are required", "telugu_error": "సమాధానాలు అవసరం"}
                ),
                400,
            )

        answers = data["answers"]

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Assessment not found or unauthorized",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం",
                    }
                ),
                404,
            )

        if not answers:
            return (
                jsonify(
                    {
                        "error": "At least one answer is required",
                        "telugu_error": "కనీసం ఒక సమాధానం అవసరం",
                    }
                ),
                400,
            )

        # Submit and evaluate assessment
        results = assessment_service.submit_assessment_answers(assessment_id, answers)

        return (
            jsonify(
                {
                    "success": True,
                    "assessment_results": results,
                    "message": "Assessment completed successfully",
                    "telugu_message": "మూల్యాంకనం విజయవంతంగా పూర్తయింది",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e), "telugu_error": "మూల్యాంకనం సమర్పణలో లోపం"}), 400
    except Exception as e:
        print(f"Error in assessment submission: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to submit assessment",
                    "telugu_error": "మూల్యాంకనం సమర్పణలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route(
    "/api/assessment/<int:assessment_id>/submit-answer", methods=["POST"]
)
@jwt_required()
def submit_single_answer(assessment_id):
    """
    Submit a single answer for an assessment question (adaptive/step-by-step).
    Expected JSON body:
    {
        "question_id": "q_vocab_beginner_1",
        "answer": "A"
    }
    """
    try:
        user_id = int(get_jwt_identity())  # Convert to int for comparison
        data = request.get_json()

        if not data or "question_id" not in data or "answer" not in data:
            return (
                jsonify(
                    {
                        "error": "question_id and answer are required",
                        "telugu_error": "ప్రశ్న ID మరియు సమాధానం అవసరం",
                    }
                ),
                400,
            )

        question_id = data["question_id"]
        answer = data["answer"]

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            print(f"Assessment {assessment_id} not found in database")
            return (
                jsonify(
                    {
                        "error": "Assessment not found",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు",
                    }
                ),
                404,
            )
        
        if assessment.user_id != user_id:
            print(f"Assessment {assessment_id} belongs to user {assessment.user_id}, but request is from user {user_id}")
            return (
                jsonify(
                    {
                        "error": "Unauthorized - Assessment belongs to different user",
                        "telugu_error": "అనధికృతం - వేరే వినియోగదారుకు చెందిన మూల్యాంకనం",
                    }
                ),
                403,
            )

        # Submit single answer and get next question
        result = assessment_service.submit_single_answer(
            assessment_id, question_id, answer
        )

        return (
            jsonify(
                {
                    "success": True,
                    "result": result,
                    "message": "Answer submitted successfully",
                    "telugu_message": "సమాధానం విజయవంతంగా సమర్పించబడింది",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e), "telugu_error": "సమాధానం సమర్పణలో లోపం"}), 400
    except Exception as e:
        print(f"Error in single answer submission: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to submit answer",
                    "telugu_error": "సమాధానం సమర్పణలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route(
    "/api/assessment/<int:assessment_id>/complete", methods=["POST"]
)
@jwt_required()
def complete_assessment(assessment_id):
    """
    Complete the assessment and update user profile.
    Can be called after all answers are submitted via submit-answer endpoint.
    Expected JSON body (optional):
    {
        "time_spent_seconds": 300
    }
    """
    try:
        user_id = int(get_jwt_identity())  # Convert to int for comparison
        data = request.get_json() or {}

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Assessment not found or unauthorized",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం",
                    }
                ),
                404,
            )

        # Check if already completed - evaluate if needed and return results
        if assessment.completed_at:
            # Assessment was already completed
            # But check if it needs evaluation
            if not assessment.ai_evaluation and assessment.user_responses:
                try:
                    print(f"⚠️ Assessment {assessment_id} was completed but not evaluated - evaluating now...")
                    # Evaluate the assessment now
                    current_responses = assessment.user_responses if assessment.user_responses else {}
                    questions_asked = assessment.questions_asked if assessment.questions_asked else []
                    answers = {qid: resp["answer"] for qid, resp in current_responses.items() if "answer" in resp}
                    
                    if answers and questions_asked:
                        # Call the evaluation service with force_re_evaluate=True
                        eval_results = assessment_service.submit_assessment_answers(assessment_id, answers, force_re_evaluate=True)
                        if eval_results:
                            print(f"✅ Successfully evaluated assessment {assessment_id}")
                except Exception as eval_err:
                    print(f"⚠️ Could not re-evaluate assessment {assessment_id}: {str(eval_err)}")
                    # Continue and return whatever we have
            
            # Return the results (evaluated or not)
            questions_for_scoring = assessment.questions_asked if assessment.questions_asked else []
            max_score = sum(q.get("points", 2) for q in questions_for_scoring) if questions_for_scoring else 1
            formatted_results = {
                "overall_score": assessment.score or 0,
                "max_score": max_score,
                "percentage": (
                    (assessment.score / max_score) * 100 if max_score > 0 else 0
                ),
                "proficiency_level": assessment.proficiency_level or "not_assessed",
                "skill_breakdown": (
                    assessment.ai_evaluation.get("skill_scores", {})
                    if assessment.ai_evaluation
                    else {}
                ),
            }
            
            return (
                jsonify(
                    {
                        "success": True,
                        "results": formatted_results,
                        "message": "Assessment was already completed. Returning results.",
                        "telugu_message": "మూల్యాంకనం ఇప్పటికే పూర్తయింది. ఫలితాలు తిరిగి ఇస్తున్నాం.",
                        "assessment_completed": True,
                    }
                ),
                200,
            )

        # Check if all questions have been answered
        current_responses = (
            assessment.user_responses if assessment.user_responses else {}
        )
        questions = assessment.questions_asked if assessment.questions_asked else []

        if len(current_responses) < len(questions):
            return (
                jsonify(
                    {
                        "error": f"Not all questions answered. {len(current_responses)}/{len(questions)} completed.",
                        "telugu_error": "అన్ని ప్రశ్నలకు సమాధానం ఇవ్వలేదు",
                    }
                ),
                400,
            )

        # Prepare answers dict for evaluation
        answers = {qid: resp["answer"] for qid, resp in current_responses.items()}

        # Submit and evaluate if not already evaluated
        if not assessment.ai_evaluation:
            results = assessment_service.submit_assessment_answers(
                assessment_id, answers, force_re_evaluate=True
            )
        else:
            # Already evaluated, just format the results
            max_score = sum(q.get("points", 2) for q in questions) if questions else 1
            results = {
                "assessment_completed": True,
                "assessment_id": assessment_id,
                "results": {
                    "overall_score": assessment.score or 0,
                    "max_score": max_score,
                    "percentage": (
                        (assessment.score / max_score) * 100 if max_score > 0 else 0
                    ),
                    "proficiency_level": assessment.proficiency_level,
                    "skill_breakdown": (
                        assessment.ai_evaluation.get("skill_scores", {})
                        if assessment.ai_evaluation
                        else {}
                    ),
                },
                "recommendations": assessment.recommendations or [],
                "next_steps": [],
            }

        # Format response for frontend
        formatted_results = {
            "overall_score": results["results"]["percentage"],
            "overall_proficiency_level": results["results"]["proficiency_level"],
            "max_score": results["results"]["max_score"],
            "raw_score": results["results"]["overall_score"],
            "skill_breakdown": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": results.get("recommendations", []),
            "next_steps": results.get("next_steps", []),
        }

        # Format skill breakdown - extract percentage from nested object
        if isinstance(results["results"]["skill_breakdown"], dict):
            for skill, data in results["results"]["skill_breakdown"].items():
                if isinstance(data, dict):
                    formatted_results["skill_breakdown"][skill] = data.get(
                        "percentage", 0
                    )
                    # Identify strengths and weaknesses
                    if data.get("level") == "strong":
                        formatted_results["strengths"].append(skill)
                    elif data.get("level") == "needs_improvement":
                        formatted_results["weaknesses"].append(skill)
                else:
                    formatted_results["skill_breakdown"][skill] = data

        # Update user profile
        user = User.query.get(user_id)
        if user:
            user.proficiency_level = results["results"]["proficiency_level"]
            user.needs_initial_assessment = False
            user.assessment_taken_at = datetime.utcnow()
            user.initial_assessment_id = assessment_id
            user.current_learning_phase = "learning"

            # Also update Profile if exists
            from app.models import Profile

            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                profile.proficiency_level = results["results"]["proficiency_level"]

            db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "results": formatted_results,
                    "message": "Assessment completed successfully! Your profile has been updated.",
                    "telugu_message": "మూల్యాంకనం విజయవంతంగా పూర్తయింది! మీ ప్రొఫైల్ నవీకరించబడింది.",
                }
            ),
            200,
        )

    except ValueError as e:
        return (
            jsonify({"error": str(e), "telugu_error": "మూల్యాంకనం పూర్తి చేయడంలో లోపం"}),
            400,
        )
    except Exception as e:
        print(f"Error in assessment completion: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to complete assessment",
                    "telugu_error": "మూల్యాంకనం పూర్తి చేయడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/<int:assessment_id>/results", methods=["GET"])
@jwt_required()
def get_assessment_results(assessment_id):
    """
    Get results for a completed assessment.
    Can be called at any time after assessment is completed.
    """
    try:
        user_id = int(get_jwt_identity())

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Assessment not found or unauthorized",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం",
                    }
                ),
                404,
            )

        # Check if assessment is completed or has all answers submitted
        user_responses = assessment.user_responses or {}
        questions_asked = assessment.questions_asked or []
        
        # Count answers that match question IDs
        if questions_asked:
            question_ids = {q.get("id") or q.get("question_id") for q in questions_asked}
            answered_ids = [qid for qid in user_responses.keys() if qid in question_ids]
            all_answered = len(answered_ids) >= len(questions_asked)
        else:
            all_answered = False
        
        # Allow results if completed OR if all questions are answered (even if /complete wasn't called)
        if not assessment.completed_at and not all_answered:
            return (
                jsonify(
                    {
                        "error": "Assessment is not completed yet",
                        "telugu_error": "మూల్యాంకనం ఇంకా పూర్తికాలేదు",
                    }
                ),
                400,
            )

        # If all questions answered but not yet evaluated, evaluate now
        if all_answered and not assessment.ai_evaluation:
            try:
                print(f"⚠️ Assessment {assessment_id} has all answers but no evaluation - evaluating now...")
                # Prepare answers for evaluation
                answers = {qid: resp.get("answer") for qid, resp in user_responses.items() if qid in question_ids}
                # Call the evaluation service with force_re_evaluate=True
                eval_result = assessment_service.submit_assessment_answers(assessment_id, answers, force_re_evaluate=True)
                # The service will update the assessment with evaluation results
                assessment = ProficiencyAssessment.query.get(assessment_id)  # Refresh
                print(f"✅ Assessment {assessment_id} evaluated successfully")
            except Exception as e:
                print(f"⚠️ Error evaluating assessment {assessment_id}: {str(e)}")
                # Continue even if evaluation fails - return what we have

        # Format and return results
        max_score = sum(q.get("points", 2) for q in (assessment.questions_asked or [])) if assessment.questions_asked else 1
        
        formatted_results = {
            "overall_score": (
                (assessment.score / max_score) * 100 if max_score > 0 and assessment.score else 0
            ),
            "overall_proficiency_level": assessment.proficiency_level or "not_assessed",
            "max_score": max_score,
            "raw_score": assessment.score or 0,
            "skill_breakdown": {},
            "strengths": [],
            "weaknesses": [],
            "recommendations": assessment.recommendations or [],
            "next_steps": [],
        }

        # Parse skill breakdown if available
        if assessment.ai_evaluation:
            try:
                import json
                if isinstance(assessment.ai_evaluation, str):
                    eval_data = json.loads(assessment.ai_evaluation)
                else:
                    eval_data = assessment.ai_evaluation
                
                skill_scores = eval_data.get("skill_scores", {})
                for skill, data in skill_scores.items():
                    if isinstance(data, dict):
                        formatted_results["skill_breakdown"][skill] = data.get("percentage", 0)
                        if data.get("level") == "strong":
                            formatted_results["strengths"].append(skill)
                        elif data.get("level") == "needs_improvement":
                            formatted_results["weaknesses"].append(skill)
                    else:
                        formatted_results["skill_breakdown"][skill] = data
            except Exception as e:
                print(f"Error parsing evaluation data: {str(e)}")

        return (
            jsonify(
                {
                    "success": True,
                    "results": formatted_results,
                    "assessment_id": assessment_id,
                    "message": "Assessment results retrieved successfully",
                    "telugu_message": "మూల్యాంకన ఫలితాలు విజయవంతంగా వెలికితీయబడ్డాయి",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in get_assessment_results: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to retrieve assessment results",
                    "telugu_error": "మూల్యాంకన ఫలితాలను వెలికితీయడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/history", methods=["GET"])
@jwt_required()
def get_assessment_history():
    """
    Get assessment history for the current user.
    """
    try:
        user_id = get_jwt_identity()

        history = assessment_service.get_assessment_history(user_id)

        return (
            jsonify(
                {
                    "success": True,
                    "assessment_history": history,
                    "total_assessments": len(history),
                    "message": f"Retrieved {len(history)} assessment records",
                    "telugu_message": f"{len(history)} మూల్యాంకన రికార్డులు వెలికితీయబడ్డాయి",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in assessment history: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to retrieve assessment history",
                    "telugu_error": "మూల్యాంకన చరిత్రను వెలికితీయడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/<int:assessment_id>/details", methods=["GET"])
@jwt_required()
def get_assessment_details(assessment_id):
    """
    Get detailed information about a specific assessment.
    """
    try:
        user_id = get_jwt_identity()

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            return (
                jsonify(
                    {
                        "error": "Assessment not found",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        if assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Unauthorized access to assessment",
                        "telugu_error": "మూల్యాంకనానికి అనధికృత ప్రవేశం",
                    }
                ),
                403,
            )

        # Build assessment details
        assessment_details = {
            "assessment_id": assessment.id,
            "assessment_type": assessment.assessment_type,
            "status": assessment.status,
            "started_at": (
                assessment.started_at.isoformat() if assessment.started_at else None
            ),
            "completed_at": (
                assessment.completed_at.isoformat() if assessment.completed_at else None
            ),
            "proficiency_level": assessment.proficiency_level,
            "score": assessment.score,
            "max_score": assessment.max_score,
        }

        # Add detailed results if assessment is completed
        if assessment.status == "completed" and assessment.evaluation_results:
            import json

            evaluation_results = json.loads(assessment.evaluation_results)
            skill_breakdown = (
                json.loads(assessment.skill_breakdown)
                if assessment.skill_breakdown
                else {}
            )

            assessment_details.update(
                {
                    "percentage": (
                        (assessment.score / assessment.max_score * 100)
                        if assessment.max_score > 0
                        else 0
                    ),
                    "skill_breakdown": skill_breakdown,
                    "evaluation_summary": {
                        "total_questions": len(
                            evaluation_results.get("question_results", [])
                        ),
                        "correct_answers": len(
                            [
                                q
                                for q in evaluation_results.get("question_results", [])
                                if q.get("correct")
                            ]
                        ),
                        "skill_performance": evaluation_results.get("skill_scores", {}),
                        "level_performance": evaluation_results.get("level_scores", {}),
                    },
                }
            )

        # Add questions if assessment is in progress
        elif assessment.status == "in_progress" and assessment.questions_data:
            import json

            questions = json.loads(assessment.questions_data)
            assessment_details["questions"] = questions

        return (
            jsonify(
                {
                    "success": True,
                    "assessment_details": assessment_details,
                    "message": "Assessment details retrieved successfully",
                    "telugu_message": "మూల్యాంకన వివరాలు విజయవంతంగా వెలికితీయబడ్డాయి",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in assessment details: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to retrieve assessment details",
                    "telugu_error": "మూల్యాంకన వివరాలను వెలికితీయడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/<int:assessment_id>/report", methods=["GET"])
@jwt_required()
def get_assessment_report(assessment_id):
    """
    Get comprehensive assessment report.
    """
    try:
        user_id = get_jwt_identity()

        # Verify assessment belongs to current user and is completed
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment:
            return (
                jsonify(
                    {
                        "error": "Assessment not found",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        if assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Unauthorized access to assessment",
                        "telugu_error": "మూల్యాంకనానికి అనధికృత ప్రవేశం",
                    }
                ),
                403,
            )

        if assessment.status != "completed":
            return (
                jsonify(
                    {
                        "error": "Assessment is not completed yet",
                        "telugu_error": "మూల్యాంకనం ఇంకా పూర్తికాలేదు",
                    }
                ),
                400,
            )

        # Generate comprehensive report
        import json

        evaluation_results = json.loads(assessment.evaluation_results)
        skill_breakdown = (
            json.loads(assessment.skill_breakdown) if assessment.skill_breakdown else {}
        )

        # Create proficiency analysis from stored data
        proficiency_analysis = {
            "overall_level": assessment.proficiency_level,
            "overall_percentage": (
                (assessment.score / assessment.max_score * 100)
                if assessment.max_score > 0
                else 0
            ),
            "skill_breakdown": skill_breakdown,
            "strengths": [
                skill
                for skill, data in skill_breakdown.items()
                if data.get("level") == "strong"
            ],
            "weaknesses": [
                skill
                for skill, data in skill_breakdown.items()
                if data.get("level") == "needs_improvement"
            ],
        }

        # Generate learning path recommendations
        learning_path_recommendations = assessment_service._recommend_learning_paths(
            proficiency_analysis
        )

        # Generate comprehensive report
        report = assessment_service._generate_assessment_report(
            assessment,
            evaluation_results,
            proficiency_analysis,
            learning_path_recommendations,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "assessment_report": report,
                    "message": "Assessment report generated successfully",
                    "telugu_message": "మూల్యాంకన నివేదిక విజయవంతంగా రూపొందించబడింది",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in assessment report: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate assessment report",
                    "telugu_error": "మూల్యాంకన నివేదిక రూపొందించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/<int:assessment_id>/retake", methods=["POST"])
@jwt_required()
def retake_assessment(assessment_id):
    """
    Generate a retake assessment based on previous performance.
    """
    try:
        user_id = get_jwt_identity()

        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return (
                jsonify(
                    {
                        "error": "Assessment not found or unauthorized",
                        "telugu_error": "మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం",
                    }
                ),
                404,
            )

        # Generate retake assessment
        retake_data = assessment_service.retake_assessment(user_id, assessment_id)

        return (
            jsonify(
                {
                    "success": True,
                    "retake_assessment": retake_data,
                    "message": "Retake assessment generated successfully",
                    "telugu_message": "మళ్లీ చేయు మూల్యాంకనం విజయవంతంగా రూపొందించబడింది",
                    "note": "This assessment is adapted based on your previous performance",
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e), "telugu_error": "మళ్లీ చేయు మూల్యాంకనంలో లోపం"}), 400
    except Exception as e:
        print(f"Error in retake assessment: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate retake assessment",
                    "telugu_error": "మళ్లీ చేయు మూల్యాంకనం రూపొందించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/placement-recommendations", methods=["GET"])
@jwt_required()
def get_placement_recommendations():
    """
    Get learning path placement recommendations based on latest assessment.
    """
    try:
        user_id = get_jwt_identity()

        # Get user's latest completed assessment
        latest_assessment = (
            ProficiencyAssessment.query.filter_by(user_id=user_id, status="completed")
            .order_by(ProficiencyAssessment.completed_at.desc())
            .first()
        )

        if not latest_assessment:
            return (
                jsonify(
                    {
                        "error": "No completed assessment found. Please take an assessment first.",
                        "telugu_error": "పూర్తయిన మూల్యాంకనం కనుగొనబడలేదు. దయచేసి మొదట మూల్యాంకనం చేయండి",
                        "suggestion": "Take a placement assessment to get personalized recommendations",
                    }
                ),
                404,
            )

        # Generate recommendations based on latest assessment
        import json

        skill_breakdown = (
            json.loads(latest_assessment.skill_breakdown)
            if latest_assessment.skill_breakdown
            else {}
        )

        proficiency_analysis = {
            "overall_level": latest_assessment.proficiency_level,
            "overall_percentage": (
                (latest_assessment.score / latest_assessment.max_score * 100)
                if latest_assessment.max_score > 0
                else 0
            ),
            "skill_breakdown": skill_breakdown,
            "strengths": [
                skill
                for skill, data in skill_breakdown.items()
                if data.get("level") == "strong"
            ],
            "weaknesses": [
                skill
                for skill, data in skill_breakdown.items()
                if data.get("level") == "needs_improvement"
            ],
        }

        learning_path_recommendations = assessment_service._recommend_learning_paths(
            proficiency_analysis
        )
        next_steps = assessment_service._generate_next_steps(
            proficiency_analysis, learning_path_recommendations
        )

        return (
            jsonify(
                {
                    "success": True,
                    "placement_recommendations": {
                        "based_on_assessment": {
                            "assessment_id": latest_assessment.id,
                            "assessment_date": latest_assessment.completed_at.isoformat(),
                            "proficiency_level": latest_assessment.proficiency_level,
                            "overall_score": f"{latest_assessment.score}/{latest_assessment.max_score}",
                        },
                        "proficiency_summary": proficiency_analysis,
                        "learning_path_recommendations": learning_path_recommendations,
                        "immediate_next_steps": next_steps,
                    },
                    "telugu_summary": assessment_service._generate_telugu_report_summary(
                        proficiency_analysis
                    ),
                    "recommendation_confidence": (
                        "high" if latest_assessment.max_score > 20 else "medium"
                    ),
                    "validity_period": "4-6 weeks",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in placement recommendations: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate placement recommendations",
                    "telugu_error": "ప్లేస్‌మెంట్ సిఫార్సులు రూపొందించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/quick-check", methods=["POST"])
@jwt_required()
def quick_proficiency_check():
    """
    Generate and immediately evaluate a quick proficiency check (5 questions).
    Expected JSON body:
    {
        "skill_area": "vocabulary" (optional - defaults to mixed)
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        skill_area = data.get("skill_area", "mixed")

        # Generate quick assessment questions
        if skill_area == "mixed":
            # Mix of vocabulary and grammar for quick check
            quick_questions = []
            for skill in ["vocabulary", "grammar"]:
                questions = assessment_service._generate_skill_level_questions(
                    skill, "intermediate", 2
                )
                quick_questions.extend(questions)
            questions = quick_questions[:5]  # Limit to 5 questions
        else:
            valid_skills = ["vocabulary", "grammar", "reading", "writing"]
            if skill_area not in valid_skills:
                return (
                    jsonify(
                        {
                            "error": f'Invalid skill area for quick check. Must be one of: {", ".join(valid_skills)} or "mixed"',
                            "telugu_error": "త్వరిత తనిఖీ కోసం చెల్లని నైపుణ్య రంగం",
                        }
                    ),
                    400,
                )

            questions = assessment_service._generate_skill_level_questions(
                skill_area, "intermediate", 5
            )

        # Create temporary assessment for quick check
        max_score = sum(q["points"] for q in questions)

        return (
            jsonify(
                {
                    "success": True,
                    "quick_check": {
                        "questions": questions,
                        "metadata": {
                            "total_questions": len(questions),
                            "max_score": max_score,
                            "skill_focus": skill_area,
                            "estimated_duration": "5-8 minutes",
                            "purpose": "Quick proficiency verification",
                        },
                        "instructions": {
                            "english": "Answer these 5 questions to get a quick assessment of your current level.",
                            "telugu": "మీ ప్రస్తుత స్థాయి యొక్క త్వరిత మూల్యాంకనం పొందడానికి ఈ 5 ప్రశ్నలకు సమాధానం ఇవ్వండి।",
                        },
                    },
                    "message": "Quick proficiency check generated",
                    "telugu_message": "త్వరిత ప్రావీణ్య తనిఖీ రూపొందించబడింది",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in quick proficiency check: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to generate quick proficiency check",
                    "telugu_error": "త్వరిత ప్రావీణ్య తనిఖీ రూపొందించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/validate-answers", methods=["POST"])
@jwt_required()
def validate_quick_answers():
    """
    Validate answers for quick proficiency check without storing results.
    Expected JSON body:
    {
        "questions": [...], // Original questions
        "answers": {
            "question_id_1": "A",
            "question_id_2": "B",
            ...
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or "questions" not in data or "answers" not in data:
            return (
                jsonify(
                    {
                        "error": "Questions and answers are required",
                        "telugu_error": "ప్రశ్నలు మరియు సమాధానాలు అవసరం",
                    }
                ),
                400,
            )

        questions = data["questions"]
        answers = data["answers"]

        # Evaluate answers
        evaluation_result = assessment_service._evaluate_assessment_answers(
            questions, answers
        )

        # Generate quick proficiency analysis
        total_percentage = (
            evaluation_result["total_score"] / evaluation_result["max_possible_score"]
        ) * 100

        if total_percentage >= 80:
            level_estimate = "advanced"
            level_telugu = "ఉన్నత"
            message = "Excellent performance! You demonstrate advanced English skills."
            telugu_message = "అద్భుతమైన పనితీరు! మీరు ఉన్నత ఇంగ్లీష్ నైపుణ్యాలను ప్రదర్శిస్తున్నారు."
        elif total_percentage >= 60:
            level_estimate = "intermediate"
            level_telugu = "మధ్యస్థ"
            message = "Good performance! You have solid intermediate English skills."
            telugu_message = "మంచి పనితీరు! మీకు దృఢమైన మధ్యస్థ ఇంగ్లీష్ నైపుణ్యాలు ఉన్నాయి."
        else:
            level_estimate = "beginner"
            level_telugu = "ప్రాథమిక"
            message = "Keep practicing! Focus on building fundamental English skills."
            telugu_message = (
                "అభ్యాసం కొనసాగించండి! ప్రాథమిక ఇంగ్లీష్ నైపుణ్యాలను అభివృద్ధి చేయడంపై దృష్టి పెట్టండి."
            )

        return (
            jsonify(
                {
                    "success": True,
                    "quick_assessment_results": {
                        "score": f"{evaluation_result['total_score']}/{evaluation_result['max_possible_score']}",
                        "percentage": round(total_percentage, 1),
                        "estimated_level": level_estimate,
                        "estimated_level_telugu": level_telugu,
                        "correct_answers": len(
                            [
                                q
                                for q in evaluation_result["question_results"]
                                if q["correct"]
                            ]
                        ),
                        "total_questions": len(evaluation_result["question_results"]),
                        "question_breakdown": evaluation_result["question_results"],
                    },
                    "recommendations": {
                        "message": message,
                        "telugu_message": telugu_message,
                        "suggested_action": "Take a comprehensive assessment for detailed analysis and personalized learning path",
                        "telugu_suggested_action": "వివరణాత్మక విశ్లేషణ మరియు వ్యక్తిగతీకరించిన అభ్యాస మార్గం కోసం సమగ్ర మూల్యాంకనం చేయండి",
                    },
                    "note": "This is a quick check only. For accurate placement, take a comprehensive assessment.",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in validating quick answers: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to validate answers",
                    "telugu_error": "సమాధానాలను ధృవీకరించడంలో వైఫల్యం",
                    "details": str(e),
                }
            ),
            500,
        )


# Health check for assessment service
@assessment_routes.route("/api/assessment/health", methods=["GET"])
def assessment_health_check():
    """Health check for assessment service."""
    try:
        # Test basic functionality
        test_result = assessment_service._generate_skill_level_questions(
            "vocabulary", "beginner", 1
        )

        return (
            jsonify(
                {
                    "status": "healthy",
                    "service": "Initial Assessment Service",
                    "capabilities": [
                        "Comprehensive placement assessment",
                        "Quick proficiency check",
                        "Adaptive assessment",
                        "Skill-specific assessment",
                        "Assessment history tracking",
                        "Learning path recommendations",
                    ],
                    "test_generation": "success" if test_result else "limited",
                    "telugu_support": True,
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "degraded",
                    "error": str(e),
                    "note": "Assessment service may have limited functionality",
                }
            ),
            200,
        )


# ============================================================================
# USER ASSESSMENT HISTORY - Complete tracking endpoints
# ============================================================================


@assessment_routes.route("/api/assessment/history/detailed", methods=["GET"])
@jwt_required()
def get_detailed_assessment_history():
    """
    Get detailed assessment history from UserAssessmentHistory table.
    Query params:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10)
    - assessment_type: Filter by type (optional)
    """
    try:
        user_id = get_jwt_identity()
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        assessment_type = request.args.get("assessment_type")

        # Build query
        query = UserAssessmentHistory.query.filter_by(user_id=user_id)

        if assessment_type:
            query = query.filter_by(assessment_type=assessment_type)

        # Paginate results
        pagination = query.order_by(
            UserAssessmentHistory.completed_at.desc()
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
                    "message": f"Retrieved {len(history_items)} assessment records",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in detailed assessment history: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to retrieve detailed assessment history",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/history/detailed/<int:history_id>", methods=["GET"])
@jwt_required()
def get_assessment_history_detail(history_id: int):
    """
    Get detailed view of a specific assessment from history.
    Includes full questions, answers, AI feedback, and recommendations.
    """
    try:
        user_id = get_jwt_identity()

        # Get history entry - ensure it belongs to the user
        history_entry = UserAssessmentHistory.query.filter_by(
            id=history_id, user_id=user_id
        ).first()

        if not history_entry:
            return (
                jsonify(
                    {
                        "error": "Assessment history not found",
                        "telugu_error": "మూల్యాంకన చరిత్ర కనుగొనబడలేదు",
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "success": True,
                    "assessment": history_entry.to_dict(),
                    "message": "Assessment details retrieved successfully",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in assessment detail: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to retrieve assessment details",
                    "details": str(e),
                }
            ),
            500,
        )


@assessment_routes.route("/api/assessment/history/stats", methods=["GET"])
@jwt_required()
def get_assessment_statistics():
    """
    Get assessment statistics for the user.
    Returns: average scores, progress over time, skill improvements, etc.
    """
    try:
        user_id = get_jwt_identity()

        # Get all assessments
        assessments = UserAssessmentHistory.query.filter_by(user_id=user_id).order_by(
            UserAssessmentHistory.completed_at.asc()
        ).all()

        if not assessments:
            return (
                jsonify(
                    {
                        "success": True,
                        "stats": {
                            "total_assessments": 0,
                            "message": "No assessments completed yet",
                        },
                    }
                ),
                200,
            )

        # Calculate statistics
        total_assessments = len(assessments)
        avg_score = sum(a.score for a in assessments) / total_assessments
        
        # Get latest proficiency level
        latest_level = assessments[-1].proficiency_level

        # Calculate improvement (compare first and last assessment scores)
        if total_assessments > 1:
            first_score = assessments[0].score
            last_score = assessments[-1].score
            improvement = last_score - first_score
        else:
            improvement = 0

        # Aggregate skill breakdown from all assessments
        all_skills = {}
        for assessment in assessments:
            if assessment.skill_breakdown:
                for skill, score in assessment.skill_breakdown.items():
                    if skill not in all_skills:
                        all_skills[skill] = []
                    all_skills[skill].append(score)

        # Calculate average for each skill
        skill_averages = {
            skill: sum(scores) / len(scores) for skill, scores in all_skills.items()
        }

        # Compile common strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        for assessment in assessments:
            if assessment.strengths:
                all_strengths.extend(assessment.strengths)
            if assessment.weaknesses:
                all_weaknesses.extend(assessment.weaknesses)

        # Get most common items
        from collections import Counter
        strength_counts = Counter(all_strengths)
        weakness_counts = Counter(all_weaknesses)

        stats = {
            "total_assessments": total_assessments,
            "average_score": round(avg_score, 2),
            "latest_proficiency_level": latest_level,
            "improvement": round(improvement, 2),
            "skill_averages": {
                skill: round(avg, 2) for skill, avg in skill_averages.items()
            },
            "top_strengths": [
                {"skill": skill, "count": count}
                for skill, count in strength_counts.most_common(5)
            ],
            "top_weaknesses": [
                {"skill": skill, "count": count}
                for skill, count in weakness_counts.most_common(5)
            ],
            "assessment_timeline": [
                {
                    "date": a.completed_at.isoformat() if a.completed_at else None,
                    "score": a.score,
                    "level": a.proficiency_level,
                    "type": a.assessment_type,
                }
                for a in assessments
            ],
        }

        return (
            jsonify(
                {
                    "success": True,
                    "stats": stats,
                    "message": "Assessment statistics calculated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in assessment statistics: {str(e)}")
        traceback.print_exc()
        return (
            jsonify(
                {
                    "error": "Failed to calculate assessment statistics",
                    "details": str(e),
                }
            ),
            500,
        )
