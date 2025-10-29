"""
Seed 50+ Achievements for Gamification System
Run this script to populate the Achievement table with comprehensive achievements
"""

from app import create_app, db
from app.models.gamification_enhanced import GamificationAchievement

app = create_app()

# Achievement definitions
ACHIEVEMENTS = [
    # ============================================================================
    # ACTIVITY MILESTONES (8 achievements)
    # ============================================================================
    {
        'achievement_key': 'first_activity',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '🎯 First Steps',
        'description': 'Complete your first learning activity',
        'icon': '🎯',
        'unlock_criteria': {'type': 'activity_count', 'value': 1},
        'rarity': 'common',
        'points_value': 10,
        'is_secret': False
    },
    {
        'achievement_key': 'activity_10',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '🌟 Getting Started',
        'description': 'Complete 10 activities',
        'icon': '🌟',
        'unlock_criteria': {'type': 'activity_count', 'value': 10},
        'rarity': 'common',
        'points_value': 25,
        'is_secret': False
    },
    {
        'achievement_key': 'activity_50',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '💪 Dedicated Learner',
        'description': 'Complete 50 activities',
        'icon': '💪',
        'unlock_criteria': {'type': 'activity_count', 'value': 50},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'activity_100',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '🏅 Century Club',
        'description': 'Complete 100 activities',
        'icon': '🏅',
        'unlock_criteria': {'type': 'activity_count', 'value': 100},
        'rarity': 'rare',
        'points_value': 100,
        'is_secret': False
    },
    {
        'achievement_key': 'activity_500',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '⭐ Elite Achiever',
        'description': 'Complete 500 activities',
        'icon': '⭐',
        'unlock_criteria': {'type': 'activity_count', 'value': 500},
        'rarity': 'epic',
        'points_value': 250,
        'is_secret': False
    },
    {
        'achievement_key': 'activity_1000',
        'category': 'milestone',
        'subcategory': 'activities',
        'title': '👑 Grand Master',
        'description': 'Complete 1000 activities',
        'icon': '👑',
        'unlock_criteria': {'type': 'activity_count', 'value': 1000},
        'rarity': 'legendary',
        'points_value': 500,
        'is_secret': False
    },
    {
        'achievement_key': 'perfect_score',
        'category': 'skill',
        'subcategory': 'accuracy',
        'title': '💯 Perfect Score',
        'description': 'Achieve 100% accuracy on any activity',
        'icon': '💯',
        'unlock_criteria': {'type': 'perfect_score'},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False,
        'is_repeatable': True
    },
    {
        'achievement_key': 'perfect_streak_5',
        'category': 'skill',
        'subcategory': 'accuracy',
        'title': '🎖️ Perfectionist',
        'description': 'Achieve 5 perfect scores in a row',
        'icon': '🎖️',
        'unlock_criteria': {'type': 'perfect_streak', 'value': 5},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False
    },
    
    # ============================================================================
    # STREAK ACHIEVEMENTS (7 achievements)
    # ============================================================================
    {
        'achievement_key': 'streak_3',
        'category': 'streak',
        'subcategory': None,
        'title': '🔥 On Fire!',
        'description': 'Maintain a 3-day learning streak',
        'icon': '🔥',
        'unlock_criteria': {'type': 'streak_days', 'value': 3},
        'rarity': 'common',
        'points_value': 30,
        'is_secret': False
    },
    {
        'achievement_key': 'streak_7',
        'category': 'streak',
        'subcategory': None,
        'title': '🌟 Week Warrior',
        'description': 'Maintain a 7-day learning streak',
        'icon': '🌟',
        'unlock_criteria': {'type': 'streak_days', 'value': 7},
        'rarity': 'uncommon',
        'points_value': 70,
        'is_secret': False
    },
    {
        'achievement_key': 'streak_30',
        'category': 'streak',
        'subcategory': None,
        'title': '🏆 Month Master',
        'description': 'Maintain a 30-day learning streak',
        'icon': '🏆',
        'unlock_criteria': {'type': 'streak_days', 'value': 30},
        'rarity': 'rare',
        'points_value': 300,
        'is_secret': False
    },
    {
        'achievement_key': 'streak_100',
        'category': 'streak',
        'subcategory': None,
        'title': '💎 Century Streaker',
        'description': 'Maintain a 100-day learning streak',
        'icon': '💎',
        'unlock_criteria': {'type': 'streak_days', 'value': 100},
        'rarity': 'epic',
        'points_value': 1000,
        'is_secret': False
    },
    {
        'achievement_key': 'streak_365',
        'category': 'streak',
        'subcategory': None,
        'title': '🌈 Year Champion',
        'description': 'Maintain a 365-day learning streak',
        'icon': '🌈',
        'unlock_criteria': {'type': 'streak_days', 'value': 365},
        'rarity': 'legendary',
        'points_value': 5000,
        'is_secret': False
    },
    {
        'achievement_key': 'comeback_kid',
        'category': 'streak',
        'subcategory': None,
        'title': '💪 Comeback Kid',
        'description': 'Successfully recover a broken streak',
        'icon': '💪',
        'unlock_criteria': {'type': 'streak_recovery'},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False,
        'is_repeatable': True
    },
    {
        'achievement_key': 'freeze_master',
        'category': 'streak',
        'subcategory': None,
        'title': '❄️ Freeze Master',
        'description': 'Use 5 streak freezes',
        'icon': '❄️',
        'unlock_criteria': {'type': 'freeze_count', 'value': 5},
        'rarity': 'uncommon',
        'points_value': 25,
        'is_secret': False
    },
    
    # ============================================================================
    # STUDY TIME ACHIEVEMENTS (6 achievements)
    # ============================================================================
    {
        'achievement_key': 'study_1hour',
        'category': 'milestone',
        'subcategory': 'study_time',
        'title': '⏱️ Hour Power',
        'description': 'Study for a total of 1 hour',
        'icon': '⏱️',
        'unlock_criteria': {'type': 'study_hours', 'value': 1},
        'rarity': 'common',
        'points_value': 20,
        'is_secret': False
    },
    {
        'achievement_key': 'study_10hours',
        'category': 'milestone',
        'subcategory': 'study_time',
        'title': '📚 Study Marathon',
        'description': 'Study for a total of 10 hours',
        'icon': '📚',
        'unlock_criteria': {'type': 'study_hours', 'value': 10},
        'rarity': 'uncommon',
        'points_value': 100,
        'is_secret': False
    },
    {
        'achievement_key': 'study_50hours',
        'category': 'milestone',
        'subcategory': 'study_time',
        'title': '🎓 Dedicated Student',
        'description': 'Study for a total of 50 hours',
        'icon': '🎓',
        'unlock_criteria': {'type': 'study_hours', 'value': 50},
        'rarity': 'rare',
        'points_value': 500,
        'is_secret': False
    },
    {
        'achievement_key': 'study_100hours',
        'category': 'milestone',
        'subcategory': 'study_time',
        'title': '🏅 Century Scholar',
        'description': 'Study for a total of 100 hours',
        'icon': '🏅',
        'unlock_criteria': {'type': 'study_hours', 'value': 100},
        'rarity': 'epic',
        'points_value': 1000,
        'is_secret': False
    },
    {
        'achievement_key': 'study_500hours',
        'category': 'milestone',
        'subcategory': 'study_time',
        'title': '👨‍🎓 Professor',
        'description': 'Study for a total of 500 hours',
        'icon': '👨‍🎓',
        'unlock_criteria': {'type': 'study_hours', 'value': 500},
        'rarity': 'legendary',
        'points_value': 5000,
        'is_secret': False
    },
    {
        'achievement_key': 'intense_session',
        'category': 'skill',
        'subcategory': 'study_time',
        'title': '🔥 Intense Session',
        'description': 'Study for 2 hours in a single session',
        'icon': '🔥',
        'unlock_criteria': {'type': 'session_duration', 'value': 120},
        'rarity': 'uncommon',
        'points_value': 75,
        'is_secret': False,
        'is_repeatable': True
    },
    
    # ============================================================================
    # SKILL MASTERY ACHIEVEMENTS (12 achievements - 2 per skill)
    # ============================================================================
    {
        'achievement_key': 'vocab_novice',
        'category': 'skill',
        'subcategory': 'vocabulary',
        'title': '📖 Vocabulary Novice',
        'description': 'Reach 50% vocabulary proficiency',
        'icon': '📖',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'vocabulary', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'vocab_master',
        'category': 'skill',
        'subcategory': 'vocabulary',
        'title': '📚 Vocabulary Master',
        'description': 'Reach 80% vocabulary proficiency',
        'icon': '📚',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'vocabulary', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'vocab_novice'
    },
    {
        'achievement_key': 'grammar_novice',
        'category': 'skill',
        'subcategory': 'grammar',
        'title': '✍️ Grammar Novice',
        'description': 'Reach 50% grammar proficiency',
        'icon': '✍️',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'grammar', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'grammar_master',
        'category': 'skill',
        'subcategory': 'grammar',
        'title': '✅ Grammar Master',
        'description': 'Reach 80% grammar proficiency',
        'icon': '✅',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'grammar', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'grammar_novice'
    },
    {
        'achievement_key': 'reading_novice',
        'category': 'skill',
        'subcategory': 'reading',
        'title': '📖 Reading Novice',
        'description': 'Reach 50% reading proficiency',
        'icon': '📖',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'reading', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'reading_master',
        'category': 'skill',
        'subcategory': 'reading',
        'title': '📚 Reading Master',
        'description': 'Reach 80% reading proficiency',
        'icon': '📚',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'reading', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'reading_novice'
    },
    {
        'achievement_key': 'writing_novice',
        'category': 'skill',
        'subcategory': 'writing',
        'title': '✏️ Writing Novice',
        'description': 'Reach 50% writing proficiency',
        'icon': '✏️',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'writing', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'writing_master',
        'category': 'skill',
        'subcategory': 'writing',
        'title': '✒️ Writing Master',
        'description': 'Reach 80% writing proficiency',
        'icon': '✒️',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'writing', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'writing_novice'
    },
    {
        'achievement_key': 'listening_novice',
        'category': 'skill',
        'subcategory': 'listening',
        'title': '👂 Listening Novice',
        'description': 'Reach 50% listening proficiency',
        'icon': '👂',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'listening', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'listening_master',
        'category': 'skill',
        'subcategory': 'listening',
        'title': '🎧 Listening Master',
        'description': 'Reach 80% listening proficiency',
        'icon': '🎧',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'listening', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'listening_novice'
    },
    {
        'achievement_key': 'speaking_novice',
        'category': 'skill',
        'subcategory': 'speaking',
        'title': '🗣️ Speaking Novice',
        'description': 'Reach 50% speaking proficiency',
        'icon': '🗣️',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'speaking', 'threshold': 0.5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'speaking_master',
        'category': 'skill',
        'subcategory': 'speaking',
        'title': '🎤 Speaking Master',
        'description': 'Reach 80% speaking proficiency',
        'icon': '🎤',
        'unlock_criteria': {'type': 'skill_mastery', 'skill': 'speaking', 'threshold': 0.8},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': False,
        'prerequisite_achievement': 'speaking_novice'
    },
    
    # ============================================================================
    # LEVEL ACHIEVEMENTS (6 achievements)
    # ============================================================================
    {
        'achievement_key': 'level_a1',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '🎯 A1 Complete',
        'description': 'Complete A1 (Beginner) level',
        'icon': '🎯',
        'unlock_criteria': {'type': 'level_reached', 'level': 'A1'},
        'rarity': 'common',
        'points_value': 100,
        'is_secret': False
    },
    {
        'achievement_key': 'level_a2',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '🌟 A2 Complete',
        'description': 'Complete A2 (Elementary) level',
        'icon': '🌟',
        'unlock_criteria': {'type': 'level_reached', 'level': 'A2'},
        'rarity': 'uncommon',
        'points_value': 200,
        'is_secret': False
    },
    {
        'achievement_key': 'level_b1',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '🏅 B1 Complete',
        'description': 'Complete B1 (Intermediate) level',
        'icon': '🏅',
        'unlock_criteria': {'type': 'level_reached', 'level': 'B1'},
        'rarity': 'rare',
        'points_value': 300,
        'is_secret': False
    },
    {
        'achievement_key': 'level_b2',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '⭐ B2 Complete',
        'description': 'Complete B2 (Upper Intermediate) level',
        'icon': '⭐',
        'unlock_criteria': {'type': 'level_reached', 'level': 'B2'},
        'rarity': 'epic',
        'points_value': 500,
        'is_secret': False
    },
    {
        'achievement_key': 'level_c1',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '💎 C1 Complete',
        'description': 'Complete C1 (Advanced) level',
        'icon': '💎',
        'unlock_criteria': {'type': 'level_reached', 'level': 'C1'},
        'rarity': 'legendary',
        'points_value': 1000,
        'is_secret': False
    },
    {
        'achievement_key': 'level_c2',
        'category': 'milestone',
        'subcategory': 'level',
        'title': '👑 C2 Complete',
        'description': 'Complete C2 (Mastery) level - Native-like proficiency!',
        'icon': '👑',
        'unlock_criteria': {'type': 'level_reached', 'level': 'C2'},
        'rarity': 'legendary',
        'points_value': 5000,
        'is_secret': False
    },
    
    # ============================================================================
    # SOCIAL ACHIEVEMENTS (5 achievements)
    # ============================================================================
    {
        'achievement_key': 'first_friend',
        'category': 'social',
        'subcategory': None,
        'title': '👋 First Friend',
        'description': 'Connect with your first friend',
        'icon': '👋',
        'unlock_criteria': {'type': 'friend_count', 'value': 1},
        'rarity': 'common',
        'points_value': 25,
        'is_secret': False
    },
    {
        'achievement_key': 'social_butterfly',
        'category': 'social',
        'subcategory': None,
        'title': '🦋 Social Butterfly',
        'description': 'Connect with 10 friends',
        'icon': '🦋',
        'unlock_criteria': {'type': 'friend_count', 'value': 10},
        'rarity': 'uncommon',
        'points_value': 100,
        'is_secret': False
    },
    {
        'achievement_key': 'study_partner',
        'category': 'social',
        'subcategory': None,
        'title': '🤝 Study Partner',
        'description': 'Find a study partner',
        'icon': '🤝',
        'unlock_criteria': {'type': 'study_partner_matched'},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'achievement_sharer',
        'category': 'social',
        'subcategory': None,
        'title': '📢 Achievement Sharer',
        'description': 'Share 5 achievements',
        'icon': '📢',
        'unlock_criteria': {'type': 'achievements_shared', 'value': 5},
        'rarity': 'uncommon',
        'points_value': 50,
        'is_secret': False
    },
    {
        'achievement_key': 'popular',
        'category': 'social',
        'subcategory': None,
        'title': '🌟 Popular',
        'description': 'Get 100 likes on shared achievements',
        'icon': '🌟',
        'unlock_criteria': {'type': 'total_likes', 'value': 100},
        'rarity': 'rare',
        'points_value': 200,
        'is_secret': False
    },
    
    # ============================================================================
    # SECRET/SPECIAL ACHIEVEMENTS (6 achievements)
    # ============================================================================
    {
        'achievement_key': 'night_owl',
        'category': 'special',
        'subcategory': None,
        'title': '🦉 Night Owl',
        'description': 'Complete 10 activities between midnight and 5 AM',
        'icon': '🦉',
        'unlock_criteria': {'type': 'night_activities', 'value': 10},
        'rarity': 'rare',
        'points_value': 100,
        'is_secret': True
    },
    {
        'achievement_key': 'early_bird',
        'category': 'special',
        'subcategory': None,
        'title': '🌅 Early Bird',
        'description': 'Complete 10 activities before 7 AM',
        'icon': '🌅',
        'unlock_criteria': {'type': 'early_activities', 'value': 10},
        'rarity': 'rare',
        'points_value': 100,
        'is_secret': True
    },
    {
        'achievement_key': 'speed_demon',
        'category': 'special',
        'subcategory': None,
        'title': '⚡ Speed Demon',
        'description': 'Complete 10 activities in under 2 minutes each',
        'icon': '⚡',
        'unlock_criteria': {'type': 'fast_completions', 'value': 10},
        'rarity': 'rare',
        'points_value': 150,
        'is_secret': True
    },
    {
        'achievement_key': 'comeback_champion',
        'category': 'special',
        'subcategory': None,
        'title': '💪 Comeback Champion',
        'description': 'Return after 30+ days absence and complete 10 activities',
        'icon': '💪',
        'unlock_criteria': {'type': 'comeback_after_absence', 'days': 30, 'activities': 10},
        'rarity': 'epic',
        'points_value': 300,
        'is_secret': True
    },
    {
        'achievement_key': 'challenge_crusher',
        'category': 'special',
        'subcategory': None,
        'title': '🎖️ Challenge Crusher',
        'description': 'Complete 30 daily challenges in a row',
        'icon': '🎖️',
        'unlock_criteria': {'type': 'challenge_streak', 'value': 30},
        'rarity': 'epic',
        'points_value': 500,
        'is_secret': True
    },
    {
        'achievement_key': 'legend',
        'category': 'special',
        'subcategory': None,
        'title': '🌟 Legend',
        'description': 'Unlock all non-secret achievements',
        'icon': '🌟',
        'unlock_criteria': {'type': 'all_achievements_unlocked'},
        'rarity': 'legendary',
        'points_value': 10000,
        'is_secret': True
    },
]


