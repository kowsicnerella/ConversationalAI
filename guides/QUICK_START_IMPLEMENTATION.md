# 🚀 QUICK START IMPLEMENTATION GUIDE

## 📋 Overview

This guide helps you start implementing the AI-personalized learning system **TODAY**. Follow these steps in order for maximum impact with minimal disruption to the existing system.

---

## 🎯 Week 1 Goals (Priority Tasks)

### Day 1-2: Setup Foundation
**Goal**: Create the curriculum framework and enhanced models

#### Task 1: Create Curriculum Models (4 hours)

**Step 1**: Create the new models file

```bash
cd language-learning-platform/app/models
```

Create `curriculum.py`:

```python
from .user import db
from datetime import datetime


class CurriculumLevel(db.Model):
    """CEFR-based curriculum levels (A1 to C2)"""
    __tablename__ = "curriculum_levels"
    
    id = db.Column(db.Integer, primary_key=True)
    cefr_level = db.Column(db.String(2), unique=True, nullable=False)  # A1, A2, B1, B2, C1, C2
    level_name = db.Column(db.String(50), nullable=False)  # Beginner, Elementary, etc.
    description = db.Column(db.Text)
    
    # Requirements
    vocabulary_range_min = db.Column(db.Integer)  # Min words needed
    vocabulary_range_max = db.Column(db.Integer)  # Target words
    grammar_concepts = db.Column(db.JSON)  # List of grammar concepts
    functional_skills = db.Column(db.JSON)  # Can-do statements
    
    # Progression
    estimated_hours = db.Column(db.Integer)  # Hours to complete level
    prerequisite_level_id = db.Column(db.Integer, db.ForeignKey('curriculum_levels.id'))
    
    # Relationships
    learning_nodes = db.relationship('LearningNode', backref='curriculum_level', lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CurriculumLevel {self.cefr_level} - {self.level_name}>"


class LearningNode(db.Model):
    """Atomic learning unit - the smallest teachable concept"""
    __tablename__ = "learning_nodes"
    
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.String(100), unique=True, nullable=False)  # e.g., "A1_VOCAB_GREETINGS"
    
    # Classification
    curriculum_level_id = db.Column(db.Integer, db.ForeignKey('curriculum_levels.id'), nullable=False)
    skill_domain = db.Column(db.String(50), nullable=False)  # vocabulary, grammar, listening, etc.
    concept_name = db.Column(db.String(200), nullable=False)  # e.g., "Basic Greetings"
    
    # Learning Design
    learning_objectives = db.Column(db.JSON)  # What user should be able to do
    activity_templates = db.Column(db.JSON)  # Types of activities for this concept
    example_content = db.Column(db.JSON)  # Example content for AI generation
    
    # Difficulty & Timing
    difficulty_range_min = db.Column(db.Float, default=0.0)  # 0-1 scale
    difficulty_range_max = db.Column(db.Float, default=1.0)
    estimated_time_minutes = db.Column(db.Integer, default=15)
    
    # Mastery
    mastery_threshold = db.Column(db.Float, default=0.8)  # Threshold to consider mastered
    
    # Dependencies
    prerequisites = db.Column(db.JSON)  # List of node_ids that must be completed first
    
    # Metadata
    is_core = db.Column(db.Boolean, default=True)  # Core vs optional
    tags = db.Column(db.JSON)  # Tags for search/filtering
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<LearningNode {self.node_id} - {self.concept_name}>"


class UserLearningPathProgress(db.Model):
    """Track user's progress through the curriculum"""
    __tablename__ = "user_learning_path_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Current Position
    current_level = db.Column(db.String(2), nullable=False)  # A1, A2, etc.
    current_node_id = db.Column(db.String(100))  # Current learning node
    
    # Goals
    target_level = db.Column(db.String(2))  # Goal level
    target_date = db.Column(db.Date)
    
    # Learning Preferences
    learning_style = db.Column(db.String(50))  # visual, auditory, kinesthetic
    preferred_pace = db.Column(db.String(20), default='medium')  # slow, medium, fast
    preferred_session_length = db.Column(db.Integer, default=20)  # minutes
    
    # Skill Focus
    skill_priorities = db.Column(db.JSON)  # Which skills to emphasize
    weak_areas = db.Column(db.JSON)  # Areas needing work
    strong_areas = db.Column(db.JSON)  # Areas of strength
    current_focus_skill = db.Column(db.String(50))  # Current skill focus
    
    # Progress Metrics
    nodes_completed = db.Column(db.Integer, default=0)
    nodes_in_progress = db.Column(db.Integer, default=0)
    nodes_mastered = db.Column(db.Integer, default=0)
    
    # Learning Analytics
    learning_velocity = db.Column(db.Float)  # Nodes per week
    average_accuracy = db.Column(db.Float)  # Overall accuracy
    time_invested_hours = db.Column(db.Float, default=0.0)
    
    # Engagement
    last_activity_date = db.Column(db.DateTime)
    longest_streak_days = db.Column(db.Integer, default=0)
    current_streak_days = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', name='unique_user_path'),
    )
    
    def __repr__(self):
        return f"<UserLearningPathProgress User {self.user_id} - {self.current_level}>"


class NodeCompletion(db.Model):
    """Track completion of individual learning nodes"""
    __tablename__ = "node_completions"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    node_id = db.Column(db.String(100), nullable=False)
    
    # Performance
    attempts = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Float)  # 0-1 scale
    average_score = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, mastered
    mastery_level = db.Column(db.Float, default=0.0)  # 0-1 scale
    
    # Timing
    first_attempt_date = db.Column(db.DateTime)
    last_attempt_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    mastery_date = db.Column(db.DateTime)
    
    # Learning Data
    time_spent_minutes = db.Column(db.Integer, default=0)
    activities_completed = db.Column(db.Integer, default=0)
    mistakes_made = db.Column(db.JSON)  # Common mistakes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'node_id', name='unique_user_node'),
    )
    
    def __repr__(self):
        return f"<NodeCompletion User {self.user_id} - Node {self.node_id}>"
```

