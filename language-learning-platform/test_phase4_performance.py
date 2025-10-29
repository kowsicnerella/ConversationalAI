"""
Phase 4: Performance Tracking Test Suite
Comprehensive tests for all performance tracking features
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "native_language": "telugu",
    "target_language": "english"
}


class Phase4PerformanceTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        self.activity_id = None
    
    def login(self):
        """Login and get JWT token"""
        print("\n1. Testing Login...")
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            print(f"✓ Login successful. User ID: {self.user_id}")
            return True
        else:
            print(f"✗ Login failed: {response.json()}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_listening_performance(self):
        """Test listening performance tracking"""
        print("\n2. Testing Listening Performance Tracking...")
        
        performance_data = {
            "activity_id": 1,
            "session_id": "test-session-001",
            "audio_duration": 120.5,
            "audio_url": "https://example.com/audio.mp3",
            "accent_type": "american",
            "speed_factor": 1.0,
            "topic": "Travel and Tourism",
            "difficulty_level": "intermediate",
            "comprehension_score": 85.5,
            "accuracy_percentage": 80.0,
            "playback_count": 2,
            "pause_points": [30.5, 45.2, 90.1],
            "replay_sections": [[20, 35], [80, 95]],
            "difficult_segments": [{"start": 30, "end": 40, "reason": "fast speech"}],
            "difficult_words": ["itinerary", "accommodation"],
            "new_vocabulary": ["excursion", "destination"],
            "context_understanding": 85.0,
            "inference_ability": 75.0,
            "questions_data": {
                "questions": [
                    {"id": 1, "text": "What is the main topic?", "answer": "Travel"}
                ]
            },
            "total_questions": 10,
            "correct_answers": 8,
            "time_to_complete": 300,
            "avg_time_per_question": 30.0,
            "weak_phonemes": ["th", "r"],
            "accent_adaptation": 70.0,
            "ai_feedback": "Great progress! Focus on improving recognition of 'th' sound.",
            "improvement_suggestions": [
                "Practice with faster audio",
                "Focus on phoneme recognition"
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/performance/listening",
            headers=self.get_headers(),
            json=performance_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Listening performance tracked successfully")
            print(f"  Score: {data['performance']['comprehension_score']}%")
            print(f"  Mastery Level: {data['performance']['mastery_level']}")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_speaking_performance(self):
        """Test speaking performance tracking"""
        print("\n3. Testing Speaking Performance Tracking...")
        
        performance_data = {
            "activity_id": 2,
            "session_id": "test-session-002",
            "speaking_type": "conversation",
            "topic": "Job Interview",
            "scenario": "Introducing yourself in a professional setting",
            "difficulty_level": "advanced",
            "audio_url": "https://example.com/recording.mp3",
            "recording_duration": 120.0,
            "transcript": "Hello, my name is John. I have five years of experience in software development.",
            "expected_content": "Professional self-introduction",
            "pronunciation_accuracy": 88.0,
            "fluency_score": 82.0,
            "grammar_score": 90.0,
            "vocabulary_richness": 75.0,
            "overall_score": 83.75,
            "words_per_minute": 120.0,
            "speaking_rate": "normal",
            "hesitation_count": 3,
            "filler_words": ["um", "uh"],
            "filler_word_count": 2,
            "pause_analysis": {"avg_pause_length": 0.5, "total_pauses": 8},
            "mispronounced_words": ["development"],
            "phoneme_errors": ["th"],
            "accent_score": 85.0,
            "intonation_score": 80.0,
            "grammar_errors": [],
            "grammar_error_count": 0,
            "vocabulary_used": ["experience", "professional", "development"],
            "advanced_vocabulary_count": 3,
            "vocabulary_appropriateness": 90.0,
            "confidence_level": 85.0,
            "volume_consistency": 88.0,
            "emotional_expression": 75.0,
            "content_relevance": 95.0,
            "coherence_score": 90.0,
            "task_completion": 100.0,
            "ai_feedback": "Excellent grammar and vocabulary! Work on reducing filler words.",
            "pronunciation_tips": ["Practice 'th' sound", "Work on word stress"],
            "grammar_corrections": [],
            "vocabulary_suggestions": ["Consider using 'expertise' instead of 'experience'"],
            "improvement_areas": ["Reduce hesitations", "Improve fluency"],
            "practice_needed": ["Phoneme practice", "Fluency drills"]
        }
        
        response = requests.post(
            f"{self.base_url}/performance/speaking",
            headers=self.get_headers(),
            json=performance_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Speaking performance tracked successfully")
            print(f"  Overall Score: {data['performance']['overall_score']}%")
            print(f"  Pronunciation: {data['performance']['pronunciation_accuracy']}%")
            print(f"  Fluency: {data['performance']['fluency_score']}%")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_reading_performance(self):
        """Test reading performance tracking"""
        print("\n4. Testing Reading Performance Tracking...")
        
        performance_data = {
            "activity_id": 3,
            "session_id": "test-session-003",
            "text_title": "The Benefits of Learning Languages",
            "text_type": "article",
            "topic": "Education",
            "difficulty_level": "intermediate",
            "word_count": 500,
            "text_complexity": 8.5,
            "reading_time_seconds": 180,
            "reading_speed_wpm": 166,
            "speed_rating": "average",
            "target_speed_wpm": 200,
            "comprehension_score": 88.0,
            "accuracy_percentage": 85.0,
            "literal_comprehension": 90.0,
            "inferential_comprehension": 85.0,
            "critical_comprehension": 80.0,
            "vocabulary_lookups": ["cognitive", "proficiency"],
            "lookup_count": 2,
            "re_read_sections": [[100, 150]],
            "re_read_count": 1,
            "time_per_paragraph": [30, 40, 35, 40, 35],
            "questions_data": {
                "questions": [
                    {"id": 1, "text": "What is the main benefit?", "answer": "Cognitive improvement"}
                ]
            },
            "total_questions": 8,
            "correct_answers": 7,
            "time_per_question": [20, 25, 30, 22, 28, 25, 30, 20],
            "avg_time_per_question": 25.0,
            "new_vocabulary": ["cognitive", "proficiency", "bilingual"],
            "unknown_words": ["cognitive"],
            "vocabulary_coverage": 95.0,
            "main_idea_understanding": 90.0,
            "detail_retention": 85.0,
            "inference_ability": 82.0,
            "context_clue_usage": 88.0,
            "ai_feedback": "Good comprehension! Try to increase reading speed gradually.",
            "reading_strategies": ["skimming", "context clues"],
            "improvement_suggestions": [
                "Practice speed reading techniques",
                "Expand vocabulary in education domain"
            ],
            "vocabulary_to_study": ["cognitive", "proficiency"]
        }
        
        response = requests.post(
            f"{self.base_url}/performance/reading",
            headers=self.get_headers(),
            json=performance_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Reading performance tracked successfully")
            print(f"  Comprehension: {data['performance']['comprehension_score']}%")
            print(f"  Reading Speed: {data['performance']['reading_speed_wpm']} WPM")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_writing_performance(self):
        """Test writing performance tracking"""
        print("\n5. Testing Writing Performance Tracking...")
        
        performance_data = {
            "activity_id": 4,
            "session_id": "test-session-004",
            "writing_type": "essay",
            "topic": "The Impact of Technology on Education",
            "prompt": "Write an essay discussing how technology has changed education",
            "difficulty_level": "advanced",
            "target_word_count": 300,
            "content": "Technology has revolutionized education in many ways...",
            "word_count": 320,
            "character_count": 1856,
            "paragraph_count": 4,
            "sentence_count": 18,
            "overall_score": 85.0,
            "grammar_score": 88.0,
            "vocabulary_score": 82.0,
            "coherence_score": 86.0,
            "task_achievement": 90.0,
            "grammar_errors": [
                {"error": "subject-verb agreement", "location": "paragraph 2"}
            ],
            "grammar_error_count": 1,
            "error_types": {"agreement": 1},
            "spelling_errors": [],
            "spelling_error_count": 0,
            "punctuation_errors": [],
            "punctuation_error_count": 0,
            "vocabulary_used": ["revolutionized", "impact", "transform"],
            "unique_words": 180,
            "advanced_vocabulary": ["revolutionized", "facilitate", "enhance"],
            "advanced_vocabulary_count": 3,
            "vocabulary_diversity": 85.0,
            "vocabulary_appropriateness": 90.0,
            "repetitive_words": ["technology"],
            "sentence_lengths": [15, 12, 18, 16, 14, 20, 13, 17, 15, 19, 14, 16, 18, 15, 17, 16, 14, 18],
            "avg_sentence_length": 16.2,
            "sentence_variety": 88.0,
            "simple_sentences": 6,
            "compound_sentences": 7,
            "complex_sentences": 5,
            "sentence_complexity": 82.0,
            "paragraph_organization": 90.0,
            "transition_usage": 85.0,
            "topic_consistency": 92.0,
            "argument_development": 88.0,
            "originality_score": 80.0,
            "depth_of_content": 85.0,
            "relevance_to_prompt": 95.0,
            "supporting_evidence": 82.0,
            "writing_time_minutes": 25,
            "revision_count": 2,
            "edit_history": ["Added introduction", "Improved conclusion"],
            "planning_time": 5,
            "ai_feedback": "Excellent essay with strong arguments and good structure.",
            "strengths": ["Clear thesis", "Good examples", "Strong vocabulary"],
            "areas_for_improvement": ["Add more transitions", "Vary sentence structure"],
            "grammar_corrections": [{"original": "students has", "correction": "students have"}],
            "vocabulary_suggestions": ["Consider using 'transform' instead of 'change'"],
            "structural_suggestions": ["Add topic sentence to paragraph 3"],
            "target_skills": ["Advanced transitions", "Complex sentence structures"]
        }
        
        response = requests.post(
            f"{self.base_url}/performance/writing",
            headers=self.get_headers(),
            json=performance_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Writing performance tracked successfully")
            print(f"  Overall Score: {data['performance']['overall_score']}%")
            print(f"  Grammar: {data['performance']['grammar_score']}%")
            print(f"  Vocabulary: {data['performance']['vocabulary_score']}%")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_real_world_performance(self):
        """Test real-world scenario performance tracking"""
        print("\n6. Testing Real-World Performance Tracking...")
        
        performance_data = {
            "activity_id": 5,
            "session_id": "test-session-005",
            "scenario_type": "email",
            "industry": "business",
            "context": "Responding to a client inquiry",
            "difficulty_level": "advanced",
            "task_description": "Write a professional email to a client",
            "expected_outcomes": ["Professional tone", "Clear response", "Call to action"],
            "user_response": "Dear Mr. Smith, Thank you for your inquiry...",
            "response_format": "written",
            "overall_score": 88.0,
            "task_completion": 95.0,
            "appropriateness_score": 90.0,
            "professional_language_use": 92.0,
            "cultural_awareness": 85.0,
            "clarity_score": 90.0,
            "persuasiveness": 82.0,
            "diplomacy_score": 88.0,
            "engagement_quality": 85.0,
            "vocabulary_appropriateness": 90.0,
            "grammar_accuracy": 95.0,
            "register_appropriateness": 92.0,
            "idiomatic_usage": 80.0,
            "email_etiquette_score": 95.0,
            "time_management": 90.0,
            "response_time_seconds": 600,
            "expected_time_seconds": 720,
            "strengths": ["Professional tone", "Clear structure", "Good closing"],
            "weaknesses": ["Could add more details"],
            "mistakes_made": [],
            "best_practices_followed": ["Proper greeting", "Clear subject line"],
            "best_practices_missed": ["Could include signature block"],
            "ai_feedback": "Excellent professional email with appropriate tone and structure.",
            "improvement_suggestions": ["Add contact information", "Include call to action"],
            "alternative_approaches": ["Could start with appreciation"],
            "vocabulary_suggestions": ["Consider 'regarding' instead of 'about'"],
            "phrase_suggestions": ["'I would be happy to assist' is more professional"],
            "skills_demonstrated": ["Professional writing", "Business etiquette"],
            "skills_to_develop": ["Advanced persuasion techniques"],
            "real_world_readiness": 90.0,
            "confidence_level": 85.0
        }
        
        response = requests.post(
            f"{self.base_url}/performance/real-world",
            headers=self.get_headers(),
            json=performance_data
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Real-world performance tracked successfully")
            print(f"  Overall Score: {data['performance']['overall_score']}%")
            print(f"  Professional Language: {data['performance']['professional_language_use']}%")
            print(f"  Real-world Readiness: {data['performance']['real_world_readiness']}%")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_skill_trajectory(self):
        """Test skill trajectory analysis"""
        print("\n7. Testing Skill Trajectory Analysis...")
        
        response = requests.get(
            f"{self.base_url}/performance/trajectory/listening",
            headers=self.get_headers(),
            params={"time_window_days": 30}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Skill trajectory retrieved successfully")
            print(f"  Skill: {data.get('skill_domain')}")
            print(f"  Current Level: {data.get('current_level')}")
            print(f"  Mastery Status: {data.get('mastery_status')}")
            if data.get('trend'):
                print(f"  Trend: {data['trend'].get('direction')} ({data['trend'].get('velocity')})")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_learning_patterns(self):
        """Test learning pattern identification"""
        print("\n8. Testing Learning Pattern Identification...")
        
        response = requests.get(
            f"{self.base_url}/performance/patterns",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Learning patterns identified successfully")
            if data.get('time_patterns'):
                print(f"  Best Learning Time: {data['time_patterns'].get('best_time')}")
            if data.get('activity_preferences'):
                print(f"  Best Activity Type: {data['activity_preferences'].get('best_performing_type')}")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_mastery_prediction(self):
        """Test mastery timeline prediction"""
        print("\n9. Testing Mastery Timeline Prediction...")
        
        response = requests.get(
            f"{self.base_url}/performance/mastery-prediction/listening",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Mastery prediction retrieved successfully")
            print(f"  Current Level: {data.get('current_level')}")
            print(f"  Estimated Days to Mastery: {data.get('estimated_days')}")
            print(f"  Confidence: {data.get('confidence_level')}")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_performance_dashboard(self):
        """Test comprehensive performance dashboard"""
        print("\n10. Testing Performance Dashboard...")
        
        response = requests.get(
            f"{self.base_url}/performance/dashboard",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Performance dashboard retrieved successfully")
            print(f"  Skill Trajectories: {len(data.get('skill_overview', []))}")
            print(f"  Mastery Predictions: {len(data.get('mastery_predictions', {}))}")
            return True
        else:
            print(f"✗ Failed: {response.json()}")
            return False
    
    def test_performance_history(self):
        """Test performance history retrieval"""
        print("\n11. Testing Performance History...")
        
        endpoints = [
            'listening',
            'speaking',
            'reading',
            'writing',
            'real-world'
        ]
        
        success_count = 0
        for endpoint in endpoints:
            response = requests.get(
                f"{self.base_url}/performance/history/{endpoint}",
                headers=self.get_headers(),
                params={"limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ {endpoint.title()} history: {len(data.get('performances', []))} records")
                success_count += 1
            else:
                print(f"  ✗ {endpoint.title()} history failed")
        
        return success_count == len(endpoints)
    
    def run_all_tests(self):
        """Run all Phase 4 tests"""
        print("="*60)
        print("PHASE 4: COMPREHENSIVE PERFORMANCE TRACKING TEST SUITE")
        print("="*60)
        
        results = []
        
        # Login first
        if not self.login():
            print("\n❌ LOGIN FAILED - Cannot proceed with tests")
            return
        
        # Run all tests
        tests = [
            ("Listening Performance", self.test_listening_performance),
            ("Speaking Performance", self.test_speaking_performance),
            ("Reading Performance", self.test_reading_performance),
            ("Writing Performance", self.test_writing_performance),
            ("Real-World Performance", self.test_real_world_performance),
            ("Skill Trajectory", self.test_skill_trajectory),
            ("Learning Patterns", self.test_learning_patterns),
            ("Mastery Prediction", self.test_mastery_prediction),
            ("Performance Dashboard", self.test_performance_dashboard),
            ("Performance History", self.test_performance_history),
        ]
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"\n✗ {test_name} test crashed: {str(e)}")
                results.append((test_name, False))
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status} - {test_name}")
        
        print("\n" + "="*60)
        print(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print("="*60)
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Phase 4 implementation is working correctly!")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed. Please review the errors above.")


if __name__ == "__main__":
    tester = Phase4PerformanceTester()
    tester.run_all_tests()
