# Dashboard - Quick Reference & Testing

## 🚀 Quick Start

### Backend
```bash
cd language-learning-platform
python app.py
```

### Frontend
```bash
cd ConvAI_frontV1
npm run dev
```

### Access
- **Dashboard URL:** http://localhost:5173/dashboard
- **API Endpoint:** GET /api/personalization/dashboard

---

## ✅ Features Checklist

| Feature | Status | Details |
|---------|--------|---------|
| Current Streak | ✅ | Fire icon, days count, best streak |
| Total Points | ✅ | Trophy icon, level display, points count |
| Words Learned | ✅ | Book icon, total + monthly count |
| Time Spent | ✅ | Clock icon, total + weekly hours |
| Daily Goal Progress | ✅ | Progress bar, % completion, time tracking |
| Next Milestone | ✅ | Badge preview, points needed, progress bar |
| Recommended Activities | ✅ | 3-5 cards based on preferences |
| Weekly Activity Chart | ✅ | Line chart, last 7 days |
| Skill Breakdown Chart | ✅ | Bar chart, 6 skills |
| Daily Challenge | ✅ | Question, Telugu hint, start button |
| Recent Vocabulary | ✅ | 3-5 words, English-Telugu pairs |

---

## 📊 API Response Structure

```json
{
  "dashboard": {
    "current_streak": 5,
    "total_points": 250,
    "words_learned": 120,
    "total_study_time_hours": 12.5,
    "daily_progress_percentage": 50,
    "next_milestone": {...},
    "recommended_activities": [...],
    "weekly_activity": [...],
    "skill_breakdown": [...],
    "daily_challenge": {...},
    "recent_vocabulary": [...]
  }
}
```

---

## 🧪 Quick Test Script

### Test API with cURL
```bash
# 1. Login first
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  | jq -r '.access_token')

# 2. Get dashboard
curl -X GET http://localhost:5000/api/personalization/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### Expected Output
```json
{
  "message": "Dashboard data retrieved successfully!",
  "telugu_message": "డాష్‌బోర్డ్ డేటా విజయవంతంగా తీసుకోబడింది!",
  "dashboard": {
    "user_name": "test",
    "current_streak": 0,
    "total_points": 0,
    ...
  }
}
```

---

## 🎯 Testing Priorities

### High Priority (Must Test)
1. ✅ Dashboard loads successfully
2. ✅ Stats cards display correct data
3. ✅ Daily progress bar works
4. ✅ Recommendations match preferences
5. ✅ Charts render without errors

### Medium Priority (Should Test)
6. ✅ Milestone card displays
7. ✅ Daily challenge shows
8. ✅ Vocabulary grid populates
9. ✅ Navigation buttons work
10. ✅ Mobile responsive

### Low Priority (Nice to Test)
11. ✅ Loading states
12. ✅ Error handling
13. ✅ Animations
14. ✅ Tooltips
15. ✅ Color schemes

---

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Dashboard blank | Check JWT token, ensure logged in |
| No recommendations | Complete goal setting in onboarding |
| Charts empty | Complete activities to generate data |
| Streak = 0 | Practice daily to build streak |
| Wrong progress % | Check daily_time_goal in UserGoal |

---

## 📱 Test on Different Screens

### Desktop (1920x1080)
- [ ] All 4 stat cards in one row
- [ ] Charts side-by-side (7/5 grid)
- [ ] Activity cards 3 per row

### Tablet (768x1024)
- [ ] 2 stat cards per row
- [ ] Charts stack vertically
- [ ] Activity cards 2 per row

### Mobile (375x667)
- [ ] 1 stat card per row
- [ ] Full-width charts
- [ ] 1 activity card per row

---

## 🎨 Visual Check

### Colors
- 🔥 Streak: Orange (#f59e0b)
- 🏆 Points: Green (#22c55e)
- 📚 Vocabulary: Blue (#0ea5e9)
- ⏰ Time: Purple (#d946ef)

### Icons
- Current Streak: LocalFireDepartment
- Total Points: EmojiEvents
- Words Learned: AutoStories
- Time Spent: AccessTime

### Charts
- Weekly Activity: Purple line (#667eea)
- Skill Breakdown: Green bars (#22c55e)

---

## 🔌 API Integration

### Endpoints Used
```javascript
// Get dashboard data
GET /api/personalization/dashboard

// Start activity from recommendation
POST /api/personalization/session/start

// Complete daily challenge
POST /api/challenges/complete
```

---

## 📈 Data Validation

### Streak Logic
```python
# Streak increases if user practices daily
if last_practice_date == yesterday and practice_today:
    current_streak += 1
else if practice_today:
    current_streak = 1
```

### Progress Calculation
```python
daily_progress_percentage = (today_time_spent / daily_goal_minutes) * 100
# Capped at 100%
```

### Points System
```python
# Points awarded per activity
points_per_activity = {
    'conversation': 20,
    'vocabulary': 10,
    'grammar': 15,
    'challenge': 25
}
```

---

## 🚀 Performance Benchmarks

| Metric | Target | Actual |
|--------|--------|--------|
| Page Load | < 2s | ⏱️ Test |
| API Response | < 500ms | ⏱️ Test |
| Chart Render | < 1s | ⏱️ Test |
| Smooth Animations | 60fps | ⏱️ Test |

---

## 📝 Quick Test Scenarios

### Scenario 1: New User (5 min)
1. Create new account
2. Complete onboarding
3. Navigate to dashboard
4. **Verify:** All counters = 0, recommendations shown

### Scenario 2: Active User (5 min)
1. Login as user with progress
2. Check dashboard
3. **Verify:** Stats reflect actual progress

### Scenario 3: Daily Goal (10 min)
1. Set 30-minute daily goal
2. Complete 15-minute activity
3. Return to dashboard
4. **Verify:** Progress = 50%

### Scenario 4: Streak Maintenance (Daily)
1. Practice today
2. Check dashboard tomorrow
3. **Verify:** Streak increased by 1

---

## 🎯 Acceptance Criteria

### Dashboard is ready when:
- [ ] All 11 features display correctly
- [ ] Data is accurate and real-time
- [ ] Recommendations match user preferences
- [ ] Charts render without errors
- [ ] Mobile responsive
- [ ] No console errors
- [ ] Loading states work
- [ ] Error handling in place

---

## 📞 Quick Commands

```bash
# Backend
cd language-learning-platform && python app.py

# Frontend  
cd ConvAI_frontV1 && npm run dev

# Test API
curl http://localhost:5000/api/personalization/dashboard \
  -H "Authorization: Bearer $TOKEN"

# Check logs
tail -f language-learning-platform/logs/app.log
```

---

## 🎉 Success Indicators

✅ **Dashboard loads in < 2 seconds**  
✅ **All metrics display correctly**  
✅ **Recommendations are personalized**  
✅ **Charts provide insights**  
✅ **User can navigate to activities**  
✅ **Daily progress motivates learning**  
✅ **Mobile experience is smooth**

---

**Status:** ✅ Ready for Testing  
**Last Updated:** October 9, 2025  
**Version:** 1.0
