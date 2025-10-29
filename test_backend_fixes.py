#!/usr/bin/env python
"""
Week 2 Phase 1 - Comprehensive Backend Test Script
Tests all fixed endpoints and verifies data persistence.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TOKEN = None  # Will be set after login

def print_section(title):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_login():
    """Test 1: Login and get JWT token"""
    print_section("TEST 1: User Login")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "tanojrahul",  # Replace with your test username
        "password": "Tanoj@190605"  # Replace with your test password
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            global TOKEN
            TOKEN = response.json().get("access_token")
            print("✅ Login successful!")
            print(f"Token: {TOKEN[:20]}...")
            return True
        else:
            print(f"❌ Login failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_activity_generation():
    """Test 2: Generate activity and verify database persistence"""
    print_section("TEST 2: Activity Generation & Persistence")
    
    url = f"{BASE_URL}/api/learning-path/next-activity"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.post(url, headers=headers, json={})
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Activity generated successfully!")
            print(f"Activity Type: {data.get('activity_type')}")
            print(f"Activity ID: {data.get('activity_id')}")
            
            # Check for the LearningNode error
            if 'activity_id' in data and data['activity_id']:
                print("✅ Activity saved to database!")
            else:
                print("⚠️ Activity may not have been saved")
            
            return data.get('activity_id')
        else:
            print(f"❌ Failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_incomplete_activities():
    """Test 3: Get incomplete activities (was returning 422)"""
    print_section("TEST 3: Incomplete Activities Endpoint")
    
    url = f"{BASE_URL}/api/learning-path/activities/incomplete"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint working! Found {data['data']['count']} incomplete activities")
            
            if data['data']['activities']:
                print("\nFirst incomplete activity:")
                activity = data['data']['activities'][0]
                print(f"  - ID: {activity.get('id')}")
                print(f"  - Type: {activity.get('activity_type')}")
                print(f"  - Title: {activity.get('title')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_spaced_repetition():
    """Test 4: Get due reviews (was returning 422)"""
    print_section("TEST 4: Spaced Repetition Endpoint")
    
    url = f"{BASE_URL}/api/learning-path/spaced-repetition/due"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint working! Found {data['data']['count']} due reviews")
            
            if data['data']['due_reviews']:
                print("\nFirst due review:")
                review = data['data']['due_reviews'][0]
                print(f"  - Activity ID: {review.get('activity_id')}")
                print(f"  - Type: {review.get('activity_type')}")
                print(f"  - Days Overdue: {review.get('days_overdue')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_vocabulary_endpoint():
    """Test 5: Vocabulary endpoint (was throwing created_at error)"""
    print_section("TEST 5: Vocabulary Words Endpoint")
    
    url = f"{BASE_URL}/api/vocabulary/words"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('pagination', {}).get('total', 0)
            print(f"✅ Endpoint working! Found {total} vocabulary words")
            
            if data.get('words'):
                print("\nFirst vocabulary word:")
                word = data['words'][0]
                print(f"  - English: {word.get('english_word')}")
                print(f"  - Telugu: {word.get('telugu_translation')}")
                print(f"  - Discovered: {word.get('discovered_at')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_activity_history():
    """Test 6: Activity history endpoint"""
    print_section("TEST 6: Activity History Endpoint")
    
    url = f"{BASE_URL}/api/learning-path/activity-history"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stats = data['data']['statistics']
            print("✅ Endpoint working!")
            print(f"\nStatistics:")
            print(f"  - Total Activities: {stats.get('total_activities')}")
            print(f"  - Average Performance: {stats.get('average_performance', 0):.2f}")
            print(f"  - Time Spent: {stats.get('total_time_spent_seconds', 0)} seconds")
            print(f"\nMastery Breakdown:")
            for level, count in stats.get('mastery_breakdown', {}).items():
                print(f"  - {level}: {count}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          WEEK 2 PHASE 1 - BACKEND TEST SUITE              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Test 1: Login
    if not test_login():
        print("\n❌ Cannot proceed without login. Please check credentials.")
        return
    
    # Test 2: Activity Generation
    activity_id = test_activity_generation()
    results.append(("Activity Generation", activity_id is not None))
    
    # Test 3: Incomplete Activities
    results.append(("Incomplete Activities", test_incomplete_activities()))
    
    # Test 4: Spaced Repetition
    results.append(("Spaced Repetition", test_spaced_repetition()))
    
    # Test 5: Vocabulary
    results.append(("Vocabulary Words", test_vocabulary_endpoint()))
    
    # Test 6: Activity History
    results.append(("Activity History", test_activity_history()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for Week 2!")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                   BEFORE RUNNING TESTS                      ║
╠════════════════════════════════════════════════════════════╣
║  1. Make sure Flask server is running on port 5000         ║
║  2. Update TEST CREDENTIALS in the script:                 ║
║     - username: Your test user username                     ║
║     - password: Your test user password                     ║
║  3. Make sure you have at least one user account           ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    input("Press Enter to start tests...")
    run_all_tests()
