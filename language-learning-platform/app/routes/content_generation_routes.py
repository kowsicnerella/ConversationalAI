"""
Content Generation API Routes - Phase 2
REST endpoints for AI-powered content generation with full CRUD support.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.content_generation_engine import ContentGenerationEngine
from app.models.curriculum import LearningNode
from app.models.course import LearningPath
from app.models.activity import Activity, UserActivityLog
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import desc, asc

content_generation_bp = Blueprint('content_generation', __name__, url_prefix='/api/content-generation')

# Initialize the content generation engine
engine = ContentGenerationEngine()


# ============================================
# Helper Functions
# ============================================

def save_generated_activity(activity_data, user_id, activity_type, learning_path_id=None):
    """
    Save a generated activity to the database.
    
    Args:
        activity_data: Generated activity content
        user_id: ID of the user who requested the activity
        activity_type: Type of activity (quiz, flashcard, etc.)
        learning_path_id: Optional learning path ID
        
    Returns:
        Saved Activity object
    """
    # Get or create a default learning path if not specified
    if not learning_path_id:
        # Look for user's active learning path
        user = User.query.get(user_id)
        if user and user.enrolled_paths:
            # Get the first enrolled learning path
            enrolled_paths = user.enrolled_paths.all()
            if enrolled_paths:
                learning_path_id = enrolled_paths[0].id
        
        # If still no path, create a default one
        if not learning_path_id:
            default_path = LearningPath.query.filter_by(
                title="AI-Generated Activities"
            ).first()
            if not default_path:
                default_path = LearningPath(
                    title="AI-Generated Activities",
                    description="Collection of AI-generated personalized activities",
                    proficiency_level="mixed",
                    created_at=datetime.utcnow()
                )
                db.session.add(default_path)
                db.session.flush()
            learning_path_id = default_path.id
    
    # Determine order in path (get max order + 1)
    max_order = db.session.query(db.func.max(Activity.order_in_path))\
        .filter_by(learning_path_id=learning_path_id).scalar() or 0
    
    # Create activity record
    activity = Activity(
        learning_path_id=learning_path_id,
        activity_type=activity_type,
        title=activity_data.get('title', f'{activity_type.title()} Activity'),
        description=activity_data.get('description', ''),
        content=activity_data,
        difficulty_level=activity_data.get('difficulty_level', 0.5),
        order_in_path=max_order + 1,
        estimated_duration_minutes=activity_data.get('estimated_duration_minutes', 10),
        points_reward=activity_data.get('points_reward', 10),
        skill_area=activity_data.get('skill_area', activity_type),
        concept_focus=activity_data.get('concept_focus', ''),
        is_adaptive=activity_data.get('is_adaptive', True),
        generation_metadata={
            'generated_by': 'ContentGenerationEngine',
            'generated_for_user': user_id,
            'generated_at': datetime.utcnow().isoformat(),
            'generation_context': activity_data.get('metadata', {})
        },
        created_at=datetime.utcnow()
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return activity


@content_generation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_activity():
    """
    Generate a personalized activity.
    
    POST /api/content-generation/generate
    Body:
    {
        "activity_type": "quiz|flashcard|reading|writing|listening|speaking|etc",
        "learning_node_id": "optional_node_id",
        "difficulty": "easy|medium|hard or 0-1",
        "options": {
            // Activity-specific options
        }
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        activity_type = data.get('activity_type')
        learning_node_id = data.get('learning_node_id')
        difficulty = data.get('difficulty', 'medium')
        options = data.get('options', {})
        
        if not activity_type:
            return jsonify({"error": "activity_type is required"}), 400
        
        # Get learning node if specified
        learning_node = None
        if learning_node_id:
            learning_node = LearningNode.query.filter_by(node_id=learning_node_id).first()
            if not learning_node:
                return jsonify({"error": f"Learning node {learning_node_id} not found"}), 404
        
        # Generate the activity
        result = engine.generate_personalized_activity(
            user_id=user_id,
            learning_node=learning_node,
            difficulty=difficulty,
            activity_type=activity_type,
            user_context=None  # Will be loaded automatically
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Save to database with proper structure
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type=activity_type,
            learning_path_id=learning_node.learning_path_id if learning_node else None
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    """
    Generate an adaptive quiz.
    
    POST /api/content-generation/quiz
    Body:
    {
        "concept": "Topic or concept",
        "difficulty": 0.5,
        "question_count": 10,
        "focus_areas": ["vocabulary", "grammar"],
        "learning_path_id": optional
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_adaptive_quiz(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            concept=data.get('concept'),
            question_count=data.get('question_count', 10),
            focus_areas=data.get('focus_areas', [])
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='quiz',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/flashcards', methods=['POST'])
@jwt_required()
def generate_flashcards():
    """
    Generate contextual flashcards.
    
    POST /api/content-generation/flashcards
    Body:
    {
        "vocabulary_list": ["word1", "word2"],
        "context_theme": "Daily conversation",
        "difficulty": 0.5
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_contextual_flashcards(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            vocabulary_list=data.get('vocabulary_list'),
            context_theme=data.get('context_theme')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='flashcard',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/reading', methods=['POST'])
@jwt_required()
def generate_reading():
    """
    Generate reading comprehension passage.
    
    POST /api/content-generation/reading
    Body:
    {
        "topic": "Technology",
        "difficulty": 0.6,
        "length_words": 300,
        "target_vocabulary": ["optional", "words"]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_reading_passage(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            topic=data.get('topic'),
            length_words=data.get('length_words', 300),
            target_vocabulary=data.get('target_vocabulary')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='reading',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/writing', methods=['POST'])
@jwt_required()
def generate_writing():
    """
    Generate writing prompt.
    
    POST /api/content-generation/writing
    Body:
    {
        "writing_type": "essay|email|story|description",
        "difficulty": 0.5,
        "word_count_range": [100, 200],
        "target_grammar": ["present_tense"]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        word_count_range = data.get('word_count_range', [100, 200])
        if isinstance(word_count_range, list) and len(word_count_range) == 2:
            word_count_range = tuple(word_count_range)
        else:
            word_count_range = (100, 200)
        
        result = engine.generate_writing_prompt(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            writing_type=data.get('writing_type', 'essay'),
            target_grammar=data.get('target_grammar'),
            word_count_range=word_count_range
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='writing',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/listening', methods=['POST'])
@jwt_required()
def generate_listening():
    """
    Generate listening exercise.
    
    POST /api/content-generation/listening
    Body:
    {
        "topic": "Weather",
        "difficulty": 0.5,
        "duration_seconds": 120,
        "focus_phonemes": ["th", "r"]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_listening_exercise(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            topic=data.get('topic'),
            duration_seconds=data.get('duration_seconds', 120),
            focus_phonemes=data.get('focus_phonemes')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='listening',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/speaking', methods=['POST'])
@jwt_required()
def generate_speaking():
    """
    Generate speaking scenario.
    
    POST /api/content-generation/speaking
    Body:
    {
        "scenario_type": "conversation|interview|shopping",
        "difficulty": 0.5,
        "target_phrases": ["How are you?"]
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_speaking_scenario(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            scenario_type=data.get('scenario_type', 'conversation'),
            target_phrases=data.get('target_phrases')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='speaking',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/real-world', methods=['POST'])
@jwt_required()
def generate_real_world():
    """
    Generate real-world task.
    
    POST /api/content-generation/real-world
    Body:
    {
        "task_type": "email|presentation|negotiation",
        "difficulty": 0.5,
        "industry": "technology"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_real_world_task(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            task_type=data.get('task_type', 'email'),
            industry=data.get('industry', 'general')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='real_world',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/pronunciation', methods=['POST'])
@jwt_required()
def generate_pronunciation():
    """Generate pronunciation practice."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_pronunciation_practice(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            focus_sounds=data.get('focus_sounds')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='pronunciation',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/sentence-construction', methods=['POST'])
@jwt_required()
def generate_sentence_construction():
    """Generate sentence construction exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_sentence_construction(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            grammar_focus=data.get('grammar_focus')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='sentence_construction',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/dialogue-completion', methods=['POST'])
@jwt_required()
def generate_dialogue_completion():
    """Generate dialogue completion exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_dialogue_completion(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            context=data.get('context')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='dialogue_completion',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/error-correction', methods=['POST'])
@jwt_required()
def generate_error_correction():
    """Generate error correction exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_error_correction(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            error_types=data.get('error_types')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='error_correction',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/story-sequencing', methods=['POST'])
@jwt_required()
def generate_story_sequencing():
    """Generate story sequencing exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_story_sequencing(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            theme=data.get('theme')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='story_sequencing',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/synonym-antonym', methods=['POST'])
@jwt_required()
def generate_synonym_antonym():
    """Generate synonym/antonym matching exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_synonym_antonym(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            vocabulary_level=data.get('vocabulary_level')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='synonym_antonym',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/dictation', methods=['POST'])
@jwt_required()
def generate_dictation():
    """Generate dictation exercise."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_dictation_exercise(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            topic=data.get('topic')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='dictation',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/translation', methods=['POST'])
@jwt_required()
def generate_translation():
    """Generate translation challenge."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_context = engine._get_user_context(user_id)
        
        result = engine.generate_translation_challenge(
            user_id=user_id,
            user_context=user_context,
            difficulty=data.get('difficulty', 0.5),
            direction=data.get('direction', 'telugu_to_english')
        )
        
        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='translation',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/batch', methods=['POST'])
@jwt_required()
def generate_batch():
    """
    Generate multiple activities at once for a learning session.
    
    POST /api/content-generation/batch
    Body:
    {
        "activity_types": ["quiz", "flashcard", "reading"],
        "difficulty": 0.5,
        "learning_node_id": "optional"
    }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        activity_types = data.get('activity_types', [])
        if not activity_types:
            return jsonify({"error": "activity_types is required"}), 400
        
        difficulty = data.get('difficulty', 0.5)
        learning_node_id = data.get('learning_node_id')
        
        learning_node = None
        if learning_node_id:
            learning_node = LearningNode.query.filter_by(node_id=learning_node_id).first()
        
        # Get user context once for all activities
        user_context = engine._get_user_context(user_id)
        
        results = []
        for activity_type in activity_types:
            try:
                activity = engine.generate_personalized_activity(
                    user_id=user_id,
                    learning_node=learning_node,
                    difficulty=difficulty,
                    activity_type=activity_type,
                    user_context=user_context
                )
                results.append(activity)
            except Exception as e:
                results.append({"activity_type": activity_type, "error": str(e)})
        
        return jsonify({
            "activities": results,
            "total_generated": len(results)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@content_generation_bp.route('/activity-types', methods=['GET'])
def get_activity_types():
    """
    Get list of all supported activity types.
    
    GET /api/content-generation/activity-types
    """
    activity_types = [
        {
            "type": "quiz",
            "name": "Adaptive Quiz",
            "description": "Dynamic quiz with multiple question types",
            "skills": ["comprehension", "vocabulary", "grammar"]
        },
        {
            "type": "flashcard",
            "name": "Contextual Flashcards",
            "description": "Flashcards with examples and translations",
            "skills": ["vocabulary", "memory"]
        },
        {
            "type": "reading",
            "name": "Reading Comprehension",
            "description": "Reading passage with questions",
            "skills": ["reading", "comprehension", "vocabulary"]
        },
        {
            "type": "writing",
            "name": "Writing Practice",
            "description": "Guided writing with rubric",
            "skills": ["writing", "grammar", "vocabulary"]
        },
        {
            "type": "listening",
            "name": "Listening Exercise",
            "description": "Audio comprehension with questions",
            "skills": ["listening", "comprehension"]
        },
        {
            "type": "speaking",
            "name": "Speaking Scenario",
            "description": "Role-play conversation practice",
            "skills": ["speaking", "pronunciation", "fluency"]
        },
        {
            "type": "real_world",
            "name": "Real-World Task",
            "description": "Practical tasks like emails and presentations",
            "skills": ["writing", "professional_communication"]
        },
        {
            "type": "pronunciation",
            "name": "Pronunciation Practice",
            "description": "Phoneme and sound practice",
            "skills": ["speaking", "pronunciation"]
        },
        {
            "type": "sentence_construction",
            "name": "Sentence Construction",
            "description": "Build sentences with grammar focus",
            "skills": ["grammar", "writing"]
        },
        {
            "type": "dialogue_completion",
            "name": "Dialogue Completion",
            "description": "Fill in missing parts of conversations",
            "skills": ["comprehension", "vocabulary"]
        },
        {
            "type": "error_correction",
            "name": "Error Correction",
            "description": "Find and fix mistakes",
            "skills": ["grammar", "editing"]
        },
        {
            "type": "story_sequencing",
            "name": "Story Sequencing",
            "description": "Order story parts correctly",
            "skills": ["comprehension", "logic"]
        },
        {
            "type": "synonym_antonym",
            "name": "Synonym/Antonym Matching",
            "description": "Match words with synonyms and antonyms",
            "skills": ["vocabulary", "word_relationships"]
        },
        {
            "type": "dictation",
            "name": "Dictation Exercise",
            "description": "Listen and write what you hear",
            "skills": ["listening", "writing", "spelling"]
        },
        {
            "type": "translation",
            "name": "Translation Challenge",
            "description": "Translate between Telugu and English",
            "skills": ["translation", "vocabulary", "grammar"]
        }
    ]
    
    return jsonify({
        "activity_types": activity_types,
        "total_types": len(activity_types)
    }), 200


# ============================================
# GET Endpoints - Retrieve Activities
# ============================================

@content_generation_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    """
    Get all generated activities for the current user with filtering and pagination.
    
    GET /api/content-generation/activities
    Query params:
    - activity_type: Filter by type (quiz, flashcard, etc.)
    - difficulty_min: Minimum difficulty (0-1)
    - difficulty_max: Maximum difficulty (0-1)
    - skill_area: Filter by skill area
    - learning_path_id: Filter by learning path
    - limit: Results per page (default 20)
    - offset: Pagination offset (default 0)
    - sort_by: Sort field (created_at, difficulty_level, title)
    - sort_order: asc or desc (default desc)
    """
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        activity_type = request.args.get('activity_type')
        difficulty_min = request.args.get('difficulty_min', type=float)
        difficulty_max = request.args.get('difficulty_max', type=float)
        skill_area = request.args.get('skill_area')
        learning_path_id = request.args.get('learning_path_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query - get all activities and filter in Python (SQLite JSON limitations)
        # For better performance with PostgreSQL, use: Activity.generation_metadata['generated_for_user'].astext == str(user_id)
        query = Activity.query
        
        # Apply filters
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        if difficulty_min is not None:
            query = query.filter(Activity.difficulty_level >= difficulty_min)
        if difficulty_max is not None:
            query = query.filter(Activity.difficulty_level <= difficulty_max)
        if skill_area:
            query = query.filter_by(skill_area=skill_area)
        if learning_path_id:
            query = query.filter_by(learning_path_id=learning_path_id)
        
        # Apply sorting
        if hasattr(Activity, sort_by):
            if sort_order == 'asc':
                query = query.order_by(asc(getattr(Activity, sort_by)))
            else:
                query = query.order_by(desc(getattr(Activity, sort_by)))
        else:
            query = query.order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        activities = query.limit(limit).offset(offset).all()
        
        # Format response
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'skill_area': activity.skill_area,
                'concept_focus': activity.concept_focus,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'learning_path_id': activity.learning_path_id,
                'is_adaptive': activity.is_adaptive
            })
        
        return jsonify({
            'activities': activities_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    """
    Get a specific activity by ID with full content.
    
    GET /api/content-generation/activities/:id
    """
    try:
        user_id = get_jwt_identity()
        
        # Get activity and verify it belongs to this user
        activity = Activity.query.get_or_404(activity_id)
        
        # Check if activity was generated for this user
        generated_for_user = activity.generation_metadata.get('generated_for_user') if activity.generation_metadata else None
        if generated_for_user != user_id:
            # Allow access if user has completed this activity (collaborative paths)
            log = UserActivityLog.query.filter_by(
                user_id=user_id,
                activity_id=activity_id
            ).first()
            if not log:
                return jsonify({'error': 'Access denied'}), 403
        
        # Return full activity with content
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'activity_type': activity.activity_type,
            'difficulty_level': activity.difficulty_level,
            'skill_area': activity.skill_area,
            'concept_focus': activity.concept_focus,
            'content': activity.content,
            'estimated_duration_minutes': activity.estimated_duration_minutes,
            'points_reward': activity.points_reward,
            'created_at': activity.created_at.isoformat() if activity.created_at else None,
            'learning_path_id': activity.learning_path_id,
            'is_adaptive': activity.is_adaptive,
            'generation_metadata': activity.generation_metadata
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/by-type/<activity_type>', methods=['GET'])
@jwt_required()
def get_activities_by_type(activity_type):
    """
    Get all activities of a specific type for the current user.
    
    GET /api/content-generation/activities/by-type/:activity_type
    Query params:
    - limit: Results per page (default 20)
    - offset: Pagination offset (default 0)
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query activities of this type (SQLite doesn't support JSON filtering well)
        query = Activity.query.filter(
            Activity.activity_type == activity_type
        ).order_by(desc(Activity.created_at))
        
        total_count = query.count()
        activities = query.limit(limit).offset(offset).all()
        
        activities_data = [{
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'difficulty_level': a.difficulty_level,
            'skill_area': a.skill_area,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'estimated_duration_minutes': a.estimated_duration_minutes
        } for a in activities]
        
        return jsonify({
            'activity_type': activity_type,
            'activities': activities_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/stats', methods=['GET'])
@jwt_required()
def get_activity_stats():
    """
    Get statistics about user's generated activities.
    
    GET /api/content-generation/activities/stats
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all activities (SQLite doesn't support JSON field filtering well)
        activities = Activity.query.all()
        
        if not activities:
            return jsonify({
                'total_activities': 0,
                'by_type': {},
                'by_skill_area': {},
                'average_difficulty': 0,
                'total_estimated_time_minutes': 0
            }), 200
        
        # Calculate statistics
        by_type = {}
        by_skill_area = {}
        by_difficulty = {}
        total_time = 0
        
        # Difficulty level mapping
        difficulty_map = {
            'beginner': 1, 'A1': 1, 'A2': 2,
            'intermediate': 3, 'B1': 3, 'B2': 4,
            'advanced': 5, 'C1': 5, 'C2': 6
        }
        
        for activity in activities:
            # Count by type
            activity_type = activity.activity_type
            by_type[activity_type] = by_type.get(activity_type, 0) + 1
            
            # Count by skill area
            if activity.skill_area:
                by_skill_area[activity.skill_area] = by_skill_area.get(activity.skill_area, 0) + 1
            
            # Count by difficulty
            if activity.difficulty_level:
                diff_level = activity.difficulty_level
                by_difficulty[diff_level] = by_difficulty.get(diff_level, 0) + 1
            
            # Sum time
            if activity.estimated_duration_minutes:
                total_time += activity.estimated_duration_minutes
        
        return jsonify({
            'total_activities': len(activities),
            'by_type': by_type,
            'by_skill_area': by_skill_area,
            'by_difficulty': by_difficulty,
            'total_estimated_time_minutes': total_time
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/<int:activity_id>/history', methods=['GET'])
@jwt_required()
def get_activity_history(activity_id):
    """
    Get completion history for a specific activity.
    
    GET /api/content-generation/activities/:id/history
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all completion logs for this activity by this user
        logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        history_data = []
        for log in logs:
            history_data.append({
                'id': log.id,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'score': log.score,
                'max_score': log.max_score,
                'time_spent_minutes': log.time_spent_minutes,
                'accuracy_score': log.accuracy_score,
                'attempt_number': log.attempt_number,
                'is_completed': log.is_completed,
                'mastery_level': log.mastery_level
            })
        
        return jsonify({
            'activity_id': activity_id,
            'total_attempts': len(history_data),
            'history': history_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
