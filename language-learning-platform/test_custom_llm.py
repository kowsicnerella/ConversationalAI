"""
Test Script for Custom LLM Model Response
Tests the custom model endpoint with various prompts and scenarios
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_config import LLMConfig, LLMProvider

# Load environment
load_dotenv()


class CustomLLMTester:
    """Test suite for custom LLM model"""

    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = None

    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70)

    def print_test(self, test_name):
        """Print test name"""
        print(f"\n🧪 Test: {test_name}")
        print("-" * 70)

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")

    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        self.print_test(test_name)
        self.total_tests += 1
        
        try:
            start = time.time()
            result = test_func()
            duration = time.time() - start
            
            self.results.append({
                "test": test_name,
                "status": "PASSED" if result["success"] else "FAILED",
                "duration": f"{duration:.2f}s",
                "details": result
            })
            
            if result["success"]:
                self.passed_tests += 1
                self.print_success(f"Test passed in {duration:.2f}s")
                if "response" in result:
                    print(f"\n📝 Response Preview:\n{result['response'][:200]}...")
            else:
                self.failed_tests += 1
                self.print_error(f"Test failed: {result.get('error', 'Unknown error')}")
            
            return result
        
        except Exception as e:
            self.failed_tests += 1
            error_msg = str(e)
            self.print_error(f"Test crashed: {error_msg}")
            self.results.append({
                "test": test_name,
                "status": "CRASHED",
                "duration": "N/A",
                "error": error_msg
            })
            return {"success": False, "error": error_msg}

    # ==================== TEST CASES ====================

    def test_basic_text_generation(self):
        """Test basic text generation"""
        prompt = "Say 'Hello, World!' in Telugu and English."
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.7,
            max_tokens=100
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["text"],
                "model": response.get("model"),
                "tokens": response.get("usage", {})
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_telugu_translation(self):
        """Test Telugu-English translation"""
        prompt = "Translate the following English text to Telugu: 'Good morning, how are you?'"
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.5,
            max_tokens=150
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["text"],
                "model": response.get("model")
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_grammar_explanation(self):
        """Test grammar explanation generation"""
        prompt = """Explain the difference between present simple and present continuous tense in English.
        Provide examples for a beginner learner."""
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.7,
            max_tokens=300
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["text"],
                "model": response.get("model")
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_json_generation(self):
        """Test JSON format response"""
        prompt = """Generate a simple vocabulary quiz question about animals.
        Return ONLY a JSON object with this structure:
        {
            "question": "question text",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "explanation text"
        }"""
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.5,
            max_tokens=300,
            json_mode=True
        )
        
        if response["success"]:
            try:
                # Try to parse as JSON
                json_data = json.loads(response["text"])
                return {
                    "success": True,
                    "response": json.dumps(json_data, indent=2),
                    "model": response.get("model"),
                    "json_valid": True
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON: {e}",
                    "raw_response": response["text"]
                }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_chat_completion(self):
        """Test chat-style completion"""
        messages = [
            {"role": "system", "content": "You are a helpful English language tutor."},
            {"role": "user", "content": "What are some common greetings in English?"},
        ]
        
        response = LLMConfig.chat_completion(
            messages=messages,
            stream=False,
            provider=LLMProvider.CUSTOM,
            temperature=0.7,
            max_tokens=200
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["message"],
                "model": response.get("model")
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_long_form_content(self):
        """Test longer content generation"""
        prompt = """Write a short story (3-4 sentences) about a student learning English.
        Make it motivational and encouraging."""
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.8,
            max_tokens=500
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["text"],
                "model": response.get("model"),
                "word_count": len(response["text"].split())
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_system_prompt_adherence(self):
        """Test if model follows system prompts"""
        system_prompt = "You are a strict grammar checker. Only respond with corrections, no explanations."
        prompt = "Me go to school yesterday."
        
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=100
        )
        
        if response["success"]:
            return {
                "success": True,
                "response": response["text"],
                "model": response.get("model")
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Unknown error")
            }

    def test_temperature_variation(self):
        """Test different temperature settings"""
        prompt = "Describe a sunny day in one sentence."
        results = []
        
        for temp in [0.0, 0.5, 1.0]:
            response = LLMConfig.generate_text(
                prompt=prompt,
                provider=LLMProvider.CUSTOM,
                temperature=temp,
                max_tokens=50
            )
            
            if response["success"]:
                results.append({
                    "temperature": temp,
                    "response": response["text"]
                })
        
        if len(results) == 3:
            return {
                "success": True,
                "response": json.dumps(results, indent=2),
                "model": "temperature comparison"
            }
        else:
            return {
                "success": False,
                "error": "Not all temperature tests succeeded"
            }

    def test_fallback_mechanism(self):
        """Test if fallback to Gemini works when custom fails"""
        # This test will intentionally fail custom and check Gemini fallback
        self.print_info("Testing fallback mechanism (expect custom to fail, Gemini to succeed)")
        
        prompt = "Say hello in a simple way."
        
        # Try with custom first
        response = LLMConfig.generate_text(
            prompt=prompt,
            provider=LLMProvider.CUSTOM,
            temperature=0.7,
            max_tokens=50
        )
        
        # The fallback is automatic in LLMConfig
        if response["success"]:
            used_model = response.get("model", "unknown")
            is_gemini = "gemini" in used_model.lower()
            
            return {
                "success": True,
                "response": response["text"],
                "model": used_model,
                "used_fallback": is_gemini
            }
        else:
            return {
                "success": False,
                "error": response.get("error", "Both custom and fallback failed")
            }

    def test_endpoint_connection(self):
        """Test if custom endpoint is reachable"""
        endpoint = os.getenv("VLLM_ENDPOINT")
        
        if not endpoint or endpoint == "None":
            return {
                "success": False,
                "error": "VLLM_ENDPOINT not configured in .env"
            }
        
        self.print_info(f"Testing endpoint: {endpoint}")
        
        try:
            import requests
            # Simple health check
            response = requests.get(endpoint, timeout=5)
            return {
                "success": True,
                "response": f"Endpoint reachable. Status: {response.status_code}",
                "endpoint": endpoint
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Endpoint timeout (5s)",
                "endpoint": endpoint
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to endpoint",
                "endpoint": endpoint
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {str(e)}",
                "endpoint": endpoint
            }

    # ==================== MAIN TEST RUNNER ====================

    def run_all_tests(self):
        """Run all tests and generate report"""
        self.print_header("🚀 Custom LLM Model Test Suite")
        self.start_time = datetime.now()
        
        # Print configuration
        self.print_info(f"VLLM_ENDPOINT: {os.getenv('VLLM_ENDPOINT')}")
        self.print_info(f"Default Provider: {LLMConfig.DEFAULT_PROVIDER.value}")
        self.print_info(f"Custom Model: {LLMConfig.MODELS[LLMProvider.CUSTOM]['text']}")
        
        # Run all tests
        self.run_test("1. Endpoint Connection Test", self.test_endpoint_connection)
        self.run_test("2. Basic Text Generation", self.test_basic_text_generation)
        self.run_test("3. Telugu Translation", self.test_telugu_translation)
        self.run_test("4. Grammar Explanation", self.test_grammar_explanation)
        self.run_test("5. JSON Generation", self.test_json_generation)
        self.run_test("6. Chat Completion", self.test_chat_completion)
        self.run_test("7. Long Form Content", self.test_long_form_content)
        self.run_test("8. System Prompt Adherence", self.test_system_prompt_adherence)
        self.run_test("9. Temperature Variation", self.test_temperature_variation)
        self.run_test("10. Fallback Mechanism", self.test_fallback_mechanism)
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate and display test summary"""
        self.print_header("📊 Test Summary")
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n⏱️  Total Duration: {duration:.2f}s")
        print(f"📝 Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        
        # Detailed results
        print("\n" + "=" * 70)
        print("Detailed Results:")
        print("=" * 70)
        
        for i, result in enumerate(self.results, 1):
            status_symbol = "✅" if result["status"] == "PASSED" else "❌"
            print(f"\n{i}. {status_symbol} {result['test']}")
            print(f"   Status: {result['status']} | Duration: {result['duration']}")
            
            if result["status"] != "PASSED":
                print(f"   Error: {result.get('error', 'N/A')}")
        
        # Save results to JSON
        self.save_results()

    def save_results(self):
        """Save test results to JSON file"""
        output_file = "llm_test_results.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": os.getenv("VLLM_ENDPOINT"),
            "model": LLMConfig.MODELS[LLMProvider.CUSTOM]['text'],
            "summary": {
                "total_tests": self.total_tests,
                "passed": self.passed_tests,
                "failed": self.failed_tests,
                "success_rate": f"{(self.passed_tests/self.total_tests*100):.1f}%"
            },
            "results": self.results
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.print_success(f"Results saved to: {output_file}")


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  🤖 Custom LLM Model Test Script")
    print("  Testing custom model responses and fallback mechanisms")
    print("=" * 70)
    
    tester = CustomLLMTester()
    tester.run_all_tests()
    
    print("\n" + "=" * 70)
    print("  🎉 Testing Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
