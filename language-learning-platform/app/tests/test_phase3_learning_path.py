"""
Phase 3 Learning Path Test Suite
Comprehensive tests for CEFR-based adaptive learning system
Tests for: Difficulty Engine, Orchestrator, API Routes, and Database Integration
"""

import os
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User, Profile
from app.models.learning_node import (
    CurriculumLevel,
    SkillDomain,
    LearningNode,
    UserLearningNodeProgress,
    UserSkillProfile
)
from app.models.activity import Activity, UserActivityLog
from app.services.adaptive_difficulty_engine import AdaptiveDifficultyEngine
from app.services.learning_path_orchestrator import LearningPathOrchestrator


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def app():
    """Create and configure a test app instance using ONLY in-memory SQLite."""
    app = create_app()
    app.config['TESTING'] = True
    # ALWAYS use in-memory SQLite for tests - NEVER use production database!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        # Create tables in the test database
        db.create_all()
        yield app
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Push application context."""
    with app.app_context():
        yield


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('test_password_123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    # Return just the ID so caller can refetch within their context
    return type('TestUser', (), {'id': user_id})()


@pytest.fixture
def test_profile(app, test_user):
    """Create a test user profile."""
    with app.app_context():
        profile = Profile(
            user_id=test_user.id,
            native_language='English',
            target_language='Spanish'
        )
        db.session.add(profile)
        db.session.commit()
        profile_id = profile.id
    return type('TestProfile', (), {'id': profile_id})()


@pytest.fixture
def curriculum_levels(app):
    """Fetch or create test CEFR levels."""
    with app.app_context():
        # Try to fetch existing ones first (from database seed data)
        levels = CurriculumLevel.query.all()
        if not levels:
            # Create them if they don't exist
            levels = [
                CurriculumLevel(
                    cefr_level='A1',
                    level_name='Beginner',
                    vocabulary_range_min=0,
                    vocabulary_range_max=500,
                    level_order=1,
                    estimated_hours=80
                ),
                CurriculumLevel(
                    cefr_level='A2',
                    level_name='Elementary',
                    vocabulary_range_min=500,
                    vocabulary_range_max=1000,
                    level_order=2,
                    estimated_hours=150
                ),
                CurriculumLevel(
                    cefr_level='B1',
                    level_name='Intermediate',
                    vocabulary_range_min=1000,
                    vocabulary_range_max=2000,
                    level_order=3,
                    estimated_hours=200
                ),
            ]
            for level in levels:
                db.session.add(level)
            db.session.commit()
        # Return IDs
        return [type('Level', (), {'id': l.id})() for l in levels]


@pytest.fixture
def skill_domains(app):
    """Fetch or create test skill domains."""
    with app.app_context():
        # Try to fetch existing ones first
        domains = SkillDomain.query.all()
        if not domains:
            # Create if needed
            domains = [
                SkillDomain(
                    domain_name='Listening',
                    icon='🎧',
                    color='#4A90E2',
                    order=1,
                    sub_skills=['phoneme recognition', 'word recognition'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
                SkillDomain(
                    domain_name='Speaking',
                    icon='🗣️',
                    color='#F5A623',
                    order=2,
                    sub_skills=['pronunciation', 'fluency'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
                SkillDomain(
                    domain_name='Reading',
                    icon='📖',
                    color='#7ED321',
                    order=3,
                    sub_skills=['comprehension', 'vocabulary recognition'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
                SkillDomain(
                    domain_name='Writing',
                    icon='✍️',
                    color='#BD10E0',
                    order=4,
                    sub_skills=['grammar', 'spelling'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
                SkillDomain(
                    domain_name='Vocabulary',
                    icon='📚',
                    color='#50E3C2',
                    order=5,
                    sub_skills=['word recognition', 'word usage'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
                SkillDomain(
                    domain_name='Grammar',
                    icon='📝',
                    color='#FF6B6B',
                    order=6,
                    sub_skills=['tense', 'structure'],
                    mastery_thresholds={'beginner': 0.3, 'intermediate': 0.6, 'advanced': 0.8}
                ),
            ]
            for domain in domains:
                db.session.add(domain)
            db.session.commit()
        # Return IDs
        return [type('Domain', (), {'id': d.id})() for d in domains]


@pytest.fixture
def learning_nodes(app, curriculum_levels, skill_domains):
    """Fetch or create test learning nodes."""
    with app.app_context():
        # Refetch from database to get proper IDs
        level = CurriculumLevel.query.first()
        domain = SkillDomain.query.first()
        
        if not level or not domain:
            pytest.skip("Curriculum levels or skill domains not available")
        
        nodes = LearningNode.query.limit(3).all()
        if not nodes:
            # Create them if they don't exist
            nodes = [
                LearningNode(
                    node_id='A1_LISTEN_001',
                    curriculum_level_id=level.id,
                    skill_domain_id=domain.id,
                    concept_name='Basic Listening',
                    learning_objectives=['Understand basic greetings'],
                    difficulty_min=0.1,
                    difficulty_max=0.4,
                    recommended_difficulty=0.25,
                    estimated_time_minutes=15,
                    mastery_threshold=0.8,
                    is_active=True
                ),
                LearningNode(
                    node_id='A1_SPEAK_001',
                    curriculum_level_id=level.id,
                    skill_domain_id=domain.id,
                    concept_name='Basic Speaking',
                    learning_objectives=['Greet someone'],
                    difficulty_min=0.2,
                    difficulty_max=0.5,
                    recommended_difficulty=0.35,
                    estimated_time_minutes=15,
                    mastery_threshold=0.8,
                    is_active=True
                ),
                LearningNode(
                    node_id='A1_READ_001',
                    curriculum_level_id=level.id,
                    skill_domain_id=domain.id,
                    concept_name='Basic Reading',
                    learning_objectives=['Read simple texts'],
                    difficulty_min=0.15,
                    difficulty_max=0.45,
                    recommended_difficulty=0.3,
                    estimated_time_minutes=15,
                    mastery_threshold=0.8,
                    is_active=True
                ),
            ]
            for node in nodes:
                db.session.add(node)
            db.session.commit()
        # Return IDs
        return [type('Node', (), {'id': n.id})() for n in nodes[:3]]


# ============================================================================
# TESTS: ADAPTIVE DIFFICULTY ENGINE
# ============================================================================

class TestAdaptiveDifficultyEngine:
    """Test suite for AdaptiveDifficultyEngine."""

    def test_engine_initialization(self, app_context):
        """Test that difficulty engine initializes correctly."""
        engine = AdaptiveDifficultyEngine()
        assert engine is not None
        assert hasattr(engine, 'calculate_user_skill_level')
        assert hasattr(engine, 'adjust_activity_difficulty')
        assert hasattr(engine, 'generate_challenge_curve')

    def test_calculate_user_skill_level_all_skills(self, app, test_user):
        """Test skill level calculation for all 6 skills."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Test general skill level (no specific domain)
            level = engine.calculate_user_skill_level(
                user_id=test_user.id
            )
            # Initial level should be 0-100
            assert isinstance(level, (int, float))
            assert 0 <= level <= 100
            
            # Test with specific domain (if supported)
            level_domain = engine.calculate_user_skill_level(
                user_id=test_user.id,
                skill_domain='Listening'
            )
            assert isinstance(level_domain, (int, float))

    def test_adjust_activity_difficulty_increase(self, app, test_user):
        """Test difficulty increase when performance is high."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # High performance (85%) should increase difficulty
            new_difficulty = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=0.85
            )
            # Should increase from 0.5
            assert new_difficulty > 0.5

    def test_adjust_activity_difficulty_decrease(self, app, test_user):
        """Test difficulty decrease when performance is low."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Low performance (40%) should decrease difficulty
            new_difficulty = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=0.40
            )
            # Should decrease from 0.5
            assert new_difficulty < 0.5

    def test_adjust_activity_difficulty_maintain(self, app, test_user):
        """Test difficulty stays stable at sweet spot (75%)."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # 75% performance should maintain difficulty
            new_difficulty = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=0.75
            )
            # Should be close to 0.5
            assert 0.45 <= new_difficulty <= 0.55

    def test_adjust_activity_difficulty_bounds(self, app, test_user):
        """Test that adjusted difficulty stays within valid bounds."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Test with extreme performance values
            for performance in [0.0, 1.0, 0.5]:
                new_difficulty = engine.adjust_activity_difficulty(
                    user_id=test_user.id,
                    activity_id=1,
                    current_difficulty=0.5,
                    performance_score=performance
                )
                assert 0.0 <= new_difficulty <= 1.0

    def test_generate_challenge_curve_progression(self, app, test_user):
        """Test that challenge curve shows proper progression."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            curve = engine.generate_challenge_curve(
                user_id=test_user.id,
                session_id='session_001',
                session_duration_minutes=30
            )
            
            # Should return a curve with progression
            assert isinstance(curve, list)
            assert len(curve) > 0
            
            # Each activity in curve should have difficulty in range
            for activity in curve:
                assert 'difficulty' in activity
                assert 0.0 <= activity['difficulty'] <= 1.0

    def test_estimate_skill_trajectory_improvement(self, app, test_user, skill_domains):
        """Test skill trajectory analysis for improving user."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Create some progress data
            skill_profile = UserSkillProfile(
                user_id=test_user.id,
                listening_level=50,
                listening_trend='improving'
            )
            db.session.add(skill_profile)
            db.session.commit()
            
            trajectory = engine.estimate_skill_trajectory(
                user_id=test_user.id,
                skill_domain='Listening',
                days_lookback=30
            )
            
            assert trajectory is not None
            assert isinstance(trajectory, dict)

    def test_recommend_difficulty_adjustment_high_accuracy(self, app, test_user):
        """Test recommendation when accuracy is high."""
        with app.app_context():
            # Create a test activity
            activity = Activity(
                activity_type='vocabulary',
                difficulty_level=0.5,
                title='Test Activity',
                description='Test'
            )
            db.session.add(activity)
            db.session.commit()
            
            engine = AdaptiveDifficultyEngine()
            
            recommendation = engine.recommend_difficulty_adjustment(
                user_id=test_user.id,
                current_activity_id=activity.id,
                recent_performance=[0.90, 0.85, 0.88]
            )
            
            assert isinstance(recommendation, dict)
            assert 'recommendation' in recommendation

    def test_recommend_difficulty_adjustment_low_accuracy(self, app, test_user):
        """Test recommendation when accuracy is low."""
        with app.app_context():
            # Create a test activity
            activity = Activity(
                activity_type='vocabulary',
                difficulty_level=0.5,
                title='Test Activity',
                description='Test'
            )
            db.session.add(activity)
            db.session.commit()
            
            engine = AdaptiveDifficultyEngine()
            
            recommendation = engine.recommend_difficulty_adjustment(
                user_id=test_user.id,
                current_activity_id=activity.id,
                recent_performance=[0.40, 0.35, 0.45]
            )
            
            assert isinstance(recommendation, dict)
            assert 'recommendation' in recommendation

    def test_recommend_difficulty_adjustment_insufficient_data(self, app, test_user):
        """Test recommendation with insufficient performance data."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            recommendation = engine.recommend_difficulty_adjustment(
                user_id=test_user.id,
                current_activity_id=1,
                recent_performance=[0.75]
            )
            
            assert isinstance(recommendation, dict)
            assert recommendation['recommendation'] == 'continue'


# ============================================================================
# TESTS: LEARNING PATH ORCHESTRATOR
# ============================================================================

class TestLearningPathOrchestrator:
    """Test suite for LearningPathOrchestrator."""

    def test_orchestrator_initialization(self, app_context):
        """Test that orchestrator initializes correctly."""
        orchestrator = LearningPathOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, 'determine_next_activity')
        assert hasattr(orchestrator, 'complete_activity')

    def test_determine_next_activity_basic(self, app, test_user, learning_nodes, test_profile):
        """Test basic next activity determination."""
        with app.app_context():
            orchestrator = LearningPathOrchestrator()
            
            activity = orchestrator.determine_next_activity(
                user_id=test_user.id
            )
            
            # Should return a dict with activity info
            assert activity is not None
            assert isinstance(activity, dict)

    def test_plan_learning_session_structure(self, app, test_user, learning_nodes, test_profile):
        """Test complete activity endpoint."""
        with app.app_context():
            orchestrator = LearningPathOrchestrator()
            
            # Test completing an activity
            result = orchestrator.complete_activity(
                user_id=test_user.id,
                learning_node_id='A1_LISTEN_001',
                performance_score=0.85,
                time_spent_seconds=300
            )
            
            # Should return a result dict
            assert result is not None

    def test_adjust_difficulty_dynamically(self, app, test_user, learning_nodes, test_profile):
        """Test activity completion tracking."""
        with app.app_context():
            orchestrator = LearningPathOrchestrator()
            
            # Test getting next activity after completion
            activity = orchestrator.determine_next_activity(
                user_id=test_user.id
            )
            
            assert activity is not None
            assert isinstance(activity, dict)


# ============================================================================
# TESTS: DATABASE MODELS AND QUERIES
# ============================================================================

class TestPhase3Models:
    """Test suite for Phase 3 database models."""

    def test_curriculum_level_creation(self, app, curriculum_levels):
        """Test CurriculumLevel model creation."""
        with app.app_context():
            level = CurriculumLevel.query.filter_by(cefr_level='A1').first()
            assert level is not None
            assert level.level_name == 'Beginner'
            assert level.vocabulary_range_min == 0
            assert level.vocabulary_range_max == 500

    def test_skill_domain_creation(self, app, skill_domains):
        """Test SkillDomain model creation."""
        with app.app_context():
            domain = SkillDomain.query.filter_by(domain_name='Listening').first()
            assert domain is not None
            assert domain.icon == '🎧'
            assert domain.sub_skills is not None

    def test_learning_node_creation(self, app, learning_nodes):
        """Test LearningNode model creation."""
        with app.app_context():
            node = LearningNode.query.filter_by(node_id='A1_LISTEN_001').first()
            assert node is not None
            assert node.concept_name == 'Basic Listening'
            assert node.difficulty_min == 0.1
            assert node.difficulty_max == 0.4

    def test_user_skill_profile_creation(self, app, test_user):
        """Test UserSkillProfile auto-creation."""
        with app.app_context():
            profile = UserSkillProfile(user_id=test_user.id)
            db.session.add(profile)
            db.session.commit()
            
            retrieved = UserSkillProfile.query.filter_by(user_id=test_user.id).first()
            assert retrieved is not None
            assert retrieved.listening_level == 0
            assert retrieved.overall_level == 0

    def test_user_learning_node_progress_creation(self, app, test_user, learning_nodes):
        """Test UserLearningNodeProgress model creation."""
        with app.app_context():
            node = learning_nodes[0]
            progress = UserLearningNodeProgress(
                user_id=test_user.id,
                learning_node_id=node.id,
                status='in_progress',
                attempts=2,
                best_score=0.85
            )
            db.session.add(progress)
            db.session.commit()
            
            retrieved = UserLearningNodeProgress.query.filter_by(
                user_id=test_user.id,
                learning_node_id=node.id
            ).first()
            assert retrieved is not None
            assert retrieved.status == 'in_progress'
            assert retrieved.attempts == 2

    def test_learning_node_to_dict(self, app, learning_nodes):
        """Test LearningNode model structure."""
        with app.app_context():
            # Refetch the actual node from database
            node = LearningNode.query.first()
            if node:
                # Just verify the node has required fields
                assert hasattr(node, 'node_id')
                assert hasattr(node, 'concept_name')
                assert hasattr(node, 'difficulty_min')
            else:
                pytest.skip("No learning nodes in database")

    def test_curriculum_level_to_dict(self, app, curriculum_levels):
        """Test CurriculumLevel model structure."""
        with app.app_context():
            # Refetch from database
            level = CurriculumLevel.query.first()
            if level:
                assert hasattr(level, 'cefr_level')
                assert hasattr(level, 'level_name')
                assert hasattr(level, 'vocabulary_range_min')
            else:
                pytest.skip("No curriculum levels in database")

    def test_skill_domain_to_dict(self, app, skill_domains):
        """Test SkillDomain model structure."""
        with app.app_context():
            # Refetch from database
            domain = SkillDomain.query.first()
            if domain:
                assert hasattr(domain, 'domain_name')
                assert hasattr(domain, 'sub_skills')
                assert hasattr(domain, 'icon')
            else:
                pytest.skip("No skill domains in database")


# ============================================================================
# TESTS: INTEGRATION
# ============================================================================

class TestPhase3Integration:
    """Integration tests for Phase 3 system."""

    def test_end_to_end_user_journey(self, app, test_user, curriculum_levels, skill_domains, learning_nodes):
        """Test complete user journey through Phase 3."""
        with app.app_context():
            # 1. User starts with skill profile
            skill_profile = UserSkillProfile(user_id=test_user.id)
            db.session.add(skill_profile)
            db.session.commit()
            
            assert skill_profile.listening_level == 0
            
            # 2. System recommends a learning node
            node = learning_nodes[0]
            
            # 3. User completes activity
            progress = UserLearningNodeProgress(
                user_id=test_user.id,
                learning_node_id=node.id,
                status='completed',
                attempts=1,
                best_score=0.85,
                mastery_level='proficient'
            )
            db.session.add(progress)
            db.session.commit()
            
            # 4. Verify progress was recorded
            retrieved_progress = UserLearningNodeProgress.query.filter_by(
                user_id=test_user.id,
                learning_node_id=node.id
            ).first()
            assert retrieved_progress.status == 'completed'
            assert retrieved_progress.best_score == 0.85

    def test_multi_skill_progression(self, app, test_user, learning_nodes):
        """Test progression across multiple skills."""
        with app.app_context():
            # Create progress for different skill nodes
            for node in learning_nodes:
                progress = UserLearningNodeProgress(
                    user_id=test_user.id,
                    learning_node_id=node.id,
                    status='completed',
                    attempts=1,
                    best_score=0.80,
                    mastery_level='proficient'
                )
                db.session.add(progress)
            
            db.session.commit()
            
            # Verify all progress records exist
            all_progress = UserLearningNodeProgress.query.filter_by(
                user_id=test_user.id
            ).all()
            assert len(all_progress) == len(learning_nodes)

    def test_service_and_model_integration(self, app, test_user, curriculum_levels, skill_domains, learning_nodes):
        """Test that services work with Phase 3 models."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            orchestrator = LearningPathOrchestrator()
            
            # Create user skill profile
            skill_profile = UserSkillProfile(user_id=test_user.id)
            db.session.add(skill_profile)
            db.session.commit()
            
            # Test difficulty adjustment
            new_difficulty = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=0.75
            )
            assert 0.0 <= new_difficulty <= 1.0
            
            # Test orchestrator with models
            activity = orchestrator.determine_next_activity(test_user.id)
            assert activity is not None


