# Telugu-English Learning Platform API Documentation

## Overview

The Telugu-English Learning Platform provides a comprehensive REST API for building language learning applications. The API supports user management, personalized learning paths, real-time conversations with AI tutoring, media upload for visual/audio learning, analytics, and gamification features.

**Base URL:** `http://localhost:5000`  
**Authentication:** JWT Bearer Token  
**Content-Type:** `application/json`

---

## Authentication

### Register User

**POST** `/api/auth/register`

Register a new user account.

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "native_language": "telugu",
  "proficiency_level": "beginner"
}
```

**Response:**

```json
{
  "message": "User registered successfully!",
  "telugu_message": "వినియోగదారు విజయవంతంగా నమోదు చేయబడ్డారు!",
  "user_id": 123
}
```

### Login

**POST** `/api/auth/login`

Authenticate user and receive JWT tokens.

**Request Body:**

```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:**

```json
{
  "message": "Login successful!",
  "telugu_message": "లాగిన్ విజయవంతం!",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### Refresh Token

**POST** `/api/auth/refresh`

Get new access token using refresh token.

**Headers:** `Authorization: Bearer {refresh_token}`

---

## User Management

All user endpoints require authentication.

### Get User Profile

**GET** `/api/user/profile`

Get current user's profile information.

**Response:**

```json
{
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "profile": {
      "proficiency_level": "beginner",
      "native_language": "telugu",
      "current_streak": 5,
      "longest_streak": 12,
      "total_points": 2450
    }
  }
}
```

### Update User Settings

**PUT** `/api/user/settings`

Update user preferences and settings.

**Request Body:**

```json
{
  "language_preference": "telugu",
  "difficulty_preference": "intermediate",
  "daily_goal_minutes": 30,
  "notification_settings": {
    "reminders": true,
    "achievements": true,
    "progress_updates": false
  }
}
```

### Change Password

**PUT** `/api/user/change-password`

Change user password.

**Request Body:**

```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

### Get User Statistics

**GET** `/api/user/statistics`

Get comprehensive user learning statistics.

**Response:**

```json
{
  "statistics": {
    "total_learning_time_minutes": 1250,
    "activities_completed": 45,
    "vocabulary_words_learned": 120,
    "current_streak": 5,
    "average_score": 82.5,
    "level_progress": {
      "current_level": "intermediate",
      "progress_percentage": 65
    }
  }
}
```

---

## Chat & Conversations

Real-time conversation management with AI tutoring.

### Get Conversations

**GET** `/api/chat/conversations`

Get user's conversation history.

**Response:**

```json
{
  "conversations": [
    {
      "id": 1,
      "title": "Learning Telugu Colors",
      "created_at": "2024-01-15T10:30:00Z",
      "last_message_at": "2024-01-15T11:15:00Z",
      "message_count": 12,
      "conversation_type": "learning_chat"
    }
  ]
}
```

### Send Message

**POST** `/api/chat/send-message`

Send a message in a conversation with AI tutor.

**Request Body:**

```json
{
  "message": "How do you say 'good morning' in Telugu?",
  "conversation_id": 1,
  "conversation_type": "learning_chat"
}
```

**Response:**

```json
{
  "message": "Message sent successfully!",
  "ai_response": {
    "text": "In Telugu, 'good morning' is said as 'శుభోదయం' (Shubhodayam). Let me break it down: 'శుభ' means good/auspicious, and 'ఉదయం' means morning.",
    "translations": [
      {
        "english": "good morning",
        "telugu": "శుభోదయం",
        "pronunciation": "Shubhodayam"
      }
    ],
    "suggested_practice": "Try using this greeting in your next conversation!"
  }
}
```

### Quick Chat

**POST** `/api/chat/quick-chat`

Quick AI chat without creating a persistent conversation.

**Request Body:**

```json
{
  "message": "What are common Telugu greetings?",
  "context": "greetings"
}
```

### Get Chat Suggestions

