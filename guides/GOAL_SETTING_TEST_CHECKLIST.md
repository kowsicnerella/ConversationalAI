# Goal Setting Feature - Testing & Deployment Checklist

## 🎯 Pre-Testing Setup

### Backend Setup
- [ ] Flask backend is running (`python app.py`)
- [ ] Database is initialized with latest migrations
- [ ] Gemini API key is configured in environment
- [ ] JWT secret is set
- [ ] CORS is configured for frontend origin

### Frontend Setup
- [ ] React dev server is running (`npm run dev`)
- [ ] API endpoints are configured correctly in `api.js`
- [ ] Node modules are installed (`npm install`)
- [ ] No build errors in console

## 🧪 Manual Testing Checklist

### 1. Initial Setup
- [ ] Navigate to `http://localhost:5173/onboarding`
- [ ] User is logged in (check AuthContext)
- [ ] No console errors on page load

### 2. Complete Onboarding Flow

#### Step 1-2: Welcome & Assessment Info
- [ ] Welcome message displays with user's name
- [ ] Telugu translations show correctly
- [ ] "Continue" button works
- [ ] Assessment info page loads
- [ ] "Start Assessment" button works

#### Step 3: Take Assessment
- [ ] Redirects to `/assessment` page
- [ ] Assessment loads without errors
- [ ] Questions display one at a time
- [ ] Can submit answers
- [ ] Feedback displays after each answer
- [ ] Progress indicator updates
- [ ] Complete assessment successfully

#### Step 4: View Results
- [ ] Returns to onboarding at results step
- [ ] Overall score displays correctly
- [ ] Proficiency level shows (Beginner/Intermediate/Advanced/Expert)
- [ ] Skill breakdown visible
- [ ] "Continue" button works

#### Step 5: Set Goals (NEW FEATURE)
**Goal Selection (Step 1 of 4)**
- [ ] Page loads with 4 goal cards
- [ ] Cards display:
  - [ ] Conversational Fluency (💬)
  - [ ] Business English (💼)
  - [ ] Travel English (✈️)
  - [ ] Academic English (📚)
- [ ] Each card shows English and Telugu labels
- [ ] Clicking a card selects it (purple gradient border)
- [ ] Only one card can be selected at a time
- [ ] "Continue" button is disabled until selection
- [ ] "Continue" button works after selection

**Daily Time Commitment (Step 2 of 4)**
- [ ] Slider appears with 5-60 minute range
- [ ] Default value is 15 minutes
- [ ] Slider moves smoothly
- [ ] Time value updates in real-time
- [ ] Visual bar shows time commitment
- [ ] "Continue" button works

**Topic Preferences (Step 3 of 4)**
- [ ] 10 topic chips display in grid:
  - [ ] Food (ఆహారం)
  - [ ] Travel (ప్రయాణం)
  - [ ] Work (పని)
  - [ ] Daily Life (రోజువారీ జీవితం)
  - [ ] Shopping (షాపింగ్)
  - [ ] Health (ఆరోగ్యం)
  - [ ] Education (విద్య)
  - [ ] Technology (సాంకేతికత)
  - [ ] Sports (క్రీడలు)
  - [ ] Entertainment (వినోదం)
- [ ] Chips are clickable
- [ ] Multiple chips can be selected
- [ ] Selected chips show purple background
- [ ] Can deselect chips
- [ ] Validation: At least 1 topic required
- [ ] Error message if no topics selected
- [ ] "Continue" enabled after selection

**Notification Settings (Step 4 of 4)**
- [ ] 4 toggle switches display:
  - [ ] Daily Reminders (రోజువారీ రిమైండర్లు) - Default ON
  - [ ] Achievement Notifications (సాఫల్య నోటిఫికేషన్లు) - Default ON
  - [ ] Weekly Reports (వారపు నివేదికలు) - Default OFF
  - [ ] Learning Tips (నేర్చుకునే చిట్కాలు) - Default ON
- [ ] Switches toggle correctly
- [ ] Telugu labels display
- [ ] "Save Preferences" button is enabled
- [ ] Clicking "Save Preferences" starts loading

**Submission & Success**
- [ ] Loading spinner shows on submit
- [ ] No console errors during API calls
- [ ] Success animation appears (green checkmark)
- [ ] Success message displays in English
- [ ] Success message displays in Telugu
- [ ] Auto-navigates to Choose Path after 2 seconds

#### Step 6: Choose Learning Path
- [ ] Reaches this step after goal setting
- [ ] Learning paths display
- [ ] Can select a path
- [ ] "Continue" button works

#### Step 7: Get Started
- [ ] Success message displays
- [ ] Shows "50 points earned" message
- [ ] "Complete & Start Learning" button works
- [ ] Redirects to Dashboard

### 3. API Integration Testing

#### Save Learning Goals
- [ ] Request sent to `/api/personalization/goals`
- [ ] Request includes `learning_focus` and `daily_time_goal`
- [ ] JWT token sent in Authorization header
- [ ] Response status 200
- [ ] Response includes success message in Telugu

#### Save Preferences
- [ ] Request sent to `/api/personalization/preferences`
- [ ] Request includes:
  - [ ] `preferred_topics` (array)
  - [ ] `learning_goal_type` (string)
  - [ ] `notification_settings` (object)
- [ ] JWT token sent in Authorization header
- [ ] Response status 200
- [ ] Response includes Telugu success message

#### Get Preferences
- [ ] Can retrieve saved preferences
- [ ] GET request to `/api/personalization/preferences`
- [ ] Response includes all saved data
- [ ] Data matches what was saved

### 4. Error Handling

#### Network Errors
- [ ] Stop backend server
- [ ] Try to save preferences
- [ ] Error message displays
- [ ] User can retry after restarting server