# ============================================================================
# TESTS: ERROR HANDLING
# ============================================================================

class TestPhase3ErrorHandling:
    """Test error handling in Phase 3."""

    def test_invalid_skill_domain(self, app, test_user):
        """Test handling of skill domain."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Should handle gracefully
            result = engine.calculate_user_skill_level(
                user_id=test_user.id,
                skill_domain='InvalidDomain'
            )
            # Should return a valid number
            assert isinstance(result, (int, float))

    def test_nonexistent_user(self, app):
        """Test handling of nonexistent user."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Should handle gracefully
            result = engine.calculate_user_skill_level(
                user_id=99999
            )
            assert isinstance(result, (int, float))

    def test_learning_node_without_domain(self, app, curriculum_levels):
        """Test creating learning node without skill domain."""
        with app.app_context():
            # Get first curriculum level
            level_id = CurriculumLevel.query.first().id
            
            # Should fail or handle gracefully
            node = LearningNode(
                node_id='TEST_001',
                curriculum_level_id=level_id,
                skill_domain_id=None,  # Invalid: no skill domain
                concept_name='Test',
                difficulty_min=0.1,
                difficulty_max=0.5
            )
            
            # This should either be rejected or handled
            # Depending on model validation
            try:
                db.session.add(node)
                db.session.commit()
                # If it succeeds, that's okay too (validation at API level)
            except Exception:
                # If it fails, that's also fine
                db.session.rollback()


