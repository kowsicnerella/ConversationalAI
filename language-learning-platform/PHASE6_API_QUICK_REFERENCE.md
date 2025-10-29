# Phase 6: Intelligent Assessment System - API Quick Reference

## 🚀 Base URL
```
http://localhost:5000/api/intelligent-assessment
```

## 🔐 Authentication
All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

---

## 📋 API Endpoints (27 Total)

### 1️⃣ Assessment Management (6 endpoints)

#### Create Assessment
```http
POST /assessments/create
Content-Type: application/json

{
  "title": "Telugu Placement Test",
  "description": "Comprehensive proficiency assessment",
  "assessment_type": "placement",
  "target_language": "Telugu",
  "proficiency_level": "intermediate",
  "skill_areas": ["grammar", "vocabulary", "reading"],
  "is_adaptive": true,
  "duration_minutes": 45,
  "passing_score": 70.0,
  "irt_config": {
    "se_threshold": 0.3,
    "min_questions": 10,
    "max_questions": 40
  }
}
```

#### List Assessments
```http
GET /assessments?assessment_type=placement&target_language=Telugu
```

#### Get Assessment Details
```http
GET /assessments/{assessment_id}
```

#### Update Assessment
```http
PUT /assessments/{assessment_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "is_adaptive": false,
  "passing_score": 75.0
}
```

#### Delete Assessment (Soft Delete)
```http
DELETE /assessments/{assessment_id}
```

---

### 2️⃣ Question Management (6 endpoints)

#### Add Question to Assessment
```http
POST /assessments/{assessment_id}/questions
Content-Type: application/json

{
  "question_text": "What is the Telugu word for 'hello'?",
  "question_type": "multiple_choice",
  "correct_answer": "నమస్కారం",
  "options": ["నమస్కారం", "ధన్యవాదాలు", "మళ్లీ కలుద్దాం"],
  "skill_area": "vocabulary",
  "sub_skills": ["greetings", "basic_words"],
  "difficulty_level": "beginner",
  "irt_params": {
    "discrimination": 1.2,
    "difficulty": -0.5,
    "guessing": 0.25
  },
  "explanation": "నమస్కారం is the formal greeting in Telugu.",
  "context": "Used in formal and respectful situations."
}
```

#### Get Question
```http
GET /assessments/questions/{question_id}
```

#### Update Question
```http
PUT /assessments/questions/{question_id}
Content-Type: application/json

{
  "question_text": "Updated question?",
  "irt_discrimination": 1.5
}
```

#### Delete Question
```http
DELETE /assessments/questions/{question_id}
```

#### Bulk Import Questions
```http
POST /assessments/questions/bulk-import
Content-Type: application/json

{
  "assessment_id": 1,
  "questions": [
    {
      "question_text": "Question 1?",
      "question_type": "multiple_choice",
      "correct_answer": "A",
      "options": ["A", "B", "C"]
    },
    {
      "question_text": "Question 2?",
      "question_type": "fill_in_blank",
      "correct_answer": "answer"
    }
  ]
}
```

---

### 3️⃣ Taking Assessments (5 endpoints)

#### Start Assessment
```http
POST /assessments/{assessment_id}/start
Content-Type: application/json

{
  "initial_theta": 0.5  // Optional
}

Response:
{
  "success": true,
  "attempt_id": 123,
  "is_adaptive": true,
  "duration_minutes": 45,
  "first_question": {
    "question_id": 42,
    "question_text": "...",
    "question_type": "multiple_choice",
    "options": ["A", "B", "C"],
    "skill_area": "vocabulary"
  },
  "current_theta": 0.5
}
```

#### Get Next Question
```http
GET /assessments/attempts/{attempt_id}/next-question

Response:
{
  "success": true,
  "question": {
    "question_id": 43,
    "question_text": "...",
    "options": [...]
  },
  "progress": {
    "questions_answered": 5,
    "current_theta": 0.8,
    "theta_se": 0.4,
    "correct_count": 4
  }
}

// Or when complete:
{
  "success": true,
  "completed": true,
  "message": "Assessment complete. Please submit to see results."
}
```

