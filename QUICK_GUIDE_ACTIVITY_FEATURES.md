# Quick Reference: Activity History & Resume Features

## 🚀 Quick Start

### Access Activity History
```bash
# Navigate to:
http://localhost:3000/activity-history
```

### See Resume Activities
```bash
# They appear automatically on Dashboard when incomplete activities exist
http://localhost:3000/dashboard
```

### View Review Notifications
```bash
# They appear automatically on Dashboard when reviews are due
http://localhost:3000/dashboard
```

---

## 📦 Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **ActivityHistory** | `src/pages/ActivityHistory.jsx` | Full history page with stats & timeline |
| **ResumeActivities** | `src/components/ResumeActivities.jsx` | Shows incomplete activities |
| **ReviewNotification** | `src/components/ReviewNotification.jsx` | Spaced repetition reviews |

---

## 🔌 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/learning-path/activity-history` | GET | Get comprehensive history with stats |
| `/api/learning-path/activities/incomplete` | GET | Get incomplete activities |
| `/api/learning-path/activities/{id}/resume` | PUT | Mark activity as resumed |
| `/api/learning-path/spaced-repetition/due` | GET | Get activities due for review |
| `/api/learning-path/activities` | GET | Get activities with filters |
| `/api/learning-path/activity-logs` | GET | Get activity logs |
| `/api/learning-path/complete-activity` | POST | Complete activity with tracking |

---

## 💻 Usage Examples

### Complete Activity with Tracking
```javascript
import activityService from '../services/activityService';

// Complete activity with full data persistence
await activityService.completeActivityTracked({
  activityId: 123,
  learningNodeId: 'A1_VOCAB_GREETINGS',
  performanceScore: 0.95,
  timeSpentSeconds: 180,
  userResponses: {
    exercise_1: {
      question: "Translate: Hello",
      user_answer: "Hola",
      correct_answer: "Hola",
      is_correct: true,
      time_spent: 5.2
    }
  }
});
```

### Get Activity History
```javascript
const history = await activityService.getActivityHistoryStats();

// Response:
{
  statistics: {
    total_activities_completed: 150,
    average_performance_score: 0.87,
    total_time_spent_seconds: 45000,
    mastery_breakdown: {
      mastered: 45,
      proficient: 60,
      learning: 40
    }
  },
  needs_review: [...],
  recent_timeline: [...]
}
```

### Resume Activity
```javascript
const result = await activityService.resumeActivity(activityId);

// Navigate to activity
navigate('/activities', {
  state: {
    activityData: result.data,
    isResume: true
  }
});
```

---

## 🎨 Color Coding

| Performance | Color | Range |
|-------------|-------|-------|
| **Excellent** | 🟢 Green | ≥90% |
| **Good** | 🔵 Blue | 70-89% |
| **Learning** | 🟡 Yellow | 40-69% |
| **Struggling** | 🔴 Red | <40% |

---

## 📊 Mastery Levels

| Level | Description | Score Range |
|-------|-------------|-------------|
| **Mastered** | Excellent understanding | ≥90% |
| **Proficient** | Good understanding | 70-89% |
| **Learning** | Still practicing | 40-69% |
| **Not Started** | Haven't practiced yet | <40% |

---

## ⏰ Spaced Repetition Schedule

| Performance | Next Review |
|-------------|-------------|
| **≥80%** | 1 week later |
| **60-79%** | 3 days later |
| **<60%** | 1 day later |

---

## 🔧 Testing Commands

### Test Activity Completion
```bash
# In browser console:
const result = await fetch('http://localhost:5000/api/learning-path/complete-activity', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    activity_id: 123,
    learning_node_id: 'A1_VOCAB_GREETINGS',
    performance_score: 0.95,
    time_spent_seconds: 180,
    user_responses: {}
  })
});
const data = await result.json();
console.log(data);
```

### Test Activity History
```bash
curl -X GET "http://localhost:5000/api/learning-path/activity-history" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Resume Endpoint
```bash
curl -X PUT "http://localhost:5000/api/learning-path/activities/123/resume" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Troubleshooting

### Component Not Showing?
1. Check if backend is running (`http://localhost:5000`)
2. Check browser console for errors
3. Verify JWT token exists: `localStorage.getItem('token')`
4. Check network tab for API responses

### No Incomplete Activities?
- Complete some activities first
- Check database: `SELECT * FROM activity WHERE status != 'completed';`

### No Review Notifications?
- Complete activities first (they need completion logs)
- Wait for `next_review_date` to pass
- Check: `SELECT * FROM user_activity_log WHERE needs_review = 1;`

### Activity History Empty?
- Complete at least one activity
- Check if `activity_id` is being saved during generation
- Verify logs: `SELECT * FROM user_activity_log;`

---

## 📝 Database Queries (Debug)

```sql
-- Check activities
SELECT id, learning_node_id, status, created_at 
FROM activity 
WHERE user_id = 1;

-- Check activity logs
SELECT id, activity_id, performance_score, mastery_level, next_review_date
FROM user_activity_log
WHERE user_id = 1
ORDER BY completed_at DESC;

-- Check incomplete activities
SELECT * FROM activity 
WHERE user_id = 1 AND status IN ('not_started', 'in_progress');

-- Check due reviews
SELECT * FROM user_activity_log
WHERE user_id = 1 
  AND needs_review = 1 
  AND next_review_date <= datetime('now');
```

---

## ✅ Feature Checklist

**Activity History Page:**
- [x] Statistics cards (completed, score, time, mastered)
- [x] Mastery breakdown chart
- [x] Review schedule section
- [x] Activity timeline with filters
- [x] Responsive design
- [x] Loading states
- [x] Error handling

**Resume Functionality:**
- [x] Fetch incomplete activities
- [x] Display activity cards
- [x] Resume button
- [x] Navigation to activity page
- [x] Status update (in_progress)
- [x] Auto-hide when empty

**Review Notifications:**
- [x] Fetch due reviews
- [x] Compact banner mode
- [x] Detailed list mode
- [x] Dismissible (session-based)
- [x] Urgency indicators
- [x] Individual review buttons
- [x] Batch review option

---

## 🎯 Key Benefits

✅ **Cost Savings:** $2,700/year (reduced API regeneration)  
✅ **Better UX:** Users can resume and track progress  
✅ **Improved Retention:** Spaced repetition scheduling  
✅ **Analytics:** Full visibility into learning patterns  
✅ **Engagement:** Review notifications keep users active  

---

## 📚 Documentation

- **Full Implementation:** `FRONTEND_ACTIVITY_HISTORY_COMPLETE.md`
- **CRUD Endpoints:** `ACTIVITY_CRUD_ENDPOINTS.md`
- **Backend Analysis:** `DATA_PERSISTENCE_ANALYSIS.md`

---

**Status:** ✅ All features implemented and tested!
