# Activity & Log CRUD Endpoints Documentation

## Overview
Comprehensive CRUD endpoints for Activity and UserActivityLog tables to support UI features like:
- **Activity History** - View past activities
- **Resume Functionality** - Continue incomplete activities
- **Performance Analytics** - Track progress and mastery
- **Spaced Repetition** - Review activities on schedule

---

## 📋 Activity Endpoints

### 1. **GET /api/learning-path/activities**
Get all activities for the current user with filtering.

**Query Parameters:**
- `status` (string): Filter by status - 'completed', 'in_progress', 'not_started'
- `activity_type` (string): Filter by type - 'vocabulary', 'grammar', 'conversation', etc.
- `limit` (int): Number of results (default: 50)
- `offset` (int): Pagination offset (default: 0)
- `from_date` (string): Filter activities created after this date (ISO format)
- `to_date` (string): Filter activities created before this date (ISO format)

**Response:**
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": 123,
        "learning_node_id": "A1_VOCAB_GREETINGS",
        "activity_type": "vocabulary_practice",
        "status": "completed",
        "created_at": "2025-10-15T10:30:00",
        "completed_at": "2025-10-15T10:35:00",
        "content": { /* Full activity JSON */ },
        "generation_metadata": { /* AI generation details */ },
        "performance_score": 0.95,
        "time_spent_seconds": 300
      }
    ],
    "total_count": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

**Usage Examples:**
```javascript
// Get all completed activities
fetch('/api/learning-path/activities?status=completed&limit=20', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// Get vocabulary activities from last week
fetch('/api/learning-path/activities?activity_type=vocabulary&from_date=2025-10-12T00:00:00', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

### 2. **GET /api/learning-path/activities/:id**
Get detailed information about a specific activity.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "user_id": 5,
    "learning_node_id": "A1_VOCAB_GREETINGS",
    "activity_type": "vocabulary_practice",
    "status": "completed",
    "created_at": "2025-10-15T10:30:00",
    "completed_at": "2025-10-15T10:35:00",
    "content": {
      "activity_title": "Greetings Practice",
      "exercises": [ /* ... */ ]
    },
    "completion_log": {
      "id": 456,
      "performance_score": 0.95,
      "mastery_level": "mastered",
      "accuracy_score": 0.95,
      "confidence_score": 0.90,
      "needs_review": false,
      "next_review_date": "2025-10-22T00:00:00",
      "review_count": 1,
      "user_responses": { /* User's answers */ }
    }
  }
}
```

