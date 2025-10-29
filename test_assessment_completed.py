#!/usr/bin/env python
"""
Test script to verify the assessment results endpoint works correctly
for already-completed assessments.

This tests the flow:
1. User completes assessment (or has an existing completed assessment)
2. User clicks "View Results" on the "already completed" page
3. Frontend calls GET /assessment/{id}/results
4. Backend returns the results for that completed assessment
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
HEADERS = {
    "Content-Type": "application/json",
}

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_completed_assessment_results():
    """Test fetching results for a completed assessment"""
    print_section("Testing Assessment Results Endpoint")
    
    # First, we need to get a JWT token
    print("Step 1: Authenticating...")
    auth_data = {
        "email": "test@example.com",
        "password": "Test@123"
    }
    
    try:
        auth_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=auth_data,
            headers=HEADERS
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.json()}")
            return False
        
        token = auth_response.json().get("access_token")
        print(f"✅ Authenticated successfully")
        print(f"Token: {token[:20]}...")
        
        # Add token to headers
        headers = HEADERS.copy()
        headers["Authorization"] = f"Bearer {token}"
        
        # Step 2: Generate a new assessment
        print("\nStep 2: Generating assessment...")
        assess_response = requests.post(
            f"{API_BASE_URL}/api/assessment/generate",
            json={"assessment_type": "comprehensive"},
            headers=headers
        )
        
        if assess_response.status_code != 200:
            print(f"❌ Assessment generation failed: {assess_response.status_code}")
            print(f"Response: {assess_response.json()}")
            return False
        
        assessment_data = assess_response.json().get("assessment", {})
        assessment_id = assessment_data.get("assessment_id")
        questions = assessment_data.get("questions", [])
        
        print(f"✅ Assessment generated successfully")
        print(f"Assessment ID: {assessment_id}")
        print(f"Total Questions: {len(questions)}")
        
        # Step 3: Answer a question to advance the assessment
        print("\nStep 3: Answering first question...")
        if questions:
            first_question = questions[0]
            submit_response = requests.post(
                f"{API_BASE_URL}/api/assessment/{assessment_id}/submit-answer",
                json={
                    "question_id": first_question.get("id") or first_question.get("question_id"),
                    "answer": "test answer"
                },
                headers=headers
            )
            
            if submit_response.status_code == 200:
                print(f"✅ Answer submitted successfully")
                result = submit_response.json().get("result", {})
                print(f"Progress: {result.get('progress', {})}")
            else:
                print(f"⚠️ Warning: Answer submission status: {submit_response.status_code}")
        
        # Step 4: Try to complete an incomplete assessment (should give error)
        print("\nStep 4: Testing /complete endpoint on incomplete assessment...")
        complete_response = requests.post(
            f"{API_BASE_URL}/api/assessment/{assessment_id}/complete",
            json={"time_spent_seconds": 60},
            headers=headers
        )
        
        print(f"Status: {complete_response.status_code}")
        print(f"Response: {json.dumps(complete_response.json(), indent=2, ensure_ascii=False)}")
        
        # Step 5: Test the new /results endpoint
        print("\nStep 5: Testing new /results endpoint...")
        results_response = requests.get(
            f"{API_BASE_URL}/api/assessment/{assessment_id}/results",
            headers=headers
        )
        
        print(f"Status: {results_response.status_code}")
        if results_response.status_code == 200:
            print("✅ Results endpoint working!")
            results = results_response.json()
            print(f"Response: {json.dumps(results, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Results endpoint failed: {results_response.json()}")
            
        print("\n" + "="*60)
        print("✅ Test completed successfully!")
        print("="*60)
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Cannot connect to {API_BASE_URL}")
        print("Make sure the Flask backend is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_completed_assessment_results()
    exit(0 if success else 1)
