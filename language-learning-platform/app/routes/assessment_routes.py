"""
Assessment API Routes

Provides comprehensive RESTful API for intelligent assessment system with IRT-based
adaptive testing, skill diagnostics, and analytics.

Endpoints:
- Assessment management (CRUD)
- Question management
- Taking assessments (adaptive & fixed)
- Results and diagnostics
- Analytics and comparisons
- Recommendations

Author: AI Learning Platform
Date: October 20, 2025
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from typing import Dict, List, Optional

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
from app.services.intelligent_assessment_service import IntelligentAssessmentEngine

# Create blueprint
assessment_bp = Blueprint('intelligent_assessment', __name__)

# Initialize service
assessment_engine = IntelligentAssessmentEngine()


# ================================================================
# ASSESSMENT MANAGEMENT
# ================================================================

@assessment_bp.route('/assessments/create', methods=['POST'])
@jwt_required()
def create_assessment():
    """
    Create a new assessment template.
    
    Body:
    {
        "title": "Telugu Proficiency Test",
        "description": "Comprehensive assessment...",
        "assessment_type": "placement",  // placement, progress, mastery, certification
        "target_language": "Telugu",
        "proficiency_level": "intermediate",  // optional
        "skill_areas": ["grammar", "vocabulary", "reading"],  // optional
        "is_adaptive": true,
        "duration_minutes": 60,  // optional
        "passing_score": 70.0,  // optional
        "certification_name": "Telugu Advanced Certificate",  // optional for certification type
        "irt_config": {  // optional
            "se_threshold": 0.3,
            "min_questions": 10,
            "max_questions": 40
        }
    }
    
    Returns:
    {
        "success": true,
        "assessment": {...},
        "message": "Assessment created successfully"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required = ['title', 'description', 'assessment_type']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate assessment type
        valid_types = ['placement', 'progress', 'mastery', 'certification']
        if data['assessment_type'] not in valid_types:
            return jsonify({
                'success': False,
                'error': f'Invalid assessment type. Must be one of: {valid_types}'
            }), 400
        
        # Create assessment
        assessment = assessment_engine.create_assessment(
            title=data['title'],
            description=data['description'],
            assessment_type=data['assessment_type'],
            target_language=data.get('target_language', 'Telugu'),
            proficiency_level=data.get('proficiency_level'),
            skill_areas=data.get('skill_areas'),
            is_adaptive=data.get('is_adaptive', True),
            duration_minutes=data.get('duration_minutes'),
            passing_score=data.get('passing_score'),
            certification_name=data.get('certification_name'),
            irt_config=data.get('irt_config'),
            created_by=user_id
        )
        
        return jsonify({
            'success': True,
            'assessment': assessment.to_dict(),
            'message': 'Assessment created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments', methods=['GET'])
@jwt_required()
def list_assessments():
    """
    List available assessments with optional filtering.
    
    Query params:
    - assessment_type: Filter by type
    - target_language: Filter by language
    - proficiency_level: Filter by level
    - is_active: Filter by active status (default: true)
    
    Returns:
    {
        "success": true,
        "assessments": [...],
        "total": 10
    }
    """
    try:
        # Build query
        query = Assessment.query
        
        # Apply filters
        assessment_type = request.args.get('assessment_type')
        if assessment_type:
            query = query.filter_by(assessment_type=assessment_type)
        
        target_language = request.args.get('target_language')
        if target_language:
            query = query.filter_by(target_language=target_language)
        
        proficiency_level = request.args.get('proficiency_level')
        if proficiency_level:
            query = query.filter_by(proficiency_level=proficiency_level)
        
        is_active = request.args.get('is_active', 'true').lower() == 'true'
        query = query.filter_by(is_active=is_active)
        
        # Execute query
        assessments = query.order_by(Assessment.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'assessments': [a.to_dict() for a in assessments],
            'total': len(assessments)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/<int:assessment_id>', methods=['GET'])
@jwt_required()
def get_assessment(assessment_id):
    """
    Get detailed information about a specific assessment.
    
    Returns:
    {
        "success": true,
        "assessment": {...},
        "question_count": 25,
        "avg_completion_time": 35.5,
        "total_attempts": 150
    }
    """
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        # Get statistics
        question_count = AssessmentQuestion.query.filter_by(
            assessment_id=assessment_id,
            is_active=True
        ).count()
        
        attempts = UserAssessmentAttempt.query.filter_by(
            assessment_id=assessment_id,
            status='completed'
        ).all()
        
        avg_completion_time = None
        if attempts:
            completion_times = [
                (a.completed_at - a.started_at).total_seconds() / 60
                for a in attempts if a.completed_at
            ]
            if completion_times:
                avg_completion_time = sum(completion_times) / len(completion_times)
        
        return jsonify({
            'success': True,
            'assessment': assessment.to_dict(),
            'question_count': question_count,
            'avg_completion_time': avg_completion_time,
            'total_attempts': len(attempts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/<int:assessment_id>', methods=['PUT'])
@jwt_required()
def update_assessment(assessment_id):
    """
    Update an assessment template.
    
    Body: (all fields optional)
    {
        "title": "Updated Title",
        "description": "Updated description",
        "is_adaptive": false,
        "duration_minutes": 45,
        "passing_score": 75.0,
        ...
    }
    """
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'is_adaptive', 'duration_minutes',
            'passing_score', 'certification_name', 'irt_config', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(assessment, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'assessment': assessment.to_dict(),
            'message': 'Assessment updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/<int:assessment_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment(assessment_id):
    """
    Soft delete an assessment (mark as inactive).
    """
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        assessment.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assessment deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# QUESTION MANAGEMENT
# ================================================================

@assessment_bp.route('/assessments/<int:assessment_id>/questions', methods=['POST'])
@jwt_required()
def add_question(assessment_id):
    """
    Add a question to an assessment.
    
    Body:
    {
        "question_text": "What is the Telugu word for 'hello'?",
        "question_type": "multiple_choice",
        "correct_answer": "నమస్కారం",
        "options": ["నమస్కారం", "ధన్యవాదాలు", "మళ్లీ కలుద్దాం"],
        "skill_area": "vocabulary",
        "sub_skills": ["greetings", "basic_words"],
        "difficulty_level": "beginner",
        "irt_params": {  // optional
            "discrimination": 1.2,
            "difficulty": -0.5,
            "guessing": 0.25
        },
        "explanation": "నమస్కారం is the formal greeting...",
        "context": "Used in formal situations..."
    }
    """
    try:
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        required = ['question_text', 'question_type', 'correct_answer']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add question
        question = assessment_engine.add_question_to_assessment(
            assessment_id=assessment_id,
            question_text=data['question_text'],
            question_type=data['question_type'],
            correct_answer=data['correct_answer'],
            options=data.get('options'),
            skill_area=data.get('skill_area'),
            sub_skills=data.get('sub_skills'),
            difficulty_level=data.get('difficulty_level'),
            irt_params=data.get('irt_params'),
            explanation=data.get('explanation'),
            context=data.get('context')
        )
        
        return jsonify({
            'success': True,
            'question': question.to_dict(),
            'message': 'Question added successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/questions/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question(question_id):
    """
    Get question details (with correct answer - admin only view).
    """
    try:
        question = AssessmentQuestion.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
        
        return jsonify({
            'success': True,
            'question': question.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
def update_question(question_id):
    """
    Update a question.
    """
    try:
        question = AssessmentQuestion.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'question_text', 'question_type', 'correct_answer', 'options',
            'skill_area', 'sub_skills', 'difficulty_level', 'explanation',
            'context', 'is_active', 'irt_discrimination', 'irt_difficulty',
            'irt_guessing', 'order_index'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(question, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'question': question.to_dict(),
            'message': 'Question updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    """
    Soft delete a question.
    """
    try:
        question = AssessmentQuestion.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
        
        question.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/questions/bulk-import', methods=['POST'])
@jwt_required()
def bulk_import_questions():
    """
    Import multiple questions at once.
    
    Body:
    {
        "assessment_id": 1,
        "questions": [
            {
                "question_text": "...",
                "question_type": "...",
                ...
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if 'assessment_id' not in data or 'questions' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing assessment_id or questions'
            }), 400
        
        assessment_id = data['assessment_id']
        questions_data = data['questions']
        
        # Verify assessment exists
        assessment = Assessment.query.get(assessment_id)
        if not assessment:
            return jsonify({
                'success': False,
                'error': 'Assessment not found'
            }), 404
        
        # Import questions
        created_questions = []
        errors = []
        
        for idx, q_data in enumerate(questions_data):
            try:
                question = assessment_engine.add_question_to_assessment(
                    assessment_id=assessment_id,
                    question_text=q_data['question_text'],
                    question_type=q_data['question_type'],
                    correct_answer=q_data['correct_answer'],
                    options=q_data.get('options'),
                    skill_area=q_data.get('skill_area'),
                    sub_skills=q_data.get('sub_skills'),
                    difficulty_level=q_data.get('difficulty_level'),
                    irt_params=q_data.get('irt_params'),
                    explanation=q_data.get('explanation'),
                    context=q_data.get('context')
                )
                created_questions.append(question.to_dict())
            except Exception as e:
                errors.append({
                    'index': idx,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'created_count': len(created_questions),
            'error_count': len(errors),
            'questions': created_questions,
            'errors': errors
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# TAKING ASSESSMENTS
# ================================================================

@assessment_bp.route('/assessments/<int:assessment_id>/start', methods=['POST'])
@jwt_required()
def start_assessment(assessment_id):
    """
    Start a new assessment attempt.
    
    Body (optional):
    {
        "initial_theta": 0.5  // Optional initial ability estimate
    }
    
    Returns:
    {
        "success": true,
        "attempt_id": 123,
        "is_adaptive": true,
        "first_question": {...}
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Check if assessment exists
        assessment = Assessment.query.get(assessment_id)
        if not assessment or not assessment.is_active:
            return jsonify({
                'success': False,
                'error': 'Assessment not found or inactive'
            }), 404
        
        # Get initial theta if provided
        data = request.get_json() or {}
        initial_theta = data.get('initial_theta')
        
        # Start assessment
        attempt, adaptive_session = assessment_engine.start_assessment(
            user_id=user_id,
            assessment_id=assessment_id,
            initial_theta=initial_theta
        )
        
        # Get first question
        first_question = assessment_engine.get_next_question_for_attempt(attempt.id)
        
        return jsonify({
            'success': True,
            'attempt_id': attempt.id,
            'is_adaptive': assessment.is_adaptive,
            'duration_minutes': assessment.duration_minutes,
            'first_question': first_question,
            'current_theta': attempt.current_theta_estimate,
            'message': 'Assessment started successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/next-question', methods=['GET'])
@jwt_required()
def get_next_question(attempt_id):
    """
    Get the next question for an ongoing assessment.
    
    Returns:
    {
        "success": true,
        "question": {...},
        "progress": {
            "questions_answered": 5,
            "current_theta": 0.8,
            "theta_se": 0.4
        }
    }
    or
    {
        "success": true,
        "completed": true,
        "message": "Assessment complete"
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify attempt belongs to user
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        # Get next question
        next_question = assessment_engine.get_next_question_for_attempt(attempt_id)
        
        if not next_question:
            # Assessment is complete
            return jsonify({
                'success': True,
                'completed': True,
                'message': 'Assessment complete. Please submit to see results.'
            }), 200
        
        # Return question with progress
        return jsonify({
            'success': True,
            'question': next_question,
            'progress': {
                'questions_answered': attempt.questions_answered,
                'current_theta': attempt.current_theta_estimate,
                'theta_se': attempt.theta_standard_error,
                'correct_count': attempt.correct_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
def submit_response(attempt_id):
    """
    Submit a response to a question.
    
    Body:
    {
        "question_id": 42,
        "user_answer": "నమస్కారం",
        "time_spent_seconds": 25,
        "hints_used": []
    }
    
    Returns:
    {
        "success": true,
        "is_correct": true,
        "explanation": "...",
        "updated_theta": 0.9,
        "theta_se": 0.35,
        "questions_answered": 6
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify attempt
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        if attempt.status != 'in_progress':
            return jsonify({
                'success': False,
                'error': 'Assessment is not in progress'
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'question_id' not in data or 'user_answer' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing question_id or user_answer'
            }), 400
        
        # Submit response
        feedback = assessment_engine.submit_response(
            attempt_id=attempt_id,
            question_id=data['question_id'],
            user_answer=data['user_answer'],
            time_spent_seconds=data.get('time_spent_seconds'),
            hints_used=data.get('hints_used')
        )
        
        return jsonify({
            'success': True,
            **feedback
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/complete', methods=['POST'])
@jwt_required()
def complete_assessment_attempt(attempt_id):
    """
    Complete an assessment and generate results.
    
    Returns:
    {
        "success": true,
        "result": {
            "overall_score": 85.5,
            "proficiency_level": "intermediate",
            "theta_estimate": 0.8,
            "percentile_rank": 73.5,
            "skill_scores": {...},
            "strengths": [...],
            "weaknesses": [...],
            "recommendations": [...]
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify attempt
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        # Complete assessment
        result = assessment_engine.complete_assessment(attempt_id)
        
        return jsonify({
            'success': True,
            'result': result.to_dict(),
            'message': 'Assessment completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/status', methods=['GET'])
@jwt_required()
def get_attempt_status(attempt_id):
    """
    Get current status of an assessment attempt.
    """
    try:
        user_id = get_jwt_identity()
        
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        # Get assessment info
        assessment = Assessment.query.get(attempt.assessment_id)
        
        # Calculate progress percentage
        if assessment.is_adaptive:
            # For adaptive, estimate based on SE threshold
            progress = min(100, (1 - attempt.theta_standard_error) * 100)
        else:
            # For fixed, based on questions answered
            total_questions = AssessmentQuestion.query.filter_by(
                assessment_id=assessment.id,
                is_active=True
            ).count()
            progress = (attempt.questions_answered / total_questions * 100) if total_questions > 0 else 0
        
        return jsonify({
            'success': True,
            'attempt': {
                'id': attempt.id,
                'status': attempt.status,
                'questions_answered': attempt.questions_answered,
                'correct_count': attempt.correct_count,
                'current_theta': attempt.current_theta_estimate,
                'theta_se': attempt.theta_standard_error,
                'progress_percent': progress,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None
            },
            'assessment': {
                'title': assessment.title,
                'is_adaptive': assessment.is_adaptive,
                'duration_minutes': assessment.duration_minutes
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# RESULTS AND DIAGNOSTICS
# ================================================================

@assessment_bp.route('/assessments/attempts/<int:attempt_id>/results', methods=['GET'])
@jwt_required()
def get_results(attempt_id):
    """
    Get comprehensive results for a completed assessment.
    """
    try:
        user_id = get_jwt_identity()
        
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        if attempt.status != 'completed':
            return jsonify({
                'success': False,
                'error': 'Assessment not yet completed'
            }), 400
        
        # Get result
        result = AssessmentResult.query.filter_by(attempt_id=attempt_id).first()
        if not result:
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404
        
        # Get assessment info
        assessment = Assessment.query.get(attempt.assessment_id)
        
        return jsonify({
            'success': True,
            'result': result.to_dict(),
            'assessment': {
                'title': assessment.title,
                'assessment_type': assessment.assessment_type,
                'passing_score': assessment.passing_score
            },
            'attempt': {
                'questions_answered': attempt.questions_answered,
                'correct_count': attempt.correct_count,
                'started_at': attempt.started_at.isoformat(),
                'completed_at': attempt.completed_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/diagnostics', methods=['GET'])
@jwt_required()
def get_diagnostics(attempt_id):
    """
    Get detailed skill diagnostics for an assessment attempt.
    """
    try:
        user_id = get_jwt_identity()
        
        attempt = UserAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Assessment attempt not found'
            }), 404
        
        # Get diagnostics
        diagnostics = assessment_engine.get_skill_diagnostics(attempt_id)
        
        return jsonify({
            'success': True,
            'diagnostics': diagnostics,
            'total_skills': len(diagnostics)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# ANALYTICS AND HISTORY
# ================================================================

@assessment_bp.route('/assessments/my-history', methods=['GET'])
@jwt_required()
def get_my_history():
    """
    Get user's assessment history.
    
    Query params:
    - assessment_id: Filter by specific assessment
    """
    try:
        user_id = get_jwt_identity()
        assessment_id = request.args.get('assessment_id', type=int)
        
        history = assessment_engine.get_user_assessment_history(
            user_id=user_id,
            assessment_id=assessment_id
        )
        
        return jsonify({
            'success': True,
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/<int:assessment_id>/analytics', methods=['GET'])
@jwt_required()
def get_analytics(assessment_id):
    """
    Get analytics for an assessment (aggregated statistics).
    """
    try:
        analytics = assessment_engine.get_assessment_analytics(assessment_id)
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/compare/<int:attempt_id_1>/<int:attempt_id_2>', methods=['GET'])
@jwt_required()
def compare_attempts(attempt_id_1, attempt_id_2):
    """
    Compare two assessment attempts to show improvement.
    """
    try:
        user_id = get_jwt_identity()
        
        # Verify both attempts belong to user
        attempt1 = UserAssessmentAttempt.query.get(attempt_id_1)
        attempt2 = UserAssessmentAttempt.query.get(attempt_id_2)
        
        if not attempt1 or not attempt2:
            return jsonify({
                'success': False,
                'error': 'One or both attempts not found'
            }), 404
        
        if attempt1.user_id != user_id or attempt2.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to attempts'
            }), 403
        
        # Compare
        comparison = assessment_engine.compare_attempts(attempt_id_1, attempt_id_2)
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# RECOMMENDATIONS AND ADVANCED FEATURES
# ================================================================

@assessment_bp.route('/assessments/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """
    Get recommended assessments for the user based on their history.
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user's latest assessment
        latest_attempt = UserAssessmentAttempt.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(UserAssessmentAttempt.completed_at.desc()).first()
        
        recommendations = []
        
        if latest_attempt:
            # Get result
            result = AssessmentResult.query.filter_by(
                attempt_id=latest_attempt.id
            ).first()
            
            if result:
                # Recommend based on proficiency and weaknesses
                proficiency = result.proficiency_level
                
                # Recommend progress assessments
                progress_assessments = Assessment.query.filter_by(
                    assessment_type='progress',
                    proficiency_level=proficiency,
                    is_active=True
                ).limit(3).all()
                
                recommendations.extend([{
                    'assessment': a.to_dict(),
                    'reason': f'Progress check for {proficiency} level',
                    'priority': 'high'
                } for a in progress_assessments])
                
                # Recommend mastery for strengths
                if result.strengths:
                    for strength in result.strengths[:2]:
                        mastery_assessments = Assessment.query.filter(
                            Assessment.assessment_type == 'mastery',
                            Assessment.skill_areas.contains([strength]),
                            Assessment.is_active == True
                        ).limit(1).all()
                        
                        recommendations.extend([{
                            'assessment': a.to_dict(),
                            'reason': f'Master your strength in {strength}',
                            'priority': 'medium'
                        } for a in mastery_assessments])
        else:
            # No history - recommend placement
            placement = Assessment.query.filter_by(
                assessment_type='placement',
                is_active=True
            ).limit(3).all()
            
            recommendations.extend([{
                'assessment': a.to_dict(),
                'reason': 'Determine your initial proficiency level',
                'priority': 'high'
            } for a in placement])
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/certification-ready', methods=['GET'])
@jwt_required()
def check_certification_readiness():
    """
    Check if user is ready for certification based on recent performance.
    
    Query params:
    - certification_name: Name of certification
    """
    try:
        user_id = get_jwt_identity()
        certification_name = request.args.get('certification_name')
        
        if not certification_name:
            return jsonify({
                'success': False,
                'error': 'certification_name required'
            }), 400
        
        # Find certification assessment
        cert_assessment = Assessment.query.filter_by(
            assessment_type='certification',
            certification_name=certification_name,
            is_active=True
        ).first()
        
        if not cert_assessment:
            return jsonify({
                'success': False,
                'error': 'Certification assessment not found'
            }), 404
        
        # Get user's recent mastery assessments
        mastery_attempts = UserAssessmentAttempt.query.join(Assessment).filter(
            UserAssessmentAttempt.user_id == user_id,
            UserAssessmentAttempt.status == 'completed',
            Assessment.assessment_type == 'mastery'
        ).order_by(UserAssessmentAttempt.completed_at.desc()).limit(5).all()
        
        # Analyze readiness
        readiness_score = 0.0
        skill_readiness = {}
        
        if mastery_attempts:
            for attempt in mastery_attempts:
                result = AssessmentResult.query.filter_by(
                    attempt_id=attempt.id
                ).first()
                
                if result and result.passed:
                    readiness_score += 20  # Each passed mastery adds to readiness
                    
                    # Track skill readiness
                    for skill, score in result.skill_scores.items():
                        if skill not in skill_readiness:
                            skill_readiness[skill] = []
                        skill_readiness[skill].append(score)
        
        # Calculate average skill scores
        avg_skill_scores = {
            skill: sum(scores) / len(scores)
            for skill, scores in skill_readiness.items()
        }
        
        # Check if all required skills are covered
        required_skills = set(cert_assessment.skill_areas or [])
        covered_skills = set(avg_skill_scores.keys())
        missing_skills = list(required_skills - covered_skills)
        
        # Determine readiness
        is_ready = (
            readiness_score >= 60 and
            len(missing_skills) == 0 and
            all(score >= 70 for score in avg_skill_scores.values())
        )
        
        return jsonify({
            'success': True,
            'is_ready': is_ready,
            'readiness_score': min(100, readiness_score),
            'skill_readiness': avg_skill_scores,
            'missing_skills': missing_skills,
            'mastery_assessments_completed': len(mastery_attempts),
            'recommendation': (
                'You are ready for certification!' if is_ready
                else f'Complete mastery assessments for: {", ".join(missing_skills)}' if missing_skills
                else 'Improve scores in mastery assessments to 70%+'
            )
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# LEARNING PATH INTEGRATION
# ================================================================

@assessment_bp.route('/assessments/attempts/<int:attempt_id>/learning-path-recommendations', methods=['GET'])
@jwt_required()
def get_learning_path_recommendations_from_assessment(attempt_id):
    """
    Get personalized learning path recommendations based on assessment results.
    
    Returns:
        Recommended learning paths with priority and reasons
    """
    try:
        from app.services.assessment_learning_path_integration import AssessmentLearningPathIntegration
        
        user_id = get_jwt_identity()
        
        # Get recommendations
        recommendations = AssessmentLearningPathIntegration.recommend_paths_from_assessment(
            user_id, attempt_id
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/attempts/<int:attempt_id>/create-personalized-path', methods=['POST'])
@jwt_required()
def create_personalized_path(attempt_id):
    """
    Create a personalized adaptive learning path based on assessment results.
    
    Returns:
        Created learning path ID and details
    """
    try:
        from app.services.assessment_learning_path_integration import AssessmentLearningPathIntegration
        
        user_id = get_jwt_identity()
        
        # Create path
        path_id = AssessmentLearningPathIntegration.create_personalized_path_from_assessment(
            user_id, attempt_id
        )
        
        if not path_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create personalized path'
            }), 400
        
        return jsonify({
            'success': True,
            'path_id': path_id,
            'message': 'Personalized learning path created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/learning-paths/<int:path_id>/suggested-assessments', methods=['GET'])
@jwt_required()
def get_suggested_assessments_for_path(path_id):
    """
    Get suggested assessments based on learning path progress.
    
    Returns:
        Suggested assessments with timing and priority
    """
    try:
        from app.services.assessment_learning_path_integration import AssessmentLearningPathIntegration
        
        user_id = get_jwt_identity()
        
        # Get suggestions
        suggestions = AssessmentLearningPathIntegration.suggest_next_assessment(
            user_id, path_id
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'total': len(suggestions)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@assessment_bp.route('/assessments/learning-paths/<int:path_id>/update-from-assessment/<int:attempt_id>', methods=['POST'])
@jwt_required()
def update_path_from_assessment(path_id, attempt_id):
    """
    Update adaptive learning path based on progress assessment results.
    
    Returns:
        Updated path data with improvements and remaining skills
    """
    try:
        from app.services.assessment_learning_path_integration import AssessmentLearningPathIntegration
        
        user_id = get_jwt_identity()
        
        # Update path
        update_data = AssessmentLearningPathIntegration.update_path_from_progress_assessment(
            user_id, path_id, attempt_id
        )
        
        if not update_data:
            return jsonify({
                'success': False,
                'error': 'Failed to update path or invalid parameters'
            }), 400
        
        return jsonify({
            'success': True,
            'update': update_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ================================================================
# HEALTH CHECK
# ================================================================

@assessment_bp.route('/assessments/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for assessment system.
    """
    try:
        # Check database connectivity
        assessment_count = Assessment.query.count()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'Intelligent Assessment System',
            'features': {
                'irt_adaptive_testing': True,
                'skill_diagnostics': True,
                'multi_stage_assessments': True,
                'analytics': True,
                'learning_path_integration': True
            },
            'total_assessments': assessment_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500
