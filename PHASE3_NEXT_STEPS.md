# Phase 3 Implementation - Next Steps

**Current Status**: Core components complete (3 of 8 tasks)  
**Time to completion**: ~8-10 hours  
**Next action**: Complete API routes

---

## 📋 Immediate Action Items (Today)

### Task 4: Complete API Routes (⏳ IN PROGRESS)
**Estimated time**: 1-2 hours  
**Status**: Started, needs completion  
**Blocking**: Everything else

#### What to do:
1. Edit `app/routes/learning_path_routes.py`
2. Add 9 endpoints for Phase 3

#### Endpoints to add:

**1. GET Next Activity**
```http
POST /api/learning-path/next-activity
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "user_id": 123,
  "preferred_skill": "optional_string"
}

Response:
{
  "activity_id": 456,
  "activity_type": "listening_comprehension",
  "title": "Cafe Ordering Dialogue",
  "difficulty": 0.65,
  "estimated_duration": 5,
  "skill_domain": "listening",
  "reason": "Due for spaced repetition review",
  "difficulty_explanation": "Based on 78% recent accuracy"
}
```

**2. Plan Learning Session**
```http
POST /api/learning-path/plan-session
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "user_id": 123,
  "duration_minutes": 30
}

Response:
{
  "session_id": "session_789",
  "total_duration": 30,
  "activities": [
    {
      "sequence": 1,
      "activity_id": 1001,
      "phase": "warmup",
      "duration": 5,
      "difficulty": 0.35,
      "title": "Easy vocab review"
    },
    {
      "sequence": 2,
      "activity_id": 1002,
      "phase": "main",
      "duration": 15,
      "difficulty": 0.65,
      "title": "Dialogue comprehension"
    },
    {
      "sequence": 3,
      "activity_id": 1003,
      "phase": "cooldown",
      "duration": 10,
      "difficulty": 0.50,
      "title": "Vocabulary reinforcement"
    }
  ]
}
```

**3. Adjust Difficulty**
```http
POST /api/learning-path/adjust-difficulty
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "activity_id": 456,
  "accuracy": 0.88,
  "response_time_seconds": 8.5,
  "error_count": 1
}

Response:
{
  "current_difficulty": 0.65,
  "new_difficulty": 0.80,
  "adjustment": "+0.15",
  "recommendation": "increase",
  "reason": "Accuracy 88% > 85% threshold"
}
```

**4. Get Skill Level**
```http
GET /api/learning-path/skill-level?user_id=123&skill=listening
Authorization: Bearer {token}

Response:
{
  "user_id": 123,
  "skill": "listening",
  "level": 75,
  "trend": "improving",
  "confidence": 0.82,
  "days_to_mastery": 45
}
```

**5. Get Challenge Curve**
```http
GET /api/learning-path/challenge-curve?user_id=123&duration=30
Authorization: Bearer {token}

Response:
{
  "session_duration": 30,
  "activities": [
    {
      "phase": "warmup",
      "difficulty": 0.35,
      "duration": 5,
      "target_accuracy": 0.85
    },
    {
      "phase": "main",
      "difficulty": 0.65,
      "duration": 15,
      "target_accuracy": 0.75
    },
    {
      "phase": "cooldown",
      "difficulty": 0.50,
      "duration": 10,
      "target_accuracy": 0.80
    }
  ]
}
```

**6. Get Skill Trajectory**
```http
GET /api/learning-path/skill-trajectory/listening?user_id=123
Authorization: Bearer {token}

Response:
{
  "skill": "listening",
  "current_level": 75,
  "trend": "improving",
  "trend_details": {
    "7_day_avg": 74,
    "30_day_avg": 71,
    "improvement_rate": 0.4,
    "days_to_mastery": 45
  },
  "historical": {
    "highest": 82,
    "lowest": 52,
    "average": 68
  }
}
```

**7. Get Difficulty Recommendation**
```http
POST /api/learning-path/difficulty-recommendation
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "activity_id": 456,
  "accuracy": 0.65,
  "response_time_seconds": 25,
  "error_count": 5
}

Response:
{
  "recommendation": "decrease",
  "current_difficulty": 0.65,
  "suggested_difficulty": 0.55,
  "reasons": [
    "Accuracy 65% < 70% threshold",
    "Response time 25s > ideal 15s",
    "Error count 5 > acceptable 3"
  ]
}
```

