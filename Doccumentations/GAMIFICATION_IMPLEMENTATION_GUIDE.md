# Gamification System - Complete Implementation Guide

## 🎮 Overview
The Gamification System motivates users through points, badges, streaks, and leaderboards. Users earn points for completing activities, unlock badges for achievements, maintain daily streaks, and compete on leaderboards.

---

## ✅ Implementation Status

### **Backend - 100% Complete** ✅
All gamification features are fully implemented and integrated.

### **Frontend - 0% Complete** ⚠️
Components need to be created.

### **Database - Needs Initialization** ⚠️
Badges need to be added to the database via initialization script.

---

## 🏗️ Architecture

### 1. **Database Models** ✅

**Location:** `app/models/gamification.py`

#### Badge Model
```python
class Badge(db.Model):
    id = Integer (Primary Key)
    name = String (e.g., "First Steps")
    name_telugu = String (e.g., "మొదటి అడుగులు")
    description = String
    description_telugu = String
    icon_name = String (e.g., "star", "fire", "book")
    requirement_type = String (activity_count, streak, points, specific_activity)
    requirement_value = Integer
    requirement_metadata = JSON (optional filters: activity_type, level)
    points_reward = Integer (bonus points on unlock)
    rarity = String (common, rare, epic, legendary)
    created_at = DateTime
```

#### UserBadge Model
```python
class UserBadge(db.Model):
    id = Integer (Primary Key)
    user_id = Integer (Foreign Key → User)
    badge_id = Integer (Foreign Key → Badge)
    earned_at = DateTime
    progress = Integer (current progress toward next tier)
```

#### Achievement Model
```python
class Achievement(db.Model):
    id = Integer (Primary Key)
    user_id = Integer (Foreign Key → User)
    achievement_type = String (first_quiz, first_writing, etc.)
    earned_at = DateTime
    points_awarded = Integer
```

### 2. **Gamification Service** ✅

**Location:** `app/services/gamification_service.py`

**Key Methods:**

#### `award_activity_points(user_id, activity_type, activity_data)`
Awards points based on activity type:
- **Quiz**: 8 points per correct answer
- **Flashcard**: 1 point per card reviewed
- **Reading**: 20 points flat
- **Writing**: 50 points flat
- **Role-Play**: 30 points flat

**Returns:**
```python
{
    'points_awarded': 40,
    'total_points': 340,
    'new_badges': [
        {
            'id': 1,
            'name': 'First Steps',
            'name_telugu': 'మొదటి అడుగులు',
            'description': 'Complete your first activity',
            'icon_name': 'star',
            'points_reward': 10
        }
    ],
    'level_up': False,
    'new_level': 3
}
```

#### `update_streak(user_id)`
Updates daily streak and awards bonuses:
- **Daily Goal (3 activities)**: +25 bonus points
- **7-Day Streak**: +100 bonus points
- Resets streak if user missed a day

#### `check_for_new_achievements(user_id)`
Checks and unlocks badges when criteria met:
- Activity count badges
- Streak badges
- Points milestone badges
- Specific activity badges

#### `get_leaderboard(timeframe='weekly', limit=100)`
Returns ranked user list with points.

**Timeframes:**
- `all_time`: Total points ever
- `weekly`: Points earned in last 7 days
- `monthly`: Points earned in last 30 days

### 3. **API Endpoints** ✅

**Location:** `app/api/gamification_routes.py`

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|----------------|
| `/api/gamification/points` | GET | Get user's total points | JWT Required |
| `/api/gamification/badges` | GET | Get user's badges (earned + available) | JWT Required |
| `/api/gamification/leaderboard` | GET | Get ranked user list | JWT Required |
| `/api/gamification/daily-challenge` | GET | Get today's challenge | JWT Required |
| `/api/gamification/daily-challenge` | POST | Complete daily challenge | JWT Required |
| `/api/gamification/stats` | GET | Get comprehensive stats | JWT Required |
| `/api/gamification/achievements` | GET | Get achievement history | JWT Required |

