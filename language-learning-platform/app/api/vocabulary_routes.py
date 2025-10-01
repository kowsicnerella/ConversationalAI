from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, VocabularyWord, User, LearningSession
from datetime import datetime
from sqlalchemy import or_, and_

vocabulary_bp = Blueprint('vocabulary', __name__)

@vocabulary_bp.route('/words', methods=['GET'])
@jwt_required()
def get_vocabulary_words():
    """Get vocabulary words with filtering and pagination"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search = request.args.get('search', '').strip()
        difficulty = request.args.get('difficulty', '').strip()
        mastery_level = request.args.get('mastery_level', '').strip()
        sort_by = request.args.get('sort_by', 'created_at').strip()
        sort_order = request.args.get('sort_order', 'desc').strip()
        
        # Build query
        query = VocabularyWord.query.filter_by(user_id=user_id)
        
        # Apply filters
        if search:
            query = query.filter(or_(
                VocabularyWord.english_word.ilike(f'%{search}%'),
                VocabularyWord.telugu_translation.ilike(f'%{search}%'),
                VocabularyWord.definition.ilike(f'%{search}%')
            ))
        
        if difficulty and difficulty in ['beginner', 'intermediate', 'advanced']:
            query = query.filter_by(difficulty_level=difficulty)
        
        if mastery_level and mastery_level in ['learning', 'familiar', 'mastered']:
            query = query.filter_by(mastery_level=mastery_level)
        
        # Apply sorting
        if sort_by == 'alphabetical':
            order_column = VocabularyWord.english_word
        elif sort_by == 'difficulty':
            order_column = VocabularyWord.difficulty_level
        elif sort_by == 'mastery':
            order_column = VocabularyWord.mastery_level
        else:
            order_column = VocabularyWord.created_at
        
        if sort_order == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        words = []
        for word in pagination.items:
            words.append({
                'id': word.id,
                'english_word': word.english_word,
                'telugu_translation': word.telugu_translation,
                'phonetic_spelling': word.phonetic_spelling,
                'definition': word.definition,
                'example_sentence': word.example_sentence,
                'difficulty_level': word.difficulty_level,
                'mastery_level': word.mastery_level,
                'practice_count': word.practice_count,
                'correct_count': word.correct_count,
                'created_at': word.created_at.isoformat() if word.created_at else None,
                'last_practiced': word.last_practiced.isoformat() if word.last_practiced else None
            })
        
        return jsonify({
            'message': 'Vocabulary words retrieved successfully',
            'telugu_message': 'పదజాలం పదాలు విజయవంతంగా పొందబడ్డాయి',
            'words': words,
            'pagination': {
                'page': pagination.page,
                'pages': pagination.pages,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting vocabulary words: {str(e)}")
        return jsonify({
            'error': 'Failed to get vocabulary words',
            'telugu_error': 'పదజాలం పదాలు పొందడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/words', methods=['POST'])
@jwt_required()
def add_vocabulary_word():
    """Add a new vocabulary word"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['english_word', 'telugu_translation']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({
                    'error': f'{field} is required',
                    'telugu_error': f'{field} అవసరం'
                }), 400
        
        english_word = data['english_word'].strip().lower()
        telugu_translation = data['telugu_translation'].strip()
        
        # Check if word already exists for this user
        existing_word = VocabularyWord.query.filter_by(
            user_id=user_id, 
            english_word=english_word
        ).first()
        
        if existing_word:
            return jsonify({
                'error': 'Word already exists in your vocabulary',
                'telugu_error': 'పదం మీ పదజాలంలో ఇప్పటికే ఉంది'
            }), 409
        
        # Create new vocabulary word
        vocab_word = VocabularyWord(
            user_id=user_id,
            english_word=english_word,
            telugu_translation=telugu_translation,
            phonetic_spelling=data.get('phonetic_spelling', '').strip(),
            definition=data.get('definition', '').strip(),
            example_sentence=data.get('example_sentence', '').strip(),
            difficulty_level=data.get('difficulty_level', 'beginner'),
            mastery_level='learning',
            created_at=datetime.utcnow()
        )
        
        db.session.add(vocab_word)
        db.session.commit()
        
        return jsonify({
            'message': 'Vocabulary word added successfully',
            'telugu_message': 'పదజాలం పదం విజయవంతంగా జోడించబడింది',
            'word': {
                'id': vocab_word.id,
                'english_word': vocab_word.english_word,
                'telugu_translation': vocab_word.telugu_translation,
                'difficulty_level': vocab_word.difficulty_level,
                'mastery_level': vocab_word.mastery_level
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding vocabulary word: {str(e)}")
        return jsonify({
            'error': 'Failed to add vocabulary word',
            'telugu_error': 'పదజాలం పదం జోడించడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/words/<int:word_id>', methods=['PUT'])
@jwt_required()
def update_vocabulary_word(word_id):
    """Update a vocabulary word"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        word = VocabularyWord.query.filter_by(id=word_id, user_id=user_id).first()
        if not word:
            return jsonify({
                'error': 'Vocabulary word not found',
                'telugu_error': 'పదజాలం పదం కనుగొనబడలేదు'
            }), 404
        
        # Update fields
        if 'telugu_translation' in data:
            word.telugu_translation = data['telugu_translation'].strip()
        if 'phonetic_spelling' in data:
            word.phonetic_spelling = data['phonetic_spelling'].strip()
        if 'definition' in data:
            word.definition = data['definition'].strip()
        if 'example_sentence' in data:
            word.example_sentence = data['example_sentence'].strip()
        if 'difficulty_level' in data and data['difficulty_level'] in ['beginner', 'intermediate', 'advanced']:
            word.difficulty_level = data['difficulty_level']
        if 'mastery_level' in data and data['mastery_level'] in ['learning', 'familiar', 'mastered']:
            word.mastery_level = data['mastery_level']
        
        word.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Vocabulary word updated successfully',
            'telugu_message': 'పదజాలం పదం విజయవంతంగా నవీకరించబడింది',
            'word': {
                'id': word.id,
                'english_word': word.english_word,
                'telugu_translation': word.telugu_translation,
                'difficulty_level': word.difficulty_level,
                'mastery_level': word.mastery_level
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating vocabulary word: {str(e)}")
        return jsonify({
            'error': 'Failed to update vocabulary word',
            'telugu_error': 'పదజాలం పదం నవీకరించడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/words/<int:word_id>', methods=['DELETE'])
@jwt_required()
def delete_vocabulary_word(word_id):
    """Delete a vocabulary word"""
    try:
        user_id = int(get_jwt_identity())
        
        word = VocabularyWord.query.filter_by(id=word_id, user_id=user_id).first()
        if not word:
            return jsonify({
                'error': 'Vocabulary word not found',
                'telugu_error': 'పదజాలం పదం కనుగొనబడలేదు'
            }), 404
        
        db.session.delete(word)
        db.session.commit()
        
        return jsonify({
            'message': 'Vocabulary word deleted successfully',
            'telugu_message': 'పదజాలం పదం విజయవంతంగా తొలగించబడింది'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting vocabulary word: {str(e)}")
        return jsonify({
            'error': 'Failed to delete vocabulary word',
            'telugu_error': 'పదజాలం పదం తొలగించడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/words/<int:word_id>/examples', methods=['GET'])
@jwt_required()
def get_word_examples(word_id):
    """Get usage examples for a vocabulary word"""
    try:
        user_id = int(get_jwt_identity())
        
        word = VocabularyWord.query.filter_by(id=word_id, user_id=user_id).first()
        if not word:
            return jsonify({
                'error': 'Vocabulary word not found',
                'telugu_error': 'పదజాలం పదం కనుగొనబడలేదు'
            }), 404
        
        # In a real implementation, you might generate examples using AI
        # For now, return the stored example sentence
        examples = []
        if word.example_sentence:
            examples.append({
                'sentence': word.example_sentence,
                'translation': f"Telugu translation of: {word.example_sentence}",
                'difficulty': word.difficulty_level
            })
        
        return jsonify({
            'message': 'Word examples retrieved successfully',
            'telugu_message': 'పద ఉదాహరణలు విజయవంతంగా పొందబడ్డాయి',
            'word': word.english_word,
            'examples': examples
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting word examples: {str(e)}")
        return jsonify({
            'error': 'Failed to get word examples',
            'telugu_error': 'పద ఉదాహరణలు పొందడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/words/<int:word_id>/practice-result', methods=['POST'])
@jwt_required()
def log_practice_result(word_id):
    """Log practice result for a vocabulary word"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        word = VocabularyWord.query.filter_by(id=word_id, user_id=user_id).first()
        if not word:
            return jsonify({
                'error': 'Vocabulary word not found',
                'telugu_error': 'పదజాలం పదం కనుగొనబడలేదు'
            }), 404
        
        is_correct = data.get('is_correct', False)
        practice_type = data.get('practice_type', 'general')  # flashcard, quiz, etc.
        
        # Update practice statistics
        word.practice_count = (word.practice_count or 0) + 1
        if is_correct:
            word.correct_count = (word.correct_count or 0) + 1
        
        word.last_practiced = datetime.utcnow()
        
        # Update mastery level based on performance
        if word.practice_count >= 3:
            accuracy = word.correct_count / word.practice_count
            if accuracy >= 0.8:
                word.mastery_level = 'mastered'
            elif accuracy >= 0.6:
                word.mastery_level = 'familiar'
            else:
                word.mastery_level = 'learning'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Practice result logged successfully',
            'telugu_message': 'అభ్యాస ఫలితం విజయవంతంగా నమోదు చేయబడింది',
            'word': {
                'id': word.id,
                'mastery_level': word.mastery_level,
                'practice_count': word.practice_count,
                'correct_count': word.correct_count,
                'accuracy': word.correct_count / word.practice_count if word.practice_count > 0 else 0
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error logging practice result: {str(e)}")
        return jsonify({
            'error': 'Failed to log practice result',
            'telugu_error': 'అభ్యాస ఫలితం నమోదు చేయడంలో విఫలం'
        }), 500

@vocabulary_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_vocabulary_stats():
    """Get vocabulary statistics for the user"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get overall statistics
        total_words = VocabularyWord.query.filter_by(user_id=user_id).count()
        learning_words = VocabularyWord.query.filter_by(user_id=user_id, mastery_level='learning').count()
        familiar_words = VocabularyWord.query.filter_by(user_id=user_id, mastery_level='familiar').count()
        mastered_words = VocabularyWord.query.filter_by(user_id=user_id, mastery_level='mastered').count()
        
        # Get difficulty distribution
        beginner_words = VocabularyWord.query.filter_by(user_id=user_id, difficulty_level='beginner').count()
        intermediate_words = VocabularyWord.query.filter_by(user_id=user_id, difficulty_level='intermediate').count()
        advanced_words = VocabularyWord.query.filter_by(user_id=user_id, difficulty_level='advanced').count()
        
        return jsonify({
            'message': 'Vocabulary statistics retrieved successfully',
            'telugu_message': 'పదజాలం గణాంకాలు విజయవంతంగా పొందబడ్డాయి',
            'stats': {
                'total_words': total_words,
                'mastery_distribution': {
                    'learning': learning_words,
                    'familiar': familiar_words,
                    'mastered': mastered_words
                },
                'difficulty_distribution': {
                    'beginner': beginner_words,
                    'intermediate': intermediate_words,
                    'advanced': advanced_words
                },
                'mastery_percentage': {
                    'learning': (learning_words / total_words * 100) if total_words > 0 else 0,
                    'familiar': (familiar_words / total_words * 100) if total_words > 0 else 0,
                    'mastered': (mastered_words / total_words * 100) if total_words > 0 else 0
                }
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting vocabulary stats: {str(e)}")
        return jsonify({
            'error': 'Failed to get vocabulary statistics',
            'telugu_error': 'పదజాలం గణాంకాలు పొందడంలో విఫలం'
        }), 500