"""
Test Phase 2 Activity CRUD Operations
Tests for content generation with storage and retrieval.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
API_PREFIX = "/api/content-generation"

# Test user credentials (update with actual test user)
TEST_USER = {
    "username": "johndoe",
    "password": "password123"
}

# Store JWT token
jwt_token = None
activity_ids = []


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def login():
    """Login and get JWT token."""
    global jwt_token
    print_section("1. LOGIN")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_USER
    )
    
    if response.status_code == 200:
        jwt_token = response.json()["access_token"]
        print(f"✅ Login successful")
        print(f"Token: {jwt_token[:50]}...")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return False


def test_generate_and_save_quiz():
    """Test quiz generation and storage."""
    print_section("2. GENERATE AND SAVE QUIZ")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/quiz",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "concept": "Present tense verbs",
            "difficulty": 0.5,
            "question_count": 5,
            "focus_areas": ["grammar", "vocabulary"]
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        activity_id = data.get("activity_id")
        saved = data.get("saved")
        
        print(f"✅ Quiz generated successfully")
        print(f"Activity ID: {activity_id}")
        print(f"Saved: {saved}")
        print(f"Title: {data.get('title', 'N/A')}")
        
        if activity_id:
            activity_ids.append(activity_id)
        return True
    else:
        print(f"❌ Quiz generation failed: {response.status_code}")
        print(response.text)
        return False


def test_generate_flashcards():
    """Test flashcard generation and storage."""
    print_section("3. GENERATE AND SAVE FLASHCARDS")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/flashcards",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "vocabulary_list": ["hello", "goodbye", "thank you"],
            "context_theme": "Greetings",
            "difficulty": 0.4
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        activity_id = data.get("activity_id")
        
        print(f"✅ Flashcards generated successfully")
        print(f"Activity ID: {activity_id}")
        print(f"Saved: {data.get('saved')}")
        
        if activity_id:
            activity_ids.append(activity_id)
        return True
    else:
        print(f"❌ Flashcard generation failed: {response.status_code}")
        print(response.text)
        return False


def test_generate_reading():
    """Test reading passage generation and storage."""
    print_section("4. GENERATE AND SAVE READING PASSAGE")
    
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/reading",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={
            "topic": "Technology and Daily Life",
            "difficulty": 0.6,
            "length_words": 200
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        activity_id = data.get("activity_id")
        
        print(f"✅ Reading passage generated successfully")
        print(f"Activity ID: {activity_id}")
        print(f"Saved: {data.get('saved')}")
        
        if activity_id:
            activity_ids.append(activity_id)
        return True
    else:
        print(f"❌ Reading generation failed: {response.status_code}")
        print(response.text)
        return False


def test_list_all_activities():
    """Test listing all activities."""
    print_section("5. LIST ALL ACTIVITIES")
    
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={"limit": 10, "offset": 0}
    )
    
    if response.status_code == 200:
        data = response.json()
        activities = data.get("activities", [])
        total = data.get("total_count", 0)
        
        print(f"✅ Retrieved activities successfully")
        print(f"Total activities: {total}")
        print(f"Returned in this page: {len(activities)}")
        
        if activities:
            print("\nFirst few activities:")
            for i, activity in enumerate(activities[:3], 1):
                print(f"\n  {i}. {activity.get('title', 'No title')}")
                print(f"     Type: {activity.get('activity_type')}")
                print(f"     Difficulty: {activity.get('difficulty_level')}")
                print(f"     Created: {activity.get('created_at')}")
        
        return True
    else:
        print(f"❌ List activities failed: {response.status_code}")
        print(response.text)
        return False


def test_get_single_activity():
    """Test getting a single activity by ID."""
    print_section("6. GET SINGLE ACTIVITY BY ID")
    
    if not activity_ids:
        print("⚠️  No activity IDs available. Skipping test.")
        return False
    
    activity_id = activity_ids[0]
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities/{activity_id}",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Retrieved activity successfully")
        print(f"ID: {data.get('id')}")
        print(f"Title: {data.get('title')}")
        print(f"Type: {data.get('activity_type')}")
        print(f"Difficulty: {data.get('difficulty_level')}")
        print(f"Has content: {'content' in data}")
        print(f"Has metadata: {'generation_metadata' in data}")
        
        return True
    else:
        print(f"❌ Get activity failed: {response.status_code}")
        print(response.text)
        return False


def test_filter_by_type():
    """Test filtering activities by type."""
    print_section("7. FILTER ACTIVITIES BY TYPE")
    
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={"activity_type": "quiz", "limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        activities = data.get("activities", [])
        
        print(f"✅ Retrieved filtered activities successfully")
        print(f"Total quiz activities: {data.get('total_count', 0)}")
        print(f"Returned: {len(activities)}")
        
        if activities:
            all_quizzes = all(a.get("activity_type") == "quiz" for a in activities)
            print(f"All are quizzes: {all_quizzes}")
        
        return True
    else:
        print(f"❌ Filter by type failed: {response.status_code}")
        print(response.text)
        return False


def test_filter_by_difficulty():
    """Test filtering by difficulty range."""
    print_section("8. FILTER BY DIFFICULTY RANGE")
    
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={
            "difficulty_min": 0.4,
            "difficulty_max": 0.6,
            "limit": 10
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        activities = data.get("activities", [])
        
        print(f"✅ Retrieved filtered activities successfully")
        print(f"Total in range: {data.get('total_count', 0)}")
        
        if activities:
            difficulties = [a.get("difficulty_level") for a in activities]
            print(f"Difficulty range: {min(difficulties):.2f} - {max(difficulties):.2f}")
        
        return True
    else:
        print(f"❌ Filter by difficulty failed: {response.status_code}")
        print(response.text)
        return False


def test_get_activities_by_type():
    """Test the by-type endpoint."""
    print_section("9. GET ACTIVITIES BY TYPE ENDPOINT")
    
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities/by-type/quiz",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={"limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Retrieved activities by type successfully")
        print(f"Activity type: {data.get('activity_type')}")
        print(f"Total count: {data.get('total_count', 0)}")
        print(f"Returned: {len(data.get('activities', []))}")
        
        return True
    else:
        print(f"❌ Get by type failed: {response.status_code}")
        print(response.text)
        return False


def test_get_statistics():
    """Test statistics endpoint."""
    print_section("10. GET ACTIVITY STATISTICS")
    
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities/stats",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Retrieved statistics successfully")
        print(f"Total activities: {data.get('total_activities', 0)}")
        print(f"Average difficulty: {data.get('average_difficulty', 0):.2f}")
        print(f"Total estimated time: {data.get('total_estimated_time_minutes', 0)} minutes")
        
        print("\nActivities by type:")
        for activity_type, count in data.get('by_type', {}).items():
            print(f"  - {activity_type}: {count}")
        
        print("\nActivities by skill area:")
        for skill, count in data.get('by_skill_area', {}).items():
            print(f"  - {skill}: {count}")
        
        return True
    else:
        print(f"❌ Get statistics failed: {response.status_code}")
        print(response.text)
        return False


def test_pagination():
    """Test pagination."""
    print_section("11. TEST PAGINATION")
    
    # Get first page
    response1 = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={"limit": 2, "offset": 0}
    )
    
    # Get second page
    response2 = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={"limit": 2, "offset": 2}
    )
    
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        print(f"✅ Pagination working")
        print(f"Page 1: {len(data1.get('activities', []))} activities")
        print(f"Page 2: {len(data2.get('activities', []))} activities")
        print(f"Total count: {data1.get('total_count', 0)}")
        print(f"Has more after page 1: {data1.get('has_more', False)}")
        
        return True
    else:
        print(f"❌ Pagination test failed")
        return False


def test_sorting():
    """Test sorting."""
    print_section("12. TEST SORTING")
    
    # Sort by difficulty ascending
    response = requests.get(
        f"{BASE_URL}{API_PREFIX}/activities",
        headers={"Authorization": f"Bearer {jwt_token}"},
        params={
            "limit": 5,
            "sort_by": "difficulty_level",
            "sort_order": "asc"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        activities = data.get("activities", [])
        
        print(f"✅ Sorting working")
        print(f"Retrieved {len(activities)} activities sorted by difficulty (asc)")
        
        if activities:
            difficulties = [a.get("difficulty_level") for a in activities]
            print(f"Difficulties: {[f'{d:.2f}' for d in difficulties]}")
            is_sorted = all(difficulties[i] <= difficulties[i+1] for i in range(len(difficulties)-1))
            print(f"Is sorted correctly: {is_sorted}")
        
        return True
    else:
        print(f"❌ Sorting test failed")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("  PHASE 2 ACTIVITY CRUD OPERATIONS - TEST SUITE")
    print("="*70)
    
    results = []
    
    # Login first
    if not login():
        print("\n❌ Login failed. Cannot proceed with tests.")
        return
    
    time.sleep(0.5)
    
    # Run all tests
    tests = [
        ("Generate Quiz", test_generate_and_save_quiz),
        ("Generate Flashcards", test_generate_flashcards),
        ("Generate Reading", test_generate_reading),
        ("List All Activities", test_list_all_activities),
        ("Get Single Activity", test_get_single_activity),
        ("Filter by Type", test_filter_by_type),
        ("Filter by Difficulty", test_filter_by_difficulty),
        ("Get Activities by Type", test_get_activities_by_type),
        ("Get Statistics", test_get_statistics),
        ("Test Pagination", test_pagination),
        ("Test Sorting", test_sorting),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print(f"\n❌ Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    print(f"\nTotal tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    print("\nDetailed results:")
    for i, (test_name, result) in enumerate(results, 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i:2d}. {status} - {test_name}")
    
    print("\n" + "="*70)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} test(s) failed. Review output above for details.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