#### Submit Answer
```http
POST /assessments/attempts/{attempt_id}/submit
Content-Type: application/json

{
  "question_id": 42,
  "user_answer": "నమస్కారం",
  "time_spent_seconds": 25,
  "hints_used": []
}

Response:
{
  "success": true,
  "is_correct": true,
  "explanation": "Correct! నమస్కారం means hello.",
  "correct_answer": null,  // Only shown if incorrect
  "current_theta": 0.9,
  "theta_se": 0.35,
  "probability_correct": 0.82,
  "information": 1.15,
  "questions_answered": 6,
  "correct_count": 5
}
```

#### Complete Assessment
```http
POST /assessments/attempts/{attempt_id}/complete

Response:
{
  "success": true,
  "result": {
    "overall_score": 85.5,
    "proficiency_level": "intermediate",
    "theta_estimate": 0.8,
    "theta_se": 0.25,
    "percentile_rank": 73.5,
    "skill_scores": {
      "grammar": 90.0,
      "vocabulary": 85.0,
      "reading": 80.0
    },
    "strengths": ["grammar", "vocabulary"],
    "weaknesses": ["reading"],
    "learning_gaps": [
      {
        "skill_area": "reading",
        "sub_skill": "comprehension",
        "error_count": 3,
        "severity": "medium"
      }
    ],
    "recommendations": [
      "Focus on improving reading through targeted practice",
      "Challenge yourself with advanced materials while reinforcing basics"
    ],
    "passed": true
  }
}
```

#### Get Attempt Status
```http
GET /assessments/attempts/{attempt_id}/status

Response:
{
  "success": true,
  "attempt": {
    "id": 123,
    "status": "in_progress",
    "questions_answered": 8,
    "correct_count": 6,
    "current_theta": 0.7,
    "theta_se": 0.38,
    "progress_percent": 65,
    "started_at": "2025-10-20T10:30:00Z"
  },
  "assessment": {
    "title": "Telugu Placement Test",
    "is_adaptive": true,
    "duration_minutes": 45
  }
}
```

---

### 4️⃣ Results & Diagnostics (2 endpoints)

#### Get Results
```http
GET /assessments/attempts/{attempt_id}/results

Response:
{
  "success": true,
  "result": {
    "overall_score": 85.5,
    "skill_scores": {...},
    "proficiency_level": "intermediate",
    "theta_estimate": 0.8,
    "percentile_rank": 73.5,
    "strengths": [...],
    "weaknesses": [...],
    "learning_gaps": [...],
    "recommendations": [...]
  },
  "assessment": {
    "title": "Telugu Placement Test",
    "assessment_type": "placement",
    "passing_score": 70.0
  },
  "attempt": {
    "questions_answered": 25,
    "correct_count": 21,
    "started_at": "2025-10-20T10:30:00Z",
    "completed_at": "2025-10-20T11:15:00Z"
  }
}
```

#### Get Skill Diagnostics
```http
GET /assessments/attempts/{attempt_id}/diagnostics

Response:
{
  "success": true,
  "diagnostics": [
    {
      "skill_area": "grammar",
      "score": 90.0,
      "questions_attempted": 10,
      "correct_count": 9,
      "sub_skill_scores": {
        "verb_conjugation": 95.0,
        "noun_cases": 85.0,
        "word_order": 90.0
      },
      "error_patterns": [
        {
          "pattern_type": "difficulty",
          "description": "Most errors on advanced questions",
          "count": 1
        }
      ],
      "improvement_strategies": [
        "Review advanced grammar concepts",
        "Practice more complex sentence structures"
      ]
    },
    {
      "skill_area": "vocabulary",
      "score": 85.0,
      ...
    }
  ],
  "total_skills": 3
}
```

---

### 5️⃣ Analytics & History (3 endpoints)

#### Get My History
```http
GET /assessments/my-history?assessment_id=1

Response:
{
  "success": true,
  "history": [
    {
      "attempt_id": 125,
      "assessment_title": "Telugu Placement Test",
      "assessment_type": "placement",
      "completed_at": "2025-10-20T11:15:00Z",
      "overall_score": 85.5,
      "proficiency_level": "intermediate",
      "theta_estimate": 0.8,
      "questions_answered": 25,
      "correct_count": 21,
      "passed": true
    },
    ...
  ],
  "total": 5
}
```

