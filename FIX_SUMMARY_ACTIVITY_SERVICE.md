# Fixed: ActivityGeneratorService.model.generate_content() References

## Problem
Multiple files were using `activity_service.model.generate_content()` which doesn't exist on the `ActivityGeneratorService` class. This caused 500 errors when those endpoints were called.

## Root Cause
`ActivityGeneratorService` doesn't have a `model` attribute. The class uses `LLMConfig.generate_text()` instead.

## Solution
Replaced all instances of:
```python
ai_response = activity_service.model.generate_content(prompt)
result = ai_response.text
```

With:
```python
from app.services.llm_config import LLMConfig
result = LLMConfig.generate_text(prompt, json_mode=True/False)
if not result['success']:
    return jsonify({"error": "...", "telugu_error": "..."}), 500
text_content = result['text']
```

## Files Fixed

### ✅ app/api/chat_routes.py (6 occurrences - FIXED)
- Line 249: Conversation context generation
- Line 317: Vocabulary extraction 
- Line 443: Quick chat context response
- Line 552: Help request response
- Line 1146: Learning assistance response
- Line 1695: Practice session tutor helper

### 🔄 Still Need Fixing:
- app/api/test_routes.py (1 occurrence)
- app/api/practice_routes.py (5 occurrences)
- app/api/media_routes.py (1 occurrence)
- app/api/learning_path_routes_old.py (4 occurrences)
- app/api/chapter_routes.py (2 occurrences)
- app/api/analytics_routes.py (3 occurrences)

**Note**: `app/api/learning_path_routes.py` was already fixed in a previous session (4 occurrences)

## How to Fix Remaining Files

Each occurrence follows the same pattern:
1. Import LLMConfig: `from app.services.llm_config import LLMConfig`
2. Replace `.model.generate_content()` with `LLMConfig.generate_text()`
3. Add error handling for unsuccessful results
4. Replace `response.text` with `result['text']`

## Testing

After fixes, test these endpoints:
- `POST /api/chat/quick-chat` - Quick chat interaction
- `POST /api/chat/send-message` - Full conversation chat
- Other affected endpoints based on the files above

## Error Handling Improvement

Also improved `LLMConfig._custom_generate_text()` to:
1. Better handle non-JSON responses from custom endpoint
2. Validate response structure before accessing nested keys
3. Provide clearer error messages for debugging
4. Gracefully fallback to Gemini on custom endpoint failure
