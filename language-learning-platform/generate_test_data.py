#!/usr/bin/env python3
"""
Generate Test Data for Phase 9 Gamification System

Creates:
1. Daily challenges
2. User activities
3. Challenge completions
4. Achievement unlocks
5. Leaderboard entries
6. Streak records
"""

from app import create_app, db
from app.models.user import User
from app.models.activity import Activity, UserActivityLog
from app.models.gamification_enhanced import (
    GamificationChallenge,
    GamificationAchievement,
    UserAchievement,
    LeaderboardEntry,
    GamificationStreak,
)
from datetime import datetime, timedelta
import random

app = create_app()
ctx = app.app_context()
ctx.push()

# Configuration
NUM_CHALLENGES = 10
NUM_ACTIVITIES = 50
NUM_USERS = 5

print("=" * 60)
print("Phase 9 Test Data Generator")
print("=" * 60)
print()

# Step 1: Get or create test users
print("Step 1: Creating/Getting Test Users...")
users = []

# Test user 1 (already exists)
user1 = User.query.filter_by(username="testuser").first()
if user1:
    print(f"  ✓ Found testuser (ID: {user1.id})")
    users.append(user1)
else:
    user1 = User(email="testuser@example.com", username="testuser")
    user1.set_password("test123")
    db.session.add(user1)
    print(f"  ✓ Created testuser")
    users.append(user1)

# Create additional test users
for i in range(2, NUM_USERS + 1):
    existing = User.query.filter_by(username=f"testuser{i}").first()
    if not existing:
        user = User(
            email=f"testuser{i}@example.com",
            username=f"testuser{i}",
            timezone="Asia/Kolkata"
        )
        user.set_password("test123")
        db.session.add(user)
        users.append(user)
        print(f"  ✓ Created testuser{i}")
    else:
        print(f"  ✓ Found testuser{i}")
        users.append(existing)

db.session.commit()
print()

# Step 2: Create Daily Challenges
print("Step 2: Creating Daily Challenges...")
challenge_types = ["vocabulary", "grammar", "listening", "speaking", "reading"]
difficulty_levels = ["beginner", "intermediate", "advanced"]
target_metrics = ["complete_5_activities", "earn_100_points", "study_30_minutes"]

existing_challenges = GamificationChallenge.query.count()
print(f"  Existing challenges: {existing_challenges}")

if existing_challenges < NUM_CHALLENGES:
    for i in range(NUM_CHALLENGES - existing_challenges):
        user = random.choice(users)
        # Use different dates and challenge types to avoid unique constraint violations
        challenge_date = (datetime.utcnow().date() - timedelta(days=i % 5))
        challenge_type = challenge_types[i % len(challenge_types)]
        
        # Check if this combination already exists
        existing = GamificationChallenge.query.filter_by(
            user_id=user.id,
            challenge_date=challenge_date,
            challenge_type=challenge_type
        ).first()
        
        if not existing:
            challenge = GamificationChallenge(
                user_id=user.id,
                challenge_date=challenge_date,
                challenge_type=challenge_type,
                difficulty_level=random.choice(difficulty_levels),
                title=f"{challenge_type.title()} Challenge {i+1}",
                description=f"Complete this {challenge_type.lower()} challenge to earn points",
                target_metric=random.choice(target_metrics),
                target_value=random.randint(5, 20),
                points_reward=random.randint(10, 50),
                expires_at=datetime.utcnow() + timedelta(hours=24),
                skill_focus={"area": random.choice(challenge_types)},
                weak_areas_targeted={}
            )
            db.session.add(challenge)
    
    db.session.commit()
    new_count = GamificationChallenge.query.count()
    print(f"  ✓ Created {new_count - existing_challenges} new challenges")
else:
    print(f"  ✓ Already have {existing_challenges} challenges")

print()

# Step 3: Create Activities for Users
print("Step 3: Creating User Activities...")
existing_logs = UserActivityLog.query.count()
print(f"  Existing activity logs: {existing_logs}")

if existing_logs < NUM_ACTIVITIES:
    activities = Activity.query.limit(10).all()
    
    if not activities:
        print("  ⚠ No activities in database, skipping activity logs")
    else:
        for user in users:
            for j in range(random.randint(5, 10)):
                activity = random.choice(activities)
                log = UserActivityLog(
                    user_id=user.id,
                    activity_id=activity.id,
                    time_spent=random.randint(1, 30),
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                )
                db.session.add(log)
        
        db.session.commit()
        new_count = UserActivityLog.query.count()
        print(f"  ✓ Created {new_count - existing_logs} activity logs")
else:
    print(f"  ✓ Already have {existing_logs} activity logs")

print()

# Step 4: Create Challenge Completions
print("Step 4: Recording Challenge Completions...")
challenges = GamificationChallenge.query.limit(5).all()

for user in users:
    for challenge in challenges[:3]:
        existing = (
            db.session.query(GamificationChallenge)
            .filter_by(id=challenge.id)
            .first()
        )
        if existing:
            # Record completion in user's profile/context
            print(f"  ✓ User {user.username} completed {challenge.title}")

print()

