from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, AssessmentQuestionResponse, ActivityQuestionResponse,
    ProficiencyAssessment, Activity, UserActivityLog, UserAnalytics,
    UserLearningTimeline
)
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import traceback

enhanced_assessment_bp = Blueprint('enhanced_assessment', __name__)
enhanced_activity_bp = Blueprint('enhanced_activity', __name__)

# Enhanced Assessment Endpoints

@enhanced_assessment_bp.route('/<int:assessment_id>/question-analysis', methods=['GET'])
@jwt_required()
def get_assessment_question_analysis(assessment_id):
    """Get detailed per-question analysis for an assessment."""
    try:
        user_id = get_jwt_identity()
        
        # Verify assessment belongs to user
        assessment = ProficiencyAssessment.query.filter_by(
            id=assessment_id, 
            user_id=user_id
        ).first()
        
        if not assessment:
            return jsonify({
                'error': 'Assessment not found or access denied',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు లేదా ప్రవేశం నిరాకరించబడింది'
            }), 404
        
        # Get question responses
        question_responses = AssessmentQuestionResponse.query.filter_by(
            assessment_id=assessment_id,
            user_id=user_id
        ).order_by(AssessmentQuestionResponse.question_id).all()
        
        if not question_responses:
            return jsonify({
                'error': 'No question responses found for this assessment',
                'telugu_error': 'ఈ మూల్యాంకనానికి ప్రశ్న ప్రతిస్పందనలు కనుగొనబడలేదు'
            }), 404
        
        # Analyze questions
        question_analysis = []
        total_time = 0
        correct_count = 0
        
        for response in question_responses:
            analysis = {
                'question_id': response.question_id,
                'question_text': response.question_text,
                'question_type': response.question_type,
                'user_answer': response.user_answer,
                'correct_answer': response.correct_answer,
                'is_correct': response.is_correct,
                'time_spent_seconds': response.time_spent_seconds,
                'confidence_level': response.confidence_level,
                'difficulty_level': response.difficulty_level,
                'skill_area': response.skill_area,
                'points_earned': response.points_earned,
                'hints_used': response.hints_used,
                'attempts_before_correct': response.attempts_before_correct
            }
            question_analysis.append(analysis)
            
            if response.time_spent_seconds:
                total_time += response.time_spent_seconds
            if response.is_correct:
                correct_count += 1
        
        # Calculate statistics
        stats = {
            'total_questions': len(question_responses),
            'correct_answers': correct_count,
            'accuracy_percentage': (correct_count / len(question_responses)) * 100,
            'total_time_seconds': total_time,
            'average_time_per_question': total_time / len(question_responses) if question_responses else 0,
            'total_hints_used': sum(r.hints_used or 0 for r in question_responses),
            'average_confidence': sum(r.confidence_level or 0 for r in question_responses) / len(question_responses) if question_responses else 0
        }
        
        # Skill breakdown
        skill_breakdown = {}
        for response in question_responses:
            if response.skill_area:
                if response.skill_area not in skill_breakdown:
                    skill_breakdown[response.skill_area] = {
                        'total': 0,
                        'correct': 0,
                        'total_time': 0
                    }
                skill_breakdown[response.skill_area]['total'] += 1
                if response.is_correct:
                    skill_breakdown[response.skill_area]['correct'] += 1
                if response.time_spent_seconds:
                    skill_breakdown[response.skill_area]['total_time'] += response.time_spent_seconds
        
        # Calculate skill percentages
        for skill, data in skill_breakdown.items():
            data['accuracy_percentage'] = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
            data['average_time'] = data['total_time'] / data['total'] if data['total'] > 0 else 0
        
        return jsonify({
            'success': True,
            'assessment_id': assessment_id,
            'question_analysis': question_analysis,
            'statistics': stats,
            'skill_breakdown': skill_breakdown
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get question analysis',
            'details': str(e)
        }), 500