#### Get Assessment Analytics
```http
GET /assessments/{assessment_id}/analytics

Response:
{
  "success": true,
  "analytics": {
    "assessment_title": "Telugu Placement Test",
    "assessment_type": "placement",
    "total_attempts": 150,
    "average_score": 72.5,
    "average_theta": 0.45,
    "pass_rate": 68.5,
    "proficiency_distribution": {
      "beginner": 20,
      "elementary": 45,
      "intermediate": 60,
      "advanced": 20,
      "expert": 5
    },
    "question_statistics": [
      {
        "question_id": 42,
        "skill_area": "vocabulary",
        "difficulty_level": "intermediate",
        "irt_difficulty": 0.5,
        "empirical_difficulty": 0.48,
        "times_answered": 150,
        "correct_rate": 52.0
      },
      ...
    ],
    "total_questions": 50
  }
}
```

#### Compare Attempts
```http
GET /assessments/compare/{attempt_id_1}/{attempt_id_2}

Response:
{
  "success": true,
  "comparison": {
    "attempt1": {
      "date": "2025-09-15T10:00:00Z",
      "score": 65.0,
      "theta": 0.2,
      "proficiency": "elementary"
    },
    "attempt2": {
      "date": "2025-10-20T10:00:00Z",
      "score": 85.5,
      "theta": 0.8,
      "proficiency": "intermediate"
    },
    "improvements": {
      "score_change": 20.5,
      "score_change_percent": 31.5,
      "theta_change": 0.6,
      "proficiency_improved": true
    },
    "skill_improvements": {
      "grammar": {
        "before": 60.0,
        "after": 90.0,
        "change": 30.0
      },
      "vocabulary": {
        "before": 70.0,
        "after": 85.0,
        "change": 15.0
      },
      "reading": {
        "before": 65.0,
        "after": 80.0,
        "change": 15.0
      }
    }
  }
}
```

---

### 6️⃣ Recommendations & Advanced (3 endpoints)

#### Get Recommendations
```http
GET /assessments/recommendations

Response:
{
  "success": true,
  "recommendations": [
    {
      "assessment": {
        "id": 2,
        "title": "Telugu Progress Check",
        "assessment_type": "progress",
        "duration_minutes": 30
      },
      "reason": "Progress check for intermediate level",
      "priority": "high"
    },
    {
      "assessment": {
        "id": 5,
        "title": "Grammar Mastery Test",
        "assessment_type": "mastery"
      },
      "reason": "Master your strength in grammar",
      "priority": "medium"
    }
  ],
  "total": 3
}
```

#### Check Certification Readiness
```http
GET /assessments/certification-ready?certification_name=Telugu Advanced Certificate

Response:
{
  "success": true,
  "is_ready": true,
  "readiness_score": 85,
  "skill_readiness": {
    "grammar": 90.0,
    "vocabulary": 85.0,
    "reading": 80.0,
    "writing": 82.0
  },
  "missing_skills": [],
  "mastery_assessments_completed": 4,
  "recommendation": "You are ready for certification!"
}

// Or if not ready:
{
  "success": true,
  "is_ready": false,
  "readiness_score": 45,
  "skill_readiness": {
    "grammar": 85.0,
    "vocabulary": 75.0
  },
  "missing_skills": ["reading", "writing"],
  "mastery_assessments_completed": 2,
  "recommendation": "Complete mastery assessments for: reading, writing"
}
```

#### Health Check
```http
GET /assessments/health

Response:
{
  "success": true,
  "status": "healthy",
  "service": "Intelligent Assessment System",
  "features": {
    "irt_adaptive_testing": true,
    "skill_diagnostics": true,
    "multi_stage_assessments": true,
    "analytics": true
  },
  "total_assessments": 15
}
```

---

## 📊 Assessment Types

| Type | Purpose | Typical Use |
|------|---------|-------------|
| **placement** | Determine initial proficiency | Start of learning path |
| **progress** | Track improvement over time | End of modules/chapters |
| **mastery** | Verify topic mastery | Before advancing topics |
| **certification** | Exam simulation | Final certification |

---

## 🎯 Proficiency Levels (Theta Ranges)

| Level | Theta Range | Percentile | Description |
|-------|-------------|------------|-------------|
| **beginner** | -3.0 to -1.0 | 0-16% | Just starting |
| **elementary** | -1.0 to 0.0 | 16-50% | Basic understanding |
| **intermediate** | 0.0 to 1.0 | 50-84% | Average ability |
| **advanced** | 1.0 to 2.0 | 84-98% | Above average |
| **expert** | 2.0 to 3.0 | 98-100% | Mastery level |

