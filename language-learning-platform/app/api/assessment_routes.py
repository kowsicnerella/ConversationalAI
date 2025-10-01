from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.initial_assessment_service import InitialAssessmentService
from app.models import User, ProficiencyAssessment
from app.models import db
from typing import Dict, List
import traceback

assessment_routes = Blueprint('assessment', __name__)
assessment_service = InitialAssessmentService()


@assessment_routes.route('/api/assessment/generate', methods=['POST'])
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
        
        assessment_type = data.get('assessment_type', 'comprehensive')
        skill_area = data.get('skill_area')
        
        # Validate assessment type
        valid_types = ['comprehensive', 'quick', 'adaptive', 'skill_specific']
        if assessment_type not in valid_types:
            return jsonify({
                'error': f'Invalid assessment type. Must be one of: {", ".join(valid_types)}',
                'telugu_error': 'చెల్లని మూల్యాంకన రకం'
            }), 400
        
        # Validate skill area for skill-specific assessment
        if assessment_type == 'skill_specific':
            if not skill_area:
                return jsonify({
                    'error': 'skill_area is required for skill_specific assessment',
                    'telugu_error': 'నైపుణ్య రంగం అవసరం'
                }), 400
            
            valid_skills = ['vocabulary', 'grammar', 'reading', 'listening', 'writing']
            if skill_area not in valid_skills:
                return jsonify({
                    'error': f'Invalid skill area. Must be one of: {", ".join(valid_skills)}',
                    'telugu_error': 'చెల్లని నైపుణ్య రంగం'
                }), 400
            
            assessment_data = assessment_service.generate_skill_specific_assessment(user_id, skill_area)
        else:
            assessment_data = assessment_service.generate_placement_assessment(user_id, assessment_type)
        
        return jsonify({
            'success': True,
            'assessment': assessment_data,
            'message': f'{assessment_type.title()} assessment generated successfully',
            'telugu_message': f'{assessment_type} మూల్యాంకనం విజయవంతంగా రూపొందించబడింది'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'telugu_error': 'మూల్యాంకనం రూపొందించడంలో లోపం'
        }), 400
    except Exception as e:
        print(f"Error in assessment generation: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate assessment',
            'telugu_error': 'మూల్యాంకనం రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/<int:assessment_id>/submit', methods=['POST'])
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
        
        if not data or 'answers' not in data:
            return jsonify({
                'error': 'Answers are required',
                'telugu_error': 'సమాధానాలు అవసరం'
            }), 400
        
        answers = data['answers']
        
        # Verify assessment belongs to current user
        assessment = ProficiencyAssessment.query.get(assessment_id)
        if not assessment or assessment.user_id != user_id:
            return jsonify({
                'error': 'Assessment not found or unauthorized',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం'
            }), 404
        
        if not answers:
            return jsonify({
                'error': 'At least one answer is required',
                'telugu_error': 'కనీసం ఒక సమాధానం అవసరం'
            }), 400
        
        # Submit and evaluate assessment
        results = assessment_service.submit_assessment_answers(assessment_id, answers)
        
        return jsonify({
            'success': True,
            'assessment_results': results,
            'message': 'Assessment completed successfully',
            'telugu_message': 'మూల్యాంకనం విజయవంతంగా పూర్తయింది'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'telugu_error': 'మూల్యాంకనం సమర్పణలో లోపం'
        }), 400
    except Exception as e:
        print(f"Error in assessment submission: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to submit assessment',
            'telugu_error': 'మూల్యాంకనం సమర్పణలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/history', methods=['GET'])
