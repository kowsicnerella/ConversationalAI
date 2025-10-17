"""
Comprehensive Application Testing Suite
Tests all user flows, activity generation, and personalized learning experiences
"""

import sys
import json
import traceback
from datetime import datetime
from app import create_app
from app.models import (
    db,
    User,
    Profile,
    Activity,
    UserActivityLog,
    Chapter,
    UserGoal,
    Badge,
    LearningPath,
)


class ComprehensiveTestSuite:
    def __init__(self):
        self.app = create_app("development")
        self.client = self.app.test_client()
        self.test_results = {"total_tests": 0, "passed": 0, "failed": 0, "errors": []}
        self.auth_token = None
        self.test_user_id = None

    def log_test(self, test_name, status, message=""):
        """Log test results"""
        self.test_results["total_tests"] += 1
        if status == "PASS":
            self.test_results["passed"] += 1
            print(f"✓ {test_name}: PASSED {message}")
        else:
            self.test_results["failed"] += 1
            error_msg = f"{test_name}: {message}"
            self.test_results["errors"].append(error_msg)
            print(f"✗ {test_name}: FAILED - {message}")

    def print_section(self, title):
        """Print section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")

    # ========== DATABASE TESTS ==========
    def test_database_connection(self):
        """Test database connectivity"""
        self.print_section("DATABASE CONNECTION TESTS")
        try:
            with self.app.app_context():
                # Test connection
                result = db.session.execute(db.text("SELECT 1")).scalar()
                self.log_test("Database Connection", "PASS", "- Connection successful")

                # Test models
                user_count = User.query.count()
                self.log_test("User Model", "PASS", f"- Found {user_count} users")

                chapter_count = Chapter.query.count()
                self.log_test(
                    "Chapter Model", "PASS", f"- Found {chapter_count} chapters"
                )

                return True
        except Exception as e:
            self.log_test("Database Connection", "FAIL", str(e))
            return False

    # ========== AUTHENTICATION TESTS ==========
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        self.print_section("AUTHENTICATION FLOW TESTS")

        # Test 1: User Registration
        try:
            register_data = {
                "username": f"testuser_{datetime.now().timestamp()}",
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "TestPassword123!",
            }

            response = self.client.post(
                "/api/auth/register",
                json=register_data,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test(
                    "User Registration", "PASS", f"- User created successfully"
                )
                self.test_username = register_data["username"]
            else:
                self.log_test(
                    "User Registration",
                    "FAIL",
                    f"Status: {response.status_code}, Response: {response.get_json()}",
                )
                return False
        except Exception as e:
            self.log_test("User Registration", "FAIL", str(e))
            return False

        # Test 2: User Login
        try:
            login_data = {
                "username": self.test_username,
                "password": "TestPassword123!",
            }

            response = self.client.post(
                "/api/auth/login", json=login_data, content_type="application/json"
            )

            if response.status_code == 200:
                data = response.get_json()
                self.auth_token = data.get("access_token")
                self.test_user_id = data.get("user", {}).get("id")
                self.log_test(
                    "User Login",
                    "PASS",
                    f"- Token received, User ID: {self.test_user_id}",
                )
            else:
                self.log_test("User Login", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Login", "FAIL", str(e))
            return False

        return True

    # ========== ONBOARDING TESTS ==========
    def test_onboarding_flow(self):
        """Test complete onboarding flow"""
        self.print_section("ONBOARDING FLOW TESTS")

        if not self.auth_token:
            self.log_test("Onboarding Flow", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Get Initial Assessment
        try:
            response = self.client.get("/api/onboarding/assessment", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test(
                    "Get Initial Assessment",
                    "PASS",
                    f"- {len(data.get('questions', []))} questions received",
                )
            else:
                self.log_test(
                    "Get Initial Assessment", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Initial Assessment", "FAIL", str(e))

        # Test 2: Submit Assessment
        try:
            assessment_data = {
                "answers": [
                    {"question_id": 1, "answer": "intermediate", "is_correct": True},
                    {"question_id": 2, "answer": "work", "is_correct": True},
                    {"question_id": 3, "answer": "5-10", "is_correct": True},
                ]
            }

            response = self.client.post(
                "/api/onboarding/submit-assessment",
                json=assessment_data,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test(
                    "Submit Assessment",
                    "PASS",
                    f"- Level: {data.get('proficiency_level', 'N/A')}",
                )
            else:
                self.log_test(
                    "Submit Assessment", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Submit Assessment", "FAIL", str(e))

        # Test 3: Get Recommended Learning Paths
        try:
            response = self.client.get(
                "/api/learning-paths/recommended", headers=headers
            )
            if response.status_code == 200:
                data = response.get_json()
                paths = data if isinstance(data, list) else data.get("paths", [])
                self.log_test(
                    "Get Recommended Learning Paths",
                    "PASS",
                    f"- {len(paths)} paths found",
                )
            else:
                self.log_test(
                    "Get Recommended Learning Paths",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.log_test("Get Recommended Learning Paths", "FAIL", str(e))

        return True

    # ========== GOAL SETTING TESTS ==========
    def test_goal_setting(self):
        """Test goal setting functionality"""
        self.print_section("GOAL SETTING TESTS")

        if not self.auth_token:
            self.log_test("Goal Setting", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Create User Goal
        try:
            goal_data = {
                "goal_type": "vocabulary",
                "target_value": 100,
                "timeline_days": 30,
                "description": "Learn 100 new words in 30 days",
            }

            response = self.client.post(
                "/api/goals/create",
                json=goal_data,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test(
                    "Create User Goal",
                    "PASS",
                    f"- Goal created: {data.get('goal', {}).get('description', 'N/A')}",
                )
            else:
                self.log_test(
                    "Create User Goal", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Create User Goal", "FAIL", str(e))

        # Test 2: Get User Goals
        try:
            response = self.client.get("/api/goals/", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                goals = data.get("goals", [])
                self.log_test("Get User Goals", "PASS", f"- {len(goals)} goals found")
            else:
                self.log_test(
                    "Get User Goals", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get User Goals", "FAIL", str(e))

        return True

    # ========== ACTIVITY GENERATION TESTS ==========
    def test_activity_generation(self):
        """Test AI-powered activity generation"""
        self.print_section("ACTIVITY GENERATION TESTS")

        if not self.auth_token:
            self.log_test("Activity Generation", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Generate Vocabulary Activity
        try:
            activity_request = {
                "activity_type": "vocabulary",
                "difficulty": "intermediate",
                "topic": "daily_conversation",
            }

            response = self.client.post(
                "/api/activities/generate",
                json=activity_request,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test(
                    "Generate Vocabulary Activity", "PASS", f"- Activity created"
                )
            else:
                self.log_test(
                    "Generate Vocabulary Activity",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.log_test("Generate Vocabulary Activity", "FAIL", str(e))

        # Test 2: Generate Grammar Activity
        try:
            activity_request = {
                "activity_type": "grammar",
                "difficulty": "intermediate",
                "topic": "present_tense",
            }

            response = self.client.post(
                "/api/activities/generate",
                json=activity_request,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                self.log_test(
                    "Generate Grammar Activity", "PASS", f"- Activity created"
                )
            else:
                self.log_test(
                    "Generate Grammar Activity",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.log_test("Generate Grammar Activity", "FAIL", str(e))

        # Test 3: Get Available Activities
        try:
            response = self.client.get("/api/activities/", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                activities = data.get("activities", [])
                self.log_test(
                    "Get Available Activities",
                    "PASS",
                    f"- {len(activities)} activities available",
                )
            else:
                self.log_test(
                    "Get Available Activities",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.log_test("Get Available Activities", "FAIL", str(e))

        return True

    # ========== PERSONALIZATION TESTS ==========
    def test_personalization(self):
        """Test personalized learning experience"""
        self.print_section("PERSONALIZATION TESTS")

        if not self.auth_token:
            self.log_test("Personalization", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Get Personalized Recommendations
        try:
            response = self.client.get(
                "/api/personalization/recommendations", headers=headers
            )
            if response.status_code == 200:
                data = response.get_json()
                self.log_test(
                    "Get Personalized Recommendations",
                    "PASS",
                    f"- Recommendations received",
                )
            else:
                self.log_test(
                    "Get Personalized Recommendations",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.log_test("Get Personalized Recommendations", "FAIL", str(e))

        # Test 2: Get User Progress
        try:
            response = self.client.get("/api/personalization/progress", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get User Progress", "PASS", f"- Progress data received")
            else:
                self.log_test(
                    "Get User Progress", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get User Progress", "FAIL", str(e))

        # Test 3: Get Adaptive Content
        try:
            response = self.client.get(
                "/api/adaptive-learning/next-activity", headers=headers
            )
            if response.status_code == 200:
                data = response.get_json()
                self.log_test(
                    "Get Adaptive Content", "PASS", f"- Next activity recommended"
                )
            else:
                self.log_test(
                    "Get Adaptive Content", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Adaptive Content", "FAIL", str(e))

        return True

    # ========== GAMIFICATION TESTS ==========
    def test_gamification(self):
        """Test gamification features"""
        self.print_section("GAMIFICATION TESTS")

        if not self.auth_token:
            self.log_test("Gamification", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Get User Badges
        try:
            response = self.client.get("/api/gamification/badges", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                badges = data.get("badges", [])
                self.log_test(
                    "Get User Badges", "PASS", f"- {len(badges)} badges found"
                )
            else:
                self.log_test(
                    "Get User Badges", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get User Badges", "FAIL", str(e))

        # Test 2: Get Leaderboard
        try:
            response = self.client.get("/api/gamification/leaderboard", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get Leaderboard", "PASS", f"- Leaderboard received")
            else:
                self.log_test(
                    "Get Leaderboard", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Leaderboard", "FAIL", str(e))

        # Test 3: Get User Stats
        try:
            response = self.client.get("/api/gamification/stats", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get User Stats", "PASS", f"- Stats received")
            else:
                self.log_test(
                    "Get User Stats", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get User Stats", "FAIL", str(e))

        return True

    # ========== CHAT TUTOR TESTS ==========
    def test_chat_tutor(self):
        """Test AI chat tutor functionality"""
        self.print_section("CHAT TUTOR TESTS")

        if not self.auth_token:
            self.log_test("Chat Tutor", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Send Chat Message
        try:
            chat_message = {
                "message": "How do I say hello in Telugu?",
                "context": "learning",
            }

            response = self.client.post(
                "/api/chat/message",
                json=chat_message,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test("Send Chat Message", "PASS", f"- Response received")
            else:
                self.log_test(
                    "Send Chat Message", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Send Chat Message", "FAIL", str(e))

        # Test 2: Get Chat History
        try:
            response = self.client.get("/api/chat/history", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get Chat History", "PASS", f"- Chat history received")
            else:
                self.log_test(
                    "Get Chat History", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Chat History", "FAIL", str(e))

        return True

    # ========== PRACTICE SESSION TESTS ==========
    def test_practice_sessions(self):
        """Test practice session functionality"""
        self.print_section("PRACTICE SESSION TESTS")

        if not self.auth_token:
            self.log_test("Practice Sessions", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Start Practice Session
        try:
            session_data = {"activity_type": "vocabulary", "difficulty": "intermediate"}

            response = self.client.post(
                "/api/practice/start",
                json=session_data,
                headers=headers,
                content_type="application/json",
            )

            if response.status_code in [200, 201]:
                data = response.get_json()
                self.log_test("Start Practice Session", "PASS", f"- Session started")
            else:
                self.log_test(
                    "Start Practice Session", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Start Practice Session", "FAIL", str(e))

        # Test 2: Get Practice History
        try:
            response = self.client.get("/api/practice/history", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get Practice History", "PASS", f"- History received")
            else:
                self.log_test(
                    "Get Practice History", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Practice History", "FAIL", str(e))

        return True

    # ========== ANALYTICS TESTS ==========
    def test_analytics(self):
        """Test analytics and reporting"""
        self.print_section("ANALYTICS TESTS")

        if not self.auth_token:
            self.log_test("Analytics", "FAIL", "No auth token available")
            return False

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test 1: Get Learning Analytics
        try:
            response = self.client.get("/api/analytics/learning", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get Learning Analytics", "PASS", f"- Analytics received")
            else:
                self.log_test(
                    "Get Learning Analytics", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Learning Analytics", "FAIL", str(e))

        # Test 2: Get Performance Metrics
        try:
            response = self.client.get("/api/analytics/performance", headers=headers)
            if response.status_code == 200:
                data = response.get_json()
                self.log_test("Get Performance Metrics", "PASS", f"- Metrics received")
            else:
                self.log_test(
                    "Get Performance Metrics", "FAIL", f"Status: {response.status_code}"
                )
        except Exception as e:
            self.log_test("Get Performance Metrics", "FAIL", str(e))

        return True

    # ========== MAIN TEST RUNNER ==========
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "=" * 80)
        print("  COMPREHENSIVE APPLICATION TEST SUITE")
        print("  Testing all user flows and personalized learning experiences")
        print("=" * 80 + "\n")

        # Run all test suites
        self.test_database_connection()
        self.test_authentication_flow()
        self.test_onboarding_flow()
        self.test_goal_setting()
        self.test_activity_generation()
        self.test_personalization()
        self.test_gamification()
        self.test_chat_tutor()
        self.test_practice_sessions()
        self.test_analytics()

        # Print final results
        self.print_final_results()

    def print_final_results(self):
        """Print final test results summary"""
        print("\n" + "=" * 80)
        print("  TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"\nTotal Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']} ✓")
        print(f"Failed: {self.test_results['failed']} ✗")

        if self.test_results["failed"] > 0:
            print(f"\nFailed Tests:")
            for error in self.test_results["errors"]:
                print(f"  - {error}")

        success_rate = (
            (self.test_results["passed"] / self.test_results["total_tests"] * 100)
            if self.test_results["total_tests"] > 0
            else 0
        )
        print(f"\nSuccess Rate: {success_rate:.2f}%")
        print("=" * 80 + "\n")

        # Save results to file
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print("Results saved to test_results.json\n")


if __name__ == "__main__":
    try:
        tester = ComprehensiveTestSuite()
        tester.run_all_tests()
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
