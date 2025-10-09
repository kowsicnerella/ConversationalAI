# Goal Setting & Personalization Implementation

## Overview

This document details the complete implementation of the **Goal Setting & Personalization** feature (Step 3 of the onboarding journey). This feature allows users to:
- Select their learning goals (Conversational Fluency, Business English, Travel English, Academic English)
- Set daily time commitment (5-60 minutes)
- Choose preferred topics (Food, Travel, Work, Daily Life, etc.)
- Configure notification preferences (Daily reminders, achievements, weekly reports, learning tips)

## Architecture

### Backend Components

#### 1. API Endpoints

**File:** `language-learning-platform/app/api/personalization_routes.py`

##### POST /api/personalization/preferences
Saves user preferences including topics, learning goal type, and notifications.

**Request Body:**
```json
{
  "preferred_topics": ["Food", "Travel", "Work"],
  "learning_goal_type": "conversational",
  "notification_settings": {
    "daily_reminders": true,
    "achievements": true,
    "weekly_reports": false,
    "learning_tips": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Preferences saved successfully",
  "preferences": {
    "preferred_topics": ["Food", "Travel", "Work"],
    "learning_goal_type": "conversational",
    "notification_settings": {...}
  }
}
```

**Telugu Response (on success):**
```json
{
  "success": true,
  "message": "ప్రాధాన్యతలు విజయవంతంగా సేవ్ చేయబడ్డాయి"
}
```

##### GET /api/personalization/preferences
Retrieves stored user preferences.

**Response:**
```json
{
  "success": true,
  "preferences": {
    "preferred_topics": ["Food", "Travel", "Work"],
    "learning_goal_type": "conversational",
    "notification_settings": {...}
  }
}
```

**Error Handling:**
- 400: Invalid request data (missing required fields)
- 401: User not authenticated
- 500: Server error during save/retrieval

#### 2. Database Models

**User Model Updates:**
- `preferred_topics` (JSON field): Stores array of topic preferences
- `learning_goal_type` (String): "conversational" | "business" | "travel" | "academic"
- `notification_settings` (JSON field): Stores notification preferences

### Frontend Components

#### 1. GoalSetting Component

**File:** `ConvAI_frontV1/src/components/onboarding/GoalSetting.jsx`

**Props:**
- `proficiencyLevel`: User's assessed proficiency level (optional)
- `onComplete`: Callback function called when goal setting is successfully completed

**Features:**
- **Step 1: Learning Goal Selection**
  - 4 goal cards: Conversational Fluency, Business English, Travel English, Academic English
  - Each card includes icon, title, Telugu translation, and description
  - Visual feedback on hover and selection
  
- **Step 2: Daily Time Commitment**
  - Slider from 5 to 60 minutes
  - Real-time display of selected time
  - Visual bar representation
  
- **Step 3: Topic Preferences**
  - 10 topic chips: Food, Travel, Work, Daily Life, Shopping, Health, Education, Technology, Sports, Entertainment
  - Each chip shows English and Telugu labels
  - Multi-select with visual indication
  
- **Step 4: Notification Settings**
  - 4 toggle switches:
    - Daily Reminders (రోజువారీ రిమైండర్లు)
    - Achievement Notifications (సాఫల్య నోటిఫికేషన్లు)
    - Weekly Reports (వారపు నివేదికలు)
    - Learning Tips (నేర్చుకునే చిట్కాలు)
  
- **Success State**
  - Celebration animation with green checkmark
  - Success message in English and Telugu
  - Auto-navigation after 2 seconds

**State Management:**
```javascript
const [activeStep, setActiveStep] = useState(0);
const [selectedGoal, setSelectedGoal] = useState('');
const [dailyTime, setDailyTime] = useState(15);
const [selectedTopics, setSelectedTopics] = useState([]);
const [notifications, setNotifications] = useState({
  daily_reminders: true,
  achievements: true,
  weekly_reports: false,
  learning_tips: true
});
const [loading, setLoading] = useState(false);
const [error, setError] = useState('');
const [success, setSuccess] = useState(false);
```

**API Integration:**
```javascript
const handleSubmit = async () => {
  try {
    // Save learning goals
    await axiosInstance.post(API_ENDPOINTS.PERSONALIZATION.GOALS, {
      learning_focus: selectedGoal,
      daily_time_goal: dailyTime
    });

    // Save preferences
    await axiosInstance.post(API_ENDPOINTS.PERSONALIZATION.PREFERENCES, {
      preferred_topics: selectedTopics,
      learning_goal_type: selectedGoal,
      notification_settings: notifications
    });

    setSuccess(true);
    setTimeout(() => onComplete(), 2000);
  } catch (err) {
    setError(err.response?.data?.error || 'Failed to save preferences');
  }
};
```