**GET** `/api/chat/suggestions?topic=greetings&level=beginner`

Get AI-generated conversation starters.

**Response:**

```json
{
  "suggestions": [
    "Ask me how to greet someone in Telugu",
    "Let's practice introducing yourself",
    "Learn about different times of day greetings"
  ]
}
```

---

## Courses & Learning Paths

Structured learning path management with progress tracking.

### Get Learning Paths

**GET** `/api/courses/learning-paths`

Get available learning paths.

**Response:**

```json
{
  "learning_paths": [
    {
      "id": 1,
      "title": "Telugu for Beginners",
      "description": "Start your Telugu learning journey",
      "difficulty_level": "beginner",
      "estimated_hours": 20,
      "activity_count": 15,
      "enrollment_count": 1250
    }
  ]
}
```

### Get Learning Path Details

**GET** `/api/courses/learning-paths/{id}`

Get detailed information about a specific learning path.

### Enroll in Learning Path

**POST** `/api/courses/enroll`

Enroll in a learning path.

**Request Body:**

```json
{
  "learning_path_id": 1
}
```

### Get Enrollment Progress

**GET** `/api/courses/enrollment/{enrollment_id}/progress`

Get progress for a specific enrollment.

### Start Activity

**POST** `/api/courses/start-activity`

Start a learning activity.

**Request Body:**

```json
{
  "enrollment_id": 1,
  "activity_id": 5
}
```

### Complete Activity

**POST** `/api/courses/complete-activity`

Mark an activity as completed with score.

**Request Body:**

```json
{
  "enrollment_id": 1,
  "activity_id": 5,
  "score": 85,
  "time_spent_minutes": 15
}
```

---

## Media Upload & Processing

Image and audio upload with AI analysis for enhanced learning.

### Upload Image

**POST** `/api/media/upload-image`

Upload image for visual learning with AI analysis.

**Request:** `multipart/form-data`

- `image`: Image file (JPEG, PNG, GIF, WebP)
- `context`: Learning context (optional)

**Response:**

```json
{
  "message": "Image uploaded and analyzed successfully!",
  "file_info": {
    "filename": "learning_image_20240115_103045.jpg",
    "url": "/api/media/serve/learning_image_20240115_103045.jpg",
    "size_bytes": 245760
  },
  "ai_analysis": {
    "description": "This image shows a traditional Telugu kitchen with various cooking utensils",
    "vocabulary_suggestions": [
      { "english": "kitchen", "telugu": "వంటగది" },
      { "english": "cooking", "telugu": "వంట" }
    ],
    "learning_activities": [
      "Create vocabulary flashcards for kitchen items",
      "Practice describing the scene in Telugu"
    ]
  }
}
```

### Upload Audio

**POST** `/api/media/upload-audio`

Upload audio for pronunciation practice and analysis.

**Request:** `multipart/form-data`

- `audio`: Audio file (MP3, WAV, M4A)
- `target_word`: Word being practiced (optional)

### Generate Pronunciation Exercise

**POST** `/api/media/pronunciation-exercise`

Generate pronunciation exercise for specific words.

**Request Body:**

```json
{
  "target_word": "నమస్కారం",
  "difficulty_level": "beginner"
}
```

### Get Media Files

**GET** `/api/media/files`

Get user's uploaded media files.

---

## Analytics & Reporting

Comprehensive learning analytics and progress reporting.

### Dashboard Summary

**GET** `/api/analytics/dashboard-summary`

Get overview analytics for user dashboard.

**Response:**

```json
{
  "summary": {
    "learning_time": {
      "total_minutes": 1250,
      "weekly_minutes": 180,
      "monthly_minutes": 720,
      "daily_average": 25.7
    },
    "activities": {
      "total_completed": 45,
      "weekly_completed": 8,
      "average_score": 82.5,
      "recent_average_score": 85.2
    },
    "vocabulary": {
      "total_words": 120,
      "mastered_words": 65,
      "weekly_new_words": 12,
      "mastery_rate": 54.2
    },
    "streaks_and_goals": {
      "current_streak": 5,
      "longest_streak": 12,
      "today_goal_progress": 75.0,
      "daily_goal_minutes": 30
    }
  }
}
```

