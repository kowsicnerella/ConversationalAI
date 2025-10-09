# 🚀 Quick Start - Complete Workflow Testing

## Before You Start

### ✅ Checklist

- [ ] Backend server running on `localhost:5000`
- [ ] Frontend server running on `localhost:5174`
- [ ] Database migrated (`flask db upgrade`)
- [ ] Virtual environment activated

---

## 🎯 Fast Track Testing (10 Minutes)

### **1. Start Both Servers** (2 min)

**Terminal 1 - Backend:**

```powershell
cd D:\ConversationalAI\language-learning-platform
.\venv1\Scripts\Activate.ps1
python app.py
```

**Terminal 2 - Frontend:**

```powershell
cd D:\ConversationalAI\ConvAI_frontV1
npm run dev
```

### **2. Register New Account** (1 min)

Navigate to: `http://localhost:5174/register`

```
Email: test@example.com
Username: testuser
Password: Test@123
```

**Expected:** Auto-redirect to `/onboarding`

### **3. Complete Onboarding** (3 min)

- **Step 1:** Welcome screen → Click "Next"
- **Step 2:** Assessment info → Click "Next"
- **Step 3:** Click "Start Assessment" → Navigate to `/assessment`

⚠️ **If assessment endpoint not ready:**

- Manually navigate to `/onboarding` (skip assessment for now)
- Click through remaining steps

### **4. Dashboard Check** (2 min)

Navigate to: `http://localhost:5174/dashboard`

**Verify:**

- [ ] Overall Mastery card displays
- [ ] Current Lesson card shows (if available)
- [ ] Recent Achievements section visible
- [ ] Progress snapshot loads without errors

### **5. Test Lesson Flow** (2 min)

**Option A - If lesson available:**
Click "Continue Learning" → Complete activity → View AI review

**Option B - Manual:**
Navigate to: `http://localhost:5174/lesson`

---

## 🔍 Component Testing

### **Test LearningPathSelector**

1. Complete assessment or mock assessment results
2. Navigate to onboarding step 5
3. Should see recommended learning paths with:
   - Match scores
   - Difficulty chips
   - Enroll buttons

### **Test LessonView**

1. Navigate to `/lesson` (fetches next)
2. Or `/lesson/{id}` (specific lesson)
3. Complete an activity (quiz/flashcards/reading)
4. Should show:
   - Lesson header with gradient
   - Activity component
   - Time tracking
   - Submit/Complete flow

### **Test AI Review**

After completing a lesson:

- Performance score card
- Motivational message (bilingual)
- Strengths/weaknesses
- AI feedback
- Next lesson preview

### **Test Milestone Modal**

Trigger conditions:

- Complete onboarding
- Perfect lesson score (100%)
- 7-day streak
- Mastery milestones (25%, 50%, 75%, 100%)

---

## 🐛 Quick Troubleshooting

### **Issue: Frontend won't start**

```powershell
cd ConvAI_frontV1
rm -r node_modules
npm install
npm run dev
```

### **Issue: Backend errors**

```powershell
cd language-learning-platform
.\venv1\Scripts\Activate.ps1
pip install -r requirements.txt
flask db upgrade
python app.py
```

### **Issue: 422 JWT errors**

```javascript
// In browser console
localStorage.clear();
// Then login again
```

### **Issue: Assessment page blank**

Check if `/api/assessment/generate` endpoint exists:

```bash
curl -X POST http://localhost:5000/api/assessment/generate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **Issue: No lessons loading**

Check if learning path enrollment worked:

```bash
curl http://localhost:5000/api/courses/my-learning-paths \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Success Criteria

### **✅ Onboarding Flow Works**

- All 6 steps render without errors
- Navigation buttons work
- Can reach completion

### **✅ Dashboard Loads**

- Progress snapshot fetches
- Cards display correctly
- No console errors

### **✅ Lesson Flow Works**

- Lesson loads with activity
- Activity can be completed
- Score is calculated
- Time is tracked

### **✅ AI Review Displays**

- Review component shows after completion
- Feedback is visible
- Next lesson preview available
- Continue button works

### **✅ Milestone System**

- Modal appears on achievements
- Confetti animation plays
- Points awarded shown

---

## 📁 File Locations (Quick Reference)

### **New Components (Today)**

```
src/components/LearningPathSelector.jsx  ← Path selection UI
src/pages/LessonView.jsx                 ← Main learning interface
```

### **Updated Components**

```
src/pages/Onboarding.jsx                 ← Integrated path selector
src/pages/Dashboard.jsx                  ← Added progress cards
src/App.jsx                              ← Added lesson routes
src/config/api.js                        ← Updated endpoints
```

### **Backend Services**

```
app/services/lesson_review_service.py    ← AI review generation
app/services/adaptive_lesson_curator.py  ← Next lesson selection
app/api/lesson_routes.py                 ← Lesson endpoints
app/api/onboarding_routes.py             ← Onboarding endpoints
```

---

## 🎯 Test Scenarios

### **Scenario 1: New User Journey**

```
Register → Onboarding → (Assessment) → Path Selection → Dashboard
```

### **Scenario 2: Lesson Completion**

```
Dashboard → Continue Learning → Complete Activity → View Review → Next Lesson
```

### **Scenario 3: Progress Tracking**

```
Dashboard → Mastery Dashboard → View Skills → Recent Achievements
```

### **Scenario 4: Milestone Achievement**

```
Complete Lesson (100%) → Milestone Modal → Confetti → Points Awarded
```

---

## 🔗 Quick Links

| Page        | URL                                        | Purpose          |
| ----------- | ------------------------------------------ | ---------------- |
| Landing     | `http://localhost:5174/`                   | Home page        |
| Register    | `http://localhost:5174/register`           | Account creation |
| Login       | `http://localhost:5174/login`              | User login       |
| Onboarding  | `http://localhost:5174/onboarding`         | 6-step flow      |
| Assessment  | `http://localhost:5174/assessment`         | Initial test     |
| Results     | `http://localhost:5174/assessment-results` | Test results     |
| Dashboard   | `http://localhost:5174/dashboard`          | Main hub         |
| Mastery     | `http://localhost:5174/mastery`            | Progress view    |
| Lesson      | `http://localhost:5174/lesson`             | Next lesson      |
| Lesson (ID) | `http://localhost:5174/lesson/1`           | Specific lesson  |

---

## 💡 Pro Tips

1. **Keep browser console open** - Watch for errors
2. **Check Network tab** - Monitor API calls
3. **Clear localStorage** - If auth issues persist
4. **Check both terminals** - Backend & frontend logs
5. **Use React DevTools** - Inspect component state
6. **Test mobile view** - Toggle device toolbar (F12 → Ctrl+Shift+M)

---

## 📞 Need Help?

### **Check Documentation**

- `COMPLETE_WORKFLOW_SUMMARY.md` - Full feature list
- `TESTING_GUIDE.md` - Detailed testing steps
- `WORKFLOW_IMPLEMENTATION_STATUS.md` - Development status

### **Common Questions**

**Q: Where are the assessment questions?**  
A: Generated by backend `/api/assessment/generate` endpoint

**Q: How do I trigger a milestone?**  
A: Complete onboarding or score 100% on a lesson

**Q: Why isn't the next lesson loading?**  
A: Check if user is enrolled in a learning path

**Q: Can I skip the assessment?**  
A: Yes, manually navigate through onboarding steps

---

**Current Status:** All components implemented, ready for integration testing! ✅

**Time to Test:** ~10 minutes for basic flow, ~30 minutes for comprehensive testing

🚀 **Let's test the complete workflow!**
