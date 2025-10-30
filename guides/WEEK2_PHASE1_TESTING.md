# Week 2 - Phase 1: Testing & Bug Fixes

## Objective
Test all existing features end-to-end, fix critical bugs, and ensure data persistence works correctly.

---

## Test Plan

### Test 1: Activity Generation & Database Persistence ✅

**What to Test:**
1. Generate a new activity via `/api/learning-path/next-activity`
2. Verify activity is saved to `activities` table
3. Verify activity content is complete and valid

**Steps:**
```bash
# 1. Make API call to generate activity
curl -X POST http://localhost:5000/api/learning-path/next-activity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# 2. Check database
sqlite3 d:\ConversationalAI\language-learning-platform\telugu_english_learning.db
SELECT * FROM activities ORDER BY created_at DESC LIMIT 1;
.exit
```

**Expected Result:**
- Activity record exists with all fields populated
- `generation_metadata` contains node info
- `content` field has valid JSON
- No error: "LearningNode object has no attribute 'name'"

---

### Test 2: Activity Completion Flow ✅

**What to Test:**
1. Complete an activity
2. Verify `UserActivityLog` is created
3. Check mastery level calculation
4. Verify spaced repetition date is set

**Steps:**
```bash
# Complete activity
curl -X POST http://localhost:5000/api/learning-path/complete-activity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": 123,
    "learning_node_id": "A1_VOCAB_GREETINGS",
    "performance_score": 0.85,
    "time_spent_seconds": 300,
    "user_responses": {"q1": "correct", "q2": "incorrect"}
  }'

# Check database
sqlite3 telugu_english_learning.db
SELECT * FROM user_activity_logs ORDER BY completed_at DESC LIMIT 1;
```

**Expected Result:**
- UserActivityLog created with correct user_id and activity_id
- `mastery_level` calculated (should be "proficient" for 0.85)
- `next_review_date` set based on score
- `accuracy_score` populated

---

### Test 3: Incomplete Activities Endpoint ✅

**What to Test:**
1. Call `/api/learning-path/activities/incomplete`
2. Verify it returns incomplete activities
3. Check response format matches frontend expectations

**Steps:**
```bash
# Get incomplete activities
curl -X GET http://localhost:5000/api/learning-path/activities/incomplete \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result:**
- HTTP 200 (not 422!)
- Returns activities with `is_completed=False` from UserActivityLog
- Response includes: id, log_id, activity_type, title, content

---

### Test 4: Spaced Repetition Due Reviews ✅

**What to Test:**
1. Call `/api/learning-path/spaced-repetition/due`
2. Verify it returns activities needing review
3. Check urgency calculation

**Steps:**
```bash
# Get due reviews
curl -X GET http://localhost:5000/api/learning-path/spaced-repetition/due \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Result:**
- HTTP 200 (not 422!)
- Returns activities where `next_review_date <= today`
- Includes urgency indicators
- Shows days_overdue

---

### Test 5: Frontend Dashboard Components ✅

**What to Test:**
1. Navigate to Dashboard (http://localhost:5174)
2. Check Resume Activities component loads
3. Check Review Notifications component loads
4. Verify no console errors

**Steps:**
1. Open browser to http://localhost:5174
2. Login with test account
3. Navigate to Dashboard
4. Open browser console (F12)

**Expected Result:**
- Resume Activities section visible (if incomplete activities exist)
- Review Notifications banner shows count
- No JavaScript errors in console
- No 422 errors in Network tab

---

### Test 6: Activity History Page ✅

**What to Test:**
1. Navigate to /activity-history route
2. Check statistics display
3. Verify mastery breakdown
4. Check activity timeline

**Steps:**
1. Click "Activity History" in navigation
2. Verify page loads
3. Check all sections render

**Expected Result:**
- Statistics cards show correct data
- Mastery progress bars display
- Review schedule section visible
- Activity timeline shows recent activities
- All icons display correctly (Material-UI)

---

## Bug Fixes Checklist

### Critical Bugs (Must Fix):

- [x] **Fix 1: LearningNode.name → concept_name**
  - File: `app/services/learning_path_orchestrator.py`
  - Status: ✅ FIXED

- [x] **Fix 2: Incomplete Activities Endpoint**
  - File: `app/routes/learning_path_routes.py`
  - Status: ✅ FIXED

- [ ] **Fix 3: Spaced Repetition Field Mismatches**
  - File: `app/routes/learning_path_routes.py`
  - Fields to check: `learning_node_id`, `performance_score`, `review_count`
  - Status: ⏳ NEEDS VERIFICATION

- [ ] **Fix 4: Activity History Endpoint Field Mismatches**
  - File: `app/routes/learning_path_routes.py`
  - Line 893: References `Activity.user_id` (doesn't exist)
  - Line 894: References `Activity.status` (doesn't exist)
  - Status: 🔴 NEEDS FIX

### Medium Priority Bugs:

- [ ] **Bug: VocabularyWord.created_at Missing**
  - Error: `type object 'VocabularyWord' has no attribute 'created_at'`
  - File: `app/routes/vocabulary_routes.py`
  - Status: 🔴 NEEDS FIX

- [ ] **Bug: Complete Endpoint Path Mismatch**
  - Frontend calls: `/api/courses/activities/{id}/complete`
  - Backend has: `/api/learning-path/complete-activity`
  - Status: 🔴 NEEDS FIX

---

## Execution Order

### **Step 1: Fix Remaining Backend Errors** (30 min)
1. Fix Activity History endpoint query
2. Fix Spaced Repetition field references
3. Fix VocabularyWord model/route

### **Step 2: Test All Endpoints** (20 min)
1. Test activity generation (should work now!)
2. Test completion flow
3. Test incomplete activities
4. Test spaced repetition

### **Step 3: Frontend Testing** (15 min)
1. Test Dashboard components
2. Test Activity History page
3. Verify no console errors

### **Step 4: Database Verification** (10 min)
1. Check activities table
2. Check user_activity_logs table
3. Verify data relationships

### **Step 5: Documentation** (15 min)
1. Document test results
2. Create bug report for remaining issues
3. Update API documentation

---

## Success Criteria

✅ **Phase 1 Complete When:**
- [ ] All critical bugs fixed
- [ ] Activity generation saves to database
- [ ] Completion flow creates UserActivityLog
- [ ] Incomplete activities endpoint returns 200
- [ ] Spaced repetition endpoint returns 200
- [ ] Frontend components load without errors
- [ ] No 422 or 500 errors in backend logs
- [ ] Database has valid activity and log records

---

## Next: Phase 2 - Analytics Dashboard

Once Phase 1 is complete, we'll move to building the Analytics Dashboard with:
- Visual charts (Chart.js or Recharts)
- Performance trends
- Skill breakdown
- Weekly/monthly statistics

**Estimated Time for Phase 1:** 1.5 - 2 hours

Ready to proceed? Let's fix the remaining bugs! 🚀