### Learning Trends

**GET** `/api/analytics/learning-trends?days=30`

Get learning trends over time.

**Query Parameters:**

- `days`: Number of days (7, 14, 30, 90)

### Performance Analysis

**GET** `/api/analytics/performance-analysis`

Get detailed performance analysis by activity type and difficulty.

**Response:**

```json
{
  "performance": {
    "by_activity_type": [
      {
        "activity_type": "vocabulary_quiz",
        "total_attempts": 25,
        "average_score": 84.2,
        "best_score": 95,
        "performance_level": "excellent"
      }
    ],
    "analysis": {
      "strengths": ["vocabulary_quiz", "conversation_practice"],
      "improvement_areas": ["grammar_exercises"],
      "overall_score": 82.5,
      "recommendations": [
        "Great job with vocabulary quizzes! Keep it up!",
        "Focus more practice on: grammar_exercises"
      ]
    }
  }
}
```

### Vocabulary Analytics

**GET** `/api/analytics/vocabulary-analytics`

Get detailed vocabulary learning analytics.

### Export Progress Report

**GET** `/api/analytics/export/progress-report?type=summary`

Generate comprehensive progress report for export.

**Query Parameters:**

- `type`: Report type (`summary`, `detailed`, `vocabulary`)

---

## Activity Generation

Generate personalized learning activities.

### Generate Activity

**POST** `/api/activity/generate`

Generate a personalized learning activity.

**Request Body:**

```json
{
  "activity_type": "vocabulary_quiz",
  "difficulty": "beginner",
  "topic": "greetings",
  "count": 10
}
```

### Submit Activity

**POST** `/api/activity/submit`

Submit completed activity for scoring.

**Request Body:**

```json
{
  "activity_id": "activity_123",
  "answers": [
    { "question_id": 1, "answer": "నమస్కారం" },
    { "question_id": 2, "answer": "వీడ్కోలు" }
  ]
}
```

---

## Gamification

Track points, achievements, and streaks.

### Get Gamification Profile

**GET** `/api/gamification/profile`

Get user's gamification profile with points and achievements.

### Get Leaderboard

**GET** `/api/gamification/leaderboard?period=weekly`

Get leaderboard rankings.

### Get Achievements

**GET** `/api/gamification/achievements`

Get available and earned achievements.

---

## Personalization

AI-powered personalization features.

### Get Insights

**GET** `/api/personalization/insights`

Get personalized learning insights and recommendations.

### Update Learning Preferences

**POST** `/api/personalization/preferences`

Update learning preferences for better personalization.

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Validation failed",
  "telugu_message": "ధృవీకరణ విఫలమైంది",
  "details": {
    "field": "username",
    "message": "Username is required"
  }
}
```

**Common HTTP Status Codes:**

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

- Authentication endpoints: 5 requests per minute
- Media upload endpoints: 10 requests per minute
- Other endpoints: 100 requests per minute

---

## Testing

Use the provided test script to test all endpoints:

```bash
cd language-learning-platform
python test_all_endpoints.py
```

The test script includes:

- Authentication flow testing
- All endpoint categories
- Error handling validation
- Response format verification

---

## Setup & Installation

1. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Create `.env` file with:

   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   GOOGLE_API_KEY=your-google-api-key
   DATABASE_URL=sqlite:///telugu_english_learning.db
   ```

3. **Initialize Database:**

   ```bash
   python init_db.py
   ```

4. **Run Application:**
   ```bash
   python app.py
   ```

---

## Support

For questions or issues:

- Check the test script examples
- Review error messages for debugging hints
- Ensure all required dependencies are installed
- Verify JWT tokens are properly included in headers

The API supports both English and Telugu messages for better user experience in language learning applications.