#### 2. Onboarding Integration

**File:** `ConvAI_frontV1/src/pages/Onboarding.jsx`

**Updated Stepper:**
```javascript
const steps = [
  { label: "Welcome", teluguLabel: "స్వాగతం" },
  { label: "Assessment Info", teluguLabel: "మూల్యాంకన సమాచారం" },
  { label: "Take Assessment", teluguLabel: "మూల్యాంకనం తీసుకోండి" },
  { label: "View Results", teluguLabel: "ఫలితాలు చూడండి" },
  { label: "Set Goals", teluguLabel: "లక్ష్యాలను సెట్ చేయండి" }, // NEW
  { label: "Choose Path", teluguLabel: "మార్గాన్ని ఎంచుకోండి" },
  { label: "Get Started", teluguLabel: "ప్రారంభించండి" },
];
```

**Step Rendering:**
```javascript
{activeStep === 4 && (
  <GoalSetting
    proficiencyLevel={assessmentResults?.overall_proficiency_level}
    onComplete={() => setActiveStep(5)}
  />
)}
```

**Flow:**
1. Welcome
2. Assessment Info
3. Take Assessment (navigate to /assessment)
4. View Results (display assessment completion)
5. **Set Goals** (NEW - configure learning preferences)
6. Choose Path (select learning path based on goals)
7. Get Started (complete onboarding)

## User Journey

### Complete Onboarding Flow

```
┌─────────────┐
│   Welcome   │
│  স్వాగతం   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Assessment Info │
│ మూల్యాంకన సమాచారం │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ Take Assessment  │
│ (10-15 questions)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  View Results    │
│ (Proficiency Level)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Set Goals      │ ← NEW STEP
│ • Learning Goal  │
│ • Daily Time     │
│ • Topics         │
│ • Notifications  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Choose Path     │
│ (Based on goals) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Get Started    │
│  (Dashboard)     │
└──────────────────┘
```

### Goal Setting Step Details

**Step 1: Select Learning Goal**
- User sees 4 cards with learning goal options
- Clicks to select their primary focus
- Visual feedback: selected card gets purple gradient border

**Step 2: Set Daily Time**
- Slider appears with 5-60 minute range
- Default: 15 minutes
- Updates in real-time as user drags

**Step 3: Choose Topics**
- 10 topic chips displayed in a grid
- User can select multiple topics (no limit)
- Selected topics show purple background
- Each topic has Telugu translation

**Step 4: Configure Notifications**
- 4 toggle switches for different notification types
- Default: Daily reminders and achievements ON
- User can enable/disable each type

**Submit & Success**
- "Save Preferences" button becomes active
- Shows loading spinner during API calls
- On success: green checkmark animation
- Auto-navigates to Choose Path step after 2 seconds

## Testing Guide

### Manual Testing Checklist

#### 1. Goal Selection
- [ ] All 4 goal cards display correctly with icons and descriptions
- [ ] Clicking a card selects it (purple border appears)
- [ ] Only one goal can be selected at a time
- [ ] "Continue" button is disabled until a goal is selected
- [ ] Telugu labels display correctly

#### 2. Daily Time Commitment
- [ ] Slider moves smoothly from 5 to 60 minutes
- [ ] Time value updates in real-time
- [ ] Visual bar represents the selected time correctly
- [ ] "Continue" button is always enabled

#### 3. Topic Preferences
- [ ] All 10 topic chips display with English and Telugu labels
- [ ] Multiple topics can be selected
- [ ] Selected chips show purple background
- [ ] At least one topic must be selected to continue
- [ ] Validation error shows if no topics selected

#### 4. Notification Settings
- [ ] All 4 toggle switches display correctly
- [ ] Switches can be toggled on/off
- [ ] Default state: daily_reminders and achievements ON
- [ ] "Save Preferences" button is always enabled

#### 5. API Integration
- [ ] Goals are saved to /api/personalization/goals
- [ ] Preferences are saved to /api/personalization/preferences
- [ ] Loading spinner shows during save
- [ ] Error messages display on failure
- [ ] Success animation plays on completion
- [ ] Auto-navigation to next step after success

#### 6. Onboarding Flow
- [ ] Goal Setting step appears after assessment results
- [ ] Proficiency level is passed correctly (if needed)
- [ ] Step 5 in the stepper highlights correctly
- [ ] Navigation proceeds to Choose Path after completion

