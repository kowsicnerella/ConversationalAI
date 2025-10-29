"""
Debug script to test assessment completion
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

# Register user
username = f"debug_test_{int(time.time())}"
register_payload = {
    "username": username,
    "email": f"{username}@test.com",
    "password": "Test123!",
    "native_language": "Telugu",
    "target_language": "English"
}

print("[1] Registering user...")
response = requests.post(f"{BASE_URL}/api/auth/register", json=register_payload)
print(f"Status: {response.status_code}")
data = response.json()
user_id = data.get("user", {}).get("id")
token = data.get("access_token")
print(f"User ID: {user_id}, Token: {token[:20]}...")

# Generate assessment
print("\n[2] Generating assessment...")
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(f"{BASE_URL}/api/assessment/generate", headers=headers, json={"assessment_type": "comprehensive"})
print(f"Status: {response.status_code}")
data = response.json()
assessment_obj = data.get("assessment", {})
assessment_id = assessment_obj.get("assessment_id")
questions = assessment_obj.get("questions", [])
print(f"Assessment ID: {assessment_id}, Questions: {len(questions)}")

# Answer all questions
print(f"\n[3] Answering all {len(questions)} questions...")
answered = 0
for i, question in enumerate(questions):
    q_id = question.get("id") or question.get("question_id")
    response = requests.post(
        f"{BASE_URL}/api/assessment/{assessment_id}/submit-answer",
        headers=headers,
        json={"question_id": q_id, "answer": "A"}
    )
    if response.status_code == 200:
        answered += 1
    if (i + 1) % 12 == 0:
        print(f"  Answered {answered}/{i+1}")
    time.sleep(0.05)

print(f"Total answered: {answered}/{len(questions)}")

# Try to complete assessment
print(f"\n[4] Completing assessment...")
headers["Content-Type"] = "application/json"
response = requests.post(
    f"{BASE_URL}/api/assessment/{assessment_id}/complete",
    headers=headers,
    json={}
)
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")
