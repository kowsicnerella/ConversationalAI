"""
Initialize Gamification Badges

This script creates the 7 specific badges for the gamification system:
1. First Steps - Complete first activity
2. Bookworm - Complete 10 reading activities
3. Word Smith - Complete 5 writing activities
4. Hot Streak - Maintain 7-day streak
5. Century - Earn 100 points
6. Champion - Earn 1000 points
7. Conversationalist - Complete 10 role-playing activities
"""

from app import create_app, db
from app.models.gamification import Badge


def init_badges():
    """Initialize all gamification badges"""
    app = create_app()

    with app.app_context():
        # Check if badges already exist
        existing_count = Badge.query.count()
        if existing_count > 0:
            print(f"⚠️ Found {existing_count} existing badges. Clearing...")
            Badge.query.delete()
            db.session.commit()

        badges = [
            {
                "name": "First Steps",
                "description": "Complete your first activity",
                "category": "beginner",
                "requirement_type": "activities_completed",
                "requirement_value": 1,
                "points_reward": 10,
                "rarity": "common",
                "icon_url": "🎯",
            },
            {
                "name": "Bookworm",
                "description": "Complete 10 reading activities",
                "category": "reading",
                "requirement_type": "reading_completed",
                "requirement_value": 10,
                "points_reward": 50,
                "rarity": "rare",
                "icon_url": "📚",
            },
            {
                "name": "Word Smith",
                "description": "Complete 5 writing activities",
                "category": "writing",
                "requirement_type": "writing_completed",
                "requirement_value": 5,
                "points_reward": 50,
                "rarity": "rare",
                "icon_url": "✍️",
            },
            {
                "name": "Hot Streak",
                "description": "Maintain a 7-day learning streak",
                "category": "consistency",
                "requirement_type": "streak_days",
                "requirement_value": 7,
                "points_reward": 100,
                "rarity": "epic",
                "icon_url": "🔥",
            },
            {
                "name": "Century",
                "description": "Earn 100 total points",
                "category": "points",
                "requirement_type": "points_earned",
                "requirement_value": 100,
                "points_reward": 20,
                "rarity": "uncommon",
                "icon_url": "💯",
            },
            {
                "name": "Champion",
                "description": "Earn 1000 total points",
                "category": "points",
                "requirement_type": "points_earned",
                "requirement_value": 1000,
                "points_reward": 200,
                "rarity": "legendary",
                "icon_url": "🏆",
            },
            {
                "name": "Conversationalist",
                "description": "Complete 10 role-playing activities",
                "category": "speaking",
                "requirement_type": "roleplay_completed",
                "requirement_value": 10,
                "points_reward": 75,
                "rarity": "rare",
                "icon_url": "💬",
            },
        ]

        print("🎮 Initializing Gamification Badges...")
        print("=" * 50)

        for badge_data in badges:
            badge = Badge(**badge_data)
            db.session.add(badge)
            print(f"✅ Created badge: {badge_data['name']} ({badge_data['rarity']})")
            print(f"   {badge_data['description']}")
            print(
                f"   Requirement: {badge_data['requirement_type']} = {badge_data['requirement_value']}"
            )
            print(f"   Reward: {badge_data['points_reward']} points")
            print()

        db.session.commit()

        print("=" * 50)
        print(f"✅ Successfully initialized {len(badges)} badges!")
        print("\nBadge Summary:")
        print(f"   🎯 Beginner: 1 badge")
        print(f"   📚 Reading: 1 badge")
        print(f"   ✍️  Writing: 1 badge")
        print(f"   💬 Speaking: 1 badge")
        print(f"   🔥 Consistency: 1 badge")
        print(f"   💯 Points: 2 badges")


if __name__ == "__main__":
    init_badges()
