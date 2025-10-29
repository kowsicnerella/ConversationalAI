"""
Test script to verify end-to-end data persistence for activity generation and completion.

Tests:
1. Generate activity via /next-activity
2. Verify Activity record exists in database
3. Complete activity with activity_id and user_responses
4. Verify UserActivityLog record exists in database
5. Verify all fields are properly populated
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def login_user():
    """Login and get JWT token"""
    print_section("STEP 1: Login User")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ Login successful")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def generate_activity(token):
    """Generate next activity"""
    print_section("STEP 2: Generate Next Activity")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/learning-path/next-activity",
        headers=headers,
        json={}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Activity generated successfully")
        
        # Extract activity details
        activity_data = data.get('data', {}).get('activity', {})
        activity_id = data.get('data', {}).get('activity_id')
        node_id = activity_data.get('learning_node', {}).get('node_id')
        
        print(f"\n📋 Activity Details:")
        print(f"  Activity ID: {activity_id}")
        print(f"  Node ID: {node_id}")
        print(f"  Activity Type: {activity_data.get('activity_type')}")
        print(f"  Title: {activity_data.get('activity_title')}")
        print(f"  Can Resume: {data.get('data', {}).get('can_resume')}")
        
        # Show first exercise
        exercises = activity_data.get('exercises', [])
        if exercises:
            print(f"\n📝 First Exercise Preview:")
            print(f"  Type: {exercises[0].get('type')}")
            print(f"  Question: {exercises[0].get('question')[:80]}...")
        
        return {
            'activity_id': activity_id,
            'node_id': node_id,
            'activity_data': activity_data
        }
    else:
        print(f"❌ Activity generation failed: {response.status_code}")
        print(response.text)
        return None

def verify_activity_in_database(activity_id):
    """Verify activity was saved to database"""
    print_section("STEP 3: Verify Activity in Database")
    
    try:
        # Import database models
        import sys
        sys.path.append('d:/ConversationalAI/language-learning-platform')
        
        from app import create_app
        from app.models import Activity
        
        app = create_app()
        
        with app.app_context():
            activity = Activity.query.filter_by(id=activity_id).first()
            
            if activity:
                print(f"✅ Activity found in database!")
                print(f"\n📊 Database Record:")
                print(f"  ID: {activity.id}")
                print(f"  User ID: {activity.user_id}")
                print(f"  Learning Node ID: {activity.learning_node_id}")
                print(f"  Activity Type: {activity.activity_type}")
                print(f"  Status: {activity.status}")
                print(f"  Created At: {activity.created_at}")
                
                # Check content
                content = activity.content
                if content:
                    print(f"\n📝 Stored Content:")
                    print(f"  Exercises: {len(content.get('exercises', []))} exercises")
                    print(f"  Has Instructions: {'instructions' in content}")
                    print(f"  Has Tips: {'tips' in content}")
                
                # Check metadata
                metadata = activity.generation_metadata
                if metadata:
                    print(f"\n🔧 Generation Metadata:")
                    print(f"  AI Model: {metadata.get('ai_model')}")
                    print(f"  Generated At: {metadata.get('generated_at')}")
                    print(f"  Personalized: {metadata.get('personalization_applied', False)}")
                
                return True
            else:
                print(f"❌ Activity NOT found in database!")
                return False
                
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def complete_activity(token, activity_id, node_id):
    """Complete activity with responses"""
    print_section("STEP 4: Complete Activity")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Sample user responses
    user_responses = {
        "exercise_1": {
            "question": "Translate: Hello",
            "user_answer": "Hola",
            "correct_answer": "Hola",
            "is_correct": True,
            "time_spent": 5.2
        },
        "exercise_2": {
            "question": "Translate: Goodbye",
            "user_answer": "Adiós",
            "correct_answer": "Adiós",
            "is_correct": True,
            "time_spent": 4.8
        },
        "exercise_3": {
            "question": "Translate: Please",
            "user_answer": "Por favor",
            "correct_answer": "Por favor",
            "is_correct": True,
            "time_spent": 6.1
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/learning-path/complete-activity",
        headers=headers,
        json={
            "activity_id": activity_id,
            "learning_node_id": node_id,
            "performance_score": 0.95,
            "time_spent_seconds": 180,
            "user_responses": user_responses
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Activity completed successfully")
        print(f"\n📈 Completion Response:")
        print(f"  Success: {data.get('success')}")
        print(f"  Message: {data.get('message')}")
        print(f"  Activity Logged: {data.get('activity_logged', False)}")
        print(f"  Next Node: {data.get('next_node', {}).get('node_id')}")
        
        return True
    else:
        print(f"❌ Activity completion failed: {response.status_code}")
        print(response.text)
        return False

def verify_activity_log_in_database(activity_id):
    """Verify activity log was saved to database"""
    print_section("STEP 5: Verify Activity Log in Database")
    
    try:
        # Import database models
        import sys
        sys.path.append('d:/ConversationalAI/language-learning-platform')
        
        from app import create_app
        from app.models import UserActivityLog
        
        app = create_app()
        
        with app.app_context():
            log = UserActivityLog.query.filter_by(activity_id=activity_id).first()
            
            if log:
                print(f"✅ Activity log found in database!")
                print(f"\n📊 Log Record:")
                print(f"  ID: {log.id}")
                print(f"  Activity ID: {log.activity_id}")
                print(f"  User ID: {log.user_id}")
                print(f"  Performance Score: {log.performance_score}")
                print(f"  Time Spent: {log.time_spent_seconds}s")
                print(f"  Completed At: {log.completed_at}")
                
                print(f"\n📈 Performance Metrics:")
                print(f"  Mastery Level: {log.mastery_level}")
                print(f"  Accuracy Score: {log.accuracy_score}")
                print(f"  Confidence Score: {log.confidence_score}")
                print(f"  Needs Review: {log.needs_review}")
                
                print(f"\n🔄 Spaced Repetition:")
                print(f"  Next Review Date: {log.next_review_date}")
                print(f"  Review Count: {log.review_count}")
                
                # Check user responses
                if log.user_responses:
                    print(f"\n✍️ User Responses Stored:")
                    print(f"  Number of responses: {len(log.user_responses)}")
                    for key, response in list(log.user_responses.items())[:2]:  # Show first 2
                        print(f"  {key}: {response.get('is_correct')} - {response.get('time_spent')}s")
                
                return True
            else:
                print(f"❌ Activity log NOT found in database!")
                return False
                
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_full_test():
    """Run complete end-to-end test"""
    print("\n" + "█"*80)
    print("  DATA PERSISTENCE END-TO-END TEST")
    print("  Testing: Activity Generation → Database Save → Completion → Log Save")
    print("█"*80)
    
    results = {
        "login": False,
        "generate": False,
        "verify_activity": False,
        "complete": False,
        "verify_log": False
    }
    
    # Step 1: Login
    token = login_user()
    if not token:
        print("\n❌ TEST FAILED: Could not login")
        return results
    results["login"] = True
    
    # Step 2: Generate activity
    activity_info = generate_activity(token)
    if not activity_info or not activity_info.get('activity_id'):
        print("\n❌ TEST FAILED: Could not generate activity or no activity_id returned")
        return results
    results["generate"] = True
    
    activity_id = activity_info['activity_id']
    node_id = activity_info['node_id']
    
    # Step 3: Verify activity in database
    results["verify_activity"] = verify_activity_in_database(activity_id)
    
    # Step 4: Complete activity
    results["complete"] = complete_activity(token, activity_id, node_id)
    
    # Step 5: Verify activity log in database
    if results["complete"]:
        results["verify_log"] = verify_activity_log_in_database(activity_id)
    
    # Final report
    print_section("FINAL TEST RESULTS")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\n{'✅' if results['login'] else '❌'} Login User")
    print(f"{'✅' if results['generate'] else '❌'} Generate Activity (with activity_id)")
    print(f"{'✅' if results['verify_activity'] else '❌'} Verify Activity in Database")
    print(f"{'✅' if results['complete'] else '❌'} Complete Activity")
    print(f"{'✅' if results['verify_log'] else '❌'} Verify Activity Log in Database")
    
    print(f"\n{'='*80}")
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED! ({passed_tests}/{total_tests})")
        print(f"✅ Data persistence is working correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed_tests}/{total_tests} passed)")
        print(f"❌ Please review failed tests above")
    print(f"{'='*80}\n")
    
    return results

if __name__ == "__main__":
    try:
        results = run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
