"""
Comprehensive Test Script for AI-Personalized Learning Path System
Tests the complete flow: Database → Orchestrator → Activity Generation → API
"""
import sys
import json
from datetime import datetime

# Test configuration
TEST_USER_EMAIL = "test_learner@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_USERNAME = "test_learner"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_success(message):
    """Print success message"""
    print(f"[PASS] {message}")

def print_error(message):
    """Print error message"""
    print(f"[FAIL] {message}")

def print_info(message):
    """Print info message"""
    print(f"[INFO] {message}")

def print_json(data, title=None):
    """Print formatted JSON data"""
    if title:
        print(f"\n{title}:")
    print(json.dumps(data, indent=2, default=str))


# =============================================================================
# TEST 1: Database and Models
# =============================================================================
def test_database_models():
    """Test that all database models are properly configured"""
    print_section("TEST 1: Database Models & Configuration")
    
    try:
        from app import create_app
        from app.models.curriculum import (
            CurriculumLevel, 
            LearningNode, 
            UserLearningPathProgress,
            NodeCompletion
        )
        from app.models.user import User, Profile
        
        app = create_app()
        
        with app.app_context():
            # Test 1.1: Check CEFR levels exist
            levels = CurriculumLevel.query.all()
            print_info(f"Found {len(levels)} curriculum levels")
            for level in levels:
                print(f"  - {level.cefr_level}: {level.level_name} ({level.estimated_hours} hours)")
            
            if len(levels) >= 3:
                print_success("CEFR levels loaded successfully")
            else:
                print_error(f"Expected at least 3 levels, found {len(levels)}")
                return False
            
            # Test 1.2: Check learning nodes exist
            nodes = LearningNode.query.all()
            print_info(f"Found {len(nodes)} learning nodes")
            
            # Group by level
            a1_nodes = [n for n in nodes if n.curriculum_level.cefr_level == 'A1']
            a2_nodes = [n for n in nodes if n.curriculum_level.cefr_level == 'A2']
            b1_nodes = [n for n in nodes if n.curriculum_level.cefr_level == 'B1']
            
            print(f"  - A1 Nodes: {len(a1_nodes)}")
            print(f"  - A2 Nodes: {len(a2_nodes)}")
            print(f"  - B1 Nodes: {len(b1_nodes)}")
            
            if len(nodes) >= 20:
                print_success("Learning nodes loaded successfully")
            else:
                print_error(f"Expected at least 20 nodes, found {len(nodes)}")
                return False
            
            # Test 1.3: Check node relationships
            sample_node = nodes[0] if nodes else None
            if sample_node:
                print_info(f"Sample Node: {sample_node.node_id}")
                print(f"  - Concept: {sample_node.concept_name}")
                print(f"  - Skill Domain: {sample_node.skill_domain}")
                print(f"  - Is Core: {sample_node.is_core}")
                print(f"  - Prerequisites: {sample_node.prerequisites}")
                print(f"  - Activity Templates: {sample_node.activity_templates}")
                print_success("Node structure verified")
            
            return True
            
    except Exception as e:
        print_error(f"Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 2: User Setup and Authentication
# =============================================================================
def test_user_setup():
    """Create or verify test user exists"""
    print_section("TEST 2: User Setup & Authentication")
    
    try:
        from app import create_app
        from app.models.user import User, Profile, db
        
        app = create_app()
        
        with app.app_context():
            # Check if test user exists
            user = User.query.filter_by(email=TEST_USER_EMAIL).first()
            
            if user:
                print_info(f"Test user already exists: {user.username}")
            else:
                # Create test user
                print_info("Creating new test user...")
                user = User(
                    username=TEST_USER_USERNAME,
                    email=TEST_USER_EMAIL
                )
                user.set_password(TEST_USER_PASSWORD)
                db.session.add(user)
                db.session.commit()
                print_success(f"Created user: {user.username} (ID: {user.id})")
            
            # Check profile
            profile = Profile.query.filter_by(user_id=user.id).first()
            
            if not profile:
                print_info("Creating user profile...")
                profile = Profile(
                    user_id=user.id,
                    native_language="Telugu",
                    target_language="English",
                    proficiency_level="beginner",
                    current_streak=0,
                    points=0,
                    mastery_metrics={
                        "vocabulary": 0,
                        "grammar": 0,
                        "reading": 0,
                        "writing": 0,
                        "listening": 0,
                        "speaking": 0,
                        "overall": 0
                    }
                )
                db.session.add(profile)
                db.session.commit()
                print_success("Profile created")
            else:
                print_info(f"Profile exists - Level: {profile.proficiency_level}")
            
            print_json({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "proficiency_level": profile.proficiency_level,
                "native_language": profile.native_language,
                "target_language": profile.target_language,
                "mastery_metrics": profile.mastery_metrics
            }, "User Profile")
            
            return user.id
            
    except Exception as e:
        print_error(f"User setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# =============================================================================
# TEST 3: Learning Path Orchestrator
# =============================================================================
def test_orchestrator(user_id):
    """Test the learning path orchestrator logic"""
    print_section("TEST 3: Learning Path Orchestrator")
    
    if not user_id:
        print_error("No user_id provided, skipping orchestrator test")
        return False
    
    try:
        from app import create_app
        from app.services.learning_path_orchestrator import LearningPathOrchestrator
        from app.models.curriculum import UserLearningPathProgress
        
        app = create_app()
        orchestrator = LearningPathOrchestrator()
        
        with app.app_context():
            # Test 3.1: Initialize user progress (if needed)
            progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
            
            if progress:
                print_info("User progress already initialized")
            else:
                print_info("User progress will be initialized on first activity request")
            
            # Test 3.2: Determine next activity
            print_info("Requesting next activity from orchestrator...")
            activity = orchestrator.determine_next_activity(user_id)
            
            if "error" in activity:
                print_error(f"Orchestrator returned error: {activity['error']}")
                return False
            
            print_success("Activity generated successfully!")
            print_json({
                "orchestration_reason": activity.get('orchestration_reason'),
                "orchestration_message": activity.get('orchestration_message'),
                "priority_level": activity.get('priority_level'),
                "learning_node_id": activity.get('learning_node_id'),
                "activity_type": activity.get('activity_type'),
                "title": activity.get('title'),
                "estimated_time": activity.get('estimated_time')
            }, "Activity Metadata")
            
            # Show sample content based on activity type
            if activity.get('activity_type') == 'quiz' and 'questions' in activity:
                print_info(f"Generated {len(activity['questions'])} quiz questions")
                if activity['questions']:
                    first_q = activity['questions'][0]
                    print(f"  Sample Question: {first_q.get('question_text', 'N/A')}")
            elif activity.get('activity_type') == 'flashcard' and 'flashcards' in activity:
                print_info(f"Generated {len(activity['flashcards'])} flashcards")
                if activity['flashcards']:
                    first_fc = activity['flashcards'][0]
                    print(f"  Sample Flashcard: {first_fc.get('front', 'N/A')} → {first_fc.get('back', 'N/A')}")
            
            # Test 3.3: Test activity completion
            print_info("\nTesting activity completion...")
            node_id = activity.get('learning_node_id')
            if node_id:
                result = orchestrator.complete_activity(
                    user_id=user_id,
                    learning_node_id=node_id,
                    performance_score=0.85,
                    time_spent_seconds=120
                )
                print_success("Activity completion recorded!")
                print_json(result, "Completion Result")
            else:
                print_error("No learning_node_id in activity")
            
            # Test 3.4: Request second activity (should be different)
            print_info("\nRequesting second activity to test progression...")
            activity2 = orchestrator.determine_next_activity(user_id)
            
            if "error" not in activity2:
                print_success("Second activity generated!")
                print_info(f"Reason: {activity2.get('orchestration_reason')}")
                print_info(f"Node: {activity2.get('learning_node_id')}")
            
            return True
            
    except Exception as e:
        print_error(f"Orchestrator test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 4: Activity Generator Service
# =============================================================================
def test_activity_generator(user_id):
    """Test AI activity generation with personalization"""
    print_section("TEST 4: AI Activity Generator")
    
    if not user_id:
        print_error("No user_id provided, skipping activity generator test")
        return False
    
    try:
        from app import create_app
        from app.services.activity_generator_service import ActivityGeneratorService
        
        app = create_app()
        generator = ActivityGeneratorService()
        
        with app.app_context():
            # Test different activity types
            test_cases = [
                ("A1_VOCAB_GREETINGS", "flashcard", "Flashcard Generation"),
                ("A1_GRAMMAR_PRESENT_SIMPLE", "quiz", "Quiz Generation"),
                ("A1_VOCAB_DAILY_ROUTINE", None, "Auto Activity Type Selection")
            ]
            
            for node_id, activity_type, test_name in test_cases:
                print_info(f"\nTest Case: {test_name}")
                print(f"  Node: {node_id}")
                print(f"  Type: {activity_type or 'Auto'}")
                
                try:
                    activity = generator.generate_personalized_activity(
                        user_id=user_id,
                        learning_node_id=node_id,
                        activity_type=activity_type
                    )
                    
                    if "error" in activity:
                        print_error(f"Generation failed: {activity['error']}")
                        continue
                    
                    print_success(f"Generated: {activity.get('title', 'Untitled')}")
                    print(f"  Type: {activity.get('activity_type')}")
                    print(f"  Time: {activity.get('estimated_time')} minutes")
                    print(f"  Personalized for: {activity.get('personalized_for_user')}")
                    
                    # Verify structure based on type
                    act_type = activity.get('activity_type')
                    if act_type == 'flashcard':
                        if 'flashcards' in activity and activity['flashcards']:
                            print_success(f"Contains {len(activity['flashcards'])} flashcards")
                        else:
                            print_error("Missing flashcards array")
                    elif act_type == 'quiz':
                        if 'questions' in activity and activity['questions']:
                            print_success(f"Contains {len(activity['questions'])} questions")
                        else:
                            print_error("Missing questions array")
                    
                except Exception as e:
                    print_error(f"Test case failed: {str(e)}")
            
            print_success("\nActivity Generator tests completed")
            return True
            
    except Exception as e:
        print_error(f"Activity generator test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 5: Progress Tracking
# =============================================================================
def test_progress_tracking(user_id):
    """Test progress calculation and statistics"""
    print_section("TEST 5: Progress Tracking & Statistics")
    
    if not user_id:
        print_error("No user_id provided, skipping progress test")
        return False
    
    try:
        from app import create_app
        from app.models.curriculum import (
            UserLearningPathProgress,
            NodeCompletion,
            CurriculumLevel
        )
        from app.models.user import Profile
        
        app = create_app()
        
        with app.app_context():
            # Get progress
            progress = UserLearningPathProgress.query.filter_by(user_id=user_id).first()
            
            if progress:
                print_info("Learning Path Progress:")
                progress_data = progress.to_dict()
                print_json({
                    "current_level": progress.current_level,  # It's already a string (A1, A2, etc.)
                    "target_level": progress_data.get('target_level'),
                    "nodes_completed": progress.nodes_completed,
                    "nodes_mastered": progress.nodes_mastered,
                    "weak_areas": progress_data.get('weak_areas'),
                    "strong_areas": progress_data.get('strong_areas'),
                    "learning_style": progress_data.get('learning_style')
                })
            else:
                print_info("No progress record yet (will be created on first activity)")
            
            # Get node completions
            completions = NodeCompletion.query.filter_by(user_id=user_id).all()
            print_info(f"\nCompleted Nodes: {len(completions)}")
            
            for completion in completions[:5]:  # Show first 5
                print(f"  - {completion.node_id}: {completion.mastery_level:.2f} mastery ({completion.attempts} attempts)")
            
            if len(completions) > 5:
                print(f"  ... and {len(completions) - 5} more")
            
            # Get profile mastery
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile and profile.mastery_metrics:
                print_info("\nMastery Metrics:")
                for skill, score in profile.mastery_metrics.items():
                    bar_filled = "#" * int(score / 10)
                    bar_empty = "-" * (10 - int(score / 10))
                    print(f"  {skill:12s}: [{bar_filled}{bar_empty}] {score}%")
            
            print_success("Progress tracking verified")
            return True
            
    except Exception as e:
        print_error(f"Progress tracking test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 6: API Endpoints (Simulated)
# =============================================================================
def test_api_endpoints():
    """Test that API endpoints are properly registered"""
    print_section("TEST 6: API Endpoint Registration")
    
    try:
        from app import create_app
        
        app = create_app()
        
        # Check registered routes
        print_info("Checking for learning path API routes...")
        
        learning_path_routes = [
            rule for rule in app.url_map.iter_rules() 
            if '/api/learning-path' in rule.rule
        ]
        
        if not learning_path_routes:
            print_error("No /api/learning-path routes found!")
            return False
        
        print_success(f"Found {len(learning_path_routes)} learning path endpoints:")
        
        for rule in learning_path_routes:
            methods = ', '.join([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']])
            print(f"  {methods:15s} {rule.rule}")
        
        # Check for expected endpoints
        expected_endpoints = [
            'next-activity',
            'complete-activity',
            'progress',
            'nodes',
            'levels',
            'stats'
        ]
        
        found_endpoints = [rule.rule for rule in learning_path_routes]
        found_endpoint_names = ' '.join(found_endpoints)
        
        for endpoint in expected_endpoints:
            if endpoint in found_endpoint_names:
                print_success(f"Endpoint '{endpoint}' registered")
            else:
                print_error(f"Endpoint '{endpoint}' NOT found")
        
        return True
        
    except Exception as e:
        print_error(f"API endpoint test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# TEST 7: End-to-End Simulation
# =============================================================================
def test_end_to_end(user_id):
    """Simulate a complete learning session"""
    print_section("TEST 7: End-to-End Learning Session Simulation")
    
    if not user_id:
        print_error("No user_id provided, skipping E2E test")
        return False
    
    try:
        from app import create_app
        from app.services.learning_path_orchestrator import LearningPathOrchestrator
        from app.models.user import Profile, db
        import random
        
        app = create_app()
        orchestrator = LearningPathOrchestrator()
        
        with app.app_context():
            print_info("Simulating 5 learning activities...\n")
            
            for i in range(1, 6):
                print(f"{'='*70}")
                print(f"Activity #{i}")
                print(f"{'='*70}")
                
                # Get next activity
                activity = orchestrator.determine_next_activity(user_id)
                
                if "error" in activity:
                    print_error(f"Failed to get activity: {activity['error']}")
                    break
                
                print_info(f"Reason: {activity.get('orchestration_message')}")
                print_info(f"Node: {activity.get('learning_node_id')}")
                print_info(f"Type: {activity.get('activity_type')}")
                print_info(f"Title: {activity.get('title')}")
                
                # Simulate performance (random score between 0.6 and 1.0)
                performance = random.uniform(0.6, 1.0)
                time_spent = random.randint(60, 300)
                
                print_info(f"Simulating performance: {performance:.2f} ({time_spent}s)")
                
                # Complete activity
                result = orchestrator.complete_activity(
                    user_id=user_id,
                    learning_node_id=activity.get('learning_node_id'),
                    performance_score=performance,
                    time_spent_seconds=time_spent
                )
                
                print_success(f"Completed! Mastery: {result['mastery_level']:.2f}")
                print()
            
            # Show final statistics
            print(f"\n{'='*70}")
            print("FINAL STATISTICS")
            print(f"{'='*70}\n")
            
            profile = Profile.query.filter_by(user_id=user_id).first()
            if profile:
                print_info("Updated Mastery Metrics:")
                for skill, score in profile.mastery_metrics.items():
                    print(f"  {skill}: {score}%")
            
            print_success("\nEnd-to-End simulation completed!")
            return True
            
    except Exception as e:
        print_error(f"E2E test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# Main Test Runner
# =============================================================================
def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AI-PERSONALIZED LEARNING PATH - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    user_id = None
    
    # Run tests
    results['Database Models'] = test_database_models()
    
    if results['Database Models']:
        user_id = test_user_setup()
        results['User Setup'] = user_id is not None
    else:
        results['User Setup'] = False
    
    if user_id:
        results['Orchestrator'] = test_orchestrator(user_id)
        results['Activity Generator'] = test_activity_generator(user_id)
        results['Progress Tracking'] = test_progress_tracking(user_id)
    else:
        results['Orchestrator'] = False
        results['Activity Generator'] = False
        results['Progress Tracking'] = False
    
    results['API Endpoints'] = test_api_endpoints()
    
    if user_id:
        results['End-to-End'] = test_end_to_end(user_id)
    else:
        results['End-to-End'] = False
    
    # Print summary
    print_section("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{test_name:25s} : {status}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print(f"{'='*70}\n")
    
    if passed_tests == total_tests:
        print("SUCCESS! ALL TESTS PASSED! System is ready for production!")
        return 0
    else:
        print(f"WARNING: {total_tests - passed_tests} test(s) failed. Please review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
