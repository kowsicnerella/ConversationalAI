"""
Test Comprehensive Assessment Completion
This script tests the full assessment flow including completion.
"""
import requests
import time
import random
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

class AssessmentCompleteTest:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.assessment_id = None
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "SUCCESS": "✅",
            "ERROR": "❌",
            "INFO": "ℹ️",
            "TEST": "🧪",
            "PROGRESS": "📊"
        }
        print(f"[{timestamp}] {symbols.get(status, 'ℹ️')} {message}")
    
    def register_user(self):
        """Register a new test user"""
        self.log("Registering new test user...", "TEST")
        username = f"testuser_{int(time.time())}"
        payload = {
            "username": username,
            "email": f"{username}@test.com",
            "password": "Test123!",
            "native_language": "Telugu",
            "target_language": "English"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/register", json=payload)
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("user", {}).get("id")
                self.access_token = data.get("access_token")
                self.log(f"Registration successful! User ID: {self.user_id}", "SUCCESS")
                return True
            else:
                self.log(f"Registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Registration error: {str(e)}", "ERROR")
            return False
    
    def generate_assessment(self):
        """Generate a comprehensive assessment"""
        self.log("Generating comprehensive assessment...", "TEST")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/assessment/generate",
                headers=headers,
                json={"assessment_type": "comprehensive"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.assessment_id = data.get("assessment_id")
                total_questions = data.get("total_questions", 0)
                self.log(f"Assessment generated! ID: {self.assessment_id}, Questions: {total_questions}", "SUCCESS")
                return True
            else:
                self.log(f"Assessment generation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Assessment generation error: {str(e)}", "ERROR")
            return False
    
    def submit_all_answers(self):
        """Submit answers to all 36 questions"""
        self.log("Starting to answer all 36 questions...", "TEST")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # Answer options to cycle through
        answer_options = ['A', 'B', 'C', 'D']
        
        for i in range(36):
            try:
                # Get next question first
                response = self.session.get(
                    f"{BASE_URL}/api/assessment/{self.assessment_id}/next-question",
                    headers=headers
                )
                
                if response.status_code != 200:
                    self.log(f"Failed to get question {i+1}", "ERROR")
                    continue
                
                question_data = response.json()
                question_id = question_data.get("question", {}).get("id")
                
                if not question_id:
                    self.log(f"No question ID for question {i+1}", "ERROR")
                    continue
                
                # Submit answer
                answer = random.choice(answer_options)
                answer_payload = {
                    "question_id": question_id,
                    "answer": answer
                }
                
                submit_response = self.session.post(
                    f"{BASE_URL}/api/assessment/{self.assessment_id}/submit-answer",
                    headers=headers,
                    json=answer_payload
                )
                
                if submit_response.status_code == 200:
                    progress = i + 1
                    if progress % 6 == 0:  # Log every 6 questions (each skill level)
                        self.log(f"Progress: {progress}/36 questions answered", "PROGRESS")
                else:
                    self.log(f"Failed to submit answer {i+1}: {submit_response.status_code}", "ERROR")
                
                time.sleep(0.1)  # Small delay between questions
                
            except Exception as e:
                self.log(f"Error answering question {i+1}: {str(e)}", "ERROR")
        
        self.log("All 36 questions answered!", "SUCCESS")
        return True
    
    def complete_assessment(self):
        """Complete the assessment and get results"""
        self.log("Completing assessment...", "TEST")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = self.session.post(
                f"{BASE_URL}/api/assessment/{self.assessment_id}/complete",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log("Assessment completed successfully!", "SUCCESS")
                
                # Display results
                print("\n" + "="*60)
                print("📊 ASSESSMENT RESULTS")
                print("="*60)
                
                results = data.get("results", {})
                print(f"Score: {results.get('score', 0):.1f}/{results.get('max_score', 0):.1f}")
                print(f"Proficiency Level: {results.get('proficiency_level', 'N/A').upper()}")
                print(f"Confidence Score: {results.get('confidence_score', 0):.2%}")
                
                print("\n📈 Skill Breakdown:")
                skill_breakdown = results.get("skill_breakdown", {})
                for skill, score_data in skill_breakdown.items():
                    score = score_data.get("score", 0)
                    max_score = score_data.get("max_score", 0)
                    percentage = (score / max_score * 100) if max_score > 0 else 0
                    print(f"  {skill.capitalize()}: {score}/{max_score} ({percentage:.1f}%)")
                
                print("\n💪 Strengths:")
                for strength in results.get("strengths", []):
                    print(f"  • {strength}")
                
                print("\n📚 Areas for Improvement:")
                for weakness in results.get("weaknesses", []):
                    print(f"  • {weakness}")
                
                print("\n🎯 Recommendations:")
                for i, rec in enumerate(results.get("recommendations", [])[:3], 1):
                    print(f"  {i}. {rec.get('title', 'N/A')}")
                
                print("="*60 + "\n")
                
                return True
            else:
                self.log(f"Assessment completion failed: {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Assessment completion error: {str(e)}", "ERROR")
            return False
    
    def run_complete_test(self):
        """Run the complete assessment test"""
        print("\n" + "="*60)
        print("🧪 COMPREHENSIVE ASSESSMENT COMPLETION TEST")
        print("="*60 + "\n")
        
        # Step 1: Register
        if not self.register_user():
            self.log("Test failed at registration", "ERROR")
            return False
        
        time.sleep(1)
        
        # Step 2: Generate assessment
        if not self.generate_assessment():
            self.log("Test failed at assessment generation", "ERROR")
            return False
        
        time.sleep(1)
        
        # Step 3: Answer all questions
        if not self.submit_all_answers():
            self.log("Test failed at answering questions", "ERROR")
            return False
        
        time.sleep(1)
        
        # Step 4: Complete assessment
        if not self.complete_assessment():
            self.log("Test failed at assessment completion", "ERROR")
            return False
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        return True


if __name__ == "__main__":
    test = AssessmentCompleteTest()
    success = test.run_complete_test()
    exit(0 if success else 1)
