"""
Script to initialize the database with sample chapters and learning content.
Run this after database migration to set up initial learning chapters.
"""

from app import create_app
from app.models import db, Chapter, ChapterDependency
from datetime import datetime

def init_sample_chapters():
    """Initialize the database with sample chapters for Telugu-English learning."""
    
    app = create_app('development')
    with app.app_context():
        # Check if chapters already exist
        existing_chapters = Chapter.query.count()
        if existing_chapters > 0:
            print(f"Database already has {existing_chapters} chapters. Skipping initialization.")
            return
        
        print("Initializing sample chapters...")
        
        # Chapter 1: Basic Greetings
        chapter1 = Chapter(
            title="Basic Greetings and Introductions",
            description="Learn essential English greetings and how to introduce yourself",
            chapter_number=1,
            difficulty_level="beginner",
            topic="greetings",
            subtopics=["hello", "goodbye", "introductions", "politeness"],
            estimated_duration_minutes=20,
            required_score_to_pass=0.7,
            prerequisites=[],
            content={
                "introduction": "In this chapter, you will learn basic English greetings and how to introduce yourself politely.",
                "telugu_introduction": "ఈ అధ్యాయంలో, మీరు ప్రాథమిక ఇంగ్లీష్ శుభాకాంక్షలు మరియు మీరు మీరే మర్యాదగా పరిచయం చేసుకోవడం నేర్చుకుంటారు.",
                "key_phrases": [
                    {"english": "Hello", "telugu": "హలో / నమస్కారం"},
                    {"english": "Good morning", "telugu": "శుభోదయం"},
                    {"english": "My name is...", "telugu": "నా పేరు..."},
                    {"english": "Nice to meet you", "telugu": "మిమ్మల్ని కలవడం ఆనందంగా ఉంది"}
                ]
            }
        )
        
        # Chapter 2: Family and Relationships
        chapter2 = Chapter(
            title="Family and Relationships",
            description="Learn vocabulary related to family members and relationships",
            chapter_number=2,
            difficulty_level="beginner",
            topic="family",
            subtopics=["family_members", "relationships", "age", "descriptions"],
            estimated_duration_minutes=25,
            required_score_to_pass=0.7,
            prerequisites=[1],
            content={
                "introduction": "Learn to talk about your family members and relationships in English.",
                "telugu_introduction": "ఇంగ్లీష్‌లో మీ కుటుంబ సభ్యులు మరియు సంబంధాల గురించి మాట్లాడటం నేర్చుకోండి.",
                "key_phrases": [
                    {"english": "Father", "telugu": "తండ్రి"},
                    {"english": "Mother", "telugu": "తల్లి"},
                    {"english": "Brother", "telugu": "అన్న / తమ్ముడు"},
                    {"english": "Sister", "telugu": "అక్క / చెల్లెలు"}
                ]
            }
        )
        
        # Chapter 3: Daily Activities
        chapter3 = Chapter(
            title="Daily Activities and Routines",
            description="Express daily activities and routines in English",
            chapter_number=3,
            difficulty_level="beginner",
            topic="daily_activities",
            subtopics=["morning_routine", "work_activities", "evening_routine", "time_expressions"],
            estimated_duration_minutes=30,
            required_score_to_pass=0.7,
            prerequisites=[1],
            content={
                "introduction": "Learn to describe your daily activities and routines in English.",
                "telugu_introduction": "ఇంగ్లీష్‌లో మీ దైనందిన కార్యకలాపాలు మరియు దినచర్యలను వివరించడం నేర్చుకోండి.",
                "key_phrases": [
                    {"english": "I wake up at...", "telugu": "నేను... గంటలకు లేస్తాను"},
                    {"english": "I go to work", "telugu": "నేను పనికి వెళ్తాను"},
                    {"english": "I eat breakfast", "telugu": "నేను అల్పాహారం తింటాను"},
                    {"english": "I sleep at night", "telugu": "నేను రాత్రికి నిద్రపోతాను"}
                ]
            }
        )
        
        # Chapter 4: Food and Cooking
        chapter4 = Chapter(
            title="Food and Cooking",
            description="Learn vocabulary related to food, cooking, and dining",
            chapter_number=4,
            difficulty_level="intermediate",
            topic="food",
            subtopics=["food_items", "cooking_methods", "restaurant", "ordering_food"],
            estimated_duration_minutes=35,
            required_score_to_pass=0.75,
            prerequisites=[2, 3],
            content={
                "introduction": "Explore food vocabulary and learn to talk about cooking and dining experiences.",
                "telugu_introduction": "ఆహార పదజాలాన్ని అన్వేషించండి మరియు వంట మరియు భోజన అనుభవాల గురించి మాట్లాడటం నేర్చుకోండి.",
                "key_phrases": [
                    {"english": "I'm hungry", "telugu": "నాకు ఆకలిగా ఉంది"},
                    {"english": "I like spicy food", "telugu": "నాకు కారం ఇష్టం"},
                    {"english": "Can I have the menu?", "telugu": "మెనూ ఇవ్వగలరా?"},
                    {"english": "The food is delicious", "telugu": "ఆహారం రుచిగా ఉంది"}
                ]
            }
        )
        
        # Chapter 5: Shopping and Money
        chapter5 = Chapter(
            title="Shopping and Money",
            description="Learn to shop, handle money, and make purchases in English",
            chapter_number=5,
            difficulty_level="intermediate",
            topic="shopping",
            subtopics=["shopping_vocabulary", "money", "prices", "bargaining"],
            estimated_duration_minutes=40,
            required_score_to_pass=0.75,
            prerequisites=[3, 4],
            content={
                "introduction": "Master shopping vocabulary and learn to make purchases confidently in English.",
                "telugu_introduction": "షాపింగ్ పదజాలంలో నైపుణ్యం సాధించండి మరియు ఇంగ్లీష్‌లో నమ్మకంగా కొనుగోళ్లు చేయడం నేర్చుకోండి.",
                "key_phrases": [
                    {"english": "How much does this cost?", "telugu": "ఇది ఎంత ఖర్చు?"},
                    {"english": "I want to buy...", "telugu": "నేను... కొనాలనుకుంటున్నాను"},
                    {"english": "Do you accept credit cards?", "telugu": "మీరు క్రెడిట్ కార్డులను అంగీకరిస్తారా?"},
                    {"english": "Can you give me a discount?", "telugu": "మీరు నాకు డిస్కౌంట్ ఇవ్వగలరా?"}
                ]
            }
        )
        
        # Add chapters to database
        chapters = [chapter1, chapter2, chapter3, chapter4, chapter5]
        for chapter in chapters:
            db.session.add(chapter)
        
        db.session.commit()
        print(f"Added {len(chapters)} chapters to database.")
        
        # Add chapter dependencies
        dependencies = [
            ChapterDependency(chapter_id=2, prerequisite_chapter_id=1, is_strict=True),
            ChapterDependency(chapter_id=3, prerequisite_chapter_id=1, is_strict=True),
            ChapterDependency(chapter_id=4, prerequisite_chapter_id=2, is_strict=True),
            ChapterDependency(chapter_id=4, prerequisite_chapter_id=3, is_strict=False),  # Recommended but not strict
            ChapterDependency(chapter_id=5, prerequisite_chapter_id=3, is_strict=True),
            ChapterDependency(chapter_id=5, prerequisite_chapter_id=4, is_strict=False),  # Recommended but not strict
        ]
        
        for dependency in dependencies:
            db.session.add(dependency)
        
        db.session.commit()
        print(f"Added {len(dependencies)} chapter dependencies.")
        
        print("Sample chapters initialization completed successfully!")

if __name__ == '__main__':
    init_sample_chapters()