**8. Get Learning Nodes**
```http
GET /api/learning-path/learning-nodes?user_id=123&level=A1&skill=listening
Authorization: Bearer {token}

Response:
{
  "level": "A1",
  "skill": "listening",
  "nodes": [
    {
      "node_id": "A1_GREETING_001",
      "title": "Basic Greetings",
      "status": "mastered",
      "mastery_level": 0.92,
      "difficulty_range": [0.10, 0.40],
      "estimated_duration": 10
    },
    {
      "node_id": "A1_GREETING_002",
      "title": "Formal vs Informal",
      "status": "in_progress",
      "mastery_level": 0.45,
      "difficulty_range": [0.20, 0.50],
      "estimated_duration": 12
    }
  ]
}
```

**9. Get Node Progress**
```http
GET /api/learning-path/node-progress/A1_GREETING_001?user_id=123
Authorization: Bearer {token}

Response:
{
  "node_id": "A1_GREETING_001",
  "user_id": 123,
  "status": "mastered",
  "mastery_level": 0.92,
  "attempts": 4,
  "last_accessed": "2025-10-19T14:30:00Z",
  "first_completed": "2025-10-12T10:15:00Z",
  "review_schedule": {
    "next_review_date": "2025-10-22T00:00:00Z",
    "review_stage": 2
  },
  "performance": {
    "average_accuracy": 0.88,
    "best_accuracy": 0.95,
    "worst_accuracy": 0.78
  }
}
```

---

## 🛠️ Implementation Guide for Routes

### Step 1: Open the file
```
app/routes/learning_path_routes.py
```

### Step 2: Add imports at top (if not already present)
```python
from app.services.learning_path_orchestrator import LearningPathOrchestrator
from app.services.adaptive_difficulty_engine import AdaptiveDifficultyEngine
from flask import jsonify, request
```

### Step 3: Create blueprint (if not exists)
```python
learning_path_bp = Blueprint('learning_path', __name__)
orchestrator = LearningPathOrchestrator()
engine = AdaptiveDifficultyEngine()
```

### Step 4: Add each endpoint
For example, next-activity endpoint:

