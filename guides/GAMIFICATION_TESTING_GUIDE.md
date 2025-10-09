# Gamification System - Comprehensive Testing Guide

## 🎯 Overview
This guide provides step-by-step testing scenarios for the complete gamification system including points, badges, streaks, and leaderboards.

---

## ✅ Pre-Testing Checklist

### 1. Initialize Badges
```bash
cd language-learning-platform
python init_badges.py
```

**Expected Output:**
```
🎮 Initializing Gamification Badges...
==================================================
✅ Created badge: First Steps (common)
   Complete your first activity
   Requirement: activities_completed = 1
   Reward: 10 points

✅ Created badge: Bookworm (rare)
   Complete 10 reading activities
   Requirement: reading_completed = 10
   Reward: 50 points

✅ Created badge: Word Smith (rare)
   Complete 5 writing activities
   Requirement: writing_completed = 5
   Reward: 50 points

✅ Created badge: Hot Streak (epic)
   Maintain a 7-day learning streak
   Requirement: streak_days = 7
   Reward: 100 points

✅ Created badge: Century (uncommon)
   Earn 100 total points
   Requirement: points_earned = 100
   Reward: 20 points

✅ Created badge: Champion (legendary)
   Earn 1000 total points
   Requirement: points_earned = 1000
   Reward: 200 points

✅ Created badge: Conversationalist (rare)
   Complete 10 role-playing activities
   Requirement: roleplay_completed = 10
   Reward: 75 points

==================================================
✅ Successfully initialized 7 badges!
```

### 2. Verify Database
```sql
SELECT id, name, requirement_type, requirement_value, points_reward, rarity
FROM badge
ORDER BY id;
```

**Expected Result:** 7 rows with all badges

### 3. Start Backend Server
```bash
python app.py
```

**Expected:**
```
 * Running on http://127.0.0.1:5000
```

### 4. Start Frontend (Separate Terminal)
```bash
cd ConvAI_frontV1
npm run dev
```

---

## 📋 Test Scenarios

### **Test 1: First Activity & "First Steps" Badge** 🎯

**Objective:** Verify points awarded for first quiz and "First Steps" badge unlock.

**Steps:**

1. **Create Learning Session (Quiz):**
```bash
POST http://127.0.0.1:5000/api/learning-sessions
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "learning_path_id": 1,
  "chapter_id": 1,
  "activity_type": "quiz",
  "difficulty": "beginner"
}
```

**Expected Response:**
```json
{
  "id": 1,
  "activity_type": "quiz",
  "content": {
    "questions": [
      {
        "question": "What does 'నమస్కారం' mean in English?",
        "options": ["Hello", "Goodbye", "Thank you", "Sorry"],
        "correct_answer": 0
      },
      // ... 4 more questions
    ]
  }
}
```

2. **Complete Quiz (3/5 correct):**
```bash
POST http://127.0.0.1:5000/api/activities/submit
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "session_id": 1,
  "activity_type": "quiz",
  "user_answers": [0, 1, 2, 3, 1],  # 3 correct (indices 0, 1, 4)
  "time_spent": 120
}
```

**Expected Response:**
```json
{
  "message": "Activity completed successfully",
  "score": 60,
  "points_earned": 24,  # 3 correct * 8 points
  "total_questions": 5,
  "correct_answers": 3,
  "gamification": {
    "points_awarded": 24,
    "total_points": 34,  # 24 + 10 (First Steps bonus)
    "new_badges": [
      {
        "id": 1,
        "name": "First Steps",
        "description": "Complete your first activity",
        "points_reward": 10,
        "rarity": "common",
        "icon_url": "🎯"
      }
    ],
    "level_up": false,
    "new_level": 1
  }
}
```

**Verification:**

3. **Check User Points:**
```bash
GET http://127.0.0.1:5000/api/gamification/points
Authorization: Bearer <JWT_TOKEN>
```

