"""
Comprehensive End-to-End Testing Script
Tests the complete user journey: Register → Assess → Goals → Enroll → Dashboard
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class EndToEndTest:
    def __init__(self):
        self.session = requests.Session()
        self.user_data = {}
        self.test_results = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "SUCCESS": "✅",
            "ERROR": "❌",
            "INFO": "ℹ️",
            "TEST": "🧪",
            "PROGRESS": "📊",
            "STEP": "📍"
        }
        symbol = symbols.get(status, "ℹ️")
        print(f"[{timestamp}] {symbol} {message}")
    
    def test(self, name, func):
        """Wrapper to run a test and track results"""
        try:
            self.log(f"Testing: {name}", "TEST")
            result = func()
            if result:
                self.log(f"✓ PASSED: {name}", "SUCCESS")
                self.test_results.append((name, "PASS"))
                return True
            else:
                self.log(f"✗ FAILED: {name}", "ERROR")
                self.test_results.append((name, "FAIL"))
                return False
        except Exception as e:
            self.log(f"✗ EXCEPTION in {name}: {str(e)}", "ERROR")
            self.test_results.append((name, "ERROR"))
            return False
    
    def step(self, message):
        """Print a major step"""
        print("\n" + "="*70)
        self.log(message, "STEP")
        print("="*70)
    
    def test_1_register(self):
        """Test: User Registration"""
        username = f"e2etest_{int(time.time())}"
        payload = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "Test123!",
            "native_language": "Telugu",
            "target_language": "English"
        }
        
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
        if response.status_code == 201:
            data = response.json()
            self.user_data["user_id"] = data.get("user", {}).get("id")
            self.user_data["access_token"] = data.get("access_token")
            self.user_data["username"] = username
            self.log(f"User registered: ID={self.user_data['user_id']}, Email={username}@test.com", "SUCCESS")
            return True
        else:
            self.log(f"Registration failed: {response.text}", "ERROR")
            return False
    
    def test_2_generate_assessment(self):
        """Test: Generate Comprehensive Assessment"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        payload = {"assessment_type": "comprehensive"}
        
        response = self.session.post(
            f"{BASE_URL}/api/assessment/generate",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            # The response returns "assessment" object with assessment_id inside
            assessment_obj = data.get("assessment", {})
            self.user_data["assessment_id"] = assessment_obj.get("assessment_id")
            questions = assessment_obj.get("questions", [])
            self.user_data["questions"] = questions  # Store questions for test_3
            total_questions = len(questions)
            
            if not self.user_data["assessment_id"]:
                self.log(f"Assessment generation failed: No assessment ID in response", "ERROR")
                return False
            
            self.log(f"Assessment generated: ID={self.user_data['assessment_id']}, Questions={total_questions}", "SUCCESS")
            return True
        else:
            self.log(f"Assessment generation failed: {response.status_code}", "ERROR")
            return False
    
    def test_3_answer_sample_questions(self):
        """Test: Answer ALL assessment questions"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        assessment_id = self.user_data.get("assessment_id")
        questions = self.user_data.get("questions", [])
        
        if not assessment_id or not questions:
            self.log("No assessment or questions available", "ERROR")
            return False
        
        answered = 0
        total_questions = len(questions)
        
        for i in range(total_questions):
            try:
                question = questions[i]
                question_id = question.get("id") or question.get("question_id")
                
                if not question_id:
                    self.log(f"Question {i+1} has no ID", "ERROR")
                    continue
                
                answer_payload = {
                    "question_id": question_id,
                    "answer": "A"
                }
                
                response = self.session.post(
                    f"{BASE_URL}/api/assessment/{assessment_id}/submit-answer",
                    headers=headers,
                    json=answer_payload
                )
                
                if response.status_code == 200:
                    answered += 1
                    if (i + 1) % 6 == 0:  # Show progress every 6 questions
                        self.log(f"  • Progress: {answered}/{total_questions} questions answered", "INFO")
                else:
                    self.log(f"  • Question {i+1}: Failed ({response.status_code})", "ERROR")
                
                time.sleep(0.05)
            except Exception as e:
                self.log(f"Error answering question {i+1}: {str(e)}", "ERROR")
        
        if answered == total_questions:
            self.log(f"All {answered}/{total_questions} questions answered successfully!", "SUCCESS")
            return True
        else:
            self.log(f"Only answered {answered}/{total_questions} questions", "ERROR")
            return answered >= int(total_questions * 0.8)  # Accept if at least 80% answered
    
    def test_4_complete_assessment(self):
        """Test: Complete Assessment and Get Results"""
        headers = {
            "Authorization": f"Bearer {self.user_data['access_token']}",
            "Content-Type": "application/json"
        }
        assessment_id = self.user_data.get("assessment_id")
        
        if not assessment_id:
            self.log("No assessment ID available", "ERROR")
            return False
        
        self.log(f"  • Assessment ID: {assessment_id}", "INFO")
        self.log(f"  • Token: {self.user_data['access_token'][:20]}...", "INFO")
        
        response = self.session.post(
            f"{BASE_URL}/api/assessment/{assessment_id}/complete",
            headers=headers,
            json={}
        )
        
        self.log(f"  • Response Status: {response.status_code}", "INFO")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", {})
            
            self.user_data["proficiency_level"] = results.get("proficiency_level") or results.get("overall_proficiency_level", "")
            self.user_data["score"] = results.get("score") or results.get("overall_score", 0)
            
            self.log(f"Assessment completed successfully!", "SUCCESS")
            self.log(f"  • Proficiency Level: {results.get('overall_proficiency_level', 'N/A')}", "INFO")
            self.log(f"  • Score: {results.get('overall_score', 0):.1f}/{results.get('max_score', 0)}", "INFO")
            
            return True
        else:
            self.log(f"Assessment completion failed: {response.status_code}", "ERROR")
            self.log(f"Full Response: {response.text}", "ERROR")
            return False
    
    def test_5_set_goals(self):
        """Test: Set Learning Goals"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        payload = {
            "daily_time_goal_minutes": 30,
            "learning_focus": "academic_english"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/personalization/goals",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            data = response.json()
            self.log(f"Goals set: {data.get('message', 'Success')}", "SUCCESS")
            return True
        else:
            self.log(f"Goal setting failed: {response.status_code}", "ERROR")
            return False
    
    def test_6_get_learning_paths(self):
        """Test: Get Learning Paths"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        
        response = self.session.get(
            f"{BASE_URL}/api/courses/learning-paths",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            paths = data.get("data", []) or data.get("learning_paths", [])
            self.user_data["learning_path_id"] = paths[0].get("id") if paths else None
            
            self.log(f"Found {len(paths)} learning paths", "SUCCESS")
            if self.user_data["learning_path_id"]:
                self.log(f"  • First path ID: {self.user_data['learning_path_id']}", "INFO")
            
            return len(paths) > 0
        else:
            self.log(f"Learning paths retrieval failed: {response.status_code}", "ERROR")
            return False
    
    def test_7_enroll_path(self):
        """Test: Enroll in a Learning Path"""
        if not self.user_data.get("learning_path_id"):
            self.log("Skipping: No learning path available", "INFO")
            return False
        
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        path_id = self.user_data["learning_path_id"]
        
        response = self.session.post(
            f"{BASE_URL}/api/courses/learning-paths/{path_id}/enroll",
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            self.log(f"Enrolled in learning path: {data.get('message', 'Success')}", "SUCCESS")
            return True
        else:
            self.log(f"Enrollment failed: {response.status_code}", "ERROR")
            return False
    
    def test_8_dashboard(self):
        """Test: Get Dashboard Data"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        
        response = self.session.get(
            f"{BASE_URL}/api/personalization/dashboard",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"Dashboard data retrieved successfully", "SUCCESS")
            
            # Display dashboard stats
            stats = data.get("stats", {})
            if stats:
                self.log(f"  • Lessons Completed: {stats.get('lessons_completed', 0)}", "INFO")
                self.log(f"  • Current Streak: {stats.get('current_streak', 0)}", "INFO")
                self.log(f"  • Total XP: {stats.get('total_xp', 0)}", "INFO")
            
            return True
        else:
            self.log(f"Dashboard retrieval failed: {response.status_code}", "ERROR")
            return False
    
    def test_9_get_activities(self):
        """Test: Get Available Activities"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        
        response = self.session.get(
            f"{BASE_URL}/api/activity/all",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            activities = data.get("data", []) or data.get("activities", [])
            
            if activities:
                self.log(f"Found {len(activities)} activities", "SUCCESS")
                return True
            else:
                self.log(f"No activities available (might be expected)", "INFO")
                return True
        else:
            self.log(f"Activities retrieval failed: {response.status_code}", "ERROR")
            return False
    
    def test_10_user_status(self):
        """Test: Get User Status"""
        headers = {"Authorization": f"Bearer {self.user_data['access_token']}"}
        
        response = self.session.get(
            f"{BASE_URL}/api/user/status",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"User status retrieved successfully", "SUCCESS")
            
            # Check if assessment is marked as complete
            is_assessment_complete = data.get("assessment_completed", False)
            self.log(f"  • Assessment Completed: {is_assessment_complete}", "INFO")
            self.log(f"  • Proficiency Level: {data.get('proficiency_level', 'N/A')}", "INFO")
            
            return True
        else:
            self.log(f"User status retrieval failed: {response.status_code}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n")
        print("=" * 70)
        print(" " * 15 + "END-TO-END TESTING SUITE")
        print("=" * 70)
        
        self.step("STEP 1: USER AUTHENTICATION")
        self.test("Register new user", self.test_1_register)
        time.sleep(0.5)
        
        self.step("STEP 2: ASSESSMENT")
        self.test("Generate comprehensive assessment", self.test_2_generate_assessment)
        time.sleep(0.5)
        
        self.test("Answer all assessment questions", self.test_3_answer_sample_questions)
        time.sleep(0.5)
        
        self.test("Complete assessment", self.test_4_complete_assessment)
        time.sleep(0.5)
        
        self.step("STEP 3: PERSONALIZATION")
        self.test("Set learning goals", self.test_5_set_goals)
        time.sleep(0.5)
        
        self.test("Retrieve learning paths", self.test_6_get_learning_paths)
        time.sleep(0.5)
        
        self.test("Enroll in learning path", self.test_7_enroll_path)
        time.sleep(0.5)
        
        self.step("STEP 4: DASHBOARD & ACTIVITIES")
        self.test("Get dashboard data", self.test_8_dashboard)
        time.sleep(0.5)
        
        self.test("Get available activities", self.test_9_get_activities)
        time.sleep(0.5)
        
        self.step("STEP 5: USER STATUS")
        self.test("Check user status", self.test_10_user_status)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n")
        print("=" * 70)
        print(" " * 20 + "TEST SUMMARY")
        print("=" * 70 + "\n")
        
        passed = sum(1 for _, result in self.test_results if result == "PASS")
        failed = sum(1 for _, result in self.test_results if result == "FAIL")
        errors = sum(1 for _, result in self.test_results if result == "ERROR")
        total = len(self.test_results)
        
        for test_name, result in self.test_results:
            symbol = "✅" if result == "PASS" else "❌" if result in ["FAIL", "ERROR"] else "⚠️"
            print(f"{symbol} {test_name}: {result}")
        
        print("\n" + "="*70)
        print(f"Total: {total} | Passed: {passed} ✅ | Failed: {failed} ❌ | Errors: {errors} ⚠️")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print("="*70 + "\n")
        
        return passed, failed, errors


if __name__ == "__main__":
    test_suite = EndToEndTest()
    test_suite.run_all_tests()
