"""Test the personalized recommendation endpoint"""
import requests
import json

url = "http://localhost:5000/api/learning-paths/personalized-recommendation"

# First, let's register a new user to get a token
register_url = "http://localhost:5000/api/auth/register"
register_data = {
    "username": "testuser123",
    "password": "password123",
    "email": "test@example.com"
}

# Try to register first
try:
    reg_response = requests.post(register_url, json=register_data)
    print("Register Status:", reg_response.status_code)
except:
    pass

# Then login
auth_url = "http://localhost:5000/api/auth/login"
auth_data = {
    "username": "testuser123",
    "password": "password123"
}

try:
    # Login to get token
    auth_response = requests.post(auth_url, json=auth_data)
    print("Auth Response Status:", auth_response.status_code)
    
    if auth_response.status_code == 200:
        token = auth_response.json().get("access_token")
        print("✅ Got token:", token[:20] + "...")
        
        # Test the personalized recommendation
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        test_data = {
            "english_level": "intermediate",
            "learning_goals": ["conversation", "business"],
            "interests": ["technology", "movies"],
            "time_available_minutes": 30,
            "previous_experience": {"years": 2}
        }
        
        print("\nTesting personalized recommendation...")
        response = requests.post(url, json=test_data, headers=headers)
        
        print("Status Code:", response.status_code)
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    else:
        print("❌ Auth failed:", auth_response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
