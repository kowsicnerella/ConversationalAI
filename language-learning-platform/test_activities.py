"""
Activity System Testing Script
Tests quiz generation, flashcard generation, submission, and evaluation
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "Test123!"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(test_name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")
    
    test_results["tests"].append({
        "name": test_name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def login_user():
    """Login and get access token"""
    print("\n🔐 Logging in...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            log_test("User Login", True, f"Token received: {token[:20]}...")
            return token
        else:
            log_test("User Login", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("User Login", False, str(e))
        return None

def test_generate_quiz(token):
    """Test quiz generation"""
    print("\n📝 Testing Quiz Generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Basic quiz generation
    try:
        response = requests.post(
            f"{BASE_URL}/activities/generate-quiz",
            headers=headers,
            json={
                "topic": "daily routine",
                "level": "beginner",
                "num_questions": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                quiz_data = data['data']
                
                # Validate quiz structure
                has_title = 'quiz_title' in quiz_data
                has_questions = 'questions' in quiz_data and len(quiz_data['questions']) == 5
                has_session_id = 'session_id' in quiz_data
                
                if has_title and has_questions and has_session_id:
                    log_test("Generate Quiz - Basic", True, 
                            f"Generated {len(quiz_data['questions'])} questions, Session ID: {quiz_data['session_id']}")
                    return quiz_data
                else:
                    log_test("Generate Quiz - Basic", False, 
                            f"Missing fields: title={has_title}, questions={has_questions}, session_id={has_session_id}")
                    return None
            else:
                log_test("Generate Quiz - Basic", False, "Invalid response structure")
                return None
        else:
            log_test("Generate Quiz - Basic", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Generate Quiz - Basic", False, str(e))
        return None

def test_submit_quiz(token, quiz_data):
    """Test quiz submission and evaluation"""
    print("\n✍️ Testing Quiz Submission...")
    
    if not quiz_data:
        log_test("Submit Quiz", False, "No quiz data available")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create user answers (answer all questions correctly for first test)
    user_answers = {}
    for question in quiz_data['questions']:
        user_answers[str(question['question_id'])] = question['correct_answer']
    
    try:
        response = requests.post(
            f"{BASE_URL}/activities/submit",
            headers=headers,
            json={
                "session_id": quiz_data['session_id'],
                "activity_type": "quiz",
                "activity_data": quiz_data,
                "user_answers": user_answers,
                "time_spent_minutes": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'evaluation' in data:
                evaluation = data['evaluation']
                
                # Validate evaluation structure
                has_score = 'score_percentage' in evaluation
                has_points = 'points_earned' in evaluation
                has_feedback = 'detailed_feedback' in evaluation
                
                score = evaluation.get('score_percentage', 0)
                points = evaluation.get('points_earned', 0)
                
                if has_score and has_points and has_feedback:
                    log_test("Submit Quiz - All Correct", True, 
                            f"Score: {score}%, Points: {points}, Feedback items: {len(evaluation['detailed_feedback'])}")
                    return evaluation
                else:
                    log_test("Submit Quiz - All Correct", False, "Missing evaluation fields")
                    return None
            else:
                log_test("Submit Quiz - All Correct", False, "Invalid response structure")
                return None
        else:
            log_test("Submit Quiz - All Correct", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Submit Quiz - All Correct", False, str(e))
        return None

def test_generate_flashcards(token):
    """Test flashcard generation"""
    print("\n🎴 Testing Flashcard Generation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/activities/generate-flashcards",
            headers=headers,
            json={
                "topic": "food",
                "level": "beginner",
                "num_cards": 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                flashcard_data = data['data']
                
                # Validate flashcard structure
                has_title = 'title' in flashcard_data
                has_cards = 'flashcards' in flashcard_data and len(flashcard_data['flashcards']) == 10
                has_session_id = 'session_id' in flashcard_data
                
                if has_title and has_cards and has_session_id:
                    log_test("Generate Flashcards - Basic", True, 
                            f"Generated {len(flashcard_data['flashcards'])} cards, Session ID: {flashcard_data['session_id']}")
                    return flashcard_data
                else:
                    log_test("Generate Flashcards - Basic", False, 
                            f"Missing fields: title={has_title}, cards={has_cards}, session_id={has_session_id}")
                    return None
            else:
                log_test("Generate Flashcards - Basic", False, "Invalid response structure")
                return None
        else:
            log_test("Generate Flashcards - Basic", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Generate Flashcards - Basic", False, str(e))
        return None

def test_submit_flashcards(token, flashcard_data):
    """Test flashcard submission"""
    print("\n💾 Testing Flashcard Submission...")
    
    if not flashcard_data:
        log_test("Submit Flashcards", False, "No flashcard data available")
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create user responses (mark half as known, half as practice)
    responses = []
    for i, card in enumerate(flashcard_data['flashcards']):
        responses.append({
            "card_id": card['id'],
            "marked_as_known": i % 2 == 0,  # Alternate between known and practice
            "reviewed_at": datetime.utcnow().isoformat()
        })
    
    try:
        response = requests.post(
            f"{BASE_URL}/activities/submit",
            headers=headers,
            json={
                "session_id": flashcard_data['session_id'],
                "activity_type": "flashcard",
                "activity_data": flashcard_data,
                "user_answers": {
                    "responses": responses
                },
                "time_spent_minutes": 3
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'evaluation' in data:
                evaluation = data['evaluation']
                
                # Validate evaluation
                has_total = 'total_cards' in evaluation
                has_known = 'cards_known' in evaluation
                has_points = 'points_earned' in evaluation
                
                total = evaluation.get('total_cards', 0)
                known = evaluation.get('cards_known', 0)
                points = evaluation.get('points_earned', 0)
                
                if has_total and has_known and has_points:
                    log_test("Submit Flashcards", True, 
                            f"Total: {total}, Known: {known}, Points: {points}")
                    return evaluation
                else:
                    log_test("Submit Flashcards", False, "Missing evaluation fields")
                    return None
            else:
                log_test("Submit Flashcards", False, "Invalid response structure")
                return None
        else:
            log_test("Submit Flashcards", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        log_test("Submit Flashcards", False, str(e))
        return None

def test_get_topics(token):
    """Test getting available topics"""
    print("\n📚 Testing Get Topics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/activities/topics",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'topics' in data:
                topics = data['topics']
                log_test("Get Available Topics", True, f"Found {len(topics)} topics")
                return topics
            else:
                log_test("Get Available Topics", False, "Invalid response structure")
                return None
        else:
            log_test("Get Available Topics", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Available Topics", False, str(e))
        return None

def test_get_history(token):
    """Test getting activity history"""
    print("\n📊 Testing Get Activity History...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/activities/history",
            headers=headers,
            params={"limit": 10}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'history' in data:
                history = data['history']
                log_test("Get Activity History", True, f"Found {len(history)} completed activities")
                return history
            else:
                log_test("Get Activity History", False, "Invalid response structure")
                return None
        else:
            log_test("Get Activity History", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        log_test("Get Activity History", False, str(e))
        return None

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"📝 Total: {len(test_results['tests'])}")
    
    success_rate = (test_results['passed'] / len(test_results['tests']) * 100) if test_results['tests'] else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if test_results['failed'] > 0:
        print("\n❌ Failed Tests:")
        for test in test_results['tests']:
            if not test['passed']:
                print(f"   - {test['name']}: {test['message']}")
    
    print("="*60)

def main():
    """Main test execution"""
    print("="*60)
    print("🧪 ACTIVITY SYSTEM TESTING")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print("="*60)
    
    # Step 1: Login
    token = login_user()
    if not token:
        print("\n❌ Cannot proceed without valid token")
        print_summary()
        return
    
    # Step 2: Test quiz generation
    quiz_data = test_generate_quiz(token)
    
    # Step 3: Test quiz submission
    if quiz_data:
        test_submit_quiz(token, quiz_data)
    
    # Step 4: Test flashcard generation
    flashcard_data = test_generate_flashcards(token)
    
    # Step 5: Test flashcard submission
    if flashcard_data:
        test_submit_flashcards(token, flashcard_data)
    
    # Step 6: Test get topics
    test_get_topics(token)
    
    # Step 7: Test get history
    test_get_history(token)
    
    # Print summary
    print_summary()

if __name__ == "__main__":
    main()