**Expected:**
```json
{
  "total_points": 34,
  "weekly_points": 34,
  "monthly_points": 34,
  "rank": 1,
  "level": 1
}
```

4. **Check User Badges:**
```bash
GET http://127.0.0.1:5000/api/gamification/badges
Authorization: Bearer <JWT_TOKEN>
```

**Expected:**
```json
{
  "earned_badges": [
    {
      "id": 1,
      "name": "First Steps",
      "description": "Complete your first activity",
      "earned_at": "2025-01-09T15:30:00",
      "points_reward": 10,
      "rarity": "common"
    }
  ],
  "available_badges": [
    {
      "id": 2,
      "name": "Bookworm",
      "description": "Complete 10 reading activities",
      "requirement_type": "reading_completed",
      "requirement_value": 10,
      "user_progress": 0,
      "percentage": 0
    },
    // ... other 5 badges
  ],
  "total_badges": 7,
  "earned_count": 1
}
```

**✅ Success Criteria:**
- Quiz completion awards 24 points (3 * 8)
- "First Steps" badge unlocks automatically
- Badge adds 10 bonus points (total 34)
- Badge appears in earned_badges array

---

### **Test 2: Writing Activity & Point Accumulation** ✍️

**Objective:** Verify 50 points awarded for writing and progress toward "Word Smith" badge.

**Steps:**

1. **Create Writing Session:**
```bash
POST http://127.0.0.1:5000/api/learning-sessions
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "learning_path_id": 1,
  "chapter_id": 2,
  "activity_type": "writing",
  "difficulty": "beginner"
}
```

2. **Complete Writing Activity:**
```bash
POST http://127.0.0.1:5000/api/activities/submit
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "session_id": 2,
  "activity_type": "writing",
  "user_input": "My family is very loving. My father works as a teacher. My mother cooks delicious food. I have one sister who is studying in college. We enjoy spending time together on weekends.",
  "time_spent": 300
}
```

**Expected Response:**
```json
{
  "message": "Activity completed successfully",
  "evaluation": {
    "score": 85,
    "grammar_feedback": [...],
    "vocabulary_suggestions": [...]
  },
  "points_earned": 50,
  "gamification": {
    "points_awarded": 50,
    "total_points": 84,  # 34 + 50
    "new_badges": [],
    "level_up": false,
    "new_level": 1
  }
}
```

**Verification:**

3. **Check Badge Progress:**
```bash
GET http://127.0.0.1:5000/api/gamification/badges
```

**Expected:**
```json
{
  "available_badges": [
    {
      "id": 3,
      "name": "Word Smith",
      "description": "Complete 5 writing activities",
      "requirement_value": 5,
      "user_progress": 1,  # NOW 1/5
      "percentage": 20
    }
  ]
}
```

**✅ Success Criteria:**
- Writing awards 50 points flat
- Total points now 84
- Word Smith progress increases to 1/5 (20%)

---

### **Test 3: "Century" Badge Unlock** 💯

**Objective:** Earn 100+ points to unlock "Century" badge.

**Current Points:** 84  
**Needed:** 16+ more points

**Steps:**

1. **Complete Another Quiz (2/5 correct = 16 points):**
```bash
# Create session
POST /api/learning-sessions
{
  "activity_type": "quiz",
  "difficulty": "beginner"
}

# Complete quiz
POST /api/activities/submit
{
  "session_id": 3,
  "activity_type": "quiz",
  "user_answers": [0, 3, 2, 1, 4],  # 2 correct
  "time_spent": 90
}
```

**Expected Response:**
```json
{
  "points_earned": 16,  # 2 * 8
  "gamification": {
    "points_awarded": 16,
    "total_points": 120,  # 84 + 16 + 20 (Century bonus)
    "new_badges": [
      {
        "id": 5,
        "name": "Century",
        "description": "Earn 100 total points",
        "points_reward": 20,
        "rarity": "uncommon"
      }
    ],
    "level_up": true,  # NOW LEVEL 2!
    "new_level": 2
  }
}
```

