"""Quick connectivity test"""
import requests
import sys

print("Testing backend connectivity...")

try:
    # Test if backend is running
    response = requests.get("http://127.0.0.1:5000/api/courses/learning-paths", timeout=5)
    print(f"✅ Backend is responding: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is NOT responding - Connection refused")
    sys.exit(1)
except requests.exceptions.Timeout:
    print("❌ Backend timeout")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
