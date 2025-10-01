from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import db, User, LearningSession
from app.services.activity_generator_service import ActivityGeneratorService
import os
import uuid
from datetime import datetime
from PIL import Image
import io

media_bp = Blueprint('media', __name__)
activity_service = ActivityGeneratorService()

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    return upload_folder

@media_bp.route('/upload/image', methods=['POST'])
@jwt_required()
def upload_image():
    """
    Upload an image for vocabulary learning or visual exercises.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if file is present
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image file provided',
                'telugu_message': 'చిత్రం ఫైల్ అందించబడలేదు'
            }), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'error': 'No image file selected',
                'telugu_message': 'చిత్రం ఫైల్ ఎంచుకోబడలేదు'
            }), 400
        
        # Validate file type
        image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not allowed_file(file.filename, image_extensions):
            return jsonify({
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP',
                'telugu_message': 'చెల్లని ఫైల్ రకం. అనుమతించబడినవి: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
        
        # Create upload directory
        upload_folder = create_upload_folder()
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(upload_folder, unique_filename)
        
        # Process and save image
        try:
            # Open and process image with PIL
            image = Image.open(file.stream)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 1024x1024)
            max_size = (1024, 1024)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            image.save(filepath, optimize=True, quality=85)
            
        except Exception as img_error:
            current_app.logger.error(f"Image processing error: {str(img_error)}")
            return jsonify({
                'error': 'Failed to process image',
                'telugu_message': 'చిత్రం ప్రాసెసింగ్‌లో విఫలం'
            }), 400
        
        # Get image analysis for vocabulary learning
        analysis_result = None
        try:
            # Use the activity service to analyze the image
            learning_type = request.form.get('learning_type', 'vocabulary')
            analysis_result = activity_service.analyze_image_for_learning(
                filepath, learning_type
            )
        except Exception as analysis_error:
            current_app.logger.warning(f"Image analysis failed: {str(analysis_error)}")
            analysis_result = {
                'vocabulary_words': ['image', 'picture', 'photo'],
                'description': 'An uploaded image for learning',
                'learning_suggestions': ['Describe what you see in the image', 'Practice naming objects']
            }
        
        # Store file info in database (you might want to create a MediaFile model)
        file_info = {
            'user_id': user_id,
            'filename': unique_filename,
            'original_filename': secure_filename(file.filename),
            'file_type': 'image',
            'file_size': os.path.getsize(filepath),
            'upload_time': datetime.utcnow().isoformat(),
            'analysis_result': analysis_result
        }
        
        return jsonify({
            'message': 'Image uploaded successfully!',
            'telugu_message': 'చిత్రం విజయవంతంగా అప్‌లోడ్ చేయబడింది!',
            'file_info': file_info,
            'learning_content': analysis_result,
            'image_url': f'/api/media/files/{unique_filename}'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading image: {str(e)}")
        return jsonify({
            'error': 'Failed to upload image',
            'telugu_message': 'చిత్రం అప్‌లోడ్ చేయడంలో విఫలం'
        }), 500

@media_bp.route('/upload/audio', methods=['POST'])
@jwt_required()
def upload_audio():
    """
    Upload an audio file for pronunciation practice or speech recognition.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if file is present
        if 'audio' not in request.files:
            return jsonify({
                'error': 'No audio file provided',
                'telugu_message': 'ఆడియో ఫైల్ అందించబడలేదు'
            }), 400
        
        file = request.files['audio']
        if file.filename == '':
            return jsonify({
                'error': 'No audio file selected',
                'telugu_message': 'ఆడియో ఫైల్ ఎంచుకోబడలేదు'
            }), 400
        
        # Validate file type
        audio_extensions = {'wav', 'mp3', 'ogg', 'webm', 'm4a'}
        if not allowed_file(file.filename, audio_extensions):
            return jsonify({
                'error': 'Invalid file type. Allowed: WAV, MP3, OGG, WEBM, M4A',
                'telugu_message': 'చెల్లని ఫైల్ రకం. అనుమతించబడినవి: WAV, MP3, OGG, WEBM, M4A'
            }), 400
        
        # Create upload directory
        upload_folder = create_upload_folder()
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        filepath = os.path.join(upload_folder, unique_filename)
        
        # Save audio file
        file.save(filepath)
        
        # Get pronunciation analysis type
        analysis_type = request.form.get('analysis_type', 'pronunciation')
        target_text = request.form.get('target_text', '')
        
        # Mock pronunciation analysis (in real implementation, use speech recognition API)
        analysis_result = {
            'analysis_type': analysis_type,
            'target_text': target_text,
            'confidence_score': 0.85,  # Mock score
            'pronunciation_feedback': {
                'overall_score': 85,
                'clarity': 'Good',
                'pace': 'Appropriate',
                'suggestions': [
                    'Work on consonant sounds',
                    'Practice word stress patterns'
                ]
            },
            'transcribed_text': target_text,  # In real implementation, this would be from speech recognition
            'detected_language': 'en',
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        # For actual implementation, you would integrate with:
        # - Google Speech-to-Text API
        # - Azure Speech Services
        # - AWS Transcribe
        # - Or similar speech recognition services
        
        file_info = {
            'user_id': user_id,
            'filename': unique_filename,
            'original_filename': secure_filename(file.filename),
            'file_type': 'audio',
            'file_size': os.path.getsize(filepath),
            'upload_time': datetime.utcnow().isoformat(),
            'analysis_result': analysis_result
        }
        
        return jsonify({
            'message': 'Audio uploaded and analyzed successfully!',
            'telugu_message': 'ఆడియో విజయవంతంగా అప్‌లోడ్ మరియు విశ్లేషించబడింది!',
            'file_info': file_info,
            'pronunciation_analysis': analysis_result,
            'audio_url': f'/api/media/files/{unique_filename}'
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading audio: {str(e)}")
        return jsonify({
            'error': 'Failed to upload audio',
            'telugu_message': 'ఆడియో అప్‌లోడ్ చేయడంలో విఫలం'
        }), 500

@media_bp.route('/record/voice', methods=['POST'])
@jwt_required()
def analyze_voice_recording():
    """
    Analyze voice recording for pronunciation practice.
    
    Expected JSON:
    {
        "audio_data": "base64_encoded_audio",
        "target_text": "Hello, how are you?",
        "practice_type": "pronunciation"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        audio_data = data.get('audio_data')
        target_text = data.get('target_text', '')
        practice_type = data.get('practice_type', 'pronunciation')
        
        if not audio_data or not target_text:
            return jsonify({
                'error': 'Audio data and target text are required',
                'telugu_message': 'ఆడియో డేటా మరియు లక్ష్య టెక్స్ట్ అవసరం'
            }), 400
        
        # Mock voice analysis (implement with real speech recognition)
        pronunciation_analysis = {
            'target_text': target_text,
            'practice_type': practice_type,
            'overall_score': 78,
            'word_scores': [
                {'word': 'Hello', 'score': 85, 'feedback': 'Good pronunciation'},
                {'word': 'how', 'score': 70, 'feedback': 'Work on the vowel sound'},
                {'word': 'are', 'score': 80, 'feedback': 'Clear pronunciation'},
                {'word': 'you', 'score': 75, 'feedback': 'Good effort'}
            ],
            'pronunciation_tips': [
                'Focus on vowel sounds in "how"',
                'Practice word linking: "how are"',
                'Great job with clear consonants!'
            ],
            'fluency_score': 82,
            'confidence_score': 76,
            'suggestions': [
                'Practice this phrase 3 more times',
                'Try recording in a quiet environment',
                'Focus on natural rhythm and stress'
            ]
        }
        
        # Create a practice session record
        session_data = {
            'user_id': user_id,
            'practice_type': 'voice_recording',
            'target_text': target_text,
            'analysis_result': pronunciation_analysis,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'message': 'Voice recording analyzed successfully!',
            'telugu_message': 'వాయిస్ రికార్డింగ్ విజయవంతంగా విశ్లేషించబడింది!',
            'analysis': pronunciation_analysis,
            'encouragement': 'Keep practicing! Your pronunciation is improving! అభ్యాసం కొనసాగించండి!',
            'next_steps': {
                'practice_again': True,
                'try_similar_phrases': [
                    'Hi, nice to meet you',
                    'How was your day?',
                    'What are you doing?'
                ]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing voice recording: {str(e)}")
        return jsonify({
            'error': 'Failed to analyze voice recording',
            'telugu_message': 'వాయిస్ రికార్డింగ్ విశ్లేషణలో విఫలం'
        }), 500

@media_bp.route('/generate/pronunciation-exercise', methods=['POST'])
@jwt_required()
def generate_pronunciation_exercise():
    """
    Generate a pronunciation exercise based on user's difficulty level.
    
    Expected JSON:
    {
        "focus_area": "vowel_sounds",  // "vowel_sounds", "consonants", "word_stress", "sentence_rhythm"
        "difficulty": "beginner"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        focus_area = data.get('focus_area', 'vowel_sounds')
        difficulty = data.get('difficulty', 'beginner')
        
        # Get user info for personalization
        user = User.query.get(user_id)
        proficiency_level = user.profile.proficiency_level if user.profile else difficulty
        
        # Generate pronunciation exercise using AI
        exercise_prompt = f"""
        Create a pronunciation exercise for a Telugu speaker learning English.
        
        Focus Area: {focus_area}
        Difficulty Level: {proficiency_level}
        
        Generate a JSON response with:
        {{
            "exercise_title": "Practice [focus_area]",
            "instructions": "Clear instructions in English with Telugu translation",
            "target_phrases": [
                {{
                    "phrase": "English phrase",
                    "telugu_translation": "Telugu translation",
                    "pronunciation_tips": "Specific tips for Telugu speakers",
                    "phonetic": "IPA or simplified phonetics"
                }}
            ],
            "common_mistakes": ["mistakes Telugu speakers make"],
            "practice_tips": ["helpful practice suggestions"]
        }}
        
        Focus on sounds that are challenging for Telugu speakers.
        """
        
        try:
            ai_response = activity_service.model.generate_content(exercise_prompt)
            exercise_content = activity_service._extract_json_from_response(ai_response.text)
        except Exception as ai_error:
            current_app.logger.warning(f"AI content generation failed: {str(ai_error)}")
            # Fallback exercise content
            exercise_content = {
                "exercise_title": f"Practice {focus_area.replace('_', ' ').title()}",
                "instructions": "Listen and repeat each phrase. Focus on clear pronunciation.",
                "target_phrases": [
                    {
                        "phrase": "Hello, how are you?",
                        "telugu_translation": "హలో, మీరు ఎలా ఉన్నారు?",
                        "pronunciation_tips": "Focus on the 'h' sound at the beginning",
                        "phonetic": "/həˈloʊ haʊ ɑr ju/"
                    }
                ],
                "common_mistakes": ["Confusing 'a' and 'e' sounds"],
                "practice_tips": ["Record yourself and compare", "Practice slowly first"]
            }
        
        return jsonify({
            'message': 'Pronunciation exercise generated successfully!',
            'telugu_message': 'ఉచ్చారణ వ్యాయామం విజయవంతంగా రూపొందించబడింది!',
            'exercise': exercise_content,
            'session_info': {
                'focus_area': focus_area,
                'difficulty': proficiency_level,
                'estimated_duration': '10-15 minutes'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating pronunciation exercise: {str(e)}")
        return jsonify({
            'error': 'Failed to generate pronunciation exercise',
            'telugu_message': 'ఉచ్చారణ వ్యాయామం రూపొందించడంలో విఫలం'
        }), 500

@media_bp.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    """
    Serve uploaded files (images, audio).
    """
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        current_app.logger.error(f"Error serving file: {str(e)}")
        return jsonify({'error': 'File not found'}), 404

@media_bp.route('/my-uploads', methods=['GET'])
@jwt_required()
def get_my_uploads():
    """
    Get user's uploaded files with pagination.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        file_type = request.args.get('type', None)  # 'image', 'audio', or None for all
        
        # In a real implementation, you would query a MediaFile model
        # For now, return mock data
        mock_uploads = {
            'uploads': [
                {
                    'id': 1,
                    'filename': 'vocabulary_image_1.jpg',
                    'file_type': 'image',
                    'upload_time': '2024-01-15T10:30:00Z',
                    'analysis_result': {'vocabulary_words': ['cat', 'pet', 'animal']},
                    'file_url': '/api/media/files/vocabulary_image_1.jpg'
                }
            ],
            'pagination': {
                'page': 1,
                'per_page': 20,
                'total': 1,
                'pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }
        
        return jsonify({
            'message': 'Uploads retrieved successfully!',
            'telugu_message': 'అప్‌లోడ్‌లు విజయవంతంగా తీసుకోబడ్డాయి!',
            **mock_uploads
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting uploads: {str(e)}")
        return jsonify({
            'error': 'Failed to get uploads',
            'telugu_message': 'అప్‌లోడ్‌లు పొందడంలో విఫలం'
        }), 500