@jwt_required()
def get_assessment_history():
    """
    Get assessment history for the current user.
    """
    try:
        user_id = get_jwt_identity()
        
        history = assessment_service.get_assessment_history(user_id)
        
        return jsonify({
            'success': True,
            'assessment_history': history,
            'total_assessments': len(history),
            'message': f'Retrieved {len(history)} assessment records',
            'telugu_message': f'{len(history)} మూల్యాంకన రికార్డులు వెలికితీయబడ్డాయి'
        }), 200
        
    except Exception as e:
        print(f"Error in assessment history: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to retrieve assessment history',
            'telugu_error': 'మూల్యాంకన చరిత్రను వెలికితీయడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/<int:assessment_id>/details', methods=['GET'])
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
            return jsonify({
                'error': 'Assessment not found',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు'
            }), 404
        
        if assessment.user_id != user_id:
            return jsonify({
                'error': 'Unauthorized access to assessment',
                'telugu_error': 'మూల్యాంకనానికి అనధికృత ప్రవేశం'
            }), 403
        
        # Build assessment details
        assessment_details = {
            'assessment_id': assessment.id,
            'assessment_type': assessment.assessment_type,
            'status': assessment.status,
            'started_at': assessment.started_at.isoformat() if assessment.started_at else None,
            'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None,
            'proficiency_level': assessment.proficiency_level,
            'score': assessment.score,
            'max_score': assessment.max_score
        }
        
        # Add detailed results if assessment is completed
        if assessment.status == 'completed' and assessment.evaluation_results:
            import json
            evaluation_results = json.loads(assessment.evaluation_results)
            skill_breakdown = json.loads(assessment.skill_breakdown) if assessment.skill_breakdown else {}
            
            assessment_details.update({
                'percentage': (assessment.score / assessment.max_score * 100) if assessment.max_score > 0 else 0,
                'skill_breakdown': skill_breakdown,
                'evaluation_summary': {
                    'total_questions': len(evaluation_results.get('question_results', [])),
                    'correct_answers': len([q for q in evaluation_results.get('question_results', []) if q.get('correct')]),
                    'skill_performance': evaluation_results.get('skill_scores', {}),
                    'level_performance': evaluation_results.get('level_scores', {})
                }
            })
        
        # Add questions if assessment is in progress
        elif assessment.status == 'in_progress' and assessment.questions_data:
            import json
            questions = json.loads(assessment.questions_data)
            assessment_details['questions'] = questions
        
        return jsonify({
            'success': True,
            'assessment_details': assessment_details,
            'message': 'Assessment details retrieved successfully',
            'telugu_message': 'మూల్యాంకన వివరాలు విజయవంతంగా వెలికితీయబడ్డాయి'
        }), 200
        
    except Exception as e:
        print(f"Error in assessment details: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to retrieve assessment details',
            'telugu_error': 'మూల్యాంకన వివరాలను వెలికితీయడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/<int:assessment_id>/report', methods=['GET'])
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
            return jsonify({
                'error': 'Assessment not found',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు'
            }), 404
        
        if assessment.user_id != user_id:
            return jsonify({
                'error': 'Unauthorized access to assessment',
                'telugu_error': 'మూల్యాంకనానికి అనధికృత ప్రవేశం'
            }), 403
        
        if assessment.status != 'completed':
            return jsonify({
                'error': 'Assessment is not completed yet',
                'telugu_error': 'మూల్యాంకనం ఇంకా పూర్తికాలేదు'
            }), 400
        
        # Generate comprehensive report
        import json
        evaluation_results = json.loads(assessment.evaluation_results)
        skill_breakdown = json.loads(assessment.skill_breakdown) if assessment.skill_breakdown else {}
        
        # Create proficiency analysis from stored data
        proficiency_analysis = {
            'overall_level': assessment.proficiency_level,
            'overall_percentage': (assessment.score / assessment.max_score * 100) if assessment.max_score > 0 else 0,
            'skill_breakdown': skill_breakdown,
            'strengths': [skill for skill, data in skill_breakdown.items() if data.get('level') == 'strong'],
            'weaknesses': [skill for skill, data in skill_breakdown.items() if data.get('level') == 'needs_improvement']
        }
        
        # Generate learning path recommendations
        learning_path_recommendations = assessment_service._recommend_learning_paths(proficiency_analysis)
        
        # Generate comprehensive report
        report = assessment_service._generate_assessment_report(
            assessment, evaluation_results, proficiency_analysis, learning_path_recommendations
        )
        
        return jsonify({
            'success': True,
            'assessment_report': report,
            'message': 'Assessment report generated successfully',
            'telugu_message': 'మూల్యాంకన నివేదిక విజయవంతంగా రూపొందించబడింది'
        }), 200
        
    except Exception as e:
        print(f"Error in assessment report: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate assessment report',
            'telugu_error': 'మూల్యాంకన నివేదిక రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/<int:assessment_id>/retake', methods=['POST'])
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
            return jsonify({
                'error': 'Assessment not found or unauthorized',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు లేదా అనధికృతం'
            }), 404
        
        # Generate retake assessment
        retake_data = assessment_service.retake_assessment(user_id, assessment_id)
        
        return jsonify({
            'success': True,
            'retake_assessment': retake_data,
            'message': 'Retake assessment generated successfully',
            'telugu_message': 'మళ్లీ చేయు మూల్యాంకనం విజయవంతంగా రూపొందించబడింది',
            'note': 'This assessment is adapted based on your previous performance'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'telugu_error': 'మళ్లీ చేయు మూల్యాంకనంలో లోపం'
        }), 400
    except Exception as e:
        print(f"Error in retake assessment: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate retake assessment',
            'telugu_error': 'మళ్లీ చేయు మూల్యాంకనం రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/placement-recommendations', methods=['GET'])