@enhanced_assessment_bp.route('/<int:assessment_id>/comparative-report', methods=['GET'])
@jwt_required()
def get_comparative_assessment_report(assessment_id):
    """Compare current assessment with previous assessments."""
    try:
        user_id = get_jwt_identity()
        
        # Get current assessment
        current_assessment = ProficiencyAssessment.query.filter_by(
            id=assessment_id,
            user_id=user_id
        ).first()
        
        if not current_assessment:
            return jsonify({
                'error': 'Assessment not found',
                'telugu_error': 'మూల్యాంకనం కనుగొనబడలేదు'
            }), 404
        
        # Get previous assessments
        previous_assessments = ProficiencyAssessment.query.filter(
            ProficiencyAssessment.user_id == user_id,
            ProficiencyAssessment.id < assessment_id,
            ProficiencyAssessment.status == 'completed'
        ).order_by(desc(ProficiencyAssessment.completed_at)).limit(5).all()
        
        if not previous_assessments:
            return jsonify({
                'message': 'No previous assessments found for comparison',
                'telugu_message': 'పోలిక కోసం మునుపటి మూల్యాంకనలు కనుగొనబడలేదు',
                'current_assessment': {
                    'id': current_assessment.id,
                    'score': current_assessment.score,
                    'max_score': current_assessment.max_score,
                    'proficiency_level': current_assessment.proficiency_level,
                    'completed_at': current_assessment.completed_at.isoformat() if current_assessment.completed_at else None
                }
            }), 200
        
        # Compare with most recent previous assessment
        most_recent = previous_assessments[0]
        
        current_percentage = (current_assessment.score / current_assessment.max_score * 100) if current_assessment.max_score > 0 else 0
        previous_percentage = (most_recent.score / most_recent.max_score * 100) if most_recent.max_score > 0 else 0
        
        improvement = current_percentage - previous_percentage
        
        # Skill comparison
        current_skills = current_assessment.skill_breakdown or {}
        previous_skills = most_recent.skill_breakdown or {}
        
        skill_comparison = {}
        all_skills = set(current_skills.keys()) | set(previous_skills.keys())
        
        for skill in all_skills:
            current_score = current_skills.get(skill, 0)
            previous_score = previous_skills.get(skill, 0)
            skill_comparison[skill] = {
                'current_score': current_score,
                'previous_score': previous_score,
                'improvement': current_score - previous_score,
                'improvement_percentage': ((current_score - previous_score) / previous_score * 100) if previous_score > 0 else 0
            }
        
        # Historical trend
        historical_trend = []
        for assessment in reversed(previous_assessments):
            if assessment.score and assessment.max_score:
                percentage = (assessment.score / assessment.max_score * 100)
                historical_trend.append({
                    'assessment_id': assessment.id,
                    'score_percentage': percentage,
                    'proficiency_level': assessment.proficiency_level,
                    'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None
                })
        
        # Add current assessment to trend
        historical_trend.append({
            'assessment_id': current_assessment.id,
            'score_percentage': current_percentage,
            'proficiency_level': current_assessment.proficiency_level,
            'completed_at': current_assessment.completed_at.isoformat() if current_assessment.completed_at else None
        })
        
        return jsonify({
            'success': True,
            'current_assessment': {
                'id': current_assessment.id,
                'score_percentage': current_percentage,
                'proficiency_level': current_assessment.proficiency_level
            },
            'comparison_with_previous': {
                'previous_assessment_id': most_recent.id,
                'previous_score_percentage': previous_percentage,
                'improvement': improvement,
                'improvement_status': 'improved' if improvement > 0 else 'declined' if improvement < 0 else 'same'
            },
            'skill_comparison': skill_comparison,
            'historical_trend': historical_trend
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate comparative report',
            'details': str(e)
        }), 500

@enhanced_assessment_bp.route('/skill-progression', methods=['GET'])
@jwt_required()
def get_skill_progression():
    """Track skill improvement over time across assessments."""
    try:
        user_id = get_jwt_identity()
        
        # Get all completed assessments
        assessments = ProficiencyAssessment.query.filter(
            ProficiencyAssessment.user_id == user_id,
            ProficiencyAssessment.status == 'completed'
        ).order_by(ProficiencyAssessment.completed_at).all()
        
        if not assessments:
            return jsonify({
                'message': 'No completed assessments found',
                'telugu_message': 'పూర్తి చేసిన మూల్యాంకనలు కనుగొనబడలేదు'
            }), 200
        
        # Track skill progression
        skill_progression = {}
        assessment_timeline = []
        
        for assessment in assessments:
            assessment_data = {
                'assessment_id': assessment.id,
                'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None,
                'overall_score': (assessment.score / assessment.max_score * 100) if assessment.max_score > 0 else 0,
                'proficiency_level': assessment.proficiency_level
            }
            
            if assessment.skill_breakdown:
                assessment_data['skills'] = assessment.skill_breakdown
                
                # Track each skill over time
                for skill, score in assessment.skill_breakdown.items():
                    if skill not in skill_progression:
                        skill_progression[skill] = []
                    
                    skill_progression[skill].append({
                        'assessment_id': assessment.id,
                        'score': score,
                        'completed_at': assessment.completed_at.isoformat() if assessment.completed_at else None
                    })
            
            assessment_timeline.append(assessment_data)
        
        # Calculate improvement rates for each skill
        skill_analysis = {}
        for skill, progression in skill_progression.items():
            if len(progression) >= 2:
                first_score = progression[0]['score']
                latest_score = progression[-1]['score']
                improvement = latest_score - first_score
                
                skill_analysis[skill] = {
                    'progression': progression,
                    'first_score': first_score,
                    'latest_score': latest_score,
                    'total_improvement': improvement,
                    'assessment_count': len(progression),
                    'trend': 'improving' if improvement > 0 else 'declining' if improvement < 0 else 'stable'
                }
            else:
                skill_analysis[skill] = {
                    'progression': progression,
                    'first_score': progression[0]['score'] if progression else 0,
                    'latest_score': progression[-1]['score'] if progression else 0,
                    'total_improvement': 0,
                    'assessment_count': len(progression),
                    'trend': 'insufficient_data'
                }
        
        return jsonify({
            'success': True,
            'total_assessments': len(assessments),
            'assessment_timeline': assessment_timeline,
            'skill_progression': skill_analysis
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get skill progression',
            'details': str(e)
        }), 500

# Enhanced Activity Endpoints