### API Testing with Postman

#### Test Case 1: Save Preferences

**Request:**
```
POST http://localhost:5000/api/personalization/preferences
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "preferred_topics": ["Food", "Travel", "Work"],
  "learning_goal_type": "conversational",
  "notification_settings": {
    "daily_reminders": true,
    "achievements": true,
    "weekly_reports": false,
    "learning_tips": true
  }
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "ప్రాధాన్యతలు విజయవంతంగా సేవ్ చేయబడ్డాయి",
  "preferences": {
    "preferred_topics": ["Food", "Travel", "Work"],
    "learning_goal_type": "conversational",
    "notification_settings": {
      "daily_reminders": true,
      "achievements": true,
      "weekly_reports": false,
      "learning_tips": true
    }
  }
}
```

#### Test Case 2: Get Preferences

**Request:**
```
GET http://localhost:5000/api/personalization/preferences
Authorization: Bearer <jwt_token>
```

**Expected Response:**
```json
{
  "success": true,
  "preferences": {
    "preferred_topics": ["Food", "Travel", "Work"],
    "learning_goal_type": "conversational",
    "notification_settings": {
      "daily_reminders": true,
      "achievements": true,
      "weekly_reports": false,
      "learning_tips": true
    }
  }
}
```

#### Test Case 3: Invalid Request (Missing Fields)

**Request:**
```
POST http://localhost:5000/api/personalization/preferences
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "preferred_topics": []
}
```

**Expected Response:**
```json
{
  "error": "preferred_topics, learning_goal_type, and notification_settings are required"
}
```

### Integration Testing

#### End-to-End Flow Test

1. **Start Onboarding**
   ```
   Navigate to: http://localhost:5173/onboarding
   Verify: Welcome step displays
   ```

2. **Complete Assessment**
   ```
   Click: "Start Assessment"
   Complete: 10-15 questions
   Verify: Results display with proficiency level
   ```

3. **Set Goals**
   ```
   Click: "Continue" on Results step
   Verify: Goal Setting component loads
   
   Step 1: Select "Conversational Fluency"
   Verify: Card shows purple border
   Click: "Continue"
   
   Step 2: Move slider to 30 minutes
   Verify: Time displays as "30 minutes"
   Click: "Continue"
   
   Step 3: Select "Food", "Travel", "Work"
   Verify: 3 chips show purple background
   Click: "Continue"
   
   Step 4: Toggle settings
   - Keep Daily Reminders ON
   - Keep Achievements ON
   - Turn Weekly Reports ON
   - Keep Learning Tips ON
   Click: "Save Preferences"
   
   Verify: Loading spinner shows
   Verify: Success animation plays
   Verify: Auto-navigation to Choose Path
   ```

4. **Choose Path**
   ```
   Verify: Learning paths display
   Select: A learning path
   Click: "Continue"
   ```

5. **Get Started**
   ```
   Verify: Success message displays
   Click: "Complete & Start Learning"
   Verify: Redirects to Dashboard
   ```

## Database Schema

### User Table Updates

```sql
-- New columns added to users table
ALTER TABLE users ADD COLUMN preferred_topics JSON;
ALTER TABLE users ADD COLUMN learning_goal_type VARCHAR(50);
ALTER TABLE users ADD COLUMN notification_settings JSON;

-- Example data
UPDATE users SET 
  preferred_topics = '["Food", "Travel", "Work"]',
  learning_goal_type = 'conversational',
  notification_settings = '{
    "daily_reminders": true,
    "achievements": true,
    "weekly_reports": false,
    "learning_tips": true
  }'
WHERE id = 1;
```

### UserGoal Table