**Verification:**

2. **Check Points:**
```bash
GET /api/gamification/points
```

**Expected:**
```json
{
  "total_points": 120,
  "level": 2  # LEVELED UP!
}
```

3. **Check Badges:**
```bash
GET /api/gamification/badges
```

**Expected:**
```json
{
  "earned_badges": [
    {
      "id": 1,
      "name": "First Steps"
    },
    {
      "id": 5,
      "name": "Century"  # NEW!
    }
  ],
  "earned_count": 2
}
```

**✅ Success Criteria:**
- Century badge unlocks at 100 points
- Badge adds 20 bonus points
- User levels up to Level 2
- level_up flag = true in response

---

### **Test 4: Flashcard Activity & Points** 🃏

**Objective:** Verify 1 point per flashcard reviewed.

**Steps:**

1. **Create Flashcard Session:**
```bash
POST /api/learning-sessions
{
  "activity_type": "flashcard",
  "difficulty": "beginner"
}
```

**Expected:** Session with 10 flashcards

2. **Complete Flashcards (10 cards):**
```bash
POST /api/activities/submit
{
  "session_id": 4,
  "activity_type": "flashcard",
  "user_answers": [
    {"card_id": 1, "correct": true},
    {"card_id": 2, "correct": true},
    {"card_id": 3, "correct": false},
    {"card_id": 4, "correct": true},
    {"card_id": 5, "correct": true},
    {"card_id": 6, "correct": false},
    {"card_id": 7, "correct": true},
    {"card_id": 8, "correct": true},
    {"card_id": 9, "correct": true},
    {"card_id": 10, "correct": false}
  ],
  "time_spent": 180
}
```

**Expected Response:**
```json
{
  "points_earned": 10,  # 10 cards * 1 point
  "gamification": {
    "points_awarded": 10,
    "total_points": 130,  # 120 + 10
    "new_badges": [],
    "level_up": false
  }
}
```

**✅ Success Criteria:**
- 1 point per flashcard (regardless of correct/incorrect)
- Total 10 points for 10 cards
- Points added to user total

---

### **Test 5: Role-Play Activity & "Conversationalist" Badge** 💬

**Objective:** Complete 10 role-plays to unlock badge.

**Steps:**

1. **Complete First Role-Play:**
```bash
# Create session
POST /api/learning-sessions
{
  "activity_type": "roleplay",
  "difficulty": "beginner"
}

# Submit conversation
POST /api/activities/roleplay/submit
{
  "session_id": 5,
  "conversation_history": [
    {"role": "user", "message": "Hello, I would like to buy vegetables."},
    {"role": "ai", "message": "నమస్కారం! Sure, what vegetables do you need?"},
    // ... 6-8 more messages
  ]
}
```

**Expected Response:**
```json
{
  "evaluation": {...},
  "points_earned": 30,
  "gamification": {
    "points_awarded": 30,
    "total_points": 160,  # 130 + 30
    "new_badges": [],
    "level_up": false
  }
}
```

2. **Repeat 9 More Times:**
```bash
# Complete role-plays 2-10
# Each awards 30 points
```

**Expected After 10th Role-Play:**
```json
{
  "points_earned": 30,
  "gamification": {
    "points_awarded": 30,
    "total_points": 505,  # 160 + (9 * 30) + 75 (badge bonus)
    "new_badges": [
      {
        "id": 7,
        "name": "Conversationalist",
        "description": "Complete 10 role-playing activities",
        "points_reward": 75
      }
    ],
    "level_up": true,
    "new_level": 4
  }
}
```

**✅ Success Criteria:**
- Each role-play awards 30 points
- After 10th completion, "Conversationalist" unlocks
- Badge adds 75 bonus points
- User reaches Level 4

---

