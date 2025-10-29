"""
Content Quality Validation Service
Ensures generated content meets quality standards.
"""

from typing import Dict, List, Tuple
import re


class ContentQualityValidator:
    """Validates generated content for quality and appropriateness."""
    
    def __init__(self):
        self.minimum_content_length = 50  # characters
        self.minimum_questions = 3
        self.minimum_flashcards = 5
        
    def validate_activity(self, activity_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate generated activity content.
        
        Args:
            activity_data: Generated activity dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        activity_type = activity_data.get('activity_type')
        
        # Check for basic required fields
        if not activity_data.get('title'):
            errors.append("Activity must have a title")
        
        if not activity_data.get('description'):
            errors.append("Activity must have a description")
        
        if not activity_data.get('learning_objectives'):
            errors.append("Activity must have learning objectives")
        
        # Type-specific validation
        if activity_type == 'quiz':
            errors.extend(self._validate_quiz(activity_data))
        elif activity_type == 'flashcard':
            errors.extend(self._validate_flashcards(activity_data))
        elif activity_type == 'reading':
            errors.extend(self._validate_reading(activity_data))
        elif activity_type == 'writing':
            errors.extend(self._validate_writing(activity_data))
        elif activity_type == 'listening':
            errors.extend(self._validate_listening(activity_data))
        elif activity_type == 'speaking':
            errors.extend(self._validate_speaking(activity_data))
        
        return (len(errors) == 0, errors)
    
    def _validate_quiz(self, data: Dict) -> List[str]:
        """Validate quiz content."""
        errors = []
        questions = data.get('questions', [])
        
        if len(questions) < self.minimum_questions:
            errors.append(f"Quiz must have at least {self.minimum_questions} questions")
        
        for i, q in enumerate(questions):
            if not q.get('question'):
                errors.append(f"Question {i+1} is missing question text")
            
            if q.get('type') == 'multiple_choice':
                options = q.get('options', [])
                if len(options) < 2:
                    errors.append(f"Question {i+1} must have at least 2 options")
                
                if 'correct_answer' not in q:
                    errors.append(f"Question {i+1} is missing correct answer")
            
            if not q.get('explanation'):
                errors.append(f"Question {i+1} should have an explanation")
        
        return errors
    
    def _validate_flashcards(self, data: Dict) -> List[str]:
        """Validate flashcard content."""
        errors = []
        cards = data.get('cards', [])
        
        if len(cards) < self.minimum_flashcards:
            errors.append(f"Must have at least {self.minimum_flashcards} flashcards")
        
        for i, card in enumerate(cards):
            if not card.get('front'):
                errors.append(f"Card {i+1} is missing front content")
            if not card.get('back'):
                errors.append(f"Card {i+1} is missing back content")
            if not card.get('example'):
                errors.append(f"Card {i+1} should have an example")
        
        return errors
    
    def _validate_reading(self, data: Dict) -> List[str]:
        """Validate reading passage."""
        errors = []
        passage = data.get('passage', '')
        questions = data.get('questions', [])
        
        if len(passage) < self.minimum_content_length:
            errors.append(f"Reading passage too short (minimum {self.minimum_content_length} characters)")
        
        if len(questions) < 3:
            errors.append("Reading should have at least 3 comprehension questions")
        
        # Check for reasonable word count
        word_count = len(passage.split())
        if word_count < 50:
            errors.append("Reading passage should have at least 50 words")
        
        return errors
    
    def _validate_writing(self, data: Dict) -> List[str]:
        """Validate writing prompt."""
        errors = []
        prompt = data.get('prompt', '')
        
        if len(prompt) < 20:
            errors.append("Writing prompt too short")
        
        if not data.get('guidelines'):
            errors.append("Writing activity should have guidelines")
        
        if not data.get('rubric'):
            errors.append("Writing activity should have a rubric")
        
        return errors
    
    def _validate_listening(self, data: Dict) -> List[str]:
        """Validate listening exercise."""
        errors = []
        script = data.get('audio_script', '')
        questions = data.get('questions', [])
        
        if len(script) < self.minimum_content_length:
            errors.append("Audio script too short")
        
        if len(questions) < 3:
            errors.append("Listening should have at least 3 questions")
        
        return errors
    
    def _validate_speaking(self, data: Dict) -> List[str]:
        """Validate speaking scenario."""
        errors = []
        scenario = data.get('scenario', '')
        
        if len(scenario) < 20:
            errors.append("Speaking scenario description too short")
        
        if not data.get('conversation_flow'):
            errors.append("Speaking activity should have conversation flow")
        
        if not data.get('sample_responses'):
            errors.append("Speaking activity should have sample responses")
        
        return errors
    
    def check_content_appropriateness(self, text: str) -> Tuple[bool, List[str]]:
        """
        Check if content is appropriate (no offensive language, etc.).
        
        Args:
            text: Text to check
            
        Returns:
            Tuple of (is_appropriate, list_of_issues)
        """
        issues = []
        
        # Basic checks - in production, use more sophisticated content filtering
        text_lower = text.lower()
        
        # Check for placeholder text that shouldn't be in final content
        placeholders = ['lorem ipsum', 'sample text', 'placeholder', 'todo', 'fixme']
        for placeholder in placeholders:
            if placeholder in text_lower:
                issues.append(f"Content contains placeholder text: {placeholder}")
        
        # Check for minimum quality markers
        if len(text.strip()) == 0:
            issues.append("Content is empty")
        
        # Check for proper sentence structure (should have periods)
        if len(text) > 50 and '.' not in text:
            issues.append("Content may lack proper punctuation")
        
        return (len(issues) == 0, issues)
    
    def calculate_quality_score(self, activity_data: Dict) -> float:
        """
        Calculate overall quality score (0-1 scale).
        
        Args:
            activity_data: Generated activity
            
        Returns:
            Quality score between 0 and 1
        """
        score = 1.0
        is_valid, errors = self.validate_activity(activity_data)
        
        # Deduct points for each error
        score -= len(errors) * 0.1
        
        # Bonus for comprehensive content
        if activity_data.get('learning_objectives') and len(activity_data['learning_objectives']) >= 3:
            score += 0.1
        
        if activity_data.get('success_criteria'):
            score += 0.05
        
        # Check content appropriateness
        title = activity_data.get('title', '')
        description = activity_data.get('description', '')
        combined_text = f"{title} {description}"
        
        is_appropriate, issues = self.check_content_appropriateness(combined_text)
        if not is_appropriate:
            score -= len(issues) * 0.05
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))


# Global validator instance
validator = ContentQualityValidator()


def validate_generated_activity(activity_data: Dict) -> Dict:
    """
    Validate generated activity and return with validation metadata.
    
    Args:
        activity_data: Generated activity
        
    Returns:
        Activity data with validation metadata added
    """
    is_valid, errors = validator.validate_activity(activity_data)
    quality_score = validator.calculate_quality_score(activity_data)
    
    activity_data['validation'] = {
        'is_valid': is_valid,
        'errors': errors,
        'quality_score': quality_score,
        'validated_at': None  # Will be set by caller if needed
    }
    
    return activity_data
