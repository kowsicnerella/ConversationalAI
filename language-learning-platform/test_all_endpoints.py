#!/usr/bin/env python3
"""
Comprehensive Test Script for Telugu-English Learning Platform REST API
Tests all endpoints including chat, courses, media, analytics, and enhanced user management.
"""

import requests
import json
import time
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.auth_token = None
        
    def set_auth_token(self, token):
        """Set authorization token for authenticated requests."""
        self.auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'
    
    def make_request(self, method, endpoint, data=None, files=None):
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        try:
            if files:
                # For file uploads, don't set Content-Type
                headers = {'Authorization': self.headers.get('Authorization', '')} if self.auth_token else {}
                response = requests.request(method, url, data=data, files=files, headers=headers)
            else:
                response = requests.request(method, url, json=data, headers=self.headers)
            
            print(f"\n{method} {endpoint}")
            print(f"Status: {response.status_code}")
            
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
                return response.status_code, result
            except:
                print(f"Raw Response: {response.text}")
                return response.status_code, response.text
                
        except Exception as e:
            print(f"Error making request: {str(e)}")
            return None, str(e)
    
    def test_health_check(self):
        """Test health check endpoint."""
        print("\n" + "="*50)
        print("TESTING HEALTH CHECK")
        print("="*50)
        return self.make_request('GET', '/health')
    
    def test_auth_endpoints(self):
        """Test authentication endpoints."""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("="*50)
        
        # Test user registration
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "native_language": "telugu",
            "proficiency_level": "beginner"
        }
        status, response = self.make_request('POST', '/api/auth/register', register_data)
        
        # Test user login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        status, response = self.make_request('POST', '/api/auth/login', login_data)
        
        if status == 200 and 'access_token' in response:
            self.set_auth_token(response['access_token'])
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed!")
            return False
        
        return True
    
    def test_user_endpoints(self):
        """Test enhanced user management endpoints."""
        print("\n" + "="*50)
        print("TESTING USER MANAGEMENT ENDPOINTS")
        print("="*50)
        
        # Test get profile
        self.make_request('GET', '/api/user/profile')
        
        # Test update settings
        settings_data = {
            "language_preference": "telugu",
            "difficulty_preference": "intermediate",
            "daily_goal_minutes": 30,
            "notification_settings": {
                "reminders": True,
                "achievements": True
            }
        }
        self.make_request('PUT', '/api/user/settings', settings_data)
        
        # Test get user statistics
        self.make_request('GET', '/api/user/statistics')
        
        # Test change password
        password_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        self.make_request('PUT', '/api/user/change-password', password_data)
    
    def test_chat_endpoints(self):
        """Test chat/conversation endpoints."""
        print("\n" + "="*50)
        print("TESTING CHAT & CONVERSATION ENDPOINTS")
        print("="*50)
        
        # Test get conversations
        self.make_request('GET', '/api/chat/conversations')
        
        # Test send message
        message_data = {
            "message": "Hello! I want to learn Telugu colors.",
            "conversation_type": "learning_chat"
        }
        self.make_request('POST', '/api/chat/send-message', message_data)
        
        # Test quick chat
        quick_chat_data = {
            "message": "How do you say 'thank you' in Telugu?",
            "context": "polite_expressions"
        }
        self.make_request('POST', '/api/chat/quick-chat', quick_chat_data)
        
        # Test get chat suggestions
        self.make_request('GET', '/api/chat/suggestions?topic=greetings')
        
        # Test conversation feedback
        feedback_data = {
            "conversation_id": 1,
            "rating": 5,
            "feedback_text": "Very helpful conversation!"
        }
        self.make_request('POST', '/api/chat/feedback', feedback_data)
    
    def test_course_endpoints(self):
        """Test course/learning path endpoints."""
        print("\n" + "="*50)
        print("TESTING COURSE & LEARNING PATH ENDPOINTS")
        print("="*50)
        
        # Test get learning paths
        self.make_request('GET', '/api/courses/learning-paths')
        
        # Test get course details
        self.make_request('GET', '/api/courses/learning-paths/1')
        
        # Test enroll in learning path
        enroll_data = {"learning_path_id": 1}
        self.make_request('POST', '/api/courses/enroll', enroll_data)
        
        # Test get enrollment progress
        self.make_request('GET', '/api/courses/enrollment/1/progress')
        
        # Test start activity
        start_activity_data = {
            "enrollment_id": 1,
            "activity_id": 1
        }
        self.make_request('POST', '/api/courses/start-activity', start_activity_data)
        
        # Test complete activity
        complete_activity_data = {
            "enrollment_id": 1,
            "activity_id": 1,
            "score": 85,
            "time_spent_minutes": 10
        }
        self.make_request('POST', '/api/courses/complete-activity', complete_activity_data)
    
    def test_media_endpoints(self):
        """Test media upload and processing endpoints."""
        print("\n" + "="*50)
        print("TESTING MEDIA UPLOAD & PROCESSING ENDPOINTS")
        print("="*50)
        
        # Test upload image (simulated)
        # Note: In real testing, you'd provide actual image files
        print("Simulating image upload...")
        self.make_request('GET', '/api/media/files')  # Test file listing instead
        
        # Test generate pronunciation exercise
        pronunciation_data = {
            "target_word": "నమస్కారం",
            "difficulty_level": "beginner"
        }
        self.make_request('POST', '/api/media/pronunciation-exercise', pronunciation_data)
        
        # Test get media files
        self.make_request('GET', '/api/media/files')
    
    def test_analytics_endpoints(self):
        """Test analytics and reporting endpoints."""
        print("\n" + "="*50)
        print("TESTING ANALYTICS & REPORTING ENDPOINTS")
        print("="*50)
        
        # Test dashboard summary
        self.make_request('GET', '/api/analytics/dashboard-summary')
        
        # Test learning trends
        self.make_request('GET', '/api/analytics/learning-trends?days=30')
        
        # Test performance analysis
        self.make_request('GET', '/api/analytics/performance-analysis')
        
        # Test vocabulary analytics
        self.make_request('GET', '/api/analytics/vocabulary-analytics')
        
        # Test export progress report
        self.make_request('GET', '/api/analytics/export/progress-report?type=summary')
    
    def test_existing_endpoints(self):
        """Test existing activity, gamification, and personalization endpoints."""
        print("\n" + "="*50)
        print("TESTING EXISTING ENDPOINTS")
        print("="*50)
        
        # Test activity generation
        activity_data = {
            "activity_type": "vocabulary_quiz",
            "difficulty": "beginner",
            "topic": "greetings"
        }
        self.make_request('POST', '/api/activity/generate', activity_data)
        
        # Test gamification profile
        self.make_request('GET', '/api/gamification/profile')
        
        # Test personalization insights
        self.make_request('GET', '/api/personalization/insights')
    
    def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting Comprehensive API Testing...")
        print(f"Base URL: {self.base_url}")
        print(f"Time: {datetime.now()}")
        
        # Test health check first
        self.test_health_check()
        
        # Test authentication
        if not self.test_auth_endpoints():
            print("❌ Authentication failed - stopping tests")
            return
        
        # Test all endpoint categories
        self.test_user_endpoints()
        self.test_chat_endpoints()
        self.test_course_endpoints()
        self.test_media_endpoints()
        self.test_analytics_endpoints()
        self.test_existing_endpoints()
        
        print("\n" + "="*50)
        print("🎉 API TESTING COMPLETED!")
        print("="*50)
        print("\nNote: Some endpoints may return 404 or validation errors")
        print("because they depend on database data that may not exist yet.")
        print("This is expected for a new installation.")

def main():
    """Main function to run the tests."""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()