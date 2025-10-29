#!/usr/bin/env python
"""
Quick test to verify the /complete endpoint now returns 200 for already-completed assessments
"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

# Test credentials (user with assessment 7)
auth_data = {
    "username": "tanojrahul",  # Use username instead of email
    "password": "Tanoj@190605"
}

print("=" * 60)
print("Testing Updated /complete Endpoint")
print("=" * 60)

try:
    # Step 1: Authenticate
    print("\n1. Authenticating...")
    auth_response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        json=auth_data
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        print(auth_response.json())
        exit(1)
    
    token = auth_response.json().get("access_token")
    print("✅ Authenticated")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Call /complete on assessment 7 (already completed)
    print("\n2. Calling POST /assessment/7/complete (already-completed assessment)...")
    complete_response = requests.post(
        f"{API_BASE_URL}/api/assessment/7/complete",
        json={"time_spent_seconds": 60},
        headers=headers
    )
    
    print(f"Status: {complete_response.status_code}")
    
    if complete_response.status_code == 200:
        print("✅ SUCCESS! /complete now returns 200 for already-completed assessments!")
        result = complete_response.json()
        print(f"\nResponse data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verify it has results
        if result.get("results"):
            print("\n✅ Results are included in response")
            print(f"   - Overall score: {result['results'].get('overall_score')}")
            print(f"   - Proficiency level: {result['results'].get('proficiency_level')}")
        else:
            print("❌ Results missing from response")
            
    else:
        print(f"❌ FAILED - Status {complete_response.status_code}")
        print(json.dumps(complete_response.json(), indent=2, ensure_ascii=False))
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