### **Test 6: Streak System & "Hot Streak" Badge** 🔥

**Objective:** Maintain 7-day streak and unlock badge.

**Steps:**

**Day 1:**
```bash
# Complete any 1 activity
POST /api/activities/submit
{...}

# Check streak
GET /api/gamification/stats
```

**Expected:**
```json
{
  "current_streak": 1,
  "longest_streak": 1,
  "last_activity_date": "2025-01-09"
}
```

**Day 2 (Next Calendar Day):**
```bash
# Complete any 1 activity
# Streak increments
```

**Expected:**
```json
{
  "current_streak": 2,
  "longest_streak": 2
}
```

**Day 3 (Complete 3 Activities = Daily Goal):**
```bash
# Complete 1st activity
POST /api/activities/submit {...}  # +points, streak = 3

# Complete 2nd activity
POST /api/activities/submit {...}  # +points

# Complete 3rd activity
POST /api/activities/submit {...}  # +points + 25 BONUS
```

**Expected After 3rd Activity:**
```json
{
  "gamification": {
    "points_awarded": 50,  # Base activity points
    "bonus_awarded": 25,   # Daily Goal bonus!
    "total_points": 575,
    "daily_goal_met": true
  }
}
```

**Days 4-6:**
```bash
# Complete 1+ activity each day
# Streak continues: 4, 5, 6
```

**Day 7:**
```bash
# Complete 1 activity
POST /api/activities/submit {...}
```

**Expected Response:**
```json
{
  "gamification": {
    "points_awarded": 50,
    "bonus_awarded": 100,  # 7-Day Streak bonus!
    "total_points": 675,
    "new_badges": [
      {
        "id": 4,
        "name": "Hot Streak",
        "description": "Maintain a 7-day learning streak",
        "points_reward": 100
      }
    ],
    "streak_milestone_reached": true,
    "current_streak": 7
  }
}
```

**Day 8 (Skip a Day):**
```bash
# Don't complete any activity
# Wait until Day 9
```

**Day 9:**
```bash
# Complete activity
GET /api/gamification/stats
```

**Expected:**
```json
{
  "current_streak": 1,  # RESET!
  "longest_streak": 7   # Preserved
}
```

**✅ Success Criteria:**
- Streak increments daily with activity
- 3 activities in 1 day = +25 bonus
- 7 consecutive days = +100 bonus + "Hot Streak" badge
- Missing a day resets streak to 0
- Longest streak preserved

---

### **Test 7: Leaderboard System** 🏆

**Objective:** Verify user rankings and timeframe filtering.

**Steps:**

1. **Get All-Time Leaderboard:**
```bash
GET /api/gamification/leaderboard?timeframe=all_time&limit=10
Authorization: Bearer <JWT_TOKEN>
```

**Expected Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 5,
      "username": "john_doe",
      "points": 1250,
      "level": 5,
      "badge_count": 6,
      "current_streak": 12
    },
    {
      "rank": 2,
      "user_id": 12,
      "username": "jane_smith",
      "points": 890,
      "level": 4,
      "badge_count": 4,
      "current_streak": 5
    },
    // ... top 10 users
  ],
  "user_rank": 3,
  "total_users": 42,
  "timeframe": "all_time"
}
```

2. **Get Weekly Leaderboard:**
```bash
GET /api/gamification/leaderboard?timeframe=weekly&limit=10
```

**Expected:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "points": 340  # Points earned THIS WEEK only
    }
  ],
  "timeframe": "weekly"
}
```

3. **Get Monthly Leaderboard:**
```bash
GET /api/gamification/leaderboard?timeframe=monthly&limit=10
```

**✅ Success Criteria:**
- Users ranked by points (desc)
- All-time shows total_points
- Weekly shows last 7 days
- Monthly shows last 30 days
- user_rank shows current user position
- Pagination works (limit parameter)

---

### **Test 8: "Word Smith" Badge (5 Writing Activities)** ✍️

