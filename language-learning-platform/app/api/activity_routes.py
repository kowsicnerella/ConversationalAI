
from flask import Blueprint, request, jsonify
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db, Activity, LearningPath
import base64
import io
from PIL import Image

activity_bp = Blueprint('activity', __name__)
activity_service = ActivityGeneratorService()

@activity_bp.route('/generate/quiz', methods=['POST'])
def generate_quiz():
    """Generate a quiz activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        quiz_content = activity_service.generate_quiz(topic, level)
        
        if 'error' in quiz_content:
            return jsonify({'error': 'Failed to generate quiz', 'details': quiz_content}), 500
        
        return jsonify({
            'activity_type': 'quiz',
            'topic': topic,
            'level': level,
            'content': quiz_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Quiz generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/flashcards', methods=['POST'])
def generate_flashcards():
    """Generate flashcard activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        flashcard_content = activity_service.generate_flashcards(topic, level)
        
        if 'error' in flashcard_content:
            return jsonify({'error': 'Failed to generate flashcards', 'details': flashcard_content}), 500
        
        return jsonify({
            'activity_type': 'flashcard',
            'topic': topic,
            'level': level,
            'content': flashcard_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Flashcard generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/reading', methods=['POST'])
def generate_reading():
    """Generate reading comprehension activity"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        reading_content = activity_service.generate_text_reading(topic, level)
        
        if 'error' in reading_content:
            return jsonify({'error': 'Failed to generate reading', 'details': reading_content}), 500
        
        return jsonify({
            'activity_type': 'reading',
            'topic': topic,
            'level': level,
            'content': reading_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Reading generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/writing-prompt', methods=['POST'])
def generate_writing_prompt():
    """Generate writing practice prompt"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        prompt_content = activity_service.generate_writing_practice_prompt(topic, level)
        
        if 'error' in prompt_content:
            return jsonify({'error': 'Failed to generate writing prompt', 'details': prompt_content}), 500
        
        return jsonify({
            'activity_type': 'writing',
            'topic': topic,
            'level': level,
            'content': prompt_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Writing prompt generation failed', 'details': str(e)}), 500

@activity_bp.route('/generate/role-play', methods=['POST'])
def generate_role_play():
    """Generate role-playing scenario"""
    try:
        data = request.get_json()
        
        topic = data.get('topic', '').strip()
        level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        if level not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
        
        roleplay_content = activity_service.generate_role_playing_scenario(topic, level)
        
        if 'error' in roleplay_content:
            return jsonify({'error': 'Failed to generate role-play scenario', 'details': roleplay_content}), 500
        
        return jsonify({
            'activity_type': 'role_play',
            'topic': topic,
            'level': level,
            'content': roleplay_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Role-play generation failed', 'details': str(e)}), 500

@activity_bp.route('/analyze-image', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for vocabulary learning"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'Image data is required'}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(data['image'])
            image = Image.open(io.BytesIO(image_data))
        except Exception as e:
            return jsonify({'error': 'Invalid image data', 'details': str(e)}), 400
        
        analysis_content = activity_service.analyze_image_for_learning(image)
        
        if 'error' in analysis_content:
            return jsonify({'error': 'Failed to analyze image', 'details': analysis_content}), 500
        
        return jsonify({
            'activity_type': 'image_recognition',
            'content': analysis_content
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Image analysis failed', 'details': str(e)}), 500

@activity_bp.route('/chat', methods=['POST'])
def chat_with_tutor():
    """Chat with AI English tutor"""
    try:
        data = request.get_json()
        
        user_message = data.get('message', '').strip()
        message_history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        response = activity_service.generate_general_chat_response(message_history, user_message)
        
        return jsonify({
            'activity_type': 'chat',
            'user_message': user_message,
            'tutor_response': response
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Chat failed', 'details': str(e)}), 500

@activity_bp.route('/feedback', methods=['POST'])
def get_writing_feedback():
    """Get feedback on user's English writing"""
    try:
        data = request.get_json()
        
        user_writing = data.get('text', '').strip()
        
        if not user_writing:
            return jsonify({'error': 'Text is required for feedback'}), 400
        
        feedback = activity_service.get_feedback_on_writing(user_writing)
        
        if 'error' in feedback:
            return jsonify({'error': 'Failed to generate feedback', 'details': feedback}), 500
        
        return jsonify({
            'activity_type': 'writing_feedback',
            'original_text': user_writing,
            'feedback': feedback
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Feedback generation failed', 'details': str(e)}), 500

@activity_bp.route('/save', methods=['POST'])
def save_activity():
    """Save a generated activity to a learning path"""
    try:
        data = request.get_json()
        
        required_fields = ['path_id', 'activity_type', 'title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        path_id = data['path_id']
        activity_type = data['activity_type']
        title = data['title'].strip()
        content = data['content']
        difficulty_level = data.get('difficulty_level', 'beginner')
        points_reward = data.get('points_reward', 10)
        estimated_duration = data.get('estimated_duration_minutes', 10)
        
        # Validate learning path exists
        learning_path = LearningPath.query.get(path_id)
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        # Get next order in path
        last_activity = Activity.query.filter_by(path_id=path_id).order_by(Activity.order_in_path.desc()).first()
        order_in_path = (last_activity.order_in_path + 1) if last_activity else 1
        
        # Create activity
        activity = Activity(
            path_id=path_id,
            activity_type=activity_type,
            title=title,
            content=content,
            difficulty_level=difficulty_level,
            order_in_path=order_in_path,
            estimated_duration_minutes=estimated_duration,
            points_reward=points_reward
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Activity saved successfully',
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'order_in_path': activity.order_in_path,
                'created_at': activity.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to save activity', 'details': str(e)}), 500

@activity_bp.route('/path/<int:path_id>', methods=['GET'])
def get_path_activities(path_id):
    """Get all activities in a learning path"""
    try:
        learning_path = LearningPath.query.get(path_id)
        if not learning_path:
            return jsonify({'error': 'Learning path not found'}), 404
        
        activities = Activity.query.filter_by(path_id=path_id).order_by(Activity.order_in_path).all()
        
        activity_list = []
        for activity in activities:
            activity_list.append({
                'id': activity.id,
                'title': activity.title,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'order_in_path': activity.order_in_path,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'content': activity.content
            })
        
        return jsonify({
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'description': learning_path.description
            },
            'activities': activity_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch activities', 'details': str(e)}), 500
