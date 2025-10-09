# 🎮 Gamification System - Quick Reference

**Last Updated:** January 9, 2025  
**Status:** Backend ✅ Complete | Frontend ⚠️ Pending

---

## ⚡ Quick Start

### 1. Initialize Badges (One-Time Setup)
```bash
cd language-learning-platform
python init_badges.py
```

### 2. Test Points System
```bash
# Complete a quiz
POST /api/activities/submit
{
  "session_id": 1,
  "activity_type": "quiz",
  "user_answers": [0, 1, 2, 3, 4]
}

# Check points
GET /api/gamification/points
Authorization: Bearer <JWT_TOKEN>
```

### 3. Check Badges
```bash
GET /api/gamification/badges
Authorization: Bearer <JWT_TOKEN>
```

---

## 📊 Points Cheat Sheet

| Activity | Points | Example |
|----------|--------|---------|
| Quiz | **8** per correct | 5/10 = 40 pts |
| Flashcard | **1** per card | 10 cards = 10 pts |
| Writing | **50** flat | 50 pts |
| Role-Play | **30** flat | 30 pts |
| Reading | **20** flat | 20 pts |
| Daily Goal | **+25** bonus | 3 activities/day |
| 7-Day Streak | **+100** bonus | 7 consecutive days |

---

## 🏅 7 Badges

| Badge | Icon | Requirement | Reward | Rarity |
|-------|------|------------|--------|--------|
| First Steps | 🎯 | 1 activity | **10 pts** | Common |
| Bookworm | 📚 | 10 readings | **50 pts** | Rare |
| Word Smith | ✍️ | 5 writings | **50 pts** | Rare |
| Hot Streak | 🔥 | 7-day streak | **100 pts** | Epic |
| Century | 💯 | 100 points | **20 pts** | Uncommon |
| Champion | 🏆 | 1000 points | **200 pts** | Legendary |
| Conversationalist | 💬 | 10 role-plays | **75 pts** | Rare |

---

## 🎯 Levels

| Level | Points Required | Progress |
|-------|----------------|----------|
| 1 | 0-99 | ⭐ |
| 2 | 100-299 | ⭐⭐ |
| 3 | 300-599 | ⭐⭐⭐ |
| 4 | 600-999 | ⭐⭐⭐⭐ |
| 5 | 1000+ | ⭐⭐⭐⭐⭐ |

---

## 🔌 API Endpoints

### Points
```bash
GET /api/gamification/points
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "total_points": 340,
  "level": 3,
  "rank": 5
}
```

### Badges
```bash
GET /api/gamification/badges
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "earned_badges": [...],
  "available_badges": [...],
  "earned_count": 3
}
```

### Leaderboard
```bash
GET /api/gamification/leaderboard?timeframe=weekly&limit=10
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "leaderboard": [
    {"rank": 1, "username": "john_doe", "points": 450},
    ...
  ],
  "user_rank": 5
}
```

### Stats
```bash
GET /api/gamification/stats
Authorization: Bearer <JWT_TOKEN>

Response:
{
  "total_points": 340,
  "current_streak": 5,
  "longest_streak": 12,
  "badges_earned": 3,
  "level": 3
}
```

---

## 🎨 Frontend Components (To Create)

### 1. PointsDisplay
```jsx
<PointsDisplay 
  points={340} 
  level={3} 
  animated={true}
/>
```
**Features:** Animated counter, trophy icon, level badge

---

### 2. BadgesGrid
```jsx
<BadgesGrid 
  earnedBadges={earnedBadges}
  availableBadges={availableBadges}
  showProgress={true}
/>
```
**Features:** Grid layout, earned (color) vs locked (grayscale), progress bars

---

### 3. BadgeUnlockModal
```jsx
<BadgeUnlockModal 
  badge={badge}
  onClose={() => setShowModal(false)}
/>
```
**Features:** Confetti animation, large badge icon, points reward

---

### 4. Leaderboard
```jsx
<Leaderboard 
  timeframe="weekly"
  limit={10}
/>
```
**Features:** Timeframe tabs, top 10 users, highlight current user

---