**Step 2**: Create database migration

```bash
cd language-learning-platform
python -m flask db migrate -m "Add curriculum and learning path models"
python -m flask db upgrade
```

**Step 3**: Create seed data script

Create `language-learning-platform/seed_curriculum.py`:

```python
from app import create_app, db
from app.models.curriculum import CurriculumLevel, LearningNode

app = create_app()

def seed_curriculum():
    with app.app_context():
        # Create CEFR Levels
        levels = [
            {
                'cefr_level': 'A1',
                'level_name': 'Beginner',
                'description': 'Can understand and use familiar everyday expressions',
                'vocabulary_range_min': 0,
                'vocabulary_range_max': 1000,
                'estimated_hours': 80,
                'grammar_concepts': [
                    'Present simple tense',
                    'Basic pronouns',
                    'Articles (a/an/the)',
                    'Plural nouns',
                    'Basic prepositions',
                    'Question words'
                ],
                'functional_skills': [
                    'Introduce yourself',
                    'Ask and answer simple questions',
                    'Understand basic instructions',
                    'Tell time and dates',
                    'Order food',
                    'Ask for directions'
                ]
            },
            {
                'cefr_level': 'A2',
                'level_name': 'Elementary',
                'description': 'Can communicate in simple routine tasks',
                'vocabulary_range_min': 1000,
                'vocabulary_range_max': 2000,
                'estimated_hours': 120,
                'grammar_concepts': [
                    'Past simple tense',
                    'Future tense (going to)',
                    'Modal verbs (can, could, should)',
                    'Comparative and superlative',
                    'Present continuous',
                    'There is/are'
                ],
                'functional_skills': [
                    'Describe past experiences',
                    'Make plans for the future',
                    'Give opinions',
                    'Write simple messages',
                    'Understand conversations about familiar topics',
                    'Handle most travel situations'
                ]
            },
            {
                'cefr_level': 'B1',
                'level_name': 'Intermediate',
                'description': 'Can deal with most situations when traveling',
                'vocabulary_range_min': 2000,
                'vocabulary_range_max': 3500,
                'estimated_hours': 180,
                'grammar_concepts': [
                    'Present perfect',
                    'Past continuous',
                    'First and second conditionals',
                    'Passive voice (simple)',
                    'Reported speech',
                    'Relative clauses'
                ],
                'functional_skills': [
                    'Understand main points of clear standard speech',
                    'Produce simple connected text',
                    'Describe experiences and events',
                    'Explain opinions and plans',
                    'Write personal letters',
                    'Handle work situations'
                ]
            }
        ]
        
        for level_data in levels:
            level = CurriculumLevel(**level_data)
            db.session.add(level)
        
        db.session.commit()
        print("✅ Curriculum levels seeded")
        
        # Create Learning Nodes for A1
        a1_level = CurriculumLevel.query.filter_by(cefr_level='A1').first()
        
        nodes = [
            {
                'node_id': 'A1_VOCAB_GREETINGS',
                'curriculum_level_id': a1_level.id,
                'skill_domain': 'vocabulary',
                'concept_name': 'Basic Greetings and Introductions',
                'learning_objectives': [
                    'Use common greeting phrases',
                    'Introduce yourself with name and basic info',
                    'Ask someone\'s name politely',
                    'Say goodbye in different contexts'
                ],
                'activity_templates': ['flashcard', 'dialogue_completion', 'role_play'],
                'difficulty_range_min': 0.0,
                'difficulty_range_max': 0.3,
                'estimated_time_minutes': 15,
                'prerequisites': [],
                'is_core': True,
                'tags': ['vocabulary', 'conversation', 'basics']
            },
            {
                'node_id': 'A1_VOCAB_NUMBERS',
                'curriculum_level_id': a1_level.id,
                'skill_domain': 'vocabulary',
                'concept_name': 'Numbers 1-100',
                'learning_objectives': [
                    'Count from 1 to 100',
                    'Use numbers in daily contexts',
                    'Tell time',
                    'Say prices'
                ],
                'activity_templates': ['flashcard', 'quiz', 'listening'],
                'difficulty_range_min': 0.0,
                'difficulty_range_max': 0.3,
                'estimated_time_minutes': 20,
                'prerequisites': ['A1_VOCAB_GREETINGS'],
                'is_core': True,
                'tags': ['vocabulary', 'numbers', 'practical']
            },
            {
                'node_id': 'A1_GRAMMAR_PRESENT_SIMPLE',
                'curriculum_level_id': a1_level.id,
                'skill_domain': 'grammar',
                'concept_name': 'Present Simple Tense',
                'learning_objectives': [
                    'Form present simple sentences',
                    'Use correct subject-verb agreement',
                    'Make negative sentences',
                    'Ask yes/no questions'
                ],
                'activity_templates': ['sentence_construction', 'error_correction', 'quiz'],
                'difficulty_range_min': 0.2,
                'difficulty_range_max': 0.5,
                'estimated_time_minutes': 25,
                'prerequisites': ['A1_VOCAB_GREETINGS'],
                'is_core': True,
                'tags': ['grammar', 'verb_tenses', 'fundamental']
            },
            {
                'node_id': 'A1_VOCAB_FAMILY',
                'curriculum_level_id': a1_level.id,
                'skill_domain': 'vocabulary',
                'concept_name': 'Family Members',
                'learning_objectives': [
                    'Name immediate family members',
                    'Describe family relationships',
                    'Talk about family in simple terms'
                ],
                'activity_templates': ['flashcard', 'reading', 'speaking'],
                'difficulty_range_min': 0.1,
                'difficulty_range_max': 0.3,
                'estimated_time_minutes': 15,
                'prerequisites': ['A1_VOCAB_GREETINGS'],
                'is_core': True,
                'tags': ['vocabulary', 'family', 'personal']
            },
            {
                'node_id': 'A1_VOCAB_DAILY_ROUTINE',
                'curriculum_level_id': a1_level.id,
                'skill_domain': 'vocabulary',
                'concept_name': 'Daily Routine Activities',
                'learning_objectives': [
                    'Name common daily activities',
                    'Describe your daily routine',
                    'Use time expressions'
                ],
                'activity_templates': ['flashcard', 'writing', 'speaking'],
                'difficulty_range_min': 0.2,
                'difficulty_range_max': 0.4,
                'estimated_time_minutes': 20,
                'prerequisites': ['A1_VOCAB_NUMBERS', 'A1_GRAMMAR_PRESENT_SIMPLE'],
                'is_core': True,
                'tags': ['vocabulary', 'daily_life', 'routine']
            }
        ]
        
        for node_data in nodes:
            node = LearningNode(**node_data)
            db.session.add(node)
        
        db.session.commit()
        print(f"✅ {len(nodes)} learning nodes seeded")

if __name__ == '__main__':
    seed_curriculum()
```

