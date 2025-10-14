# Chat Tutor & Notification System Implementation Guide

## Overview
This document provides comprehensive implementation details for **Step 10: Personalized Chat Tutor** and **Step 11: Notification & Reminder System** for the English Learning Platform.

---

## Step 10: Personalized Chat Tutor

### Features Implemented
✅ **AI-Powered Conversational Tutor** using LLMConfig  
✅ **Context-Aware Conversations** with message history  
✅ **Telugu Translations** embedded in responses  
✅ **Grammar Explanations** with automatic parsing  
✅ **Example Sentences** for better understanding  
✅ **Mistake Corrections** with gentle feedback  
✅ **Conversation Management** (create, clear, delete, rename)  
✅ **Conversation Summarization** using AI  

### Backend Implementation

#### Database Models (`app/models/chat.py`)

**ChatConversation Model:**
```python
- id (PK)
- user_id (FK to users)
- title (default: "New Conversation")
- topic (e.g., "Grammar", "Vocabulary", "General")
- created_at, updated_at
- is_active (for soft delete)
- message_count
- Relationships: user, messages
```

**ChatMessage Model:**
```python
- id (PK)
- conversation_id (FK to chat_conversations)
- role ('user' or 'assistant')
- content (message text)
- telugu_translation (AI-extracted Telugu text)
- grammar_explanation (AI-extracted grammar rules)
- examples (JSON array of example sentences)
- correction (if user made mistakes)
- created_at
- Metadata: tokens_used, model_used, response_time
```

#### Service Layer (`app/services/chat_service.py`)

**ChatService Methods:**

1. **create_conversation(user_id, title, topic)**
   - Creates new chat conversation
   - Auto-generates title if not provided
   - Returns conversation dict

2. **get_user_conversations(user_id, limit, offset, include_inactive)**
   - Fetches all conversations for user
   - Pagination support
   - Can filter active/inactive

3. **get_conversation(conversation_id, user_id)**
   - Gets specific conversation with all messages
   - Ownership verification
   - Returns full conversation history

4. **send_message(conversation_id, user_message, user_id)**
   - Sends user message and gets AI response
   - Uses **LLMConfig.chat_completion()** with system prompt
   - Parses AI response for:
     - Telugu translations (regex: `\([^)]*[\u0C00-\u0C7F]+[^)]*\)`)
     - Grammar explanations (keywords: "Grammar:", "Rule:", "Note:")
     - Examples (lines starting with "Example:", "-", "•", numbered)
     - Corrections (keywords: "Correction:", "Correct form:")
   - Tracks tokens, model, response time
   - Updates conversation metadata

5. **clear_conversation(conversation_id, user_id)**
   - Deletes all messages in conversation
   - Resets message count

6. **delete_conversation(conversation_id, user_id)**
   - Soft delete (marks as inactive)

7. **update_conversation_title(conversation_id, title, user_id)**
   - Updates conversation title

8. **get_conversation_summary(conversation_id, user_id)**
   - AI-generated summary of conversation
   - Uses **LLMConfig.generate_text()** to summarize

**AI Tutor System Prompt:**
```
You are a friendly and patient English language tutor for Telugu speakers.
Your role is to:
1. Answer questions about English grammar, vocabulary, and usage in simple, clear language
2. Provide Telugu translations (in Telugu script) when helpful for understanding
3. Give practical examples that Telugu speakers can relate to
4. Correct mistakes gently and explain why the correction is needed
5. Encourage learners and make them feel confident
6. Break down complex concepts into simple steps
7. Use everyday scenarios that Telugu speakers encounter

Guidelines:
- Keep responses concise and easy to understand
- Use simple English when explaining concepts
- Provide 2-3 relevant examples for each explanation
- Include Telugu translations for key words/phrases (using Telugu script: తెలుగు)
- If user makes a mistake, correct it kindly and explain the correct form
- Ask follow-up questions to check understanding
- Be encouraging and positive
- Use emojis sparingly to make responses friendly

Remember: Your goal is to build confidence and make learning English enjoyable!
```