```python
@learning_path_bp.route('/api/learning-path/next-activity', methods=['POST'])
@token_required
def get_next_activity(current_user):
    try:
        data = request.get_json()
        user_id = data.get('user_id') or current_user.id
        
        # Get next activity from orchestrator
        next_activity = orchestrator.determine_next_activity(user_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'activity_id': next_activity.id,
                'activity_type': next_activity.activity_type,
                'title': next_activity.title,
                'difficulty': next_activity.difficulty,
                'estimated_duration': next_activity.estimated_duration_seconds,
                'skill_domain': next_activity.skill_domain,
                'reason': 'Recommendation from learning path orchestrator'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### Step 5: Register blueprint in app/__init__.py
```python
from app.routes.learning_path_routes import learning_path_bp
app.register_blueprint(learning_path_bp)
```

---

## 📊 Task Breakdown (Next 8 Hours)

| Task | Time | Status | Notes |
|------|------|--------|-------|
| Add 9 API endpoints | 1-2 hrs | ⏳ TODO | Implement all routes above |
| Create DB migration | 1 hr | ⏳ TODO | Alembic + 5 models |
| Seed CEFR data | 1 hr | ⏳ TODO | A1-C2 levels + skill domains |
| Create unit tests | 2-3 hrs | ⏳ TODO | 80%+ coverage target |
| Create integration tests | 1-2 hrs | ⏳ TODO | Phase 2 ↔ Phase 3 |
| Documentation | 1-2 hrs | ⏳ TODO | API docs + guides |
| **Total** | **8-10 hrs** | | |

---

## 🚀 How to Continue

### Next Session Plan:

1. **First 30 minutes**: Complete API routes (Task 4)
   - Add all 9 endpoints to `learning_path_routes.py`
   - Register blueprint in app/__init__.py
   - Quick manual test of each endpoint

2. **Next 1.5 hours**: Database migrations (Task 5)
   - Create Alembic migration: `flask db migrate -m "Phase 3: Learning nodes"`
   - Run migration: `flask db upgrade`
   - Seed CEFR levels (A1-C2) and skill domains

3. **Next 2-3 hours**: Create test suite (Task 6)
   - Unit tests for orchestrator (all 4 priority levels)
   - Unit tests for difficulty engine (all rules)
   - Integration tests (Phase 2 ↔ Phase 3)

4. **Last 1-2 hours**: Documentation (Task 8)
   - API endpoint documentation
   - Architecture diagrams
   - Frontend integration guide

---

## 🎯 Testing Checklist (After Implementation)

### API Routes Testing
- [ ] POST /next-activity - Returns next optimal activity
- [ ] POST /plan-session - Returns 3-activity session plan
- [ ] POST /adjust-difficulty - Returns difficulty adjustment
- [ ] GET /skill-level - Returns 0-100 skill score
- [ ] GET /challenge-curve - Returns difficulty progression
- [ ] GET /skill-trajectory/:skill - Returns improvement analysis
- [ ] POST /difficulty-recommendation - Returns adjustment recommendation
- [ ] GET /learning-nodes - Returns available nodes
- [ ] GET /node-progress/:id - Returns user's node progress

### Decision Algorithm Testing
- [ ] Priority 1 (Review due) - Selects node past review date
- [ ] Priority 2 (Current node) - Continues unfinished node
- [ ] Priority 3 (Progression) - Next node in curriculum
- [ ] Priority 4 (Weak area) - Targets low-scoring skill

### Difficulty Adjustment Testing
- [ ] Accuracy > 85% - Increases difficulty (+0.15)
- [ ] Accuracy < 60% - Decreases difficulty (-0.15)
- [ ] 80-85% range - Slight increase (+0.075)
- [ ] 60-70% range - Slight decrease (-0.075)

### Session Planning Testing
- [ ] Warm-up phase - Difficulty 0.30-0.40
- [ ] Main phase - Progressive difficulty
- [ ] Cool-down phase - Difficulty 0.50
- [ ] Duration allocation - 5-15-10 for 30 min session

---

## 📁 Files to Create/Modify

### To Create
1. **Tests** - `app/tests/test_phase3_learning_path.py` (500+ lines)
   - Unit tests for orchestrator
   - Unit tests for difficulty engine
   - Integration tests
   - Edge case tests

2. **Seeds** - `app/seeds/phase3_seed.py` (200+ lines)
   - CEFR levels (6 records)
   - Skill domains (6 records)
   - Sample learning nodes (50+ records)

3. **Migration** - `migrations/versions/xxxx_phase3_learning_nodes.py`
   - Create 5 new tables
   - Add relationships and constraints

### To Modify
1. **Routes** - `app/routes/learning_path_routes.py`
   - Add 9 Phase 3 endpoints
   - Register blueprint

2. **Init** - `app/__init__.py`
   - Register learning_path_bp
   - Include seeding script

---

## 🧪 Quick Test Commands (After Implementation)

```bash
# Test API endpoint
curl -X POST http://localhost:5000/api/learning-path/next-activity \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Run all tests
pytest app/tests/test_phase3_learning_path.py -v

# Run with coverage
pytest app/tests/test_phase3_learning_path.py --cov=app.services --cov=app.models

# Database migration
flask db migrate -m "Phase 3: Learning nodes"
flask db upgrade

# Seed data
python app/seeds/phase3_seed.py
```

---

## 📚 Reference Documents

**For Implementation**:
- ✅ `PHASE3_IMPLEMENTATION_STARTED.md` - Overview of Phase 3
- ✅ `PHASE3_COMPONENTS_SUMMARY.md` - Detailed component breakdown
- ✅ `PHASE3_QUICK_REFERENCE.md` - Quick reference guide
- ✅ `PROJECT_STATUS_OCTOBER_19.md` - Overall project status

**After Implementation**:
- Create API documentation (endpoint reference)
- Create integration guide (for frontend devs)
- Create troubleshooting guide

---

## ✨ Success Criteria

Phase 3 will be **COMPLETE** when:

✅ All 9 API endpoints implemented and tested  
✅ Database migrations created and run  
✅ CEFR levels and skill domains seeded  
✅ Comprehensive test suite passing (80%+ coverage)  
✅ Phase 2 ↔ Phase 3 integration verified  
✅ API documentation created  
✅ All TODO items marked complete  

---

## 🎓 Learning Path is Now...

**Smart** - AI chooses optimal next activity  
**Adaptive** - Difficulty adjusts to performance  
**Personalized** - Unique path for each user  
**Structured** - Sessions planned with phases  
**Effective** - Weak areas get reinforcement  
**Engaging** - Right difficulty (75% accuracy sweet spot)  

---

**Next Action**: Complete API routes (Task 4)  
**Estimated Time**: 1-2 hours  
**File to Edit**: `app/routes/learning_path_routes.py`  
**Then**: Database migrations + seeding