#### Validation Errors
- [ ] Try to continue without selecting goal - blocked ✓
- [ ] Try to continue without topics - shows error ✓
- [ ] Invalid data sent - backend returns 400

#### Authentication Errors
- [ ] Token expiry handled
- [ ] Redirects to login if unauthorized
- [ ] Error message is user-friendly

## 🔍 Backend Testing

### Using test_goal_setting.py Script
```bash
cd d:\ConversationalAI
python test_goal_setting.py
```

**Expected Output:**
- [ ] Login successful (200)
- [ ] Save goals successful (200)
- [ ] Save preferences successful (200)
- [ ] Get preferences successful (200)
- [ ] Error handling test (400)
- [ ] All 5/5 tests pass

### Using Postman/cURL

#### Test 1: Save Preferences
```bash
curl -X POST http://localhost:5000/api/personalization/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_topics": ["Food", "Travel", "Work"],
    "learning_goal_type": "conversational",
    "notification_settings": {
      "daily_reminders": true,
      "achievements": true,
      "weekly_reports": false,
      "learning_tips": true
    }
  }'
```

**Expected:**
- [ ] Status: 200
- [ ] Response includes Telugu success message
- [ ] Preferences object in response

#### Test 2: Get Preferences
```bash
curl -X GET http://localhost:5000/api/personalization/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:**
- [ ] Status: 200
- [ ] Preferences object with all saved data

#### Test 3: Invalid Data
```bash
curl -X POST http://localhost:5000/api/personalization/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"preferred_topics": []}'
```

**Expected:**
- [ ] Status: 400
- [ ] Error message about missing fields

## 🗄️ Database Verification

### Check User Table
```sql
SELECT 
  id, 
  username, 
  proficiency_level,
  preferred_topics,
  learning_goal_type,
  notification_settings
FROM users
WHERE id = <test_user_id>;
```

**Verify:**
- [ ] `preferred_topics` contains array of selected topics
- [ ] `learning_goal_type` matches selected goal
- [ ] `notification_settings` is JSON object with 4 keys
- [ ] `proficiency_level` was set by assessment

### Check UserGoals Table
```sql
SELECT 
  id,
  user_id,
  learning_focus,
  daily_time_goal,
  created_at
FROM user_goals
WHERE user_id = <test_user_id>
ORDER BY created_at DESC
LIMIT 1;
```

**Verify:**
- [ ] `learning_focus` matches selected goal
- [ ] `daily_time_goal` matches slider value
- [ ] `created_at` is recent timestamp

## 📱 UI/UX Verification

### Visual Checks
- [ ] All text is readable
- [ ] Colors match design (purple theme)
- [ ] Icons display correctly
- [ ] Animations are smooth
- [ ] No layout shifts
- [ ] Responsive on mobile (test at 375px width)
- [ ] Telugu text renders correctly
- [ ] No overlapping elements

### Accessibility
- [ ] Buttons have clear labels
- [ ] Focus indicators visible
- [ ] Can navigate with keyboard
- [ ] Screen reader friendly (test with NVDA/JAWS if possible)
- [ ] Color contrast meets WCAG standards

### Performance
- [ ] Page loads in < 2 seconds
- [ ] Animations don't lag
- [ ] API calls complete in < 1 second
- [ ] No memory leaks (check DevTools)

## 🚀 Pre-Deployment Checklist

### Code Quality
- [ ] No console.log statements in production code
- [ ] No commented-out code
- [ ] Linting errors resolved (or documented)
- [ ] Code follows project conventions
- [ ] PropTypes added (or documented as optional)

### Documentation
- [ ] README updated with new feature
- [ ] API endpoints documented
- [ ] Component props documented
- [ ] Testing guide complete
- [ ] Known issues documented

### Configuration
- [ ] Environment variables set
- [ ] API URLs correct for production
- [ ] CORS configured for production domain
- [ ] Security headers enabled
- [ ] Rate limiting configured (if needed)

### Testing
- [ ] All manual tests passed
- [ ] API tests passed (test_goal_setting.py)
- [ ] Database updates verified
- [ ] Error scenarios tested
- [ ] Edge cases tested

## ✅ Sign-Off

### Development Team
- [ ] Feature implemented according to requirements
- [ ] Code reviewed
- [ ] Tests passing
- [ ] Documentation complete

### Testing Team
- [ ] Manual testing complete
- [ ] No critical bugs found
- [ ] User experience is smooth
- [ ] Ready for user acceptance testing

### Product Team
- [ ] Feature meets requirements
- [ ] User flow is intuitive
- [ ] Telugu translations are accurate
- [ ] Ready for production

## 📝 Test Results

### Test Session Details
- **Date:** _______________
- **Tester:** _______________
- **Environment:** Development / Staging / Production
- **Browser:** _______________
- **Test Duration:** _______________

### Issues Found
| # | Description | Severity | Status | Notes |
|---|-------------|----------|--------|-------|
| 1 |             |          |        |       |
| 2 |             |          |        |       |
| 3 |             |          |        |       |

### Overall Status
- [ ] 🟢 **PASS** - Ready for deployment
- [ ] 🟡 **PASS WITH NOTES** - Minor issues documented
- [ ] 🔴 **FAIL** - Critical issues must be fixed

### Notes
```
Add any additional notes here...
```

## 🎉 Post-Deployment Verification

### After Deploy
- [ ] Feature accessible in production
- [ ] All API endpoints working
- [ ] Database updates happening
- [ ] No errors in production logs
- [ ] Analytics tracking working (if configured)
- [ ] Performance metrics acceptable

### User Feedback
- [ ] Monitor user completion rate
- [ ] Track most selected goals
- [ ] Track most selected topics
- [ ] Collect user feedback
- [ ] Monitor error rates

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Ready for Testing  
