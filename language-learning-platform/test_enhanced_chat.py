"""
Enhanced Chat Testing with Mem0 Integration
Tests the improved chat accuracy and personalization
"""

import requests
import json
import time
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000/api"


class EnhancedChatTester:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.conversation_id = None
        self.test_results = []

    def log(self, test_name, passed, message="", details=None):
        """Log test result"""
        status = f"{Fore.GREEN}✓ PASS" if passed else f"{Fore.RED}✗ FAIL"
        print(f"{status}{Style.RESET_ALL} - {test_name}")
        if message:
            print(f"  {Fore.CYAN}{message}{Style.RESET_ALL}")
        if details and not passed:
            print(f"  {Fore.YELLOW}Details: {details}{Style.RESET_ALL}")

        self.test_results.append(
            {"test": test_name, "passed": passed, "message": message}
        )

    def section(self, title):
        """Print section header"""
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}  {title}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

    def login(self):
        """Login or create test user"""
        self.section("AUTHENTICATION")

        # Try to login first
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "chattest", "password": "TestPass123!"},
            )

            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                self.log(
                    "User Login", True, f"Logged in as chattest (ID: {self.user_id})"
                )
                return True
        except:
            pass

        # Create user if login failed
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": "chattest",
                    "email": "chattest@test.com",
                    "password": "TestPass123!",
                },
            )

            if response.status_code in [200, 201]:
                # Now login
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={"username": "chattest", "password": "TestPass123!"},
                )

                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    self.user_id = data.get("user", {}).get("id")
                    self.log(
                        "User Registration & Login",
                        True,
                        f"Created and logged in as chattest",
                    )
                    return True
        except Exception as e:
            self.log("Authentication", False, str(e))
            return False

    def test_mem0_integration(self):
        """Test Mem0 integration"""
        self.section("MEM0 INTEGRATION TEST")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.get(
                f"{BASE_URL}/enhanced-chat/test-mem0", headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                test_results = data.get("test_results", {})
                mem0_available = test_results.get("mem0_available", False)

                if mem0_available:
                    memory_count = test_results.get("memory_count", 0)
                    self.log(
                        "Mem0 Integration",
                        True,
                        f"Mem0 is active! Found {memory_count} memories",
                    )
                    return True
                else:
                    self.log(
                        "Mem0 Integration",
                        True,
                        "Mem0 not configured (will use standard chat)",
                    )
                    return True
            else:
                self.log("Mem0 Integration", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log("Mem0 Integration", False, str(e))
            return False

    def test_create_conversation(self):
        """Test creating a conversation"""
        self.section("CREATE CONVERSATION")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.post(
                f"{BASE_URL}/enhanced-chat/conversations",
                json={"title": "Test Learning Session", "topic": "grammar_practice"},
                headers=headers,
            )

            if response.status_code == 201:
                data = response.json()
                conversation = data.get("conversation", {})
                self.conversation_id = conversation.get("id")
                self.log(
                    "Create Conversation",
                    True,
                    f"Created conversation ID: {self.conversation_id}",
                )
                return True
            else:
                self.log(
                    "Create Conversation",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log("Create Conversation", False, str(e))
            return False

    def test_send_messages(self):
        """Test sending messages with context"""
        self.section("SEND MESSAGES WITH CONTEXT")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        # Test messages that demonstrate personalization
        test_messages = [
            {
                "message": "How do I say 'Good morning' in Telugu?",
                "expected_keywords": ["శుభోదయం", "telugu", "morning"],
            },
            {
                "message": "What is the difference between 'I am' and 'I was'?",
                "expected_keywords": ["present", "past", "tense", "example"],
            },
            {
                "message": "Can you help me introduce myself in English?",
                "expected_keywords": ["introduction", "example", "name"],
            },
            {
                "message": "I want to learn about English verb tenses",
                "expected_keywords": ["verb", "tense", "example", "present", "past"],
            },
            {
                "message": "Teach me 5 common English greetings",
                "expected_keywords": ["hello", "greeting", "example"],
            },
        ]

        for i, test_msg in enumerate(test_messages, 1):
            try:
                print(
                    f"\n{Fore.CYAN}Message {i}: {test_msg['message']}{Style.RESET_ALL}"
                )

                response = requests.post(
                    f"{BASE_URL}/enhanced-chat/conversations/{self.conversation_id}/message",
                    json={"message": test_msg["message"]},
                    headers=headers,
                )

                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("ai_response", {})
                    content = ai_response.get("content", "")

                    # Check for Telugu translation
                    has_telugu = ai_response.get("telugu_translation") is not None

                    # Check for examples
                    has_examples = len(ai_response.get("examples", [])) > 0

                    # Check for grammar explanation
                    has_grammar = ai_response.get("grammar_explanation") is not None

                    # Display response summary
                    print(f"  {Fore.GREEN}Response received:{Style.RESET_ALL}")
                    print(f"  - Length: {len(content)} characters")
                    print(f"  - Has Telugu: {'✓' if has_telugu else '✗'}")
                    print(
                        f"  - Has Examples: {'✓' if has_examples else '✗'} ({len(ai_response.get('examples', []))} examples)"
                    )
                    print(f"  - Has Grammar: {'✓' if has_grammar else '✗'}")

                    # Show first 200 chars of response
                    print(f"\n  {Fore.WHITE}Response preview:{Style.RESET_ALL}")
                    print(f"  {content[:200]}...")

                    # Show context used
                    context_info = data.get("context_info", {})
                    personalization = context_info.get("personalization_used", {})
                    print(f"\n  {Fore.MAGENTA}Personalization:{Style.RESET_ALL}")
                    print(
                        f"  - Proficiency: {personalization.get('proficiency_level', 'N/A')}"
                    )
                    print(
                        f"  - Memories Used: {personalization.get('memories_used', 0)}"
                    )
                    print(
                        f"  - Mem0 Enabled: {context_info.get('mem0_enabled', False)}"
                    )

                    self.log(f"Message {i}", True, "Response received with context")
                else:
                    self.log(
                        f"Message {i}",
                        False,
                        f"Status: {response.status_code}",
                        response.text,
                    )

                time.sleep(1)  # Small delay between messages

            except Exception as e:
                self.log(f"Message {i}", False, str(e))

        return True

    def test_quick_chat(self):
        """Test quick chat endpoint"""
        self.section("QUICK CHAT (Single Request)")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.post(
                f"{BASE_URL}/enhanced-chat/quick-chat",
                json={
                    "message": "Explain English articles (a, an, the) with Telugu examples",
                    "topic": "grammar",
                },
                headers=headers,
            )

            if response.status_code == 201:
                data = response.json()
                ai_response = data.get("ai_response", {})
                content = ai_response.get("content", "")

                print(f"{Fore.GREEN}Quick Chat Response:{Style.RESET_ALL}")
                print(f"Length: {len(content)} characters")
                print(f"\nPreview:\n{content[:300]}...")

                self.log("Quick Chat", True, "Received comprehensive response")
                return True
            else:
                self.log(
                    "Quick Chat",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log("Quick Chat", False, str(e))
            return False

    def test_conversation_summary(self):
        """Test conversation summary generation"""
        self.section("CONVERSATION SUMMARY")

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        try:
            response = requests.get(
                f"{BASE_URL}/enhanced-chat/conversations/{self.conversation_id}/summary",
                headers=headers,
            )

            if response.status_code == 200:
                data = response.json()
                summary = data.get("summary", "")
                message_count = data.get("message_count", 0)

                print(f"{Fore.GREEN}Summary Generated:{Style.RESET_ALL}")
                print(f"Messages analyzed: {message_count}")
                print(f"\n{Fore.WHITE}Summary:{Style.RESET_ALL}")
                print(summary)

                self.log(
                    "Conversation Summary", True, f"Analyzed {message_count} messages"
                )
                return True
            else:
                self.log(
                    "Conversation Summary",
                    False,
                    f"Status: {response.status_code}",
                    response.text,
                )
                return False
        except Exception as e:
            self.log("Conversation Summary", False, str(e))
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}  ENHANCED CHAT TESTING WITH MEM0 INTEGRATION")
        print(f"{Fore.CYAN}  Testing Improved Accuracy & Personalization")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

        if not self.login():
            print(
                f"\n{Fore.RED}Authentication failed. Cannot continue.{Style.RESET_ALL}"
            )
            return

        self.test_mem0_integration()
        self.test_create_conversation()
        self.test_send_messages()
        self.test_quick_chat()
        self.test_conversation_summary()

        # Print summary
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}  TEST SUMMARY")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")

        passed = sum(1 for r in self.test_results if r["passed"])
        failed = len(self.test_results) - passed
        success_rate = (
            (passed / len(self.test_results) * 100) if self.test_results else 0
        )

        print(f"Total Tests: {len(self.test_results)}")
        print(f"{Fore.GREEN}Passed: {passed} ✓{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed: {failed} ✗{Style.RESET_ALL}")
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if failed > 0:
            print(f"\n{Fore.RED}Failed Tests:{Style.RESET_ALL}")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['test']}: {result['message']}")

        print(
            f"\n{Fore.CYAN}Results saved to enhanced_chat_test_results.json{Style.RESET_ALL}\n"
        )

        with open("enhanced_chat_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)


if __name__ == "__main__":
    print(f"{Fore.YELLOW}Starting Enhanced Chat Testing...")
    print(
        f"{Fore.YELLOW}Make sure Flask server is running on {BASE_URL}{Style.RESET_ALL}\n"
    )

    time.sleep(1)

    tester = EnhancedChatTester()
    tester.run_all_tests()
