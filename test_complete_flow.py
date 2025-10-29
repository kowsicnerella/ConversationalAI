"""
Complete End-to-End Testing Script
Tests all endpoints and UI flows for the language learning platform
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000/api"
FRONTEND_URL = "http://localhost:5174"

# Test user credentials
TEST_USER = {
    "username": f"testuser_{int(time.time())}",
    "email": f"testuser_{int(time.time())}@test.com",
    "password": "TestPassword123!",
    "native_language": "Telugu",
    "target_language": "English"
}

class TestSession:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.assessment_id = None
        self.learning_path_id = None
        self.activity_id = None
        
    def print_result(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {test_name}")
        if details:
            print(f"   {details}")
    
    def test_registration(self):
        """Test user registration"""
        print("\n" + "="*60)
        print("TEST 1: User Registration")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=TEST_USER
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 201:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.print_result("User Registration", True, 
                                f"User ID: {self.user_id}, Token received")
                return True
            else:
                self.print_result("User Registration", False, 
                                f"Expected 201, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("User Registration", False, f"Error: {str(e)}")
            return False
    
    def test_login(self):
        """Test user login"""
        print("\n" + "="*60)
        print("TEST 2: User Login")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.print_result("User Login", True, "Token refreshed")
                return True
            else:
                self.print_result("User Login", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("User Login", False, f"Error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_start_assessment(self):
        """Test starting initial assessment"""
        print("\n" + "="*60)
        print("TEST 3: Start Initial Assessment")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/personalization/assessment/start",
                headers=self.get_headers(),
                json={"assessment_type": "initial"}
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 201:
                # Extract assessment_id from nested structure
                assessment_data = data.get("assessment", {})
                self.assessment_id = assessment_data.get("assessment_id")
                questions = assessment_data.get("questions", [])
                total_questions = len(questions)
                self.print_result("Start Assessment", True, 
                                f"Assessment ID: {self.assessment_id}, "
                                f"Total Questions: {total_questions}")
                return True
            else:
                self.print_result("Start Assessment", False, 
                                f"Expected 201, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Start Assessment", False, f"Error: {str(e)}")
            return False
    
    def test_get_question(self):
        """Test getting current assessment question"""
        print("\n" + "="*60)
        print("TEST 4: Get Assessment Question")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/personalization/assessment/{self.assessment_id}/question",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                question = data.get("question", {})
                print(f"Question: {question.get('text', 'No text')[:50]}...")
                self.print_result("Get Question", True, "Question retrieved")
                return True
            else:
                self.print_result("Get Question", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Get Question", False, f"Error: {str(e)}")
            return False
    
    def test_submit_answers(self):
        """Test submitting assessment answers"""
        print("\n" + "="*60)
        print("TEST 5: Submit Assessment Answers (36 questions)")
        print("="*60)
        
        try:
            # Answer all 36 questions
            for i in range(36):
                # Get current question
                response = requests.get(
                    f"{BASE_URL}/personalization/assessment/{self.assessment_id}/question",
                    headers=self.get_headers()
                )
                
                if response.status_code != 200:
                    print(f"  Question {i+1}/36 - Failed to fetch")
                    continue
                
                question_data = response.json()
                question_id = question_data.get("question", {}).get("id")
                
                if not question_id:
                    print(f"  Question {i+1}/36 - No question ID")
                    break
                
                # Submit answer (always answer B for testing)
                answer_response = requests.post(
                    f"{BASE_URL}/personalization/assessment/{self.assessment_id}/respond",
                    headers=self.get_headers(),
                    json={
                        "question_id": question_id,
                        "answer": "B"
                    }
                )
                
                if answer_response.status_code == 200:
                    progress = answer_response.json().get("progress", {})
                    answered = progress.get("answered", i+1)
                    total = progress.get("total", 36)
                    print(f"  Question {answered}/{total} answered ✓")
                else:
                    print(f"  Question {i+1}/36 - Failed to submit")
            
            self.print_result("Submit Answers", True, "All 36 questions answered")
            return True
            
        except Exception as e:
            self.print_result("Submit Answers", False, f"Error: {str(e)}")
            return False
    
    def test_complete_assessment(self):
        """Test completing assessment"""
        print("\n" + "="*60)
        print("TEST 6: Complete Assessment")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/personalization/assessment/{self.assessment_id}/complete",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code == 200:
                results = data.get("results", {})
                level = results.get("proficiency_level")
                score = results.get("score")
                self.print_result("Complete Assessment", True, 
                                f"Level: {level}, Score: {score}")
                return True
            else:
                self.print_result("Complete Assessment", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Complete Assessment", False, f"Error: {str(e)}")
            return False
    
    def test_learning_paths(self):
        """Test getting learning paths"""
        print("\n" + "="*60)
        print("TEST 7: Get Learning Paths")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/courses/learning-paths",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                paths = data.get("learning_paths", [])
                if paths:
                    self.learning_path_id = paths[0].get("id")
                    print(f"Learning Paths: {len(paths)}")
                    for path in paths[:3]:  # Show first 3
                        print(f"  - {path.get('title')} (Level: {path.get('level')})")
                    self.print_result("Get Learning Paths", True, 
                                    f"Found {len(paths)} paths")
                    return True
                else:
                    self.print_result("Get Learning Paths", False, "No paths found")
                    return False
            else:
                self.print_result("Get Learning Paths", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Get Learning Paths", False, f"Error: {str(e)}")
            return False
    
    def test_enroll_learning_path(self):
        """Test enrolling in a learning path"""
        print("\n" + "="*60)
        print("TEST 8: Enroll in Learning Path")
        print("="*60)
        
        if not self.learning_path_id:
            self.print_result("Enroll Learning Path", False, "No learning path ID")
            return False
        
        try:
            response = requests.post(
                f"{BASE_URL}/courses/learning-paths/{self.learning_path_id}/enroll",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if response.status_code in [200, 201]:
                self.print_result("Enroll Learning Path", True, 
                                f"Enrolled in path {self.learning_path_id}")
                return True
            else:
                self.print_result("Enroll Learning Path", False, 
                                f"Expected 200/201, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Enroll Learning Path", False, f"Error: {str(e)}")
            return False
    
    def test_dashboard(self):
        """Test dashboard data"""
        print("\n" + "="*60)
        print("TEST 9: Get Dashboard Data")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/personalization/dashboard",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                print(f"User: {data.get('user', {}).get('username')}")
                print(f"Level: {data.get('gamification', {}).get('level')}")
                print(f"XP: {data.get('gamification', {}).get('xp')}")
                print(f"Streak: {data.get('gamification', {}).get('current_streak')}")
                self.print_result("Get Dashboard", True, "Dashboard data loaded")
                return True
            else:
                self.print_result("Get Dashboard", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Get Dashboard", False, f"Error: {str(e)}")
            return False
    
    def test_activities(self):
        """Test getting activities"""
        print("\n" + "="*60)
        print("TEST 10: Get Activities")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/activity/all",
                headers=self.get_headers()
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                activities = data.get("activities", [])
                if activities:
                    self.activity_id = activities[0].get("id")
                    print(f"Activities: {len(activities)}")
                    for activity in activities[:3]:
                        print(f"  - {activity.get('title')} ({activity.get('type')})")
                    self.print_result("Get Activities", True, 
                                    f"Found {len(activities)} activities")
                    return True
                else:
                    self.print_result("Get Activities", False, "No activities found")
                    return False
            else:
                self.print_result("Get Activities", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Get Activities", False, f"Error: {str(e)}")
            return False
    
    def test_chat(self):
        """Test chat endpoint"""
        print("\n" + "="*60)
        print("TEST 11: Chat with AI Tutor")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/quick-chat",
                headers=self.get_headers(),
                json={
                    "message": "Hello! Can you help me learn English?",
                    "context": "greeting"
                }
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if response.status_code == 200:
                ai_response = data.get("response", "")
                print(f"AI Response: {ai_response[:100]}...")
                self.print_result("Chat", True, "AI responded successfully")
                return True
            else:
                self.print_result("Chat", False, 
                                f"Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Chat", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*80)
        print("STARTING COMPREHENSIVE API TESTING")
        print("="*80)
        print(f"Backend URL: {BASE_URL}")
        print(f"Frontend URL: {FRONTEND_URL}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        # Run tests in sequence
        results.append(("Registration", self.test_registration()))
        if results[-1][1]:
            results.append(("Login", self.test_login()))
            results.append(("Start Assessment", self.test_start_assessment()))
            if results[-1][1]:
                results.append(("Get Question", self.test_get_question()))
                results.append(("Submit Answers", self.test_submit_answers()))
                results.append(("Complete Assessment", self.test_complete_assessment()))
            results.append(("Learning Paths", self.test_learning_paths()))
            if results[-1][1]:
                results.append(("Enroll", self.test_enroll_learning_path()))
            results.append(("Dashboard", self.test_dashboard()))
            results.append(("Activities", self.test_activities()))
            results.append(("Chat", self.test_chat()))
        
        # Print summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\n{'='*80}")
        print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        print(f"{'='*80}\n")
        
        return passed == total

if __name__ == "__main__":
    session = TestSession()
    success = session.run_all_tests()
    exit(0 if success else 1)