Run the seed script:

```bash
python seed_curriculum.py
```

---

### Day 3-4: Enhance Activity Generator
**Goal**: Make activity generation personalized

#### Task 2: Update Activity Generator Service (4 hours)

Edit `language-learning-platform/app/services/activity_generator_service.py`:

Add this new method to the `ActivityGeneratorService` class:

```python
def generate_personalized_activity(
    self,
    user_id: int,
    learning_node_id: int,
    activity_type: str = None,
    user_context: dict = None
) -> dict:
    """
    Generate activity personalized to user's current state
    
    Args:
        user_id: User ID
        learning_node_id: ID of the learning node
        activity_type: Specific type, or let AI choose
        user_context: Additional context (optional)
    
    Returns:
        Generated activity with metadata
    """
    from app.models.curriculum import LearningNode
    from app.models.personalization import VocabularyWord
    from app.models.user import User
    
    # Get learning node
    node = LearningNode.query.get(learning_node_id)
    if not node:
        return {"error": "Learning node not found"}
    
    # Get user profile
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}
    
    # Get user's learned vocabulary to avoid repetition
    learned_words = VocabularyWord.query.filter_by(user_id=user_id).all()
    learned_word_list = [w.english_word for w in learned_words]
    
    # Get user's weak areas if available
    weak_areas = user_context.get('weak_areas', []) if user_context else []
    
    # Determine activity type if not specified
    if not activity_type and node.activity_templates:
        import random
        activity_type = random.choice(node.activity_templates)
    
    # Build personalized prompt
    personalization_context = f"""
    User Profile:
    - Proficiency Level: {user.profile.proficiency_level if user.profile else 'beginner'}
    - Learning Node: {node.concept_name} ({node.skill_domain})
    - Already Learned Words: {', '.join(learned_word_list[:20]) if learned_word_list else 'None'}
    - Weak Areas: {', '.join(weak_areas) if weak_areas else 'None identified'}
    
    Learning Objectives for this activity:
    {chr(10).join('- ' + obj for obj in node.learning_objectives)}
    
    Instructions:
    - Generate content that helps achieve the learning objectives
    - Avoid using words the user has already learned unless reinforcing
    - Focus on weak areas if identified
    - Match the user's proficiency level
    - Include Telugu translations for new concepts
    - Make it engaging and culturally relevant
    """
    
    # Generate based on activity type
    if activity_type == 'flashcard':
        return self.generate_contextual_flashcards(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )
    elif activity_type == 'quiz':
        return self.generate_personalized_quiz(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )
    elif activity_type == 'reading':
        return self.generate_personalized_reading(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )
    elif activity_type == 'writing':
        return self.generate_personalized_writing_prompt(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )
    elif activity_type == 'role_play':
        return self.generate_personalized_role_play(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )
    else:
        # Default to quiz
        return self.generate_personalized_quiz(
            node.concept_name,
            user.profile.proficiency_level if user.profile else 'beginner',
            personalization_context
        )

def generate_contextual_flashcards(self, topic, level, context):
    """Generate flashcards with additional context"""
    prompt = f"""
    {context}
    
    Generate 10 flashcards for learning: {topic}
    Level: {level}
    
    Return JSON format:
    {{
        "flashcards": [
            {{
                "front": "English word/phrase",
                "back": "Telugu translation",
                "example_sentence": "Example usage",
                "pronunciation_hint": "Phonetic guide"
            }}
        ]
    }}
    """
    
    result = LLMConfig.generate_text(prompt, json_mode=True)
    if result['success']:
        return _extract_json_from_response(result['text'])
    else:
        return {"error": result.get('error', 'Failed to generate flashcards')}

def generate_personalized_quiz(self, topic, level, context):
    """Generate quiz with personalization"""
    prompt = f"""
    {context}
    
    Generate a 5-question quiz about: {topic}
    Level: {level}
    
    Return JSON format with questions, options, correct answers, and explanations.
    Include Telugu translations for clarity.
    """
    
    result = LLMConfig.generate_text(prompt, json_mode=True)
    if result['success']:
        return _extract_json_from_response(result['text'])
    else:
        return {"error": result.get('error', 'Failed to generate quiz')}

# Add similar methods for other activity types...
```

