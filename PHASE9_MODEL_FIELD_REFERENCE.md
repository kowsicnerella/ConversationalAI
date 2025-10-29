# Phase 9 Gamification Models - Complete Field Reference

## Quick Reference for Model Fields

### GamificationChallenge
```python
# Required Fields
user_id          # Foreign key to users.id
challenge_date   # Date of challenge (auto: today)
challenge_type   # String: vocabulary, grammar, listening, speaking, reading
difficulty_level # String: beginner, intermediate, advanced
title            # String (200 chars)
description      # Text
target_metric    # String: complete_5_activities, earn_100_points, study_30_minutes
target_value     # Integer
points_reward    # Integer
expires_at       # DateTime

# Optional Fields
current_progress         # Integer (default: 0)
bonus_multiplier        # Float (default: 1.0)
badge_reward           # String
is_completed           # Boolean (default: False)
completed_at           # DateTime
is_streak_bonus        # Boolean (default: False)
skill_focus            # JSON object
weak_areas_targeted    # JSON object

# Unique Constraint: (user_id, challenge_date, challenge_type)
# This means each user can have max 1 challenge per type per date
```

### GamificationAchievement
```python
# Required Fields
achievement_key   # String, unique (100 chars) - Primary identifier
category         # String: skill, milestone, streak, social, special
title            # String (200 chars)
description      # Text
unlock_criteria  # JSON - Conditions to unlock

# Optional Fields
subcategory      # String (50 chars)
icon            # String (emoji/icon name)
badge_image     # String (path to image)
rarity          # String: common, uncommon, rare, epic, legendary, secret (default: common)
points_value    # Integer (default: 0)
is_secret       # Boolean (default: False)
is_repeatable   # Boolean (default: False)
prerequisite_achievement # String (achievement_key)
is_active       # Boolean (default: True)
```

### UserAchievement
```python
# Required Fields
user_id         # Foreign key to users.id
achievement_id  # Foreign key to achievements.id
unlocked_at     # DateTime (auto: utcnow)

# Optional Fields
progress_when_unlocked  # JSON - snapshot of user progress
unlock_count           # Integer (default: 1) - for repeatable achievements
last_unlock_at        # DateTime (auto: utcnow)
is_showcased          # Boolean (default: False) - NOT 'showcase'
is_notified          # Boolean (default: False)

# Unique Constraint: (user_id, achievement_id)
# Indexes: idx_user_achievement, idx_user_showcased
```

### LeaderboardEntry
```python
# Required Fields
user_id      # Foreign key to users.id
category     # String: overall, vocabulary, grammar, reading, etc.
time_period  # String: daily, weekly, monthly, all_time
period_start # Date
period_end   # Date
score        # Integer - NOT 'points'

# Optional Fields
rank               # Integer - current rank
previous_rank      # Integer - rank from previous period
activities_completed # Integer (default: 0)
study_time_minutes # Integer (default: 0)
accuracy_percentage # Float (default: 0.0)
streak_days        # Integer (default: 0)
updated_at        # DateTime (auto: utcnow)
```

### GamificationStreak
```python
# Required Fields (implicitly)
user_id # Foreign key to users.id (unique)

# Streak Tracking
current_streak      # Integer (default: 0)
last_activity_date  # Date
streak_start_date   # Date
longest_streak      # Integer (default: 0)
longest_streak_start # Date
longest_streak_end  # Date

# Freezes (allow missing days without breaking)
freeze_count        # Integer (default: 0) - Available freezes - NOT 'status'
max_freezes        # Integer (default: 2) - Max freezes user can have
freezes_used       # Integer (default: 0) - Total ever used
last_freeze_earned # Date

# Recovery
is_recovery_available        # Boolean (default: False)
recovery_challenge_completed # Boolean (default: False)
recovery_expires_at         # DateTime

# Milestones
milestone_7_reached   # Boolean (default: False)
milestone_30_reached  # Boolean (default: False)
milestone_100_reached # Boolean (default: False)
milestone_365_reached # Boolean (default: False)

# Metadata
created_at # DateTime (auto: utcnow)
updated_at # DateTime (auto: utcnow)
```

### ProgressMilestone
```python
# Fields
user_id          # Foreign key to users.id
milestone_type   # String: streak_7, streak_30, points_100, etc.
milestone_name   # String
milestone_value  # Integer
is_reached      # Boolean
reached_at      # DateTime
```

### SocialConnection
```python
# Fields
user_id          # Foreign key to users.id
friend_id        # Foreign key to users.id
status           # String: pending, accepted, blocked
created_at       # DateTime
```

