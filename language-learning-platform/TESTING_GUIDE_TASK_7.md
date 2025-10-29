# Quick Testing Guide - AI Learning Path Integration

## Prerequisites

1. ✅ Backend server running: `http://localhost:5000`
2. ✅ Database seeded with curriculum (run `python seed_curriculum.py`)
3. ✅ Frontend server running (Vite dev server)
4. ✅ Test user account created

---

## Quick Test Sequence

### Step 1: Start the Backend
```bash
cd D:\ConversationalAI\language-learning-platform
.venv\Scripts\activate  # or `source .venv/bin/activate` on Mac/Linux
python app.py
```

**Expected Output:**
```
* Running on http://127.0.0.1:5000
```

### Step 2: Start the Frontend
```bash
cd D:\ConversationalAI\ConvAI_frontV1
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Step 3: Login
1. Open browser: `http://localhost:5173`
2. Navigate to Login page
3. Login as:
   - **Email:** `test_learner@example.com`
   - **Password:** Your test password
   - OR use any existing user account

### Step 4: Test Activities Page
1. Navigate to `/activities` (or click Activities in nav)
2. **Expected Results:**
   - ✅ Loading spinner appears briefly
   - ✅ AI Learning Assistant banner shows:
     - "Let's work on vocabulary (current: 0%)" or similar
   - ✅ Learning Path Info shows:
     - CEFR Level (A1, A2, B1)
     - Node name (e.g., "Greetings and Introductions")
     - Focus areas tags
   - ✅ Single activity card displays:
     - AI-generated title
     - Description/instructions
     - Estimated time (~15 min)
     - Difficulty level
     - "Start Activity" button

### Step 5: Test Activity Generation
1. Click **"Get Different Activity"** button
2. **Expected Results:**
   - ✅ Loading spinner appears
   - ✅ New activity appears (may be different type)
   - ✅ New orchestrator message explains selection
   - ✅ Node info may change

3. Repeat 2-3 times to see variety

### Step 6: Test Activity Navigation
1. Click **"Start Activity"** button
2. **Expected Results:**
   - ✅ Navigates to activity-specific page:
     - Flashcard → `/activities/flashcards/:id`
     - Quiz → `/activities/quiz/:id`
     - Reading → `/activities/reading/:id`
   - ✅ Activity data passed via state
   - ✅ Activity data also in sessionStorage

---

## What to Look For

### ✅ Success Indicators

1. **No Mock Data**
   - Activity titles are unique and AI-generated
   - Content varies each time you click "Get Different Activity"
   - No repeated "Daily Vocabulary Practice" or other hardcoded titles

2. **Personalization Working**
   - Orchestrator message explains WHY this activity was chosen
   - Messages reference weak areas or current mastery levels
   - Different users see different activities

3. **Beautiful UI**
   - AI Learning Assistant banner with gradient background
   - Learning Path Info section shows current progress context
   - Single centered activity card (not a grid)
   - Smooth animations and transitions

4. **Error Handling**
   - If backend is down, shows empty state with retry button
   - No console errors (except expected CORS/network errors when backend down)

### ❌ Potential Issues

1. **401 Unauthorized Error**
   - **Cause:** JWT token expired or invalid
   - **Fix:** Logout and login again

2. **Empty Activity Card**
   - **Cause:** Curriculum not seeded or user progress not initialized
   - **Fix:** Run `python seed_curriculum.py` in backend

3. **CORS Errors**
   - **Cause:** Backend CORS not configured for frontend origin
   - **Fix:** Check `app/config.py` has correct CORS settings

4. **"No activity available"**
   - **Cause:** Orchestrator couldn't select activity (rare)
   - **Fix:** Click "Get Next Activity" to retry

---

## Console Logs to Check

### Frontend (Browser Console)

**Good Output:**
```javascript
🔑 Request interceptor - Token present: true
📡 Request URL: /learning-path/next-activity
📡 Request Method: post
✅ Authorization header set
✅ Response received: /learning-path/next-activity 200
```

**Bad Output:**
```javascript
❌ Response error: {status: 401, statusText: 'Unauthorized'}
🔒 401 Unauthorized - Clearing auth and redirecting to login
```

### Backend (Terminal)

**Good Output:**
```
INFO:app:POST /api/learning-path/next-activity - User: 1
INFO:app:Orchestrator determined next activity: A1_VOCAB_GREETINGS
INFO:app:Activity generated successfully: flashcard
```

**Bad Output:**
```
ERROR:app:Failed to generate activity: ...
ERROR:app:Orchestrator error: ...
```

