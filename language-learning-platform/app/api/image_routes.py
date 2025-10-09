"""
Image-Based Learning API Routes
Endpoints for uploading images, analyzing them, and learning vocabulary
"""
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.services.image_service import ImageService
from app.services.activity_service import ActivityService
from app.models import ImageLearning, LearningSession, db
import os
from config import Config

image_bp = Blueprint('image', __name__, url_prefix='/api/image-learning')


@image_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_uploaded_image():
    """
    Upload and analyze image for vocabulary learning
    
    Request:
        - Content-Type: multipart/form-data
        - image: Image file (JPG/PNG/WEBP, max 5MB)
        - is_camera_capture: boolean (optional)
        - device_type: string (optional: mobile, desktop, tablet)
        
    Response:
        {
            "success": true,
            "image_id": 1,
            "image_url": "/uploads/images/user_5_20251009_a3f4b2c1.jpg",
            "objects": [
                {
                    "object_name_english": "Refrigerator",
                    "object_name_telugu": "రెఫ్రిజరేటర్",
                    "sample_sentence": "I keep milk in the refrigerator.",
                    "sentence_telugu": "నేను రెఫ్రిజరేటర్ లో పాలు ఉంచుతాను.",
                    "pronunciation": "re-fri-juh-rey-ter",
                    "category": "kitchen_appliance",
                    "confidence": 0.95
                }
            ],
            "scene_description": "A modern kitchen with appliances",
            "scene_description_telugu": "ఆధునిక వంటగది పరికరాలతో",
            "learning_context": "Kitchen vocabulary",
            "total_objects_found": 5
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Check if image file present
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided',
                'error_telugu': 'చిత్ర ఫైల్ అందించబడలేదు'
            }), 400
        
        file = request.files['image']
        
        # Get optional parameters
        is_camera_capture = request.form.get('is_camera_capture', 'false').lower() == 'true'
        device_type = request.form.get('device_type', 'desktop')
        
        # Validate image
        is_valid, error_msg, file_info = ImageService.validate_image(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg,
                'error_telugu': 'చిత్రం చెల్లదు'
            }), 400
        
        # Save image
        success, file_path, filename, save_error = ImageService.save_uploaded_image(file, user_id)
        if not success:
            return jsonify({
                'success': False,
                'error': save_error,
                'error_telugu': 'చిత్రాన్ని సేవ్ చేయడంలో విఫలమైంది'
            }), 500
        
        # Analyze image with AI
        analysis_result = ImageService.analyze_image_for_learning(file_path, user_id)
        
        # Create database record
        image_record = ImageService.create_image_learning_record(
            user_id=user_id,
            file_info=file_info,
            image_path=file_path,
            filename=filename,
            analysis_result=analysis_result,
            is_camera_capture=is_camera_capture,
            device_type=device_type
        )
        
        # Return success response
        if analysis_result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Image analyzed successfully! Found {analysis_result.get("total_objects_found", 0)} objects',
                'message_telugu': f'చిత్రం విజయవంతంగా విశ్లేషించబడింది! {analysis_result.get("total_objects_found", 0)} వస్తువులు కనుగొనబడ్డాయి',
                'image_id': image_record.id,
                'image_url': image_record.image_url,
                'objects': analysis_result.get('objects', []),
                'scene_description': analysis_result.get('scene_description', ''),
                'scene_description_telugu': analysis_result.get('scene_description_telugu', ''),
                'learning_context': analysis_result.get('learning_context', ''),
                'total_objects_found': analysis_result.get('total_objects_found', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': analysis_result.get('error', 'Analysis failed'),
                'error_telugu': analysis_result.get('error_telugu', 'విశ్లేషణ విఫలమైంది'),
                'image_id': image_record.id,
                'raw_response': analysis_result.get('raw_response')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Image analysis failed: {str(e)}',
            'error_telugu': 'చిత్ర విశ్లేషణ విఫలమైంది'
        }), 500


@image_bp.route('/history', methods=['GET'])
@jwt_required()
def get_image_learning_history():
    """
    Get user's image learning history
    
    Query Parameters:
        - limit: int (default: 20, max: 100)
        
    Response:
        {
            "success": true,
            "history": [
                {
                    "id": 1,
                    "image_url": "/uploads/images/...",
                    "analyzed_at": "2025-10-09T10:00:00",
                    "total_objects_found": 5,
                    "objects_saved_to_vocabulary": [0, 1, 2],
                    "flashcard_session_created": false
                }
            ],
            "total": 10
        }
    """
    try:
        user_id = get_jwt_identity()
        limit = min(int(request.args.get('limit', 20)), 100)
        
        result = ImageService.get_user_image_history(user_id, limit=limit)
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch history: {str(e)}',
            'error_telugu': 'చరిత్రను పొందడంలో విఫలమైంది'
        }), 500


@image_bp.route('/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image_details(image_id):
    """
    Get detailed information about a specific image analysis
    
    Response:
        {
            "success": true,
            "image": {
                "id": 1,
                "image_url": "/uploads/images/...",
                "analyzed_at": "2025-10-09T10:00:00",
                "identified_objects": [...],
                "total_objects_found": 5,
                ...
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        
        image_record = ImageLearning.query.get(image_id)
        if not image_record or image_record.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Image not found',
                'error_telugu': 'చిత్రం కనుగొనబడలేదు'
            }), 404
        
        return jsonify({
            'success': True,
            'image': image_record.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch image details: {str(e)}',
            'error_telugu': 'చిత్ర వివరాలను పొందడంలో విఫలమైంది'
        }), 500


