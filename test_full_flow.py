#!/usr/bin/env python
"""
Comprehensive test to verify the assessment completion and evaluation flow works properly
"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

# Test credentials
auth_data = {
    "username": "tanojrahul",
    "password": "Tanoj@190605"
}

print("=" * 70)
print("Testing Assessment Completion and Evaluation Flow")
print("=" * 70)

try:
    # Step 1: Authenticate
    print("\n[Step 1] Authenticating...")
    auth_response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json=auth_data,
        timeout=10
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        print(auth_response.json())
        exit(1)
    
    token = auth_response.json().get("access_token")
    print("✅ Authenticated successfully")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Generate a fresh assessment
    print("\n[Step 2] Generating a fresh assessment...")
    generate_response = requests.post(
        f"{API_BASE_URL}/api/assessment/generate",
        headers=headers,
        json={"proficiency_level": "beginner"},
        timeout=20
    )
    
    if generate_response.status_code != 200:
        print(f"❌ Generate failed: {generate_response.status_code}")
        print(generate_response.text[:500])
        exit(1)
    
    gen_data = generate_response.json()
    assessment_id = gen_data.get("assessment", {}).get("assessment_id")
    questions = gen_data.get("assessment", {}).get("questions", [])
    print(f"✅ Generated assessment ID: {assessment_id}")
    print(f"   Questions: {len(questions)} questions")
    
    # Step 3: Submit answers for all questions
    print(f"\n[Step 3] Submitting answers for all {len(questions)} questions...")
    for idx, q in enumerate(questions, 1):
        q_id = q.get("id") or q.get("question_id")
        submit_response = requests.post(
            f"{API_BASE_URL}/api/assessment/{assessment_id}/submit-answer",
            json={"question_id": q_id, "answer": "B"},
            headers=headers,
            timeout=10
        )
        
        if submit_response.status_code not in [200, 201]:
            print(f"❌ Failed to submit answer {idx}/{len(questions)}: {submit_response.status_code}")
            print(submit_response.text[:200])
            exit(1)
        
        if idx % 10 == 0:
            print(f"  Submitted {idx}/{len(questions)} answers...")
    
    # Step 4: Call complete endpoint (should trigger evaluation)
    print(f"\n[Step 4] Calling POST /assessment/{assessment_id}/complete...")
    complete_response = requests.post(
        f"{API_BASE_URL}/api/assessment/{assessment_id}/complete",
        json={"time_spent_seconds": 300},
        headers=headers,
        timeout=20
    )
    
    print(f"Status: {complete_response.status_code}")
    complete_data = complete_response.json()
    
    if complete_response.status_code == 200:
        print("✅ SUCCESS! Complete endpoint returned 200")
        results = complete_data.get("results", {})
        print(f"   Score: {results.get('overall_score', 'N/A')}")
        print(f"   Proficiency: {results.get('overall_proficiency_level', 'N/A')}")
        print(f"   Skills: {list(results.get('skill_breakdown', {}).keys())}")
    else:
        print(f"❌ FAILED - Status {complete_response.status_code}")
        print(f"Response: {json.dumps(complete_data, indent=2)[:500]}")
        exit(1)
    
    # Step 5: Call complete endpoint again (should return 200 for already-completed)
    print(f"\n[Step 5] Calling POST /assessment/{assessment_id}/complete again...")
    complete_response_2 = requests.post(
        f"{API_BASE_URL}/api/assessment/{assessment_id}/complete",
        json={"time_spent_seconds": 300},
        headers=headers,
        timeout=20
    )
    
    print(f"Status: {complete_response_2.status_code}")
    complete_data_2 = complete_response_2.json()
    
    if complete_response_2.status_code == 200:
        print("✅ SUCCESS! Already-completed assessment returned 200")
        print(f"   Message: {complete_data_2.get('message', 'N/A')}")
        results = complete_data_2.get("results", {})
        print(f"   Score: {results.get('overall_score', 'N/A')}")
        print(f"   Proficiency: {results.get('overall_proficiency_level', 'N/A')}")
    else:
        print(f"❌ FAILED - Status {complete_response_2.status_code}")
        print(f"Response: {json.dumps(complete_data_2, indent=2)[:500]}")
        exit(1)
    
    # Step 6: Call /results endpoint
    print(f"\n[Step 6] Calling GET /assessment/{assessment_id}/results...")
    results_response = requests.get(
        f"{API_BASE_URL}/api/assessment/{assessment_id}/results",
        headers=headers,
        timeout=20
    )
    
    print(f"Status: {results_response.status_code}")
    results_data = results_response.json()
    
    if results_response.status_code == 200:
        print("✅ SUCCESS! Results endpoint returned 200")
        results = results_data.get("results", {})
        print(f"   Score: {results.get('overall_score', 'N/A')}")
        print(f"   Proficiency: {results.get('overall_proficiency_level', 'N/A')}")
        print(f"   Skills: {list(results.get('skill_breakdown', {}).keys())}")
    else:
        print(f"❌ FAILED - Status {results_response.status_code}")
        print(f"Response: {json.dumps(results_data, indent=2)[:500]}")
        exit(1)
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    
except requests.exceptions.ConnectionError:
    print("❌ Connection error - is Flask server running on http://localhost:5000?")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
