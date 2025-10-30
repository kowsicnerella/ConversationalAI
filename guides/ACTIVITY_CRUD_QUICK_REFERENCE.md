# Phase 2 Activity CRUD - Quick Reference Guide

## 🎯 What Was Added

### Storage (CREATE)
All 18 activity generation endpoints now **automatically save** activities to the database:
- Every generated activity gets a unique `activity_id`
- Activities are linked to users and learning paths
- Full generation metadata is preserved

### Retrieval (READ)
5 new GET endpoints to view activities:
1. **List with filters** - `/api/content-generation/activities`
2. **Get by ID** - `/api/content-generation/activities/:id`
3. **Get by type** - `/api/content-generation/activities/by-type/:type`
4. **Statistics** - `/api/content-generation/activities/stats`
5. **History** - `/api/content-generation/activities/:id/history`

---

## 📋 Quick API Examples

### Generate and Save a Quiz
```bash
curl -X POST http://localhost:5000/api/content-generation/quiz \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Present tense verbs",
    "difficulty": 0.5,
    "question_count": 10
  }'

# Returns:
{
  ...quiz content...,
  "activity_id": 123,
  "saved": true
}
```

### List All My Activities
```bash
curl http://localhost:5000/api/content-generation/activities?limit=20 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Returns:
{
  "activities": [...],
  "total_count": 45,
  "has_more": true
}
```

### Filter by Type and Difficulty
```bash
curl "http://localhost:5000/api/content-generation/activities?activity_type=quiz&difficulty_min=0.4&difficulty_max=0.6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Specific Activity
```bash
curl http://localhost:5000/api/content-generation/activities/123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Returns full activity with content
```

### Get My Statistics
```bash
curl http://localhost:5000/api/content-generation/activities/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Returns:
{
  "total_activities": 45,
  "by_type": {"quiz": 10, "flashcard": 8, ...},
  "average_difficulty": 0.55,
  "total_estimated_time_minutes": 450
}
```

---

## 🔍 Available Filters

### Query Parameters for `/activities`
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `activity_type` | string | Filter by type | `?activity_type=quiz` |
| `difficulty_min` | float | Min difficulty (0-1) | `?difficulty_min=0.4` |
| `difficulty_max` | float | Max difficulty (0-1) | `?difficulty_max=0.6` |
| `skill_area` | string | Filter by skill | `?skill_area=vocabulary` |
| `learning_path_id` | int | Filter by path | `?learning_path_id=1` |
| `limit` | int | Results per page | `?limit=20` |
| `offset` | int | Page offset | `?offset=40` |
| `sort_by` | string | Sort field | `?sort_by=difficulty_level` |
| `sort_order` | string | asc or desc | `?sort_order=asc` |

### Combine Multiple Filters
```bash
# Get medium-difficulty quizzes, sorted by date
curl "http://localhost:5000/api/content-generation/activities?activity_type=quiz&difficulty_min=0.4&difficulty_max=0.6&sort_by=created_at&sort_order=desc&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📊 Response Formats