**Objective:** Complete 5 writings to unlock badge.

**Progress from Test 2:** 1/5 complete

**Steps:**

1. **Complete Writings 2-5:**
```bash
# Writing 2
POST /api/activities/submit
{
  "activity_type": "writing",
  "user_input": "I love learning English..."
}

# Writing 3
POST /api/activities/submit {...}

# Writing 4
POST /api/activities/submit {...}

# Writing 5
POST /api/activities/submit {...}
```

**Expected After 5th Writing:**
```json
{
  "points_earned": 50,
  "gamification": {
    "points_awarded": 50,
    "total_points": 925,  # Previous + 50 + 50 (badge bonus)
    "new_badges": [
      {
        "id": 3,
        "name": "Word Smith",
        "description": "Complete 5 writing activities",
        "points_reward": 50
      }
    ]
  }
}
```

**✅ Success Criteria:**
- Badge unlocks after exactly 5 writings
- 50 bonus points awarded
- Badge appears in earned_badges

---

### **Test 9: "Bookworm" Badge (10 Reading Activities)** 📚

**Objective:** Complete 10 readings to unlock badge.

**Note:** Reading activities require creating sessions with reading content (articles/passages).

**Steps:**

1. **Complete 10 Reading Sessions:**
```bash
# Loop 10 times:
POST /api/learning-sessions
{
  "activity_type": "reading",
  "difficulty": "beginner"
}

# Read content, then complete
POST /api/activities/complete-reading
{
  "session_id": X
}
```

**Expected After 10th Reading:**
```json
{
  "message": "Reading activity completed",
  "gamification": {
    "points_awarded": 20,
    "total_points": 1145,  # Previous + 20 + 50 (badge bonus)
    "new_badges": [
      {
        "id": 2,
        "name": "Bookworm",
        "description": "Complete 10 reading activities",
        "points_reward": 50
      }
    ]
  }
}
```

**✅ Success Criteria:**
- Each reading awards 20 points
- After 10th completion, "Bookworm" unlocks
- Badge adds 50 bonus points

---

### **Test 10: "Champion" Badge (1000 Points)** 🏆

**Objective:** Earn 1000+ total points to unlock ultimate badge.

**Current Progress:** ~1145 points (from all tests above)

**Expected:**
- "Champion" badge already unlocked during previous activities
- Check with GET /api/gamification/badges

**If Not Unlocked Yet:**
```bash
# Complete more activities until total_points >= 1000
# When threshold reached:
```

**Expected Response:**
```json
{
  "gamification": {
    "total_points": 1000+,
    "new_badges": [
      {
        "id": 6,
        "name": "Champion",
        "description": "Earn 1000 total points",
        "points_reward": 200,
        "rarity": "legendary"
      }
    ]
  }
}
```

**✅ Success Criteria:**
- Badge unlocks at exactly 1000 points
- 200 bonus points awarded
- Rarity = "legendary"

---

## 🎯 Complete Badge Checklist

| Badge | Requirement | Points Reward | Status |
|-------|------------|---------------|--------|
| 🎯 First Steps | 1 activity | 10 | Test 1 ✅ |
| 💯 Century | 100 points | 20 | Test 3 ✅ |
| ✍️ Word Smith | 5 writings | 50 | Test 8 ✅ |
| 📚 Bookworm | 10 readings | 50 | Test 9 ✅ |
| 💬 Conversationalist | 10 role-plays | 75 | Test 5 ✅ |
| 🔥 Hot Streak | 7-day streak | 100 | Test 6 ✅ |
| 🏆 Champion | 1000 points | 200 | Test 10 ✅ |

---

## 📊 Points Accumulation Summary

### Activity Points Earned (Example Session)

