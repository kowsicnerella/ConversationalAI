# 🚀 Quick Start Testing Guide

## Prerequisites Checklist

### Backend Setup

```powershell
# Navigate to backend directory
cd language-learning-platform

# Activate virtual environment
.\venv1\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Start the backend server
python app.py
```

**Expected:** Backend running on `http://localhost:5000`

### Frontend Setup

```powershell
# Open new terminal, navigate to frontend
cd ConvAI_frontV1

# Install dependencies (if not already installed)
npm install

# Start the frontend development server
npm run dev
```

**Expected:** Frontend running on `http://localhost:5174`

---

## 🧪 Test Scenarios

### Scenario 1: New User Registration & Onboarding

**Goal:** Test the complete flow from registration to assessment

1. **Register New Account**

   - Navigate to `http://localhost:5174/register`
   - Fill in:
     - Username: `testuser`
     - Email: `test@example.com`
     - Password: `Test@123`
   - Click "Register"

   **Expected:** Auto-redirect to `/onboarding`

2. **Onboarding Flow**

   - Should land on **Step 1: Welcome**
   - Click "Next" through steps:
     - Step 1: Welcome (introduction)
     - Step 2: Assessment Info (explains what's coming)
     - Step 3: Take Assessment (should have button to start)
     - Step 4: Results (currently placeholder)
     - Step 5: Choose Path (currently placeholder)
     - Step 6: Get Started (completion)

   **Expected:** Smooth step transitions with animations

3. **Start Assessment** (from Step 3)

   - Click "Start Assessment" button
   - Should navigate to `/assessment`

   **Expected:** Assessment page loads with first question

4. **Complete Assessment**

   - Answer each question (MCQ or text input)
   - Click "Next Question" to progress
   - On last question, click "Complete Assessment"

   **Expected:** Redirect to `/assessment-results` with scores

5. **View Results**

   - See overall score percentage
   - View radar chart with 6 skills
   - Read strengths and weaknesses
   - Click "View Personalized Learning Paths"

   **Expected:** Navigate to `/learning-paths`

---

### Scenario 2: Dashboard Progress Tracking

**Goal:** Verify dashboard displays learning progress

1. **Login**

   - Navigate to `http://localhost:5174/login`
   - Login with: `test@example.com` / `Test@123`

   **Expected:** Smart redirect based on user state

   - If onboarding incomplete → `/onboarding`
   - If assessment pending → `/assessment`
   - If complete → `/dashboard`

2. **Dashboard Overview**

   - Check **Overall Mastery Card** displays:
     - Mastery percentage (should be 0% if no lessons completed)
     - Completed lessons count
   - Check **Current Lesson Card**:
     - Should show if a lesson is in progress
     - "Continue Learning" button present
   - Check **Recent Achievements**:
     - Onboarding completion milestone should appear

   **Expected:** All cards load without errors

3. **Navigate to Mastery Dashboard**

   - Click on Mastery link in navigation (or go to `/mastery`)
   - View detailed progress:
     - Overall mastery %
     - Skill breakdowns (6 skills)
     - Statistics grid
     - Recent achievements

   **Expected:** Comprehensive progress visualization

---

### Scenario 3: Lesson Completion & AI Review (When Integrated)

**Goal:** Test lesson → AI review → next lesson flow

⚠️ **Note:** LessonView component not yet created. This will test the backend APIs.

**Manual API Test:**

```bash
# 1. Complete a lesson
curl -X POST http://localhost:5000/api/lesson/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": 1,
    "activity_id": 1,
    "score": 85,
    "time_spent": 300,
    "activity_type": "quiz"
  }'

# Expected Response:
# {
#   "success": true,
#   "lesson_review": { ... AI feedback ... },
#   "next_lesson": { ... next lesson details ... },
#   "milestone_achieved": { ... if applicable ... }
# }

# 2. Get lesson review
curl http://localhost:5000/api/lesson/review/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. Get next recommended lesson
curl http://localhost:5000/api/lesson/next \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Scenario 4: Onboarding Status API

**Goal:** Verify backend onboarding endpoints

**Test Endpoints:**

```bash
# 1. Get onboarding status
curl http://localhost:5000/api/onboarding/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected Response:
# {
#   "onboarding_completed": false,
#   "current_learning_phase": "onboarding",
#   "needs_initial_assessment": true,
#   "assessment_taken_at": null,
#   "current_step": 1
# }

# 2. Update learning phase
curl -X POST http://localhost:5000/api/onboarding/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "learning_phase": "assessment"
  }'

# 3. Complete onboarding
curl -X POST http://localhost:5000/api/onboarding/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Milestone awarded, onboarding_completed = true

# 4. Get progress snapshot
curl http://localhost:5000/api/onboarding/progress/snapshot \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Comprehensive progress data with mastery metrics
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Backend Not Starting

**Symptoms:** `ModuleNotFoundError` or import errors

**Solutions:**

```powershell
# Ensure virtual environment is activated
cd language-learning-platform
.\venv1\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (should be 3.8+)
python --version
```

### Issue 2: Database Errors

**Symptoms:** `sqlalchemy.exc.OperationalError` or table not found

**Solutions:**

```powershell
# Run migrations
flask db upgrade

# Or reinitialize database
python init_db.py
```

