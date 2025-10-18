# Custom LLM Testing Guide

This directory contains test scripts to verify your custom LLM model integration.

## Test Scripts

### 1. `test_llm_quick.py` - Quick Test
A simple, fast test script that runs 4 basic tests:
- Endpoint connectivity
- Simple text generation
- Translation capability
- Chat completion

**Usage:**
```bash
# Activate virtual environment
.\venv1\Scripts\Activate.ps1

# Run quick test
python test_llm_quick.py
```

**Expected Output:**
```
🚀 Quick Custom LLM Test
=================================
📌 Configuration:
   Endpoint: https://hpc.kluniversity.in/dev/jupyter/...
   Model: sarvamai/sarvam-m
   Provider: custom

🧪 Test 0: Endpoint Connectivity
✅ Endpoint reachable! Status: 200

🧪 Test 1: Simple Prompt
✅ Success!
💬 Response: Hello, World! ... నమస్కారం, ప్రపంచం!

...

📊 Test Summary
   Endpoint Test: ✅ PASSED
   Simple Prompt: ✅ PASSED
   Translation: ✅ PASSED
   Chat Completion: ✅ PASSED

📈 Results: 4/4 tests passed (100%)
🎉 All tests passed!
```

---

### 2. `test_custom_llm.py` - Comprehensive Test
A detailed test suite that runs 10 comprehensive tests:
1. Endpoint connection test
2. Basic text generation
3. Telugu translation
4. Grammar explanation
5. JSON generation
6. Chat completion
7. Long-form content
8. System prompt adherence
9. Temperature variation
10. Fallback mechanism

**Usage:**
```bash
# Activate virtual environment
.\venv1\Scripts\Activate.ps1

# Run comprehensive test
python test_custom_llm.py
```

**Features:**
- ✅ Detailed test results with timing
- ✅ Response preview for each test
- ✅ JSON output saved to `llm_test_results.json`
- ✅ Tests fallback to Gemini
- ✅ Tests different parameters (temperature, tokens)

**Expected Output:**
```
🚀 Custom LLM Model Test Suite
=====================================
ℹ️  VLLM_ENDPOINT: https://hpc.kluniversity.in/...
ℹ️  Default Provider: custom
ℹ️  Custom Model: sarvamai/sarvam-m

🧪 Test: 1. Endpoint Connection Test
--------------------------------------------------
✅ Test passed in 0.45s

🧪 Test: 2. Basic Text Generation
--------------------------------------------------
✅ Test passed in 2.31s
📝 Response Preview:
Hello, World! in Telugu is నమస్కారం, ప్రపంచం! (Namaskāraṁ, prapañcaṁ!)...

...

📊 Test Summary
=====================================
⏱️  Total Duration: 45.23s
📝 Total Tests: 10
✅ Passed: 9
❌ Failed: 1
📈 Success Rate: 90.0%
```

---

## Configuration

Ensure your `.env` file has the custom endpoint configured:

```env
# Custom LLM Endpoint
VLLM_ENDPOINT=https://hpc.kluniversity.in/dev/jupyter/MTkyLjE2OC4yMC4xNDo1NDEzMg/infer

# Gemini API Key (fallback)
GEMINI_API_KEY=your_gemini_key_here
```

---

## Test Results

### Quick Test Output
- **Duration**: ~10-15 seconds
- **Tests**: 4 basic tests
- **Format**: Console output only

### Comprehensive Test Output
- **Duration**: ~45-60 seconds  
- **Tests**: 10 detailed tests
- **Format**: Console + JSON file (`llm_test_results.json`)

### JSON Results Structure
```json
{
  "timestamp": "2025-10-17T23:30:00",
  "endpoint": "https://...",
  "model": "sarvamai/sarvam-m",
  "summary": {
    "total_tests": 10,
    "passed": 9,
    "failed": 1,
    "success_rate": "90.0%"
  },
  "results": [
    {
      "test": "1. Endpoint Connection Test",
      "status": "PASSED",
      "duration": "0.45s",
      "details": {...}
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

#### 1. "VLLM_ENDPOINT not configured"
**Solution**: Add endpoint to `.env` file:
```env
VLLM_ENDPOINT=https://your-endpoint-url/infer
```

#### 2. "Cannot connect to endpoint"
**Possible causes**:
- ✅ Check if endpoint URL is correct
- ✅ Check if server is running
- ✅ Check network connectivity
- ✅ Check firewall settings

#### 3. "Endpoint timeout"
**Possible causes**:
- Server is slow or overloaded
- Network latency issues
- Try increasing timeout in test script

#### 4. Tests fail but fallback works
**This is normal!** The system is designed to:
1. Try custom model first
2. If custom fails, automatically fallback to Gemini
3. This ensures your app always works

---

## Integration with Your App

The test scripts use the same `LLMConfig` class that your application uses:

```python
from app.services.llm_config import LLMConfig, LLMProvider

# Generate text (automatic fallback)
response = LLMConfig.generate_text(
    prompt="Your prompt here",
    provider=LLMProvider.CUSTOM,
    temperature=0.7,
    max_tokens=200
)

if response["success"]:
    print(response["text"])
else:
    print(response["error"])
```

---

## What Gets Tested

### Text Generation
- ✅ Simple prompts
- ✅ Telugu translation
- ✅ Grammar explanations
- ✅ Long-form content
- ✅ JSON structured output

### Parameters
- ✅ Temperature (0.0 to 1.0)
- ✅ Max tokens
- ✅ System prompts
- ✅ JSON mode

### Reliability
- ✅ Endpoint connectivity
- ✅ Response time
- ✅ Fallback mechanism
- ✅ Error handling

---

## Next Steps

1. **Run Quick Test First**
   ```bash
   python test_llm_quick.py
   ```

2. **If Quick Test Passes, Run Comprehensive Test**
   ```bash
   python test_custom_llm.py
   ```

3. **Review Results**
   - Check console output
   - Review `llm_test_results.json`

4. **Monitor in Production**
   - Watch for fallback usage
   - Monitor response times
   - Track success rates

---

## Need Help?

- Check test output for error messages
- Review `llm_test_results.json` for details
- Verify `.env` configuration
- Test endpoint connectivity separately
- Check Flask app logs for LLM calls

---

**Happy Testing! 🚀**