---

### Day 5: Create Learning Path Orchestrator
**Goal**: AI determines what user should learn next

#### Task 3: Build Learning Path Orchestrator (6 hours)

Create `language-learning-platform/app/services/learning_path_orchestrator.py`:

```python
from app.models import db
from app.models.curriculum import (
    LearningNode,
    NodeCompletion,
    UserLearningPathProgress
)
from app.models.personalization import VocabularyWord
from app.models.activity import UserActivityLog
from app.services.activity_generator_service import ActivityGeneratorService
from datetime import datetime, timedelta
from sqlalchemy import func
import random


class LearningPathOrchestrator:
    """
    AI-driven orchestrator that determines the next best learning activity
    """
    
    def __init__(self):
        self.activity_generator = ActivityGeneratorService()
    
    def determine_next_activity(self, user_id: int, session_context: dict = None) -> dict:
        """
        Determine the next best activity for the user
        
        Priority Order:
        1. Vocabulary review (spaced repetition) if overdue
        2. Weak area reinforcement if performance < 70%
        3. Continue learning path progression
        4. Mixed review for variety
        
        Returns:
            dict with next activity information
        """
        
        # Get user's learning path progress
        path_progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        if not path_progress:
            # Initialize learning path for new user
            path_progress = self._initialize_learning_path(user_id)
        
        # Priority 1: Check for overdue vocabulary reviews
        overdue_vocab = self._get_overdue_vocabulary_reviews(user_id)
        if overdue_vocab and len(overdue_vocab) >= 5:
            return self._generate_vocabulary_review_activity(user_id, overdue_vocab[:10])
        
        # Priority 2: Check for weak areas needing reinforcement
        weak_areas = self._identify_weak_areas(user_id)
        if weak_areas:
            return self._generate_reinforcement_activity(user_id, weak_areas[0])
        
        # Priority 3: Continue learning path progression
        next_node = self._get_next_learning_node(user_id, path_progress)
        if next_node:
            return self._generate_node_activity(user_id, next_node)
        
        # Priority 4: Generate review activity
        return self._generate_mixed_review_activity(user_id, path_progress)
    
    def _initialize_learning_path(self, user_id: int):
        """Initialize learning path for new user"""
        from app.models.user import User
        from app.models.curriculum import CurriculumLevel
        
        user = User.query.get(user_id)
        
        # Determine starting level from profile or default to A1
        starting_level = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Map proficiency to CEFR
        level_map = {
            'absolute_beginner': 'A1',
            'beginner': 'A1',
            'elementary': 'A2',
            'intermediate': 'B1',
            'upper_intermediate': 'B2',
            'advanced': 'C1',
            'master': 'C2'
        }
        
        cefr_level = level_map.get(starting_level, 'A1')
        
        # Create path progress
        path_progress = UserLearningPathProgress(
            user_id=user_id,
            current_level=cefr_level,
            target_level='B2',  # Default goal
            learning_style='mixed',
            preferred_pace='medium',
            preferred_session_length=20
        )
        
        db.session.add(path_progress)
        db.session.commit()
        
        return path_progress
    
    def _get_overdue_vocabulary_reviews(self, user_id: int):
        """Get vocabulary words that need review"""
        # For now, return words that haven't been practiced recently
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        
        overdue_words = VocabularyWord.query.filter(
            VocabularyWord.user_id == user_id,
            VocabularyWord.times_practiced < 5,  # Not mastered yet
            db.or_(
                VocabularyWord.last_practiced == None,
                VocabularyWord.last_practiced < cutoff_date
            )
        ).limit(10).all()
        
        return overdue_words
    
    def _identify_weak_areas(self, user_id: int):
        """Identify areas where user is struggling"""
        # Get recent activity performance
        recent_logs = UserActivityLog.query.filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.completed_at >= datetime.utcnow() - timedelta(days=7)
        ).all()
        
        if not recent_logs:
            return []
        
        # Calculate average score by skill area
        skill_performance = {}
        for log in recent_logs:
            if log.skill_area and log.accuracy_score:
                if log.skill_area not in skill_performance:
                    skill_performance[log.skill_area] = []
                skill_performance[log.skill_area].append(log.accuracy_score)
        
        # Find skills with average < 0.7
        weak_areas = []
        for skill, scores in skill_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 0.7:
                weak_areas.append({
                    'skill': skill,
                    'average_score': avg_score,
                    'attempts': len(scores)
                })
        
        # Sort by weakest first
        weak_areas.sort(key=lambda x: x['average_score'])
        
        return weak_areas
    
    def _get_next_learning_node(self, user_id: int, path_progress):
        """Get the next learning node to study"""
        # Get completed nodes
        completed_nodes = NodeCompletion.query.filter(
            NodeCompletion.user_id == user_id,
            NodeCompletion.status.in_(['completed', 'mastered'])
        ).all()
        
        completed_node_ids = [nc.node_id for nc in completed_nodes]
        
        # Get available nodes at current level
        from app.models.curriculum import CurriculumLevel
        current_level = CurriculumLevel.query.filter_by(
            cefr_level=path_progress.current_level
        ).first()
        
        if not current_level:
            return None
        
        # Get nodes that:
        # 1. Are at current level
        # 2. Haven't been completed
        # 3. Have prerequisites met
        available_nodes = LearningNode.query.filter(
            LearningNode.curriculum_level_id == current_level.id,
            ~LearningNode.node_id.in_(completed_node_ids)
        ).all()
        
        # Filter by prerequisites
        for node in available_nodes:
            if not node.prerequisites or len(node.prerequisites) == 0:
                return node  # No prerequisites, can start
            
            # Check if all prerequisites are met
            prereqs_met = all(
                prereq in completed_node_ids
                for prereq in node.prerequisites
            )
            
            if prereqs_met:
                return node
        
        return None
    
    def _generate_node_activity(self, user_id: int, node: LearningNode):
        """Generate activity for a specific learning node"""
        # Generate personalized activity
        activity_data = self.activity_generator.generate_personalized_activity(
            user_id=user_id,
            learning_node_id=node.id
        )
        
        return {
            'activity_type': 'learning_node',
            'node_id': node.node_id,
            'node_name': node.concept_name,
            'skill_domain': node.skill_domain,
            'activity_data': activity_data,
            'estimated_minutes': node.estimated_time_minutes
        }
    
    def _generate_vocabulary_review_activity(self, user_id: int, words: list):
        """Generate vocabulary review activity"""
        flashcards = []
        for word in words:
            flashcards.append({
                'front': word.english_word,
                'back': word.telugu_translation,
                'context': word.context_sentence
            })
        
        return {
            'activity_type': 'vocabulary_review',
            'activity_data': {
                'flashcards': flashcards
            },
            'word_count': len(flashcards),
            'estimated_minutes': 5
        }
    
    def _generate_reinforcement_activity(self, user_id: int, weak_area: dict):
        """Generate activity to reinforce weak area"""
        # Find a node in the weak skill area
        from app.models.curriculum import LearningNode
        
        # Get nodes in this skill area
        nodes = LearningNode.query.filter_by(
            skill_domain=weak_area['skill']
        ).all()
        
        if nodes:
            node = random.choice(nodes)
            activity_data = self.activity_generator.generate_personalized_activity(
                user_id=user_id,
                learning_node_id=node.id,
                user_context={'weak_areas': [weak_area['skill']]}
            )
            
            return {
                'activity_type': 'reinforcement',
                'weak_area': weak_area['skill'],
                'activity_data': activity_data,
                'estimated_minutes': 15
            }
        
        return self._generate_mixed_review_activity(user_id, None)
    
    def _generate_mixed_review_activity(self, user_id: int, path_progress):
        """Generate mixed review of previously learned concepts"""
        # Get recently completed nodes
        recent_completions = NodeCompletion.query.filter(
            NodeCompletion.user_id == user_id,
            NodeCompletion.status == 'completed'
        ).order_by(NodeCompletion.completion_date.desc()).limit(5).all()
        
        if not recent_completions:
            # Generate a general practice activity
            return {
                'activity_type': 'general_practice',
                'activity_data': self.activity_generator.generate_quiz(
                    'general English practice',
                    'beginner'
                ),
                'estimated_minutes': 10
            }
        
        # Pick a random recent node for review
        review_node_completion = random.choice(recent_completions)
        node = LearningNode.query.filter_by(
            node_id=review_node_completion.node_id
        ).first()
        
        if node:
            activity_data = self.activity_generator.generate_personalized_activity(
                user_id=user_id,
                learning_node_id=node.id
            )
            
            return {
                'activity_type': 'review',
                'node_name': node.concept_name,
                'activity_data': activity_data,
                'estimated_minutes': 10
            }
        
        return {
            'activity_type': 'general_practice',
            'activity_data': self.activity_generator.generate_quiz(
                'general English practice',
                'beginner'
            ),
            'estimated_minutes': 10
        }
```

