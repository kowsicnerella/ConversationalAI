# Phase 7: Complete API Reference Guide

## Overview
**API Base URL**: `/api/learning-analytics`  
**Authentication**: JWT Bearer Token (required for all endpoints except health)  
**Content-Type**: `application/json`  
**Response Format**: JSON

---

## Table of Contents
1. [Authentication](#authentication)
2. [Weekly Reports](#weekly-reports)
3. [Progress Visualization](#progress-visualization)
4. [Predictions](#predictions)
5. [Comparisons](#comparisons)
6. [Velocity & Momentum](#velocity--momentum)
7. [Insights & Patterns](#insights--patterns)
8. [Study Sessions](#study-sessions)
9. [Progress Snapshots](#progress-snapshots)
10. [Health Check](#health-check)
11. [Error Codes](#error-codes)

---

## Authentication

All API endpoints (except `/health`) require JWT authentication.

**Header Format**:
```http
Authorization: Bearer <your_jwt_token>
```

**Getting JWT Token**:
Token is obtained from login endpoint and stored in `localStorage`.

**Example**:
```javascript
const token = localStorage.getItem('token');
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

---

## Weekly Reports

### 1. Get Weekly Report
**Endpoint**: `GET /api/learning-analytics/weekly-report`  
**Auth**: Required  
**Description**: Get weekly learning report with AI insights

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `week_offset` | integer | No | 0 | Weeks back from current (0=this week, 1=last week) |

**Request Example**:
```http
GET /api/learning-analytics/weekly-report?week_offset=0
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "id": 1,
  "user_id": 123,
  "week_start": "2025-10-15",
  "week_end": "2025-10-21",
  "total_study_time": 420,
  "activities_completed": 15,
  "total_points": 1250,
  "consistency_score": 0.85,
  "streak_days": 7,
  "study_time_change": 15.5,
  "ai_insights": "Excellent consistency this week...",
  "strengths": ["Reading comprehension", "Vocabulary retention"],
  "areas_for_improvement": ["Speaking practice", "Grammar accuracy"],
  "recommendations": ["Practice speaking 20min daily", "Review grammar rules"],
  "achievements": ["7-day streak", "1000+ points"]
}
```

**Error Responses**:
- `401 Unauthorized`: Missing/invalid JWT token
- `404 Not Found`: No report found for the specified week
- `500 Internal Server Error`: Server error

---

### 2. Get Historical Weekly Reports
**Endpoint**: `GET /api/learning-analytics/weekly-reports`  
**Auth**: Required  
**Description**: Get list of historical weekly reports

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of reports to return |

**Request Example**:
```http
GET /api/learning-analytics/weekly-reports?limit=5
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
[
  {
    "id": 3,
    "week_start": "2025-10-15",
    "week_end": "2025-10-21",
    "total_study_time": 420,
    "activities_completed": 15,
    "total_points": 1250
  },
  {
    "id": 2,
    "week_start": "2025-10-08",
    "week_end": "2025-10-14",
    "total_study_time": 365,
    "activities_completed": 12,
    "total_points": 980
  }
]
```

---

## Progress Visualization

### 3. Get Progress Visualization Data
**Endpoint**: `GET /api/learning-analytics/progress-visualization`  
**Auth**: Required  
**Description**: Get comprehensive progress data for charts

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `time_range` | string | No | `30d` | Time range: `7d`, `30d`, `90d`, `1y`, `all` |

**Request Example**:
```http
GET /api/learning-analytics/progress-visualization?time_range=30d
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "overall_progress": 68.5,
  "skill_proficiencies": {
    "reading": 72.0,
    "writing": 65.0,
    "listening": 70.0,
    "speaking": 58.0,
    "grammar": 75.0,
    "vocabulary": 71.0
  },
  "progress_trend": "improving",
  "milestones": [
    {
      "date": "2025-10-10",
      "description": "Reached B1 reading level",
      "skill": "reading"
    }
  ],
  "weekly_progress": [
    {"week": "Week 1", "progress": 60.0},
    {"week": "Week 2", "progress": 64.0},
    {"week": "Week 3", "progress": 67.0},
    {"week": "Week 4", "progress": 68.5}
  ]
}
```

---

### 4. Get Skill Radar Data
**Endpoint**: `GET /api/learning-analytics/skill-radar`  
**Auth**: Required  
**Description**: Get 6-dimensional skill proficiency data for radar chart

**Request Example**:
```http
GET /api/learning-analytics/skill-radar
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "reading_proficiency": 72.0,
  "writing_proficiency": 65.0,
  "listening_proficiency": 70.0,
  "speaking_proficiency": 58.0,
  "grammar_proficiency": 75.0,
  "vocabulary_proficiency": 71.0,
  "overall_proficiency": 68.5,
  "last_updated": "2025-10-21T10:30:00"
}
```

---

## Predictions

### 5. Predict Level Completion
**Endpoint**: `GET /api/learning-analytics/predictions/level-completion`  
**Auth**: Required  
**Description**: Predict when user will complete next CEFR level

**Request Example**:
```http
GET /api/learning-analytics/predictions/level-completion
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "current_level": "A2",
  "next_level": "B1",
  "predicted_date": "2025-12-15",
  "days_to_completion": 55,
  "confidence": 0.82,
  "current_progress": 68.5,
  "required_progress": 100.0,
  "daily_velocity": 0.57,
  "message": "Based on your current pace, you'll reach B1 level in approximately 55 days"
}
```

---

### 6. Predict Skill Mastery
**Endpoint**: `GET /api/learning-analytics/predictions/skill-mastery/<skill>`  
**Auth**: Required  
**Description**: Predict when user will master a specific skill

**Path Parameters**:
| Parameter | Type | Required | Values |
|-----------|------|----------|--------|
| `skill` | string | Yes | `reading`, `writing`, `listening`, `speaking`, `grammar`, `vocabulary` |

**Request Example**:
```http
GET /api/learning-analytics/predictions/skill-mastery/reading
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "skill_name": "reading",
  "current_proficiency": 72.0,
  "predicted_proficiency": 90.0,
  "predicted_date": "2025-11-30",
  "days_to_mastery": 40,
  "confidence": 0.85,
  "improvement_rate": 0.45,
  "message": "You're making great progress in reading! Expected mastery in 40 days."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid skill name
- `404 Not Found`: No data available for prediction

---

## Comparisons

### 7. Get Comparison Insights
**Endpoint**: `GET /api/learning-analytics/comparisons`  
**Auth**: Required  
**Description**: Get all comparison insights (vs self, peers, expected)

**Request Example**:
```http
GET /api/learning-analytics/comparisons
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "comparison_type": "vs_peers",
    "metric_name": "reading_proficiency",
    "your_value": 72.0,
    "peer_average": 65.0,
    "difference": 7.0,
    "percentile": 75
  },
  {
    "id": 2,
    "comparison_type": "vs_self",
    "metric_name": "overall_proficiency",
    "your_value": 68.5,
    "peer_average": 62.0,
    "difference": 6.5,
    "time_period": "30 days ago"
  },
  {
    "id": 3,
    "comparison_type": "vs_expected",
    "metric_name": "study_time",
    "your_value": 420.0,
    "peer_average": 360.0,
    "difference": 60.0
  }
]
```

---

### 8. Get Percentile Ranking
**Endpoint**: `GET /api/learning-analytics/percentile/<metric>`  
**Auth**: Required  
**Description**: Get user's percentile ranking for a specific metric

**Path Parameters**:
| Parameter | Type | Required | Values |
|-----------|------|----------|--------|
| `metric` | string | Yes | `overall_proficiency`, `study_time`, `activities_completed`, `consistency_score`, etc. |

**Request Example**:
```http
GET /api/learning-analytics/percentile/overall_proficiency
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "metric": "overall_proficiency",
  "your_value": 68.5,
  "percentile": 75,
  "rank": "Top 25%",
  "total_users": 1000,
  "your_rank": 250,
  "message": "You're in the top 25% of learners at your level!"
}
```

---

## Velocity & Momentum

### 9. Get Learning Velocity
**Endpoint**: `GET /api/learning-analytics/velocity`  
**Auth**: Required  
**Description**: Get learning velocity and momentum metrics

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | string | No | `week` | Time period: `week`, `month` |

**Request Example**:
```http
GET /api/learning-analytics/velocity?period=week
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "current_velocity": 1.25,
  "average_velocity": 1.10,
  "acceleration": 0.15,
  "momentum": 0.85,
  "trend": "improving",
  "trend_message": "Your learning velocity is accelerating! Keep up the excellent pace.",
  "period": "week",
  "calculated_at": "2025-10-21T10:30:00"
}
```

**Velocity Scale**:
- `0.0 - 0.5`: Low velocity (needs improvement)
- `0.5 - 1.0`: Fair velocity (on track)
- `1.0 - 1.5`: Good velocity (above average)
- `1.5+`: Excellent velocity (exceptional progress)

---

### 10. Get Optimal Study Schedule
**Endpoint**: `GET /api/learning-analytics/study-schedule`  
**Auth**: Required  
**Description**: Get AI-recommended optimal study times

**Request Example**:
```http
GET /api/learning-analytics/study-schedule
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "recommended_times": [
    "Monday 8:00 AM - 9:00 AM",
    "Wednesday 7:00 PM - 8:00 PM",
    "Friday 8:00 AM - 9:00 AM",
    "Sunday 2:00 PM - 3:00 PM"
  ],
  "best_day": "Wednesday",
  "best_time": "7:00 PM - 8:00 PM",
  "optimal_session_length": 45,
  "recommended_frequency": 4,
  "recommendation": "Based on your patterns, you learn best on weekday evenings. Try scheduling 45-minute sessions 4 times per week."
}
```

---

## Insights & Patterns

### 11. Get Personalized Insights
**Endpoint**: `GET /api/learning-analytics/insights`  
**Auth**: Required  
**Description**: Get AI-generated personalized learning insights

**Request Example**:
```http
GET /api/learning-analytics/insights
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
[
  {
    "id": 1,
    "insight_type": "strength",
    "title": "Excellent Reading Comprehension",
    "description": "Your reading proficiency is in the top 25% of learners at your level.",
    "priority_score": 0.85,
    "confidence_score": 0.92,
    "action_items": [
      "Continue reading advanced texts",
      "Try reading longer articles",
      "Explore literature in target language"
    ],
    "context": "Based on 15 reading activities completed this week",
    "identified_date": "2025-10-21"
  },
  {
    "id": 2,
    "insight_type": "weakness",
    "title": "Speaking Practice Needed",
    "description": "Your speaking proficiency is below your overall level. Focus on conversation practice.",
    "priority_score": 0.75,
    "confidence_score": 0.88,
    "action_items": [
      "Practice speaking 15 minutes daily",
      "Join conversation groups",
      "Record yourself speaking"
    ],
    "context": "Speaking proficiency: 58% vs Overall: 68.5%",
    "identified_date": "2025-10-20"
  },
  {
    "id": 3,
    "insight_type": "recommendation",
    "title": "Increase Vocabulary Practice",
    "description": "Your vocabulary is strong but can be improved with daily review sessions.",
    "priority_score": 0.60,
    "confidence_score": 0.80,
    "action_items": [
      "Review 10 new words daily",
      "Use spaced repetition",
      "Practice words in context"
    ],
    "identified_date": "2025-10-19"
  }
]
```

---

### 12. Get Learning Patterns
**Endpoint**: `GET /api/learning-analytics/patterns`  
**Auth**: Required  
**Description**: Identify behavioral learning patterns

**Request Example**:
```http
GET /api/learning-analytics/patterns
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
{
  "best_study_time": "Evening (7-9 PM)",
  "most_productive_day": "Wednesday",
  "strongest_skill": "reading",
  "needs_focus": "speaking",
  "consistency_pattern": "weekday_learner",
  "session_length_preference": 45,
  "patterns": [
    "You tend to learn best in 45-minute sessions",
    "Your consistency is higher on weekdays",
    "Evening study sessions show better retention",
    "You prefer text-based activities over audio"
  ],
  "recommendations": [
    "Schedule most important tasks for Wednesday evenings",
    "Break longer sessions into 45-minute blocks",
    "Focus on speaking practice during peak hours"
  ]
}
```

---

## Study Sessions

### 13. Get Study Session History
**Endpoint**: `GET /api/learning-analytics/study-sessions`  
**Auth**: Required  
**Description**: Get history of study sessions

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `days` | integer | No | 30 | Number of days to look back |
| `limit` | integer | No | 50 | Maximum sessions to return |

**Request Example**:
```http
GET /api/learning-analytics/study-sessions?days=7&limit=10
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
[
  {
    "id": 25,
    "session_date": "2025-10-21",
    "session_start": "2025-10-21T08:00:00",
    "session_end": "2025-10-21T09:00:00",
    "duration_minutes": 60,
    "activities_completed": 3,
    "points_earned": 120,
    "skills_practiced": ["reading", "vocabulary"],
    "engagement_score": 0.88,
    "focus_score": 0.92,
    "quality_score": 0.85
  }
]
```

---

### 14. Track Study Session
**Endpoint**: `POST /api/learning-analytics/study-sessions`  
**Auth**: Required  
**Description**: Track a new study session

**Request Body**:
```json
{
  "session_start": "2025-10-21T08:00:00",
  "session_end": "2025-10-21T09:00:00",
  "duration_minutes": 60,
  "activities_completed": 3,
  "points_earned": 120,
  "skills_practiced": ["reading", "vocabulary"]
}
```

**Response 201 Created**:
```json
{
  "message": "Study session tracked successfully",
  "session_id": 26,
  "engagement_score": 0.88,
  "quality_score": 0.85
}
```

**Error Responses**:
- `400 Bad Request`: Invalid session data
- `422 Unprocessable Entity`: Invalid datetime format

---

## Progress Snapshots

### 15. Get Snapshot History
**Endpoint**: `GET /api/learning-analytics/snapshots`  
**Auth**: Required  
**Description**: Get daily progress snapshots

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `days` | integer | No | 30 | Number of days to retrieve |

**Request Example**:
```http
GET /api/learning-analytics/snapshots?days=14
Authorization: Bearer <token>
```

**Response 200 OK**:
```json
[
  {
    "id": 100,
    "snapshot_date": "2025-10-21",
    "reading_proficiency": 72.0,
    "writing_proficiency": 65.0,
    "listening_proficiency": 70.0,
    "speaking_proficiency": 58.0,
    "grammar_proficiency": 75.0,
    "vocabulary_proficiency": 71.0,
    "overall_proficiency": 68.5,
    "learning_velocity": 1.25,
    "activities_today": 3,
    "study_time_today": 60
  }
]
```

---

### 16. Create Daily Snapshot
**Endpoint**: `POST /api/learning-analytics/snapshots/create`  
**Auth**: Required  
**Description**: Manually create a daily progress snapshot

**Request Body**:
```json
{
  "snapshot_date": "2025-10-21"
}
```

**Response 201 Created**:
```json
{
  "message": "Daily snapshot created successfully",
  "snapshot_id": 101,
  "snapshot_date": "2025-10-21",
  "overall_proficiency": 68.5
}
```

**Note**: Snapshots are typically created automatically by the system.

---

## Health Check

### 17. Health Check
**Endpoint**: `GET /api/learning-analytics/health`  
**Auth**: Not Required  
**Description**: Check if analytics service is running

**Request Example**:
```http
GET /api/learning-analytics/health
```

**Response 200 OK**:
```json
{
  "status": "healthy",
  "service": "learning-analytics",
  "timestamp": "2025-10-21T10:30:00",
  "version": "1.0.0"
}
```

---

## Error Codes

### Standard HTTP Status Codes

| Code | Name | Description | Example Response |
|------|------|-------------|------------------|
| 200 | OK | Request successful | `{"data": {...}}` |
| 201 | Created | Resource created | `{"message": "Created", "id": 123}` |
| 400 | Bad Request | Invalid request parameters | `{"error": "Invalid time_range"}` |
| 401 | Unauthorized | Missing/invalid JWT token | `{"error": "Unauthorized"}` |
| 404 | Not Found | Resource not found | `{"error": "Report not found"}` |
| 422 | Unprocessable Entity | Invalid data format | `{"error": "Invalid datetime format"}` |
| 500 | Internal Server Error | Server error | `{"error": "Internal server error"}` |

### Error Response Format
```json
{
  "error": "Error message describing what went wrong",
  "details": "Optional additional details",
  "timestamp": "2025-10-21T10:30:00"
}
```

---

## Rate Limiting

**Current Limit**: None (MVP phase)  
**Recommended**: 100 requests per minute per user  
**Future Implementation**: Add rate limiting in production

---

## API Versioning

**Current Version**: v1  
**Base Path**: `/api/learning-analytics`  
**Future Versions**: `/api/v2/learning-analytics`

---

## Best Practices

### 1. Authentication
- Always include JWT token in Authorization header
- Refresh token before expiry
- Handle 401 errors by redirecting to login

### 2. Error Handling
- Check response status codes
- Parse error messages
- Implement retry logic for network failures
- Show user-friendly error messages

### 3. Performance
- Use batch endpoints when available (`getDashboardData`)
- Cache responses where appropriate
- Implement pagination for large datasets

### 4. Data Validation
- Validate inputs before sending
- Handle edge cases (empty data, null values)
- Test with various time ranges

---

## Code Examples

### JavaScript/React Example
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
const token = localStorage.getItem('token');

// Get weekly report
async function getWeeklyReport(weekOffset = 0) {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/learning-analytics/weekly-report`,
      {
        params: { week_offset: weekOffset },
        headers: { 'Authorization': `Bearer ${token}` }
      }
    );
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    throw error;
  }
}

// Get all skill predictions
async function getAllSkillPredictions() {
  const skills = ['reading', 'writing', 'listening', 'speaking', 'grammar', 'vocabulary'];
  const predictions = await Promise.all(
    skills.map(skill =>
      axios.get(`${API_BASE_URL}/api/learning-analytics/predictions/skill-mastery/${skill}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    )
  );
  return predictions.map(res => res.data);
}
```

### Python/Flask Example
```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/learning-analytics/weekly-report', methods=['GET'])
@jwt_required()
def get_weekly_report():
    user_id = get_jwt_identity()
    week_offset = request.args.get('week_offset', default=0, type=int)
    
    try:
        report = service.generate_weekly_report(user_id, week_offset)
        return jsonify(report), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
```

### cURL Example
```bash
# Get weekly report
curl -X GET "http://localhost:5000/api/learning-analytics/weekly-report?week_offset=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get skill radar data
curl -X GET "http://localhost:5000/api/learning-analytics/skill-radar" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Track study session
curl -X POST "http://localhost:5000/api/learning-analytics/study-sessions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_start": "2025-10-21T08:00:00",
    "session_end": "2025-10-21T09:00:00",
    "duration_minutes": 60,
    "activities_completed": 3,
    "points_earned": 120,
    "skills_practiced": ["reading", "vocabulary"]
  }'
```

---

## Support

**Documentation**: See `PHASE7_COMPLETE_DOCUMENTATION.md`  
**Issues**: Contact development team  
**Updates**: Check version history in release notes

---

**Last Updated**: October 21, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅

