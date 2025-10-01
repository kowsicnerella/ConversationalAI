from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, Chapter, UserChapterProgress, TestAssessment, 
    VocabularyWord, MistakePattern
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.services.practice_agent_service import PracticeAgentService
from datetime import datetime
import json

test_bp = Blueprint('tests', __name__)
activity_service = ActivityGeneratorService()
practice_agent = PracticeAgentService()

@test_bp.route('/tests/create', methods=['POST'])
@jwt_required()
def create_test():
    """
    Create a comprehensive test for one or more chapters.
    
    Expected JSON:
    {
        "test_type": "chapter_test",  // chapter_test, comprehensive_test, placement_test
        "chapter_ids": [1, 2, 3],
        "num_questions": 20,
        "time_limit_minutes": 30,
        "question_types": ["multiple_choice", "fill_blank", "translation"]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        test_type = data.get('test_type', 'chapter_test')
        chapter_ids = data.get('chapter_ids', [])
        num_questions = data.get('num_questions', 10)
        time_limit = data.get('time_limit_minutes', 30)
        question_types = data.get('question_types', ['multiple_choice'])
        
        if not chapter_ids:
            return jsonify({
                'error': 'At least one chapter must be specified',
                'telugu_message': 'కనీసం ఒక అధ్యాయం తెలియజేయాలి'
            }), 400
        
        # Verify all chapters exist and are accessible
        chapters = Chapter.query.filter(Chapter.id.in_(chapter_ids)).all()
        if len(chapters) != len(chapter_ids):
            return jsonify({
                'error': 'One or more chapters not found',
                'telugu_message': 'ఒకటి లేదా అంతకంటే ఎక్కువ అధ్యాయాలు కనుగొనబడలేదు'
            }), 404
        
        # Generate comprehensive test questions
        test_questions = _generate_comprehensive_test_questions(
            user_id, chapters, num_questions, question_types, test_type
        )
        
        # Create test assessment record
        test_assessment = TestAssessment(
            user_id=user_id,
            test_type=test_type,
            chapter_ids=chapter_ids,
            total_questions=len(test_questions),
            questions_data=test_questions
        )
        
        db.session.add(test_assessment)
        db.session.commit()
        
        return jsonify({
            'message': 'Test created successfully!',
            'telugu_message': 'పరీక్ష విజయవంతంగా సృష్టించబడింది!',
            'test': {
                'id': test_assessment.id,
                'test_type': test_type,
                'total_questions': len(test_questions),
                'time_limit_minutes': time_limit,
                'chapters_covered': [ch.title for ch in chapters],
                'instructions': _get_test_instructions(test_type)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating test: {str(e)}")
        return jsonify({
            'error': 'Failed to create test',
            'telugu_message': 'పరీక్ష సృష్టించడంలో విఫలం'
        }), 500

@test_bp.route('/create', methods=['POST'])
@jwt_required()
def create_test_simple():
    """
    Create a test with simplified URL - alias for /tests/create.
    Supports the format you're using with title, description, etc.
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Map your parameters to the internal format
        title = data.get('title', 'Custom Test')
        description = data.get('description', '')
        chapter_ids = data.get('chapter_ids', [])
        question_count = data.get('question_count', 15)
        time_limit_minutes = data.get('time_limit_minutes', 30)
        difficulty_levels = data.get('difficulty_levels', ['beginner'])
        question_types = data.get('question_types', ['multiple_choice'])
        
        if not chapter_ids:
            return jsonify({
                'error': 'At least one chapter must be specified',
                'telugu_message': 'కనీసం ఒక అధ్యాయం తెలియజేయాలి'
            }), 400
        
        # Verify all chapters exist
        chapters = Chapter.query.filter(Chapter.id.in_(chapter_ids)).all()
        if len(chapters) != len(chapter_ids):
            return jsonify({
                'error': 'One or more chapters not found',
                'telugu_message': 'ఒకటి లేదా అంతకంటే ఎక్కువ అధ్యాయాలు కనుగొనబడలేదు'
            }), 404
        
        # Generate test questions based on your specifications
        test_questions = _generate_comprehensive_test_questions(
            user_id, chapters, question_count, question_types, 'chapter_test'
        )
        
        # Create test assessment record
        test_assessment = TestAssessment(
            user_id=user_id,
            test_type='chapter_test',
            chapter_ids=chapter_ids,
            total_questions=len(test_questions),
            questions_data=test_questions
        )
        
        db.session.add(test_assessment)
        db.session.commit()
        
        return jsonify({
            'message': 'Test created successfully!',
            'telugu_message': 'పరీక్ష విజయవంతంగా సృష్టించబడింది!',
            'success': True,
            'test': {
                'id': test_assessment.id,
                'title': title,
                'description': description,
                'test_type': 'chapter_test',
                'total_questions': len(test_questions),
                'time_limit_minutes': time_limit_minutes,
                'difficulty_levels': difficulty_levels,
                'question_types': question_types,
                'chapters_covered': [ch.title for ch in chapters],
                'chapter_ids': chapter_ids,
                'instructions': _get_test_instructions('chapter_test')
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating test: {str(e)}")
        return jsonify({
            'error': 'Failed to create test',
            'telugu_message': 'పరీక్ష సృష్టించడంలో విఫలం'
        }), 500

@test_bp.route('/tests/<int:test_id>/start', methods=['POST'])
@jwt_required()
def start_test(test_id):
    """
    Start taking a test and get the first set of questions.
    """
    try:
        user_id = int(get_jwt_identity())
        
        test = TestAssessment.query.filter_by(
            id=test_id, user_id=user_id
        ).first()
        
        if not test:
            return jsonify({
                'error': 'Test not found',
                'telugu_message': 'పరీక్ష కనుగొనబడలేదు'
            }), 404
        
        if test.is_completed:
            return jsonify({
                'error': 'Test already completed',
                'telugu_message': 'పరీక్ష ఇప్పటికే పూర్తైంది'
            }), 400
        
        # Update start time if not already started
        if not test.start_time:
            test.start_time = datetime.utcnow()
            db.session.commit()
        
        # Get test questions (don't show correct answers)
        questions_for_user = []
        for question in test.questions_data or []:
            user_question = {
                'id': question['id'],
                'type': question['type'],
                'question_text': question['question_text'],
                'question_telugu': question.get('question_telugu', ''),
                'options': question.get('options', []),
                'telugu_hint': question.get('telugu_hint', ''),
                'skill_tested': question.get('skill_tested', ''),
                'difficulty': question.get('difficulty', '')
            }
            # Don't include correct_answer or explanation
            questions_for_user.append(user_question)
        
        return jsonify({
            'message': 'Test started successfully!',
            'telugu_message': 'పరీక్ష విజయవంతంగా ప్రారంభైంది!',
            'test': {
                'id': test.id,
                'test_type': test.test_type,
                'total_questions': test.total_questions,
                'start_time': test.start_time.isoformat(),
                'questions': questions_for_user
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error starting test: {str(e)}")
        return jsonify({
            'error': 'Failed to start test',
            'telugu_message': 'పరీక్ష ప్రారంభించడంలో విఫలం'
        }), 500

@test_bp.route('/<int:test_id>/start', methods=['POST'])
@jwt_required()
def start_test_simple(test_id):
    """
    Start a test - simple URL format.
    Same functionality as start_test() but with simpler URL.
    """
    return start_test(test_id)

@test_bp.route('/tests/<int:test_id>/submit', methods=['POST'])
@jwt_required()
def submit_test(test_id):
    """
    Submit test answers and get comprehensive results.
    
    Expected JSON:
    {
        "answers": [
            {
                "question_id": "test_q_1",
                "user_answer": "Option A",
                "time_spent_seconds": 45
            }
        ]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_answers = data.get('answers', [])
        
        test = TestAssessment.query.filter_by(
            id=test_id, user_id=user_id
        ).first()
        
        if not test:
            return jsonify({
                'error': 'Test not found',
                'telugu_message': 'పరీక్ష కనుగొనబడలేదు'
            }), 404
        
        if test.is_completed:
            return jsonify({
                'error': 'Test already completed',
                'telugu_message': 'పరీక్ష ఇప్పటికే పూర్తైంది'
            }), 400
        
        # Process and grade the test
        test_results = _grade_test(test, user_answers)
        
        # Update test record
        test.end_time = datetime.utcnow()
        test.duration_minutes = int((test.end_time - test.start_time).total_seconds() / 60)
        test.user_responses = user_answers
        test.correct_answers = test_results['correct_answers']
        test.score_percentage = test_results['score_percentage']
        test.grade = test_results['grade']
        test.detailed_analysis = test_results['detailed_analysis']
        test.recommendations = test_results['recommendations']
        test.is_completed = True
        
        db.session.commit()
        
        # Update user progress based on test results
        _update_user_progress_from_test(user_id, test, test_results)
        
        return jsonify({
            'message': 'Test submitted successfully!',
            'telugu_message': 'పరీక్ష విజయవంతంగా సమర్పించబడింది!',
            'results': {
                'test_id': test.id,
                'score_percentage': test.score_percentage,
                'grade': test.grade,
                'correct_answers': test.correct_answers,
                'total_questions': test.total_questions,
                'duration_minutes': test.duration_minutes,
                'detailed_analysis': test.detailed_analysis,
                'recommendations': test.recommendations,
                'performance_summary': _generate_performance_summary(test_results)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting test: {str(e)}")
        return jsonify({
            'error': 'Failed to submit test',
            'telugu_message': 'పరీక్ష సమర్పించడంలో విఫలం'
        }), 500

@test_bp.route('/<int:test_id>/submit', methods=['POST'])
@jwt_required()
def submit_test_simple(test_id):
    """
    Submit test answers - simple URL format.
    Same functionality as submit_test() but with simpler URL.
    """
    return submit_test(test_id)

@test_bp.route('/tests/<int:test_id>/results', methods=['GET'])
@jwt_required()
def get_test_results(test_id):
    """
    Get detailed test results and analysis.
    """
    try:
        user_id = int(get_jwt_identity())
        
        test = TestAssessment.query.filter_by(
            id=test_id, user_id=user_id, is_completed=True
        ).first()
        
        if not test:
            return jsonify({
                'error': 'Test not found or not completed',
                'telugu_message': 'పరీక్ష కనుగొనబడలేదు లేదా పూర్తి కాలేదు'
            }), 404
        
        # Get detailed results with question-by-question breakdown
        detailed_results = _get_detailed_test_results(test)
        
        return jsonify({
            'message': 'Test results retrieved successfully!',
            'telugu_message': 'పరీక్ష ఫలితాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'test_results': detailed_results
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting test results: {str(e)}")
        return jsonify({
            'error': 'Failed to get test results',
            'telugu_message': 'పరీక్ష ఫలితాలు పొందడంలో విఫలం'
        }), 500

@test_bp.route('/<int:test_id>/results', methods=['GET'])
@jwt_required()
def get_test_results_simple(test_id):
    """
    Get test results - simple URL format.
    Same functionality as get_test_results() but with simpler URL.
    """
    return get_test_results(test_id)

@test_bp.route('/tests/history', methods=['GET'])
@jwt_required()
def get_test_history():
    """
    Get user's test history with pagination.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        test_type = request.args.get('test_type')
        
        query = TestAssessment.query.filter_by(user_id=user_id, is_completed=True)
        
        if test_type:
            query = query.filter_by(test_type=test_type)
        
        tests = query.order_by(TestAssessment.start_time.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        test_history = []
        for test in tests.items:
            test_info = {
                'id': test.id,
                'test_type': test.test_type,
                'start_time': test.start_time.isoformat(),
                'duration_minutes': test.duration_minutes,
                'score_percentage': test.score_percentage,
                'grade': test.grade,
                'total_questions': test.total_questions,
                'correct_answers': test.correct_answers,
                'chapters_tested': len(test.chapter_ids) if test.chapter_ids else 0
            }
            test_history.append(test_info)
        
        return jsonify({
            'message': 'Test history retrieved successfully!',
            'telugu_message': 'పరీక్ష చరిత్ర విజయవంతంగా తీసుకోబడింది!',
            'test_history': test_history,
            'pagination': {
                'page': tests.page,
                'per_page': tests.per_page,
                'total': tests.total,
                'pages': tests.pages,
                'has_next': tests.has_next,
                'has_prev': tests.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting test history: {str(e)}")
        return jsonify({
            'error': 'Failed to get test history',
            'telugu_message': 'పరీక్ష చరిత్ర పొందడంలో విఫలం'
        }), 500

def _generate_comprehensive_test_questions(user_id, chapters, num_questions, question_types, test_type):
    """
    Generate comprehensive test questions covering multiple chapters.
    """
    try:
        # Get user's learning context for adaptive testing
        learning_context = practice_agent._analyze_user_learning_context(user_id, chapters[0].id)
        
        # Distribute questions across chapters
        questions_per_chapter = max(1, num_questions // len(chapters))
        remaining_questions = num_questions % len(chapters)
        
        all_questions = []
        
        for i, chapter in enumerate(chapters):
            chapter_questions = questions_per_chapter
            if i < remaining_questions:
                chapter_questions += 1
            
            # Generate questions for this chapter
            chapter_question_data = practice_agent.generate_adaptive_practice_questions(
                user_id, chapter.id, chapter_questions, 'test'
            )
            
            # Add chapter context to questions
            for question in chapter_question_data['questions']:
                question['chapter_id'] = chapter.id
                question['chapter_title'] = chapter.title
                question['test_context'] = True
            
            all_questions.extend(chapter_question_data['questions'])
        
        # Shuffle questions for better test experience
        import random
        random.shuffle(all_questions)
        
        # Ensure questions have unique IDs for the test
        for i, question in enumerate(all_questions):
            question['id'] = f"test_{test_type}_{i+1}"
        
        return all_questions
        
    except Exception as e:
        current_app.logger.error(f"Error generating test questions: {str(e)}")
        # Return fallback questions if generation fails
        return _generate_fallback_test_questions(chapters, num_questions)

def _generate_fallback_test_questions(chapters, num_questions):
    """
    Generate fallback test questions if AI generation fails.
    """
    fallback_questions = []
    
    for i in range(num_questions):
        chapter = chapters[i % len(chapters)]
        question = {
            'id': f'test_fallback_{i+1}',
            'type': 'multiple_choice',
            'question_text': f'Test question {i+1} for {chapter.topic}',
            'question_telugu': f'{chapter.topic} కోసం పరీక్ష ప్రశ్న {i+1}',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 'Option A',
            'explanation': f'This is a fallback test question for {chapter.topic}',
            'difficulty': chapter.difficulty_level,
            'skill_tested': 'general',
            'chapter_id': chapter.id,
            'chapter_title': chapter.title
        }
        fallback_questions.append(question)
    
    return fallback_questions

def _grade_test(test, user_answers):
    """
    Grade the test and provide detailed analysis.
    """
    results = {
        'correct_answers': 0,
        'total_questions': test.total_questions,
        'score_percentage': 0,
        'grade': 'F',
        'detailed_analysis': {},
        'recommendations': [],
        'question_results': []
    }
    
    # Create answer lookup
    answer_lookup = {answer['question_id']: answer for answer in user_answers}
    
    # Grade each question
    skill_performance = {}
    chapter_performance = {}
    
    for question in test.questions_data or []:
        question_id = question['id']
        correct_answer = question.get('correct_answer', '')
        user_answer = answer_lookup.get(question_id, {}).get('user_answer', '')
        
        is_correct = _evaluate_test_answer(question, user_answer)
        
        if is_correct:
            results['correct_answers'] += 1
        
        # Track performance by skill
        skill = question.get('skill_tested', 'general')
        if skill not in skill_performance:
            skill_performance[skill] = {'correct': 0, 'total': 0}
        skill_performance[skill]['total'] += 1
        if is_correct:
            skill_performance[skill]['correct'] += 1
        
        # Track performance by chapter
        chapter_id = question.get('chapter_id')
        if chapter_id not in chapter_performance:
            chapter_performance[chapter_id] = {'correct': 0, 'total': 0}
        chapter_performance[chapter_id]['total'] += 1
        if is_correct:
            chapter_performance[chapter_id]['correct'] += 1
        
        # Store question result
        results['question_results'].append({
            'question_id': question_id,
            'is_correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'explanation': question.get('explanation', ''),
            'skill_tested': skill,
            'chapter_id': chapter_id
        })
    
    # Calculate overall score
    if results['total_questions'] > 0:
        results['score_percentage'] = (results['correct_answers'] / results['total_questions']) * 100
    
    # Assign grade
    results['grade'] = _calculate_grade(results['score_percentage'])
    
    # Detailed analysis
    results['detailed_analysis'] = {
        'skill_performance': {
            skill: {
                'score_percentage': (stats['correct'] / stats['total']) * 100,
                'questions_answered': stats['total'],
                'correct_answers': stats['correct']
            } for skill, stats in skill_performance.items()
        },
        'chapter_performance': {
            str(chapter_id): {
                'score_percentage': (stats['correct'] / stats['total']) * 100,
                'questions_answered': stats['total'],
                'correct_answers': stats['correct']
            } for chapter_id, stats in chapter_performance.items()
        }
    }
    
    # Generate recommendations
    results['recommendations'] = _generate_test_recommendations(results)
    
    return results

def _evaluate_test_answer(question, user_answer):
    """
    Evaluate if the user's answer is correct.
    """
    correct_answer = question.get('correct_answer', '').strip().lower()
    user_answer_normalized = user_answer.strip().lower()
    
    # Handle different question types
    question_type = question.get('type', 'multiple_choice')
    
    if question_type == 'multiple_choice':
        return user_answer_normalized == correct_answer
    elif question_type == 'fill_blank':
        # Allow some flexibility for fill-in-the-blank questions
        return user_answer_normalized in correct_answer or correct_answer in user_answer_normalized
    elif question_type == 'translation':
        # For translation, check if key words match
        return _check_translation_match(correct_answer, user_answer_normalized)
    else:
        return user_answer_normalized == correct_answer

def _check_translation_match(correct_answer, user_answer):
    """
    Check if translation answers match with some flexibility.
    """
    # Simple word-based matching - could be enhanced with NLP
    correct_words = set(correct_answer.split())
    user_words = set(user_answer.split())
    
    # Calculate overlap
    overlap = len(correct_words.intersection(user_words))
    total_words = len(correct_words)
    
    # Consider correct if 70% of words match
    return (overlap / total_words) >= 0.7 if total_words > 0 else False

def _calculate_grade(score_percentage):
    """
    Calculate letter grade based on score percentage.
    """
    if score_percentage >= 90:
        return 'A'
    elif score_percentage >= 80:
        return 'B'
    elif score_percentage >= 70:
        return 'C'
    elif score_percentage >= 60:
        return 'D'
    else:
        return 'F'

def _generate_test_recommendations(results):
    """
    Generate personalized recommendations based on test performance.
    """
    recommendations = []
    score = results['score_percentage']
    
    if score >= 90:
        recommendations = [
            'Excellent performance! You can move to more advanced topics.',
            'Consider helping other learners or teaching concepts you know well.',
            'Challenge yourself with advanced practice exercises.'
        ]
    elif score >= 75:
        recommendations = [
            'Good performance! Review any topics where you made mistakes.',
            'Continue practicing regularly to maintain your progress.',
            'Focus on weak areas identified in the detailed analysis.'
        ]
    elif score >= 60:
        recommendations = [
            'Fair performance. Spend more time reviewing chapter content.',
            'Practice more exercises in areas where you scored poorly.',
            'Consider asking for help from AI assistant or tutors.'
        ]
    else:
        recommendations = [
            'Performance needs improvement. Review all chapter content again.',
            'Take more practice sessions before attempting another test.',
            'Focus on fundamental concepts before moving to advanced topics.',
            'Consider studying with additional resources or getting extra help.'
        ]
    
    # Add skill-specific recommendations
    skill_analysis = results['detailed_analysis']['skill_performance']
    for skill, performance in skill_analysis.items():
        if performance['score_percentage'] < 60:
            recommendations.append(f'Focus on improving {skill} skills through targeted practice.')
    
    return recommendations

def _update_user_progress_from_test(user_id, test, test_results):
    """
    Update user chapter progress based on test results.
    """
    try:
        for chapter_id in test.chapter_ids:
            progress = UserChapterProgress.query.filter_by(
                user_id=user_id, chapter_id=chapter_id
            ).first()
            
            if progress:
                # Get chapter-specific performance from test
                chapter_performance = test_results['detailed_analysis']['chapter_performance'].get(str(chapter_id), {})
                chapter_score = chapter_performance.get('score_percentage', 0) / 100
                
                # Update best score if test score is better
                if chapter_score > progress.best_score:
                    progress.best_score = chapter_score
                
                # Update status based on test performance
                chapter = Chapter.query.get(chapter_id)
                if chapter and chapter_score >= chapter.required_score_to_pass:
                    if progress.status in ['not_started', 'in_progress']:
                        progress.status = 'completed'
                        progress.completed_at = datetime.utcnow()
        
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Error updating progress from test: {str(e)}")

def _get_detailed_test_results(test):
    """
    Get comprehensive test results with detailed breakdown.
    """
    return {
        'test_info': {
            'id': test.id,
            'test_type': test.test_type,
            'start_time': test.start_time.isoformat(),
            'end_time': test.end_time.isoformat() if test.end_time else None,
            'duration_minutes': test.duration_minutes
        },
        'overall_performance': {
            'score_percentage': test.score_percentage,
            'grade': test.grade,
            'correct_answers': test.correct_answers,
            'total_questions': test.total_questions
        },
        'detailed_analysis': test.detailed_analysis,
        'recommendations': test.recommendations,
        'question_breakdown': _get_question_breakdown(test),
        'performance_insights': _generate_performance_insights(test)
    }

def _get_question_breakdown(test):
    """
    Get detailed breakdown of each question and answer.
    """
    breakdown = []
    
    answer_lookup = {answer['question_id']: answer for answer in test.user_responses or []}
    
    for question in test.questions_data or []:
        question_id = question['id']
        user_response = answer_lookup.get(question_id, {})
        
        breakdown.append({
            'question_id': question_id,
            'question_text': question['question_text'],
            'user_answer': user_response.get('user_answer', ''),
            'correct_answer': question.get('correct_answer', ''),
            'is_correct': _evaluate_test_answer(question, user_response.get('user_answer', '')),
            'explanation': question.get('explanation', ''),
            'skill_tested': question.get('skill_tested', ''),
            'difficulty': question.get('difficulty', ''),
            'time_spent': user_response.get('time_spent_seconds', 0)
        })
    
    return breakdown

def _generate_performance_insights(test):
    """
    Generate AI-powered insights about test performance.
    """
    try:
        insights_prompt = f"""
        Analyze this English learning test performance for a Telugu speaker:
        
        Test Results:
        - Score: {test.score_percentage:.1f}%
        - Grade: {test.grade}
        - Questions: {test.correct_answers}/{test.total_questions}
        - Duration: {test.duration_minutes} minutes
        
        Provide encouraging insights and specific learning advice in both English and Telugu.
        Focus on strengths, areas for improvement, and next steps.
        """
        
        response = activity_service.model.generate_content(insights_prompt)
        return response.text.strip()
        
    except Exception as e:
        return "Test completed successfully. Continue practicing to improve your English skills!"

def _get_test_instructions(test_type):
    """
    Get instructions for different test types.
    """
    instructions = {
        'chapter_test': {
            'english': 'Answer all questions based on the chapter content. Take your time and read each question carefully.',
            'telugu': 'అధ్యాయ కంటెంట్ ఆధారంగా అన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి. సమయం తీసుకుని ప్రతి ప్రశ్నను జాగ్రత్తగా చదవండి.'
        },
        'comprehensive_test': {
            'english': 'This test covers multiple chapters. Demonstrate your overall understanding of the topics.',
            'telugu': 'ఈ పరీక్ష అనేక అధ్యాయాలను కవర్ చేస్తుంది. విషయాలపై మీ మొత్తం అవగాహనను ప్రదర్శించండి.'
        },
        'placement_test': {
            'english': 'This placement test will determine your current English level. Answer honestly to get accurate results.',
            'telugu': 'ఈ ప్లేస్‌మెంట్ టెస్ట్ మీ ప్రస్తుత ఇంగ్లీష్ స్థాయిని నిర్ణయిస్తుంది. ఖచ్చితమైన ఫలితాలను పొందడానికి నిజాయితీగా సమాధానం ఇవ్వండి.'
        }
    }
    
    return instructions.get(test_type, instructions['chapter_test'])

def _generate_performance_summary(test_results):
    """
    Generate a summary of test performance.
    """
    score = test_results['score_percentage']
    grade = test_results['grade']
    
    if score >= 90:
        summary = {
            'level': 'Excellent',
            'message': 'Outstanding performance! You have excellent command of the material.',
            'telugu_message': 'అద్భుతమైన ప్రదర్శన! మీకు అంశంపై అద్భుతమైన పట్టు ఉంది.',
            'next_steps': 'Ready for advanced topics'
        }
    elif score >= 75:
        summary = {
            'level': 'Good',
            'message': 'Good performance! You understand most concepts well.',
            'telugu_message': 'మంచి ప్రదర్శన! మీరు చాలా భావనలను బాగా అర్థం చేసుకున్నారు.',
            'next_steps': 'Review mistakes and continue to next level'
        }
    elif score >= 60:
        summary = {
            'level': 'Fair',
            'message': 'Fair performance. Some areas need more practice.',
            'telugu_message': 'సరైన ప్రదర్శన. కొన్ని ప్రాంతాలకు మరింత అభ్యాసం అవసరం.',
            'next_steps': 'Focus on weak areas before advancing'
        }
    else:
        summary = {
            'level': 'Needs Improvement',
            'message': 'Performance needs improvement. Review the material again.',
            'telugu_message': 'ప్రదర్శనలో మెరుగుదల అవసరం. మెటీరియల్‌ను మళ్లీ సమీక్షించండి.',
            'next_steps': 'Comprehensive review and additional practice needed'
        }
    
    return summary