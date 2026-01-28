import requests
import json

# Configuration
BASE_URL = "http://localhost:5000/api"

# Step 1: Login
print("Step 1: Logging in...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "test_user",
    "password": "password123"
})

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ Login successful! Token: {token[:20]}...")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

# Step 2: Call next-activity endpoint
print("\nStep 2: Calling /api/learning-path/next-activity...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

activity_response = requests.post(
    f"{BASE_URL}/learning-path/next-activity",
    headers=headers,
    json={}
)

print(f"Status Code: {activity_response.status_code}")
print(f"Response Headers: {dict(activity_response.headers)}")
print(f"\nResponse Content:")
print(activity_response.text)

# Try to parse JSON
try:
    data = activity_response.json()
    print(f"\n✅ JSON parsed successfully:")
    print(json.dumps(data, indent=2))
except json.JSONDecodeError as e:
    print(f"\n❌ Failed to parse JSON: {e}")
    print(f"Raw content (first 500 chars): {activity_response.text[:500]}")