---

### Day 6-7: Create API Endpoints and Frontend Integration

#### Task 4: Create Learning Path API Endpoints (3 hours)

Create `language-learning-platform/app/api/learning_path_routes.py`:

```python
from flask import Blueprint, request, jsonify
from app.services.learning_path_orchestrator import LearningPathOrchestrator
from app.models import db
from app.models.curriculum import NodeCompletion, UserLearningPathProgress

learning_path_bp = Blueprint('learning_path', __name__)
orchestrator = LearningPathOrchestrator()


@learning_path_bp.route('/next-activity', methods=['POST'])
def get_next_activity():
    """Get AI-determined next activity for user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # Get next activity from orchestrator
        next_activity = orchestrator.determine_next_activity(user_id)
        
        return jsonify({
            'success': True,
            'next_activity': next_activity
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@learning_path_bp.route('/complete-node', methods=['POST'])
def complete_node():
    """Mark a learning node as completed"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        node_id = data.get('node_id')
        score = data.get('score', 0.0)
        
        # Get or create node completion
        completion = NodeCompletion.query.filter_by(
            user_id=user_id,
            node_id=node_id
        ).first()
        
        if not completion:
            completion = NodeCompletion(
                user_id=user_id,
                node_id=node_id,
                first_attempt_date=datetime.utcnow()
            )
            db.session.add(completion)
        
        # Update completion
        completion.attempts += 1
        completion.last_attempt_date = datetime.utcnow()
        
        if score > (completion.best_score or 0):
            completion.best_score = score
        
        # Update average score
        if completion.average_score:
            completion.average_score = (
                (completion.average_score * (completion.attempts - 1) + score) /
                completion.attempts
            )
        else:
            completion.average_score = score
        
        # Update status based on score
        if score >= 0.9:
            completion.status = 'mastered'
            completion.mastery_date = datetime.utcnow()
            completion.mastery_level = 1.0
        elif score >= 0.7:
            completion.status = 'completed'
            completion.completion_date = datetime.utcnow()
            completion.mastery_level = score
        else:
            completion.status = 'in_progress'
            completion.mastery_level = score
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'completion': {
                'status': completion.status,
                'mastery_level': completion.mastery_level,
                'attempts': completion.attempts
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@learning_path_bp.route('/progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    """Get user's learning path progress"""
    try:
        progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
        
        if not progress:
            return jsonify({'error': 'Progress not found'}), 404
        
        # Get completion stats
        completions = NodeCompletion.query.filter_by(user_id=user_id).all()
        
        completed_count = len([c for c in completions if c.status in ['completed', 'mastered']])
        mastered_count = len([c for c in completions if c.status == 'mastered'])
        
        return jsonify({
            'success': True,
            'progress': {
                'current_level': progress.current_level,
                'target_level': progress.target_level,
                'nodes_completed': completed_count,
                'nodes_mastered': mastered_count,
                'learning_velocity': progress.learning_velocity,
                'current_focus_skill': progress.current_focus_skill,
                'weak_areas': progress.weak_areas,
                'strong_areas': progress.strong_areas
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

Register the blueprint in `app/__init__.py`:

```python
from app.api.learning_path_routes import learning_path_bp

