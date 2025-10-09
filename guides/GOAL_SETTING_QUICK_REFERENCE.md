# Goal Setting & Personalization - Quick Reference

## 🎯 Feature Overview

After completing the initial assessment, users configure their learning preferences through a 4-step guided process.

## 📋 Quick Implementation Status

| Component | Status | File |
|-----------|--------|------|
| Backend API | ✅ Complete | `language-learning-platform/app/api/personalization_routes.py` |
| Frontend UI | ✅ Complete | `ConvAI_frontV1/src/components/onboarding/GoalSetting.jsx` |
| Integration | ✅ Complete | `ConvAI_frontV1/src/pages/Onboarding.jsx` |
| Documentation | ✅ Complete | `GOAL_SETTING_IMPLEMENTATION.md` |

## 🚀 API Endpoints

### Save Preferences
```bash
POST /api/personalization/preferences
Authorization: Bearer <token>

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

### Get Preferences
```bash
GET /api/personalization/preferences
Authorization: Bearer <token>
```

## 🎨 UI Component

### GoalSetting Component
**Location:** `src/components/onboarding/GoalSetting.jsx`

**Props:**
- `proficiencyLevel` (optional): User's assessed level
- `onComplete` (required): Callback when preferences saved

**Usage:**
```jsx
<GoalSetting
  proficiencyLevel={assessmentResults?.overall_proficiency_level}
  onComplete={() => setActiveStep(5)}
/>
```

## 📊 4-Step Process

### Step 1: Learning Goal Selection
- **Options:** Conversational Fluency, Business English, Travel English, Academic English
- **UI:** 4 cards with icons and descriptions
- **Validation:** Must select one

### Step 2: Daily Time Commitment
- **Range:** 5-60 minutes
- **Default:** 15 minutes
- **UI:** Slider with real-time display

### Step 3: Topic Preferences
- **Options:** Food, Travel, Work, Daily Life, Shopping, Health, Education, Technology, Sports, Entertainment
- **UI:** Chip selection (multi-select)
- **Validation:** At least one required
- **Features:** Telugu labels for each topic

### Step 4: Notification Settings
- **Options:**
  - Daily Reminders (రోజువారీ రిమైండర్లు)
  - Achievement Notifications (సాఫల్య నోటిఫికేషన్లు)
  - Weekly Reports (వారపు నివేదికలు)
  - Learning Tips (నేర్చుకునే చిట్కాలు)
- **Default:** Daily reminders and achievements ON

## 🔄 Onboarding Flow

```
Step 0: Welcome
Step 1: Assessment Info
Step 2: Take Assessment
Step 3: View Results
Step 4: Set Goals ← NEW STEP
Step 5: Choose Path
Step 6: Get Started
```

## ✅ Testing Checklist

### Quick Manual Test
1. ✓ Complete assessment
2. ✓ View results page
3. ✓ Click "Continue" - should load Goal Setting
4. ✓ Select a learning goal (e.g., Conversational)
5. ✓ Set time to 30 minutes
6. ✓ Select 3 topics (Food, Travel, Work)
7. ✓ Toggle notifications as desired
8. ✓ Click "Save Preferences"
9. ✓ Watch for success animation
10. ✓ Verify auto-navigation to Choose Path

### API Test with cURL
```bash
# Save preferences
curl -X POST http://localhost:5000/api/personalization/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_topics": ["Food", "Travel"],
    "learning_goal_type": "conversational",
    "notification_settings": {
      "daily_reminders": true,
      "achievements": true,
      "weekly_reports": false,
      "learning_tips": true
    }
  }'

# Get preferences
curl -X GET http://localhost:5000/api/personalization/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Component not rendering | Check if GoalSetting imported in Onboarding.jsx |
| API 400 error | Verify all required fields in request payload |
| Topics not saving | Check if preferred_topics is an array |
| Navigation broken | Ensure step numbers updated (0-6 instead of 0-5) |

## 📦 Key Files

### Backend
- `app/api/personalization_routes.py` - API endpoints

### Frontend
- `src/components/onboarding/GoalSetting.jsx` - Main component
- `src/pages/Onboarding.jsx` - Integration
- `src/config/api.js` - API configuration

### Documentation
- `GOAL_SETTING_IMPLEMENTATION.md` - Complete implementation guide
- `GOAL_SETTING_QUICK_REFERENCE.md` - This file

## 🎯 Next Steps

1. **Test end-to-end flow** - Complete onboarding from start to finish
2. **Dashboard integration** - Use preferences to show personalized content
3. **Notification system** - Implement based on notification_settings
4. **Analytics** - Track which goals and topics are most popular

## 💡 Data Structure

### User Preferences Object
```javascript
{
  preferred_topics: ["Food", "Travel", "Work"],
  learning_goal_type: "conversational",
  notification_settings: {
    daily_reminders: true,
    achievements: true,
    weekly_reports: false,
    learning_tips: true
  }
}
```

### Learning Goals
- `conversational` - Conversational Fluency
- `business` - Business English
- `travel` - Travel English
- `academic` - Academic English

### Available Topics
- Food (ఆహారం)
- Travel (ప్రయాణం)
- Work (పని)
- Daily Life (రోజువారీ జీవితం)
- Shopping (షాపింగ్)
- Health (ఆరోగ్యం)
- Education (విద్య)
- Technology (సాంకేతికత)
- Sports (క్రీడలు)
- Entertainment (వినోదం)

## 🚀 Quick Start Commands

### Start Backend
```bash
cd language-learning-platform
python app.py
```

### Start Frontend
```bash
cd ConvAI_frontV1
npm run dev
```

### Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Onboarding: http://localhost:5173/onboarding

## 📞 Support

For detailed implementation information, see `GOAL_SETTING_IMPLEMENTATION.md`

---

**Status:** ✅ Ready for Testing  
**Last Updated:** January 2025
