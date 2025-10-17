#!/usr/bin/env python3
"""
Quick test script for Goal Setting & Personalization endpoints
Run this after starting the Flask backend to verify API functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "Test123!"


def print_response(response, description):
    """Helper to print formatted API response"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_goal_setting_flow():
    """Test the complete goal setting flow"""

    print("\n🚀 Starting Goal Setting & Personalization API Tests")
    print("=" * 60)

    # Step 1: Login to get token
    print("\n📝 Step 1: Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
    )

    if login_response.status_code != 200:
        print("❌ Login failed! Please ensure:")
        print("1. Backend is running (python app.py)")
        print(f"2. Test user exists with email: {TEST_USER_EMAIL}")
        print("3. Create test user if needed via registration endpoint")
        return

    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("✅ Login successful!")
    print(f"Token: {token[:20]}...")

    # Step 2: Save learning goals
    print("\n📝 Step 2: Saving learning goals...")
    goals_data = {"learning_focus": "conversational", "daily_time_goal": 30}

    goals_response = requests.post(
        f"{BASE_URL}/personalization/goals", json=goals_data, headers=headers
    )
    print_response(goals_response, "Save Learning Goals")

    if goals_response.status_code == 200:
        print("✅ Learning goals saved successfully!")
    else:
        print("❌ Failed to save learning goals")

    # Step 3: Save preferences
    print("\n📝 Step 3: Saving user preferences...")
    preferences_data = {
        "preferred_topics": ["Food", "Travel", "Work"],
        "learning_goal_type": "conversational",
        "notification_settings": {
            "daily_reminders": True,
            "achievements": True,
            "weekly_reports": False,
            "learning_tips": True,
        },
    }

    preferences_response = requests.post(
        f"{BASE_URL}/personalization/preferences",
        json=preferences_data,
        headers=headers,
    )
    print_response(preferences_response, "Save User Preferences")

    if preferences_response.status_code == 200:
        print("✅ User preferences saved successfully!")
        print("   Topics:", preferences_data["preferred_topics"])
        print("   Goal Type:", preferences_data["learning_goal_type"])
        print("   Notifications:", preferences_data["notification_settings"])
    else:
        print("❌ Failed to save user preferences")

    # Step 4: Retrieve preferences
    print("\n📝 Step 4: Retrieving saved preferences...")
    get_preferences_response = requests.get(
        f"{BASE_URL}/personalization/preferences", headers=headers
    )
    print_response(get_preferences_response, "Get User Preferences")

    if get_preferences_response.status_code == 200:
        saved_prefs = get_preferences_response.json().get("preferences", {})
        print("✅ Preferences retrieved successfully!")
        print(f"   Saved Topics: {saved_prefs.get('preferred_topics', [])}")
        print(f"   Saved Goal: {saved_prefs.get('learning_goal_type', 'N/A')}")
    else:
        print("❌ Failed to retrieve preferences")

    # Step 5: Test error handling - invalid data
    print("\n📝 Step 5: Testing error handling (missing required fields)...")
    invalid_data = {"preferred_topics": []}  # Missing other required fields

    error_response = requests.post(
        f"{BASE_URL}/personalization/preferences", json=invalid_data, headers=headers
    )
    print_response(error_response, "Invalid Data Test")

    if error_response.status_code == 400:
        print("✅ Error handling working correctly!")
    else:
        print("⚠️ Expected 400 error but got:", error_response.status_code)

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("Login", login_response.status_code == 200),
        ("Save Goals", goals_response.status_code == 200),
        ("Save Preferences", preferences_response.status_code == 200),
        ("Get Preferences", get_preferences_response.status_code == 200),
        ("Error Handling", error_response.status_code == 400),
    ]

    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    total_passed = sum(1 for _, passed in tests if passed)
    print(f"\n🎯 Results: {total_passed}/{len(tests)} tests passed")

    if total_passed == len(tests):
        print("\n🎉 All tests passed! Goal Setting API is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the backend logs.")


if __name__ == "__main__":
    try:
        test_goal_setting_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("Please ensure the Flask backend is running:")
        print("  cd language-learning-platform")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback

        traceback.print_exc()
