#!/usr/bin/env python3
"""
Database initialization script for the Telugu-English Learning Platform
"""

import os
from app import create_app, db
from app.models import User, Profile, Badge, Achievement

def init_database():
    """Initialize the database with tables and default data"""
    
    app = create_app('development')
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create default badges
        default_badges = [
            {
                'name': 'First Steps',
                'description': 'Complete your first activity',
                'category': 'milestone',
                'requirement_type': 'activities_completed',
                'requirement_value': 1,
                'points_reward': 25,
                'rarity': 'common'
            },
            {
                'name': 'Quiz Master',
                'description': 'Complete 10 quizzes',
                'category': 'skill',
                'requirement_type': 'quiz_completed',
                'requirement_value': 10,
                'points_reward': 100,
                'rarity': 'rare'
            },
            {
                'name': 'Week Warrior',
                'description': 'Maintain a 7-day streak',
                'category': 'streak',
                'requirement_type': 'streak_days',
                'requirement_value': 7,
                'points_reward': 150,
                'rarity': 'epic'
            },
            {
                'name': 'English Explorer',
                'description': 'Complete 50 activities',
                'category': 'milestone',
                'requirement_type': 'activities_completed',
                'requirement_value': 50,
                'points_reward': 500,
                'rarity': 'legendary'
            }
        ]
        
        for badge_data in default_badges:
            existing_badge = Badge.query.filter_by(name=badge_data['name']).first()
            if not existing_badge:
                badge = Badge(**badge_data)
                db.session.add(badge)
                print(f"Created badge: {badge_data['name']}")
        
        # Create default achievements
        default_achievements = [
            {
                'name': 'Daily Learner',
                'description': 'Complete 1 activity today',
                'achievement_type': 'daily',
                'target_value': 1,
                'points_reward': 10
            },
            {
                'name': 'Weekly Champion',
                'description': 'Complete 7 activities this week',
                'achievement_type': 'weekly',
                'target_value': 7,
                'points_reward': 50
            }
        ]
        
        for achievement_data in default_achievements:
            existing_achievement = Achievement.query.filter_by(name=achievement_data['name']).first()
            if not existing_achievement:
                achievement = Achievement(**achievement_data)
                db.session.add(achievement)
                print(f"Created achievement: {achievement_data['name']}")
        
        # Commit all changes
        db.session.commit()
        print("Database initialization completed successfully!")

if __name__ == "__main__":
    init_database()