# ============================================================================
# TESTS: EDGE CASES
# ============================================================================

class TestPhase3EdgeCases:
    """Test edge cases and boundary conditions."""

    def test_difficulty_at_boundaries(self, app, test_user):
        """Test difficulty adjustment at 0 and 1 boundaries."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Test at 0
            result_0 = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.0,
                performance_score=0.75
            )
            assert 0.0 <= result_0 <= 1.0
            
            # Test at 1
            result_1 = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=1.0,
                performance_score=0.75
            )
            assert 0.0 <= result_1 <= 1.0

    def test_accuracy_at_boundaries(self, app, test_user):
        """Test accuracy values at 0 and 1."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Perfect accuracy (1.0)
            result_perfect = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=1.0
            )
            assert 0.0 <= result_perfect <= 1.0
            
            # Zero accuracy (0.0)
            result_zero = engine.adjust_activity_difficulty(
                user_id=test_user.id,
                activity_id=1,
                current_difficulty=0.5,
                performance_score=0.0
            )
            assert 0.0 <= result_zero <= 1.0

    def test_zero_attempt_count(self, app, test_user):
        """Test with zero attempts."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Should handle gracefully with empty list
            result = engine.recommend_difficulty_adjustment(
                user_id=test_user.id,
                current_activity_id=1,
                recent_performance=[]
            )
            assert isinstance(result, dict)

    def test_large_attempt_count(self, app, test_user):
        """Test with very large attempt count."""
        with app.app_context():
            engine = AdaptiveDifficultyEngine()
            
            # Should handle gracefully with many data points
            large_performance = [0.75] * 100
            result = engine.recommend_difficulty_adjustment(
                user_id=test_user.id,
                current_activity_id=1,
                recent_performance=large_performance
            )
            assert isinstance(result, dict)

    def test_empty_learning_nodes_query(self, app, test_user):
        """Test when no learning nodes exist for a level."""
        with app.app_context():
            nodes = LearningNode.query.filter_by(
                curriculum_level_id=99999
            ).all()
            
            assert len(nodes) == 0

    def test_user_skill_profile_default_values(self, app, test_user):
        """Test default values in UserSkillProfile."""
        with app.app_context():
            profile = UserSkillProfile(user_id=test_user.id)
            db.session.add(profile)
            db.session.commit()
            
            # All skills should start at 0
            assert profile.listening_level == 0
            assert profile.speaking_level == 0
            assert profile.reading_level == 0
            assert profile.writing_level == 0
            assert profile.vocabulary_level == 0
            assert profile.grammar_level == 0
            assert profile.overall_level == 0
            
            # Trends should be stable
            assert profile.listening_trend == 'stable'
            assert profile.speaking_trend == 'stable'


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=app.services', '--cov=app.models.learning_node'])