Already exists in the schema:
```sql
CREATE TABLE user_goals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    learning_focus VARCHAR(100),
    daily_time_goal INTEGER,
    target_completion_date DATE,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Configuration

### API Endpoints Config

**File:** `ConvAI_frontV1/src/config/api.js`

```javascript
PERSONALIZATION: {
  GOALS: '/personalization/goals',
  PREFERENCES: '/personalization/preferences', // Already configured
  DASHBOARD: '/personalization/dashboard',
  // ... other endpoints
}
```

## Error Handling

### Frontend Error Scenarios

1. **Network Error**
   ```javascript
   Display: "Network error. Please check your connection."
   Action: Allow retry
   ```

2. **Validation Error**
   ```javascript
   Display: "Please select at least one topic"
   Action: Prevent submit, highlight field
   ```

3. **Server Error (500)**
   ```javascript
   Display: "Server error. Please try again later."
   Action: Allow retry
   ```

4. **Authentication Error (401)**
   ```javascript
   Display: "Session expired. Please log in again."
   Action: Redirect to login
   ```

### Backend Error Scenarios

1. **Missing Required Fields**
   ```python
   return jsonify({"error": "preferred_topics, learning_goal_type, and notification_settings are required"}), 400
   ```

2. **Invalid JSON Format**
   ```python
   return jsonify({"error": "Invalid JSON format"}), 400
   ```

3. **Database Save Error**
   ```python
   return jsonify({"error": "Failed to save preferences. Please try again."}), 500
   ```

## Next Steps

### 1. Dashboard Personalization

Update the Dashboard to use saved preferences:

```javascript
// Fetch user preferences
const response = await axiosInstance.get(API_ENDPOINTS.PERSONALIZATION.PREFERENCES);
const { preferred_topics, learning_goal_type } = response.data.preferences;

// Filter recommendations based on topics
const personalizedContent = allContent.filter(item => 
  preferred_topics.includes(item.topic)
);

// Adjust difficulty based on proficiency level
const adjustedContent = personalizedContent.filter(item =>
  item.difficulty === user.proficiency_level
);
```

### 2. Notification System

Implement notifications based on user preferences:

```python
# Check notification settings before sending
if user.notification_settings.get('daily_reminders'):
    send_daily_reminder(user)

if user.notification_settings.get('achievements'):
    send_achievement_notification(user, achievement)

if user.notification_settings.get('weekly_reports'):
    send_weekly_report(user)
```

### 3. Content Recommendation Engine

Use preferences to recommend activities:

```python
def get_personalized_activities(user):
    # Get user preferences
    preferred_topics = user.preferred_topics
    learning_goal = user.learning_goal_type
    proficiency = user.proficiency_level
    
    # Query activities matching preferences
    activities = Activity.query.filter(
        Activity.topic.in_(preferred_topics),
        Activity.goal_type == learning_goal,
        Activity.difficulty_level == proficiency
    ).limit(10).all()
    
    return activities
```

### 4. Progress Tracking

Track adherence to daily time goal:

```python
# Log session time
session = LearningSession(
    user_id=user.id,
    start_time=datetime.utcnow(),
    duration=30,  # minutes
    goal_achieved=True if 30 >= user.daily_time_goal else False
)
db.session.add(session)
db.session.commit()
```

## Troubleshooting

### Common Issues

#### 1. GoalSetting component not showing

**Symptom:** Step 4 doesn't render after assessment results

**Solution:**
- Check if assessment results contain `overall_proficiency_level`
- Verify onComplete callback is passed correctly
- Check console for import errors

#### 2. Preferences not saving

**Symptom:** API returns error when saving preferences

**Solution:**
- Verify JWT token is valid
- Check request payload format matches expected schema
- Ensure all required fields are present
- Check database connectivity

#### 3. Stepper shows wrong step

**Symptom:** Active step indicator is incorrect

**Solution:**
- Verify step numbers after adding Goal Setting step
- Update all step references (changed from 0-5 to 0-6)
- Check navigation callbacks

#### 4. Topics not displaying correctly

**Symptom:** Topic chips missing or not clickable

**Solution:**
- Check TOPICS array in GoalSetting.jsx
- Verify Material-UI Chip component is imported
- Check CSS for chip styling

## Files Modified

### Backend
- ✅ `language-learning-platform/app/api/personalization_routes.py` - Added preferences endpoints

### Frontend
- ✅ `ConvAI_frontV1/src/components/onboarding/GoalSetting.jsx` - Created new component
- ✅ `ConvAI_frontV1/src/pages/Onboarding.jsx` - Integrated Goal Setting step
- ✅ `ConvAI_frontV1/src/config/api.js` - Already has PREFERENCES endpoint

## Summary

The Goal Setting & Personalization feature has been successfully implemented with:

✅ **Backend:**
- POST/GET /api/personalization/preferences endpoints
- Database support for storing preferences
- Error handling and validation

✅ **Frontend:**
- Complete GoalSetting component with 4-step UI
- Integration into Onboarding flow as step 4
- Loading states, error handling, and success animations

✅ **Features:**
- Learning goal selection (4 options)
- Daily time commitment (5-60 minutes)
- Topic preferences (10 topics with Telugu)
- Notification settings (4 types)

**Ready for testing!** Follow the testing guide above to validate the complete onboarding flow.

---

**Last Updated:** January 2025
**Version:** 1.0
**Status:** ✅ Complete and Ready for Testing
