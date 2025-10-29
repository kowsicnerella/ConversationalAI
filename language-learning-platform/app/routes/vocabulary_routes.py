"""
Vocabulary Mastery Routes - Phase 5
RESTful API endpoints for vocabulary learning with spaced repetition
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app.models import db
from app.models.vocabulary_mastery import (
    VocabularyItem,
    UserVocabulary,
    VocabularyReview,
    WordRelationship,
    VocabularyPracticeSession,
)
from app.services.vocabulary_mastery_service import VocabularyMasteryEngine

# Create blueprint
vocabulary_bp = Blueprint('vocabulary', __name__)

# Initialize service
vocab_engine = VocabularyMasteryEngine()

# ==================== Decorators ====================

def validate_json(f):
    """Validate that request contains JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function


def handle_errors(f):
    """Handle common errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"Error in {f.__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


# ==================== Vocabulary Introduction ====================

@vocabulary_bp.route('/introduce', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def introduce_word():
    """
    Introduce a new word to the system and optionally add to user's vocabulary
    
    Request Body:
    {
        "word": "ambiguous",
        "difficulty_level": "B2",
        "generate_content": true,
        "add_to_user_vocab": true
    }
    
    Returns:
    {
        "vocabulary_item": {...},
        "user_vocabulary": {...} (if add_to_user_vocab=true)
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    word = data.get('word')
    if not word:
        return jsonify({'error': 'word is required'}), 400
    
    difficulty_level = data.get('difficulty_level', 'B1')
    generate_content = data.get('generate_content', True)
    add_to_user = data.get('add_to_user_vocab', True)
    
    # Introduce word
    vocab_item = vocab_engine.introduce_new_word(
        word=word,
        difficulty_level=difficulty_level,
        user_id=user_id if add_to_user else None,
        generate_content=generate_content
    )
    
    response = {
        'vocabulary_item': vocab_item.to_dict()
    }
    
    # Get user vocabulary if added
    if add_to_user:
        user_vocab = UserVocabulary.query.filter_by(
            user_id=user_id,
            vocabulary_item_id=vocab_item.id
        ).first()
        if user_vocab:
            response['user_vocabulary'] = user_vocab.to_dict()
    
    return jsonify(response), 201


@vocabulary_bp.route('/introduce-from-text', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def introduce_from_text():
    """
    Extract and introduce vocabulary from a text passage
    
    Request Body:
    {
        "text": "The ambiguous statement...",
        "context": "reading_passage",
        "activity_id": 123,
        "difficulty_level": "B2"
    }
    
    Returns:
    {
        "introduced_words": [...],
        "count": 5
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    text = data.get('text')
    if not text:
        return jsonify({'error': 'text is required'}), 400
    
    context = data.get('context', 'manual_input')
    activity_id = data.get('activity_id')
    difficulty_level = data.get('difficulty_level', 'B1')
    
    # Extract and introduce words
    user_vocabs = vocab_engine.introduce_words_from_context(
        user_id=user_id,
        text=text,
        context=context,
        activity_id=activity_id,
        difficulty_level=difficulty_level
    )
    
    return jsonify({
        'introduced_words': [uv.to_dict() for uv in user_vocabs],
        'count': len(user_vocabs)
    }), 201


@vocabulary_bp.route('/add-to-my-vocabulary', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def add_to_my_vocabulary():
    """
    Add an existing word to user's vocabulary
    
    Request Body:
    {
        "vocabulary_item_id": 123,
        "context": "reading_activity",
        "activity_id": 456
    }
    
    Returns:
    {
        "user_vocabulary": {...}
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    vocabulary_item_id = data.get('vocabulary_item_id')
    if not vocabulary_item_id:
        return jsonify({'error': 'vocabulary_item_id is required'}), 400
    
    context = data.get('context')
    activity_id = data.get('activity_id')
    
    # Add to user vocabulary
    user_vocab = vocab_engine.add_word_to_user_vocabulary(
        user_id=user_id,
        vocabulary_item_id=vocabulary_item_id,
        context=context,
        activity_id=activity_id
    )
    
    return jsonify({
        'user_vocabulary': user_vocab.to_dict()
    }), 201


# ==================== Review & Practice ====================

@vocabulary_bp.route('/words-due', methods=['GET'])
@jwt_required()
@handle_errors
def get_words_due():
    """
    Get words due for review
    
    Query Params:
    - limit: Maximum words to return (default: 20)
    - mastery_levels: Filter by mastery levels (comma-separated)
    
    Returns:
    {
        "words_due": [...],
        "count": 15
    }
    """
    user_id = get_jwt_identity()
    
    limit = request.args.get('limit', 20, type=int)
    mastery_levels_str = request.args.get('mastery_levels')
    
    mastery_levels = None
    if mastery_levels_str:
        mastery_levels = mastery_levels_str.split(',')
    
    # Get words due
    words_due = vocab_engine.get_words_due_for_review(
        user_id=user_id,
        limit=limit,
        mastery_levels=mastery_levels
    )
    
    return jsonify({
        'words_due': [word.to_dict() for word in words_due],
        'count': len(words_due)
    }), 200


@vocabulary_bp.route('/review', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def review_word():
    """
    Submit a vocabulary review (SM-2 algorithm)
    
    Request Body:
    {
        "user_vocabulary_id": 123,
        "quality_rating": 4,  # 0-5
        "response_time_seconds": 3.5,
        "review_type": "flashcard",
        "context": "daily_review"
    }
    
    Returns:
    {
        "next_review_date": "2025-10-25T10:00:00",
        "interval_days": 6,
        "mastery_level": "learning",
        "confidence_score": 65.0,
        ...
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user_vocabulary_id = data.get('user_vocabulary_id')
    quality_rating = data.get('quality_rating')
    
    if user_vocabulary_id is None or quality_rating is None:
        return jsonify({'error': 'user_vocabulary_id and quality_rating are required'}), 400
    
    if not (0 <= quality_rating <= 5):
        return jsonify({'error': 'quality_rating must be between 0 and 5'}), 400
    
    # Verify ownership
    user_vocab = UserVocabulary.query.get(user_vocabulary_id)
    if not user_vocab or user_vocab.user_id != user_id:
        return jsonify({'error': 'Vocabulary item not found'}), 404
    
    response_time = data.get('response_time_seconds')
    review_type = data.get('review_type', 'flashcard')
    context = data.get('context', 'manual_review')
    
    # Schedule next review
    review_data = vocab_engine.schedule_review(
        user_vocabulary_id=user_vocabulary_id,
        quality_rating=quality_rating,
        response_time_seconds=response_time,
        review_type=review_type,
        context=context
    )
    
    return jsonify(review_data), 200


@vocabulary_bp.route('/practice-session/start', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def start_practice_session():
    """
    Start a vocabulary practice session
    
    Request Body:
    {
        "session_type": "daily_review",
        "focus_area": "business_vocabulary",
        "target_mastery_level": "learning"
    }
    
    Returns:
    {
        "session": {...},
        "practice_activity": {...}
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    session_type = data.get('session_type', 'daily_review')
    focus_area = data.get('focus_area')
    target_mastery_level = data.get('target_mastery_level')
    
    # Start session
    session = vocab_engine.start_practice_session(
        user_id=user_id,
        session_type=session_type,
        focus_area=focus_area,
        target_mastery_level=target_mastery_level
    )
    
    # Generate practice activity
    activity_type = data.get('activity_type', 'flashcard')
    count = data.get('word_count', 10)
    
    practice_activity = vocab_engine.generate_practice_activity(
        user_id=user_id,
        activity_type=activity_type,
        count=count
    )
    
    return jsonify({
        'session': session.to_dict(),
        'practice_activity': practice_activity
    }), 201


@vocabulary_bp.route('/practice-session/<int:session_id>/complete', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def complete_practice_session(session_id):
    """
    Complete a practice session
    
    Request Body:
    {
        "notes": "Great session!"
    }
    
    Returns:
    {
        "session": {...},
        "insights": [...]
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Verify ownership
    session = VocabularyPracticeSession.query.get(session_id)
    if not session or session.user_id != user_id:
        return jsonify({'error': 'Session not found'}), 404
    
    notes = data.get('notes')
    
    # Complete session
    session_data = vocab_engine.complete_practice_session(
        session_id=session_id,
        notes=notes
    )
    
    return jsonify(session_data), 200


@vocabulary_bp.route('/practice-activity', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def generate_practice_activity():
    """
    Generate a vocabulary practice activity
    
    Request Body:
    {
        "activity_type": "multiple_choice",  # flashcard, multiple_choice, fill_blank, spelling, usage
        "word_count": 10,
        "word_ids": [1, 2, 3]  # Optional: specific words
    }
    
    Returns:
    {
        "activity_type": "multiple_choice",
        "questions": [...],
        "total_questions": 10
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    activity_type = data.get('activity_type', 'flashcard')
    count = data.get('word_count', 10)
    word_ids = data.get('word_ids')
    
    # Generate activity
    activity = vocab_engine.generate_practice_activity(
        user_id=user_id,
        words_to_practice=word_ids,
        activity_type=activity_type,
        count=count
    )
    
    return jsonify(activity), 200


# ==================== Mastery Assessment ====================

@vocabulary_bp.route('/mastery', methods=['GET'])
@jwt_required()
@handle_errors
def get_mastery():
    """
    Get vocabulary mastery assessment
    
    Query Params:
    - vocabulary_item_id: Specific word (optional)
    
    Returns:
    {
        "total_words": 150,
        "mastery_breakdown": {...},
        "mastery_percentage": 45.5,
        ...
    }
    """
    user_id = get_jwt_identity()
    vocabulary_item_id = request.args.get('vocabulary_item_id', type=int)
    
    # Get mastery assessment
    mastery = vocab_engine.assess_vocabulary_mastery(
        user_id=user_id,
        vocabulary_item_id=vocabulary_item_id
    )
    
    return jsonify(mastery), 200


# ==================== Word Networks ====================

@vocabulary_bp.route('/word-network/<int:vocabulary_item_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_word_network(vocabulary_item_id):
    """
    Get semantic network for a word
    
    Query Params:
    - max_depth: Network depth (default: 2)
    
    Returns:
    {
        "center_word": {...},
        "network": {
            "nodes": [...],
            "edges": [...]
        },
        "relationships_by_type": {...}
    }
    """
    max_depth = request.args.get('max_depth', 2, type=int)
    
    # Get word network
    network = vocab_engine.get_word_network(
        vocabulary_item_id=vocabulary_item_id,
        max_depth=max_depth
    )
    
    return jsonify(network), 200


@vocabulary_bp.route('/related-words', methods=['GET'])
@jwt_required()
@handle_errors
def get_related_words():
    """
    Find words related to a given word
    
    Query Params:
    - word: Word to find relations for (required)
    - relationship_type: Filter by type (optional)
    - limit: Max results (default: 10)
    
    Returns:
    {
        "word": "happy",
        "related_words": [...]
    }
    """
    word = request.args.get('word')
    if not word:
        return jsonify({'error': 'word parameter is required'}), 400
    
    relationship_type = request.args.get('relationship_type')
    limit = request.args.get('limit', 10, type=int)
    
    # Find related words
    related = vocab_engine.find_related_words(
        word=word,
        relationship_type=relationship_type,
        limit=limit
    )
    
    return jsonify({
        'word': word,
        'related_words': related,
        'count': len(related)
    }), 200


# ==================== Vocabulary Retrieval ====================

@vocabulary_bp.route('/my-vocabulary', methods=['GET'])
@jwt_required()
@handle_errors
def get_my_vocabulary():
    """
    Get user's vocabulary list
    
    Query Params:
    - mastery_level: Filter by mastery level
    - is_favorite: Filter favorites
    - limit: Results per page (default: 50)
    - offset: Pagination offset (default: 0)
    - sort_by: Sort field (added_at, mastery_level, word)
    - order: asc or desc
    
    Returns:
    {
        "vocabulary": [...],
        "total": 150,
        "limit": 50,
        "offset": 0
    }
    """
    user_id = get_jwt_identity()
    
    # Build query
    query = UserVocabulary.query.filter_by(
        user_id=user_id,
        is_active=True
    )
    
    # Filters
    mastery_level = request.args.get('mastery_level')
    if mastery_level:
        query = query.filter(UserVocabulary.mastery_level == mastery_level)
    
    is_favorite = request.args.get('is_favorite', type=bool)
    if is_favorite is not None:
        query = query.filter(UserVocabulary.is_favorite == is_favorite)
    
    # Sorting
    sort_by = request.args.get('sort_by', 'added_at')
    order = request.args.get('order', 'desc')
    
    if hasattr(UserVocabulary, sort_by):
        sort_field = getattr(UserVocabulary, sort_by)
        if order == 'desc':
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
    
    # Pagination
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    total = query.count()
    vocabulary = query.limit(limit).offset(offset).all()
    
    return jsonify({
        'vocabulary': [v.to_dict() for v in vocabulary],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


@vocabulary_bp.route('/vocabulary-item/<int:vocabulary_item_id>', methods=['GET'])
@jwt_required()
@handle_errors
def get_vocabulary_item(vocabulary_item_id):
    """
    Get detailed information about a vocabulary item
    
    Returns:
    {
        "vocabulary_item": {...},
        "user_progress": {...} (if user has this word)
    }
    """
    user_id = get_jwt_identity()
    
    # Get vocabulary item
    vocab_item = VocabularyItem.query.get(vocabulary_item_id)
    if not vocab_item:
        return jsonify({'error': 'Vocabulary item not found'}), 404
    
    response = {
        'vocabulary_item': vocab_item.to_dict()
    }
    
    # Get user's progress if they have this word
    user_vocab = UserVocabulary.query.filter_by(
        user_id=user_id,
        vocabulary_item_id=vocabulary_item_id
    ).first()
    
    if user_vocab:
        response['user_progress'] = user_vocab.to_dict(include_item=False)
    
    return jsonify(response), 200


@vocabulary_bp.route('/search', methods=['GET'])
@jwt_required()
@handle_errors
def search_vocabulary():
    """
    Search vocabulary items
    
    Query Params:
    - query: Search term (required)
    - difficulty_level: Filter by level
    - limit: Max results (default: 20)
    
    Returns:
    {
        "results": [...],
        "count": 5
    }
    """
    search_query = request.args.get('query')
    if not search_query:
        return jsonify({'error': 'query parameter is required'}), 400
    
    difficulty_level = request.args.get('difficulty_level')
    limit = request.args.get('limit', 20, type=int)
    
    # Build search query
    query = VocabularyItem.query.filter(
        VocabularyItem.word.ilike(f'%{search_query}%')
    )
    
    if difficulty_level:
        query = query.filter(VocabularyItem.difficulty_level == difficulty_level)
    
    results = query.limit(limit).all()
    
    return jsonify({
        'results': [r.to_dict() for r in results],
        'count': len(results)
    }), 200


# ==================== Analytics & Statistics ====================

@vocabulary_bp.route('/statistics', methods=['GET'])
@jwt_required()
@handle_errors
def get_statistics():
    """
    Get vocabulary learning statistics
    
    Query Params:
    - time_window_days: Time window (default: 30)
    
    Returns:
    {
        "new_words_learned": 25,
        "words_mastered": 10,
        "review_accuracy": 85.5,
        ...
    }
    """
    user_id = get_jwt_identity()
    time_window_days = request.args.get('time_window_days', 30, type=int)
    
    # Get statistics
    stats = vocab_engine.get_vocabulary_statistics(
        user_id=user_id,
        time_window_days=time_window_days
    )
    
    return jsonify(stats), 200


@vocabulary_bp.route('/review-history', methods=['GET'])
@jwt_required()
@handle_errors
def get_review_history():
    """
    Get vocabulary review history
    
    Query Params:
    - user_vocabulary_id: Filter by word (optional)
    - limit: Results per page (default: 50)
    - offset: Pagination offset (default: 0)
    
    Returns:
    {
        "reviews": [...],
        "total": 100,
        "limit": 50,
        "offset": 0
    }
    """
    user_id = get_jwt_identity()
    
    # Build query
    query = VocabularyReview.query.filter_by(user_id=user_id)
    
    user_vocabulary_id = request.args.get('user_vocabulary_id', type=int)
    if user_vocabulary_id:
        query = query.filter(VocabularyReview.user_vocabulary_id == user_vocabulary_id)
    
    # Pagination
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    total = query.count()
    reviews = query.order_by(VocabularyReview.reviewed_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify({
        'reviews': [r.to_dict() for r in reviews],
        'total': total,
        'limit': limit,
        'offset': offset
    }), 200


# ==================== User Actions ====================

@vocabulary_bp.route('/toggle-favorite/<int:user_vocabulary_id>', methods=['POST'])
@jwt_required()
@handle_errors
def toggle_favorite(user_vocabulary_id):
    """
    Toggle favorite status for a word
    
    Returns:
    {
        "is_favorite": true
    }
    """
    user_id = get_jwt_identity()
    
    # Get user vocabulary
    user_vocab = UserVocabulary.query.get(user_vocabulary_id)
    if not user_vocab or user_vocab.user_id != user_id:
        return jsonify({'error': 'Word not found'}), 404
    
    # Toggle favorite
    user_vocab.is_favorite = not user_vocab.is_favorite
    db.session.commit()
    
    return jsonify({
        'is_favorite': user_vocab.is_favorite
    }), 200


@vocabulary_bp.route('/add-note/<int:user_vocabulary_id>', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def add_note(user_vocabulary_id):
    """
    Add personal note or mnemonic to a word
    
    Request Body:
    {
        "personal_notes": "Remember: amb = both ways",
        "mnemonic_device": "Ambiguous = Am Big? You ask"
    }
    
    Returns:
    {
        "success": true
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get user vocabulary
    user_vocab = UserVocabulary.query.get(user_vocabulary_id)
    if not user_vocab or user_vocab.user_id != user_id:
        return jsonify({'error': 'Word not found'}), 404
    
    # Update notes
    if 'personal_notes' in data:
        user_vocab.personal_notes = data['personal_notes']
    if 'mnemonic_device' in data:
        user_vocab.mnemonic_device = data['mnemonic_device']
    
    db.session.commit()
    
    return jsonify({'success': True}), 200


@vocabulary_bp.route('/archive/<int:user_vocabulary_id>', methods=['POST'])
@jwt_required()
@handle_errors
def archive_word(user_vocabulary_id):
    """
    Archive a word (remove from active learning)
    
    Returns:
    {
        "success": true
    }
    """
    user_id = get_jwt_identity()
    
    # Get user vocabulary
    user_vocab = UserVocabulary.query.get(user_vocabulary_id)
    if not user_vocab or user_vocab.user_id != user_id:
        return jsonify({'error': 'Word not found'}), 404
    
    # Archive
    user_vocab.is_archived = True
    user_vocab.is_active = False
    db.session.commit()
    
    return jsonify({'success': True}), 200


# ==================== Batch Operations ====================

@vocabulary_bp.route('/batch-review', methods=['POST'])
@jwt_required()
@validate_json
@handle_errors
def batch_review():
    """
    Submit multiple word reviews at once
    
    Request Body:
    {
        "reviews": [
            {"user_vocabulary_id": 1, "quality_rating": 5, "response_time_seconds": 2.3},
            {"user_vocabulary_id": 2, "quality_rating": 3, "response_time_seconds": 5.1},
            ...
        ],
        "session_id": 123  # Optional
    }
    
    Returns:
    {
        "processed": 10,
        "failed": 0,
        "results": [...]
    }
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    reviews = data.get('reviews', [])
    session_id = data.get('session_id')
    
    results = []
    failed = 0
    
    for review_data in reviews:
        try:
            user_vocabulary_id = review_data.get('user_vocabulary_id')
            quality_rating = review_data.get('quality_rating')
            
            # Verify ownership
            user_vocab = UserVocabulary.query.get(user_vocabulary_id)
            if not user_vocab or user_vocab.user_id != user_id:
                failed += 1
                results.append({'user_vocabulary_id': user_vocabulary_id, 'error': 'Not found'})
                continue
            
            # Schedule review
            result = vocab_engine.schedule_review(
                user_vocabulary_id=user_vocabulary_id,
                quality_rating=quality_rating,
                response_time_seconds=review_data.get('response_time_seconds'),
                review_type=review_data.get('review_type', 'batch_review'),
                context=f'session_{session_id}' if session_id else 'batch_review'
            )
            
            results.append({
                'user_vocabulary_id': user_vocabulary_id,
                'success': True,
                **result
            })
            
            # Update session if provided
            if session_id:
                session = VocabularyPracticeSession.query.get(session_id)
                if session and session.user_id == user_id:
                    session.words_reviewed += 1
                    if quality_rating >= 3:
                        session.words_correct += 1
                    else:
                        session.words_incorrect += 1
                    
                    # Update words practiced list
                    if not session.words_practiced:
                        session.words_practiced = []
                    if vocab_item_id := user_vocab.vocabulary_item_id:
                        session.words_practiced.append(vocab_item_id)
            
        except Exception as e:
            failed += 1
            results.append({
                'user_vocabulary_id': review_data.get('user_vocabulary_id'),
                'error': str(e)
            })
    
    if session_id:
        db.session.commit()
    
    return jsonify({
        'processed': len(reviews) - failed,
        'failed': failed,
        'results': results
    }), 200



# ==================== Activity Integration ====================

@vocabulary_bp.route('/reinforcement-stats', methods=['GET'])
@jwt_required()
@handle_errors
def get_reinforcement_stats():
    """
    Get vocabulary reinforcement statistics from activities
    
    Query Params:
    - days: Time window (default: 30)
    
    Returns:
    {
        "total_exposures": 150,
        "production_uses": 45,
        "activities_with_vocab": 32,
        "top_reinforced_words": [...]
    }
    """
    user_id = get_jwt_identity()
    days = request.args.get('days', 30, type=int)
    
    # Get reinforcement statistics
    from app.services.vocabulary_integration_service import VocabularyIntegrationService
    vocab_integration = VocabularyIntegrationService()
    
    stats = vocab_integration.get_vocabulary_reinforcement_stats(
        user_id=user_id,
        days=days
    )
    
    return jsonify(stats), 200


# Register blueprint with app in __init__.py