| Activity | Count | Points Each | Total |
|----------|-------|-------------|-------|
| Quiz (3/5 correct) | 1 | 24 | 24 |
| Writing | 5 | 50 | 250 |
| Flashcard (10 cards) | 1 | 10 | 10 |
| Role-Play | 10 | 30 | 300 |
| Reading | 10 | 20 | 200 |
| **Subtotal** | | | **784** |

### Badge Bonuses

| Badge | Points |
|-------|--------|
| First Steps | 10 |
| Century | 20 |
| Word Smith | 50 |
| Bookworm | 50 |
| Conversationalist | 75 |
| Hot Streak | 100 |
| Champion | 200 |
| **Subtotal** | **505** |

### Streak Bonuses

| Bonus Type | Count | Points Each | Total |
|------------|-------|-------------|-------|
| Daily Goal (3 activities) | 2 | 25 | 50 |
| 7-Day Streak | 1 | 100 | 100 |
| **Subtotal** | | | **150** |

### **Grand Total:** 784 + 505 + 150 = **1,439 Points**

---

## 🐛 Common Issues & Solutions

### Issue 1: Badge Not Unlocking
**Symptom:** Completed requirement but badge not awarded

**Debug:**
```bash
# Check user's activity count
GET /api/gamification/stats

# Check badge requirements
GET /api/gamification/badges

# Verify database
SELECT * FROM user_badge WHERE user_id = X;
```

**Solution:**
- Ensure activity_type matches requirement_metadata
- Check if badge already earned (can't earn twice)
- Verify gamification service is called in activity endpoint

### Issue 2: Streak Not Incrementing
**Symptom:** Completed activity but streak stays same

**Debug:**
```sql
SELECT last_activity_date, current_streak, longest_streak
FROM user
WHERE id = X;
```

**Solution:**
- Check server time zone (UTC)
- Verify activity marked as complete in database
- Ensure update_streak() called after activity

### Issue 3: Points Not Awarded
**Symptom:** Activity completed but points unchanged

**Debug:**
```bash
# Check response gamification object
POST /api/activities/submit
# Look for "gamification" key in response

# Check user table
SELECT total_points FROM user WHERE id = X;
```

**Solution:**
- Verify gamification_service.award_activity_points() is called
- Check activity_type matches expected values
- Ensure database transaction commits

---

## ✅ Final Verification Checklist

After completing all tests:

- [ ] All 7 badges initialized in database
- [ ] "First Steps" unlocks on first activity
- [ ] Quiz awards 8 points per correct answer
- [ ] Flashcard awards 1 point per card
- [ ] Writing awards 50 points flat
- [ ] Role-Play awards 30 points flat
- [ ] Reading awards 20 points flat
- [ ] "Century" unlocks at 100 points
- [ ] "Word Smith" unlocks after 5 writings
- [ ] "Bookworm" unlocks after 10 readings
- [ ] "Conversationalist" unlocks after 10 role-plays
- [ ] Daily goal (3 activities) awards 25 bonus points
- [ ] 7-day streak awards 100 bonus points
- [ ] "Hot Streak" unlocks after 7 consecutive days
- [ ] "Champion" unlocks at 1000 points
- [ ] Leaderboard shows correct rankings
- [ ] Leaderboard filters by timeframe (all-time/weekly/monthly)
- [ ] Missing a day resets streak to 0
- [ ] Longest streak preserved after reset
- [ ] Badge progress shown in available_badges
- [ ] Badge unlock adds bonus points
- [ ] Level increases with points (100, 300, 600, 1000)
- [ ] Gamification data returned in activity completion responses

---

**Testing Date:** January 9, 2025  
**Backend Status:** ✅ 100% Complete  
**Frontend Status:** ⚠️ 0% Complete (Components need creation)  
**Database Status:** ✅ Badges Initialized

**Next Steps:**
1. Run all test scenarios above
2. Fix any issues discovered
3. Create frontend components (PointsDisplay, BadgesGrid, Leaderboard, etc.)
4. Integrate gamification UI into activity pages
5. Add real-time notifications for badge unlocks
