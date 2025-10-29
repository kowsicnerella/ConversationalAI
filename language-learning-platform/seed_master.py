"""
Master Database Seeding Script
Seeds all essential data in the correct order
"""
from app import create_app, db
from app.models.user import User, Profile
from app.models.course import LearningPath
from app.models.chapter import Chapter
from app.models.activity import Activity
from app.models.personalization import VocabularyWord
from app.models.learning_node import CurriculumLevel, SkillDomain
from datetime import datetime
import json

def seed_all_data():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("  MASTER DATABASE SEEDING")
        print("="*70 + "\n")
        
        # 1. Seed Test User
        print("1️⃣  Seeding Test User...")
        user = User.query.filter_by(email='test@example.com').first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com',
                is_active=True
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                native_language='Telugu',
                target_language='English',
                proficiency_level='Beginner'
            )
            db.session.add(profile)
            db.session.commit()
            print(f"   ✓ Created user: {user.email}")
        else:
            print(f"   ✓ User already exists: {user.email}")
        
        # 2. Seed Learning Path
        print("\n2️⃣  Seeding Learning Path...")
        path = LearningPath.query.filter_by(title='English for Telugu Speakers').first()
        if not path:
            path = LearningPath(
                title='English for Telugu Speakers',
                description='Comprehensive English learning path tailored for Telugu native speakers',
                category='general',
                difficulty_level='beginner',
                estimated_duration_hours=200,
                is_active=True,
                learning_objectives=['Master basic English communication', 'Build vocabulary', 'Understand grammar']
            )
            db.session.add(path)
            db.session.commit()
            print(f"   ✓ Created learning path: {path.title}")
        else:
            print(f"   ✓ Learning path already exists: {path.title}")
        
        # 3. Seed Chapters
        print("\n3️⃣  Seeding Chapters...")
        chapters_data = [
            {
                'title': 'Getting Started with English',
                'description': 'Basic greetings and introductions',
                'chapter_number': 1,
                'difficulty_level': 'beginner',
                'topic': 'Greetings',
                'estimated_duration_minutes': 30
            },
            {
                'title': 'Everyday Conversations',
                'description': 'Common phrases for daily interactions',
                'chapter_number': 2,
                'difficulty_level': 'beginner',
                'topic': 'Conversations',
                'estimated_duration_minutes': 45
            },
            {
                'title': 'Grammar Foundations',
                'description': 'Essential grammar rules and structures',
                'chapter_number': 3,
                'difficulty_level': 'beginner',
                'topic': 'Grammar',
                'estimated_duration_minutes': 60
            }
        ]
        
        for chapter_data in chapters_data:
            chapter = Chapter.query.filter_by(
                title=chapter_data['title']
            ).first()
            
            if not chapter:
                chapter = Chapter(**chapter_data)
                db.session.add(chapter)
                print(f"   ✓ Created chapter: {chapter_data['title']}")
        
        db.session.commit()
        
        # 4. Seed Sample Activities
        print("\n4️⃣  Seeding Sample Activities...")
        activities_data = [
            {
                'title': 'Introduction to Greetings',
                'activity_type': 'quiz',
                'difficulty_level': 'beginner',
                'description': 'Learn basic English greetings',
                'estimated_duration_minutes': 10,
                'points_reward': 50,
                'order_in_path': 1
            },
            {
                'title': 'Common Phrases Practice',
                'activity_type': 'flashcard',
                'difficulty_level': 'beginner',
                'description': 'Practice everyday English phrases',
                'estimated_duration_minutes': 15,
                'points_reward': 75,
                'order_in_path': 2
            },
            {
                'title': 'Simple Sentence Construction',
                'activity_type': 'writing',
                'difficulty_level': 'beginner',
                'description': 'Build basic English sentences',
                'estimated_duration_minutes': 20,
                'points_reward': 100,
                'order_in_path': 3
            },
            {
                'title': 'Vocabulary Expansion - Food',
                'activity_type': 'vocabulary',
                'difficulty_level': 'beginner',
                'description': 'Learn food-related vocabulary',
                'estimated_duration_minutes': 15,
                'points_reward': 75,
                'order_in_path': 4
            },
            {
                'title': 'Reading Comprehension - Short Story',
                'activity_type': 'reading',
                'difficulty_level': 'intermediate',
                'description': 'Read and understand a short story',
                'estimated_duration_minutes': 25,
                'points_reward': 125,
                'order_in_path': 5
            }
        ]
        
        for activity_data in activities_data:
            activity = Activity.query.filter_by(
                learning_path_id=path.id,
                title=activity_data['title']
            ).first()
            
            if not activity:
                activity = Activity(
                    learning_path_id=path.id,
                    content={'instructions': f"Complete the {activity_data['activity_type']} activity"},
                    **activity_data
                )
                db.session.add(activity)
                print(f"   ✓ Created activity: {activity_data['title']}")
        
        db.session.commit()
        
        # 5. Seed Sample Vocabulary
        print("\n5️⃣  Seeding Sample Vocabulary...")
        vocab_data = [
            {'word': 'hello', 'translation': 'నమస్కారం', 'difficulty': 'Beginner'},
            {'word': 'goodbye', 'translation': 'వీడ్కోలు', 'difficulty': 'Beginner'},
            {'word': 'thank you', 'translation': 'ధన్యవాదములు', 'difficulty': 'Beginner'},
            {'word': 'water', 'translation': 'నీరు', 'difficulty': 'Beginner'},
            {'word': 'food', 'translation': 'ఆహారం', 'difficulty': 'Beginner'},
            {'word': 'house', 'translation': 'ఇల్లు', 'difficulty': 'Beginner'},
            {'word': 'friend', 'translation': 'స్నేహితుడు', 'difficulty': 'Beginner'},
            {'word': 'family', 'translation': 'కుటుంబం', 'difficulty': 'Beginner'},
            {'word': 'school', 'translation': 'పాఠశాల', 'difficulty': 'Beginner'},
            {'word': 'work', 'translation': 'పని', 'difficulty': 'Beginner'}
        ]
        
        for vocab in vocab_data:
            word = VocabularyWord.query.filter_by(
                user_id=user.id,
                english_word=vocab['word']
            ).first()
            if not word:
                word = VocabularyWord(
                    user_id=user.id,
                    english_word=vocab['word'],
                    telugu_translation=vocab['translation'],
                    difficulty_level=vocab['difficulty'].lower(),
                    category='general'
                )
                db.session.add(word)
                print(f"   ✓ Added vocabulary: {vocab['word']}")
        
        db.session.commit()
        
        # 6. Summary
        print("\n" + "="*70)
        print("  SEEDING COMPLETE!")
        print("="*70)
        
        # Get final counts
        user_count = User.query.count()
        path_count = LearningPath.query.count()
        chapter_count = Chapter.query.count()
        activity_count = Activity.query.count()
        vocab_count = VocabularyWord.query.count()
        cefr_count = CurriculumLevel.query.count()
        skill_count = SkillDomain.query.count()
        
        print(f"\n📊 Database Summary:")
        print(f"   Users: {user_count}")
        print(f"   Learning Paths: {path_count}")
        print(f"   Chapters: {chapter_count}")
        print(f"   Activities: {activity_count}")
        print(f"   Vocabulary Words: {vocab_count}")
        print(f"   CEFR Levels: {cefr_count}")
        print(f"   Skill Domains: {skill_count}")
        print(f"\n✅ Database is ready for testing!\n")

if __name__ == "__main__":
    seed_all_data()