**Example Requests:**

**Get Points:**
```bash
GET /api/gamification/points
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "total_points": 340,
  "weekly_points": 120,
  "monthly_points": 340,
  "rank": 5,
  "level": 3
}
```

**Get Badges:**
```bash
GET /api/gamification/badges
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "earned_badges": [
    {
      "id": 1,
      "name": "First Steps",
      "earned_at": "2025-10-09T10:00:00",
      "progress": 1
    }
  ],
  "available_badges": [
    {
      "id": 2,
      "name": "Bookworm",
      "description": "Complete 10 reading activities",
      "requirement_type": "activity_count",
      "requirement_value": 10,
      "user_progress": 3,
      "percentage": 30
    }
  ],
  "total_badges": 7,
  "earned_count": 1
}
```

**Get Leaderboard:**
```bash
GET /api/gamification/leaderboard?timeframe=weekly&limit=10
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 5,
      "username": "john_doe",
      "points": 450,
      "level": 4,
      "badge_count": 5
    },
    {
      "rank": 2,
      "user_id": 12,
      "username": "jane_smith",
      "points": 340,
      "level": 3,
      "badge_count": 3
    }
  ],
  "user_rank": 5,
  "total_users": 42,
  "timeframe": "weekly"
}
```

**Get Stats:**
```bash
GET /api/gamification/stats
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "total_points": 340,
  "current_streak": 5,
  "longest_streak": 12,
  "badges_earned": 3,
  "badges_available": 4,
  "achievements_unlocked": 8,
  "activities_completed": 25,
  "quiz_completed": 10,
  "flashcard_completed": 8,
  "writing_completed": 4,
  "roleplay_completed": 3,
  "level": 3,
  "points_to_next_level": 60
}
```

### 4. **Activity Integration** ✅

**Location:** `app/api/activities_routes.py`

All activity completion endpoints now award points:

**Quiz Completion:**
```python
@activities_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_activity():
    # ... quiz logic ...
    
    # Award points
    gamification_data = gamification_service.award_activity_points(
        user_id=user_id,
        activity_type='quiz',
        activity_data={
            'correct_count': correct_count,
            'total_questions': total_questions
        }
    )
    
    return jsonify({
        'score': score,
        'points_earned': points_earned,
        'gamification': gamification_data  # NEW
    })
```

**Flashcard Completion:**
```python
# Same as quiz - uses submit_activity endpoint
# Points calculated: 1 per card reviewed
```

**Writing Completion:**
```python
# Same as quiz - uses submit_activity endpoint
# Points awarded: 50 flat
```

**Role-Play Completion:**
```python
@activities_bp.route('/complete-roleplay', methods=['POST'])
@jwt_required()
def complete_roleplay():
    # ... roleplay logic ...
    
    gamification_data = gamification_service.award_activity_points(
        user_id=user_id,
        activity_type='roleplay',
        activity_data={'completed': True}
    )
    
    return jsonify({
        'evaluation': evaluation,
        'gamification': gamification_data  # NEW
    })
```

**Reading Completion:**
```python
@activities_bp.route('/complete-reading', methods=['POST'])
@jwt_required()
def complete_reading():
    # Mark session complete
    session.status = 'completed'
    
    gamification_data = gamification_service.award_activity_points(
        user_id=user_id,
        activity_type='reading',
        activity_data={'session_id': session_id}
    )
    
    return jsonify({
        'message': 'Reading activity completed',
        'gamification': gamification_data  # NEW
    })
```

---

## 🎯 Points System

### Activity Points

| Activity | Points Calculation | Example |
|----------|-------------------|---------|
| **Quiz** | 8 points per correct answer | 5/10 correct = 40 pts |
| **Flashcard** | 1 point per card reviewed | 10 cards = 10 pts |
| **Reading** | 20 points flat | 20 pts |
| **Writing** | 50 points flat | 50 pts |
| **Role-Play** | 30 points flat | 30 pts |

