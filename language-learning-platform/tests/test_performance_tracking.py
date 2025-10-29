"""
Phase 4: Comprehensive Unit Tests for Performance Tracking
Tests for models, services, and API endpoints
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from app.models import db
from app.models.user import User
from app.models.activity import Activity
from app.models.performance_tracking import (
    ListeningPerformance,
    SpeakingPerformance,
    ReadingPerformance,
    WritingPerformance,
    RealWorldPerformance,
    SkillTrajectory
)
from app.services.performance_tracking_service import PerformanceTrackingEngine


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def test_activity(app):
    """Create test activity - optional since activity_id is nullable"""
    with app.app_context():
        # Activity is optional in performance tracking
        # Return None to test without activity
        return None


@pytest.fixture
def engine(app):
    """Create performance tracking engine"""
    with app.app_context():
        return PerformanceTrackingEngine()


# ==================== MODEL TESTS ====================

def test_listening_performance_creation(app, test_user, test_activity):
    """Test creating a listening performance record"""
    with app.app_context():
        performance = ListeningPerformance(
            user_id=test_user,
            activity_id=test_activity,
            audio_duration=120.5,
            accent_type='american',
            speed_factor=1.0,
            topic='travel',
            difficulty_level='intermediate',
            comprehension_score=85.0,
            accuracy_percentage=87.5,
            total_questions=10,
            correct_answers=8,
            mastery_level='proficient'
        )
        db.session.add(performance)
        db.session.commit()
        
        assert performance.id is not None
        assert performance.comprehension_score == 85.0
        assert performance.mastery_level == 'proficient'


def test_listening_performance_to_dict(app, test_user, test_activity):
    """Test serialization of listening performance"""
    with app.app_context():
        performance = ListeningPerformance(
            user_id=test_user,
            activity_id=test_activity,
            audio_duration=120.5,
            accent_type='british',
            comprehension_score=90.0,
            difficulty_level='advanced',
            total_questions=10,
            correct_answers=9,
            mastery_level='advanced'
        )
        db.session.add(performance)
        db.session.commit()
        
        data = performance.to_dict()
        assert 'id' in data
        assert data['comprehension_score'] == 90.0
        assert data['accent_type'] == 'british'
        assert 'completed_at' in data


def test_skill_trajectory_creation(app, test_user):
    """Test creating a skill trajectory record"""
    with app.app_context():
        trajectory = SkillTrajectory(
            user_id=test_user,
            skill_domain='listening',
            current_level=75.0,
            mastery_status='proficient',
            baseline_level=60.0,
            peak_level=75.0,
            lowest_level=60.0,
            total_practice_sessions=5,
            performance_history=[
                {'date': datetime.utcnow().isoformat(), 'score': 75.0, 'activity_type': 'listening'}
            ]
        )
        db.session.add(trajectory)
        db.session.commit()
        
        assert trajectory.id is not None
        assert trajectory.skill_domain == 'listening'
        assert trajectory.current_level == 75.0


# ==================== SERVICE TESTS ====================

def test_track_listening_performance(app, test_user, test_activity, engine):
    """Test tracking listening performance"""
    with app.app_context():
        performance_data = {
            'session_id': 'test-session-1',
            'audio_duration': 180.0,
            'audio_url': 'https://example.com/audio.mp3',
            'accent_type': 'american',
            'speed_factor': 1.0,
            'topic': 'business',
            'difficulty_level': 'intermediate',
            'comprehension_score': 82.0,
            'accuracy_percentage': 85.0,
            'playback_count': 2,
            'pause_points': [30.5, 60.2, 90.1],
            'total_questions': 8,
            'correct_answers': 7,
            'time_to_complete': 240
        }
        
        performance = engine.track_listening_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.comprehension_score == 82.0
        assert performance.pause_count == 3
        assert performance.mastery_level == 'proficient'


def test_track_speaking_performance(app, test_user, test_activity, engine):
    """Test tracking speaking performance"""
    with app.app_context():
        performance_data = {
            'session_id': 'test-session-2',
            'speaking_type': 'conversation',
            'topic': 'travel',
            'difficulty_level': 'intermediate',
            'recording_duration': 90.0,
            'transcript': 'This is a test transcript',
            'pronunciation_accuracy': 88.0,
            'fluency_score': 85.0,
            'grammar_score': 90.0,
            'vocabulary_richness': 80.0,
            'overall_score': 86.0,
            'words_per_minute': 120,
            'confidence_level': 75.0
        }
        
        performance = engine.track_speaking_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.overall_score == 86.0
        assert performance.speaking_type == 'conversation'
        assert performance.mastery_level == 'expert'


def test_track_reading_performance(app, test_user, test_activity, engine):
    """Test tracking reading performance"""
    with app.app_context():
        performance_data = {
            'text_title': 'Business Article',
            'text_type': 'article',
            'topic': 'economics',
            'difficulty_level': 'advanced',
            'word_count': 500,
            'reading_time_seconds': 240,
            'reading_speed_wpm': 125,
            'comprehension_score': 88.0,
            'accuracy_percentage': 90.0,
            'total_questions': 10,
            'correct_answers': 9
        }
        
        performance = engine.track_reading_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.comprehension_score == 88.0
        assert performance.reading_speed_wpm == 125
        assert performance.mastery_level == 'expert'


def test_track_writing_performance(app, test_user, test_activity, engine):
    """Test tracking writing performance"""
    with app.app_context():
        performance_data = {
            'writing_type': 'essay',
            'topic': 'Technology',
            'prompt': 'Write about the impact of AI',
            'difficulty_level': 'advanced',
            'content': 'This is a test essay about AI technology...',
            'word_count': 250,
            'overall_score': 85.0,
            'grammar_score': 88.0,
            'vocabulary_score': 82.0,
            'coherence_score': 86.0,
            'writing_time_minutes': 30
        }
        
        performance = engine.track_writing_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.overall_score == 85.0
        assert performance.word_count == 250
        assert performance.mastery_level == 'expert'


def test_track_real_world_performance(app, test_user, test_activity, engine):
    """Test tracking real-world scenario performance"""
    with app.app_context():
        performance_data = {
            'scenario_type': 'email',
            'industry': 'business',
            'context': 'Professional email to client',
            'difficulty_level': 'intermediate',
            'task_description': 'Write a follow-up email',
            'user_response': 'Dear Client, Following up on our meeting...',
            'overall_score': 84.0,
            'task_completion': 90.0,
            'appropriateness_score': 88.0,
            'professional_language_use': 85.0
        }
        
        performance = engine.track_real_world_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.overall_score == 84.0
        assert performance.scenario_type == 'email'
        assert performance.mastery_level == 'proficient'


def test_skill_trajectory_update(app, test_user, test_activity, engine):
    """Test skill trajectory updates after performance tracking"""
    with app.app_context():
        # Track multiple performances
        for i in range(3):
            performance_data = {
                'audio_duration': 120.0,
                'comprehension_score': 70.0 + (i * 5),  # Improving scores
                'difficulty_level': 'intermediate',
                'total_questions': 10,
                'correct_answers': 7 + i,
                'accuracy_percentage': 70.0 + (i * 5)
            }
            
            engine.track_listening_performance(
                user_id=test_user,
                activity_id=test_activity,
                performance_data=performance_data
            )
        
        # Check trajectory was created and updated
        trajectory = SkillTrajectory.query.filter_by(
            user_id=test_user,
            skill_domain='listening'
        ).first()
        
        assert trajectory is not None
        assert trajectory.total_practice_sessions == 3
        assert len(trajectory.performance_history) == 3
        assert trajectory.current_level == 80.0  # Last score
        assert trajectory.trend_direction == 'improving'


def test_analyze_skill_trajectory(app, test_user, test_activity, engine):
    """Test skill trajectory analysis"""
    with app.app_context():
        # Create trajectory with history
        trajectory = SkillTrajectory(
            user_id=test_user,
            skill_domain='speaking',
            current_level=78.0,
            mastery_status='proficient',
            baseline_level=60.0,
            peak_level=78.0,
            total_practice_sessions=10,
            performance_history=[
                {'date': (datetime.utcnow() - timedelta(days=i)).isoformat(), 
                 'score': 60.0 + (i * 2), 
                 'activity_type': 'speaking'}
                for i in range(10)
            ],
            practice_frequency=3.0,
            consistency_score=85.0
        )
        db.session.add(trajectory)
        db.session.commit()
        
        # Analyze trajectory
        analysis = engine.analyze_skill_trajectory(
            user_id=test_user,
            skill_domain='speaking',
            time_window_days=30
        )
        
        assert 'skill_domain' in analysis
        assert 'current_level' in analysis
        assert 'statistics' in analysis
        assert 'trend' in analysis
        assert analysis['skill_domain'] == 'speaking'


def test_predict_mastery_timeline(app, test_user, engine):
    """Test mastery timeline prediction"""
    with app.app_context():
        # Create trajectory with consistent improvement
        trajectory = SkillTrajectory(
            user_id=test_user,
            skill_domain='reading',
            current_level=70.0,
            mastery_status='proficient',
            baseline_level=50.0,
            peak_level=70.0,
            total_practice_sessions=15,
            performance_history=[
                {'date': (datetime.utcnow() - timedelta(days=i*2)).isoformat(), 
                 'score': 50.0 + (i * 1.5), 
                 'activity_type': 'reading'}
                for i in range(15)
            ],
            practice_frequency=3.5
        )
        db.session.add(trajectory)
        db.session.commit()
        
        # Predict mastery
        prediction = engine.predict_mastery_timeline(
            user_id=test_user,
            skill_domain='reading'
        )
        
        assert 'skill_domain' in prediction
        assert 'current_level' in prediction
        assert 'estimated_days' in prediction
        assert prediction['current_level'] == 70.0


def test_determine_mastery_level(engine):
    """Test mastery level determination"""
    assert engine._determine_mastery_level(95.0) == 'expert'
    assert engine._determine_mastery_level(80.0) == 'advanced'
    assert engine._determine_mastery_level(70.0) == 'proficient'
    assert engine._determine_mastery_level(50.0) == 'developing'
    assert engine._determine_mastery_level(30.0) == 'novice'


def test_calculate_trend(engine):
    """Test trend calculation"""
    # Improving trend
    improving_scores = [60, 65, 70, 75, 80]
    trend = engine._calculate_trend(improving_scores)
    assert trend['direction'] == 'improving'
    assert trend['strength'] > 0
    
    # Declining trend
    declining_scores = [80, 75, 70, 65, 60]
    trend = engine._calculate_trend(declining_scores)
    assert trend['direction'] == 'declining'
    
    # Stable trend
    stable_scores = [75, 74, 76, 75, 75]
    trend = engine._calculate_trend(stable_scores)
    assert trend['direction'] == 'stable'


def test_determine_velocity(engine):
    """Test learning velocity determination"""
    # Fast improvement
    fast_scores = [50, 55, 65, 75, 85]
    velocity = engine._determine_velocity(fast_scores)
    assert velocity in ['fast', 'accelerating']
    
    # Steady improvement
    steady_scores = [70, 72, 74, 76, 78]
    velocity = engine._determine_velocity(steady_scores)
    assert velocity == 'steady'
    
    # Plateauing
    plateau_scores = [75, 75, 76, 75, 75]
    velocity = engine._determine_velocity(plateau_scores)
    assert velocity in ['plateauing', 'steady']  # Both are acceptable for minimal change


# ==================== API ENDPOINT TESTS ====================

def test_track_performance_endpoint(client, app, test_user, test_activity):
    """Test POST /api/performance/track endpoint"""
    with app.app_context():
        # Create JWT token for authentication
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=test_user)
        
        payload = {
            'user_id': test_user,
            'activity_id': test_activity,
            'skill_type': 'listening',
            'performance_data': {
                'audio_duration': 150.0,
                'comprehension_score': 85.0,
                'difficulty_level': 'intermediate',
                'total_questions': 10,
                'correct_answers': 8
            }
        }
        
        response = client.post(
            '/api/performance/track',
            json=payload,
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'performance' in data or 'success' in data


def test_get_skill_trajectory_endpoint(client, app, test_user):
    """Test GET /api/performance/trajectory endpoint"""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=test_user)
        
        # Create a trajectory first
        trajectory = SkillTrajectory(
            user_id=test_user,
            skill_domain='speaking',
            current_level=75.0,
            mastery_status='proficient'
        )
        db.session.add(trajectory)
        db.session.commit()
        
        response = client.get(
            f'/api/performance/trajectory/{test_user}/speaking',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'skill_domain' in data or 'trajectory' in data


# ==================== EDGE CASE TESTS ====================

def test_track_performance_with_missing_data(app, test_user, test_activity, engine):
    """Test tracking with minimal required data"""
    with app.app_context():
        performance_data = {
            'audio_duration': 100.0,
            'comprehension_score': 75.0,
            'difficulty_level': 'beginner'
        }
        
        performance = engine.track_listening_performance(
            user_id=test_user,
            activity_id=test_activity,
            performance_data=performance_data
        )
        
        assert performance is not None
        assert performance.comprehension_score == 75.0


def test_trajectory_with_insufficient_data(app, test_user, engine):
    """Test analysis with insufficient trajectory data"""
    with app.app_context():
        # Create trajectory with minimal data
        trajectory = SkillTrajectory(
            user_id=test_user,
            skill_domain='writing',
            current_level=60.0,
            mastery_status='developing'
        )
        db.session.add(trajectory)
        db.session.commit()
        
        analysis = engine.analyze_skill_trajectory(
            user_id=test_user,
            skill_domain='writing'
        )
        
        assert 'message' in analysis or 'skill_domain' in analysis


def test_llm_service_fallback(app, engine):
    """Test that LLMService falls back gracefully when unavailable"""
    with app.app_context():
        # This should not raise an error even if LLM is not configured
        try:
            llm_service = engine.llm_service
            result = llm_service.summarize_performance({'score': 75.0})
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"LLMService should fallback gracefully, but raised: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