---

## 🔬 IRT Parameters

### Question IRT Parameters (3PL Model)

```javascript
{
  "irt_params": {
    "discrimination": 1.2,  // 'a' - How well question differentiates (0.5-2.5)
    "difficulty": 0.5,      // 'b' - Difficulty on theta scale (-3 to +3)
    "guessing": 0.25        // 'c' - Probability of correct guess (0.0-0.5)
  }
}
```

### Adaptive Test Configuration

```javascript
{
  "irt_config": {
    "se_threshold": 0.3,      // Stop when SE below this (precision)
    "min_questions": 10,       // Minimum questions before stopping
    "max_questions": 40,       // Maximum questions
    "stopping_criteria": {     // Advanced stopping
      "min_precision": 0.25,
      "max_ci_width": 0.8,
      "confidence_level": 0.95
    }
  }
}
```

---

## 📝 Question Types

- `multiple_choice` - Select from options
- `fill_in_blank` - Complete the sentence
- `true_false` - True or false
- `short_answer` - Brief text response (LLM evaluated)

---

## 🚦 Workflow Example

### Complete Assessment Flow

```javascript
// 1. Start assessment
POST /assessments/1/start
→ Get attempt_id and first_question

// 2. Loop: Get question and submit answer
while (true) {
  GET /assessments/attempts/123/next-question
  → Get next question or "completed" flag
  
  if (completed) break;
  
  POST /assessments/attempts/123/submit
  → Submit answer, get immediate feedback
}

// 3. Complete assessment
POST /assessments/attempts/123/complete
→ Get comprehensive results

// 4. View diagnostics
GET /assessments/attempts/123/diagnostics
→ Get detailed skill analysis

// 5. Compare with previous attempt
GET /assessments/compare/120/123
→ See improvement over time
```

---

## ⚡ Quick Tips

**Creating Effective Assessments:**
- Use adaptive mode for efficiency (50% fewer questions)
- Set appropriate SE threshold (0.3 = high precision, 0.5 = medium)
- Calibrate IRT parameters based on empirical data
- Cover all target skill areas evenly

**Taking Assessments:**
- Adaptive tests adjust difficulty in real-time
- Early questions have more impact on theta
- Guessing is modeled (don't overthink)
- Standard error decreases as you answer more

**Interpreting Results:**
- Theta is more stable than raw score
- Percentile rank shows relative performance
- Focus on skill diagnostics for improvement
- Learning gaps indicate specific weak sub-skills

---

## 🔧 Error Handling

All endpoints return consistent error format:

```javascript
{
  "success": false,
  "error": "Descriptive error message"
}
```

Common HTTP Status Codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid JWT)
- `403` - Forbidden (not allowed)
- `404` - Not Found
- `500` - Internal Server Error

---

## 📚 Integration Examples

### Frontend Integration (React)

```javascript
// assessmentService.js
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api/intelligent-assessment';

export const assessmentService = {
  // Start assessment
  async startAssessment(assessmentId, initialTheta = null) {
    const response = await axios.post(
      `${API_BASE}/assessments/${assessmentId}/start`,
      { initial_theta: initialTheta },
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    return response.data;
  },
  
  // Get next question
  async getNextQuestion(attemptId) {
    const response = await axios.get(
      `${API_BASE}/assessments/attempts/${attemptId}/next-question`,
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    return response.data;
  },
  
  // Submit answer
  async submitAnswer(attemptId, questionId, answer, timeSpent) {
    const response = await axios.post(
      `${API_BASE}/assessments/attempts/${attemptId}/submit`,
      {
        question_id: questionId,
        user_answer: answer,
        time_spent_seconds: timeSpent
      },
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    return response.data;
  },
  
  // Complete assessment
  async completeAssessment(attemptId) {
    const response = await axios.post(
      `${API_BASE}/assessments/attempts/${attemptId}/complete`,
      {},
      { headers: { Authorization: `Bearer ${getToken()}` } }
    );
    return response.data;
  }
};
```

---

*Author: AI Learning Platform*  
*Date: October 20, 2025*  
*Version: 1.0*