### Bonus Points

| Bonus | Requirement | Points |
|-------|------------|--------|
| **Daily Goal** | Complete 3 activities in one day | +25 pts |
| **7-Day Streak** | Maintain streak for 7 consecutive days | +100 pts |
| **Badge Unlock** | Unlock a new badge | Varies by badge |

### Level System
```python
Level 1: 0-99 points
Level 2: 100-299 points
Level 3: 300-599 points
Level 4: 600-999 points
Level 5: 1000+ points
```

---

## 🏅 Badge System

### 7 Required Badges

#### 1. **First Steps** (Common)
- **Requirement**: Complete first activity (any type)
- **Type**: `activity_count`
- **Value**: 1
- **Points Reward**: 10
- **Icon**: `star`

#### 2. **Bookworm** (Rare)
- **Requirement**: Complete 10 reading activities
- **Type**: `specific_activity`
- **Value**: 10
- **Metadata**: `{"activity_type": "reading"}`
- **Points Reward**: 50
- **Icon**: `book`

#### 3. **Word Smith** (Rare)
- **Requirement**: Complete 5 writing activities
- **Type**: `specific_activity`
- **Value**: 5
- **Metadata**: `{"activity_type": "writing"}`
- **Points Reward**: 40
- **Icon**: `edit`

#### 4. **Hot Streak** (Epic)
- **Requirement**: Maintain 7-day streak
- **Type**: `streak`
- **Value**: 7
- **Points Reward**: 100
- **Icon**: `fire`

#### 5. **Century** (Rare)
- **Requirement**: Earn 100 total points
- **Type**: `points`
- **Value**: 100
- **Points Reward**: 20
- **Icon**: `trophy`

#### 6. **Champion** (Legendary)
- **Requirement**: Earn 1000 total points
- **Type**: `points`
- **Value**: 1000
- **Points Reward**: 200
- **Icon**: `crown`

#### 7. **Conversationalist** (Rare)
- **Requirement**: Complete 10 role-play activities
- **Type**: `specific_activity`
- **Value**: 10
- **Metadata**: `{"activity_type": "roleplay"}`
- **Points Reward**: 50
- **Icon**: `chat`

---

## 🔥 Streak System

### How Streaks Work

**Daily Activity Tracking:**
- User must complete at least 1 activity per day
- Midnight UTC resets the "today" counter
- Streak increments if activity completed on consecutive days

**Streak Bonuses:**
- **3 Activities in One Day**: +25 bonus points (Daily Goal)
- **7 Consecutive Days**: +100 bonus points + "Hot Streak" badge

**Streak Reset:**
- If user skips a day → streak resets to 0
- User can rebuild streak from day 1

**Database Storage:**
```python
class User:
    current_streak = Integer (days, default 0)
    longest_streak = Integer (max days ever achieved)
    last_activity_date = Date (tracks last activity)
```

---

## 📊 Leaderboard System

### Timeframe Options

**All-Time:**
- Ranks by total_points (lifetime)
- Most prestigious ranking

**Weekly:**
- Ranks by points earned in last 7 days
- Resets every Monday (or rolling 7 days)
- Encourages ongoing participation

**Monthly:**
- Ranks by points earned in last 30 days
- Good for medium-term competition

### Leaderboard Data
```python
{
    'rank': 1,
    'user_id': 5,
    'username': 'john_doe',
    'points': 450,  # Points in timeframe
    'level': 4,
    'badge_count': 5,
    'current_streak': 12
}
```

---

## 🎮 Daily Challenge System

### Challenge Types

**Activity-Based:**
- Complete 3 quizzes
- Complete 1 writing activity
- Review 20 flashcards

**Performance-Based:**
- Score 80%+ on a quiz
- Maintain your streak
- Earn 50 points today

### Challenge Rewards
- **Completion**: +25 bonus points
- **Streak Contribution**: Counts toward daily activity
- **Badge Progress**: Contributes to activity count badges

---

## 🚀 Testing Guide