#### API Routes (`app/api/chat_tutor_routes.py`)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat-tutor/conversations` | Create new conversation |
| GET | `/api/chat-tutor/conversations` | List user's conversations |
| GET | `/api/chat-tutor/conversations/<id>` | Get specific conversation with messages |
| POST | `/api/chat-tutor/conversations/<id>/messages` | Send message, get AI response |
| PUT | `/api/chat-tutor/conversations/<id>` | Update conversation title |
| DELETE | `/api/chat-tutor/conversations/<id>` | Delete conversation (soft) |
| DELETE | `/api/chat-tutor/conversations/<id>/clear` | Clear all messages |
| GET | `/api/chat-tutor/conversations/<id>/summary` | Get AI summary |
| POST | `/api/chat-tutor/quick-chat` | Create conversation + send first message in one request |

**Example Request (Send Message):**
```json
POST /api/chat-tutor/conversations/1/messages
Headers: Authorization: Bearer <JWT>
Body: {
  "message": "What is difference between 'go' and 'went'?"
}

Response: {
  "success": true,
  "user_message": { ... },
  "ai_response": {
    "id": 2,
    "role": "assistant",
    "content": "Great question! 'Go' is present tense, 'went' is past tense...",
    "telugu_translation": "(నేను స్కూల్ కు వెళ్తాను - now/regularly)",
    "grammar_explanation": "Grammar: Present tense is used for current or regular actions...",
    "examples": [
      "I go to school. (Present - happens regularly)",
      "I went to school yesterday. (Past - already happened)"
    ],
    "correction": null,
    "created_at": "2025-10-09T15:30:00",
    "tokens_used": 345,
    "model_used": "gemini-2.0-flash-exp",
    "response_time": 2.3
  },
  "conversation": { ... }
}
```

### Frontend Implementation (To Do)

**Chat.jsx Component:**
- Material-UI chat interface with message bubbles
- User input with TextField and Send button
- AI responses with grammar/translation highlights
- Typing indicator during AI response
- Conversation list sidebar
- Clear conversation button
- Rename conversation dialog
- Responsive design for mobile

**Required npm packages:**
```bash
@mui/material @mui/icons-material @emotion/react @emotion/styled
```

---

## Step 11: Notification & Reminder System

### Features Implemented
✅ **7 Notification Types** (daily reminder, streak alert, achievement, new content, tips, learning path updates, milestones)  
✅ **User Notification Settings** with preferences  
✅ **Daily Reminder Scheduling** with customizable time  
✅ **Streak Alerts** to prevent streak loss  
✅ **Achievement Notifications** when badges unlocked  
✅ **Personalized Tips** based on user progress  
✅ **Notification CRUD** (create, read, update, delete)  
✅ **Multi-Channel Support** (in-app, email, push - preparation)  
✅ **Quiet Hours** and weekend reminders  

### Backend Implementation

#### Database Models (`app/models/notification.py`)

**NotificationType Model:**
```python
- id (PK)
- name (unique, e.g., "daily_reminder", "streak_alert")
- display_name (user-facing name)
- description
- icon (Material-UI icon name)
- default_enabled (boolean)
```

**Notification Model:**
```python
- id (PK)
- user_id (FK to users)
- type_id (FK to notification_types)
- title (notification title)
- message (notification message)
- action_url (navigation URL when clicked)
- action_text (button text, e.g., "Practice Now")
- is_read, is_sent
- sent_at, read_at, created_at
- Delivery channels: in_app, email, push
- data (JSON for additional data like badge info)
- priority ('low', 'normal', 'high', 'urgent')
- Relationships: user, type
```

**UserNotificationSettings Model:**
```python
- id (PK)
- user_id (FK to users, unique)
- daily_reminder_enabled (boolean)
- daily_reminder_time (time, default: 19:00)
- timezone (default: 'Asia/Kolkata')
- Notification type preferences:
  - streak_alerts
  - achievement_notifications
  - new_content_notifications
  - personalized_tips
  - learning_path_updates
- Delivery channel preferences:
  - in_app_notifications
  - email_notifications
  - push_notifications
- Advanced settings:
  - quiet_hours_start, quiet_hours_end (time)
  - weekend_reminders (boolean)
- created_at, updated_at
- Relationship: user (one-to-one)
```

#### Service Layer (`app/services/notification_service.py`)

**NotificationService Methods:**

**Setup & Settings:**

