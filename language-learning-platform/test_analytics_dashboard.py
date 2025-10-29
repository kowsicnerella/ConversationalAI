"""
Test Analytics Dashboard - Phase 2
Generates test data and verifies all 6 analytics endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import random
import sys

# Configuration
BASE_URL = "http://localhost:5000"
ANALYTICS_BASE = f"{BASE_URL}/api/analytics-v2"

# Test user credentials (use existing user or create one)
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def authenticate():
    """Authenticate and get JWT token"""
    print_info("Authenticating...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_id = data.get('user_id')
            print_success(f"Authenticated as user ID: {user_id}")
            return token, user_id
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, None
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None, None


def generate_test_data(token, user_id, num_activities=30):
    """Generate test activity data for analytics"""
    print_header("Generating Test Data")
    print_info(f"Creating {num_activities} test activities...")
    
    skill_areas = ['vocabulary', 'grammar', 'reading', 'writing', 'listening', 'speaking']
    activity_types = ['quiz', 'flashcard', 'reading', 'writing', 'listening']
    
    created_count = 0
    
    for i in range(num_activities):
        # Generate random date within last 60 days
        days_ago = random.randint(0, 60)
        completed_at = datetime.utcnow() - timedelta(days=days_ago)
        
        # Generate realistic scores (improving over time)
        base_score = 60 + (30 - days_ago) * 0.5  # Scores improve as we get closer to today
        accuracy_score = min(100, max(40, base_score + random.uniform(-15, 15)))
        
        # Random time spent (5-30 minutes)
        time_spent = random.randint(5, 30)
        
        # Create activity log
        try:
            # Note: This assumes you have an endpoint to create test activity logs
            # If not, you'll need to insert directly into the database
            activity_data = {
                'user_id': user_id,
                'skill_area': random.choice(skill_areas),
                'activity_type': random.choice(activity_types),
                'accuracy_score': round(accuracy_score, 1),
                'time_spent_minutes': time_spent,
                'is_completed': True,
                'completed_at': completed_at.isoformat()
            }
            
            # This would require a special test endpoint
            # For now, we'll just print what we would create
            if i % 10 == 0:
                print_info(f"Activity {i+1}/{num_activities}: {activity_data['skill_area']} - {accuracy_score:.1f}%")
            
            created_count += 1
            
        except Exception as e:
            print_warning(f"Could not create activity {i+1}: {str(e)}")
    
    print_success(f"Test data generation complete! ({created_count} activities)")
    print_warning("Note: If activities weren't created, you need to add them manually or via database")


def test_endpoint(name, url, token, params=None):
    """Test a single analytics endpoint"""
    print(f"\n{Colors.BOLD}Testing: {name}{Colors.END}")
    print_info(f"URL: {url}")
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(url, headers=headers, params=params)
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Pretty print response
            print(f"\n{Colors.CYAN}Response Data:{Colors.END}")
            print(json.dumps(data, indent=2))
            
            # Validate response structure
            if 'success' in data and data['success']:
                print_success(f"{name} - PASSED")
                return True, data
            else:
                print_error(f"{name} - FAILED (success=false)")
                return False, data
        else:
            print_error(f"{name} - FAILED (Status: {response.status_code})")
            print_error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"{name} - ERROR: {str(e)}")
        return False, None


def run_analytics_tests(token):
    """Run all analytics endpoint tests"""
    print_header("Testing Analytics Endpoints")
    
    results = {}
    
    # Test 1: Performance Trends
    print_info("Test 1: Performance Trends")
    for time_range in ['7days', '30days', '90days', 'all']:
        success, data = test_endpoint(
            f"Performance Trends ({time_range})",
            f"{ANALYTICS_BASE}/performance-trends",
            token,
            params={'time_range': time_range}
        )
        results[f'performance_trends_{time_range}'] = success
    
    # Test 2: Skill Breakdown
    print_info("\nTest 2: Skill Breakdown")
    success, data = test_endpoint(
        "Skill Breakdown",
        f"{ANALYTICS_BASE}/skill-breakdown",
        token
    )
    results['skill_breakdown'] = success
    
    # Test 3: Activity Summary
    print_info("\nTest 3: Activity Summary")
    success, data = test_endpoint(
        "Activity Summary",
        f"{ANALYTICS_BASE}/activity-summary",
        token
    )
    results['activity_summary'] = success
    
    # Test 4: Time Analytics
    print_info("\nTest 4: Time Analytics")
    success, data = test_endpoint(
        "Time Analytics",
        f"{ANALYTICS_BASE}/time-analytics",
        token
    )
    results['time_analytics'] = success
    
    # Test 5: Learning Velocity
    print_info("\nTest 5: Learning Velocity")
    success, data = test_endpoint(
        "Learning Velocity",
        f"{ANALYTICS_BASE}/learning-velocity",
        token
    )
    results['learning_velocity'] = success
    
    # Test 6: Weak Areas
    print_info("\nTest 6: Weak Areas")
    success, data = test_endpoint(
        "Weak Areas",
        f"{ANALYTICS_BASE}/weak-areas",
        token
    )
    results['weak_areas'] = success
    
    return results


def print_test_summary(results):
    """Print summary of test results"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print_success(f"Passed: {passed_tests}")
    if failed_tests > 0:
        print_error(f"Failed: {failed_tests}")
    print(f"\n{Colors.BOLD}Success Rate:{Colors.END} {success_rate:.1f}%\n")
    
    # Detailed results
    print(f"{Colors.BOLD}Detailed Results:{Colors.END}")
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if success_rate == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Analytics dashboard is ready!{Colors.END}")
    elif success_rate >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Most tests passed. Check failed tests.{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Multiple tests failed. Review implementation.{Colors.END}")


def main():
    """Main test execution"""
    print_header("🧪 Analytics Dashboard Test Suite - Phase 2")
    
    # Step 1: Authenticate
    token, user_id = authenticate()
    if not token:
        print_error("Cannot proceed without authentication. Exiting.")
        sys.exit(1)
    
    # Step 2: Generate test data (optional - comment out if data already exists)
    print_warning("Skipping test data generation (implement endpoint or add manually)")
    # generate_test_data(token, user_id, num_activities=30)
    
    # Step 3: Run endpoint tests
    results = run_analytics_tests(token)
    
    # Step 4: Print summary
    print_test_summary(results)
    
    # Step 5: Frontend testing instructions
    print_header("Frontend Testing Instructions")
    print_info("1. Ensure Flask server is running on http://localhost:5000")
    print_info("2. Ensure React dev server is running on http://localhost:5173")
    print_info("3. Navigate to: http://localhost:5173/analytics-dashboard")
    print_info("4. Verify all charts render correctly:")
    print("   - Performance Trend Line Chart")
    print("   - Skill Breakdown Radar Chart")
    print("   - Activity Distribution Pie Chart")
    print("   - Time Investment Bar Chart")
    print_info("5. Test time range filters: 7 days, 30 days, 90 days, All")
    print_info("6. Check responsive design on mobile (F12 -> Device Toolbar)")
    print_info("7. Verify weak areas alert displays correctly")
    
    print(f"\n{Colors.BOLD}Testing complete!{Colors.END}\n")


if __name__ == "__main__":
    main()