### 5. StreakTracker
```jsx
<StreakTracker 
  currentStreak={5}
  longestStreak={12}
/>
```
**Features:** Fire icon, current/longest streak, progress bar

---

## 🔥 Streak System

### How It Works
- Complete 1+ activity per day → Streak increments
- Skip a day → Streak resets to 0
- Longest streak is preserved

### Bonuses
- **3 activities in one day** = +25 points (Daily Goal)
- **7 consecutive days** = +100 points + "Hot Streak" badge

---

## 🧪 Quick Test Scenarios

### Test 1: First Activity
```bash
# Complete quiz
POST /api/activities/submit {...}

# Expected: 
# - Points awarded (8 per correct)
# - "First Steps" badge unlocked (+10 bonus)
```

### Test 2: Badge Unlock
```bash
# Complete 5 writings
# Expected: "Word Smith" badge unlocked (+50 bonus)

# Earn 100 points
# Expected: "Century" badge unlocked (+20 bonus)
```

### Test 3: Streak
```bash
# Day 1: Complete 1 activity → streak = 1
# Day 2: Complete 1 activity → streak = 2
# Day 3: Complete 3 activities → streak = 3 + 25 bonus
# Day 7: Complete 1 activity → streak = 7 + 100 bonus + "Hot Streak"
```

---

## 📁 Key Files

### Backend
- `app/models/gamification.py` - Badge, UserBadge, Achievement models
- `app/services/gamification_service.py` - Points & badge logic
- `app/api/gamification_routes.py` - API endpoints
- `init_badges.py` - Badge initialization script

### Frontend (To Create)
- `src/components/gamification/PointsDisplay.jsx`
- `src/components/gamification/BadgesGrid.jsx`
- `src/components/gamification/BadgeUnlockModal.jsx`
- `src/components/gamification/Leaderboard.jsx`
- `src/components/gamification/StreakTracker.jsx`

---

## ✅ Checklist

### Setup
- [ ] Run `python init_badges.py` ✅
- [ ] Verify 7 badges in database ✅
- [ ] Backend server running ✅
- [ ] Frontend server running ⚠️

### Testing
- [ ] Complete quiz → Points awarded
- [ ] "First Steps" badge unlocks
- [ ] Complete 5 writings → "Word Smith"
- [ ] Earn 100 points → "Century"
- [ ] 7-day streak → "Hot Streak"
- [ ] Leaderboard shows rankings

### Frontend
- [ ] Create PointsDisplay component
- [ ] Create BadgesGrid component
- [ ] Create BadgeUnlockModal component
- [ ] Create Leaderboard component
- [ ] Create StreakTracker component
- [ ] Integrate into activity pages

---

## 📚 Full Documentation

- **GAMIFICATION_IMPLEMENTATION_GUIDE.md** - Complete technical guide
- **GAMIFICATION_TESTING_GUIDE.md** - 10 test scenarios
- **GAMIFICATION_COMPLETE_SUMMARY.md** - Full implementation summary

---

## 🎯 Sample User Journey

| Step | Activity | Points | Total | Badge |
|------|----------|--------|-------|-------|
| 1 | Quiz (3/5) | 24 | **34** | First Steps (+10) |
| 2 | Writing | 50 | **84** | - |
| 3 | Quiz (2/5) | 16 | **120** | Century (+20) |
| 4 | Flashcard (10) | 10 | **130** | - |
| 5 | 5 Writings | 250 | **430** | Word Smith (+50) |
| 6 | 10 Role-Plays | 300 | **805** | Conversationalist (+75) |
| 7 | 10 Readings | 200 | **1055** | Bookworm (+50) |
| 8 | 7-Day Streak | 100 | **1255** | Hot Streak (+100), Champion (+200) |

**Final:** 1,255 points, Level 5, 7/7 badges 🏆

---

**Ready to test?** Run `python init_badges.py` and start completing activities!

---

**Need Help?**
- Backend issues → Check `GAMIFICATION_TESTING_GUIDE.md`
- Frontend components → Check `GAMIFICATION_IMPLEMENTATION_GUIDE.md`
- API examples → Check `GAMIFICATION_COMPLETE_SUMMARY.md`
