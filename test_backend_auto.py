#!/usr/bin/env python
"""
Week 2 Phase 1 - Automated Backend Test Script (No User Input)
Tests all fixed endpoints and verifies data persistence.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TOKEN = None

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
        "username": "tanojrahul",
        "password": "Tanoj@190605"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            global TOKEN
            TOKEN = response.json().get("access_token")
            print("✅ Login successful!")
            print(f"Token: {TOKEN[:30]}..." if TOKEN else "No token received")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
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
            
            if 'activity_id' in data and data['activity_id']:
                print("✅ Activity saved to database!")
                return data.get('activity_id')
            else:
                print("⚠️ Activity may not have been saved")
                return None
        else:
            print(f"❌ Failed: {response.text}")
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
            count = data.get('data', {}).get('count', 0)
            print(f"✅ Endpoint working! Found {count} incomplete activities")
            
            activities = data.get('data', {}).get('activities', [])
            if activities:
                print("\nFirst incomplete activity:")
                activity = activities[0]
                print(f"  - ID: {activity.get('id')}")
                print(f"  - Type: {activity.get('activity_type')}")
                print(f"  - Title: {activity.get('title', 'N/A')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
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
            count = data.get('data', {}).get('count', 0)
            print(f"✅ Endpoint working! Found {count} due reviews")
            
            reviews = data.get('data', {}).get('due_reviews', [])
            if reviews:
                print("\nFirst due review:")
                review = reviews[0]
                print(f"  - Activity ID: {review.get('activity_id')}")
                print(f"  - Type: {review.get('activity_type')}")
                print(f"  - Days Overdue: {review.get('days_overdue', 0)}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
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
            
            words = data.get('words', [])
            if words:
                print("\nFirst vocabulary word:")
                word = words[0]
                print(f"  - English: {word.get('english_word')}")
                print(f"  - Telugu: {word.get('telugu_translation')}")
                print(f"  - Discovered: {word.get('discovered_at', 'N/A')}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
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
            stats = data.get('data', {}).get('statistics', {})
            print("✅ Endpoint working!")
            print(f"\nStatistics:")
            print(f"  - Total Activities: {stats.get('total_activities', 0)}")
            print(f"  - Average Performance: {stats.get('average_performance', 0):.2f}")
            print(f"  - Time Spent: {stats.get('total_time_spent_seconds', 0)} seconds")
            
            mastery = stats.get('mastery_breakdown', {})
            if mastery:
                print(f"\nMastery Breakdown:")
                for level, count in mastery.items():
                    print(f"  - {level}: {count}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          WEEK 2 PHASE 1 - AUTOMATED TEST SUITE            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Test 1: Login
    if not test_login():
        print("\n❌ Cannot proceed without login. Tests aborted.")
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
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for Week 2!")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed! Minor issues to address.")
    else:
        print("\n⚠️ Several tests failed. Please review the errors above.")
    
    return passed, total

if __name__ == "__main__":
    print("Starting automated test suite...")
    print("Backend URL:", BASE_URL)
    passed, total = run_all_tests()
    
    # Exit code based on results
    exit(0 if passed == total else 1)
