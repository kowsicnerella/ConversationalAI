#!/usr/bin/env python3
from app import create_app, db
from app.models.gamification_enhanced import GamificationChallenge, GamificationStreak

app = create_app()
ctx = app.app_context()
ctx.push()

print(f'Challenges: {GamificationChallenge.query.count()}')
print(f'Streaks: {GamificationStreak.query.count()}')

# Sample challenges
challs = GamificationChallenge.query.limit(2).all()
if challs:
    for c in challs:
        print(f'  - {c.title}')

# Sample streaks
streaks = GamificationStreak.query.limit(2).all()
if streaks:
    for s in streaks:
        print(f'  - Streak: {s.current_streak} days')
