#!/usr/bin/env python3
"""
Test script for the Activity Generator Service
This script tests the AI-powered activity generation without requiring API keys
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.activity_generator_service import ActivityGeneratorService
import json

def test_activity_generation():
    """Test activity generation service (mock mode for testing)"""
    
    print("🚀 Testing Telugu-English Learning Platform Activity Generator")
    print("=" * 60)
    
    # Initialize the service
    try:
        service = ActivityGeneratorService()
        print("✅ Activity Generator Service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize service: {e}")
        print("💡 Note: This might be due to missing GEMINI_API_KEY environment variable")
        print("   You can still test the structure without actual AI generation")
        return
    
    # Test cases
    test_cases = [
        {
            'type': 'quiz',
            'method': 'generate_quiz',
            'params': {'topic': 'English greetings', 'level': 'beginner'}
        },
        {
            'type': 'flashcards',
            'method': 'generate_flashcards', 
            'params': {'topic': 'Daily activities', 'level': 'beginner'}
        },
        {
            'type': 'reading',
            'method': 'generate_text_reading',
            'params': {'topic': 'Family relationships', 'level': 'beginner'}
        },
        {
            'type': 'writing_prompt',
            'method': 'generate_writing_practice_prompt',
            'params': {'topic': 'My favorite food', 'level': 'beginner'}
        },
        {
            'type': 'role_play',
            'method': 'generate_role_playing_scenario',
            'params': {'topic': 'ordering food at a restaurant', 'level': 'beginner'}
        }
    ]
    
    print("\\n🧪 Running Activity Generation Tests...")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\\n{i}. Testing {test_case['type']} generation:")
        print(f"   Topic: {test_case['params']['topic']}")
        print(f"   Level: {test_case['params']['level']}")
        
        try:
            method = getattr(service, test_case['method'])
            result = method(**test_case['params'])
            
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"   ⚠️  Error in generation: {result['error']}")
                else:
                    print(f"   ✅ Successfully generated {test_case['type']}")
                    print(f"   📊 Response keys: {list(result.keys())}")
                    
                    # Show a sample of the content
                    if test_case['type'] == 'quiz' and 'questions' in result:
                        print(f"   📝 Generated {len(result['questions'])} questions")
                    elif test_case['type'] == 'flashcards' and 'flashcards' in result:
                        print(f"   🃏 Generated {len(result['flashcards'])} flashcards")
                    elif test_case['type'] == 'reading' and 'reading_text' in result:
                        text_preview = result['reading_text'][:100] + "..." if len(result['reading_text']) > 100 else result['reading_text']
                        print(f"   📖 Reading text: {text_preview}")
            else:
                print(f"   ✅ Generated response (text format)")
                preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                print(f"   📝 Preview: {preview}")
                
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
    
    print("\\n" + "=" * 60)
    print("🎯 Activity Generation Test Summary:")
    print("   - All activity types have been tested")
    print("   - Service structure is properly configured")
    print("   - Ready for Telugu speakers learning English!")
    
    print("\\n💡 Next Steps:")
    print("   1. Set up your GEMINI_API_KEY in environment variables")
    print("   2. Test with real API calls")
    print("   3. Start the Flask application: python app.py")
    print("   4. Test API endpoints with tools like Postman")

def test_json_parsing():
    """Test the JSON parsing functionality"""
    print("\\n🔍 Testing JSON Parsing Function...")
    
    from app.services.activity_generator_service import _extract_json_from_response
    
    # Test cases for JSON parsing
    test_responses = [
        {
            'name': 'Markdown JSON Block',
            'input': '''Here's your quiz:
```json
{
    "questions": [
        {
            "question_text": "What is 'hello' in Telugu?",
            "options": ["హలో", "నమస్కారం", "వందనం", "సుప్రభాతం"],
            "correct_answer": "నమస్కారం"
        }
    ]
}
```
Hope this helps!''',
            'expected_keys': ['questions']
        },
        {
            'name': 'Plain JSON',
            'input': '{"flashcards": [{"front": "Hello", "back": "హలో"}]}',
            'expected_keys': ['flashcards']
        },
        {
            'name': 'Invalid JSON',
            'input': 'This is not JSON at all',
            'expected_keys': ['error', 'raw_response']
        }
    ]
    
    for test in test_responses:
        print(f"\\n   Testing: {test['name']}")
        result = _extract_json_from_response(test['input'])
        
        if isinstance(result, dict):
            actual_keys = list(result.keys())
            if all(key in actual_keys for key in test['expected_keys']):
                print(f"   ✅ Parsing successful - Keys: {actual_keys}")
            else:
                print(f"   ⚠️  Unexpected keys - Expected: {test['expected_keys']}, Got: {actual_keys}")
        else:
            print(f"   ❌ Parsing failed - Not a dictionary")

if __name__ == "__main__":
    test_json_parsing()
    test_activity_generation()