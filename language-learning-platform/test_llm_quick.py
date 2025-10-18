"""
Quick Test Script for Custom LLM
Simple tests to verify custom model is responding correctly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.llm_config import LLMConfig, LLMProvider

# Load environment
load_dotenv()


def test_simple_prompt():
    """Test a simple prompt"""
    print("\n" + "="*60)
    print("🧪 Test 1: Simple Prompt")
    print("="*60)
    
    prompt = "Say 'Hello, World!' in Telugu and English."
    
    print(f"\n📝 Prompt: {prompt}")
    print("\n⏳ Sending request to custom model...")
    
    response = LLMConfig.generate_text(
        prompt=prompt,
        provider=LLMProvider.CUSTOM,
        temperature=0.7,
        max_tokens=100
    )
    
    if response["success"]:
        print("\n✅ Success!")
        print(f"🤖 Model: {response.get('model', 'unknown')}")
        print(f"\n💬 Response:\n{response['text']}")
        print(f"\n📊 Tokens: {response.get('usage', {})}")
    else:
        print(f"\n❌ Failed: {response.get('error')}")
    
    return response["success"]


def test_translation():
    """Test translation capability"""
    print("\n" + "="*60)
    print("🧪 Test 2: Translation")
    print("="*60)
    
    prompt = "Translate 'Good morning, how are you?' to Telugu."
    
    print(f"\n📝 Prompt: {prompt}")
    print("\n⏳ Sending request to custom model...")
    
    response = LLMConfig.generate_text(
        prompt=prompt,
        provider=LLMProvider.CUSTOM,
        temperature=0.5,
        max_tokens=150
    )
    
    if response["success"]:
        print("\n✅ Success!")
        print(f"🤖 Model: {response.get('model', 'unknown')}")
        print(f"\n💬 Response:\n{response['text']}")
    else:
        print(f"\n❌ Failed: {response.get('error')}")
    
    return response["success"]


def test_chat():
    """Test chat completion"""
    print("\n" + "="*60)
    print("🧪 Test 3: Chat Completion")
    print("="*60)
    
    messages = [
        {"role": "system", "content": "You are a helpful English tutor."},
        {"role": "user", "content": "Give me 3 common English greetings."},
    ]
    
    print(f"\n📝 Chat Messages:")
    for msg in messages:
        print(f"   {msg['role']}: {msg['content']}")
    
    print("\n⏳ Sending request to custom model...")
    
    response = LLMConfig.chat_completion(
        messages=messages,
        stream=False,
        provider=LLMProvider.CUSTOM,
        temperature=0.7,
        max_tokens=200
    )
    
    if response["success"]:
        print("\n✅ Success!")
        print(f"🤖 Model: {response.get('model', 'unknown')}")
        print(f"\n💬 Response:\n{response['message']}")
    else:
        print(f"\n❌ Failed: {response.get('error')}")
    
    return response["success"]


def test_endpoint():
    """Test if endpoint is reachable"""
    print("\n" + "="*60)
    print("🧪 Test 0: Endpoint Connectivity")
    print("="*60)
    
    endpoint = os.getenv("VLLM_ENDPOINT")
    
    if not endpoint or endpoint == "None":
        print(f"\n❌ VLLM_ENDPOINT not configured in .env file")
        return False
    
    print(f"\n🌐 Endpoint: {endpoint}")
    print("\n⏳ Testing connection...")
    
    try:
        import requests
        response = requests.get(endpoint, timeout=5)
        print(f"\n✅ Endpoint reachable! Status: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print(f"\n❌ Endpoint timeout (5 seconds)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to endpoint")
        return False
    except Exception as e:
        print(f"\n❌ Connection test failed: {str(e)}")
        return False


def main():
    """Run quick tests"""
    print("\n" + "="*60)
    print("  🚀 Quick Custom LLM Test")
    print("="*60)
    
    print(f"\n📌 Configuration:")
    print(f"   Endpoint: {os.getenv('VLLM_ENDPOINT')}")
    print(f"   Model: {LLMConfig.MODELS[LLMProvider.CUSTOM]['text']}")
    print(f"   Provider: {LLMConfig.DEFAULT_PROVIDER.value}")
    
    # Run tests
    results = []
    results.append(("Endpoint Test", test_endpoint()))
    results.append(("Simple Prompt", test_simple_prompt()))
    results.append(("Translation", test_translation()))
    results.append(("Chat Completion", test_chat()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    elif passed > 0:
        print("\n⚠️  Some tests failed. Check output above.")
    else:
        print("\n❌ All tests failed. Check your configuration.")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