### 1. Test Points Awarding

**Complete a Quiz:**
```bash
POST /api/activities/submit
{
  "session_id": 1,
  "activity_type": "quiz",
  "user_answers": [0, 2, 1, 3, 0],
  "time_spent": 120
}

Expected Response:
{
  "score": 40,
  "points_earned": 32,  # 4 correct * 8 pts
  "gamification": {
    "points_awarded": 32,
    "total_points": 32,
    "new_badges": [
      {
        "name": "First Steps",
        "points_reward": 10
      }
    ],
    "level_up": False,
    "new_level": 1
  }
}
```

**Complete Writing:**
```bash
POST /api/activities/submit
{
  "session_id": 2,
  "activity_type": "writing",
  "user_input": "My family is very loving...",
  "time_spent": 300
}

Expected Response:
{
  "evaluation": {...},
  "points_earned": 50,
  "gamification": {
    "points_awarded": 50,
    "total_points": 82,  # 32 + 50
    "new_badges": [],
    "level_up": False
  }
}
```

### 2. Test Badge Unlocking

**Check for New Badges:**
```bash
# Complete first activity → "First Steps" unlocks
# Complete 5 writing activities → "Word Smith" unlocks
# Earn 100 points → "Century" unlocks

GET /api/gamification/badges

Verify:
- earned_badges array contains unlocked badges
- available_badges shows progress toward locked badges
- user_progress increases after each activity
```

### 3. Test Streak System

**Day 1:**
```bash
POST /api/activities/submit
# Complete 1 activity
# current_streak = 1
```

**Day 2 (next day):**
```bash
POST /api/activities/submit
# Complete 1 activity
# current_streak = 2
```

**Day 2 (3rd activity same day):**
```bash
POST /api/activities/submit
# Complete 3rd activity today
# Bonus: +25 points (Daily Goal)
# total_points += 25
```

**Day 8 (7 consecutive days):**
```bash
POST /api/activities/submit
# current_streak = 7
# Bonus: +100 points (7-Day Streak)
# Badge Unlocked: "Hot Streak"
# total_points += 100
```

**Day 10 (skip day 9):**
```bash
POST /api/activities/submit
# current_streak = 1 (RESET)
# longest_streak = 8 (preserved)
```

### 4. Test Leaderboard

**Get Weekly Leaderboard:**
```bash
GET /api/gamification/leaderboard?timeframe=weekly&limit=10

Verify:
- Users ranked by weekly_points (desc)
- user_rank shows current user's position
- total_users shows participant count
```

---

## 📁 File Structure

### Backend Files (Complete ✅)
```
app/
├── models/
│   └── gamification.py         # Badge, UserBadge, Achievement models
├── services/
│   └── gamification_service.py # Points, badges, streaks logic
├── api/
│   └── gamification_routes.py  # JWT-protected endpoints
│   └── activities_routes.py    # Updated with gamification calls
└── init_badges.py              # Badge initialization script
```

### Frontend Files (To Be Created ⚠️)
```
src/
├── components/
│   ├── gamification/
│   │   ├── PointsDisplay.jsx       # Real-time points counter
│   │   ├── BadgesGrid.jsx          # Badge showcase
│   │   ├── BadgeCard.jsx           # Individual badge display
│   │   ├── BadgeUnlockModal.jsx    # Celebration modal
│   │   ├── Leaderboard.jsx         # Rankings table
│   │   ├── StreakTracker.jsx       # Streak counter
│   │   └── DailyChallenge.jsx      # Challenge card
├── pages/
│   └── Profile.jsx                 # Update to show badges
└── config/
    └── api.js                      # Add gamification endpoints
```

---

## 🎯 Initialization Steps

### 1. Initialize Badges in Database

**Run the initialization script:**
```bash
cd language-learning-platform
python init_badges.py
```

**Expected Output:**
```
Initializing 7 gamification badges...
✓ First Steps badge created
✓ Bookworm badge created
✓ Word Smith badge created
✓ Hot Streak badge created
✓ Century badge created
✓ Champion badge created
✓ Conversationalist badge created
Successfully initialized 7 badges!
```

