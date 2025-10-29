# 🚀 Phase 2 Quick Reference Guide

## Quick Start

### 1. Test the Implementation
```bash
cd language-learning-platform
python test_phase2_content_generation.py
```

### 2. Start the Backend
```bash
python app.py
```

### 3. Generate Your First Activity

**Generate a Quiz:**
```bash
curl -X POST http://localhost:5000/api/content-generation/quiz \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Present Tense",
    "difficulty": 0.5,
    "question_count": 5
  }'
```

---

## 📋 Activity Types Quick Reference

| Type | Endpoint | Primary Skills |
|------|----------|---------------|
| Quiz | `/quiz` | Comprehension, Vocabulary |
| Flashcards | `/flashcards` | Vocabulary, Memory |
| Reading | `/reading` | Reading, Comprehension |
| Writing | `/writing` | Writing, Grammar |
| Listening | `/listening` | Listening, Comprehension |
| Speaking | `/speaking` | Speaking, Pronunciation |
| Real-World | `/real-world` | Professional Communication |
| Pronunciation | `/pronunciation` | Speaking, Pronunciation |
| Sentence Construction | `/sentence-construction` | Grammar, Writing |
| Dialogue Completion | `/dialogue-completion` | Comprehension |
| Error Correction | `/error-correction` | Grammar, Editing |
| Story Sequencing | `/story-sequencing` | Comprehension, Logic |
| Synonym/Antonym | `/synonym-antonym` | Vocabulary |
| Dictation | `/dictation` | Listening, Writing |
| Translation | `/translation` | Translation, Vocabulary |

---

## 🔧 Common Use Cases

### Generate Activity by Type
```python
from app.services.content_generation_engine import ContentGenerationEngine

engine = ContentGenerationEngine()
activity = engine.generate_personalized_activity(
    user_id=1,
    activity_type='quiz',
    difficulty=0.5
)
```

### Batch Generate Activities
```python
# Via API
POST /api/content-generation/batch
{
  "activity_types": ["quiz", "flashcard", "reading"],
  "difficulty": 0.5
}
```

### With Caching
```python
from app.services.activity_cache_service import cached_activity_generation

@cached_activity_generation
def my_function(user_id, activity_type, difficulty):
    # Your code here
    pass
```

### With Validation
```python
from app.services.content_quality_validator import validate_generated_activity

activity = engine.generate_personalized_activity(...)
validated = validate_generated_activity(activity)

if validated['validation']['is_valid']:
    # Use the activity
    pass
```

---

## 📊 Difficulty Levels

| Value | Description | Suitable For |
|-------|-------------|--------------|
| 0.0-0.3 | Easy | A1-A2 beginners |
| 0.3-0.5 | Medium | A2-B1 elementary |
| 0.5-0.7 | Moderate | B1-B2 intermediate |
| 0.7-0.9 | Hard | B2-C1 advanced |
| 0.9-1.0 | Expert | C1-C2 proficient |

---

## 🎯 Personalization Parameters

### Required:
- `user_id` - User identifier

### Optional but Recommended:
- `learning_node` - Specific learning objective
- `difficulty` - 0-1 scale or easy/medium/hard
- `activity_type` - Specific type or auto-determined
- `user_context` - Pre-loaded context (for performance)

### Activity-Specific:
- **Quiz**: `concept`, `question_count`, `focus_areas`
- **Flashcards**: `vocabulary_list`, `context_theme`
- **Reading**: `topic`, `length_words`, `target_vocabulary`
- **Writing**: `writing_type`, `word_count_range`, `target_grammar`
- **Listening**: `topic`, `duration_seconds`, `focus_phonemes`
- **Speaking**: `scenario_type`, `target_phrases`
- **Real-World**: `task_type`, `industry`

---

## 🚨 Error Handling

### Common Errors:
1. **Missing User**: Returns `{"error": "User not found"}`
2. **Invalid Activity Type**: Returns `{"error": "Unknown activity type: X"}`
3. **Generation Failed**: Returns fallback activity with `"fallback": true`
4. **Validation Failed**: Returns activity with `validation.errors` array

### Handling:
```python
result = engine.generate_personalized_activity(...)

if 'error' in result:
    # Handle error
    print(f"Error: {result['error']}")
elif result.get('fallback'):
    # Using fallback content
    print("Using fallback activity")
else:
    # Success!
    print("Activity generated successfully")
```

---

## 📈 Performance Tips

1. **Use Caching**: Enable caching for repeated requests
2. **Batch Generation**: Generate multiple activities at once
3. **Pre-load Context**: Load user context once, reuse for multiple generations
4. **Cache Invalidation**: Invalidate cache when user profile updates
5. **Monitor Quality**: Check validation scores, adjust if needed

---

## 🔍 Monitoring

### Check Cache Stats:
```python
from app.services.activity_cache_service import get_cache_stats

stats = get_cache_stats()
print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Utilization: {stats['utilization']*100:.1f}%")
```

### Get Activity Quality Score:
```python
from app.services.content_quality_validator import ContentQualityValidator

validator = ContentQualityValidator()
score = validator.calculate_quality_score(activity)
print(f"Quality Score: {score:.2f}")
```

---

## 🧪 Testing Checklist

- [ ] All 15 activity types generate successfully
- [ ] Personalization uses user context
- [ ] Validation catches errors
- [ ] Caching reduces duplicate calls
- [ ] API endpoints return 201 on success
- [ ] Fallback works when AI fails
- [ ] Quality scores are reasonable (>0.7)

---

## 📝 File Locations

```
language-learning-platform/
├── app/
│   ├── services/
│   │   ├── content_generation_engine.py      ← Main engine
│   │   ├── content_quality_validator.py      ← Validation
│   │   └── activity_cache_service.py         ← Caching
│   └── routes/
│       └── content_generation_routes.py      ← API endpoints
├── test_phase2_content_generation.py         ← Tests
└── MasterDocs/
    └── PHASE2_COMPLETE_CONTENT_GENERATION.md ← Documentation
```

---

## 🎓 Next Steps

### Immediate (Today):
1. Run tests: `python test_phase2_content_generation.py`
2. Test API endpoints with Postman/curl
3. Verify caching is working

### Short-term (This Week):
1. Integrate with frontend (remove mock data)
2. Monitor cache hit rates
3. Tune quality validation thresholds

### Medium-term (Next Week):
1. Implement Phase 3 (Learning Path Orchestrator)
2. Add Redis for distributed caching
3. Implement audio generation for listening exercises

---

## 📞 Support

For issues or questions:
1. Check `PHASE2_COMPLETE_CONTENT_GENERATION.md` for detailed documentation
2. Review test output for specific error messages
3. Verify API endpoint authentication

---

**Phase 2 Status: ✅ COMPLETE**

All 16 tasks completed successfully!
