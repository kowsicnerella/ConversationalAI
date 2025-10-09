# 🚀 Initial Assessment - Quick Reference

## 📍 URLs
- **Assessment Page**: `http://localhost:5173/assessment`
- **Results Page**: `http://localhost:5173/assessment-results`
- **Backend API**: `http://localhost:5000/api/assessment/`

---

## 🔌 API Endpoints

### Generate Assessment
```http
POST /api/assessment/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "assessment_type": "comprehensive"
}
```
**Returns:** Assessment ID, questions array, metadata

---

### Submit Single Answer
```http
POST /api/assessment/{assessment_id}/submit-answer
Authorization: Bearer <token>
Content-Type: application/json

{
  "question_id": "q_vocab_beginner_1",
  "answer": "A"
}
```
**Returns:** Evaluation, feedback, next question, progress

---

### Complete Assessment
```http
POST /api/assessment/{assessment_id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
  "time_spent_seconds": 300
}
```
**Returns:** Final results, proficiency level, recommendations
**Side Effect:** Updates user profile ⭐

---

## 📊 Response Format

### Assessment Generation Response
```json
{
  "success": true,
  "assessment": {
    "assessment_id": 123,
    "questions": [
      {
        "question_id": "q_vocab_beginner_1",
        "question_text": "Choose the correct meaning...",
        "options": ["A", "B", "C", "D"],
        "skill_area": "vocabulary",
        "difficulty_level": "beginner",
        "telugu_hint": "సూచన",
        "question_type": "multiple_choice"
      }
    ],
    "metadata": {
      "total_questions": 15,
      "estimated_duration_minutes": 45
    }
  }
}
```

### Submit Answer Response
```json
{
  "success": true,
  "result": {
    "evaluation": {
      "correct": true,
      "feedback": "✅ Correct! Well done!",
      "feedback_telugu": "✅ సరైనది!",
      "points_earned": 2
    },
    "progress": {
      "answered": 5,
      "total": 15,
      "percentage": 33.33
    },
    "next_question": {...},
    "is_complete": false
  }
}
```

### Complete Assessment Response
```json
{
  "success": true,
  "results": {
    "overall_score": 75.5,
    "overall_proficiency_level": "intermediate",
    "skill_breakdown": {
      "vocabulary": 80,
      "grammar": 75,
      "reading": 70
    },
    "strengths": ["vocabulary"],
    "weaknesses": ["reading"],
    "recommendations": [...]
  }
}
```

---

## 🎯 User Profile Updates

After completing assessment, these fields are automatically updated:

```python
user.proficiency_level = "intermediate"
user.needs_initial_assessment = False
user.assessment_taken_at = datetime.utcnow()
user.initial_assessment_id = 123
user.current_learning_phase = "learning"
```

---

## 🧪 Quick Test

### 1. Terminal 1 - Backend
```bash
cd language-learning-platform
python app.py
```

### 2. Terminal 2 - Frontend
```bash
cd ConvAI_frontV1
npm run dev
```

### 3. Browser
1. Go to `http://localhost:5173/assessment`
2. Answer questions
3. Click "Complete Assessment"
4. View results

---

## ✅ Success Indicators

### Frontend
- ✅ Questions load and display
- ✅ Can select/type answers
- ✅ Progress bar updates
- ✅ "Complete Assessment" button appears on last question
- ✅ Results page shows percentage and level

### Backend
- ✅ Assessment generates successfully
- ✅ Answers submit without errors
- ✅ Completion returns 200 status
- ✅ Database shows updated profile

### Database
```sql
SELECT proficiency_level, needs_initial_assessment, 
       assessment_taken_at, current_learning_phase
FROM users 
WHERE id = <user_id>;
```
Expected: `intermediate`, `0`, `<timestamp>`, `learning`

---

## 🐛 Common Issues & Fixes

### Issue: Questions not loading
**Fix:** Check backend is running, check network tab for errors

### Issue: "question_id is required" error
**Fix:** Ensure using `question_id` field, not `id`

### Issue: Skill breakdown not displaying
**Fix:** Check response format, ensure percentages are numbers

### Issue: Profile not updating
**Fix:** Verify complete endpoint is called, check database directly

---

## 📂 Important Files

### Backend
- `app/services/initial_assessment_service.py` - Assessment logic
- `app/api/assessment_routes.py` - API endpoints
- `app/models/user.py` - User model

### Frontend
- `src/pages/InitialAssessment.jsx` - Assessment UI
- `src/pages/AssessmentResults.jsx` - Results display
- `src/config/api.js` - API configuration

---

## 🎨 Field Name Reference

### Question Object
```javascript
{
  question_id: "q_vocab_beginner_1",    // NOT 'id'
  skill_area: "vocabulary",              // NOT 'skill_focus'
  difficulty_level: "beginner",          // NOT 'difficulty'
  telugu_hint: "సూచన",                  // NOT 'question_text_telugu'
  question_type: "multiple_choice"
}
```

### Results Object
```javascript
{
  overall_score: 75.5,                   // Percentage
  overall_proficiency_level: "intermediate",  // NOT just 'proficiency_level'
  skill_breakdown: {                     // Simple object
    vocabulary: 80                       // NOT nested {percentage: 80}
  }
}
```

---

## 🚦 Status Codes

- `200` - Success
- `201` - Assessment created
- `400` - Bad request (validation error)
- `401` - Unauthorized
- `404` - Assessment not found
- `500` - Server error

---

## 📱 Responsive Breakpoints

- **Desktop**: > 1024px - Full width layout
- **Tablet**: 768px - 1024px - Adjusted spacing
- **Mobile**: < 768px - Single column

---

## 🎯 Assessment Types

| Type | Questions | Duration | Coverage |
|------|-----------|----------|----------|
| Comprehensive | 36 | 45 min | All skills, all levels |
| Quick | 9 | 15 min | Key skills only |
| Adaptive | Variable | 30 min | Adjusts to performance |
| Skill-Specific | Variable | 20 min | One skill area |

---

## 📊 Proficiency Levels

- **Beginner**: < 60% score
- **Intermediate**: 60-80% score
- **Advanced**: > 80% score

---

## 🎉 Quick Win

**Fastest way to test:**
1. Login
2. Go to `/assessment`
3. Click any answer for each question
4. Click "Complete Assessment"
5. See results!

**Total time: 2-3 minutes** ⚡

---

## 📞 Support

- Full docs: `INITIAL_ASSESSMENT_COMPLETE.md`
- Test guide: `ASSESSMENT_TEST_GUIDE.md`
- Summary: `ASSESSMENT_IMPLEMENTATION_SUMMARY.md`

---

**Happy Testing! 🚀**