@enhanced_activity_bp.route('/<int:activity_id>/question-breakdown', methods=['GET'])
@jwt_required()
def get_activity_question_breakdown(activity_id):
    """Get detailed per-question breakdown for an activity."""
    try:
        user_id = get_jwt_identity()
        
        # Verify activity access
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({'error': 'Activity not found'}), 404
        
        # Get user's activity logs for this activity
        activity_logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        if not activity_logs:
            return jsonify({
                'error': 'No activity logs found for this activity',
                'telugu_error': 'ఈ కార్యకలాపానికి లాగ్‌లు కనుగొనబడలేదు'
            }), 404
        
        # Get question responses for all attempts
        all_responses = []
        for log in activity_logs:
            responses = ActivityQuestionResponse.query.filter_by(
                activity_log_id=log.id,
                user_id=user_id,
                activity_id=activity_id
            ).order_by(ActivityQuestionResponse.question_index).all()
            
            if responses:
                attempt_data = {
                    'attempt_number': log.attempt_number,
                    'completed_at': log.completed_at.isoformat(),
                    'overall_score': log.score,
                    'max_score': log.max_score,
                    'time_spent_minutes': log.time_spent_minutes,
                    'questions': []
                }
                
                for response in responses:
                    question_data = {
                        'question_index': response.question_index,
                        'question_text': response.question_text,
                        'question_type': response.question_type,
                        'user_answer': response.user_answer,
                        'correct_answer': response.correct_answer,
                        'is_correct': response.is_correct,
                        'time_spent_seconds': response.time_spent_seconds,
                        'hints_used': response.hints_used,
                        'difficulty_level': response.difficulty_level,
                        'skill_area': response.skill_area,
                        'points_earned': response.points_earned,
                        'ai_feedback': response.ai_feedback
                    }
                    attempt_data['questions'].append(question_data)
                
                all_responses.append(attempt_data)
        
        # Calculate overall statistics across all attempts
        total_questions = 0
        total_correct = 0
        total_time = 0
        skill_stats = {}
        
        for attempt in all_responses:
            for question in attempt['questions']:
                total_questions += 1
                if question['is_correct']:
                    total_correct += 1
                if question['time_spent_seconds']:
                    total_time += question['time_spent_seconds']
                
                skill = question['skill_area']
                if skill:
                    if skill not in skill_stats:
                        skill_stats[skill] = {'total': 0, 'correct': 0}
                    skill_stats[skill]['total'] += 1
                    if question['is_correct']:
                        skill_stats[skill]['correct'] += 1
        
        # Calculate skill percentages
        for skill, stats in skill_stats.items():
            stats['accuracy'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        overall_stats = {
            'total_attempts': len(all_responses),
            'total_questions_answered': total_questions,
            'total_correct': total_correct,
            'overall_accuracy': (total_correct / total_questions * 100) if total_questions > 0 else 0,
            'total_time_seconds': total_time,
            'average_time_per_question': total_time / total_questions if total_questions > 0 else 0,
            'skill_breakdown': skill_stats
        }
        
        return jsonify({
            'success': True,
            'activity_id': activity_id,
            'activity_title': activity.title,
            'activity_type': activity.activity_type,
            'overall_statistics': overall_stats,
            'attempts': all_responses
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get activity question breakdown',
            'details': str(e)
        }), 500

@enhanced_activity_bp.route('/performance-history', methods=['GET'])
@jwt_required()
def get_activity_performance_history():
    """Get historical performance across all activities."""
    try:
        user_id = get_jwt_identity()
        activity_type = request.args.get('activity_type')  # Optional filter
        days = int(request.args.get('days', 30))
        
        # Build query
        query = db.session.query(
            UserActivityLog,
            Activity
        ).join(Activity).filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.completed_at >= datetime.now() - timedelta(days=days)
        )
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        results = query.order_by(desc(UserActivityLog.completed_at)).all()
        
        performance_history = []
        activity_type_stats = {}
        
        for log, activity in results:
            score_percentage = (log.score / log.max_score * 100) if log.max_score and log.max_score > 0 else 0
            
            performance_entry = {
                'activity_id': activity.id,
                'activity_title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'completed_at': log.completed_at.isoformat(),
                'score': log.score,
                'max_score': log.max_score,
                'score_percentage': score_percentage,
                'time_spent_minutes': log.time_spent_minutes,
                'attempt_number': log.attempt_number
            }
            performance_history.append(performance_entry)
            
            # Track stats by activity type
            if activity.activity_type not in activity_type_stats:
                activity_type_stats[activity.activity_type] = {
                    'count': 0,
                    'total_score': 0,
                    'total_time': 0
                }
            
            activity_type_stats[activity.activity_type]['count'] += 1
            activity_type_stats[activity.activity_type]['total_score'] += score_percentage
            if log.time_spent_minutes:
                activity_type_stats[activity.activity_type]['total_time'] += log.time_spent_minutes
        
        # Calculate averages
        for activity_type, stats in activity_type_stats.items():
            if stats['count'] > 0:
                stats['average_score'] = stats['total_score'] / stats['count']
                stats['average_time_minutes'] = stats['total_time'] / stats['count']
        
        return jsonify({
            'success': True,
            'performance_history': performance_history,
            'activity_type_statistics': activity_type_stats,
            'total_activities': len(performance_history)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get performance history',
            'details': str(e)
        }), 500