---

## Test Matrix

| Test Case | Action | Expected Result | Status |
|-----------|--------|----------------|--------|
| 1. Page Load | Navigate to /activities | Shows personalized activity | ⬜ |
| 2. AI Message | Check banner | Shows reasoning for selection | ⬜ |
| 3. Node Info | Check info section | Shows CEFR level, node, tags | ⬜ |
| 4. Activity Card | Check card content | Shows AI-generated title/desc | ⬜ |
| 5. Refresh Activity | Click "Get Different Activity" | New activity appears | ⬜ |
| 6. Navigation | Click "Start Activity" | Routes to activity page | ⬜ |
| 7. Data Passing | Check sessionStorage | Activity data stored | ⬜ |
| 8. Error Handling | Stop backend, refresh | Shows empty state | ⬜ |
| 9. Retry | Click retry button | Attempts to fetch again | ⬜ |
| 10. Multi-User | Login as different users | Different activities | ⬜ |

---

## Quick Checks

### Check 1: sessionStorage Data
Open browser DevTools → Application → Session Storage → Check for `currentActivity` key

**Expected:**
```json
{
  "id": "activity_1729...",
  "type": "flashcard",
  "title": "Greetings and Introductions Flashcards",
  "content": { "flashcards": [...] },
  "nodeId": "A1_VOCAB_GREETINGS",
  ...
}
```

### Check 2: Network Tab
Open browser DevTools → Network → Filter: XHR

**Expected Request:**
```
POST /api/learning-path/next-activity
Authorization: Bearer eyJ0eXAiOiJKV1...
```

**Expected Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "activity": { ... },
    "reasoning": "Let's work on vocabulary...",
    "node_info": { ... }
  }
}
```

### Check 3: Backend Logs
Check terminal running Flask app

**Expected:**
```
INFO:orchestrator:User 1 - Current level: A1
INFO:orchestrator:Selected node: A1_VOCAB_GREETINGS (priority: weak_area)
INFO:activity_generator:Generating flashcard activity for node A1_VOCAB_GREETINGS
INFO:activity_generator:Successfully generated activity with Gemini
```

---

## Troubleshooting

### Issue: "Loading spinner never stops"

**Possible Causes:**
1. Backend not running
2. Wrong API_BASE_URL in frontend
3. CORS blocking request

**Solutions:**
1. Check backend is running on port 5000
2. Check `VITE_API_BASE_URL` in frontend `.env` file
3. Check browser console for CORS errors

### Issue: "Activities look the same as before"

**Possible Causes:**
1. Changes not deployed (need to rebuild)
2. Browser cache showing old version

**Solutions:**
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Check if you're on the correct branch/commit

### Issue: "404 Not Found on activity click"

**Possible Causes:**
1. Activity type routes not set up
2. Invalid activity ID

**Solutions:**
1. Check routing configuration in frontend
2. Verify activity page components exist for each type

---

## Success Criteria

✅ **Test Passed If:**
1. Page loads without errors
2. Personalized activity appears (not mock data)
3. AI message explains selection reasoning
4. Activity card displays properly
5. "Get Different Activity" generates new content
6. "Start Activity" navigates correctly
7. No console errors (except when testing error states)

❌ **Test Failed If:**
1. Mock data still appears (e.g., "Daily Vocabulary Practice")
2. Page shows empty state on first load
3. Console shows errors
4. Navigation doesn't work
5. Same activity appears every time

---

## Next Steps After Testing

If all tests pass ✅:
1. Mark Task 7 as complete
2. Test with real users
3. Gather feedback
4. Plan Task 8 (Activity Completion Integration)

If tests fail ❌:
1. Check console logs (frontend & backend)
2. Verify backend endpoints are accessible
3. Check JWT token validity
4. Review error messages
5. Debug step-by-step using browser DevTools

---

## Need Help?

### Common Questions

**Q: Do I need to seed the database every time?**  
A: No, only once. The seed data persists in the database.

**Q: Can I test with multiple users?**  
A: Yes! Create different user accounts or use the test script to create test users with different profiles.

**Q: What if I want to change the orchestrator logic?**  
A: Edit `app/services/learning_path_orchestrator.py` and restart the backend.

**Q: How do I reset a user's progress?**  
A: Delete records from `user_learning_path_progress` and `node_completion` tables for that user.

---

*Testing Guide Created: October 19, 2025*  
*For: Task 7 - Frontend Integration*  
*Status: Ready for Testing ✅*
