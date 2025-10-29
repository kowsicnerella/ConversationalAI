"""
Automated Testing - Remaining Features
Tests: Goals, Assessment Response/Complete, Activities, Chat, Gamification
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"

class TestSession:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.username = None
        self.assessment_id = None
        self.learning_path_id = None
        self.enrollment_id = None
        
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
        
    def print_step(self, step_num, description):
        print(f"\nStep {step_num}: {description}")
        print("-" * 70)
        
    def print_result(self, success, message, data=None):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {message}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)[:500]}")
    
    def register_user(self):
        """Register a new test user"""
        self.print_step(1, "Registering new user")
        
        username = f"featuretest_{int(datetime.now().timestamp())}"
        self.username = username
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": username,
                    "email": f"{username}@test.com",
                    "password": "Test123!",
                    "native_language": "Telugu",
                    "target_language": "English"
                },
                timeout=10
            )
        except requests.exceptions.Timeout:
            self.print_result(False, "Request timeout - backend not responding", None)
            return False
        except Exception as e:
            self.print_result(False, f"Connection error: {str(e)}", None)
            return False
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get('access_token')
            self.user_id = data.get('user', {}).get('id')
            self.print_result(True, f"User registered: {username}", {"user_id": self.user_id})
            return True
        else:
            self.print_result(False, f"Registration failed: {response.status_code}", response.json())
            return False
    
    def login_user(self):
        """Login with test user"""
        self.print_step(2, "Logging in")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": self.username,
                    "password": "Test123!"
                },
                timeout=10
            )
        except Exception as e:
            self.print_result(False, f"Login request error: {str(e)}", None)
            return False
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.print_result(True, "Login successful", {"token_length": len(self.access_token)})
            return True
        else:
            self.print_result(False, f"Login failed: {response.status_code}", response.json())
            return False
    
    def get_headers(self):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    # ============================================================
    # TEST 1: GOAL SETTING
    # ============================================================
    
    def test_goal_setting(self):
        """Test setting user goals"""
        self.print_header("TEST 1: GOAL SETTING ENDPOINT")
        
        self.print_step("1.1", "Setting daily learning goals")
        
        response = requests.post(
            f"{BASE_URL}/personalization/goals",
            headers=self.get_headers(),
            json={
                "daily_time_goal": 20,
                "learning_focus": "conversation"
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            self.print_result(True, "Goal setting successful", data.get('goal'))
            return True
        else:
            self.print_result(False, f"Goal setting failed: {response.status_code}", response.json())
            return False
    
    # ============================================================
    # TEST 2: ASSESSMENT FLOW (RESPOND + COMPLETE)
    # ============================================================
    
    def test_assessment_flow(self):
        """Test assessment response and completion"""
        self.print_header("TEST 2: ASSESSMENT RESPONSE & COMPLETION")
        
        # Start assessment first
        self.print_step("2.1", "Starting assessment")
        response = requests.post(
            f"{BASE_URL}/personalization/assessment/start",
            headers=self.get_headers()
        )
        
        if response.status_code != 201:
            self.print_result(False, f"Assessment start failed: {response.status_code}", response.json())
            return False
        
        data = response.json()
        # Try to get assessment data from different possible locations
        assessment = data.get('assessment', {})
        self.assessment_id = assessment.get('assessment_id') or data.get('assessment_id')
        questions = assessment.get('questions', []) or data.get('questions', [])
        
        print(f"DEBUG: Full response = {json.dumps(data, indent=2)[:500]}")
        
        self.print_result(True, f"Assessment started (ID: {self.assessment_id})", 
                         {"question_count": len(questions), "has_assessment_key": 'assessment' in data})
        
        if not questions:
            self.print_result(False, "No questions in assessment response", None)
            return False
        
        # Respond to each question
        self.print_step("2.2", "Responding to assessment questions")
        
        responses = [
            "My name is Ram and I am a software developer from Hyderabad.",
            "I usually wake up at 6 AM, go to work, and come back home in the evening.",
            "I want to improve my English speaking skills to communicate better at work."
        ]
        
        for idx, question in enumerate(questions):
            question_id = question.get('id') or question.get('question_id')
            if not question_id:
                print(f"⚠️  Question {idx+1} has no ID, skipping")
                continue
                
            response = requests.post(
                f"{BASE_URL}/personalization/assessment/{self.assessment_id}/respond",
                headers=self.get_headers(),
                json={
                    "question_id": question_id,
                    "user_response": responses[idx] if idx < len(responses) else "Yes, I understand."
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Question {idx+1} answered successfully")
            else:
                print(f"❌ Question {idx+1} failed: {response.status_code}")
                print(f"   Response: {response.json()}")
        
        # Complete assessment
        self.print_step("2.3", "Completing assessment")
        response = requests.post(
            f"{BASE_URL}/personalization/assessment/{self.assessment_id}/complete",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                self.print_result(True, "Assessment completed", data.get('results'))
                return True
            except:
                self.print_result(True, "Assessment completed (no JSON response)", 
                                {"status": response.status_code, "text": response.text[:200]})
                return True
        elif response.status_code == 404:
            self.print_result(False, "Assessment completion endpoint not found (404)", 
                            {"assessment_id": self.assessment_id})
            return False
        else:
            try:
                error_data = response.json()
            except:
                error_data = {"text": response.text[:200]}
            self.print_result(False, f"Assessment completion failed: {response.status_code}", 
                            error_data)
            return False
    
    # ============================================================
    # TEST 3: ACTIVITIES
    # ============================================================
    
    def test_activities(self):
        """Test activities endpoint"""
        self.print_header("TEST 3: ACTIVITIES SYSTEM")
        
        # First enroll in a learning path
        self.print_step("3.1", "Enrolling in learning path")
        
        # Get learning paths
        response = requests.get(
            f"{BASE_URL}/courses/learning-paths",
            headers=self.get_headers()
        )
        
        if response.status_code != 200:
            self.print_result(False, "Failed to get learning paths", response.json())
            return False
        
        paths = response.json().get('learning_paths', [])
        if not paths:
            self.print_result(False, "No learning paths available", None)
            return False
        
        self.learning_path_id = paths[0]['id']
        
        # Enroll
        response = requests.post(
            f"{BASE_URL}/courses/learning-paths/{self.learning_path_id}/enroll",
            headers=self.get_headers()
        )
        
        if response.status_code != 201:
            self.print_result(False, "Enrollment failed", response.json())
            return False
        
        self.print_result(True, f"Enrolled in path {self.learning_path_id}", None)
        
        # Get activities
        self.print_step("3.2", "Getting activities list")
        
        response = requests.get(
            f"{BASE_URL}/activity/all",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get('activities', [])
            if activities:
                self.print_result(True, f"Activities retrieved: {len(activities)} found", 
                                {"first_activity": activities[0] if activities else None})
                return True
            else:
                self.print_result(False, "Activities list is EMPTY", 
                                {"message": "No activities generated after enrollment"})
                return False
        else:
            self.print_result(False, f"Activities endpoint failed: {response.status_code}", 
                            response.json())
            return False
    
    # ============================================================
    # TEST 4: CHAT ENDPOINT
    # ============================================================
    
    def test_chat(self):
        """Test chat endpoint"""
        self.print_header("TEST 4: CHAT/AI TUTOR ENDPOINT")
        
        self.print_step("4.1", "Sending message to AI tutor")
        
        response = requests.post(
            f"{BASE_URL}/chat/quick-chat",
            headers=self.get_headers(),
            json={
                "message": "Hello! Can you help me learn basic English greetings?",
                "context": "learning_assistance"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data.get('response', '')
            self.print_result(True, "Chat endpoint working", 
                            {"response_preview": ai_response[:200]})
            return True
        else:
            self.print_result(False, f"Chat endpoint failed: {response.status_code}", 
                            response.json())
            return False
    
    # ============================================================
    # TEST 5: GAMIFICATION
    # ============================================================
    
    def test_gamification(self):
        """Test gamification endpoints"""
        self.print_header("TEST 5: GAMIFICATION SYSTEM")
        
        # Test points
        self.print_step("5.1", "Getting user points")
        response = requests.get(
            f"{BASE_URL}/gamification/points",
            headers=self.get_headers()
        )
        
        points_success = False
        if response.status_code == 200:
            data = response.json()
            self.print_result(True, "Points retrieved", data)
            points_success = True
        else:
            self.print_result(False, f"Points endpoint failed: {response.status_code}", 
                            response.json())
        
        # Test badges
        self.print_step("5.2", "Getting user badges")
        response = requests.get(
            f"{BASE_URL}/gamification/badges",
            headers=self.get_headers()
        )
        
        badges_success = False
        if response.status_code == 200:
            data = response.json()
            self.print_result(True, "Badges retrieved", data)
            badges_success = True
        else:
            self.print_result(False, f"Badges endpoint failed: {response.status_code}", 
                            response.json())
        
        # Test leaderboard
        self.print_step("5.3", "Getting leaderboard")
        response = requests.get(
            f"{BASE_URL}/gamification/leaderboard",
            headers=self.get_headers()
        )
        
        leaderboard_success = False
        if response.status_code == 200:
            data = response.json()
            self.print_result(True, "Leaderboard retrieved", data)
            leaderboard_success = True
        else:
            self.print_result(False, f"Leaderboard endpoint failed: {response.status_code}", 
                            response.json())
        
        return points_success and badges_success and leaderboard_success


def main():
    print("="*70)
    print("  LANGUAGE LEARNING PLATFORM - REMAINING FEATURES TEST")
    print("="*70)
    print(f"Backend: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    session = TestSession()
    results = {}
    
    # Setup: Register and login
    if not session.register_user():
        print("\n❌ CRITICAL: User registration failed. Cannot continue.")
        return
    
    if not session.login_user():
        print("\n❌ CRITICAL: User login failed. Cannot continue.")
        return
    
    print("\n✅ Setup complete. Starting feature tests...\n")
    
    # Run tests
    results['goal_setting'] = session.test_goal_setting()
    results['assessment_flow'] = session.test_assessment_flow()
    results['activities'] = session.test_activities()
    results['chat'] = session.test_chat()
    results['gamification'] = session.test_gamification()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name.replace('_', ' ').title()}")
    
    print("-"*70)
    print(f"Total: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    elif passed >= total * 0.7:
        print(f"\n⚠️  Most tests passed. {total - passed} issue(s) need attention.")
    else:
        print(f"\n❌ Multiple failures detected. {total - passed} tests failed.")
    
    return results


if __name__ == "__main__":
    main()
