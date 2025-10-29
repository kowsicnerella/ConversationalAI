"""
Quick Debug Script to Check Assessment Endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def log(msg, status="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"SUCCESS": "✅", "ERROR": "❌", "INFO": "ℹ️"}
    print(f"[{timestamp}] {symbols.get(status, 'ℹ️')} {msg}")

# Step 1: Register user
log("Registering user...")
reg_response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": f"debug_user_{int(datetime.now().timestamp())}",
        "email": f"debug_{int(datetime.now().timestamp())}@test.com",
        "password": "Test123!",
        "native_language": "Telugu",
        "target_language": "English"
    }
)

if reg_response.status_code != 201:
    log(f"Registration failed: {reg_response.text}", "ERROR")
    exit(1)

user_data = reg_response.json()
user_id = user_data.get("user", {}).get("id")
token = user_data.get("access_token")
log(f"User created: ID={user_id}", "SUCCESS")

# Step 2: Generate assessment
log("Generating assessment...")
headers = {"Authorization": f"Bearer {token}"}
gen_response = requests.post(
    f"{BASE_URL}/api/assessment/generate",
    headers=headers,
    json={"assessment_type": "comprehensive"}
)

log(f"Assessment generation response code: {gen_response.status_code}", "INFO")
print("RESPONSE JSON:")
print(json.dumps(gen_response.json(), indent=2))

if gen_response.status_code == 200:
    data = gen_response.json()
    assessment_id = data.get("assessment_id") or data.get("id")
    
    if assessment_id:
        log(f"Assessment ID: {assessment_id}", "SUCCESS")
        
        # Step 3: Try to get first question
        log("Attempting to get first question...", "INFO")
        
        # Try different endpoints
        endpoints = [
            f"/api/assessment/{assessment_id}/next-question",
            f"/api/assessment/{assessment_id}/question",
            f"/api/assessment/{assessment_id}/questions",
        ]
        
        for endpoint in endpoints:
            log(f"Trying endpoint: {endpoint}", "INFO")
            q_response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Status: {q_response.status_code}")
            
            if q_response.status_code == 200:
                print("Response JSON:")
                print(json.dumps(q_response.json(), indent=2))
            else:
                print(f"Error: {q_response.text[:200]}")
            print()
    else:
        log("No assessment_id in response!", "ERROR")
else:
    log(f"Assessment generation failed: {gen_response.status_code}", "ERROR")
