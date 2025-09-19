#!/usr/bin/env python3
"""
Test script for Personalization Features
Tests the 4-phase personalized learning journey
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

class PersonalizationTester:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        self.session = requests.Session()
        
    def authenticate(self):
        """Register and login a test user"""
        print("🔐 Testing User Authentication...")
        
        # Register test user
        register_data = {
            "username": "test_learner",
            "email": "learner@test.com",
            "password": "securepass123",
            "native_language": "Telugu",
            "target_language": "English"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/register", 
                                       json=register_data, headers=HEADERS)
            
            if response.status_code == 201:
                print("✅ User registered successfully")
            else:
                print(f"⚠️  Registration response: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure the Flask app is running on port 5000")
            return False
        
        # Login
        login_data = {
            "email": "learner@test.com",
            "password": "securepass123"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/auth/login", 
                                       json=login_data, headers=HEADERS)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data['access_token']
                self.user_id = data['user']['id']
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ User authenticated successfully")
                return True
            else:
                print(f"❌ Login failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_goal_setting(self):
        """Test Phase 1: Goal Setting"""
        print("\n📈 Testing Goal Setting (Phase 1)...")
        
        goal_data = {
            "daily_time_goal": 15,
            "learning_focus": "conversation"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/api/personalization/goals", 
                                       json=goal_data)
            
            if response.status_code == 201:
                data = response.json()
                print("✅ Goals set successfully")
                print(f"   📋 Goal: {data['goal']['daily_time_goal_minutes']} minutes daily")
                print(f"   🎯 Focus: {data['goal']['learning_focus']}")
                print(f"   🗨️  Telugu Message: {data['telugu_message']}")
                return True
            else:
                print(f"❌ Goal setting failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Goal setting error: {e}")
            return False
    
    def test_proficiency_assessment(self):
        """Test Phase 2: Proficiency Assessment"""
        print("\n🧠 Testing Proficiency Assessment (Phase 2)...")
        
        # Start assessment
        try:
            response = self.session.post(f"{BASE_URL}/api/personalization/assessment/start")
            
            if response.status_code == 201:
                data = response.json()
                assessment_id = data['assessment']['assessment_id']
                questions = data['assessment']['questions']
                
                print("✅ Assessment started successfully")
                print(f"   📝 Assessment ID: {assessment_id}")
                print(f"   ❓ Questions: {len(questions)}")
                print(f"   📢 Instructions: {data['assessment']['instructions']}")
                
                # Simulate answering questions
                sample_responses = [
                    "My name is Ravi and I am from Hyderabad. I work as a software engineer.",
                    "In the morning, I usually wake up at 6 AM, brush my teeth, and have breakfast with my family.",
                    "I want to learn English because it will help me in my career and I can communicate with people from different countries."
                ]
                
                for i, question in enumerate(questions):
                    print(f"\n   📝 Question {i+1}: {question['question']}")
                    print(f"   🗨️  Telugu Hint: {question['telugu_hint']}")
                    
                    # Submit response
                    response_data = {
                        "question_id": question['id'],
                        "user_response": sample_responses[i]
                    }
                    
                    resp = self.session.post(f"{BASE_URL}/api/personalization/assessment/{assessment_id}/respond", 
                                           json=response_data)
                    
                    if resp.status_code == 200:
                        eval_data = resp.json()
                        evaluation = eval_data['evaluation']
                        print(f"   ✅ Response evaluated")
                        print(f"   📊 Proficiency: {evaluation.get('proficiency_level', 'N/A')}")
                        print(f"   🎯 Confidence: {evaluation.get('confidence_score', 0):.2f}")
                        print(f"   📝 Grammar: {evaluation.get('grammar_score', 0):.2f}")
                        print(f"   📚 Vocabulary: {evaluation.get('vocabulary_score', 0):.2f}")
                    else:
                        print(f"   ❌ Response evaluation failed: {resp.json()}")
                
                # Complete assessment
                complete_resp = self.session.post(f"{BASE_URL}/api/personalization/assessment/{assessment_id}/complete")
                
                if complete_resp.status_code == 200:
                    results = complete_resp.json()['results']
                    print(f"\n✅ Assessment completed successfully")
                    print(f"   🏆 Final Level: {results['proficiency_level']}")
                    print(f"   📊 Confidence: {results['confidence_score']:.2f}")
                    print(f"   💪 Strengths: {', '.join(results['strengths'][:3])}")
                    print(f"   📝 Areas to improve: {', '.join(results['weaknesses'][:3])}")
                    return True
                else:
                    print(f"❌ Assessment completion failed: {complete_resp.json()}")
                    return False
                    
            else:
                print(f"❌ Assessment start failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Assessment error: {e}")
            return False
    
    def test_personalized_dashboard(self):
        """Test personalized dashboard"""
        print("\n📊 Testing Personalized Dashboard...")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/personalization/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                dashboard = data['dashboard']
                
                print("✅ Dashboard data retrieved successfully")
                print(f"   👤 User: {dashboard['user_name']}")
                print(f"   🔥 Current Streak: {dashboard['current_streak']} days")
                print(f"   🎯 Daily Goal: {dashboard['daily_goal_minutes']} minutes")
                print(f"   ⏰ Today's Progress: {dashboard['today_time_spent']} minutes")
                print(f"   📈 Goal Progress: {dashboard['goal_progress_percentage']:.1f}%")
                print(f"   🏆 Proficiency: {dashboard['proficiency_level']}")
                print(f"   ❓ Question of Day: {dashboard['question_of_day']}")
                
                challenge = dashboard['daily_challenge']['challenge']
                print(f"   🎮 Daily Challenge: {challenge['question']}")
                print(f"   🗨️  Telugu Hint: {challenge['telugu_hint']}")
                
                if dashboard['recent_vocabulary']:
                    print("   📚 Recent Vocabulary:")
                    for vocab in dashboard['recent_vocabulary']:
                        print(f"      • {vocab['english']} = {vocab['telugu']}")
                
                return True
            else:
                print(f"❌ Dashboard failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            return False
    
    def test_learning_session(self):
        """Test Phase 3: Learning Session Management"""
        print("\n🎓 Testing Learning Session (Phase 3)...")
        
        # Start session
        session_data = {"session_type": "chat"}
        
        try:
            response = self.session.post(f"{BASE_URL}/api/personalization/session/start", 
                                       json=session_data)
            
            if response.status_code == 201:
                data = response.json()
                session_id = data['session']['session_id']
                
                print("✅ Learning session started")
                print(f"   🆔 Session ID: {session_id}")
                print(f"   📝 Type: {data['session']['session_type']}")
                print(f"   💬 Initial Message: {data['session']['initial_message']}")
                
                # Simulate vocabulary learning during session
                print("\n   📚 Testing vocabulary tracking...")
                
                vocab_words = [
                    {"english_word": "beautiful", "context_sentence": "The sunset is beautiful today."},
                    {"english_word": "excited", "context_sentence": "I am excited to learn English."},
                    {"english_word": "wonderful", "context_sentence": "This is a wonderful learning experience."}
                ]
                
                for vocab in vocab_words:
                    vocab['session_id'] = session_id
                    vocab_resp = self.session.post(f"{BASE_URL}/api/personalization/vocabulary/track", 
                                                 json=vocab)
                    
                    if vocab_resp.status_code == 201:
                        vocab_data = vocab_resp.json()['vocabulary']
                        print(f"   ✅ Tracked: {vocab_data['english_word']} = {vocab_data['telugu_translation']}")
                    else:
                        print(f"   ❌ Vocab tracking failed: {vocab_resp.json()}")
                
                # Simulate some learning time
                print("   ⏰ Simulating 8 minutes of learning...")
                time.sleep(2)  # In real app, this would be actual learning time
                
                # End session
                end_data = {"user_satisfaction": 4}
                end_resp = self.session.post(f"{BASE_URL}/api/personalization/session/{session_id}/end", 
                                           json=end_data)
                
                if end_resp.status_code == 200:
                    summary = end_resp.json()['summary']
                    print(f"✅ Session ended successfully")
                    print(f"   ⏱️  Duration: {summary['duration_minutes']} minutes")
                    print(f"   📚 New words: {summary['new_words_learned']}")
                    print(f"   🎯 Goals achieved: {summary['goals_achieved']}")
                    print(f"   💬 Encouragement: {summary['encouragement_message']}")
                    
                    if 'session_summary' in summary:
                        session_summary = summary['session_summary']
                        print(f"   🎉 Achievement: {session_summary.get('achievement', 'N/A')}")
                        print(f"   📈 Progress: {session_summary.get('progress_note', 'N/A')}")
                        print(f"   🗨️  Telugu Message: {session_summary.get('telugu_message', 'N/A')}")
                    
                    return True
                else:
                    print(f"❌ Session end failed: {end_resp.json()}")
                    return False
                    
            else:
                print(f"❌ Session start failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Session error: {e}")
            return False
    
    def test_vocabulary_management(self):
        """Test vocabulary learning and practice"""
        print("\n📚 Testing Vocabulary Management...")
        
        try:
            # Get user's vocabulary
            response = self.session.get(f"{BASE_URL}/api/personalization/vocabulary")
            
            if response.status_code == 200:
                data = response.json()
                vocabulary = data['vocabulary']
                
                print(f"✅ Retrieved {len(vocabulary)} vocabulary words")
                
                if vocabulary:
                    # Test practicing a word
                    first_word = vocabulary[0]
                    vocab_id = first_word['id']
                    
                    print(f"   📝 Practicing word: {first_word['english_word']} = {first_word['telugu_translation']}")
                    
                    practice_data = {
                        "correct": True,
                        "practice_type": "flashcard"
                    }
                    
                    practice_resp = self.session.post(f"{BASE_URL}/api/personalization/vocabulary/{vocab_id}/practice", 
                                                    json=practice_data)
                    
                    if practice_resp.status_code == 200:
                        practice_result = practice_resp.json()['vocabulary']
                        print(f"   ✅ Practice recorded")
                        print(f"   📊 Success Rate: {practice_result['success_rate']}%")
                        print(f"   🏆 Mastery Level: {practice_result['mastery_level']}")
                        print(f"   🔢 Times Practiced: {practice_result['times_practiced']}")
                    else:
                        print(f"   ❌ Practice failed: {practice_resp.json()}")
                
                return True
            else:
                print(f"❌ Vocabulary retrieval failed: {response.json()}")
                return False
                
        except Exception as e:
            print(f"❌ Vocabulary error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all personalization tests"""
        print("🚀 Starting Personalization Features Test Suite")
        print("=" * 60)
        
        # Authenticate
        if not self.authenticate():
            print("❌ Authentication failed. Stopping tests.")
            return
        
        # Test all phases
        tests = [
            ("Goal Setting", self.test_goal_setting),
            ("Proficiency Assessment", self.test_proficiency_assessment),
            ("Personalized Dashboard", self.test_personalized_dashboard),
            ("Learning Session", self.test_learning_session),
            ("Vocabulary Management", self.test_vocabulary_management)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - ERROR: {e}")
            
            print("-" * 40)
        
        print(f"\n📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All personalization features are working correctly!")
            print("\n🎯 The 4-Phase Learning Journey is ready:")
            print("   Phase 1: ✅ Goal Setting & Onboarding")
            print("   Phase 2: ✅ Proficiency Assessment")
            print("   Phase 3: ✅ Personalized Learning Sessions") 
            print("   Phase 4: ✅ Vocabulary Mastery & Progress Tracking")
        else:
            print(f"⚠️  {total - passed} tests failed. Please check the logs above.")

if __name__ == "__main__":
    tester = PersonalizationTester()
    tester.run_all_tests()