"""
Test Enhanced Activity Generation - Phase 2
Tests personalized activity generation with different user profiles
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
ACTIVITIES_BASE = f"{BASE_URL}/api/activities-v2"

# Test user credentials
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def authenticate():
    """Authenticate and get JWT token"""
    print_info("Authenticating...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user_id')
            print_success(f"Authenticated as user ID: {user_id}")
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None


def test_activity_generation(token, activity_type=None, focus_skill=None, test_name=""):
    """Test activity generation with specific parameters"""
    print(f"\n{Colors.BOLD}Test: {test_name}{Colors.END}")
    
    payload = {}
    if activity_type:
        payload['activity_type'] = activity_type
    if focus_skill:
        payload['focus_skill'] = focus_skill
    
    print_info(f"Request: {json.dumps(payload) if payload else 'Auto-select'}")
    
    try:
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        response = requests.post(
            f"{ACTIVITIES_BASE}/generate",
            headers=headers,
            json=payload
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Display key information
            print(f"\n{Colors.CYAN}Generated Activity:{Colors.END}")
            print(f"  Type: {data.get('activity_type', 'N/A')}")
            print(f"  Title: {data.get('title', 'N/A')}")
            print(f"  Description: {data.get('description', 'N/A')[:100]}...")
            
            # Display metadata
            if 'metadata' in data:
                meta = data['metadata']
                print(f"\n{Colors.CYAN}Personalization Metadata:{Colors.END}")
                print(f"  Difficulty: {meta.get('difficulty', 'N/A')}")
                print(f"  Focus Skill: {meta.get('focus_skill', 'N/A')}")
                print(f"  User Level: {meta.get('user_level', 'N/A')}")
                print(f"  Weak Areas Targeted: {', '.join(meta.get('weak_areas_targeted', []))}")
                print(f"  Personalization Level: {meta.get('personalization_level', 'N/A')}")
            
            # Validate structure
            if data.get('activity_type') and data.get('title'):
                print_success(f"{test_name} - PASSED")
                return True, data
            else:
                print_error(f"{test_name} - FAILED (Missing required fields)")
                return False, data
        else:
            print_error(f"{test_name} - FAILED (Status: {response.status_code})")
            print_error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"{test_name} - ERROR: {str(e)}")
        return False, None


def test_suggestion(token):
    """Test activity suggestion endpoint"""
    print(f"\n{Colors.BOLD}Test: Activity Suggestion{Colors.END}")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{ACTIVITIES_BASE}/suggest", headers=headers)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.CYAN}Suggestion:{Colors.END}")
            print(f"  Suggested Type: {data.get('suggested_type', 'N/A')}")
            print(f"  Suggested Skill: {data.get('suggested_skill', 'N/A')}")
            print(f"  Reason: {data.get('reason', 'N/A')}")
            print(f"  Difficulty: {data.get('difficulty', 'N/A')}")
            print(f"  Estimated Time: {data.get('estimated_time', 'N/A')} min")
            
            if data.get('weak_areas'):
                print(f"\n{Colors.CYAN}Weak Areas:{Colors.END}")
                for area in data.get('weak_areas', [])[:3]:
                    print(f"  - {area['skill']}: {area['score']}% ({area['priority']} priority)")
            
            print_success("Activity Suggestion - PASSED")
            return True, data
        else:
            print_error(f"Activity Suggestion - FAILED (Status: {response.status_code})")
            return False, None
            
    except Exception as e:
        print_error(f"Activity Suggestion - ERROR: {str(e)}")
        return False, None


def test_performance_analysis(token):
    """Test performance analysis endpoint"""
    print(f"\n{Colors.BOLD}Test: Performance Analysis{Colors.END}")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{ACTIVITIES_BASE}/performance", headers=headers, params={'days': 7})
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.CYAN}Performance (Last 7 Days):{Colors.END}")
            perf = data.get('performance', {})
            print(f"  Total Activities: {perf.get('total_activities', 'N/A')}")
            print(f"  Average Accuracy: {perf.get('avg_accuracy', 'N/A')}%")
            print(f"  Improvement Trend: {perf.get('improvement_trend', 'N/A')}%")
            print(f"  Average Time: {perf.get('avg_time', 'N/A')} min")
            
            print(f"\n{Colors.CYAN}User Profile:{Colors.END}")
            profile = data.get('user_profile', {})
            print(f"  Level: {profile.get('proficiency_level', 'N/A')}")
            print(f"  Streak: {profile.get('current_streak', 'N/A')} days")
            print(f"  Total Activities: {profile.get('total_activities', 'N/A')}")
            
            print(f"\n  Optimal Difficulty: {data.get('optimal_difficulty', 'N/A')}")
            
            print_success("Performance Analysis - PASSED")
            return True, data
        else:
            print_error(f"Performance Analysis - FAILED (Status: {response.status_code})")
            return False, None
            
    except Exception as e:
        print_error(f"Performance Analysis - ERROR: {str(e)}")
        return False, None


def test_difficulty_calculation(token):
    """Test difficulty calculation endpoint"""
    print(f"\n{Colors.BOLD}Test: Difficulty Calculation{Colors.END}")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{ACTIVITIES_BASE}/difficulty-test", headers=headers)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n{Colors.CYAN}Difficulty Breakdown:{Colors.END}")
            print(f"  Base Difficulty: {data.get('base_difficulty', 'N/A')}")
            print(f"  Base Reason: {data.get('base_reason', 'N/A')}")
            
            if data.get('adjustments'):
                print(f"\n{Colors.CYAN}Adjustments:{Colors.END}")
                for adj in data.get('adjustments', []):
                    print(f"  - {adj['type']}: {adj['change']:+.2f} ({adj['reason']})")
            
            print(f"\n  Final Difficulty: {data.get('final_difficulty', 'N/A')}")
            
            print_success("Difficulty Calculation - PASSED")
            return True, data
        else:
            print_error(f"Difficulty Calculation - FAILED (Status: {response.status_code})")
            return False, None
            
    except Exception as e:
        print_error(f"Difficulty Calculation - ERROR: {str(e)}")
        return False, None


def run_all_tests(token):
    """Run comprehensive test suite"""
    print_header("Enhanced Activity Generation Test Suite")
    
    results = {}
    
    # Test 1: Auto-generated activity
    success, _ = test_activity_generation(token, test_name="Auto-Generated Activity")
    results['auto_generate'] = success
    
    # Test 2: Quiz generation
    success, _ = test_activity_generation(token, activity_type='quiz', test_name="Quiz Generation")
    results['quiz_generate'] = success
    
    # Test 3: Flashcard generation
    success, _ = test_activity_generation(token, activity_type='flashcard', test_name="Flashcard Generation")
    results['flashcard_generate'] = success
    
    # Test 4: Vocabulary focus
    success, _ = test_activity_generation(token, focus_skill='vocabulary', test_name="Vocabulary Focus")
    results['vocabulary_focus'] = success
    
    # Test 5: Grammar focus
    success, _ = test_activity_generation(token, focus_skill='grammar', test_name="Grammar Focus")
    results['grammar_focus'] = success
    
    # Test 6: Activity suggestion
    success, _ = test_suggestion(token)
    results['suggestion'] = success
    
    # Test 7: Performance analysis
    success, _ = test_performance_analysis(token)
    results['performance'] = success
    
    # Test 8: Difficulty calculation
    success, _ = test_difficulty_calculation(token)
    results['difficulty'] = success
    
    return results


def print_test_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    print(f"\n{Colors.BOLD}Success Rate:{Colors.END} {success_rate:.1f}%\n")
    
    print(f"{Colors.BOLD}Detailed Results:{Colors.END}")
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Enhanced activity generation is ready!{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed. Check failed tests.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Multiple tests failed. Review implementation.{Colors.END}")


def main():
    """Main execution"""
    print_header("🧪 Enhanced Activity Generation Test Suite - Phase 2")
    
    # Authenticate
    token, user_id = authenticate()
    if not token:
        print_error("Cannot proceed without authentication. Exiting.")
        sys.exit(1)
    
    # Run tests
    results = run_all_tests(token)
    
    # Print summary
    print_test_summary(results)
    
    # Additional validation points
    print_header("Manual Validation Checklist")
    print_info("✓ Verify AI includes user context in prompts")
    print_info("✓ Check weak areas are prioritized in suggestions")
    print_info("✓ Validate difficulty matches user performance")
    print_info("✓ Test with beginner, intermediate, and advanced users")
    print_info("✓ Verify activity types match focus skills")
    print_info("✓ Check metadata is complete and accurate")
    
    print(f"\n{Colors.BOLD}Testing complete!{Colors.END}\n")


if __name__ == "__main__":
    main()
