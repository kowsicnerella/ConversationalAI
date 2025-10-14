# Centralized LLM Configuration - Usage Guide

## Overview
`llm_config.py` is the **single source of truth** for all AI model interactions. All services import from this file, making it easy to switch between providers (Gemini, OpenAI, custom endpoints) in one place.

---

## Quick Start

### 1. Text Generation

```python
from app.services.llm_config import LLMConfig

# Simple text generation
result = LLMConfig.generate_text(
    prompt="Generate 5 English vocabulary words for beginners",
    temperature=0.7,
    max_tokens=500
)

if result['success']:
    print(result['text'])
    print(f"Model used: {result['model']}")
else:
    print(f"Error: {result['error']}")
```

### 2. Chat Completion

```python
# Conversation-style interaction
messages = [
    {'role': 'system', 'content': 'You are a Telugu language tutor.'},
    {'role': 'user', 'content': 'How do I say "hello" in Telugu?'},
    {'role': 'assistant', 'content': 'In Telugu, "hello" is "నమస్కారం" (Namaskāram).'},
    {'role': 'user', 'content': 'What about "goodbye"?'}
]

result = LLMConfig.chat_completion(
    messages=messages,
    temperature=0.5,
    max_tokens=200
)

if result['success']:
    print(result['message'])
```

### 3. Image Analysis

```python
from PIL import Image

# Analyze image
image = Image.open('uploads/images/kitchen.jpg')

result = LLMConfig.analyze_image(
    image=image,
    prompt="Identify all kitchen objects in this image and name them in English and Telugu",
    temperature=0.7,
    json_mode=True  # Forces JSON output
)

if result['success']:
    analysis = result['analysis']
    print(analysis)
```

### 4. JSON Mode (Structured Output)

```python
# Force JSON response for quiz generation
result = LLMConfig.generate_text(
    prompt="""
    Generate a quiz with 3 multiple choice questions about Telugu vocabulary.
    Format: {"questions": [{"question": "...", "options": ["A", "B", "C", "D"], "correct": "A"}]}
    """,
    json_mode=True  # Automatically cleans markdown formatting
)

if result['success']:
    import json
    quiz_data = json.loads(result['text'])
    print(quiz_data)
```

### 5. Audio Transcription

```python
# Speech-to-text
result = LLMConfig.transcribe_audio(
    audio_file='uploads/audio/recording.mp3',
    language='te'  # Telugu
)

if result['success']:
    print(f"Transcription: {result['text']}")
```

### 6. Text-to-Speech

```python
# Generate audio from text
result = LLMConfig.generate_speech(
    text="నమస్కారం! మీరు ఎలా ఉన్నారు?",
    language='te',
    voice='default'
)

if result['success']:
    # Save audio file
    with open('output.wav', 'wb') as f:
        f.write(result['audio_data'])
```

---

## Switching Providers

### Change Default Provider

```python
from app.services.llm_config import LLMConfig, LLMProvider

# Switch to custom endpoint
LLMConfig.set_provider(LLMProvider.CUSTOM)

# All subsequent calls will use custom endpoint
result = LLMConfig.generate_text("Generate text...")
```

### Per-Request Provider

```python
# Use Gemini for this request only
result = LLMConfig.generate_text(
    prompt="...",
    provider=LLMProvider.GEMINI
)

# Use custom endpoint for this request
result = LLMConfig.generate_text(
    prompt="...",
    provider=LLMProvider.CUSTOM
)
```

---

## Custom Endpoint Configuration

### Set Custom Endpoints

```python
# Set custom inference endpoint
LLMConfig.set_custom_endpoint('text', 'http://your-server.com/v1/completions')
LLMConfig.set_custom_endpoint('vision', 'http://your-server.com/v1/vision')
LLMConfig.set_custom_endpoint('audio', 'http://your-server.com/v1/audio')
```

### Environment Variables

Add to `.env` file:
```bash
CUSTOM_TEXT_ENDPOINT=http://localhost:8000/v1/chat/completions
CUSTOM_VISION_ENDPOINT=http://localhost:8000/v1/vision/analyze
CUSTOM_AUDIO_ENDPOINT=http://localhost:8000/v1/audio/transcribe
CUSTOM_SPEECH_ENDPOINT=http://localhost:8000/v1/audio/synthesize
```

---

## Migrating Existing Code

### Before (Direct Gemini Call)

```python
import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

response = model.generate_content(prompt)
text = response.text
```

### After (Using LLMConfig)

```python
from app.services.llm_config import LLMConfig

result = LLMConfig.generate_text(prompt)
text = result['text'] if result['success'] else ''
```

---

## Service Integration Examples

### activity_service.py

```python
from app.services.llm_config import LLMConfig

class ActivityService:
    @staticmethod
    def generate_quiz(topic, difficulty, count):
        prompt = f"Generate {count} {difficulty} quiz questions about {topic}"
        
        result = LLMConfig.generate_text(
            prompt=prompt,
            temperature=0.8,
            json_mode=True
        )
        
        if result['success']:
            return json.loads(result['text'])
        else:
            return {'error': result['error']}
```

### image_service.py