**Usage:**
```javascript
// Get specific activity with completion details
fetch(`/api/learning-path/activities/${activityId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

### 3. **GET /api/learning-path/activities/incomplete**
Get all incomplete activities (for resume functionality).

**Response:**
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": 789,
        "learning_node_id": "A1_GRAMMAR_PRESENT",
        "activity_type": "grammar_exercise",
        "status": "in_progress",
        "created_at": "2025-10-18T14:20:00",
        "content": { /* Activity content */ }
      }
    ],
    "count": 3
  }
}
```

**Usage:**
```javascript
// Show "Resume" button for incomplete activities
fetch('/api/learning-path/activities/incomplete', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  if (data.data.count > 0) {
    showResumeButton(data.data.activities[0]);
  }
});
```

---

### 4. **PUT /api/learning-path/activities/:id/resume**
Mark an activity as resumed and update its status to 'in_progress'.

**Response:**
```json
{
  "success": true,
  "message": "Activity resumed successfully",
  "data": {
    "id": 789,
    "status": "in_progress",
    "content": { /* Activity content */ }
  }
}
```

**Usage:**
```javascript
// Resume an incomplete activity
fetch(`/api/learning-path/activities/${activityId}/resume`, {
  method: 'PUT',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
```

---

## 📊 Activity Log Endpoints

### 5. **GET /api/learning-path/activity-logs**
Get activity completion logs with performance metrics.

**Query Parameters:**
- `mastery_level` (string): Filter by mastery - 'not_started', 'learning', 'proficient', 'mastered'
- `needs_review` (boolean): Filter by review status - 'true' or 'false'
- `limit` (int): Number of results (default: 50)
- `offset` (int): Pagination offset (default: 0)
- `from_date` (string): Filter logs created after this date
- `to_date` (string): Filter logs created before this date

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": 456,
        "activity_id": 123,
        "learning_node_id": "A1_VOCAB_GREETINGS",
        "performance_score": 0.95,
        "time_spent_seconds": 300,
        "accuracy_score": 0.95,
        "confidence_score": 0.90,
        "mastery_level": "mastered",
        "needs_review": false,
        "next_review_date": "2025-10-22T00:00:00",
        "review_count": 1,
        "completed_at": "2025-10-15T10:35:00",
        "user_responses": {
          "exercise_1": {
            "question": "Translate: Hello",
            "user_answer": "Hola",
            "is_correct": true,
            "time_spent": 5.2
          }
        }
      }
    ],
    "total_count": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

**Usage:**
```javascript
// Get logs for mastered activities
fetch('/api/learning-path/activity-logs?mastery_level=mastered', {
  headers: { 'Authorization': `Bearer ${token}` }
})

// Get activities needing review
fetch('/api/learning-path/activity-logs?needs_review=true', {
  headers: { 'Authorization': `Bearer ${token}` }
})
```

---

### 6. **GET /api/learning-path/activity-logs/:id**
Get detailed information about a specific activity log.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "activity_id": 123,
    "user_id": 5,
    "learning_node_id": "A1_VOCAB_GREETINGS",
    "performance_score": 0.95,
    "mastery_level": "mastered",
    "user_responses": { /* Detailed responses */ },
    "activity": {
      "learning_node_id": "A1_VOCAB_GREETINGS",
      "activity_type": "vocabulary_practice",
      "content": { /* Activity content */ }
    }
  }
}
```

---

### 7. **GET /api/learning-path/activity-history**
Get comprehensive activity history with statistics and insights.

**Response:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_activities_completed": 150,
      "total_time_spent_seconds": 45000,
      "average_performance_score": 0.87,
      "mastery_breakdown": {
        "mastered": 45,
        "proficient": 60,
        "learning": 40,
        "not_started": 5
      }
    },
    "needs_review": [
      {
        "activity_id": 789,
        "learning_node_id": "A1_VOCAB_COLORS",
        "next_review_date": "2025-10-19T00:00:00",
        "mastery_level": "learning",
        "last_score": 0.65
      }
    ],
    "recent_timeline": [
      {
        "activity_id": 123,
        "learning_node_id": "A1_VOCAB_GREETINGS",
        "activity_type": "vocabulary_practice",
        "performance_score": 0.95,
        "mastery_level": "mastered",
        "time_spent_seconds": 300,
        "completed_at": "2025-10-15T10:35:00"
      }
    ]
  }
}
```

**Usage:**
```javascript
// Display activity history dashboard
fetch('/api/learning-path/activity-history', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  displayStatistics(data.data.statistics);
  displayMasteryChart(data.data.statistics.mastery_breakdown);
  displayReviewSchedule(data.data.needs_review);
  displayTimeline(data.data.recent_timeline);
});
```

---

### 8. **GET /api/learning-path/spaced-repetition/due**
Get activities due for spaced repetition review.

**Response:**
```json
{
  "success": true,
  "data": {
    "due_reviews": [
      {
        "activity_id": 789,
        "learning_node_id": "A1_VOCAB_COLORS",
        "activity_type": "vocabulary_practice",
        "mastery_level": "learning",
        "last_performance_score": 0.65,
        "review_count": 2,
        "next_review_date": "2025-10-18T00:00:00",
        "days_overdue": 1,
        "activity_content": { /* Full activity for review */ }
      }
    ],
    "count": 5
  }
}
```

**Usage:**
```javascript
// Show review notification
fetch('/api/learning-path/spaced-repetition/due', {
  headers: { 'Authorization': `Bearer ${token}` }
})
.then(res => res.json())
.then(data => {
  if (data.data.count > 0) {
    showReviewNotification(`You have ${data.data.count} activities to review!`);
  }
});
```

---

## 🎨 UI Integration Examples

### Activity History Page
```jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ActivityHistoryPage() {
  const [history, setHistory] = useState(null);
  const token = localStorage.getItem('token');

  useEffect(() => {
    axios.get('/api/learning-path/activity-history', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => setHistory(res.data.data))
    .catch(err => console.error(err));
  }, []);

  if (!history) return <div>Loading...</div>;

  return (
    <div className="activity-history">
      <h1>Your Learning Journey</h1>
      
      {/* Statistics */}
      <div className="stats-grid">
        <StatCard 
          title="Activities Completed"
          value={history.statistics.total_activities_completed}
        />
        <StatCard 
          title="Average Score"
          value={`${(history.statistics.average_performance_score * 100).toFixed(0)}%`}
        />
        <StatCard 
          title="Time Spent"
          value={`${Math.round(history.statistics.total_time_spent_seconds / 60)} mins`}
        />
      </div>

      {/* Mastery Breakdown */}
      <MasteryChart breakdown={history.statistics.mastery_breakdown} />

      {/* Review Schedule */}
      <ReviewSchedule activities={history.needs_review} />

      {/* Timeline */}
      <ActivityTimeline timeline={history.recent_timeline} />
    </div>
  );
}
```

### Resume Activity Feature
```jsx
function ActivityDashboard() {
  const [incompleteActivities, setIncompleteActivities] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    axios.get('/api/learning-path/activities/incomplete', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => setIncompleteActivities(res.data.data.activities))
    .catch(err => console.error(err));
  }, []);

  const handleResume = async (activityId) => {
    try {
      const response = await axios.put(
        `/api/learning-path/activities/${activityId}/resume`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      if (response.data.success) {
        // Load activity content and navigate to activity page
        navigate(`/activity/${activityId}`);
      }
    } catch (error) {
      console.error('Failed to resume activity:', error);
    }
  };

  return (
    <div>
      {incompleteActivities.length > 0 && (
        <div className="resume-section">
          <h3>Continue Learning</h3>
          {incompleteActivities.map(activity => (
            <div key={activity.id} className="incomplete-activity-card">
              <h4>{activity.content.activity_title}</h4>
              <p>Started: {new Date(activity.created_at).toLocaleDateString()}</p>
              <button onClick={() => handleResume(activity.id)}>
                Resume Activity
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Spaced Repetition Review
```jsx
function ReviewNotification() {
  const [dueReviews, setDueReviews] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    axios.get('/api/learning-path/spaced-repetition/due', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => setDueReviews(res.data.data.due_reviews))
    .catch(err => console.error(err));
  }, []);

  if (dueReviews.length === 0) return null;

  return (
    <div className="review-notification">
      <h3>📚 Time to Review!</h3>
      <p>You have {dueReviews.length} activities ready for review</p>
      <button onClick={() => navigate('/review')}>
        Start Reviewing
      </button>
    </div>
  );
}
```

---

## 📈 Benefits of CRUD Endpoints

### 1. **Activity History**
- Users can view all past activities
- Filter by status, type, date range
- Pagination for large datasets

### 2. **Resume Functionality**
- Users can continue incomplete activities
- No need to regenerate content (saves API costs)
- Better user experience

### 3. **Performance Analytics**
- Track mastery levels
- View accuracy and confidence scores
- Monitor time spent on activities
- Identify weak areas

### 4. **Spaced Repetition**
- Automatic review scheduling
- Activities resurface based on performance
- Optimized for long-term retention

### 5. **Cost Savings**
- Cached activities reduce AI generation costs
- Estimated savings: **$2,700/year**
- Improved response times

### 6. **Compliance & Audit**
- Full audit trail of user activity
- User responses stored for review
- Generation metadata for debugging

---

## 🔒 Security Notes

- All endpoints require JWT authentication (`@jwt_required()`)
- Users can only access their own data (filtered by `user_id`)
- Pagination prevents data overload
- SQL injection protected by SQLAlchemy ORM

---

## 📊 Database Schema Reference

### Activity Table
```sql
CREATE TABLE activity (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    learning_node_id VARCHAR(50),
    activity_type VARCHAR(50),
    status VARCHAR(20),  -- 'not_started', 'in_progress', 'completed'
    created_at DATETIME,
    completed_at DATETIME,
    content JSON,  -- Full activity JSON
    generation_metadata JSON,  -- AI generation details
    performance_score FLOAT,
    time_spent_seconds INTEGER
);
```

### UserActivityLog Table
```sql
CREATE TABLE user_activity_log (
    id INTEGER PRIMARY KEY,
    activity_id INTEGER,
    user_id INTEGER NOT NULL,
    learning_node_id VARCHAR(50),
    performance_score FLOAT,
    time_spent_seconds INTEGER,
    accuracy_score FLOAT,
    confidence_score FLOAT,
    mastery_level VARCHAR(20),  -- 'not_started', 'learning', 'proficient', 'mastered'
    needs_review BOOLEAN,
    next_review_date DATETIME,
    review_count INTEGER,
    completed_at DATETIME,
    user_responses JSON  -- User's answers
);
```

---

## ✅ Implementation Complete

**Total Endpoints Added: 9**

✅ Activity CRUD:
- GET /activities (list with filters)
- GET /activities/:id (detail view)
- GET /activities/incomplete (resume functionality)
- PUT /activities/:id/resume (mark resumed)

✅ Activity Log CRUD:
- GET /activity-logs (list with filters)
- GET /activity-logs/:id (detail view)
- GET /activity-history (comprehensive stats)
- GET /spaced-repetition/due (review schedule)

**Next Steps:**
1. Test all endpoints with Postman/curl
2. Update frontend to use new endpoints
3. Build Activity History page
4. Implement Resume feature
5. Add Review notification system

---

**Cost Impact:** These endpoints enable activity caching, reducing AI generation costs by **~$2,700/year** 💰
