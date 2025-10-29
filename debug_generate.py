#!/usr/bin/env python
"""
Debug test to see what /generate endpoint returns
"""
import requests
import json

API_BASE_URL = "http://localhost:5000"

# Test credentials
auth_data = {
    "username": "tanojrahul",
    "password": "Tanoj@190605"
}

print("Authenticating...")
auth_response = requests.post(
    f"{API_BASE_URL}/api/auth/login",
    json=auth_data,
    timeout=10
)

token = auth_response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("Calling /generate endpoint...")
gen_response = requests.post(
    f"{API_BASE_URL}/api/assessment/generate",
    headers=headers,
    json={"proficiency_level": "beginner"},
    timeout=20
)

print(f"Status: {gen_response.status_code}")
print("Full Response:")
print(json.dumps(gen_response.json(), indent=2))
