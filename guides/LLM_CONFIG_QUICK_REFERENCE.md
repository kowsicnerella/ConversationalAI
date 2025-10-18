# Quick Reference: Using LLM Config

## Import

```python
from app.services.llm_config import LLMConfig, LLMProvider
```

## Basic Text Generation

```python
# Simple text generation (uses custom model with Gemini fallback)
result = LLMConfig.generate_text("Translate 'hello' to Telugu")
if result['success']:
    print(result['text'])
else:
    print(f"Error: {result['error']}")
```

## JSON Mode

```python
# Force JSON output
prompt = """
Generate a quiz question in JSON format:
{
  "question": "What is the capital of France?",
  "options": ["Paris", "London", "Berlin", "Madrid"],
  "correct_answer": "Paris"
}
"""
result = LLMConfig.generate_text(prompt, json_mode=True, temperature=0.3)
if result['success']:
    import json
    data = json.loads(result['text'])
```

## Chat Completion

```python
# Multi-turn conversation
messages = [
    {"role": "system", "content": "You are a Telugu-English tutor"},
    {"role": "user", "content": "How do I say 'thank you' in English?"},
    {"role": "assistant", "content": "You say 'thank you'"},
    {"role": "user", "content": "What about 'you're welcome'?"}
]

result = LLMConfig.chat_completion(messages, stream=False, temperature=0.7)
if result['success']:
    print(result['message'])
```

## Image Analysis

```python
from PIL import Image

# Analyze image
image = Image.open('path/to/image.jpg')
prompt = "Describe this image in simple English suitable for Telugu learners"

result = LLMConfig.analyze_image(image, prompt, json_mode=False)
if result['success']:
    print(result['analysis'])
```

## Advanced Options

```python
# Custom temperature and max tokens
result = LLMConfig.generate_text(
    prompt="Explain grammar rules",
    temperature=0.5,        # Lower = more focused
    max_tokens=500,        # Limit response length
    system_prompt="You are a grammar expert",
    json_mode=False
)
```

## Error Handling

```python
result = LLMConfig.generate_text(prompt)

# Always check success
if result['success']:
    # Use the response
    text = result['text']
    model_used = result['model']
    tokens_used = result['usage']['total_tokens']
else:
    # Handle error
    error_msg = result.get('error', 'Unknown error')
    print(f"LLM failed: {error_msg}")
    # Implement fallback logic
```

## Provider Selection

```python
# Force specific provider (bypasses fallback)
result = LLMConfig.generate_text(
    prompt="Hello",
    provider=LLMProvider.GEMINI  # Use only Gemini
)

# Or use custom only (no fallback - will fail if custom is down)
result = LLMConfig.generate_text(
    prompt="Hello",
    provider=LLMProvider.CUSTOM
)

# Default (no provider arg) uses CUSTOM with automatic Gemini fallback
```

## Response Format

All methods return:
```python
{
    'success': bool,           # True if successful
    'text': str,              # For generate_text()
    'message': str,           # For chat_completion()
    'analysis': str,          # For analyze_image()
    'model': str,             # Model that was used
    'usage': {                # Token usage info
        'total_tokens': int
    },
    'error': str              # Only present if success=False
}
```

## Common Patterns

### Pattern 1: JSON Generation with Fallback
```python
def generate_quiz_question(topic):
    prompt = f"Generate quiz about {topic} in JSON format..."
    result = LLMConfig.generate_text(prompt, json_mode=True)
    
    if result['success']:
        try:
            return json.loads(result['text'])
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}
    else:
        # Fallback quiz
        return {
            "question": "Default question",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }
```

### Pattern 2: Retry Logic
```python
def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        result = LLMConfig.generate_text(prompt)
        if result['success']:
            return result['text']
        time.sleep(2 ** attempt)  # Exponential backoff
    
    raise Exception("Failed after retries")
```

### Pattern 3: Bilingual Response
```python
def get_bilingual_explanation(word):
    prompt = f"""
    Explain the English word '{word}' for Telugu speakers.
    Provide:
    1. English meaning
    2. Telugu translation
    3. Example sentence in English
    4. Example sentence in Telugu
    """
    
    result = LLMConfig.generate_text(prompt, temperature=0.5)
    return result.get('text', 'Explanation not available')
```

## Tips

1. **Always check `result['success']`** before using the response
2. **Use `json_mode=True`** when expecting structured data
3. **Lower temperature (0.3-0.5)** for factual/structured content
4. **Higher temperature (0.7-0.9)** for creative/conversational content
5. **Set max_tokens** to control response length and cost
6. **The fallback is automatic** - you don't need to handle it manually

## Configuration

Check current settings:
```python
# Get available models
models = LLMConfig.get_available_models()
print(f"Custom models: {models}")

# Check default provider
print(f"Default: {LLMConfig.DEFAULT_PROVIDER}")
```

Change global settings:
```python
# Change default provider
LLMConfig.set_provider(LLMProvider.GEMINI)

# Update custom endpoint
LLMConfig.set_custom_endpoint('text', 'http://new-endpoint/v1/completions')
```