# ... in create_app function
app.register_blueprint(learning_path_bp, url_prefix='/api/learning-path')
```

---

#### Task 5: Update Frontend Activities Page (3 hours)

Edit `ConvAI_frontV1/src/pages/Activities.jsx`:

Replace the `fetchActivities` function:

```jsx
const fetchActivities = async () => {
  try {
    setLoading(true);
    
    // Get user ID from auth context
    const userId = 1; // Replace with actual user ID from auth
    
    // Fetch AI-determined next activity
    const response = await axiosInstance.post(
      '/api/learning-path/next-activity',
      { user_id: userId }
    );
    
    if (response.data.success) {
      const nextActivity = response.data.next_activity;
      
      // Transform to match UI format
      const activity = {
        id: Date.now(), // Temporary ID
        type: nextActivity.activity_type,
        title: nextActivity.node_name || 'Practice Activity',
        description: `AI-generated personalized ${nextActivity.activity_type} activity`,
        difficulty: 'personalized',
        estimatedTime: nextActivity.estimated_minutes,
        content: nextActivity.activity_data,
        completed: false,
        progress: 0,
        tags: [nextActivity.skill_domain, 'ai-generated', 'personalized']
      };
      
      setActivities([activity]);
    }
  } catch (error) {
    console.error("Error fetching activities:", error);
    setError("Failed to load your personalized activity. Please try again.");
  } finally {
    setLoading(false);
  }
};
```

---

## 🎉 Week 1 Completion Checklist

By end of Week 1, you should have:

- [ ] ✅ Curriculum framework models created and migrated
- [ ] ✅ Seed data loaded with A1-B1 learning nodes
- [ ] ✅ Activity generator enhanced with personalization
- [ ] ✅ Learning path orchestrator determining next activities
- [ ] ✅ API endpoints for learning path operations
- [ ] ✅ Frontend fetching real AI-generated activities
- [ ] ✅ No more mock data in Activities page

---

## 🚀 Next Steps (Week 2+)

After Week 1, continue with:

1. **Week 2**: Implement more activity types (pronunciation, listening, etc.)
2. **Week 3**: Build adaptive difficulty engine
3. **Week 4**: Implement comprehensive performance tracking
4. **Week 5**: Create spaced repetition system
5. **Week 6**: Build assessment system
6. **Week 7-8**: Full frontend integration
7. **Week 9-10**: Testing and optimization

Refer to `COMPREHENSIVE_TODO_LIST.md` for detailed tasks.

---

## 💡 Quick Tips

1. **Test Frequently**: After each task, test with real user data
2. **Use Postman**: Test API endpoints before frontend integration
3. **Monitor AI Costs**: Watch your Gemini API usage
4. **Commit Often**: Git commit after each completed task
5. **Ask for Help**: If stuck, refer to existing code patterns

---

**You're ready to start! Begin with Task 1 and work through systematically. Good luck! 🚀**
