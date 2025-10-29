# Critical Fixes Required - Week 2 Start

## Status: 🔴 CRITICAL ISSUES FOUND

---

## Issue 1: LearningNode Attribute Error ✅ **FIXED**

### Problem:
```
Error saving activity: 'LearningNode' object has no attribute 'name'
```

### Root Cause:
- `learning_path_orchestrator.py` uses `node.name` (doesn't exist)
- LearningNode model has `concept_name` field, NOT `name`
- Also used `node.prerequisite_node_ids` which should be `node.prerequisites`

### Solution Applied:
**File:** `app/services/learning_path_orchestrator.py` (Lines 64, 70)

Changed:
```python
concept_focus=node.name,  # ❌ WRONG
prerequisite_concepts=node.prerequisite_node_ids,  # ❌ WRONG
'node_name': node.name,  # ❌ WRONG
```

To:
```python
concept_focus=node.concept_name,  # ✅ CORRECT
prerequisite_concepts=node.prerequisites,  # ✅ CORRECT
'node_name': node.concept_name,  # ✅ CORRECT
```

**Status:** ✅ **FIXED** - Activities will now save correctly

---

## Issue 2: CRUD Endpoints Returning 422 🔴 **NEEDS FIX**

### Problem:
```
127.0.0.1 - - [19/Oct/2025 17:16:08] "GET /api/learning-path/activities/incomplete HTTP/1.1" 422
127.0.0.1 - - [19/Oct/2025 17:16:08] "GET /api/learning-path/spaced-repetition/due HTTP/1.1" 422
```

### Root Cause:
**File:** `app/routes/learning_path_routes.py`

The endpoints are querying the wrong model structure:

```python
# ❌ WRONG CODE (Line 611-614)
activities = Activity.query.filter(
    and_(
        Activity.user_id == current_user_id,  # Activity doesn't have user_id!
        Activity.status.in_(['not_started', 'in_progress'])  # Activity doesn't have status!
    )
).order_by(desc(Activity.created_at)).all()
```

**Reality:**
- `Activity` model has NO `user_id` field
- `Activity` model has NO `status` field
- User-activity relationship is in `UserActivityLog` model
- Status/completion tracked in `UserActivityLog.is_completed` field

### Solution Required:

#### Option A: Query UserActivityLog for incomplete activities
```python
@learning_path_bp.route('/activities/incomplete', methods=['GET'])
@jwt_required()
def get_incomplete_activities():
    """Get incomplete activities for current user."""
    try:
        current_user_id = get_jwt_identity()
        
        # Find activities that user started but didn't complete
        incomplete_logs = UserActivityLog.query.filter(
            UserActivityLog.user_id == current_user_id,
            UserActivityLog.is_completed == False
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        activities_data = []
        for log in incomplete_logs:
            activity = log.activity  # Get related Activity
            activities_data.append({
                "id": activity.id,
                "log_id": log.id,
                "learning_path_id": activity.learning_path_id,
                "activity_type": activity.activity_type,
                "title": activity.title,
                "description": activity.description,
                "content": activity.content,
                "started_at": log.completed_at.isoformat() if log.completed_at else None,
                "generation_metadata": activity.generation_metadata
            })
        
        return jsonify({
            "success": True,
            "data": {
                "activities": activities_data,
                "count": len(activities_data)
            }
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
```

#### Option B: Add user_id and status fields to Activity model
This requires database migration - **NOT RECOMMENDED** for immediate fix.

---

## Issue 3: Spaced Repetition Endpoint (422 Error)

### Problem:
Same query structure issue in `/spaced-repetition/due` endpoint.

### Solution:
Query `UserActivityLog` where `next_review_date <= today` AND `needs_review == True`:

```python
@learning_path_bp.route('/spaced-repetition/due', methods=['GET'])
@jwt_required()
def get_due_reviews():
    """Get activities due for spaced repetition review."""
    try:
        current_user_id = get_jwt_identity()
        today = datetime.utcnow()
        
        # Find logs with due reviews
        due_logs = UserActivityLog.query.filter(
            UserActivityLog.user_id == current_user_id,
            UserActivityLog.needs_review == True,
            UserActivityLog.next_review_date <= today
        ).order_by(UserActivityLog.next_review_date).all()
        
        reviews_data = []
        for log in due_logs:
            activity = log.activity
            days_overdue = (today - log.next_review_date).days if log.next_review_date else 0
            
            reviews_data.append({
                "id": activity.id,
                "log_id": log.id,
                "activity_type": activity.activity_type,
                "title": activity.title,
                "concept_focus": activity.concept_focus,
                "last_completed": log.completed_at.isoformat() if log.completed_at else None,
                "next_review_date": log.next_review_date.isoformat() if log.next_review_date else None,
                "days_overdue": days_overdue,
                "mastery_level": log.mastery_level,
                "last_score": (log.score / log.max_score) if log.max_score else 0,
                "urgency": "high" if days_overdue > 3 else "medium" if days_overdue > 0 else "low"
            })
        
        return jsonify({
            "success": True,
            "data": {
                "due_reviews": reviews_data,
                "count": len(reviews_data)
            }
        }), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
```

---

## Issue 4: Complete Endpoint 404

### Problem:
```
127.0.0.1 - - [19/Oct/2025 17:15:56] "OPTIONS /api/courses/activities/activity_1760874329552/complete HTTP/1.1" 404
```

### Root Cause:
Frontend is calling wrong endpoint path: `/api/courses/activities/{id}/complete`
Backend has: `/api/learning-path/complete-activity`

### Solution:
Either:
1. Update frontend to use correct endpoint
2. OR add route alias to backend

---

## Priority Action Plan

### IMMEDIATE (Fix Now):
1. ✅ Fix `node.name` → `node.concept_name` (DONE)
2. 🔴 Fix `/activities/incomplete` endpoint query
3. 🔴 Fix `/spaced-repetition/due` endpoint query

### URGENT (Next 30 min):
4. Test activity generation → saving → retrieval flow
5. Test resume functionality
6. Test spaced repetition notifications

### HIGH (Today):
7. Fix complete endpoint path mismatch
8. End-to-end integration test
9. Document all fixes

---

## Testing Commands

### Test Activity Generation:
```bash
# Make request to generate activity
curl -X POST http://localhost:5000/api/learning-path/next-activity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Test Incomplete Activities:
```bash
curl -X GET http://localhost:5000/api/learning-path/activities/incomplete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Due Reviews:
```bash
curl -X GET http://localhost:5000/api/learning-path/spaced-repetition/due \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Next Steps After Fixes

1. **Week 2 Planning** - Define remaining features
2. **Feature Prioritization** - What to build next
3. **Code Review** - Clean up and optimize
4. **Documentation** - Update API docs
5. **Testing Strategy** - Create comprehensive test suite

---

## Summary

**Fixed:** 1/4 issues (25%)
**Remaining:** 3 critical issues blocking data persistence UI

**ETA to Fix:** ~30 minutes for endpoint fixes + 15 minutes testing

**Ready for Week 2?** Not yet - need to complete these fixes first!