### Issue 3: JWT Token Errors (422 Unprocessable Entity)

**Symptoms:** API returns 422 errors, "Token verification failed"

**Solutions:**

1. Check `.env` file has `JWT_SECRET_KEY` set
2. Clear browser localStorage:
   ```javascript
   // In browser console
   localStorage.clear();
   ```
3. Login again to get fresh token
4. Check token expiry settings in `config.py`

### Issue 4: Frontend API Calls Failing

**Symptoms:** CORS errors, network errors, or 404s

**Solutions:**

1. Ensure backend is running on port 5000
2. Check `ConvAI_frontV1/.env`:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```
3. Restart frontend dev server after .env changes
4. Check browser console for detailed error messages

### Issue 5: Assessment Page Not Loading

**Symptoms:** Blank page or "Failed to load assessment"

**Solutions:**

1. Check if `/api/assessment/generate` endpoint exists (may need to create)
2. Verify user is authenticated (JWT token present)
3. Check backend logs for errors
4. Test endpoint manually:
   ```bash
   curl -X POST http://localhost:5000/api/assessment/generate \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

## 📊 Health Check Endpoints

### Backend Health

```bash
# Check if backend is running
curl http://localhost:5000/api/auth/health
# or
curl http://localhost:5000/

# Check database connection
curl http://localhost:5000/api/health/db
```

### Frontend Health

```bash
# Open in browser
http://localhost:5174/

# Should see landing page without errors
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

**Backend (Flask):**

```python
# In app.py, set debug=True
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**Frontend (Axios):**
Already enabled in `src/config/api.js`:

- Request interceptor logs token presence
- Response interceptor logs status codes
- Check browser console for detailed logs

### Check Database State

```powershell
# Activate venv
cd language-learning-platform
.\venv1\Scripts\Activate.ps1

# Open Python shell
python

# Query database
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     from app.models import User, Milestone, LessonReview
...     users = User.query.all()
...     print(f"Total users: {len(users)}")
...     milestones = Milestone.query.all()
...     print(f"Total milestones: {len(milestones)}")
```

### Monitor Network Traffic

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by XHR/Fetch
4. Perform actions in app
5. Check:
   - Request headers (Authorization token present?)
   - Response status (200 OK? 401 Unauthorized? 422?)
   - Response body (error messages?)

---

## 🎯 Feature Test Matrix

| Feature                 | Endpoint                        | Component             | Status             | Notes                                      |
| ----------------------- | ------------------------------- | --------------------- | ------------------ | ------------------------------------------ |
| User Registration       | `/auth/register`                | Register.jsx          | ✅ Works           | Redirects to onboarding                    |
| User Login              | `/auth/login`                   | Login.jsx             | ✅ Works           | Smart redirect logic                       |
| Onboarding Flow         | `/onboarding/*`                 | Onboarding.jsx        | ⚠️ Partial         | Steps 1-2, 6 work; 3-5 need integration    |
| Initial Assessment      | `/assessment/generate`          | InitialAssessment.jsx | ⚠️ Not Tested      | Endpoint may not exist yet                 |
| Assessment Results      | `/assessment/{id}/results`      | AssessmentResults.jsx | ⚠️ Not Tested      | Depends on assessment completion           |
| Dashboard Progress      | `/onboarding/progress/snapshot` | Dashboard.jsx         | ✅ Ready           | API call added, UI updated                 |
| Mastery Dashboard       | `/onboarding/progress/snapshot` | MasteryDashboard.jsx  | ✅ Ready           | Comprehensive visualization                |
| Lesson Completion       | `/lesson/complete`              | N/A                   | ❌ Pending         | LessonView component not created           |
| AI Lesson Review        | `/lesson/review/{id}`           | LessonReview.jsx      | ✅ Component Ready | Backend service complete                   |
| Adaptive Curation       | `/lesson/next`                  | N/A                   | ❌ Pending         | Backend ready, frontend integration needed |
| Milestone System        | `/onboarding/complete`          | MilestoneModal.jsx    | ✅ Component Ready | Backend complete, modal animates           |
| Learning Path Selection | N/A                             | N/A                   | ❌ Not Created     | LearningPathSelector component needed      |

**Legend:**

- ✅ Works: Fully functional, tested
- ⚠️ Partial: Component exists but needs integration or backend
- ❌ Pending: Not yet implemented
- ⚠️ Not Tested: Code exists but not verified

---

## 📞 Support & Next Steps

### If Everything Works:

1. Complete remaining components (LearningPathSelector, LessonView)
2. Integrate Onboarding → Assessment → Paths flow
3. Add error handling and animations
4. Run full E2E test suite

### If Issues Persist:

1. Check all error messages in console (browser + terminal)
2. Verify all dependencies installed (`pip list`, `npm list`)
3. Confirm environment variables set correctly
4. Review `WORKFLOW_IMPLEMENTATION_STATUS.md` for known issues

### Next Development Priorities:

1. **LearningPathSelector Component** - Allow users to choose learning path
2. **LessonView Component** - Main lesson interface
3. **Onboarding Integration** - Connect assessment to onboarding flow
4. **End-to-End Testing** - Full user journey test

---

**Happy Testing! 🎉**

For detailed implementation status, see `WORKFLOW_IMPLEMENTATION_STATUS.md`