### SharedAchievement
```python
# Fields
user_id         # Foreign key to users.id
achievement_id  # Foreign key to achievements.id
achievement     # Relationship reference
shared_at       # DateTime
```

## Common Issues & Fixes

### ❌ WRONG → ✅ CORRECT

| Issue | Wrong | Correct | Model |
|-------|-------|---------|-------|
| Difficulty field | `difficulty` | `difficulty_level` | GamificationChallenge |
| Showcase flag | `showcase` | `is_showcased` | UserAchievement |
| Points in leaderboard | `points` | `score` | LeaderboardEntry |
| Streak status | `status="active"` | (use boolean fields) | GamificationStreak |
| Category in challenge | `category` | `challenge_type` | GamificationChallenge |
| Time limit field | `time_limit_minutes` | `target_metric` + `target_value` | GamificationChallenge |

## Database Constraints

### Unique Constraints
- `GamificationChallenge`: `(user_id, challenge_date, challenge_type)` - IMPORTANT!
- `UserAchievement`: `(user_id, achievement_id)`
- `GamificationStreak`: `(user_id)` - only one streak per user

### Foreign Key Constraints
- All models use `ForeignKey('users.id')` for user references
- `UserAchievement` uses `ForeignKey('achievements.id')` for achievements

### Indexes
- `GamificationChallenge`: `(user_id, challenge_date)`, `(challenge_type, difficulty_level)`
- `UserAchievement`: `(user_id, achievement_id)`, `(user_id, is_showcased)`
- `LeaderboardEntry`: `(user_id, category, time_period)`

## Test Data Generation Best Practices

1. **Always check model definition first** before creating test data
2. **Respect unique constraints** - distribute data across different values
3. **Use correct field names** - refer to this guide
4. **Commit after bulk inserts** - batches of 50-100 records
5. **Verify foreign keys** - check referenced records exist
6. **Use JSON for complex fields** - skill_focus, weak_areas_targeted, unlock_criteria
7. **Set timestamps correctly** - use `datetime.utcnow()` for DateTime fields

## Working Test Data Scripts

### For Challenges Only
```python
challenge = GamificationChallenge(
    user_id=user.id,
    challenge_date=date.today() - timedelta(days=offset),
    challenge_type="vocabulary",  # Not category!
    difficulty_level="beginner",  # Not difficulty!
    title="Vocabulary Challenge",
    description="Learn new words",
    target_metric="complete_5_activities",
    target_value=5,
    points_reward=25,
    expires_at=datetime.utcnow() + timedelta(hours=24),
    skill_focus={"area": "vocabulary"},
    weak_areas_targeted={}
)
db.session.add(challenge)
```

### For Streaks
```python
streak = GamificationStreak(
    user_id=user.id,
    current_streak=5,
    longest_streak=10,
    freeze_count=2,
    last_activity_date=date.today()
    # DON'T use: status="active"
)
db.session.add(streak)
```

### For Achievement Unlocks
```python
unlock = UserAchievement(
    user_id=user.id,
    achievement_id=achievement.id,
    unlocked_at=datetime.utcnow(),
    is_showcased=True  # Not showcase!
)
db.session.add(unlock)
```

## Gotchas & Workarounds

1. **GamificationChallenge Unique Constraint**
   - Can't create 2 challenges for same user on same day with same type
   - Workaround: Vary dates, types, or users

2. **Default Values**
   - Many fields have database defaults, don't force them in Python
   - Let SQLAlchemy handle auto-timestamps

3. **JSON Fields**
   - skill_focus, weak_areas_targeted, unlock_criteria are JSON
   - Pass Python dicts, SQLAlchemy converts automatically

4. **Foreign Keys**
   - Always use users.id, NOT user.id
   - Always use achievements.id, NOT achievement.id

5. **Deprecation Warning**
   - `datetime.utcnow()` is deprecated
   - Use: `datetime.now(datetime.UTC)` in Python 3.11+
   - But codebase currently uses utcnow() - OK for now

## Environment

- **Python**: 3.12
- **SQLAlchemy**: 2.x (uses new query API)
- **Database**: PostgreSQL
- **ORM**: Flask-SQLAlchemy

## Reference Files

- Model definitions: `app/models/gamification_enhanced.py`
- Test data generator: `generate_test_data_v2.py` (working version)
- Seed script: `seed_achievements.py` (50 achievements)
- API routes: `app/routes/gamification_routes.py`
- Services: `app/services/gamification_service.py`