@image_bp.route('/<int:image_id>/save-words', methods=['POST'])
@jwt_required()
def save_words_to_vocabulary(image_id):
    """
    Save selected objects from image analysis to vocabulary
    
    Request Body:
        {
            "object_indices": [0, 2, 4]  // Indices from identified_objects array
        }
        
    Response:
        {
            "success": true,
            "message": "Saved 3 words to vocabulary",
            "message_telugu": "3 పదాలు పదకోశానికి సేవ్ చేయబడ్డాయి",
            "saved_words": [
                {
                    "id": 10,
                    "word_english": "Refrigerator",
                    "word_telugu": "రెఫ్రిజరేటర్",
                    ...
                }
            ],
            "total_saved": 3
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'object_indices' not in data:
            return jsonify({
                'success': False,
                'error': 'object_indices required',
                'error_telugu': 'వస్తువు సూచికలు అవసరం'
            }), 400
        
        object_indices = data['object_indices']
        if not isinstance(object_indices, list):
            return jsonify({
                'success': False,
                'error': 'object_indices must be an array',
                'error_telugu': 'వస్తువు సూచికలు శ్రేణిగా ఉండాలి'
            }), 400
        
        result = ImageService.save_objects_to_vocabulary(image_id, user_id, object_indices)
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to save words: {str(e)}',
            'error_telugu': 'పదాలను సేవ్ చేయడంలో విఫలమైంది'
        }), 500


@image_bp.route('/<int:image_id>/create-flashcards', methods=['POST'])
@jwt_required()
def create_flashcards_from_image(image_id):
    """
    Generate flashcard activity from identified objects in image
    
    Request Body:
        {
            "object_indices": [0, 1, 2, 3, 4],  // Optional: specific objects, or all if omitted
            "difficulty": "beginner"  // Optional: beginner, intermediate, advanced
        }
        
    Response:
        {
            "success": true,
            "message": "Flashcard session created with 5 cards",
            "message_telugu": "5 ఫ్లాష్‌కార్డ్‌లతో సెషన్ సృష్టించబడింది",
            "session": {
                "id": 123,
                "activity_type": "flashcard",
                "generated_content": {
                    "flashcards": [
                        {
                            "word_english": "Refrigerator",
                            "word_telugu": "రెఫ్రిజరేటర్",
                            "example_sentence": "I keep milk in the refrigerator.",
                            ...
                        }
                    ]
                },
                "total_items": 5
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Get image record
        image_record = ImageLearning.query.get(image_id)
        if not image_record or image_record.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Image not found',
                'error_telugu': 'చిత్రం కనుగొనబడలేదు'
            }), 404
        
        # Get object indices (all by default)
        object_indices = data.get('object_indices')
        if object_indices is None:
            object_indices = list(range(len(image_record.identified_objects)))
        
        # Get selected objects
        selected_objects = []
        for idx in object_indices:
            if 0 <= idx < len(image_record.identified_objects):
                selected_objects.append(image_record.identified_objects[idx])
        
        if not selected_objects:
            return jsonify({
                'success': False,
                'error': 'No valid objects selected',
                'error_telugu': 'చెల్లుబాటు అయ్యే వస్తువులు ఎంపిక చేయబడలేదు'
            }), 400
        
        # Create flashcard session
        difficulty = data.get('difficulty', 'beginner')
        
        # Build flashcards from objects
        flashcards = []
        for obj in selected_objects:
            flashcard = {
                'word_english': obj['object_name_english'],
                'word_telugu': obj['object_name_telugu'],
                'pronunciation': obj.get('pronunciation', ''),
                'example_sentence': obj.get('sample_sentence', ''),
                'sentence_telugu': obj.get('sentence_telugu', ''),
                'category': obj.get('category', 'general'),
                'image_source': image_record.image_url
            }
            flashcards.append(flashcard)
        
        # Create LearningSession
        session = LearningSession(
            user_id=user_id,
            activity_type='flashcard',
            difficulty_level=difficulty,
            status='active',
            generated_content={
                'flashcards': flashcards,
                'source': 'image_learning',
                'image_id': image_id,
                'learning_context': 'Image-based vocabulary learning'
            },
            total_items=len(flashcards),
            is_ai_generated=True
        )
        
        db.session.add(session)
        
        # Update image record
        image_record.flashcard_session_created = True
        image_record.flashcard_session_id = session.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Flashcard session created with {len(flashcards)} cards',
            'message_telugu': f'{len(flashcards)} ఫ్లాష్‌కార్డ్‌లతో సెషన్ సృష్టించబడింది',
            'session': {
                'id': session.id,
                'activity_type': session.activity_type,
                'difficulty_level': session.difficulty_level,
                'generated_content': session.generated_content,
                'total_items': session.total_items
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to create flashcards: {str(e)}',
            'error_telugu': 'ఫ్లాష్‌కార్డ్‌లు సృష్టించడంలో విఫలమైంది'
        }), 500


@image_bp.route('/uploads/images/<filename>', methods=['GET'])
def serve_uploaded_image(filename):
    """
    Serve uploaded images
    
    This endpoint serves the uploaded images from the uploads/images directory
    No JWT required for viewing images
    """
    try:
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'images')
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Image not found'
        }), 404


# Error handlers
@image_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'error_telugu': 'ఎండ్‌పాయింట్ కనుగొనబడలేదు'
    }), 404


@image_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'error_telugu': 'అంతర్గత సర్వర్ లోపం'
    }), 500
