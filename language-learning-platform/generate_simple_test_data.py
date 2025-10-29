#!/usr/bin/env python3
"""
Simple Test Data Generator for Phase 9 Gamification System
Focuses on challenges, achievements, and user data
"""

from app import create_app, db
from app.models.user import User
from app.models.gamification_enhanced import (
    GamificationChallenge,
    GamificationAchievement,
    UserAchievement,
    LeaderboardEntry,
    GamificationStreak,
)
from datetime import datetime, timedelta, date
import random

app = create_app()
ctx = app.app_context()
ctx.push()

print("=" * 60)
print("Phase 9 Simple Test Data Generator")
print("=" * 60)
print()

# Step 1: Create/Get Test Users
print("Step 1: Getting Test Users...")
users = []

for i in range(1, 6):
    if i == 1:
        username = "testuser"
    else:
        username = f"testuser{i}"
    
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"  ✓ {username} (ID: {user.id})")
        users.append(user)
    else:
        user = User(email=f"{username}@example.com", username=username)
        user.set_password("test123")
        db.session.add(user)
        db.session.commit()
        print(f"  ✓ Created {username} (ID: {user.id})")
        users.append(user)

print()

# Step 2: Create Daily Challenges
print("Step 2: Creating Daily Challenges...")
challenge_types = ["vocabulary", "grammar", "listening", "speaking", "reading"]
difficulty_levels = ["beginner", "intermediate", "advanced"]
target_metrics = ["complete_5_activities", "earn_100_points", "study_30_minutes"]

existing = GamificationChallenge.query.count()
print(f"  Existing: {existing}")

if existing == 0:
    count = 0
    for day_offset in range(5):
        for ctype in challenge_types:
            for user in users:
                challenge = GamificationChallenge(
                    user_id=user.id,
                    challenge_date=date.today() - timedelta(days=day_offset),
                    challenge_type=ctype,
                    difficulty_level=random.choice(difficulty_levels),
                    title=f"{ctype.title()} Challenge",
                    description=f"Complete this {ctype} challenge to earn points",
                    target_metric=random.choice(target_metrics),
                    target_value=random.randint(5, 20),
                    points_reward=random.randint(10, 50),
                    expires_at=datetime.utcnow() + timedelta(hours=24),
                    skill_focus={"area": ctype},
                    weak_areas_targeted={}
                )
                db.session.add(challenge)
                count += 1
    
    db.session.commit()
    print(f"  ✓ Created {count} challenges")
else:
    print(f"  ✓ Challenges already exist")

print()

# Step 3: Unlock Achievements (skip - no achievements in database yet)
print("Step 3: Achievements...")
achievements_count = GamificationAchievement.query.count()
if achievements_count == 0:
    print("  ℹ No achievements in database (run seed_achievements.py first)")
else:
    print(f"  ℹ Found {achievements_count} achievements")

print()

# Step 4: Create Leaderboard Entries
print("Step 4: Creating Leaderboard Entries...")
existing_lb = LeaderboardEntry.query.count()

if existing_lb == 0:
    count = 0
    categories = ["overall", "activities", "badges", "vocabulary"]
    periods = ["daily", "weekly", "monthly", "all_time"]
    
    for user in users:
        for cat in categories[:2]:
            for period in periods[:2]:
                entry = LeaderboardEntry(
                    user_id=user.id,
                    category=cat,
                    time_period=period,
                    points=random.randint(50, 500),
                    rank=random.randint(1, len(users)),
                    last_updated=datetime.utcnow()
                )
                db.session.add(entry)
                count += 1
    
    db.session.commit()
    print(f"  ✓ Created {count} leaderboard entries")
else:
    print(f"  ✓ Leaderboard entries already exist ({existing_lb})")

print()

# Step 5: Create/Update Streaks
print("Step 5: Creating Learning Streaks...")
existing_streaks = GamificationStreak.query.count()

if existing_streaks < len(users):
    for user in users:
        streak = GamificationStreak.query.filter_by(user_id=user.id).first()
        if not streak:
            streak = GamificationStreak(
                user_id=user.id,
                current_streak=random.randint(1, 30),
                longest_streak=random.randint(5, 50),
                freeze_count=random.randint(0, 2),
                status="active",
                last_activity_date=datetime.utcnow() - timedelta(days=random.randint(0, 2))
            )
            db.session.add(streak)
    
    db.session.commit()
    print(f"  ✓ Created/updated {len(users)} streak records")
else:
    print(f"  ✓ Streaks already exist ({existing_streaks})")

print()

# Step 6: Summary
print("=" * 60)
print("Summary")
print("=" * 60)

print(f"✓ Users: {User.query.count()}")
print(f"✓ Challenges: {GamificationChallenge.query.count()}")
print(f"✓ Achievement Unlocks: {UserAchievement.query.count()}")
print(f"✓ Leaderboard Entries: {LeaderboardEntry.query.count()}")
print(f"✓ Streaks: {GamificationStreak.query.count()}")

print()
print("✅ Test Data Generation Complete!")
print("=" * 60)