**Verify in Database:**
```sql
SELECT id, name, requirement_type, requirement_value, points_reward
FROM badge
ORDER BY id;
```

### 2. Test Backend APIs

See testing guide above for detailed test scenarios.

### 3. Create Frontend Components

See frontend file structure and component specifications below.

---

## 🎨 Frontend Component Specifications

### PointsDisplay Component
```jsx
<PointsDisplay 
  points={340} 
  animated={true}
  showLevel={true}
  level={3}
/>

Features:
- Animated counter on points increase
- Trophy/star icon
- Level badge display
- Pulse animation on new points
```

### BadgesGrid Component
```jsx
<BadgesGrid 
  earnedBadges={[...]}
  availableBadges={[...]}
  showProgress={true}
/>

Features:
- Grid layout (3-4 columns)
- Earned badges in color
- Locked badges in grayscale
- Progress bar for locked badges
- Tooltip with description
- Click to view details
```

### BadgeUnlockModal Component
```jsx
<BadgeUnlockModal 
  badge={{name: "First Steps", icon: "star", points_reward: 10}}
  onClose={() => {}}
/>

Features:
- Celebration animation (confetti)
- Badge icon large display
- Badge name + description
- Points reward highlighted
- "Awesome!" message
- Close button
```

### Leaderboard Component
```jsx
<Leaderboard 
  timeframe="weekly"
  limit={10}
  showUserRank={true}
/>

Features:
- Timeframe selector (All-Time/Weekly/Monthly)
- Top 10 user list
- Rank, username, points, level, badges
- Highlight current user
- Pagination (if > 10)
```

### StreakTracker Component
```jsx
<StreakTracker 
  currentStreak={5}
  longestStreak={12}
  showFire={true}
/>

Features:
- Fire emoji/icon (🔥)
- Current streak counter
- Longest streak display
- Streak progress bar to next milestone
- Motivational message
```

---

## 💡 Integration Example

### Activity Completion Flow with Gamification

**Before (No Gamification):**
```jsx
const handleSubmitQuiz = async () => {
  const response = await api.post('/activities/submit', {
    session_id: sessionId,
    user_answers: answers
  });
  
  setScore(response.data.score);
  // Done
};
```

**After (With Gamification):**
```jsx
const handleSubmitQuiz = async () => {
  const response = await api.post('/activities/submit', {
    session_id: sessionId,
    user_answers: answers
  });
  
  setScore(response.data.score);
  
  // Handle gamification data
  const { gamification } = response.data;
  
  // Update points display
  setUserPoints(gamification.total_points);
  
  // Show points earned animation
  showPointsAnimation(gamification.points_awarded);
  
  // Show badge unlock modal if new badges
  if (gamification.new_badges.length > 0) {
    showBadgeUnlockModal(gamification.new_badges[0]);
  }
  
  // Show level up notification
  if (gamification.level_up) {
    showLevelUpNotification(gamification.new_level);
  }
};
```

---

## 🎯 Success Criteria

### Backend ✅
- [x] Badge models created
- [x] Gamification service implemented
- [x] Points calculation working
- [x] Badge unlock logic complete
- [x] Streak tracking functional
- [x] API endpoints created with JWT auth
- [x] Activity integration complete
- [ ] Badges initialized in database (run script)

### Frontend ⚠️
- [ ] PointsDisplay component
- [ ] BadgesGrid component
- [ ] BadgeUnlockModal component
- [ ] Leaderboard component
- [ ] StreakTracker component
- [ ] Integration with activity completion
- [ ] Real-time updates on points/badges

---

**Implementation Date:** January 9, 2025  
**Backend Status:** ✅ 100% Complete  
**Frontend Status:** ⚠️ 0% Complete  
**Priority:** HIGH - Core engagement feature  
**Estimated Frontend Time:** 4-6 hours
