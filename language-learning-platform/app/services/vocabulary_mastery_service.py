"""
Vocabulary Mastery Engine - Phase 5
Comprehensive vocabulary learning system with SM-2 spaced repetition algorithm
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import func, and_, or_
from app.models import db
from app.models.vocabulary_mastery import (
    VocabularyItem,
    UserVocabulary,
    VocabularyReview,
    WordRelationship,
    VocabularyPracticeSession,
)
from app.services.llm_service import LLMService
import json


class VocabularyMasteryEngine:
    """
    Advanced vocabulary learning engine with spaced repetition
    Implements SM-2 algorithm for optimal review scheduling
    """
    
    def __init__(self):
        """Initialize with LLM service for AI-generated content"""
        self._llm_service = None
    
    @property
    def llm_service(self):
        """Lazy load LLM service to prevent import-time errors"""
        if self._llm_service is None:
            self._llm_service = LLMService()
        return self._llm_service
    
    # ==================== Vocabulary Introduction ====================
    
    def introduce_new_word(
        self,
        word: str,
        difficulty_level: str,
        user_id: int = None,
        generate_content: bool = True
    ) -> VocabularyItem:
        """
        Introduce a new word to the system
        
        Args:
            word: The word or phrase to add
            difficulty_level: CEFR level (A1-C2)
            user_id: Optional user ID to add to their vocabulary
            generate_content: Whether to use AI to generate content
            
        Returns:
            VocabularyItem with all details populated
        """
        # Check if word already exists
        existing_word = VocabularyItem.query.filter(
            func.lower(VocabularyItem.word) == word.lower()
        ).first()
        
        if existing_word:
            # Add to user's vocabulary if provided
            if user_id:
                self.add_word_to_user_vocabulary(user_id, existing_word.id)
            return existing_word
        
        # Generate comprehensive word data with AI
        if generate_content:
            word_data = self._generate_word_content(word, difficulty_level)
        else:
            word_data = {
                'word': word,
                'difficulty_level': difficulty_level
            }
        
        # Create vocabulary item
        vocab_item = VocabularyItem(
            word=word,
            word_type=word_data.get('word_type'),
            difficulty_level=difficulty_level,
            english_definition=word_data.get('definition'),
            telugu_translation=word_data.get('telugu_translation'),
            pronunciation_ipa=word_data.get('pronunciation_ipa'),
            pronunciation_guide=word_data.get('pronunciation_guide'),
            example_sentences=word_data.get('example_sentences', []),
            common_collocations=word_data.get('collocations', []),
            usage_notes=word_data.get('usage_notes'),
            formality_level=word_data.get('formality_level'),
            topic_categories=word_data.get('categories', []),
            frequency_rank=word_data.get('frequency_rank'),
            is_high_priority=word_data.get('is_high_priority', False),
        )
        
        db.session.add(vocab_item)
        db.session.commit()
        
        # Add to user's vocabulary if provided
        if user_id:
            self.add_word_to_user_vocabulary(user_id, vocab_item.id)
        
        # Generate word relationships
        if generate_content:
            self._create_word_relationships(vocab_item.id, word, difficulty_level)
        
        return vocab_item
    
    def add_word_to_user_vocabulary(
        self,
        user_id: int,
        vocabulary_item_id: int,
        context: str = None,
        activity_id: int = None
    ) -> UserVocabulary:
        """
        Add a word to user's personal vocabulary
        Initialize with SM-2 parameters
        
        Args:
            user_id: User ID
            vocabulary_item_id: ID of vocabulary item
            context: How user encountered this word
            activity_id: Activity where word was encountered
            
        Returns:
            UserVocabulary object
        """
        # Check if already exists
        existing = UserVocabulary.query.filter_by(
            user_id=user_id,
            vocabulary_item_id=vocabulary_item_id
        ).first()
        
        if existing:
            # Mark as seen again
            existing.mark_as_seen(context)
            db.session.commit()
            return existing
        
        # Create new user vocabulary
        user_vocab = UserVocabulary(
            user_id=user_id,
            vocabulary_item_id=vocabulary_item_id,
            mastery_level='new',
            confidence_score=0.0,
            repetition_number=0,
            easiness_factor=2.5,  # SM-2 default
            interval_days=1,
            next_review_date=datetime.utcnow() + timedelta(days=1),
            times_seen=1,
            contexts_encountered=[context] if context else [],
            first_encountered_activity_id=activity_id,
            needs_review=True,
        )
        
        db.session.add(user_vocab)
        db.session.commit()
        
        return user_vocab
    
    def introduce_words_from_context(
        self,
        user_id: int,
        text: str,
        context: str,
        activity_id: int = None,
        difficulty_level: str = 'B1'
    ) -> List[UserVocabulary]:
        """
        Extract and introduce new words from a text passage
        
        Args:
            user_id: User ID
            text: Text containing vocabulary
            context: Context (reading passage, dialogue, etc.)
            activity_id: Related activity ID
            difficulty_level: Target difficulty level
            
        Returns:
            List of UserVocabulary objects for new words
        """
        # Use AI to extract important vocabulary
        new_words = self._extract_vocabulary_from_text(text, difficulty_level)
        
        introduced_words = []
        for word_info in new_words:
            try:
                # Introduce word to system
                vocab_item = self.introduce_new_word(
                    word=word_info['word'],
                    difficulty_level=difficulty_level,
                    user_id=None,  # Don't add yet
                    generate_content=False  # Already have data from extraction
                )
                
                # Update with extracted data
                vocab_item.word_type = word_info.get('type')
                vocab_item.english_definition = word_info.get('definition')
                
                # Add to user vocabulary
                user_vocab = self.add_word_to_user_vocabulary(
                    user_id=user_id,
                    vocabulary_item_id=vocab_item.id,
                    context=context,
                    activity_id=activity_id
                )
                
                introduced_words.append(user_vocab)
                
            except Exception as e:
                print(f"Error introducing word {word_info.get('word')}: {e}")
                continue
        
        return introduced_words
    
    # ==================== Spaced Repetition Scheduling ====================
    
    def get_words_due_for_review(
        self,
        user_id: int,
        limit: int = 20,
        mastery_levels: List[str] = None
    ) -> List[UserVocabulary]:
        """
        Get words that are due for review using SM-2 schedule
        
        Args:
            user_id: User ID
            limit: Maximum words to return
            mastery_levels: Filter by mastery levels
            
        Returns:
            List of UserVocabulary objects due for review
        """
        query = UserVocabulary.query.filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.is_active == True,
            UserVocabulary.is_archived == False,
            or_(
                UserVocabulary.next_review_date <= datetime.utcnow(),
                UserVocabulary.needs_review == True
            )
        )
        
        if mastery_levels:
            query = query.filter(UserVocabulary.mastery_level.in_(mastery_levels))
        
        # Prioritize by:
        # 1. Overdue words (oldest first)
        # 2. Lower mastery levels
        # 3. Words user struggles with
        words_due = query.order_by(
            UserVocabulary.next_review_date.asc(),
            UserVocabulary.mastery_level.asc(),
            UserVocabulary.times_forgotten.desc()
        ).limit(limit).all()
        
        return words_due
    
    def schedule_review(
        self,
        user_vocabulary_id: int,
        quality_rating: int,
        response_time_seconds: float = None,
        review_type: str = 'flashcard',
        context: str = 'scheduled_review'
    ) -> Dict:
        """
        Schedule next review using SM-2 algorithm
        
        Args:
            user_vocabulary_id: UserVocabulary ID
            quality_rating: 0-5 quality rating for SM-2
            response_time_seconds: How long user took to recall
            review_type: Type of review (flashcard, quiz, etc.)
            context: Review context
            
        Returns:
            Dictionary with next review date and updated stats
        """
        user_vocab = UserVocabulary.query.get(user_vocabulary_id)
        if not user_vocab:
            raise ValueError(f"UserVocabulary {user_vocabulary_id} not found")
        
        # Calculate next review using SM-2
        next_review_date = user_vocab.calculate_next_review(quality_rating)
        
        # Update confidence score based on quality
        confidence_delta = (quality_rating - 2.5) * 10  # -25 to +25
        user_vocab.confidence_score = max(0, min(100, 
            user_vocab.confidence_score + confidence_delta
        ))
        
        # Log the review
        review = VocabularyReview(
            user_vocabulary_id=user_vocabulary_id,
            user_id=user_vocab.user_id,
            review_type=review_type,
            quality_rating=quality_rating,
            was_correct=(quality_rating >= 3),
            response_time_seconds=response_time_seconds,
            context_type=context,
        )
        
        db.session.add(review)
        db.session.commit()
        
        return {
            'next_review_date': next_review_date.isoformat(),
            'interval_days': user_vocab.interval_days,
            'mastery_level': user_vocab.mastery_level,
            'confidence_score': user_vocab.confidence_score,
            'repetition_number': user_vocab.repetition_number,
            'easiness_factor': user_vocab.easiness_factor
        }
    
    # ==================== Practice Session Management ====================
    
    def start_practice_session(
        self,
        user_id: int,
        session_type: str = 'daily_review',
        focus_area: str = None,
        target_mastery_level: str = None
    ) -> VocabularyPracticeSession:
        """
        Start a vocabulary practice session
        
        Args:
            user_id: User ID
            session_type: Type of session
            focus_area: Topic/category focus
            target_mastery_level: Which level to practice
            
        Returns:
            VocabularyPracticeSession object
        """
        session = VocabularyPracticeSession(
            user_id=user_id,
            session_type=session_type,
            focus_area=focus_area,
            target_mastery_level=target_mastery_level,
            words_practiced=[],
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    def complete_practice_session(
        self,
        session_id: int,
        notes: str = None
    ) -> Dict:
        """
        Complete a practice session and calculate final stats
        
        Args:
            session_id: Session ID
            notes: Optional session notes
            
        Returns:
            Session summary dictionary
        """
        session = VocabularyPracticeSession.query.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.complete_session()
        if notes:
            session.notes = notes
        
        db.session.commit()
        
        # Generate insights
        insights = self._generate_session_insights(session)
        
        return {
            **session.to_dict(),
            'insights': insights
        }
    
    def generate_practice_activity(
        self,
        user_id: int,
        words_to_practice: List[int] = None,
        activity_type: str = 'flashcard',
        count: int = 10
    ) -> Dict:
        """
        Generate a vocabulary practice activity
        
        Args:
            user_id: User ID
            words_to_practice: Specific word IDs (if None, use due words)
            activity_type: flashcard, multiple_choice, fill_blank, etc.
            count: Number of words to practice
            
        Returns:
            Practice activity dictionary
        """
        # Get words to practice
        if words_to_practice:
            user_vocabs = UserVocabulary.query.filter(
                UserVocabulary.id.in_(words_to_practice)
            ).all()
        else:
            user_vocabs = self.get_words_due_for_review(user_id, limit=count)
        
        if not user_vocabs:
            return {
                'activity_type': activity_type,
                'words': [],
                'message': 'No words available for practice'
            }
        
        # Generate activity based on type
        if activity_type == 'flashcard':
            return self._generate_flashcard_activity(user_vocabs)
        elif activity_type == 'multiple_choice':
            return self._generate_multiple_choice_activity(user_vocabs)
        elif activity_type == 'fill_blank':
            return self._generate_fill_blank_activity(user_vocabs)
        elif activity_type == 'spelling':
            return self._generate_spelling_activity(user_vocabs)
        elif activity_type == 'usage':
            return self._generate_usage_activity(user_vocabs)
        else:
            return {
                'error': f'Unknown activity type: {activity_type}'
            }
    
    # ==================== Mastery Assessment ====================
    
    def assess_vocabulary_mastery(
        self,
        user_id: int,
        vocabulary_item_id: int = None
    ) -> Dict:
        """
        Assess user's vocabulary mastery
        
        Args:
            user_id: User ID
            vocabulary_item_id: Specific word (if None, assess all)
            
        Returns:
            Mastery assessment dictionary
        """
        if vocabulary_item_id:
            user_vocab = UserVocabulary.query.filter_by(
                user_id=user_id,
                vocabulary_item_id=vocabulary_item_id
            ).first()
            
            if not user_vocab:
                return {'error': 'Word not found in user vocabulary'}
            
            return self._assess_single_word_mastery(user_vocab)
        else:
            return self._assess_overall_mastery(user_id)
    
    def _assess_single_word_mastery(self, user_vocab: UserVocabulary) -> Dict:
        """Assess mastery of a single word"""
        # Calculate comprehensive mastery score
        factors = {
            'repetitions': min(100, user_vocab.repetition_number * 15),
            'confidence': user_vocab.confidence_score or 0,
            'accuracy': (user_vocab.recognition_accuracy or 0 + 
                        user_vocab.production_accuracy or 0) / 2,
            'retention': 100 - (user_vocab.times_forgotten * 20),
            'consistency': min(100, user_vocab.current_streak_days * 10),
        }
        
        overall_score = sum(factors.values()) / len(factors)
        
        return {
            'vocabulary_item_id': user_vocab.vocabulary_item_id,
            'word': user_vocab.vocabulary_item.word if user_vocab.vocabulary_item else None,
            'mastery_level': user_vocab.mastery_level,
            'overall_mastery_score': round(overall_score, 2),
            'factors': factors,
            'repetition_number': user_vocab.repetition_number,
            'confidence_score': user_vocab.confidence_score,
            'current_streak_days': user_vocab.current_streak_days,
            'times_forgotten': user_vocab.times_forgotten,
            'next_review_date': user_vocab.next_review_date.isoformat() if user_vocab.next_review_date else None,
            'recommendation': self._get_mastery_recommendation(user_vocab, overall_score)
        }
    
    def _assess_overall_mastery(self, user_id: int) -> Dict:
        """Assess overall vocabulary mastery"""
        user_vocabs = UserVocabulary.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        if not user_vocabs:
            return {
                'total_words': 0,
                'message': 'No vocabulary tracked yet'
            }
        
        # Count by mastery level
        mastery_counts = {
            'new': 0,
            'learning': 0,
            'familiar': 0,
            'mastered': 0
        }
        
        for uv in user_vocabs:
            mastery_counts[uv.mastery_level] = mastery_counts.get(uv.mastery_level, 0) + 1
        
        total_words = len(user_vocabs)
        mastery_percentage = (mastery_counts.get('mastered', 0) / total_words) * 100 if total_words > 0 else 0
        
        # Calculate average metrics
        avg_confidence = sum(uv.confidence_score or 0 for uv in user_vocabs) / total_words
        avg_repetitions = sum(uv.repetition_number for uv in user_vocabs) / total_words
        
        # Words due for review
        due_count = len([uv for uv in user_vocabs if uv.needs_review or 
                        (uv.next_review_date and uv.next_review_date <= datetime.utcnow())])
        
        return {
            'total_words': total_words,
            'mastery_breakdown': mastery_counts,
            'mastery_percentage': round(mastery_percentage, 2),
            'average_confidence': round(avg_confidence, 2),
            'average_repetitions': round(avg_repetitions, 2),
            'words_due_for_review': due_count,
            'estimated_active_vocabulary': mastery_counts.get('familiar', 0) + mastery_counts.get('mastered', 0),
            'learning_velocity': self._calculate_learning_velocity(user_id),
            'recommendations': self._generate_vocabulary_recommendations(user_id, user_vocabs)
        }
    
    # ==================== Word Networks ====================
    
    def get_word_network(
        self,
        vocabulary_item_id: int,
        max_depth: int = 2
    ) -> Dict:
        """
        Get semantic network of related words
        
        Args:
            vocabulary_item_id: Word ID
            max_depth: How many levels of relationships to fetch
            
        Returns:
            Network dictionary with nodes and edges
        """
        vocab_item = VocabularyItem.query.get(vocabulary_item_id)
        if not vocab_item:
            return {'error': 'Word not found'}
        
        # Get direct relationships
        relationships = WordRelationship.query.filter(
            or_(
                WordRelationship.word_id == vocabulary_item_id,
                and_(
                    WordRelationship.related_word_id == vocabulary_item_id,
                    WordRelationship.is_bidirectional == True
                )
            )
        ).all()
        
        # Build network
        nodes = {vocabulary_item_id: vocab_item.to_dict()}
        edges = []
        
        for rel in relationships:
            # Add related word as node
            if rel.related_word_id not in nodes:
                if rel.related_word:
                    nodes[rel.related_word_id] = rel.related_word.to_dict()
            
            # Add edge
            edges.append({
                'from': rel.word_id,
                'to': rel.related_word_id,
                'type': rel.relationship_type,
                'strength': rel.strength,
                'example': rel.example_usage
            })
        
        # Group by relationship type
        relationships_by_type = {}
        for edge in edges:
            rel_type = edge['type']
            if rel_type not in relationships_by_type:
                relationships_by_type[rel_type] = []
            relationships_by_type[rel_type].append(edge)
        
        return {
            'center_word': vocab_item.to_dict(),
            'network': {
                'nodes': list(nodes.values()),
                'edges': edges
            },
            'relationships_by_type': relationships_by_type,
            'total_related_words': len(nodes) - 1
        }
    
    def find_related_words(
        self,
        word: str,
        relationship_type: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find words related to a given word
        
        Args:
            word: Word to find relations for
            relationship_type: Filter by relationship type
            limit: Maximum results
            
        Returns:
            List of related words with relationship info
        """
        vocab_item = VocabularyItem.query.filter(
            func.lower(VocabularyItem.word) == word.lower()
        ).first()
        
        if not vocab_item:
            return []
        
        query = WordRelationship.query.filter(
            WordRelationship.word_id == vocab_item.id
        )
        
        if relationship_type:
            query = query.filter(WordRelationship.relationship_type == relationship_type)
        
        relationships = query.order_by(WordRelationship.strength.desc()).limit(limit).all()
        
        return [rel.to_dict(include_related_word=True) for rel in relationships]
    
    # ==================== Analytics & Insights ====================
    
    def get_vocabulary_statistics(
        self,
        user_id: int,
        time_window_days: int = 30
    ) -> Dict:
        """
        Get comprehensive vocabulary learning statistics
        
        Args:
            user_id: User ID
            time_window_days: Time window for statistics
            
        Returns:
            Statistics dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Get vocabulary added in time window
        new_words = UserVocabulary.query.filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.added_at >= cutoff_date
        ).count()
        
        # Get words mastered in time window
        mastered_words = UserVocabulary.query.filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.mastered_at >= cutoff_date
        ).count()
        
        # Get reviews in time window
        reviews = VocabularyReview.query.filter(
            VocabularyReview.user_id == user_id,
            VocabularyReview.reviewed_at >= cutoff_date
        ).all()
        
        total_reviews = len(reviews)
        correct_reviews = len([r for r in reviews if r.was_correct])
        
        # Get practice sessions in time window
        sessions = VocabularyPracticeSession.query.filter(
            VocabularyPracticeSession.user_id == user_id,
            VocabularyPracticeSession.started_at >= cutoff_date,
            VocabularyPracticeSession.is_completed == True
        ).all()
        
        total_practice_time = sum(s.duration_seconds or 0 for s in sessions)
        
        # Current status
        all_user_vocab = UserVocabulary.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        total_active = len(all_user_vocab)
        due_for_review = len([uv for uv in all_user_vocab if uv.needs_review])
        
        return {
            'time_window_days': time_window_days,
            'new_words_learned': new_words,
            'words_mastered': mastered_words,
            'total_reviews': total_reviews,
            'review_accuracy': round((correct_reviews / total_reviews * 100) if total_reviews > 0 else 0, 2),
            'practice_sessions': len(sessions),
            'total_practice_time_minutes': round(total_practice_time / 60, 2),
            'average_session_duration_minutes': round((total_practice_time / len(sessions) / 60) if sessions else 0, 2),
            'current_active_vocabulary': total_active,
            'words_due_for_review': due_for_review,
            'learning_rate': round(new_words / time_window_days, 2),
            'mastery_rate': round(mastered_words / time_window_days, 2) if time_window_days > 0 else 0
        }
    
    # ==================== Helper Methods ====================
    
    def _generate_word_content(self, word: str, difficulty_level: str) -> Dict:
        """Generate comprehensive word content using AI"""
        try:
            prompt = f"""
            Generate comprehensive information for the English word: "{word}"
            Difficulty level: {difficulty_level}
            
            Provide:
            1. Word type (noun, verb, adjective, etc.)
            2. Clear English definition
            3. Telugu translation
            4. IPA pronunciation
            5. Simple pronunciation guide
            6. 3 example sentences showing different contexts
            7. Common collocations (words commonly used with this word)
            8. Usage notes (special considerations)
            9. Formality level (formal, informal, neutral)
            10. Topic categories (business, daily life, academic, etc.)
            11. Frequency rank (1-10000, estimate)
            
            Return as JSON with these keys:
            word_type, definition, telugu_translation, pronunciation_ipa, pronunciation_guide,
            example_sentences (array), collocations (array), usage_notes, formality_level,
            categories (array), frequency_rank, is_high_priority (boolean)
            """
            
            response = self.llm_service.generate_content(
                prompt=prompt,
                temperature=0.3,
                response_format='json'
            )
            
            return json.loads(response) if isinstance(response, str) else response
            
        except Exception as e:
            print(f"Error generating word content: {e}")
            return {
                'word_type': 'unknown',
                'definition': f'Definition for {word}',
                'telugu_translation': '',
                'example_sentences': [],
                'collocations': []
            }
    
    def _create_word_relationships(
        self,
        vocabulary_item_id: int,
        word: str,
        difficulty_level: str
    ):
        """Create semantic relationships for a word using AI"""
        try:
            prompt = f"""
            For the word "{word}" (level: {difficulty_level}), identify related words:
            
            1. 3 synonyms (similar meaning)
            2. 3 antonyms (opposite meaning)
            3. 3 common collocations
            4. 2 derivative words (same root)
            
            For each related word, provide:
            - The word itself
            - Relationship type
            - Relationship strength (0-1)
            - Example usage showing the relationship
            
            Return as JSON array with objects containing:
            related_word, relationship_type, strength, example_usage
            """
            
            response = self.llm_service.generate_content(
                prompt=prompt,
                temperature=0.3,
                response_format='json'
            )
            
            relationships_data = json.loads(response) if isinstance(response, str) else response
            
            # Create relationship records
            for rel_data in relationships_data.get('relationships', []):
                # Find or create related word
                related_word = VocabularyItem.query.filter(
                    func.lower(VocabularyItem.word) == rel_data['related_word'].lower()
                ).first()
                
                if not related_word:
                    # Create minimal entry for related word
                    related_word = VocabularyItem(
                        word=rel_data['related_word'],
                        difficulty_level=difficulty_level
                    )
                    db.session.add(related_word)
                    db.session.flush()
                
                # Create relationship
                relationship = WordRelationship(
                    word_id=vocabulary_item_id,
                    related_word_id=related_word.id,
                    relationship_type=rel_data['relationship_type'],
                    strength=rel_data.get('strength', 0.8),
                    example_usage=rel_data.get('example_usage'),
                    is_bidirectional=(rel_data['relationship_type'] in ['synonym', 'antonym'])
                )
                
                db.session.add(relationship)
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error creating word relationships: {e}")
    
    def _extract_vocabulary_from_text(
        self,
        text: str,
        difficulty_level: str
    ) -> List[Dict]:
        """Extract important vocabulary from text using AI"""
        try:
            prompt = f"""
            Extract important vocabulary words from this text for a {difficulty_level} level learner:
            
            "{text}"
            
            Identify 5-10 key words that are:
            1. Important for understanding the text
            2. Appropriate for {difficulty_level} level
            3. Useful for general English learning
            
            For each word provide:
            - word
            - type (noun, verb, etc.)
            - definition
            - how it's used in this text
            
            Return as JSON array
            """
            
            response = self.llm_service.generate_content(
                prompt=prompt,
                temperature=0.3,
                response_format='json'
            )
            
            return json.loads(response) if isinstance(response, str) else []
            
        except Exception as e:
            print(f"Error extracting vocabulary: {e}")
            return []
    
    def _generate_flashcard_activity(self, user_vocabs: List[UserVocabulary]) -> Dict:
        """Generate flashcard practice activity"""
        flashcards = []
        
        for uv in user_vocabs:
            if not uv.vocabulary_item:
                continue
            
            flashcards.append({
                'user_vocabulary_id': uv.id,
                'word': uv.vocabulary_item.word,
                'definition': uv.vocabulary_item.english_definition,
                'telugu_translation': uv.vocabulary_item.telugu_translation,
                'pronunciation': uv.vocabulary_item.pronunciation_guide,
                'example_sentences': uv.vocabulary_item.example_sentences,
                'mastery_level': uv.mastery_level
            })
        
        return {
            'activity_type': 'flashcard',
            'flashcards': flashcards,
            'total_cards': len(flashcards),
            'instructions': 'Review each word. Rate your recall quality from 0-5.'
        }
    
    def _generate_multiple_choice_activity(self, user_vocabs: List[UserVocabulary]) -> Dict:
        """Generate multiple choice quiz"""
        questions = []
        
        # Get all words for distractors
        all_words = VocabularyItem.query.limit(100).all()
        
        for uv in user_vocabs:
            if not uv.vocabulary_item:
                continue
            
            vocab = uv.vocabulary_item
            
            # Create question
            question = {
                'user_vocabulary_id': uv.id,
                'word': vocab.word,
                'question': f'What does "{vocab.word}" mean?',
                'correct_answer': vocab.english_definition,
                'options': [vocab.english_definition]
            }
            
            # Add distractors
            import random
            distractors = random.sample(
                [w.english_definition for w in all_words if w.id != vocab.id and w.english_definition],
                min(3, len(all_words) - 1)
            )
            question['options'].extend(distractors)
            random.shuffle(question['options'])
            
            questions.append(question)
        
        return {
            'activity_type': 'multiple_choice',
            'questions': questions,
            'total_questions': len(questions),
            'instructions': 'Select the correct definition for each word.'
        }
    
    def _generate_fill_blank_activity(self, user_vocabs: List[UserVocabulary]) -> Dict:
        """Generate fill-in-the-blank activity"""
        questions = []
        
        for uv in user_vocabs:
            if not uv.vocabulary_item or not uv.vocabulary_item.example_sentences:
                continue
            
            vocab = uv.vocabulary_item
            
            # Use example sentence
            import random
            sentence = random.choice(vocab.example_sentences)
            
            # Replace word with blank
            blank_sentence = sentence.replace(vocab.word, '______')
            
            questions.append({
                'user_vocabulary_id': uv.id,
                'sentence': blank_sentence,
                'correct_answer': vocab.word,
                'hint': vocab.english_definition
            })
        
        return {
            'activity_type': 'fill_blank',
            'questions': questions,
            'total_questions': len(questions),
            'instructions': 'Fill in the blank with the correct word.'
        }
    
    def _generate_spelling_activity(self, user_vocabs: List[UserVocabulary]) -> Dict:
        """Generate spelling practice activity"""
        words = []
        
        for uv in user_vocabs:
            if not uv.vocabulary_item:
                continue
            
            words.append({
                'user_vocabulary_id': uv.id,
                'audio_url': uv.vocabulary_item.audio_url,
                'pronunciation': uv.vocabulary_item.pronunciation_guide,
                'correct_spelling': uv.vocabulary_item.word,
                'definition': uv.vocabulary_item.english_definition
            })
        
        return {
            'activity_type': 'spelling',
            'words': words,
            'total_words': len(words),
            'instructions': 'Listen to the pronunciation and spell the word correctly.'
        }
    
    def _generate_usage_activity(self, user_vocabs: List[UserVocabulary]) -> Dict:
        """Generate usage in context activity"""
        tasks = []
        
        for uv in user_vocabs:
            if not uv.vocabulary_item:
                continue
            
            vocab = uv.vocabulary_item
            
            tasks.append({
                'user_vocabulary_id': uv.id,
                'word': vocab.word,
                'task': f'Write a sentence using the word "{vocab.word}"',
                'example': vocab.example_sentences[0] if vocab.example_sentences else None,
                'tips': vocab.usage_notes
            })
        
        return {
            'activity_type': 'usage',
            'tasks': tasks,
            'total_tasks': len(tasks),
            'instructions': 'Create your own sentences using these words correctly.'
        }
    
    def _calculate_learning_velocity(self, user_id: int) -> float:
        """Calculate how fast user is learning vocabulary"""
        # Get words learned in last 30 days
        recent_words = UserVocabulary.query.filter(
            UserVocabulary.user_id == user_id,
            UserVocabulary.added_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Words per week
        return round(recent_words / 4.29, 2)  # 30 days ≈ 4.29 weeks
    
    def _get_mastery_recommendation(self, user_vocab: UserVocabulary, mastery_score: float) -> str:
        """Get personalized recommendation for word mastery"""
        if mastery_score >= 80:
            return "Excellent mastery! Keep reviewing to maintain."
        elif mastery_score >= 60:
            return "Good progress! Focus on using this word in context."
        elif mastery_score >= 40:
            return "Making progress. Practice more regularly."
        else:
            return "Needs more practice. Review frequently and use in sentences."
    
    def _generate_vocabulary_recommendations(
        self,
        user_id: int,
        user_vocabs: List[UserVocabulary]
    ) -> List[str]:
        """Generate personalized vocabulary learning recommendations"""
        recommendations = []
        
        # Check review frequency
        due_count = len([uv for uv in user_vocabs if uv.needs_review])
        if due_count > 20:
            recommendations.append(f"You have {due_count} words due for review. Practice daily for better retention.")
        
        # Check mastery distribution
        mastery_counts = {}
        for uv in user_vocabs:
            mastery_counts[uv.mastery_level] = mastery_counts.get(uv.mastery_level, 0) + 1
        
        if mastery_counts.get('new', 0) > mastery_counts.get('mastered', 0):
            recommendations.append("Focus on consolidating existing words before adding more new ones.")
        
        # Check forgotten words
        forgotten = [uv for uv in user_vocabs if uv.times_forgotten > 3]
        if forgotten:
            recommendations.append(f"{len(forgotten)} words need extra attention. Create mnemonics for difficult words.")
        
        # Check consistency
        avg_streak = sum(uv.current_streak_days for uv in user_vocabs) / len(user_vocabs) if user_vocabs else 0
        if avg_streak < 3:
            recommendations.append("Daily practice improves retention. Try to review vocabulary every day.")
        
        return recommendations if recommendations else ["Keep up the great work!"]
    
    def _generate_session_insights(self, session: VocabularyPracticeSession) -> List[str]:
        """Generate insights from practice session"""
        insights = []
        
        if session.session_score:
            if session.session_score >= 90:
                insights.append("Excellent performance! Your vocabulary is strong.")
            elif session.session_score >= 70:
                insights.append("Good work! Keep practicing to improve retention.")
            else:
                insights.append("Keep practicing! Regular review will improve your scores.")
        
        if session.average_quality_rating:
            if session.average_quality_rating >= 4.5:
                insights.append("Great recall quality! Your review intervals will increase.")
            elif session.average_quality_rating < 3:
                insights.append("Consider reviewing these words more frequently.")
        
        return insights