### Activity List Response
```json
{
  "activities": [
    {
      "id": 1,
      "title": "Present Tense Quiz",
      "description": "Practice present tense verbs",
      "activity_type": "quiz",
      "difficulty_level": 0.5,
      "skill_area": "grammar",
      "concept_focus": "present_tense",
      "estimated_duration_minutes": 15,
      "points_reward": 10,
      "created_at": "2024-01-15T10:30:00",
      "learning_path_id": 1,
      "is_adaptive": true
    }
  ],
  "total_count": 45,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

### Single Activity Response
```json
{
  "id": 1,
  "title": "Present Tense Quiz",
  "activity_type": "quiz",
  "content": {
    ...full quiz content with questions...
  },
  "generation_metadata": {
    "generated_by": "ContentGenerationEngine",
    "generated_for_user": 1,
    "generated_at": "2024-01-15T10:30:00"
  }
}
```

### Statistics Response
```json
{
  "total_activities": 45,
  "by_type": {
    "quiz": 10,
    "flashcard": 8,
    "reading": 7
  },
  "by_skill_area": {
    "vocabulary": 15,
    "grammar": 12
  },
  "average_difficulty": 0.55,
  "total_estimated_time_minutes": 450
}
```

---

## 🚀 Testing

### Run the Test Suite
```bash
cd d:\ConversationalAI
python test_phase2_crud.py
```

### Manual Testing Steps
1. **Start backend**: Flask server on port 5000
2. **Login**: Get JWT token
3. **Generate activities**: POST to any generation endpoint
4. **List activities**: GET `/activities`
5. **Filter**: Add query parameters
6. **View details**: GET `/activities/:id`
7. **Check stats**: GET `/activities/stats`

---

## 🔐 Security Notes

- ✅ All endpoints require JWT authentication
- ✅ Users can only see activities generated for them
- ✅ Exception: Can view activities they've completed (collaborative learning)
- ✅ 404 if activity doesn't exist
- ✅ 403 if unauthorized access

---

## 📝 Activity Types Supported

All 15 activity types automatically save:
1. `quiz` - Adaptive quizzes
2. `flashcard` - Contextual flashcards
3. `reading` - Reading comprehension
4. `writing` - Writing prompts
5. `listening` - Listening exercises
6. `speaking` - Speaking scenarios
7. `real_world` - Real-world tasks
8. `pronunciation` - Pronunciation practice
9. `sentence_construction` - Sentence building
10. `dialogue_completion` - Dialogue completion
11. `error_correction` - Error correction
12. `story_sequencing` - Story sequencing
13. `synonym_antonym` - Synonym/antonym matching
14. `dictation` - Dictation exercises
15. `translation` - Translation challenges

---

## 🎨 Frontend Integration

### React Example - List Activities
```javascript
const fetchActivities = async () => {
  const response = await fetch(
    'http://localhost:5000/api/content-generation/activities?limit=20',
    {
      headers: {
        'Authorization': `Bearer ${jwtToken}`
      }
    }
  );
  const data = await response.json();
  setActivities(data.activities);
};
```

### React Example - Generate and Save Quiz
```javascript
const generateQuiz = async () => {
  const response = await fetch(
    'http://localhost:5000/api/content-generation/quiz',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        concept: 'Present tense verbs',
        difficulty: 0.5,
        question_count: 10
      })
    }
  );
  const data = await response.json();
  console.log('Saved with ID:', data.activity_id);
};
```

### React Example - Filter Activities
```javascript
const filterActivities = async (type, difficulty) => {
  const params = new URLSearchParams({
    activity_type: type,
    difficulty_min: difficulty - 0.1,
    difficulty_max: difficulty + 0.1,
    limit: 10
  });
  
  const response = await fetch(
    `http://localhost:5000/api/content-generation/activities?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${jwtToken}`
      }
    }
  );
  const data = await response.json();
  return data.activities;
};
```

---

## ✅ Checklist

### Implementation Status
- [x] Helper function for saving activities
- [x] Updated all 18 POST endpoints to save
- [x] Created 5 GET endpoints
- [x] Added filtering by type, difficulty, skill
- [x] Added pagination (limit, offset)
- [x] Added sorting (asc, desc)
- [x] Added statistics endpoint
- [x] Added security/access control
- [x] Created test suite
- [x] Created documentation

### Next Steps
- [ ] Run test suite
- [ ] Fix any failing tests
- [ ] Frontend integration
- [ ] Add activity completion tracking
- [ ] Add activity update/delete (if needed)
- [ ] Performance optimization (indexes, caching)

---

## 📁 Files Modified

- `app/routes/content_generation_routes.py` (~1200 lines)
  - Added `save_generated_activity()` helper
  - Updated 18 POST endpoints
  - Added 5 GET endpoints

## 📄 Files Created

- `ACTIVITY_CRUD_COMPLETE.md` - Full documentation
- `test_phase2_crud.py` - Test suite
- `ACTIVITY_CRUD_QUICK_REFERENCE.md` - This guide

---

## 💡 Pro Tips

1. **Always use filters** - Don't fetch all activities at once
2. **Paginate properly** - Use `limit` and `offset` for large datasets
3. **Check `has_more`** - Know if there are more pages
4. **Use statistics** - Great for dashboard widgets
5. **Cache wisely** - Statistics can be cached longer than activity lists
6. **Sort by date** - Default sorting by `created_at desc` shows newest first
7. **Filter by difficulty** - Help users find activities at their level

---

## 🐛 Troubleshooting

### "Activities not showing up"
- Check JWT token is valid
- Verify activities were generated for this user
- Check `generation_metadata.generated_for_user` matches user ID

### "Filtering not working"
- Ensure parameter names are correct (snake_case)
- Difficulty values must be 0-1 floats
- Activity types must match exactly (case-sensitive)

### "Pagination issues"
- `offset` must be multiple of `limit` for clean pages
- Check `total_count` vs `offset + limit` to know if done

---

**🎉 Phase 2 CRUD Complete! Ready for testing and frontend integration.**
