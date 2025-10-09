"""
Image-Based Learning Service
Analyzes uploaded images using centralized LLM configuration
Identifies objects and generates Telugu translations with sample sentences
"""
import os
import uuid
from datetime import datetime
from PIL import Image
from app import db
from app.models import ImageLearning, ImageObjectVocabulary, VocabularyWord, User
from app.services.llm_config import LLMConfig
from config import Config


class ImageService:
    """Service for analyzing images and generating vocabulary learning content"""
    
    # Allowed image formats
    ALLOWED_FORMATS = {'jpg', 'jpeg', 'png', 'webp'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes
    
    @staticmethod
    def validate_image(file):
        """
        Validate uploaded image file
        
        Args:
            file: Flask FileStorage object
            
        Returns:
            tuple: (is_valid, error_message, file_info)
        """
        if not file:
            return False, "No file provided", None
        
        if file.filename == '':
            return False, "Empty filename", None
        
        # Check file extension
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in ImageService.ALLOWED_FORMATS:
            return False, f"Invalid file format. Allowed: {', '.join(ImageService.ALLOWED_FORMATS)}", None
        
        # Check file size by reading content
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > ImageService.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB). Maximum: 5MB", None
        
        # Try to open as image to validate format
        try:
            file.seek(0)
            img = Image.open(file)
            img.verify()
            file.seek(0)  # Reset after verify
            
            file_info = {
                'original_filename': file.filename,
                'file_size': file_size,
                'format': file_ext,
                'mime_type': file.content_type
            }
            return True, None, file_info
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}", None
    
    @staticmethod
    def save_uploaded_image(file, user_id):
        """
        Save uploaded image to server
        
        Args:
            file: Flask FileStorage object
            user_id: ID of user uploading image
            
        Returns:
            tuple: (success, file_path, filename, error)
        """
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'images')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename: user_id_timestamp_uuid.ext
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            filename = f"user_{user_id}_{timestamp}_{unique_id}.{file_ext}"
            
            file_path = os.path.join(upload_dir, filename)
            
            # Save file
            file.save(file_path)
            
            return True, file_path, filename, None
            
        except Exception as e:
            return False, None, None, f"Failed to save image: {str(e)}"
    
    @staticmethod
    def analyze_image_for_learning(image_path, user_id):
        """
        Analyze image using centralized LLM configuration
        
        Args:
            image_path: Path to saved image file
            user_id: ID of user
            
        Returns:
            dict: Analysis results with identified objects and translations
        """
        try:
            # Create prompt for vision model
            prompt = """
            Analyze this image and identify the main objects, items, or concepts visible.
            For each object identified, provide:
            1. Object name in English
            2. Object name in Telugu (తెలుగు)
            3. A simple sample sentence using the object in English
            4. Telugu translation of the sample sentence
            5. Pronunciation guide (in English letters)
            6. Category (e.g., kitchen_appliance, furniture, food, clothing, nature, etc.)
            7. Confidence score (0.0 to 1.0)
            
            Focus on identifying 3-10 clear, distinct objects that would be useful for vocabulary learning.
            Prioritize common, everyday objects that a language learner would find useful.
            
            Return the result in valid JSON format with this structure:
            {
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
                "scene_description": "Brief description of the overall scene",
                "scene_description_telugu": "Telugu description of the scene",
                "learning_context": "Suggested learning context (e.g., 'Kitchen vocabulary', 'Outdoor items')"
            }
            """
            
            # Use centralized LLM config for image analysis
            result = LLMConfig.analyze_image(
                image=image_path,
                prompt=prompt,
                temperature=0.7,
                max_tokens=2048,
                json_mode=True
            )
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Image analysis failed'),
                    'error_telugu': 'చిత్ర విశ్లేషణ విఫలమైంది'
                }
            
            # Parse JSON response
            import json
            analysis_text = result['analysis']
            analysis_result = json.loads(analysis_text)
            
            # Validate structure
            if 'objects' not in analysis_result:
                return {
                    'success': False,
                    'error': 'Invalid response format from AI',
                    'error_telugu': 'AI నుండి చెల్లని ప్రతిస్పందన ఆకృతి'
                }
            
            return {
                'success': True,
                'objects': analysis_result.get('objects', []),
                'scene_description': analysis_result.get('scene_description', ''),
                'scene_description_telugu': analysis_result.get('scene_description_telugu', ''),
                'learning_context': analysis_result.get('learning_context', ''),
                'total_objects_found': len(analysis_result.get('objects', []))
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}',
                'error_telugu': 'AI ప్రతిస్పందనను అన్వయించడంలో విఫలమైంది',
                'raw_response': result.get('analysis') if 'result' in locals() else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image analysis failed: {str(e)}',
                'error_telugu': 'చిత్ర విశ్లేషణ విఫలమైంది'
            }
    
    @staticmethod
    def create_image_learning_record(user_id, file_info, image_path, filename, analysis_result, 
                                     is_camera_capture=False, device_type='desktop'):
        """
        Create ImageLearning database record
        
        Args:
            user_id: User ID
            file_info: Dict with file information
            image_path: Path to saved image
            filename: Saved filename
            analysis_result: Dict with AI analysis results
            is_camera_capture: Whether image was from camera
            device_type: Device type (mobile/desktop/tablet)
            
        Returns:
            ImageLearning: Created record
        """
        try:
            # Create image URL (relative path for serving)
            image_url = f'/uploads/images/{filename}'
            
            # Determine status
            status = 'completed' if analysis_result.get('success') else 'failed'
            
            # Create record
            image_record = ImageLearning(
                user_id=user_id,
                image_filename=filename,
                image_path=image_path,
                image_url=image_url,
                original_filename=file_info.get('original_filename'),
                file_size_bytes=file_info.get('file_size'),
                image_format=file_info.get('format'),
                analyzed_at=datetime.utcnow(),
                analysis_status=status,
                error_message=analysis_result.get('error') if not analysis_result.get('success') else None,
                identified_objects=analysis_result.get('objects', []),
                total_objects_found=analysis_result.get('total_objects_found', 0),
                uploaded_from_device=device_type,
                is_camera_capture=is_camera_capture
            )
            
            db.session.add(image_record)
            db.session.commit()
            
            return image_record
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create image record: {str(e)}")
    
    @staticmethod
    def save_objects_to_vocabulary(image_learning_id, user_id, object_indices):
        """
        Save selected objects from image analysis to user's vocabulary
        
        Args:
            image_learning_id: ImageLearning record ID
            user_id: User ID
            object_indices: List of object indices to save (from identified_objects array)
            
        Returns:
            dict: Result with saved vocabulary words
        """
        try:
            # Get image learning record
            image_record = ImageLearning.query.get(image_learning_id)
            if not image_record or image_record.user_id != user_id:
                return {
                    'success': False,
                    'error': 'Image learning record not found',
                    'error_telugu': 'చిత్ర అభ్యాస రికార్డ్ కనుగొనబడలేదు'
                }
            
            saved_words = []
            already_saved = image_record.objects_saved_to_vocabulary or []
            
            for idx in object_indices:
                # Skip if already saved
                if idx in already_saved:
                    continue
                
                # Get object data
                if idx >= len(image_record.identified_objects):
                    continue
                
                obj = image_record.identified_objects[idx]
                
                # Check if word already exists in vocabulary
                existing_word = VocabularyWord.query.filter_by(
                    user_id=user_id,
                    word_english=obj['object_name_english']
                ).first()
                
                if existing_word:
                    # Link to existing word
                    vocab_word = existing_word
                else:
                    # Create new vocabulary word
                    vocab_word = VocabularyWord(
                        user_id=user_id,
                        word_english=obj['object_name_english'],
                        word_telugu=obj['object_name_telugu'],
                        pronunciation=obj.get('pronunciation', ''),
                        example_sentence=obj.get('sample_sentence', ''),
                        sentence_telugu=obj.get('sentence_telugu', ''),
                        category=obj.get('category', 'general'),
                        difficulty_level='beginner',
                        source='image_learning',
                        times_practiced=0,
                        mastery_level=0
                    )
                    db.session.add(vocab_word)
                    db.session.flush()  # Get ID
                
                # Create link
                link = ImageObjectVocabulary(
                    image_learning_id=image_learning_id,
                    vocabulary_word_id=vocab_word.id,
                    object_index=idx,
                    object_name_english=obj['object_name_english']
                )
                db.session.add(link)
                
                # Update saved list
                already_saved.append(idx)
                saved_words.append(vocab_word.to_dict())
            
            # Update image record
            image_record.objects_saved_to_vocabulary = already_saved
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Saved {len(saved_words)} words to vocabulary',
                'message_telugu': f'{len(saved_words)} పదాలు పదకోశానికి సేవ్ చేయబడ్డాయి',
                'saved_words': saved_words,
                'total_saved': len(already_saved)
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to save to vocabulary: {str(e)}',
                'error_telugu': 'పదకోశానికి సేవ్ చేయడంలో విఫలమైంది'
            }
    
    @staticmethod
    def get_user_image_history(user_id, limit=20):
        """
        Get user's image learning history
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            list: List of ImageLearning records
        """
        try:
            records = ImageLearning.query.filter_by(user_id=user_id)\
                .order_by(ImageLearning.created_at.desc())\
                .limit(limit)\
                .all()
            
            return {
                'success': True,
                'history': [record.to_dict() for record in records],
                'total': len(records)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch history: {str(e)}',
                'error_telugu': 'చరిత్రను పొందడంలో విఫలమైంది'
            }
