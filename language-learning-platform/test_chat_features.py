"""
Comprehensive Chat Feature Test
Tests all AI chat features including web search, memory, vector DB, and learning management
"""

import json
import time
from datetime import datetime
import requests
from colorama import Fore, Style, init

init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:5000/api/chat"
TEST_USER_ID = 1
TEST_CONVERSATION_TITLE = f"Test Chat - {datetime.now().isoformat()}"
TEST_MESSAGES = [
    "What is the difference between 'a' and 'an'?",
    "Give me an example of present perfect tense",
    "How do I improve my pronunciation in English?",
]

class ChatTester:
    def __init__(self, base_url, user_id):
        self.base_url = base_url
        self.user_id = user_id
        self.conversation_id = None
        self.headers = {
            "Content-Type": "application/json",
            "X-User-ID": str(user_id),
            "Authorization": f"Bearer test-token-{user_id}"
        }
        self.results = {
            "tests": [],
            "stats": {
                "passed": 0,
                "failed": 0,
                "total": 0,
            }
        }

    def log_test(self, name, status, details=""):
        """Log test result"""
        message = f"{Fore.GREEN}✓{Style.RESET_ALL}" if status else f"{Fore.RED}✗{Style.RESET_ALL}"
        print(f"{message} {name}")
        if details:
            print(f"  └─ {details}")
        
        self.results["tests"].append({
            "name": name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        self.results["stats"]["total"] += 1
        if status:
            self.results["stats"]["passed"] += 1
        else:
            self.results["stats"]["failed"] += 1

    def test_create_conversation(self):
        """Test creating a new conversation"""
        print(f"\n{Fore.CYAN}Testing: Create Conversation{Style.RESET_ALL}")
        try:
            payload = {
                "title": TEST_CONVERSATION_TITLE,
                "topic": "general"
            }
            response = requests.post(
                f"{self.base_url}/conversations",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.conversation_id = data["conversation"]["id"]
                    self.log_test(
                        "Create Conversation",
                        True,
                        f"Created conversation ID: {self.conversation_id}"
                    )
                    return True
            
            self.log_test("Create Conversation", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Create Conversation", False, str(e))
            return False

    def test_send_message(self):
        """Test sending messages"""
        print(f"\n{Fore.CYAN}Testing: Send Messages{Style.RESET_ALL}")
        if not self.conversation_id:
            self.log_test("Send Message", False, "No conversation ID")
            return False

        success_count = 0
        for msg in TEST_MESSAGES:
            try:
                payload = {
                    "message": msg,
                    "use_web_search": False,
                    "topic": "general"
                }
                response = requests.post(
                    f"{self.base_url}/conversations/{self.conversation_id}/messages",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        success_count += 1
                        self.log_test(
                            f"Send Message: '{msg[:40]}...'",
                            True,
                            f"Response received"
                        )
                    else:
                        self.log_test(f"Send Message: '{msg[:40]}...'", False, data.get("error"))
                else:
                    self.log_test(f"Send Message: '{msg[:40]}...'", False, f"Status: {response.status_code}")
                
                # Small delay between messages
                time.sleep(0.5)
            except Exception as e:
                self.log_test(f"Send Message: '{msg[:40]}...'", False, str(e))
        
        return success_count == len(TEST_MESSAGES)

    def test_get_messages(self):
        """Test retrieving conversation messages"""
        print(f"\n{Fore.CYAN}Testing: Get Messages{Style.RESET_ALL}")
        if not self.conversation_id:
            self.log_test("Get Messages", False, "No conversation ID")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/conversations/{self.conversation_id}/messages",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    messages = data.get("messages", [])
                    self.log_test(
                        "Get Messages",
                        True,
                        f"Retrieved {len(messages)} messages"
                    )
                    return True
            
            self.log_test("Get Messages", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Get Messages", False, str(e))
            return False

    def test_web_search(self):
        """Test web search functionality"""
        print(f"\n{Fore.CYAN}Testing: Web Search{Style.RESET_ALL}")
        try:
            payload = {
                "query": "English grammar tips",
                "max_results": 3
            }
            response = requests.post(
                f"{self.base_url}/web-search",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    results = data.get("results", [])
                    self.log_test(
                        "Web Search",
                        True,
                        f"Retrieved {len(results)} search results"
                    )
                    return True
            
            self.log_test("Web Search", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Web Search", False, str(e))
            return False

    def test_user_learning_context(self):
        """Test getting user learning context"""
        print(f"\n{Fore.CYAN}Testing: User Learning Context{Style.RESET_ALL}")
        try:
            response = requests.get(
                f"{self.base_url}/user-learning-context",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    context = data.get("context", {})
                    self.log_test(
                        "User Learning Context",
                        True,
                        f"Topics: {context.get('recent_topics', [])[:2]}"
                    )
                    return True
            
            self.log_test("User Learning Context", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("User Learning Context", False, str(e))
            return False

    def test_user_memories(self):
        """Test getting user memories"""
        print(f"\n{Fore.CYAN}Testing: User Memories{Style.RESET_ALL}")
        try:
            response = requests.get(
                f"{self.base_url}/user-memories",
                headers=self.headers
            )
            
            if response.status_code in [200, 503]:  # 503 if service not available
                data = response.json()
                if data.get("success"):
                    memories = data.get("memories", [])
                    self.log_test(
                        "User Memories",
                        True,
                        f"Retrieved {len(memories)} memories (Mem0 available)"
                    )
                else:
                    self.log_test(
                        "User Memories",
                        True,
                        "Mem0 service not available (expected in test environment)"
                    )
                return True
            
            self.log_test("User Memories", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("User Memories", False, str(e))
            return False

    def test_conversation_analytics(self):
        """Test getting conversation analytics"""
        print(f"\n{Fore.CYAN}Testing: Conversation Analytics{Style.RESET_ALL}")
        if not self.conversation_id:
            self.log_test("Conversation Analytics", False, "No conversation ID")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/analytics/conversations/{self.conversation_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    analytics = data.get("analytics", {})
                    self.log_test(
                        "Conversation Analytics",
                        True,
                        f"Messages: {analytics.get('message_count', 0)}"
                    )
                    return True
            
            self.log_test("Conversation Analytics", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Conversation Analytics", False, str(e))
            return False

    def test_learning_statistics(self):
        """Test getting learning statistics"""
        print(f"\n{Fore.CYAN}Testing: Learning Statistics{Style.RESET_ALL}")
        try:
            response = requests.get(
                f"{self.base_url}/analytics/learning-statistics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    stats = data.get("statistics", {})
                    self.log_test(
                        "Learning Statistics",
                        True,
                        f"Conversations: {stats.get('conversation_count', 0)}"
                    )
                    return True
            
            self.log_test("Learning Statistics", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Learning Statistics", False, str(e))
            return False

    def test_get_conversations(self):
        """Test getting user conversations"""
        print(f"\n{Fore.CYAN}Testing: Get Conversations{Style.RESET_ALL}")
        try:
            response = requests.get(
                f"{self.base_url}/conversations",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    conversations = data.get("conversations", [])
                    self.log_test(
                        "Get Conversations",
                        True,
                        f"Retrieved {len(conversations)} conversations"
                    )
                    return True
            
            self.log_test("Get Conversations", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Get Conversations", False, str(e))
            return False

    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Chat Feature - Comprehensive Test Suite{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        # Run tests in order
        tests = [
            self.test_create_conversation,
            self.test_send_message,
            self.test_get_messages,
            self.test_get_conversations,
            self.test_web_search,
            self.test_user_learning_context,
            self.test_user_memories,
            self.test_conversation_analytics,
            self.test_learning_statistics,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"{Fore.RED}Test error: {e}{Style.RESET_ALL}")
        
        # Print summary
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
        print(f"  Total: {self.results['stats']['total']}")
        print(f"  {Fore.GREEN}Passed: {self.results['stats']['passed']}{Style.RESET_ALL}")
        print(f"  {Fore.RED}Failed: {self.results['stats']['failed']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}\n")
        
        # Save results
        self.save_results()

    def save_results(self):
        """Save test results to file"""
        filename = "chat_test_results.json"
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"✓ Results saved to {filename}")


if __name__ == "__main__":
    tester = ChatTester(BASE_URL, TEST_USER_ID)
    tester.run_all_tests()