def seed_achievements():
    """Seed achievements into database"""
    with app.app_context():
        print("🎮 Starting achievement seeding...")
        
        # Check if achievements already exist
        existing_count = GamificationAchievement.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing achievements. Skipping seeding.")
            print("   Delete existing achievements first if you want to re-seed.")
            return
        
        # Create achievements
        created_count = 0
        for achievement_data in ACHIEVEMENTS:
            achievement = GamificationAchievement(**achievement_data)
            db.session.add(achievement)
            created_count += 1
        
        db.session.commit()
        
        print(f"✅ Successfully created {created_count} achievements!")
        print("\n📊 Achievement Breakdown:")
        print(f"   - Common: {sum(1 for a in ACHIEVEMENTS if a['rarity'] == 'common')}")
        print(f"   - Uncommon: {sum(1 for a in ACHIEVEMENTS if a['rarity'] == 'uncommon')}")
        print(f"   - Rare: {sum(1 for a in ACHIEVEMENTS if a['rarity'] == 'rare')}")
        print(f"   - Epic: {sum(1 for a in ACHIEVEMENTS if a['rarity'] == 'epic')}")
        print(f"   - Legendary: {sum(1 for a in ACHIEVEMENTS if a['rarity'] == 'legendary')}")
        print(f"   - Secret: {sum(1 for a in ACHIEVEMENTS if a['is_secret'])}")
        
        print("\n📂 Categories:")
        categories = {}
        for a in ACHIEVEMENTS:
            cat = a['category']
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in categories.items():
            print(f"   - {cat.title()}: {count}")


if __name__ == '__main__':
    seed_achievements()