@jwt_required()
def get_placement_recommendations():
    """
    Get learning path placement recommendations based on latest assessment.
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user's latest completed assessment
        latest_assessment = ProficiencyAssessment.query.filter_by(
            user_id=user_id, 
            status='completed'
        ).order_by(ProficiencyAssessment.completed_at.desc()).first()
        
        if not latest_assessment:
            return jsonify({
                'error': 'No completed assessment found. Please take an assessment first.',
                'telugu_error': 'పూర్తయిన మూల్యాంకనం కనుగొనబడలేదు. దయచేసి మొదట మూల్యాంకనం చేయండి',
                'suggestion': 'Take a placement assessment to get personalized recommendations'
            }), 404
        
        # Generate recommendations based on latest assessment
        import json
        skill_breakdown = json.loads(latest_assessment.skill_breakdown) if latest_assessment.skill_breakdown else {}
        
        proficiency_analysis = {
            'overall_level': latest_assessment.proficiency_level,
            'overall_percentage': (latest_assessment.score / latest_assessment.max_score * 100) if latest_assessment.max_score > 0 else 0,
            'skill_breakdown': skill_breakdown,
            'strengths': [skill for skill, data in skill_breakdown.items() if data.get('level') == 'strong'],
            'weaknesses': [skill for skill, data in skill_breakdown.items() if data.get('level') == 'needs_improvement']
        }
        
        learning_path_recommendations = assessment_service._recommend_learning_paths(proficiency_analysis)
        next_steps = assessment_service._generate_next_steps(proficiency_analysis, learning_path_recommendations)
        
        return jsonify({
            'success': True,
            'placement_recommendations': {
                'based_on_assessment': {
                    'assessment_id': latest_assessment.id,
                    'assessment_date': latest_assessment.completed_at.isoformat(),
                    'proficiency_level': latest_assessment.proficiency_level,
                    'overall_score': f"{latest_assessment.score}/{latest_assessment.max_score}"
                },
                'proficiency_summary': proficiency_analysis,
                'learning_path_recommendations': learning_path_recommendations,
                'immediate_next_steps': next_steps
            },
            'telugu_summary': assessment_service._generate_telugu_report_summary(proficiency_analysis),
            'recommendation_confidence': 'high' if latest_assessment.max_score > 20 else 'medium',
            'validity_period': '4-6 weeks'
        }), 200
        
    except Exception as e:
        print(f"Error in placement recommendations: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate placement recommendations',
            'telugu_error': 'ప్లేస్‌మెంట్ సిఫార్సులు రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/quick-check', methods=['POST'])
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
        skill_area = data.get('skill_area', 'mixed')
        
        # Generate quick assessment questions
        if skill_area == 'mixed':
            # Mix of vocabulary and grammar for quick check
            quick_questions = []
            for skill in ['vocabulary', 'grammar']:
                questions = assessment_service._generate_skill_level_questions(skill, 'intermediate', 2)
                quick_questions.extend(questions)
            questions = quick_questions[:5]  # Limit to 5 questions
        else:
            valid_skills = ['vocabulary', 'grammar', 'reading', 'writing']
            if skill_area not in valid_skills:
                return jsonify({
                    'error': f'Invalid skill area for quick check. Must be one of: {", ".join(valid_skills)} or "mixed"',
                    'telugu_error': 'త్వరిత తనిఖీ కోసం చెల్లని నైపుణ్య రంగం'
                }), 400
            
            questions = assessment_service._generate_skill_level_questions(skill_area, 'intermediate', 5)
        
        # Create temporary assessment for quick check
        max_score = sum(q['points'] for q in questions)
        
        return jsonify({
            'success': True,
            'quick_check': {
                'questions': questions,
                'metadata': {
                    'total_questions': len(questions),
                    'max_score': max_score,
                    'skill_focus': skill_area,
                    'estimated_duration': '5-8 minutes',
                    'purpose': 'Quick proficiency verification'
                },
                'instructions': {
                    'english': 'Answer these 5 questions to get a quick assessment of your current level.',
                    'telugu': 'మీ ప్రస్తుత స్థాయి యొక్క త్వరిత మూల్యాంకనం పొందడానికి ఈ 5 ప్రశ్నలకు సమాధానం ఇవ్వండి।'
                }
            },
            'message': 'Quick proficiency check generated',
            'telugu_message': 'త్వరిత ప్రావీణ్య తనిఖీ రూపొందించబడింది'
        }), 200
        
    except Exception as e:
        print(f"Error in quick proficiency check: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to generate quick proficiency check',
            'telugu_error': 'త్వరిత ప్రావీణ్య తనిఖీ రూపొందించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


@assessment_routes.route('/api/assessment/validate-answers', methods=['POST'])
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
        
        if not data or 'questions' not in data or 'answers' not in data:
            return jsonify({
                'error': 'Questions and answers are required',
                'telugu_error': 'ప్రశ్నలు మరియు సమాధానాలు అవసరం'
            }), 400
        
        questions = data['questions']
        answers = data['answers']
        
        # Evaluate answers
        evaluation_result = assessment_service._evaluate_assessment_answers(questions, answers)
        
        # Generate quick proficiency analysis
        total_percentage = (evaluation_result['total_score'] / evaluation_result['max_possible_score']) * 100
        
        if total_percentage >= 80:
            level_estimate = 'advanced'
            level_telugu = 'ఉన్నత'
            message = 'Excellent performance! You demonstrate advanced English skills.'
            telugu_message = 'అద్భుతమైన పనితీరు! మీరు ఉన్నత ఇంగ్లీష్ నైపుణ్యాలను ప్రదర్శిస్తున్నారు.'
        elif total_percentage >= 60:
            level_estimate = 'intermediate'
            level_telugu = 'మధ్యస్థ'
            message = 'Good performance! You have solid intermediate English skills.'
            telugu_message = 'మంచి పనితీరు! మీకు దృఢమైన మధ్యస్థ ఇంగ్లీష్ నైపుణ్యాలు ఉన్నాయి.'
        else:
            level_estimate = 'beginner'
            level_telugu = 'ప్రాథమిక'
            message = 'Keep practicing! Focus on building fundamental English skills.'
            telugu_message = 'అభ్యాసం కొనసాగించండి! ప్రాథమిక ఇంగ్లీష్ నైపుణ్యాలను అభివృద్ధి చేయడంపై దృష్టి పెట్టండి.'
        
        return jsonify({
            'success': True,
            'quick_assessment_results': {
                'score': f"{evaluation_result['total_score']}/{evaluation_result['max_possible_score']}",
                'percentage': round(total_percentage, 1),
                'estimated_level': level_estimate,
                'estimated_level_telugu': level_telugu,
                'correct_answers': len([q for q in evaluation_result['question_results'] if q['correct']]),
                'total_questions': len(evaluation_result['question_results']),
                'question_breakdown': evaluation_result['question_results']
            },
            'recommendations': {
                'message': message,
                'telugu_message': telugu_message,
                'suggested_action': 'Take a comprehensive assessment for detailed analysis and personalized learning path',
                'telugu_suggested_action': 'వివరణాత్మక విశ్లేషణ మరియు వ్యక్తిగతీకరించిన అభ్యాస మార్గం కోసం సమగ్ర మూల్యాంకనం చేయండి'
            },
            'note': 'This is a quick check only. For accurate placement, take a comprehensive assessment.'
        }), 200
        
    except Exception as e:
        print(f"Error in validating quick answers: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to validate answers',
            'telugu_error': 'సమాధానాలను ధృవీకరించడంలో వైఫల్యం',
            'details': str(e)
        }), 500


# Health check for assessment service
@assessment_routes.route('/api/assessment/health', methods=['GET'])
def assessment_health_check():
    """Health check for assessment service."""
    try:
        # Test basic functionality
        test_result = assessment_service._generate_skill_level_questions('vocabulary', 'beginner', 1)
        
        return jsonify({
            'status': 'healthy',
            'service': 'Initial Assessment Service',
            'capabilities': [
                'Comprehensive placement assessment',
                'Quick proficiency check',
                'Adaptive assessment',
                'Skill-specific assessment',
                'Assessment history tracking',
                'Learning path recommendations'
            ],
            'test_generation': 'success' if test_result else 'limited',
            'telugu_support': True
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'note': 'Assessment service may have limited functionality'
        }), 200