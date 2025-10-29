#!/usr/bin/env python3
"""
Minimal Test Data Generator for Phase 9 - Just Challenges and Streaks
"""

from app import create_app, db
from app.models.user import User
from app.models.gamification_enhanced import GamificationChallenge, GamificationStreak
from datetime import datetime, timedelta, date
import random

app = create_app()
ctx = app.app_context()
ctx.push()

print("=" * 60)
print("Phase 9 Test Data Generator - Challenges & Streaks")
print("=" * 60)
print()

# Step 1: Get Test Users
print("Step 1: Getting Test Users...")
users = []
for i in range(1, 6):
    username = "testuser" if i == 1 else f"testuser{i}"
    user = User.query.filter_by(username=username).first()
    if user:
        print(f"  ✓ {username} (ID: {user.id})")
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

# Step 3: Create/Update Streaks
print("Step 3: Creating Learning Streaks...")
for user in users:
    streak = GamificationStreak.query.filter_by(user_id=user.id).first()
    if not streak:
        streak = GamificationStreak(
            user_id=user.id,
            current_streak=random.randint(1, 30),
            longest_streak=random.randint(5, 50),
            freeze_count=random.randint(0, 2),
            last_activity_date=date.today() - timedelta(days=random.randint(0, 2))
        )
        db.session.add(streak)
        print(f"  ✓ Created streak for {user.username}")

db.session.commit()
print()

# Step 4: Summary
print("=" * 60)
print("✅ Test Data Ready!")
print("=" * 60)
print(f"✓ Users: {len(users)}")
print(f"✓ Challenges: {GamificationChallenge.query.count()}")
print(f"✓ Streaks: {GamificationStreak.query.count()}")
print("=" * 60)
