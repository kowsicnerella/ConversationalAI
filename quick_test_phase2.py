"""
Quick manual test for Phase 2 Activity CRUD endpoints
Run this after backend is running on localhost:5000
"""

import requests
import json

BASE_URL = "http://localhost:5000"
TOKEN = None  # Will be set after login

def test_login():
    """Test login and get token"""
    global TOKEN
    print("\n" + "="*60)
    print("1. Testing Login")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "tanojrahul", "password": "Tanoj@190605"}
    )
    
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print("[OK] Login successful")
        print(f"Token: {TOKEN[:30]}...")
        return True
    else:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(response.text)
        return False

def test_generate_quiz():
    """Test generating and saving a quiz"""
    print("\n" + "="*60)
    print("2. Testing Quiz Generation & Storage")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/api/content-generation/quiz",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={
            "concept": "Present tense verbs",
            "difficulty": 0.5,
            "question_count": 5,
            "focus_areas": ["grammar"]
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print("[OK] Quiz generated successfully")
        print(f"Activity ID: {data.get('activity_id')}")
        print(f"Saved: {data.get('saved')}")
        print(f"Title: {data.get('title', 'N/A')}")
        return data.get('activity_id')
    else:
        print(f"[FAIL] Quiz generation failed: {response.status_code}")
        print(response.text)
        return None

def test_list_activities():
    """Test listing activities"""
    print("\n" + "="*60)
    print("3. Testing Activity List")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/content-generation/activities",
        headers={"Authorization": f"Bearer {TOKEN}"},
        params={"limit": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] Activities retrieved")
        print(f"Total count: {data.get('total_count', 0)}")
        print(f"Returned: {len(data.get('activities', []))}")
        
        if data.get('activities'):
            print("\nFirst activity:")
            act = data['activities'][0]
            print(f"  ID: {act.get('id')}")
            print(f"  Title: {act.get('title')}")
            print(f"  Type: {act.get('activity_type')}")
            print(f"  Difficulty: {act.get('difficulty_level')}")
        return True
    else:
        print(f"[FAIL] List failed: {response.status_code}")
        print(response.text)
        return False

def test_get_statistics():
    """Test statistics endpoint"""
    print("\n" + "="*60)
    print("4. Testing Statistics")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/api/content-generation/activities/stats",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] Statistics retrieved")
        print(f"Total activities: {data.get('total_activities', 0)}")
        print(f"Average difficulty: {data.get('average_difficulty', 0):.2f}")
        print(f"Total time: {data.get('total_estimated_time_minutes', 0)} minutes")
        
        if data.get('by_type'):
            print("\nBy type:")
            for act_type, count in list(data['by_type'].items())[:3]:
                print(f"  {act_type}: {count}")
        return True
    else:
        print(f"[FAIL] Statistics failed: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 2 ACTIVITY CRUD - MANUAL TEST")
    print("="*60)
    print("Make sure Flask backend is running on localhost:5000")
    print("="*60)
    
    # Test login
    if not test_login():
        print("\n[FAIL] Cannot proceed without login")
        return
    
    # Test generation
    activity_id = test_generate_quiz()
    
    # Test retrieval
    test_list_activities()
    
    # Test statistics
    test_get_statistics()
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