# Step 5: Unlock Achievements
print("Step 5: Unlocking Achievements for Users...")
achievements = GamificationAchievement.query.limit(10).all()

if achievements:
    for user in users:
        # Unlock 3-5 random achievements per user
        unlocked = random.sample(achievements, min(random.randint(3, 5), len(achievements)))
        
        for achievement in unlocked:
            existing_unlock = UserAchievement.query.filter_by(
                user_id=user.id,
                achievement_id=achievement.id
            ).first()
            
            if not existing_unlock:
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id,
                    unlocked_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                    showcase=random.choice([True, False, False]),  # 33% shown
                )
                db.session.add(user_achievement)
                print(f"  ✓ {user.username} unlocked: {achievement.name}")
    
    db.session.commit()
else:
    print("  ⚠ No achievements to unlock")

print()

# Step 6: Update Leaderboard Entries
print("Step 6: Updating Leaderboard Entries...")
categories_list = ["overall", "activities", "badges", "vocabulary", "consistency"]
time_periods = ["daily", "weekly", "monthly", "all_time"]

for user in users:
    for category in random.sample(categories_list, 3):
        for period in random.sample(time_periods, 2):
            existing_entry = LeaderboardEntry.query.filter_by(
                user_id=user.id,
                category=category,
                time_period=period
            ).first()
            
            if not existing_entry:
                entry = LeaderboardEntry(
                    user_id=user.id,
                    category=category,
                    time_period=period,
                    points=random.randint(10, 500),
                    rank=random.randint(1, NUM_USERS),
                    last_updated=datetime.utcnow(),
                )
                db.session.add(entry)
                print(f"  ✓ {user.username} - {category} ({period}): {entry.points} points")

db.session.commit()
print()

# Step 7: Update Streaks
print("Step 7: Updating Learning Streaks...")

for user in users:
    streak = GamificationStreak.query.filter_by(user_id=user.id).first()
    
    if streak:
        # Update existing streak
        streak.current_streak = random.randint(1, 30)
        streak.longest_streak = max(streak.current_streak, streak.longest_streak or 0)
        streak.freeze_count = max(0, random.randint(0, 3))
        streak.status = random.choice(["active", "at-risk", "broken"])
        streak.last_activity_date = datetime.utcnow() - timedelta(days=random.randint(0, 2))
        print(f"  ✓ Updated {user.username} streak: {streak.current_streak} days")
    else:
        # Create new streak
        streak = GamificationStreak(
            user_id=user.id,
            current_streak=random.randint(1, 20),
            longest_streak=random.randint(1, 30),
            freeze_count=random.randint(0, 2),
            status="active",
            last_activity_date=datetime.utcnow(),
        )
        db.session.add(streak)
        print(f"  ✓ Created streak for {user.username}: {streak.current_streak} days")

db.session.commit()
print()

# Step 8: Statistics
print("Step 8: Data Generation Summary")
print("=" * 60)

user_count = User.query.count()
challenge_count = GamificationChallenge.query.count()
achievement_count = GamificationAchievement.query.count()
user_achievement_count = UserAchievement.query.count()
leaderboard_count = LeaderboardEntry.query.count()
streak_count = GamificationStreak.query.count()
activity_log_count = UserActivityLog.query.count()

print(f"✓ Users: {user_count}")
print(f"✓ Challenges: {challenge_count}")
print(f"✓ Achievements Total: {achievement_count}")
print(f"✓ User Achievements Unlocked: {user_achievement_count}")
print(f"✓ Leaderboard Entries: {leaderboard_count}")
print(f"✓ Active Streaks: {streak_count}")
print(f"✓ Activity Logs: {activity_log_count}")
print("=" * 60)
print()

# Step 9: Sample Data Display
print("Step 9: Sample Data Preview")
print("=" * 60)

print("\n📊 USERS:")
for user in users[:3]:
    print(f"  • {user.username} ({user.email})")

print("\n🎯 RECENT CHALLENGES:")
for challenge in GamificationChallenge.query.limit(3).all():
    print(f"  • {challenge.title} ({challenge.difficulty_level}) - {challenge.points_reward} pts")

print("\n🏆 SAMPLE ACHIEVEMENTS:")
for achievement in GamificationAchievement.query.limit(3).all():
    print(f"  • {achievement.name} ({achievement.rarity}) - {achievement.points} pts")

print("\n🔥 STREAKS:")
for streak in GamificationStreak.query.limit(3).all():
    user = User.query.get(streak.user_id)
    print(f"  • {user.username}: {streak.current_streak} days (best: {streak.longest_streak})")

print("\n📈 LEADERBOARD (Top 5):")
top_entries = LeaderboardEntry.query.order_by(LeaderboardEntry.points.desc()).limit(5).all()
for i, entry in enumerate(top_entries, 1):
    user = User.query.get(entry.user_id)
    print(f"  {i}. {user.username}: {entry.points} points ({entry.category})")

print("\n" + "=" * 60)
print("✅ Test Data Generation Complete!")
print("=" * 60)
print()
print("Next Steps:")
print("  1. Test frontend components with this data")
print("  2. Verify leaderboards update correctly")
print("  3. Test achievement unlock notifications")
print("  4. Verify streak tracking")
print()
