from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, Chapter, UserChapterProgress, PracticeSession, 
    UserNotes, TestAssessment, AIConversationContext
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.services.personalization_service import PersonalizationService
from datetime import datetime
import json

practice_bp = Blueprint('practice', __name__)
activity_service = ActivityGeneratorService()
personalization_service = PersonalizationService()

@practice_bp.route('/generate-questions', methods=['POST'])
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
        
        topic = data.get('topic', 'general')
        difficulty = data.get('difficulty', 'beginner')
        num_questions = data.get('num_questions', 5)
        question_types = data.get('question_types', ['multiple_choice'])
        language_focus = data.get('language_focus', 'vocabulary')
        
        # Get user profile for personalization
        user = User.query.get(user_id)
        user_proficiency = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Validate inputs
        if num_questions > 20:
            return jsonify({
                'error': 'Maximum 20 questions allowed per request',
                'telugu_message': 'ప్రతి అభ్యర్థనకు గరిష్టంగా 20 ప్రశ్నలు అనుమతించబడతాయి'
            }), 400
        
        valid_types = ['multiple_choice', 'fill_blank', 'translation', 'true_false', 'matching']
        if not all(qtype in valid_types for qtype in question_types):
            return jsonify({
                'error': f'Invalid question types. Valid types: {", ".join(valid_types)}',
                'telugu_message': 'చెల్లని ప్రశ్న రకాలు'
            }), 400
        
        # Generate questions using AI
        questions = []
        for i in range(num_questions):
            question_type = question_types[i % len(question_types)]
            
            # Create context-specific prompt
            prompt = f"""
            Generate a {question_type} question for Telugu speakers learning English.
            
            Context:
            - Topic: {topic}
            - Difficulty: {difficulty}
            - User proficiency: {user_proficiency}
            - Language focus: {language_focus}
            
            Requirements:
            - Question should be appropriate for {difficulty} level
            - Include Telugu translations where helpful
            - Focus on {language_focus} skills
            - Make it engaging and practical
            
            Return JSON format:
            {{
                "question_id": "q_{i+1}",
                "type": "{question_type}",
                "question": "Question text here",
                "telugu_question": "Telugu translation if needed",
                "options": ["A", "B", "C", "D"] (for multiple choice),
                "correct_answer": "B",
                "explanation": "Why this answer is correct",
                "telugu_explanation": "Telugu explanation",
                "difficulty_level": "{difficulty}",
                "topic": "{topic}",
                "points": 10
            }}
            """
            
            try:
                ai_response = activity_service.model.generate_content(prompt)
                question_data = activity_service._extract_json_from_response(ai_response.text)
                
                # Ensure question has proper structure
                if 'question' in question_data and 'correct_answer' in question_data:
                    question_data['question_id'] = f"q_{i+1}"
                    question_data['type'] = question_type
                    question_data['topic'] = topic
                    question_data['difficulty_level'] = difficulty
                    questions.append(question_data)
                else:
                    # Fallback question if AI generation fails
                    fallback_question = {
                        "question_id": f"q_{i+1}",
                        "type": "multiple_choice",
                        "question": f"What is a common {topic} phrase in English?",
                        "telugu_question": f"ఆంగ్లంలో సాధారణ {topic} వాక్యం ఏది?",
                        "options": ["Hello", "Goodbye", "Thank you", "Please"],
                        "correct_answer": "Hello",
                        "explanation": "Hello is the most common greeting in English",
                        "telugu_explanation": "హలో అనేది ఆంగ్లంలో అత్యంత సాధారణ నమస్కారం",
                        "difficulty_level": difficulty,
                        "topic": topic,
                        "points": 10
                    }
                    questions.append(fallback_question)
                    
            except Exception as e:
                current_app.logger.warning(f"AI question generation failed for question {i+1}: {str(e)}")
                # Add fallback question
                fallback_question = {
                    "question_id": f"q_{i+1}",
                    "type": "multiple_choice",
                    "question": f"Choose the correct {language_focus} for {topic}:",
                    "telugu_question": f"{topic} కోసం సరైన {language_focus} ను ఎంచుకోండి:",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": "This is the correct answer",
                    "telugu_explanation": "ఇది సరైన సమాధానం",
                    "difficulty_level": difficulty,
                    "topic": topic,
                    "points": 10
                }
                questions.append(fallback_question)
        
        return jsonify({
            'message': 'Questions generated successfully!',
            'telugu_message': 'ప్రశ్నలు విజయవంతంగా రూపొందించబడ్డాయి!',
            'questions': questions,
            'metadata': {
                'total_questions': len(questions),
                'topic': topic,
                'difficulty': difficulty,
                'question_types': question_types,
                'language_focus': language_focus,
                'estimated_time': len(questions) * 2,  # 2 minutes per question
                'points_possible': sum(q.get('points', 10) for q in questions)
            },
            'instructions': {
                'english': f"Complete {len(questions)} questions about {topic}. Take your time and read carefully.",
                'telugu': f"{topic} గురించి {len(questions)} ప్రశ్నలను పూర్తి చేయండి. మీ సమయం తీసుకోండి మరియు జాగ్రత్తగా చదవండి."
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating questions: {str(e)}")
        return jsonify({
            'error': 'Failed to generate questions',
            'telugu_message': 'ప్రశ్నలు రూపొందించడంలో విఫలం'
        }), 500

@practice_bp.route('/submit-answer', methods=['POST'])
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
        
        question_id = data.get('question_id')
        question_type = data.get('question_type')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer')
        question_text = data.get('question_text', '')
        options = data.get('options', [])
        
        if not all([question_id, question_type, user_answer is not None, correct_answer]):
            return jsonify({
                'error': 'Missing required fields: question_id, question_type, user_answer, correct_answer',
                'telugu_message': 'అవసరమైన ఫీల్డ్‌లు లేవు'
            }), 400
        
        # Evaluate the answer
        is_correct = False
        score = 0
        
        if question_type == 'multiple_choice':
            is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
            score = 10 if is_correct else 0
        elif question_type == 'fill_blank':
            # For fill in the blank, be more lenient with matching
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(correct_answer).strip().lower()
            is_correct = user_clean == correct_clean or user_clean in correct_clean
            score = 10 if is_correct else 0
        elif question_type == 'translation':
            # For translation, use fuzzy matching
            user_clean = str(user_answer).strip().lower()
            correct_clean = str(correct_answer).strip().lower()
            # Simple fuzzy matching - check if most words match
            user_words = set(user_clean.split())
            correct_words = set(correct_clean.split())
            if len(correct_words) > 0:
                match_ratio = len(user_words.intersection(correct_words)) / len(correct_words)
                is_correct = match_ratio >= 0.7  # 70% word match threshold
                score = int(10 * match_ratio) if match_ratio >= 0.7 else 0
            else:
                is_correct = user_clean == correct_clean
                score = 10 if is_correct else 0
        elif question_type == 'true_false':
            user_bool = str(user_answer).strip().lower() in ['true', 'yes', '1', 'correct']
            correct_bool = str(correct_answer).strip().lower() in ['true', 'yes', '1', 'correct']
            is_correct = user_bool == correct_bool
            score = 10 if is_correct else 0
        else:
            # Default exact match for other types
            is_correct = str(user_answer).strip().lower() == str(correct_answer).strip().lower()
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
            ai_response = activity_service.model.generate_content(feedback_prompt)
            feedback_data = activity_service._extract_json_from_response(ai_response.text)
        except Exception as e:
            current_app.logger.warning(f"AI feedback generation failed: {str(e)}")
            # Fallback feedback
            if is_correct:
                feedback_data = {
                    "feedback": "Correct! Well done!",
                    "telugu_feedback": "సరైనది! బాగా చేసారు!",
                    "tip": "Keep practicing to build confidence",
                    "telugu_tip": "ఆత్మవిశ్వాసం పెంచుకోవడానికి అభ్యసించడం కొనసాగించండి"
                }
            else:
                feedback_data = {
                    "feedback": f"Not quite right. The correct answer is '{correct_answer}'. Try again!",
                    "telugu_feedback": f"పూర్తిగా సరైనది కాదు. సరైన సమాధానం '{correct_answer}'. మళ్లీ ప్రయత్నించండి!",
                    "tip": "Read the question carefully before answering",
                    "telugu_tip": "సమాధానం ఇవ్వడానికి ముందు ప్రశ్నను జాగ్రత్తగా చదవండి"
                }
        
        # Calculate performance metrics
        response_time = data.get('response_time', 0)  # Optional field
        difficulty_level = data.get('difficulty_level', 'beginner')
        
        # Store the practice interaction (you might want to create a model for this)
        practice_data = {
            'user_id': user_id,
            'question_id': question_id,
            'question_type': question_type,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'score': score,
            'response_time': response_time,
            'difficulty_level': difficulty_level,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log the practice interaction
        current_app.logger.info(f"Practice answer submitted: {practice_data}")
        
        return jsonify({
            'message': 'Answer submitted successfully!',
            'telugu_message': 'సమాధానం విజయవంతంగా సమర్పించబడింది!',
            'result': {
                'question_id': question_id,
                'is_correct': is_correct,
                'score': score,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'percentage': (score / 10) * 100
            },
            'feedback': feedback_data.get('feedback', 'Good effort!'),
            'telugu_feedback': feedback_data.get('telugu_feedback', 'మంచి ప్రయత్నం!'),
            'tip': feedback_data.get('tip', 'Keep practicing!'),
            'telugu_tip': feedback_data.get('telugu_tip', 'అభ్యసించడం కొనసాగించండి!'),
            'performance': {
                'response_time': response_time,
                'difficulty_level': difficulty_level,
                'score_percentage': (score / 10) * 100
            },
            'encouragement': {
                'english': "Great job practicing! Every answer helps you improve.",
                'telugu': "అభ్యసించినందుకు అద్భుతం! ప్రతి సమాధానం మిమ్మల్ని మెరుగుపరచుతుంది."
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error submitting answer: {str(e)}")
        return jsonify({
            'error': 'Failed to submit answer',
            'telugu_message': 'సమాధానం సమర్పించడంలో విఫలం'
        }), 500

@practice_bp.route('/<int:session_id>/complete', methods=['POST'])
@jwt_required()
def complete_session_simple(session_id):
    """
    Complete a practice session - simple URL format.
    Same functionality as complete_practice_session() but with simpler URL.
    """
    return complete_practice_session(session_id)

@practice_bp.route('/practice/<int:session_id>/generate-questions', methods=['POST'])
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
        
        num_questions = data.get('num_questions', 5)
        question_types = data.get('question_types', ['multiple_choice'])
        
        # Get practice session
        session = PracticeSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()
        
        if not session:
            return jsonify({
                'error': 'Practice session not found',
                'telugu_message': 'అభ్యాస సెషన్ కనుగొనబడలేదు'
            }), 404
        
        if session.is_completed:
            return jsonify({
                'error': 'Practice session already completed',
                'telugu_message': 'అభ్యాస సెషన్ ఇప్పటికే పూర్తయింది'
            }), 400
        
        # Get chapter information
        chapter = Chapter.query.get(session.chapter_id)
        if not chapter:
            return jsonify({
                'error': 'Chapter not found',
                'telugu_message': 'అధ్యాయం కనుగొనబడలేదు'
            }), 404
        
        # Get user's previous performance in this chapter
        user_progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=session.chapter_id
        ).first()
        
        # Determine difficulty based on user's previous scores
        difficulty_level = _determine_adaptive_difficulty(user_progress, chapter.difficulty_level)
        
        # Generate questions using AI based on chapter content and user history
        questions = _generate_adaptive_questions(
            chapter, user_progress, num_questions, question_types, difficulty_level
        )
        
        # Store questions in session
        session.questions_data = questions
        session.total_questions = len(questions)
        db.session.commit()
        
        return jsonify({
            'message': 'Practice questions generated successfully!',
            'telugu_message': 'అభ్యాస ప్రశ్నలు విజయవంతంగా రూపొందించబడ్డాయి!',
            'questions': questions,
            'session_info': {
                'id': session.id,
                'total_questions': session.total_questions,
                'difficulty_level': difficulty_level
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating questions: {str(e)}")
        return jsonify({
            'error': 'Failed to generate questions',
            'telugu_message': 'ప్రశ్నలు రూపొందించడంలో విఫలం'
        }), 500

@practice_bp.route('/practice/<int:session_id>/submit-answer', methods=['POST'])
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
        
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        time_spent = data.get('time_spent_seconds', 0)
        
        if not question_id or not user_answer:
            return jsonify({
                'error': 'Question ID and answer are required',
                'telugu_message': 'ప్రశ్న ID మరియు సమాధానం అవసరం'
            }), 400
        
        # Get practice session
        session = PracticeSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()
        
        if not session:
            return jsonify({
                'error': 'Practice session not found',
                'telugu_message': 'అభ్యాస సెషన్ కనుగొనబడలేదు'
            }), 404
        
        # Find the question in session data
        questions = session.questions_data or []
        question = None
        for q in questions:
            if q.get('id') == question_id:
                question = q
                break
        
        if not question:
            return jsonify({
                'error': 'Question not found',
                'telugu_message': 'ప్రశ్న కనుగొనబడలేదు'
            }), 404
        
        # Evaluate the answer
        is_correct, feedback = _evaluate_answer(question, user_answer)
        
        # Store user response
        user_responses = session.user_responses or []
        response_data = {
            'question_id': question_id,
            'user_answer': user_answer,
            'correct_answer': question.get('correct_answer'),
            'is_correct': is_correct,
            'time_spent_seconds': time_spent,
            'feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        }
        user_responses.append(response_data)
        session.user_responses = user_responses
        
        # Update session statistics
        if is_correct:
            session.correct_answers = (session.correct_answers or 0) + 1
        
        # Calculate current score
        total_answered = len(user_responses)
        session.score_percentage = (session.correct_answers / total_answered) * 100 if total_answered > 0 else 0
        
        db.session.commit()
        
        return jsonify({
            'message': 'Answer submitted successfully!',
            'telugu_message': 'సమాధానం విజయవంతంగా సమర్పించబడింది!',
            'result': {
                'is_correct': is_correct,
                'feedback': feedback,
                'correct_answer': question.get('correct_answer'),
                'explanation': question.get('explanation'),
                'current_score': session.score_percentage,
                'questions_answered': total_answered,
                'questions_remaining': session.total_questions - total_answered
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting answer: {str(e)}")
        return jsonify({
            'error': 'Failed to submit answer',
            'telugu_message': 'సమాధానం సమర్పించడంలో విఫలం'
        }), 500

@practice_bp.route('/practice/<int:session_id>/complete', methods=['POST'])
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
            return jsonify({
                'error': 'Practice session not found',
                'telugu_message': 'అభ్యాస సెషన్ కనుగొనబడలేదు'
            }), 404
        
        if session.is_completed:
            return jsonify({
                'error': 'Session already completed',
                'telugu_message': 'సెషన్ ఇప్పటికే పూర్తయింది'
            }), 400
        
        # Complete the session
        session.end_time = datetime.utcnow()
        session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
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
                    (progress.average_score * (progress.total_attempts - 1)) + session.score_percentage
                ) / progress.total_attempts
            
            # Update time spent
            progress.time_spent_minutes += session.duration_minutes
            
            # Update status based on score
            chapter = Chapter.query.get(session.chapter_id)
            if chapter and session.score_percentage >= (chapter.required_score_to_pass * 100):
                if progress.status in ['not_started', 'in_progress']:
                    progress.status = 'completed'
                    progress.completed_at = datetime.utcnow()
                elif session.score_percentage >= 90:  # Mastered if 90%+
                    progress.status = 'mastered'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Practice session completed successfully!',
            'telugu_message': 'అభ్యాస సెషన్ విజయవంతంగా పూర్తైంది!',
            'session_results': {
                'session_id': session.id,
                'score_percentage': session.score_percentage,
                'total_questions': session.total_questions,
                'correct_answers': session.correct_answers,
                'duration_minutes': session.duration_minutes,
                'session_summary': session_summary,
                'progress_updated': {
                    'status': progress.status if progress else 'unknown',
                    'best_score': progress.best_score if progress else 0,
                    'total_attempts': progress.total_attempts if progress else 0
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing session: {str(e)}")
        return jsonify({
            'error': 'Failed to complete session',
            'telugu_message': 'సెషన్ పూర్తి చేయడంలో విఫలం'
        }), 500

def _determine_adaptive_difficulty(user_progress, default_difficulty):
    """
    Determine adaptive difficulty based on user's previous performance.
    """
    if not user_progress:
        return default_difficulty
    
    avg_score = user_progress.average_score
    
    if avg_score >= 0.85:  # 85%+ - increase difficulty
        difficulty_levels = ['beginner', 'intermediate', 'advanced']
        current_index = difficulty_levels.index(default_difficulty)
        return difficulty_levels[min(current_index + 1, len(difficulty_levels) - 1)]
    elif avg_score <= 0.6:  # 60%- - decrease difficulty
        difficulty_levels = ['beginner', 'intermediate', 'advanced']
        current_index = difficulty_levels.index(default_difficulty)
        return difficulty_levels[max(current_index - 1, 0)]
    
    return default_difficulty

def _generate_adaptive_questions(chapter, user_progress, num_questions, question_types, difficulty_level):
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
            'chapter_topic': chapter.topic,
            'chapter_subtopics': chapter.subtopics,
            'difficulty_level': difficulty_level,
            'user_weak_areas': weak_areas,
            'previous_average_score': user_progress.average_score if user_progress else 0,
            'question_types': question_types
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
        
        response = activity_service.model.generate_content(prompt)
        questions_data = activity_service._extract_json_from_response(response.text)
        
        return questions_data.get('questions', [])
        
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
    return ['vocabulary', 'grammar', 'sentence_structure']

def _get_fallback_questions(chapter, num_questions, question_types):
    """
    Generate fallback questions if AI generation fails.
    """
    return [
        {
            'id': f'fallback_{i}',
            'type': 'multiple_choice',
            'question_text': f'Practice question {i+1} for {chapter.topic}',
            'question_telugu': f'{chapter.topic} కోసం అభ్యాస ప్రశ్న {i+1}',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct_answer': 'Option A',
            'explanation': 'This is a fallback question',
            'difficulty': chapter.difficulty_level,
            'skill_tested': 'general'
        } for i in range(num_questions)
    ]

def _evaluate_answer(question, user_answer):
    """
    Evaluate user's answer and provide feedback.
    """
    correct_answer = question.get('correct_answer', '').strip().lower()
    user_answer_normalized = user_answer.strip().lower()
    
    # Simple exact match for now - could be enhanced with fuzzy matching
    is_correct = user_answer_normalized == correct_answer
    
    if is_correct:
        feedback = {
            'message': 'Correct! Well done!',
            'telugu_message': 'సరైనది! బాగా చేసారు!',
            'type': 'success'
        }
    else:
        feedback = {
            'message': f'Incorrect. The correct answer is: {question.get("correct_answer")}',
            'telugu_message': f'తప్పు. సరైన సమాధానం: {question.get("correct_answer")}',
            'explanation': question.get('explanation', ''),
            'type': 'error'
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
        
        response = activity_service.model.generate_content(prompt)
        return {
            'ai_summary': response.text.strip(),
            'score_analysis': _analyze_score_performance(session.score_percentage),
            'recommendations': _get_performance_recommendations(session.score_percentage)
        }
        
    except Exception as e:
        current_app.logger.error(f"Error generating session summary: {str(e)}")
        return {
            'ai_summary': 'Session completed successfully!',
            'score_analysis': 'Performance recorded.',
            'recommendations': ['Continue practicing regularly.']
        }

def _analyze_score_performance(score_percentage):
    """
    Analyze score performance and provide categorized feedback.
    """
    if score_percentage >= 90:
        return 'Excellent performance! You have mastered this chapter.'
    elif score_percentage >= 75:
        return 'Good performance! You understand most concepts well.'
    elif score_percentage >= 60:
        return 'Fair performance. Some concepts need more practice.'
    else:
        return 'Needs improvement. Consider reviewing the chapter content again.'

def _get_performance_recommendations(score_percentage):
    """
    Get performance-based recommendations.
    """
    if score_percentage >= 90:
        return [
            'Move to the next chapter',
            'Help other learners in community forums',
            'Try advanced practice exercises'
        ]
    elif score_percentage >= 75:
        return [
            'Review any incorrect answers',
            'Practice similar questions',
            'Move to next chapter when ready'
        ]
    elif score_percentage >= 60:
        return [
            'Review chapter content again',
            'Focus on areas where you made mistakes',
            'Take more practice sessions before moving on'
        ]
    else:
        return [
            'Re-read the chapter content carefully',
            'Ask for help from AI assistant',
            'Take additional practice sessions',
            'Consider reviewing prerequisite chapters'
        ]