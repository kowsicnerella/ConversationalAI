"""
Complete User Flow Testing
Tests the entire user journey from registration to advanced learning
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000/api"


class UserFlowTester:
    def __init__(self):
        self.results = {"total_tests": 0, "passed": 0, "failed": 0, "errors": []}
        self.auth_token = None
        self.user_id = None
        self.username = f"flowtest_{int(time.time())}"
        self.email = f"flowtest_{int(time.time())}@test.com"

    def log_result(self, test_name, passed, message="", details=None):
        """Log test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed"] += 1
            print(f"{Fore.GREEN}✓ {test_name}{Style.RESET_ALL}")
            if message:
                print(f"  {Fore.CYAN}{message}{Style.RESET_ALL}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(
                {"test": test_name, "message": message, "details": details}
            )
            print(f"{Fore.RED}✗ {test_name}{Style.RESET_ALL}")
            print(f"  {Fore.RED}{message}{Style.RESET_ALL}")
            if details:
                print(f"  {Fore.YELLOW}Details: {details}{Style.RESET_ALL}")

    def section_header(self, title):
        """Print section header"""
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}  {title}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

    def test_user_registration(self):
        """Test: User Registration"""
        self.section_header("STEP 1: USER REGISTRATION")

        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": self.username,
                    "email": self.email,
                    "password": "TestPass123!",
                },
            )

            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result(
                    "User Registration", True, f"Created user: {self.username}"
                )
                return True
            else:
                self.log_result(
                    "User Registration",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("User Registration", False, str(e))
            return False

    def test_user_login(self):
        """Test: User Login"""
        self.section_header("STEP 2: USER LOGIN")

        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": self.username, "password": "TestPass123!"},
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log_result(
                    "User Login",
                    True,
                    f"Logged in as {self.username} (ID: {self.user_id})",
                )
                return True
            else:
                self.log_result(
                    "User Login",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("User Login", False, str(e))
            return False

    def test_initial_assessment(self):
        """Test: Initial Proficiency Assessment"""
        self.section_header("STEP 3: INITIAL PROFICIENCY ASSESSMENT")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Get assessment questions
        try:
            response = requests.get(
                f"{BASE_URL}/onboarding/assessment", headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                questions = data.get("questions", [])
                self.log_result(
                    "Get Assessment Questions",
                    True,
                    f"Received {len(questions)} assessment questions",
                )
            else:
                self.log_result(
                    "Get Assessment Questions",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("Get Assessment Questions", False, str(e))
            return False

        # Submit assessment
        try:
            assessment_data = {
                "answers": [
                    {"question_id": 1, "answer": "intermediate", "is_correct": True},
                    {"question_id": 2, "answer": "work", "is_correct": True},
                    {"question_id": 3, "answer": "10-15", "is_correct": True},
                    {"question_id": 4, "answer": "visual", "is_correct": True},
                ]
            }

            response = requests.post(
                f"{BASE_URL}/onboarding/submit-assessment",
                json=assessment_data,
                headers=headers,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                level = data.get("proficiency_level", "N/A")
                self.log_result(
                    "Submit Assessment",
                    True,
                    f"Assessment completed - Proficiency Level: {level}",
                )
                return True
            else:
                self.log_result(
                    "Submit Assessment",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("Submit Assessment", False, str(e))
            return False

    def test_goal_setting(self):
        """Test: Goal Setting"""
        self.section_header("STEP 4: SETTING LEARNING GOALS")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        goals = [
            {
                "goal_type": "vocabulary",
                "target_value": 100,
                "timeline_days": 30,
                "description": "Learn 100 new words in 30 days",
            },
            {
                "goal_type": "practice_time",
                "target_value": 60,
                "timeline_days": 7,
                "description": "Practice 60 minutes per week",
            },
            {
                "goal_type": "streak",
                "target_value": 30,
                "timeline_days": 30,
                "description": "Maintain 30-day learning streak",
            },
        ]

        for goal in goals:
            try:
                response = requests.post(
                    f"{BASE_URL}/goals/create", json=goal, headers=headers
                )

                if response.status_code in [200, 201]:
                    self.log_result(
                        f"Create Goal: {goal['description']}",
                        True,
                        "Goal created successfully",
                    )
                else:
                    self.log_result(
                        f"Create Goal: {goal['description']}",
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(f"Create Goal: {goal['description']}", False, str(e))

        return True

    def test_learning_path_discovery(self):
        """Test: Discovering Learning Paths"""
        self.section_header("STEP 5: DISCOVERING LEARNING PATHS")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Get recommended paths
        try:
            response = requests.get(
                f"{BASE_URL}/learning-paths/recommended", headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                paths = data if isinstance(data, list) else data.get("paths", [])
                self.log_result(
                    "Get Recommended Paths",
                    True,
                    f"Found {len(paths)} recommended learning paths",
                )

                # Display path details
                for i, path in enumerate(paths[:3], 1):
                    print(
                        f"  {i}. {path.get('title', 'N/A')} - {path.get('difficulty_level', 'N/A')}"
                    )

                return True
            else:
                self.log_result(
                    "Get Recommended Paths",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("Get Recommended Paths", False, str(e))
            return False

    def test_activity_generation(self):
        """Test: AI Activity Generation"""
        self.section_header("STEP 6: AI-POWERED ACTIVITY GENERATION")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        activities = [
            {
                "activity_type": "vocabulary",
                "difficulty": "intermediate",
                "topic": "daily_conversation",
                "count": 1,
            },
            {
                "activity_type": "grammar",
                "difficulty": "intermediate",
                "topic": "present_tense",
                "count": 1,
            },
            {
                "activity_type": "flashcard",
                "difficulty": "intermediate",
                "topic": "common_phrases",
                "count": 1,
            },
        ]

        for activity in activities:
            try:
                response = requests.post(
                    f"{BASE_URL}/activities/generate", json=activity, headers=headers
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    self.log_result(
                        f"Generate {activity['activity_type'].title()} Activity",
                        True,
                        f"Topic: {activity['topic']}, Difficulty: {activity['difficulty']}",
                    )
                else:
                    self.log_result(
                        f"Generate {activity['activity_type'].title()} Activity",
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(
                    f"Generate {activity['activity_type'].title()} Activity",
                    False,
                    str(e),
                )

        return True

    def test_personalized_recommendations(self):
        """Test: Personalized Content Recommendations"""
        self.section_header("STEP 7: PERSONALIZED RECOMMENDATIONS")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        endpoints = [
            ("/personalization/recommendations", "Get Personalized Recommendations"),
            ("/personalization/progress", "Get User Progress"),
            ("/adaptive-learning/next-activity", "Get Next Adaptive Activity"),
        ]

        for endpoint, test_name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log_result(test_name, True, "Data received successfully")
                else:
                    self.log_result(
                        test_name,
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(test_name, False, str(e))

        return True

    def test_practice_session(self):
        """Test: Starting Practice Session"""
        self.section_header("STEP 8: PRACTICE SESSION")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Start practice session
        try:
            response = requests.post(
                f"{BASE_URL}/practice/start",
                json={"activity_type": "vocabulary", "difficulty": "intermediate"},
                headers=headers,
            )

            if response.status_code in [200, 201]:
                data = response.json()
                self.log_result(
                    "Start Practice Session",
                    True,
                    "Practice session started successfully",
                )
                return True
            else:
                self.log_result(
                    "Start Practice Session",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log_result("Start Practice Session", False, str(e))
            return False

    def test_chat_tutor(self):
        """Test: AI Chat Tutor"""
        self.section_header("STEP 9: AI CHAT TUTOR INTERACTION")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        messages = [
            "How do I say 'Good morning' in Telugu?",
            "Can you explain the difference between 'nenu' and 'meeru'?",
            "Help me practice introducing myself in English",
        ]

        for msg in messages:
            try:
                response = requests.post(
                    f"{BASE_URL}/chat/message",
                    json={"message": msg, "context": "learning"},
                    headers=headers,
                )

                if response.status_code in [200, 201]:
                    data = response.json()
                    self.log_result(f"Chat: '{msg[:40]}...'", True, "Response received")
                else:
                    self.log_result(
                        f"Chat: '{msg[:40]}...'",
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(f"Chat: '{msg[:40]}...'", False, str(e))

        return True

    def test_gamification(self):
        """Test: Gamification Features"""
        self.section_header("STEP 10: GAMIFICATION & ACHIEVEMENTS")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        endpoints = [
            ("/gamification/badges", "Get User Badges"),
            ("/gamification/achievements", "Get Achievements"),
            ("/gamification/stats", "Get User Stats"),
            ("/gamification/leaderboard", "Get Leaderboard"),
        ]

        for endpoint, test_name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    self.log_result(test_name, True, "Data retrieved successfully")
                else:
                    self.log_result(
                        test_name,
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(test_name, False, str(e))

        return True

    def test_analytics(self):
        """Test: Learning Analytics"""
        self.section_header("STEP 11: LEARNING ANALYTICS")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        endpoints = [
            ("/analytics/learning", "Get Learning Analytics"),
            ("/analytics/performance", "Get Performance Metrics"),
            ("/analytics/dashboard", "Get Dashboard Data"),
        ]

        for endpoint, test_name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                if response.status_code == 200:
                    self.log_result(test_name, True, "Analytics data retrieved")
                else:
                    self.log_result(
                        test_name,
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )
            except Exception as e:
                self.log_result(test_name, False, str(e))

        return True

    def run_complete_flow(self):
        """Run complete user flow test"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}  COMPREHENSIVE USER FLOW TESTING")
        print(f"{Fore.CYAN}  Testing Complete Learning Journey")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        # Execute all test steps
        if not self.test_user_registration():
            print(f"\n{Fore.RED}Registration failed. Cannot continue.{Style.RESET_ALL}")
            return

        if not self.test_user_login():
            print(f"\n{Fore.RED}Login failed. Cannot continue.{Style.RESET_ALL}")
            return

        self.test_initial_assessment()
        self.test_goal_setting()
        self.test_learning_path_discovery()
        self.test_activity_generation()
        self.test_personalized_recommendations()
        self.test_practice_session()
        self.test_chat_tutor()
        self.test_gamification()
        self.test_analytics()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}  TEST SUMMARY")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        success_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {passed} ✓{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed} ✗{Style.RESET_ALL}")
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if failed > 0:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for error in self.results["errors"]:
                print(f"  • {error['test']}: {error['message']}")

        # Save results
        with open("user_flow_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print(
            f"\n{Fore.CYAN}Results saved to user_flow_test_results.json{Style.RESET_ALL}\n"
        )


if __name__ == "__main__":
    print(f"{Fore.YELLOW}Starting User Flow Testing...")
    print(
        f"{Fore.YELLOW}Make sure the Flask server is running on {BASE_URL}{Style.RESET_ALL}\n"
    )

    time.sleep(2)

    tester = UserFlowTester()
    tester.run_complete_flow()