1. **initialize_notification_types()**
   - Seeds notification_types table with 7 predefined types
   - Called on first app request
   - Idempotent (doesn't duplicate)

2. **create_user_settings(user_id)**
   - Creates default notification settings for new user
   - Default: all enabled, 7 PM reminders, in-app only

3. **get_user_settings(user_id)**
   - Retrieves user's notification preferences
   - Auto-creates if doesn't exist

4. **update_user_settings(user_id, settings_data)**
   - Updates user preferences
   - Validates and converts time strings to time objects

**Notification CRUD:**

5. **create_notification(user_id, notification_type, title, message, action_url, action_text, data, priority)**
   - Creates new notification
   - Checks if notification type is enabled for user
   - Sets delivery channels based on user preferences
   - Returns notification dict

6. **get_user_notifications(user_id, limit, offset, unread_only)**
   - Fetches user's notifications with pagination
   - Can filter unread only
   - Returns total count and unread count

7. **mark_as_read(notification_id, user_id)**
   - Marks single notification as read
   - Sets read_at timestamp

8. **mark_all_as_read(user_id)**
   - Marks all unread notifications as read

9. **delete_notification(notification_id, user_id)**
   - Deletes specific notification

10. **clear_all_notifications(user_id)**
    - Deletes all notifications for user

**Automated Notifications:**

11. **send_daily_reminder(user_id)**
    - Sends daily practice reminder
    - Includes user's current streak
    - Title: "Time to practice English! 📚"
    - Message varies based on streak:
      - 0 days: "Start your learning journey today!"
      - 1-6 days: "Your {n}-day streak is waiting!"
      - 7+ days: "Amazing {n}-day streak! Don't break it today! 🔥"

12. **send_streak_alert(user_id)**
    - Sends alert when streak at risk
    - Only if user has active streak and hasn't practiced today
    - Priority: HIGH
    - Title: "Don't break your {n}-day streak! 🔥"

13. **send_achievement_notification(user_id, badge_id)**
    - Sends notification when badge unlocked
    - Includes badge name, description, reward points
    - Priority: HIGH
    - Title: "🎉 You unlocked '{badge_name}' badge!"

14. **send_personalized_tip(user_id)**
    - Generates personalized learning tip based on user progress
    - Analyzes enrollments, completed chapters
    - Randomly selects from 4 tip templates:
      - Vocabulary practice suggestion
      - Daily practice motivation
      - New learning paths exploration
      - Goal setting reminder

#### API Routes (`app/api/notifications_routes.py`)

**Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications/` | List user's notifications (paginated, unread filter) |
| POST | `/api/notifications/mark-read/<id>` | Mark notification as read |
| POST | `/api/notifications/mark-all-read` | Mark all as read |
| DELETE | `/api/notifications/<id>` | Delete specific notification |
| DELETE | `/api/notifications/clear` | Clear all notifications |
| GET | `/api/notifications/preferences` | Get notification settings |
| POST | `/api/notifications/preferences` | Update notification settings |
| POST | `/api/notifications/test/daily-reminder` | Trigger daily reminder (testing) |
| POST | `/api/notifications/test/streak-alert` | Trigger streak alert (testing) |
| POST | `/api/notifications/test/personalized-tip` | Trigger personalized tip (testing) |

**Example Request (Get Notifications):**
```json
GET /api/notifications/?limit=20&offset=0&unread_only=true
Headers: Authorization: Bearer <JWT>

Response: {
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": {
        "name": "daily_reminder",
        "display_name": "Daily Practice Reminder",
        "icon": "NotificationsActive"
      },
      "title": "Time to practice English! 📚",
      "message": "Your 5-day streak is waiting! Keep up the great work!",
      "action_url": "/dashboard",
      "action_text": "Practice Now",
      "is_read": false,
      "priority": "normal",
      "created_at": "2025-10-09T19:00:00",
      "data": null
    }
  ],
  "total": 15,
  "unread_count": 3,
  "limit": 20,
  "offset": 0
}
```

**Example Request (Update Settings):**
```json
POST /api/notifications/preferences
Headers: Authorization: Bearer <JWT>
Body: {
  "daily_reminder_enabled": true,
  "daily_reminder_time": "20:00",
  "streak_alerts": true,
  "achievement_notifications": true,
  "email_notifications": false,
  "quiet_hours_start": "23:00",
  "quiet_hours_end": "07:00"
}

