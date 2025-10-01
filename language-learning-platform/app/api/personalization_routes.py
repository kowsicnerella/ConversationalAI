from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.personalization_service import PersonalizationService
from app.models import db, User, LearningSession, VocabularyWord
from datetime import datetime
import logging

personalization_bp = Blueprint('personalization', __name__)
personalization_service = PersonalizationService()

@personalization_bp.route('/goals', methods=['POST'])
@jwt_required()
def set_user_goals():
    """
    Set user's daily learning goals during onboarding.
    
    Expected JSON:
    {
        "daily_time_goal": 15,
        "learning_focus": "conversation"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        daily_time_goal = data.get('daily_time_goal', 10)
        learning_focus = data.get('learning_focus', 'conversation')
        
        # Validate inputs
        if daily_time_goal < 5 or daily_time_goal > 120:
            return jsonify({
                'error': 'Daily time goal must be between 5 and 120 minutes',
                'telugu_message': 'రోజువారీ లక్ష్యం 5 నుండి 120 నిమిషాల మధ్య ఉండాలి'
            }), 400
        
        goal = personalization_service.create_user_goal(user_id, daily_time_goal, learning_focus)
        
        return jsonify({
            'message': 'Goals set successfully!',
            'telugu_message': 'లక్ష్యాలు విజయవంతంగా సెట్ చేయబడ్డాయి!',
            'goal': {
                'daily_time_goal_minutes': goal.daily_time_goal_minutes,
                'learning_focus': goal.learning_focus,
                'created_at': goal.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error setting user goals: {str(e)}")
        return jsonify({
            'error': 'Failed to set goals',
            'telugu_message': 'లక్ష్యాలు సెట్ చేయడంలో విఫలం'
        }), 500

@personalization_bp.route('/assessment/start', methods=['POST'])
@jwt_required()
def start_proficiency_assessment():
    """
    Start the initial proficiency assessment for a user.
    """
    try:
        user_id = int(get_jwt_identity())
        
        assessment_data = personalization_service.conduct_proficiency_assessment(user_id)
        
        return jsonify({
            'message': 'Assessment started successfully!',
            'telugu_message': 'మూల్యాంకనం విజయవంతంగా ప్రారంభమైంది!',
            'assessment': assessment_data
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error starting assessment: {str(e)}")
        return jsonify({
            'error': 'Failed to start assessment',
            'telugu_message': 'మూల్యాంకనం ప్రారంభించడంలో విఫలం'
        }), 500

@personalization_bp.route('/assessment/<int:assessment_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_assessment(assessment_id):
    """
    Submit a response to an assessment question.
    
    Expected JSON:
    {
        "question_id": 1,
        "user_response": "My name is Ram and I am from Hyderabad."
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        question_id = data.get('question_id')
        user_response = data.get('user_response')
        
        if not question_id or not user_response:
            return jsonify({
                'error': 'Question ID and response are required',
                'telugu_message': 'ప్రశ్న ID మరియు సమాధానం అవసరం'
            }), 400
        
        result = personalization_service.evaluate_assessment_response(
            assessment_id, question_id, user_response
        )
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'telugu_message': 'సమాధానం మూల్యాంకనంలో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Response evaluated successfully!',
            'telugu_message': 'సమాధానం విజయవంతంగా మూల్యాంకనం చేయబడింది!',
            'evaluation': result['evaluation'],
            'next_question': result['next_question']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error evaluating assessment response: {str(e)}")
        return jsonify({
            'error': 'Failed to evaluate response',
            'telugu_message': 'సమాధానం మూల్యాంకనంలో విఫలం'
        }), 500

@personalization_bp.route('/assessment/<int:assessment_id>/complete', methods=['POST'])
@jwt_required()
def complete_assessment(assessment_id):
    """
    Complete the proficiency assessment and get final results.
    """
    try:
        user_id = int(get_jwt_identity())
        
        result = personalization_service.finalize_assessment(assessment_id)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'telugu_message': 'మూల్యాంకనం పూర్తి చేయడంలో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Assessment completed successfully!',
            'telugu_message': 'మూల్యాంకనం విజయవంతంగా పూర్తైంది!',
            'results': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error completing assessment: {str(e)}")
        return jsonify({
            'error': 'Failed to complete assessment',
            'telugu_message': 'మూల్యాంకనం పూర్తి చేయడంలో విఫలం'
        }), 500

@personalization_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get personalized dashboard content for the user.
    """
    try:
        user_id = int(get_jwt_identity())
        
        dashboard_data = personalization_service.get_personalized_dashboard(user_id)
        
        if 'error' in dashboard_data:
            return jsonify({
                'error': dashboard_data['error'],
                'telugu_message': 'డాష్‌బోర్డ్ డేటా లభించడంలో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Dashboard data retrieved successfully!',
            'telugu_message': 'డాష్‌బోర్డ్ డేటా విజయవంతంగా తీసుకోబడింది!',
            'dashboard': dashboard_data['dashboard']
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard: {str(e)}")
        return jsonify({
            'error': 'Failed to get dashboard data',
            'telugu_message': 'డాష్‌బోర్డ్ డేటా పొందడంలో విఫలం'
        }), 500

@personalization_bp.route('/session/start', methods=['POST'])
@jwt_required()
def start_session():
    """
    Start a new learning session.
    
    Expected JSON:
    {
        "session_type": "chat"  // "chat", "guided_conversation", "role_play"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        session_type = data.get('session_type', 'chat')
        
        valid_types = ['chat', 'guided_conversation', 'role_play', 'flashcards', 'quiz']
        if session_type not in valid_types:
            return jsonify({
                'error': f'Invalid session type. Must be one of: {valid_types}',
                'telugu_message': 'చెల్లని సెషన్ రకం'
            }), 400
        
        session_data = personalization_service.start_learning_session(user_id, session_type)
        
        if 'error' in session_data:
            return jsonify({
                'error': session_data['error'],
                'telugu_message': 'సెషన్ ప్రారంభించడంలో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Session started successfully!',
            'telugu_message': 'సెషన్ విజయవంతంగా ప్రారంభమైంది!',
            'session': session_data
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error starting session: {str(e)}")
        return jsonify({
            'error': 'Failed to start session',
            'telugu_message': 'సెషన్ ప్రారంభించడంలో విఫలం'
        }), 500

@personalization_bp.route('/session/<int:session_id>/end', methods=['POST'])
@jwt_required()
def end_session(session_id):
    """
    End a learning session and get summary.
    
    Expected JSON:
    {
        "user_satisfaction": 5  // 1-5 rating, optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        user_satisfaction = data.get('user_satisfaction')
        if user_satisfaction and (user_satisfaction < 1 or user_satisfaction > 5):
            return jsonify({
                'error': 'User satisfaction must be between 1 and 5',
                'telugu_message': 'వినియోగదారు సంతృప్తి 1 నుండి 5 మధ్య ఉండాలి'
            }), 400
        
        # Verify session belongs to user
        session = LearningSession.query.filter_by(id=session_id, user_id=user_id).first()
        if not session:
            return jsonify({
                'error': 'Session not found or access denied',
                'telugu_message': 'సెషన్ కనుగొనబడలేదు లేదా అనుమతి లేదు'
            }), 404
        
        session_summary = personalization_service.end_learning_session(session_id, user_satisfaction)
        
        if 'error' in session_summary:
            return jsonify({
                'error': session_summary['error'],
                'telugu_message': 'సెషన్ ముగించడంలో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Session ended successfully!',
            'telugu_message': 'సెషన్ విజయవంతంగా ముగిసింది!',
            'summary': session_summary
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error ending session: {str(e)}")
        return jsonify({
            'error': 'Failed to end session',
            'telugu_message': 'సెషన్ ముగించడంలో విఫలం'
        }), 500

@personalization_bp.route('/vocabulary/track', methods=['POST'])
@jwt_required()
def track_vocabulary():
    """
    Track vocabulary learning during a session.
    
    Expected JSON:
    {
        "english_word": "beautiful",
        "context_sentence": "The sunset is beautiful.",
        "session_id": 123  // optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        english_word = data.get('english_word')
        context_sentence = data.get('context_sentence')
        session_id = data.get('session_id')
        
        if not english_word or not context_sentence:
            return jsonify({
                'error': 'English word and context sentence are required',
                'telugu_message': 'ఇంగ్లీష్ పదం మరియు సందర్భ వాక్యం అవసరం'
            }), 400
        
        vocab_data = personalization_service.track_vocabulary_learning(
            user_id, english_word, context_sentence, session_id
        )
        
        if 'error' in vocab_data:
            return jsonify({
                'error': vocab_data['error'],
                'telugu_message': 'పదజాలం ట్రాకింగ్‌లో లోపం'
            }), 400
        
        return jsonify({
            'message': 'Vocabulary tracked successfully!',
            'telugu_message': 'పదజాలం విజయవంతంగా ట్రాక్ చేయబడింది!',
            'vocabulary': vocab_data
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error tracking vocabulary: {str(e)}")
        return jsonify({
            'error': 'Failed to track vocabulary',
            'telugu_message': 'పదజాలం ట్రాక్ చేయడంలో విఫలం'
        }), 500

@personalization_bp.route('/vocabulary', methods=['GET'])
@jwt_required()
def get_user_vocabulary():
    """
    Get user's learned vocabulary with pagination.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        vocabulary = VocabularyWord.query.filter_by(user_id=user_id)\
            .order_by(VocabularyWord.discovered_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'message': 'Vocabulary retrieved successfully!',
            'telugu_message': 'పదజాలం విజయవంతంగా తీసుకోబడింది!',
            'vocabulary': [
                {
                    'id': word.id,
                    'english_word': word.english_word,
                    'telugu_translation': word.telugu_translation,
                    'context_sentence': word.context_sentence,
                    'times_encountered': word.times_encountered,
                    'mastery_level': word.mastery_level,
                    'discovered_at': word.discovered_at.isoformat()
                } for word in vocabulary.items
            ],
            'pagination': {
                'page': vocabulary.page,
                'per_page': vocabulary.per_page,
                'total': vocabulary.total,
                'pages': vocabulary.pages,
                'has_next': vocabulary.has_next,
                'has_prev': vocabulary.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting vocabulary: {str(e)}")
        return jsonify({
            'error': 'Failed to get vocabulary',
            'telugu_message': 'పదజాలం పొందడంలో విఫలం'
        }), 500

@personalization_bp.route('/vocabulary/<int:vocab_id>/practice', methods=['POST'])
@jwt_required()
def practice_vocabulary_word(vocab_id):
    """
    Mark a vocabulary word as practiced and update mastery level.
    
    Expected JSON:
    {
        "correct": true,  // whether user got it right
        "practice_type": "flashcard"  // "flashcard", "quiz", "conversation"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        correct = data.get('correct', False)
        practice_type = data.get('practice_type', 'flashcard')
        
        # Verify word belongs to user
        vocab_word = VocabularyWord.query.filter_by(id=vocab_id, user_id=user_id).first()
        if not vocab_word:
            return jsonify({
                'error': 'Vocabulary word not found',
                'telugu_message': 'పదజాలం పదం కనుగొనబడలేదు'
            }), 404
        
        # Update practice statistics
        vocab_word.times_practiced += 1
        vocab_word.last_practiced = datetime.utcnow()
        
        if correct:
            vocab_word.times_correct += 1
        
        # Update mastery level based on performance
        success_rate = vocab_word.times_correct / vocab_word.times_practiced
        if success_rate >= 0.8 and vocab_word.times_practiced >= 3:
            vocab_word.mastery_level = 'mastered'
        elif success_rate >= 0.6:
            vocab_word.mastery_level = 'learning'
        else:
            vocab_word.mastery_level = 'new'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Vocabulary practice recorded!',
            'telugu_message': 'పదజాలం అభ్యాసం రికార్డ్ చేయబడింది!',
            'vocabulary': {
                'english_word': vocab_word.english_word,
                'telugu_translation': vocab_word.telugu_translation,
                'mastery_level': vocab_word.mastery_level,
                'success_rate': round(success_rate * 100, 1),
                'times_practiced': vocab_word.times_practiced
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error recording vocabulary practice: {str(e)}")
        return jsonify({
            'error': 'Failed to record practice',
            'telugu_message': 'అభ్యాసం రికార్డ్ చేయడంలో విఫలం'
        }), 500