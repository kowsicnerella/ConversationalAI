"""
Script to seed sample activities for learning paths.
Run this once to populate the database with activities.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models import Activity, LearningPath
from datetime import datetime
import json

def seed_activities():
    """Create sample activities for the Telugu learning path"""
    
    app = create_app()
    
    with app.app_context():
        # Get the Telugu learning path
        learning_path = LearningPath.query.filter_by(id=1).first()
        
        if not learning_path:
            print("❌ Learning path with ID 1 not found!")
            return
        
        print(f"📚 Found learning path: {learning_path.title}")
        
        # Check if activities already exist
        existing_activities = Activity.query.filter_by(learning_path_id=1).count()
        if existing_activities > 0:
            print(f"⚠️  {existing_activities} activities already exist for this path")
            return
        
        # Define sample activities for Telugu Basics
        sample_activities = [
            {
                "activity_type": "quiz",
                "title": "Introduction to Telugu Script",
                "description": "Learn the basic Telugu letters and vowels",
                "content": {
                    "questions": [
                        {
                            "id": 1,
                            "question": "What is the first letter of the Telugu alphabet?",
                            "options": ["అ", "ఆ", "ఇ", "ఈ"],
                            "correct_answer": 0,
                            "explanation": "అ (a) is the first letter of the Telugu alphabet"
                        },
                        {
                            "id": 2,
                            "question": "How many basic vowels are in Telugu?",
                            "options": ["3", "5", "6", "12"],
                            "correct_answer": 1,
                            "explanation": "Telugu has 12 vowels: అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ౠ, ఌ, ౡ, ఎ, ఏ"
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "reading",
                "concept_focus": "Telugu Script",
                "order_in_path": 1,
                "estimated_duration_minutes": 15,
                "points_reward": 25
            },
            {
                "activity_type": "flashcard",
                "title": "Basic Telugu Greetings",
                "description": "Learn common Telugu greetings and responses",
                "content": {
                    "flashcards": [
                        {
                            "front": "Hello in Telugu",
                            "back": "నమస్కారం (Namaskaaram)",
                            "pronunciation": "nuh-mus-kaa-rum"
                        },
                        {
                            "front": "Good morning",
                            "back": "శుభోదయం (Shubhodayam)",
                            "pronunciation": "shoo-bho-day-um"
                        },
                        {
                            "front": "Thank you",
                            "back": "ధన్యవాదాలు (Dhanyavaadaalu)",
                            "pronunciation": "dhan-ya-vaa-daa-lu"
                        },
                        {
                            "front": "How are you?",
                            "back": "ఎలా ఉన్నారు? (Ela unnaru?)",
                            "pronunciation": "eh-laa oon-naa-ru"
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "speaking",
                "concept_focus": "Greetings",
                "order_in_path": 2,
                "estimated_duration_minutes": 20,
                "points_reward": 30
            },
            {
                "activity_type": "reading",
                "title": "Numbers 1-10 in Telugu",
                "description": "Learn to read and understand Telugu numbers",
                "content": {
                    "passages": [
                        {
                            "title": "Counting in Telugu",
                            "text": "టెలుగులో సంఖ్యలు (Telugu Numbers):\n1-ఒకటి (Okati)\n2-రెండు (Rendu)\n3-మూడు (Mudu)\n4-నాలుగు (Naalugu)\n5-ఐదు (Aidu)\n6-ఆరు (Aaru)\n7-ఏడు (Aedu)\n8-ఎight (Enimidhi)\n9-తొమ్మిది (Tommidi)\n10-పది (Padi)",
                            "questions": [
                                {
                                    "question": "How do you say 'five' in Telugu?",
                                    "options": ["ఆరు", "ఏడు", "ఐదు", "నాలుగు"],
                                    "correct_answer": 2
                                }
                            ]
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "reading",
                "concept_focus": "Numbers",
                "order_in_path": 3,
                "estimated_duration_minutes": 18,
                "points_reward": 25
            },
            {
                "activity_type": "quiz",
                "title": "Family Members Vocabulary",
                "description": "Learn Telugu words for family members",
                "content": {
                    "questions": [
                        {
                            "id": 1,
                            "question": "What is 'mother' in Telugu?",
                            "options": ["తండ్రి", "అమ్ము", "సోదరుడు", "సోదరి"],
                            "correct_answer": 1,
                            "explanation": "అమ్ము (ammu) means mother in Telugu"
                        },
                        {
                            "id": 2,
                            "question": "How do you say 'brother' in Telugu?",
                            "options": ["సోదరుడు", "సోదరి", "తండ్రి", "అమ్ము"],
                            "correct_answer": 0,
                            "explanation": "సోదరుడు (sodarudu) means brother in Telugu"
                        },
                        {
                            "id": 3,
                            "question": "What is the Telugu word for 'sister'?",
                            "options": ["సోదరుడు", "సోదరి", "తండ్రి", "అమ్ము"],
                            "correct_answer": 1,
                            "explanation": "సోదరి (sodari) means sister in Telugu"
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "vocabulary",
                "concept_focus": "Family",
                "order_in_path": 4,
                "estimated_duration_minutes": 20,
                "points_reward": 35
            },
            {
                "activity_type": "flashcard",
                "title": "Colors in Telugu",
                "description": "Learn common colors and their names in Telugu",
                "content": {
                    "flashcards": [
                        {
                            "front": "Red",
                            "back": "ఎరుపు (Erupu)",
                            "pronunciation": "eh-roo-poo"
                        },
                        {
                            "front": "Blue",
                            "back": "నీలం (Neelam)",
                            "pronunciation": "nee-lum"
                        },
                        {
                            "front": "Yellow",
                            "back": "పసుపు (Pasupu)",
                            "pronunciation": "puh-soo-poo"
                        },
                        {
                            "front": "Green",
                            "back": "ఆకుపచ్చ (Aakupaccha)",
                            "pronunciation": "aa-koo-pah-chuh"
                        },
                        {
                            "front": "White",
                            "back": "తెల్ల (Tella)",
                            "pronunciation": "tel-luh"
                        },
                        {
                            "front": "Black",
                            "back": "నలుపు (Nalupu)",
                            "pronunciation": "nuh-loo-poo"
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "vocabulary",
                "concept_focus": "Colors",
                "order_in_path": 5,
                "estimated_duration_minutes": 15,
                "points_reward": 25
            },
            {
                "activity_type": "quiz",
                "title": "Basic Food Vocabulary",
                "description": "Learn Telugu words for common foods",
                "content": {
                    "questions": [
                        {
                            "id": 1,
                            "question": "What is 'rice' in Telugu?",
                            "options": ["రొట్టె", "బియ్యం", "గోధుమ", "ఆవర్"],
                            "correct_answer": 1,
                            "explanation": "బియ్యం (biryam) means rice in Telugu"
                        },
                        {
                            "id": 2,
                            "question": "How do you say 'water' in Telugu?",
                            "options": ["నీరు", "ఆహారం", "పాలు", "జ్యూస్"],
                            "correct_answer": 0,
                            "explanation": "నీరు (neeru) means water in Telugu"
                        },
                        {
                            "id": 3,
                            "question": "What is the Telugu word for 'bread'?",
                            "options": ["రొట్టె", "బియ్యం", "గోధుమ", "కూర"],
                            "correct_answer": 0,
                            "explanation": "రొట్టె (rotte) means bread in Telugu"
                        }
                    ]
                },
                "difficulty_level": "beginner",
                "skill_area": "vocabulary",
                "concept_focus": "Food",
                "order_in_path": 6,
                "estimated_duration_minutes": 18,
                "points_reward": 30
            }
        ]
        
        # Create activities
        created_count = 0
        for activity_data in sample_activities:
            activity = Activity(
                learning_path_id=1,
                activity_type=activity_data["activity_type"],
                title=activity_data["title"],
                description=activity_data["description"],
                content=activity_data["content"],
                difficulty_level=activity_data["difficulty_level"],
                skill_area=activity_data.get("skill_area"),
                concept_focus=activity_data.get("concept_focus"),
                order_in_path=activity_data["order_in_path"],
                estimated_duration_minutes=activity_data["estimated_duration_minutes"],
                points_reward=activity_data["points_reward"],
                is_adaptive=False,
                mastery_threshold=0.8
            )
            db.session.add(activity)
            created_count += 1
            print(f"✅ Added: {activity_data['title']}")
        
        # Commit all activities
        db.session.commit()
        print(f"\n🎉 Successfully created {created_count} activities!")
        print(f"📊 Learning path now has {Activity.query.filter_by(learning_path_id=1).count()} total activities")

if __name__ == "__main__":
    seed_activities()