Response: {
  "success": true,
  "settings": { ... }
}
```

### Notification Scheduler Integration (To Do)

**Using APScheduler:**

```python
# app/__init__.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notification_service import NotificationService

def send_daily_reminders():
    """Send daily reminders to all users based on their settings"""
    with app.app_context():
        settings = UserNotificationSettings.query.filter_by(
            daily_reminder_enabled=True
        ).all()
        
        for user_settings in settings:
            # Check if it's the user's reminder time
            current_time = datetime.now(timezone(user_settings.timezone)).time()
            reminder_time = user_settings.daily_reminder_time
            
            if current_time.hour == reminder_time.hour:
                NotificationService.send_daily_reminder(user_settings.user_id)

def check_streaks():
    """Check for users with active streaks who haven't practiced today"""
    with app.app_context():
        # Get users with active streaks
        active_streaks = LearningStreak.query.filter(
            LearningStreak.current_streak > 0
        ).all()
        
        for streak in active_streaks:
            # Check if user practiced today
            last_activity_today = Activity.query.filter_by(
                user_id=streak.user_id,
                completed_at > datetime.utcnow().date()
            ).first()
            
            if not last_activity_today:
                NotificationService.send_streak_alert(streak.user_id)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_reminders, CronTrigger(hour='*', minute=0))  # Every hour
scheduler.add_job(check_streaks, CronTrigger(hour=22, minute=0))  # 10 PM daily
scheduler.start()
```

### Frontend Implementation (To Do)

**NotificationBell.jsx Component:**
- Badge with unread count
- Dropdown menu with recent notifications
- Mark as read on click
- Navigate to action_url

**NotificationCenter.jsx Component:**
- Full list of notifications
- Filter by read/unread
- Delete individual notifications
- Clear all button
- Infinite scroll or pagination

**NotificationSettings.jsx Component:**
- Toggle switches for each notification type
- Time picker for daily reminder
- Timezone selector
- Quiet hours configuration
- Delivery channel preferences (in-app, email, push)
- Weekend reminders toggle

**Required npm packages:**
```bash
@mui/material @mui/icons-material @mui/lab date-fns
```

---

## Database Migrations

**Create Migration:**
```bash
cd language-learning-platform
flask db migrate -m "Add chat tutor and notification system models"
flask db upgrade
```

**Verify Tables Created:**
```sql
-- Chat Tutor
SELECT * FROM chat_conversations LIMIT 1;
SELECT * FROM chat_messages LIMIT 1;

-- Notifications
SELECT * FROM notification_types;
SELECT * FROM notifications LIMIT 1;
SELECT * FROM user_notification_settings LIMIT 1;
```

**Initialize Notification Types:**
```python
# Automatically done on first app request via before_app_first_request
# Or manually:
from app.services.notification_service import NotificationService
NotificationService.initialize_notification_types()
```

---

## Testing Checklist

### Chat Tutor Testing

- [ ] **Create Conversation**
  - POST `/api/chat-tutor/conversations` with JWT
  - Verify conversation created with default title
  - Check user ownership

- [ ] **Send Message**
  - POST `/api/chat-tutor/conversations/1/messages` with question
  - Verify AI response includes:
    - Relevant answer
    - Telugu translation (if applicable)
    - Grammar explanation (if applicable)
    - Example sentences (2-3)
  - Check response time < 5 seconds

- [ ] **Test Conversation Context**
  - Send follow-up question referencing previous message
  - Verify AI maintains context

- [ ] **Test Telugu Translation**
  - Ask about specific Telugu words
  - Verify Telugu script in response

- [ ] **Test Grammar Correction**
  - Send grammatically incorrect sentence
  - Verify AI provides gentle correction and explanation

- [ ] **Clear Conversation**
  - DELETE `/api/chat-tutor/conversations/1/clear`
  - Verify all messages deleted, message_count = 0

- [ ] **Delete Conversation**
  - DELETE `/api/chat-tutor/conversations/1`
  - Verify is_active = False

- [ ] **Conversation Summary**
  - GET `/api/chat-tutor/conversations/1/summary`
  - Verify AI-generated summary includes main topics

### Notification System Testing

- [ ] **Get Notifications**
  - GET `/api/notifications/?unread_only=true`
  - Verify pagination works
  - Check unread_count accuracy

- [ ] **Daily Reminder**
  - POST `/api/notifications/test/daily-reminder`
  - Verify notification created with correct streak info
  - Check action_url = "/dashboard"

- [ ] **Streak Alert**
  - POST `/api/notifications/test/streak-alert`
  - Verify only sent if user has active streak
  - Check priority = "high"

- [ ] **Achievement Notification**
  - Trigger badge unlock (complete activity)
  - Verify notification created with badge details

- [ ] **Personalized Tip**
  - POST `/api/notifications/test/personalized-tip`
  - Verify tip relevance to user progress

- [ ] **Mark as Read**
  - POST `/api/notifications/mark-read/1`
  - Verify is_read = true, read_at timestamp set

- [ ] **Mark All as Read**
  - POST `/api/notifications/mark-all-read`
  - Verify all unread → read

- [ ] **Delete Notification**
  - DELETE `/api/notifications/1`
  - Verify notification removed from database

- [ ] **Update Settings**
  - POST `/api/notifications/preferences` with new settings
  - Verify settings saved
  - Test quiet hours (shouldn't send notifications during quiet hours)

- [ ] **Notification Filtering**
  - Disable streak_alerts in settings
  - Trigger streak alert
  - Verify notification NOT created

---

## Integration with Gamification System

**When Badge Unlocked:**
```python
# app/services/gamification_service.py