```python
from app.services.llm_config import LLMConfig
from PIL import Image

class ImageService:
    @staticmethod
    def analyze_image_for_learning(image_path):
        prompt = "Identify objects and provide Telugu translations..."
        
        result = LLMConfig.analyze_image(
            image=Image.open(image_path),
            prompt=prompt,
            json_mode=True
        )
        
        return result
```

### assessment_service.py

```python
from app.services.llm_config import LLMConfig

class AssessmentService:
    @staticmethod
    def generate_assessment(level):
        messages = [
            {'role': 'system', 'content': 'You generate language assessments.'},
            {'role': 'user', 'content': f'Create a {level} English assessment'}
        ]
        
        result = LLMConfig.chat_completion(
            messages=messages,
            temperature=0.7,
            json_mode=True
        )
        
        return result
```

---

## Convenience Functions

For quick one-liners:

```python
from app.services.llm_config import generate_text, analyze_image, chat

# Quick text generation
text = generate_text("What is the capital of India?")

# Quick image analysis
analysis = analyze_image(image, "Describe this image")

# Quick chat
response = chat([
    {'role': 'user', 'content': 'Hello!'}
])
```

---

## Error Handling

All methods return a consistent format:

```python
{
    'success': True/False,
    'text': '...',           # for generate_text
    'message': '...',        # for chat_completion
    'analysis': '...',       # for analyze_image
    'model': 'gemini-2.0-flash-exp',
    'usage': {'total_tokens': 150},
    'error': 'Error message' # if success=False
}
```

Example error handling:

```python
result = LLMConfig.generate_text(prompt)

if result['success']:
    # Process result
    process_text(result['text'])
else:
    # Handle error
    logger.error(f"LLM error: {result['error']}")
    return fallback_response()
```

---

## Configuration Options

### Model Selection

Models are automatically selected based on provider and modality:

```python
MODELS = {
    LLMProvider.GEMINI: {
        'text': 'gemini-2.0-flash-exp',
        'vision': 'gemini-2.0-flash-exp',
        'audio': 'gemini-2.0-flash-exp',
        'multimodal': 'gemini-2.0-flash-exp'
    },
    LLMProvider.CUSTOM: {
        'text': 'custom-model',
        'vision': 'custom-vision',
        'audio': 'custom-audio',
        'multimodal': 'custom-multimodal'
    }
}
```

### Default Parameters

```python
DEFAULT_PARAMS = {
    'temperature': 0.7,
    'max_tokens': 2048,
    'top_p': 0.9,
    'top_k': 40,
    'stop_sequences': None
}
```

---

## Advanced Usage

### System Prompts

```python
result = LLMConfig.generate_text(
    prompt="Translate: Hello, how are you?",
    system_prompt="You are an expert English-Telugu translator. Always provide natural, colloquial translations."
)
```

### Temperature Control

```python
# Creative (higher temperature)
creative = LLMConfig.generate_text(prompt, temperature=0.9)

# Deterministic (lower temperature)
precise = LLMConfig.generate_text(prompt, temperature=0.2)
```

### Token Limits

```python
# Short response
result = LLMConfig.generate_text(prompt, max_tokens=100)

# Long response
result = LLMConfig.generate_text(prompt, max_tokens=4096)
```

---

## Future: Switching to Custom Model

When you're ready to use your own model:

1. **Update environment variables**:
```bash
CUSTOM_TEXT_ENDPOINT=https://your-inference-server.com/v1/completions
```

2. **Change default provider**:
```python
# In config.py or startup
LLMConfig.set_provider(LLMProvider.CUSTOM)
```

3. **No code changes needed!** All services automatically use the new endpoint.

---

## Benefits

✅ **Single point of modification** - Change model/provider in one file  
✅ **Consistent API** - All modalities use same pattern  
✅ **Easy testing** - Mock LLMConfig in tests  
✅ **Provider agnostic** - Switch between Gemini, OpenAI, custom  
✅ **Error handling** - Standardized error responses  
✅ **JSON mode** - Automatic markdown cleanup  
✅ **Future-proof** - Add new providers without changing services  

---

## Example: Full Quiz Generation

```python
from app.services.llm_config import LLMConfig
import json

def generate_quiz(topic, difficulty, num_questions):
    prompt = f"""
    Generate {num_questions} multiple choice questions about {topic} for {difficulty} level.
    Return in this JSON format:
    {{
        "questions": [
            {{
                "question": "What is...?",
                "question_telugu": "ఏమిటి...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Because..."
            }}
        ]
    }}
    """
    
    result = LLMConfig.generate_text(
        prompt=prompt,
        temperature=0.8,
        max_tokens=2000,
        json_mode=True
    )
    
    if result['success']:
        quiz_data = json.loads(result['text'])
        return {
            'success': True,
            'quiz': quiz_data,
            'model': result['model']
        }
    else:
        return {
            'success': False,
            'error': result['error']
        }

# Usage
quiz = generate_quiz("English Grammar", "beginner", 5)
if quiz['success']:
    for q in quiz['quiz']['questions']:
        print(q['question'])
```

---

**Next Steps:**
1. Update all existing services to use `LLMConfig`
2. Remove direct `google.generativeai` imports
3. Test with current Gemini setup
4. When ready, switch to custom endpoint with one line change!
