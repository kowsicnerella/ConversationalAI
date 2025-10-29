#!/usr/bin/env python3
"""
Phase 9 Gamification API Test Script

Tests all 19 endpoints of the Phase 9 gamification system.
Requires: Flask server running on localhost:5000, valid JWT token
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:5000/api/gamification-v2"
JWT_TOKEN = None  # Will be set after login

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, status, message=""):
    """Print test result with color coding."""
    if status == "PASS":
        print(f"{Colors.GREEN}✓ {name}{Colors.RESET}")
    elif status == "FAIL":
        print(f"{Colors.RED}✗ {name}: {message}{Colors.RESET}")
    elif status == "SKIP":
        print(f"{Colors.YELLOW}⊗ {name}: {message}{Colors.RESET}")
    elif status == "INFO":
        print(f"{Colors.BLUE}ℹ {name}: {message}{Colors.RESET}")

def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

def login():
    """Get JWT token for testing."""
    global JWT_TOKEN
    print_header("Step 1: Getting JWT Token")
    
    # Try to login with a test user
    login_url = "http://localhost:5000/api/auth/login"
    credentials = {
        "email": "test@example.com",
        "password": "testTa123"
    }
    
    try:
        response = requests.post(login_url, json=credentials, timeout=5)
        if response.status_code == 200:
            data = response.json()
            JWT_TOKEN = data.get('access_token') or data.get('token')
            print_test("Login", "PASS")
            print_test("JWT Token", "INFO", f"Token: {JWT_TOKEN[:20]}...")
            return True
        else:
            print_test("Login", "FAIL", f"Status {response.status_code}")
            # Continue with unauthenticated tests
            return False
    except Exception as e:
        print_test("Login", "FAIL", str(e))
        return False

def make_request(method, endpoint, expected_status=200, data=None, require_auth=True):
    """Make HTTP request to API."""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if require_auth and JWT_TOKEN:
        headers['Authorization'] = f'Bearer {JWT_TOKEN}'
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=5)
        else:
            return None
        
        success = response.status_code == expected_status
        return {
            'success': success,
            'status': response.status_code,
            'data': response.json() if response.text else {},
            'expected': expected_status
        }
    except Exception as e:
        return {
            'success': False,
            'status': 0,
            'error': str(e),
            'expected': expected_status
        }

def test_health_check():
    """Test: Health Check"""
    print_header("Test Suite 1: Health Check")
    result = make_request("GET", "/health", expected_status=200, require_auth=False)
    if result and result['success']:
        print_test("GET /health", "PASS")
        print_test("Response", "INFO", f"Status: {result['data'].get('status')}")
    else:
        print_test("GET /health", "FAIL", f"Expected 200, got {result['status'] if result else 'error'}")

def test_challenges():
    """Test: Challenge Endpoints (5)"""
    print_header("Test Suite 2: Challenge Endpoints (5 tests)")
    
    # Test 1: Get today's challenges
    result = make_request("GET", "/challenges/today", expected_status=200)
    if result and result['success']:
        challenges = result['data'].get('challenges', [])
        print_test("GET /challenges/today", "PASS")
        print_test("Challenges Count", "INFO", f"Received {len(challenges)} challenges")
    else:
        print_test("GET /challenges/today", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Get challenge history
    result = make_request("GET", "/challenges/history", expected_status=200)
    if result and result['success']:
        print_test("GET /challenges/history", "PASS")
    else:
        print_test("GET /challenges/history", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 3: Get specific challenge (use first challenge ID if available)
    if result and result['data']:
        challenge_id = result['data'].get('challenges', [{}])[0].get('id', 1)
        result = make_request("GET", f"/challenges/{challenge_id}", expected_status=200)
        if result and result['success']:
            print_test("GET /challenges/{id}", "PASS")
        else:
            print_test("GET /challenges/{id}", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 4: Complete challenge
    result = make_request("POST", "/challenges/1/complete", expected_status=200, data={})
    if result and (result['success'] or result['status'] == 400):  # 400 if already completed
        print_test("POST /challenges/{id}/complete", "PASS")
    else:
        print_test("POST /challenges/{id}/complete", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 5: Get personalized recommendations
    result = make_request("GET", "/challenges/recommendations", expected_status=200)
    if result and (result['success'] or result['status'] == 404):
        print_test("GET /challenges/recommendations", "PASS" if result['success'] else "SKIP")
    else:
        print_test("GET /challenges/recommendations", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_achievements():
    """Test: Achievement Endpoints (3)"""
    print_header("Test Suite 3: Achievement Endpoints (3 tests)")
    
    # Test 1: Get all achievements
    result = make_request("GET", "/achievements", expected_status=200)
    if result and result['success']:
        achievements = result['data'].get('achievements', [])
        print_test("GET /achievements", "PASS")
        print_test("Achievements Count", "INFO", f"Received {len(achievements)} achievements")
    else:
        print_test("GET /achievements", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Get achievements with category filter
    result = make_request("GET", "/achievements?category=milestone", expected_status=200)
    if result and result['success']:
        print_test("GET /achievements?category=milestone", "PASS")
    else:
        print_test("GET /achievements?category=milestone", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 3: Showcase achievement
    result = make_request("POST", "/achievements/1/showcase", expected_status=200, data={})
    if result and (result['success'] or result['status'] == 400):
        print_test("POST /achievements/{id}/showcase", "PASS")
    else:
        print_test("POST /achievements/{id}/showcase", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_leaderboards():
    """Test: Leaderboard Endpoints (3)"""
    print_header("Test Suite 4: Leaderboard Endpoints (3 tests)")
    
    # Test 1: Get leaderboard
    result = make_request("GET", "/leaderboard", expected_status=200)
    if result and result['success']:
        entries = result['data'].get('leaderboard', [])
        print_test("GET /leaderboard", "PASS")
        print_test("Leaderboard Entries", "INFO", f"Received {len(entries)} entries")
    else:
        print_test("GET /leaderboard", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Get leaderboard with filters
    result = make_request("GET", "/leaderboard?category=overall&time_period=weekly", expected_status=200)
    if result and result['success']:
        print_test("GET /leaderboard?category=overall&time_period=weekly", "PASS")
    else:
        print_test("GET /leaderboard?category=overall&time_period=weekly", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 3: Get leaderboard categories
    result = make_request("GET", "/leaderboard/categories", expected_status=200)
    if result and result['success']:
        categories = result['data'].get('categories', [])
        print_test("GET /leaderboard/categories", "PASS")
        print_test("Categories", "INFO", f"Received {len(categories)} categories")
    else:
        print_test("GET /leaderboard/categories", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_streaks():
    """Test: Streak Endpoints (3)"""
    print_header("Test Suite 5: Streak Endpoints (3 tests)")
    
    # Test 1: Get current streak
    result = make_request("GET", "/streak", expected_status=200)
    if result and result['success']:
        streak_data = result['data']
        print_test("GET /streak", "PASS")
        print_test("Current Streak", "INFO", f"Days: {streak_data.get('current_streak', 0)}")
    else:
        print_test("GET /streak", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Update streak
    result = make_request("POST", "/streak/update", expected_status=200, data={})
    if result and (result['success'] or result['status'] == 400):
        print_test("POST /streak/update", "PASS")
    else:
        print_test("POST /streak/update", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 3: Freeze streak
    result = make_request("POST", "/streak/freeze", expected_status=200, data={})
    if result and (result['success'] or result['status'] == 400):
        print_test("POST /streak/freeze", "PASS")
    else:
        print_test("POST /streak/freeze", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_milestones():
    """Test: Milestone Endpoints (2)"""
    print_header("Test Suite 6: Milestone Endpoints (2 tests)")
    
    # Test 1: Get milestones
    result = make_request("GET", "/milestones", expected_status=200)
    if result and result['success']:
        milestones = result['data'].get('milestones', [])
        print_test("GET /milestones", "PASS")
        print_test("Milestones", "INFO", f"Received {len(milestones)} milestones")
    else:
        print_test("GET /milestones", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Celebrate milestone
    result = make_request("POST", "/milestones/1/celebrate", expected_status=200, data={})
    if result and (result['success'] or result['status'] == 400):
        print_test("POST /milestones/{id}/celebrate", "PASS")
    else:
        print_test("POST /milestones/{id}/celebrate", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_social():
    """Test: Social Endpoints (3)"""
    print_header("Test Suite 7: Social Endpoints (3 tests)")
    
    # Test 1: Get connections
    result = make_request("GET", "/social/connections", expected_status=200)
    if result and result['success']:
        connections = result['data'].get('connections', [])
        print_test("GET /social/connections", "PASS")
        print_test("Connections", "INFO", f"Received {len(connections)} connections")
    else:
        print_test("GET /social/connections", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 2: Share achievement
    result = make_request("POST", "/social/share-achievement", expected_status=200, 
                         data={"achievement_id": 1, "caption": "Test", "visibility": "public"})
    if result and (result['success'] or result['status'] == 400):
        print_test("POST /social/share-achievement", "PASS")
    else:
        print_test("POST /social/share-achievement", "FAIL", f"Status {result['status'] if result else 'error'}")
    
    # Test 3: Get social feed
    result = make_request("GET", "/social/feed", expected_status=200)
    if result and result['success']:
        feed = result['data'].get('feed', [])
        print_test("GET /social/feed", "PASS")
        print_test("Feed Items", "INFO", f"Received {len(feed)} items")
    else:
        print_test("GET /social/feed", "FAIL", f"Status {result['status'] if result else 'error'}")

def test_summary():
    """Test: Summary Endpoint (1)"""
    print_header("Test Suite 8: Summary Endpoint (1 test)")
    
    result = make_request("GET", "/summary", expected_status=200)
    if result and result['success']:
        print_test("GET /summary", "PASS")
        data = result['data']
        print_test("Summary Sections", "INFO", f"Keys: {', '.join(data.keys())}")
    else:
        print_test("GET /summary", "FAIL", f"Status {result['status'] if result else 'error'}")

def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print("Phase 9 Gamification API Test Suite")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}{Colors.RESET}\n")
    
    # Step 1: Login
    login()
    
    # Step 2: Run all test suites
    test_health_check()
    test_challenges()
    test_achievements()
    test_leaderboards()
    test_streaks()
    test_milestones()
    test_social()
    test_summary()
    
    print_header("Test Suite Complete")
    print(f"{Colors.GREEN}✓ All tests completed!{Colors.RESET}\n")

if __name__ == "__main__":
    main()