def unlock_badge(user_id, badge_id):
    # ... existing badge unlock logic ...
    
    # Send notification
    from app.services.notification_service import NotificationService
    NotificationService.send_achievement_notification(user_id, badge_id)
```

**When Streak Updated:**
```python
# app/services/activity_service.py

def complete_activity(user_id, activity_id):
    # ... existing activity completion logic ...
    
    # Update streak
    update_user_streak(user_id)
    
    # If first activity today, cancel pending streak alert
    cancel_pending_notification(user_id, 'streak_alert')
```

---

## Performance Considerations

1. **Chat Response Time:**
   - LLM calls typically 2-5 seconds
   - Consider adding loading state in frontend
   - Potential optimization: streaming responses (future)

2. **Notification Queries:**
   - Index on `user_id, is_read, created_at` for fast queries
   - Limit notifications per user (e.g., 200 max, auto-delete oldest)

3. **Scheduler Performance:**
   - Daily reminder job: O(n) where n = active users
   - Consider batching (send 100 users at a time)
   - Use queue system (Celery) for production

---

## Environment Variables

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key

# Optional: Custom LLM endpoint (future)
CUSTOM_TEXT_ENDPOINT=https://your-model.com/v1/completions
CUSTOM_VISION_ENDPOINT=https://your-model.com/v1/vision
```

---

## Future Enhancements

### Chat Tutor:
- [ ] Voice input/output (speech-to-text, text-to-speech)
- [ ] Conversation export (PDF, text file)
- [ ] Conversation sharing with teachers
- [ ] Topic-specific tutors (Grammar Expert, Vocabulary Coach)
- [ ] Suggested questions when conversation starts

### Notifications:
- [ ] Email notifications (SMTP integration)
- [ ] Push notifications (Firebase Cloud Messaging)
- [ ] SMS notifications (Twilio integration)
- [ ] Notification sound customization
- [ ] Notification grouping (e.g., "3 new achievements")
- [ ] Weekly digest email
- [ ] Notification analytics (click-through rate, dismissal rate)

---

## Summary

**✅ Backend Complete:**
- Chat Tutor: 8 API endpoints, 2 models, 1 service class
- Notifications: 10 API endpoints, 3 models, 1 service class
- Database models designed and ready for migration
- LLMConfig integration for AI responses
- Automated notification triggers implemented

**⏳ Frontend To Do:**
- Chat.jsx component (5-6 hours)
- NotificationBell.jsx, NotificationCenter.jsx, NotificationSettings.jsx (3-4 hours)
- Integration with existing layouts and navigation (1-2 hours)

**⏳ Infrastructure To Do:**
- Database migrations (15 minutes)
- APScheduler setup (1 hour)
- Testing all endpoints (2-3 hours)

**Estimated Total Time to Production:**
- Backend: ✅ Complete
- Frontend: ~10 hours
- Testing & Deployment: ~3 hours
- **Total: ~13 hours remaining**
