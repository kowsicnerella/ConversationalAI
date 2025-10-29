"""
Vocabulary Integration Service
Automatically extracts and tracks vocabulary from all activity types
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.models import db
from app.models.activity import Activity, UserActivityLog
from app.models.vocabulary_mastery import (
    VocabularyItem,
    UserVocabulary,
    VocabularyReview
)
from app.services.vocabulary_mastery_service import VocabularyMasteryEngine
import re


class VocabularyIntegrationService:
    """
    Integrates vocabulary tracking with all activity types
    Automatically extracts and tracks vocabulary from activity content and user responses
    """
    
    def __init__(self):
        self.vocab_engine = VocabularyMasteryEngine()
    
    # ==================== Activity Content Processing ====================
    
    def extract_vocabulary_from_activity(
        self,
        activity: Activity,
        user_id: int,
        auto_add: bool = True
    ) -> List[VocabularyItem]:
        """
        Extract vocabulary from activity content based on activity type
        
        Args:
            activity: Activity object
            user_id: User ID
            auto_add: Automatically add to user's vocabulary
            
        Returns:
            List of VocabularyItem objects
        """
        extracted_words = []
        
        try:
            content = activity.content or {}
            activity_type = activity.activity_type
            difficulty_level = self._map_difficulty_to_cefr(activity.difficulty_level)
            
            # Extract text based on activity type
            text_content = self._extract_text_from_activity_content(content, activity_type)
            
            if not text_content:
                return extracted_words
            
            # Use AI to extract important vocabulary
            user_vocabs = self.vocab_engine.introduce_words_from_context(
                user_id=user_id,
                text=text_content,
                context=f"{activity_type}_activity",
                activity_id=activity.id,
                difficulty_level=difficulty_level
            )
            
            # Collect vocabulary items
            for uv in user_vocabs:
                if uv.vocabulary_item:
                    extracted_words.append(uv.vocabulary_item)
            
        except Exception as e:
            print(f"Error extracting vocabulary from activity {activity.id}: {e}")
        
        return extracted_words
    
    def _extract_text_from_activity_content(
        self,
        content: Dict,
        activity_type: str
    ) -> str:
        """Extract text content based on activity type"""
        text_parts = []
        
        try:
            if activity_type == 'quiz':
                # Extract from questions and answers
                questions = content.get('questions', [])
                for q in questions:
                    if q.get('question'):
                        text_parts.append(q['question'])
                    if q.get('options'):
                        text_parts.extend(q['options'])
                    if q.get('explanation'):
                        text_parts.append(q['explanation'])
            
            elif activity_type == 'flashcard':
                # Extract from flashcards
                cards = content.get('cards', content.get('flashcards', []))
                for card in cards:
                    if card.get('front'):
                        text_parts.append(card['front'])
                    if card.get('back'):
                        text_parts.append(card['back'])
                    if card.get('example'):
                        text_parts.append(card['example'])
            
            elif activity_type == 'reading':
                # Extract from reading passage
                if content.get('passage'):
                    text_parts.append(content['passage'])
                if content.get('text'):
                    text_parts.append(content['text'])
                
                # Also get questions
                questions = content.get('questions', [])
                for q in questions:
                    if q.get('question'):
                        text_parts.append(q['question'])
            
            elif activity_type == 'writing':
                # Extract from prompt and examples
                if content.get('prompt'):
                    text_parts.append(content['prompt'])
                if content.get('example'):
                    text_parts.append(content['example'])
                if content.get('guidelines'):
                    if isinstance(content['guidelines'], list):
                        text_parts.extend(content['guidelines'])
                    else:
                        text_parts.append(str(content['guidelines']))
            
            elif activity_type == 'role_play':
                # Extract from scenario and dialogue
                if content.get('scenario'):
                    text_parts.append(content['scenario'])
                if content.get('context'):
                    text_parts.append(content['context'])
                
                dialogue = content.get('dialogue', content.get('conversation', []))
                for turn in dialogue:
                    if isinstance(turn, dict):
                        if turn.get('text'):
                            text_parts.append(turn['text'])
                        if turn.get('message'):
                            text_parts.append(turn['message'])
                    elif isinstance(turn, str):
                        text_parts.append(turn)
            
            elif activity_type == 'listening':
                # Extract from transcript
                if content.get('transcript'):
                    text_parts.append(content['transcript'])
                if content.get('text'):
                    text_parts.append(content['text'])
                
                questions = content.get('questions', [])
                for q in questions:
                    if q.get('question'):
                        text_parts.append(q['question'])
            
            elif activity_type == 'speaking':
                # Extract from prompts and examples
                if content.get('prompt'):
                    text_parts.append(content['prompt'])
                if content.get('example_response'):
                    text_parts.append(content['example_response'])
                if content.get('key_phrases'):
                    text_parts.extend(content['key_phrases'])
            
            else:
                # Generic extraction
                if content.get('text'):
                    text_parts.append(content['text'])
                if content.get('content'):
                    text_parts.append(str(content['content']))
        
        except Exception as e:
            print(f"Error extracting text from {activity_type} content: {e}")
        
        # Join all text parts
        return ' '.join(text_parts)
    
    # ==================== User Response Processing ====================
    
    def track_vocabulary_usage_in_response(
        self,
        user_id: int,
        activity_log: UserActivityLog,
        user_response: Dict
    ) -> List[Dict]:
        """
        Track vocabulary usage in user's responses
        Mark words as correctly used or struggled with
        
        Args:
            user_id: User ID
            activity_log: UserActivityLog object
            user_response: User's response data
            
        Returns:
            List of vocabulary usage records
        """
        usage_records = []
        
        try:
            activity_type = activity_log.activity.activity_type
            
            # Extract user's written/spoken text
            user_text = self._extract_user_text_from_response(user_response, activity_type)
            
            if not user_text:
                return usage_records
            
            # Find vocabulary words in user's text
            user_vocab_items = UserVocabulary.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            for uv in user_vocab_items:
                if not uv.vocabulary_item:
                    continue
                
                word = uv.vocabulary_item.word.lower()
                
                # Check if word appears in user's text
                if re.search(r'\b' + re.escape(word) + r'\b', user_text.lower()):
                    # Determine if used correctly (based on score/feedback)
                    correct = self._was_word_used_correctly(
                        user_response,
                        activity_log,
                        word
                    )
                    
                    # Mark as used
                    uv.mark_as_used(
                        correct=correct,
                        response_time_seconds=None
                    )
                    
                    # Track context
                    context = f"{activity_type}_production"
                    uv.mark_as_seen(context)
                    
                    usage_records.append({
                        'vocabulary_item_id': uv.vocabulary_item_id,
                        'word': word,
                        'correct': correct,
                        'context': context
                    })
            
            if usage_records:
                db.session.commit()
        
        except Exception as e:
            print(f"Error tracking vocabulary usage: {e}")
            db.session.rollback()
        
        return usage_records
    
    def _extract_user_text_from_response(
        self,
        user_response: Dict,
        activity_type: str
    ) -> str:
        """Extract user's text from response based on activity type"""
        text_parts = []
        
        try:
            if activity_type in ['writing', 'speaking']:
                # Direct text response
                if user_response.get('text'):
                    text_parts.append(user_response['text'])
                if user_response.get('content'):
                    text_parts.append(str(user_response['content']))
                if user_response.get('response'):
                    text_parts.append(str(user_response['response']))
            
            elif activity_type == 'role_play':
                # User's dialogue turns
                turns = user_response.get('user_turns', user_response.get('responses', []))
                for turn in turns:
                    if isinstance(turn, dict):
                        text_parts.append(turn.get('text', ''))
                    elif isinstance(turn, str):
                        text_parts.append(turn)
            
            elif activity_type == 'quiz':
                # Look at text answers (not just selections)
                answers = user_response.get('answers', [])
                for answer in answers:
                    if isinstance(answer, dict) and answer.get('text'):
                        text_parts.append(answer['text'])
            
        except Exception as e:
            print(f"Error extracting user text: {e}")
        
        return ' '.join(text_parts)
    
    def _was_word_used_correctly(
        self,
        user_response: Dict,
        activity_log: UserActivityLog,
        word: str
    ) -> bool:
        """Determine if word was used correctly based on feedback/score"""
        # Use accuracy score if available
        if activity_log.accuracy_score is not None:
            return activity_log.accuracy_score >= 0.7
        
        # Use score ratio
        if activity_log.score and activity_log.max_score:
            return (activity_log.score / activity_log.max_score) >= 0.7
        
        # Check feedback for errors
        if activity_log.feedback_provided:
            feedback = activity_log.feedback_provided
            if isinstance(feedback, dict):
                errors = feedback.get('errors', [])
                # Check if this word was flagged as error
                for error in errors:
                    if isinstance(error, dict) and word.lower() in str(error).lower():
                        return False
        
        # Default to true if no negative indicators
        return True
    
    # ==================== Activity Completion Hooks ====================
    
    def on_activity_completed(
        self,
        user_id: int,
        activity_log: UserActivityLog
    ) -> Dict:
        """
        Called when user completes an activity
        Processes vocabulary exposure and usage
        
        Args:
            user_id: User ID
            activity_log: Completed activity log
            
        Returns:
            Dictionary with vocabulary processing results
        """
        results = {
            'new_words_encountered': [],
            'words_used': [],
            'words_reinforced': []
        }
        
        try:
            activity = activity_log.activity
            
            # 1. Mark vocabulary as seen (exposure)
            exposed_words = self._mark_vocabulary_as_seen(
                user_id,
                activity,
                activity_log
            )
            results['words_reinforced'] = exposed_words
            
            # 2. Track vocabulary usage in responses
            if activity_log.user_response:
                used_words = self.track_vocabulary_usage_in_response(
                    user_id,
                    activity_log,
                    activity_log.user_response
                )
                results['words_used'] = used_words
            
            # 3. Extract new vocabulary if needed
            if activity.skill_area == 'vocabulary' or activity.activity_type == 'reading':
                new_words = self.extract_vocabulary_from_activity(
                    activity,
                    user_id,
                    auto_add=True
                )
                results['new_words_encountered'] = [w.word for w in new_words]
        
        except Exception as e:
            print(f"Error in on_activity_completed: {e}")
        
        return results
    
    def _mark_vocabulary_as_seen(
        self,
        user_id: int,
        activity: Activity,
        activity_log: UserActivityLog
    ) -> List[str]:
        """Mark all user's vocabulary that appears in activity as seen"""
        seen_words = []
        
        try:
            # Get activity text
            text_content = self._extract_text_from_activity_content(
                activity.content or {},
                activity.activity_type
            )
            
            if not text_content:
                return seen_words
            
            # Get user's vocabulary
            user_vocab_items = UserVocabulary.query.filter_by(
                user_id=user_id,
                is_active=True
            ).all()
            
            # Check each word
            for uv in user_vocab_items:
                if not uv.vocabulary_item:
                    continue
                
                word = uv.vocabulary_item.word.lower()
                
                # Check if word appears in activity
                if re.search(r'\b' + re.escape(word) + r'\b', text_content.lower()):
                    context = f"{activity.activity_type}_exposure"
                    uv.mark_as_seen(context)
                    seen_words.append(word)
            
            if seen_words:
                db.session.commit()
        
        except Exception as e:
            print(f"Error marking vocabulary as seen: {e}")
            db.session.rollback()
        
        return seen_words
    
    # ==================== Activity Generation Enhancement ====================
    
    def get_target_vocabulary_for_activity(
        self,
        user_id: int,
        activity_type: str,
        difficulty_level: str,
        count: int = 5
    ) -> List[VocabularyItem]:
        """
        Get vocabulary to target in a new activity
        Prioritizes words that need review
        
        Args:
            user_id: User ID
            activity_type: Type of activity being generated
            difficulty_level: Activity difficulty
            count: Number of words to target
            
        Returns:
            List of VocabularyItem objects to target
        """
        target_words = []
        
        try:
            cefr_level = self._map_difficulty_to_cefr(difficulty_level)
            
            # Get words due for review at this level
            words_due = self.vocab_engine.get_words_due_for_review(
                user_id=user_id,
                limit=count,
                mastery_levels=['learning', 'familiar']
            )
            
            # Filter by difficulty level
            for uv in words_due:
                if uv.vocabulary_item and uv.vocabulary_item.difficulty_level == cefr_level:
                    target_words.append(uv.vocabulary_item)
            
            # If not enough, add high-priority words at this level
            if len(target_words) < count:
                additional = VocabularyItem.query.filter_by(
                    difficulty_level=cefr_level,
                    is_high_priority=True
                ).limit(count - len(target_words)).all()
                
                target_words.extend(additional)
        
        except Exception as e:
            print(f"Error getting target vocabulary: {e}")
        
        return target_words[:count]
    
    def enhance_activity_with_vocabulary(
        self,
        activity_content: Dict,
        target_words: List[VocabularyItem],
        activity_type: str
    ) -> Dict:
        """
        Enhance activity content to include target vocabulary
        
        Args:
            activity_content: Original activity content
            target_words: Vocabulary to include
            activity_type: Type of activity
            
        Returns:
            Enhanced activity content
        """
        # Add vocabulary hints to content
        if target_words:
            activity_content['target_vocabulary'] = [
                {
                    'word': word.word,
                    'definition': word.english_definition,
                    'telugu': word.telugu_translation
                }
                for word in target_words
            ]
            
            # Activity-specific enhancements
            if activity_type == 'reading':
                # Add vocabulary preview section
                activity_content['vocabulary_preview'] = [
                    {
                        'word': word.word,
                        'pronunciation': word.pronunciation_guide,
                        'definition': word.english_definition
                    }
                    for word in target_words
                ]
            
            elif activity_type == 'writing':
                # Suggest vocabulary to use
                activity_content['suggested_vocabulary'] = [
                    word.word for word in target_words
                ]
            
            elif activity_type == 'speaking':
                # Add key phrases
                if 'key_phrases' not in activity_content:
                    activity_content['key_phrases'] = []
                
                for word in target_words:
                    if word.example_sentences:
                        activity_content['key_phrases'].extend(
                            word.example_sentences[:1]
                        )
        
        return activity_content
    
    # ==================== Helper Methods ====================
    
    def _map_difficulty_to_cefr(self, difficulty: str) -> str:
        """Map activity difficulty to CEFR level"""
        mapping = {
            'beginner': 'A1',
            'elementary': 'A2',
            'intermediate': 'B1',
            'upper_intermediate': 'B2',
            'advanced': 'C1',
            'expert': 'C2'
        }
        
        # Handle numeric levels
        if difficulty and difficulty.lower() in mapping:
            return mapping[difficulty.lower()]
        
        # Default to B1
        return 'B1'
    
    # ==================== Analytics ====================
    
    def get_vocabulary_reinforcement_stats(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """
        Get statistics on vocabulary reinforcement through activities
        
        Args:
            user_id: User ID
            days: Time window in days
            
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        
        stats = {
            'total_exposures': 0,
            'production_uses': 0,
            'activities_with_vocab': 0,
            'top_reinforced_words': []
        }
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get user's vocabulary
            user_vocabs = UserVocabulary.query.filter(
                UserVocabulary.user_id == user_id,
                UserVocabulary.last_updated >= cutoff_date
            ).all()
            
            # Count exposures and uses
            for uv in user_vocabs:
                # Count contexts with "exposure" or "production"
                if uv.contexts_encountered:
                    exposure_count = len([
                        c for c in uv.contexts_encountered 
                        if 'exposure' in c or 'activity' in c
                    ])
                    production_count = len([
                        c for c in uv.contexts_encountered 
                        if 'production' in c
                    ])
                    
                    stats['total_exposures'] += exposure_count
                    stats['production_uses'] += production_count
            
            # Get activity logs in time window
            activity_count = UserActivityLog.query.filter(
                UserActivityLog.user_id == user_id,
                UserActivityLog.completed_at >= cutoff_date
            ).count()
            
            stats['activities_with_vocab'] = activity_count
            
            # Top reinforced words
            top_words = sorted(
                user_vocabs,
                key=lambda uv: uv.times_seen,
                reverse=True
            )[:10]
            
            stats['top_reinforced_words'] = [
                {
                    'word': uv.vocabulary_item.word if uv.vocabulary_item else 'Unknown',
                    'exposures': uv.times_seen,
                    'mastery_level': uv.mastery_level
                }
                for uv in top_words if uv.vocabulary_item
            ]
        
        except Exception as e:
            print(f"Error getting reinforcement stats: {e}")
        
        return stats


# Global instance
vocabulary_integration = VocabularyIntegrationService()
