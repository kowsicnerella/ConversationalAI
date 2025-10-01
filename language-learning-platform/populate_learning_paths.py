#!/usr/bin/env python3
"""
Script to populate the database with comprehensive Telugu learning paths.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, LearningPath
from datetime import datetime

def create_learning_paths():
    """Create comprehensive learning paths for Telugu language learning."""
    
    learning_paths = [
        {
            'title': 'Telugu Basics for Complete Beginners',
            'description': 'Start your Telugu journey with essential greetings, numbers, and basic vocabulary. Perfect for absolute beginners.',
            'category': 'vocabulary',
            'difficulty_level': 'beginner',
            'estimated_duration_hours': 40,
            'prerequisites': [],
            'learning_objectives': [
                'Learn Telugu script and pronunciation',
                'Master basic greetings and introductions',
                'Count numbers 1-100 in Telugu',
                'Use essential daily vocabulary (family, food, colors)',
                'Form simple sentences and questions'
            ],
            'is_active': True
        },
        {
            'title': 'Conversational Telugu Mastery',
            'description': 'Build confidence in everyday Telugu conversations. Learn practical phrases for shopping, traveling, and social interactions.',
            'category': 'conversation',
            'difficulty_level': 'intermediate',
            'estimated_duration_hours': 60,
            'prerequisites': ['Basic Telugu vocabulary', 'Telugu script reading'],
            'learning_objectives': [
                'Engage in everyday conversations',
                'Navigate shopping and dining situations',
                'Discuss hobbies and interests',
                'Handle travel and transportation queries',
                'Express opinions and preferences confidently'
            ],
            'is_active': True
        },
        {
            'title': 'Telugu Grammar Fundamentals',
            'description': 'Master Telugu grammar rules, sentence structure, and verb conjugations for accurate communication.',
            'category': 'grammar',
            'difficulty_level': 'intermediate',
            'estimated_duration_hours': 50,
            'prerequisites': ['Basic Telugu vocabulary', 'Simple sentence formation'],
            'learning_objectives': [
                'Understand Telugu sentence structure',
                'Master verb conjugations and tenses',
                'Learn noun declensions and cases',
                'Use adjectives and adverbs correctly',
                'Form complex sentences with conjunctions'
            ],
            'is_active': True
        },
        {
            'title': 'Business Telugu Communication',
            'description': 'Professional Telugu for workplace communication, meetings, and business correspondence.',
            'category': 'business',
            'difficulty_level': 'advanced',
            'estimated_duration_hours': 45,
            'prerequisites': ['Intermediate Telugu conversation', 'Grammar fundamentals'],
            'learning_objectives': [
                'Conduct business meetings in Telugu',
                'Write professional emails and letters',
                'Present ideas and proposals effectively',
                'Negotiate and discuss business terms',
                'Handle customer service interactions'
            ],
            'is_active': True
        },
        {
            'title': 'Academic Telugu for Students',
            'description': 'Academic vocabulary and formal Telugu for educational settings, exams, and scholarly discussions.',
            'category': 'academic',
            'difficulty_level': 'advanced',
            'estimated_duration_hours': 55,
            'prerequisites': ['Strong grammar foundation', 'Intermediate vocabulary'],
            'learning_objectives': [
                'Master academic terminology',
                'Write essays and reports in Telugu',
                'Participate in formal discussions',
                'Understand literary and classical texts',
                'Present research and academic work'
            ],
            'is_active': True
        },
        {
            'title': 'Telugu Cultural Immersion',
            'description': 'Explore Telugu culture, traditions, festivals, and regional variations through language learning.',
            'category': 'conversation',
            'difficulty_level': 'intermediate',
            'estimated_duration_hours': 35,
            'prerequisites': ['Basic conversation skills'],
            'learning_objectives': [
                'Understand cultural contexts and traditions',
                'Learn festival and celebration vocabulary',
                'Explore regional dialects and variations',
                'Discuss literature, music, and arts',
                'Navigate social customs and etiquette'
            ],
            'is_active': True
        },
        {
            'title': 'Advanced Telugu Vocabulary Builder',
            'description': 'Expand your Telugu vocabulary with advanced words, idioms, and expressions for fluent communication.',
            'category': 'vocabulary',
            'difficulty_level': 'advanced',
            'estimated_duration_hours': 42,
            'prerequisites': ['Intermediate vocabulary', 'Grammar fundamentals'],
            'learning_objectives': [
                'Master 2000+ advanced vocabulary words',
                'Learn common idioms and expressions',
                'Understand proverbs and sayings',
                'Use synonyms and antonyms effectively',
                'Express complex ideas with precision'
            ],
            'is_active': True
        },
        {
            'title': 'Telugu for Travelers',
            'description': 'Essential Telugu phrases and vocabulary for traveling in Telugu-speaking regions.',
            'category': 'conversation',
            'difficulty_level': 'beginner',
            'estimated_duration_hours': 25,
            'prerequisites': [],
            'learning_objectives': [
                'Navigate airports and transportation',
                'Book hotels and accommodations',
                'Order food and drinks confidently',
                'Ask for directions and assistance',
                'Handle emergency situations'
            ],
            'is_active': True
        },
        {
            'title': 'Telugu Grammar Mastery',
            'description': 'Advanced grammar concepts including complex sentence structures, literary forms, and formal language.',
            'category': 'grammar',
            'difficulty_level': 'advanced',
            'estimated_duration_hours': 65,
            'prerequisites': ['Grammar fundamentals', 'Intermediate Telugu'],
            'learning_objectives': [
                'Master complex grammatical structures',
                'Understand poetic and literary forms',
                'Use formal and ceremonial language',
                'Create sophisticated written content',
                'Analyze and critique Telugu texts'
            ],
            'is_active': True
        },
        {
            'title': 'Family Telugu Conversations',
            'description': 'Learn Telugu vocabulary and phrases specifically for family interactions and household communication.',
            'category': 'vocabulary',
            'difficulty_level': 'beginner',
            'estimated_duration_hours': 30,
            'prerequisites': ['Basic greetings'],
            'learning_objectives': [
                'Learn family relationship terms',
                'Discuss daily household activities',
                'Talk about children and parenting',
                'Share family stories and traditions',
                'Express emotions and feelings'
            ],
            'is_active': True
        }
    ]
    
    print("Creating learning paths...")
    
    for path_data in learning_paths:
        # Check if learning path already exists
        existing_path = LearningPath.query.filter_by(title=path_data['title']).first()
        if existing_path:
            print(f"Learning path '{path_data['title']}' already exists, skipping...")
            continue
        
        # Convert prerequisites and learning_objectives to JSON strings
        path_data['prerequisites'] = str(path_data['prerequisites']) if path_data['prerequisites'] else '[]'
        path_data['learning_objectives'] = str(path_data['learning_objectives'])
        
        # Create new learning path
        learning_path = LearningPath(**path_data)
        db.session.add(learning_path)
        print(f"Created learning path: {path_data['title']}")
    
    try:
        db.session.commit()
        print("\n✅ Successfully created all learning paths!")
        
        # Display summary
        total_paths = LearningPath.query.count()
        print(f"\nTotal learning paths in database: {total_paths}")
        
        # Show breakdown by category and difficulty
        categories = db.session.query(LearningPath.category, db.func.count(LearningPath.id)).group_by(LearningPath.category).all()
        difficulties = db.session.query(LearningPath.difficulty_level, db.func.count(LearningPath.id)).group_by(LearningPath.difficulty_level).all()
        
        print("\nBreakdown by category:")
        for category, count in categories:
            print(f"  {category}: {count} paths")
        
        print("\nBreakdown by difficulty:")
        for difficulty, count in difficulties:
            print(f"  {difficulty}: {count} paths")
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating learning paths: {str(e)}")

def main():
    """Main function to run the script."""
    app = create_app('development')
    
    with app.app_context():
        print("Populating Telugu Learning Paths Database...")
        print("=" * 50)
        create_learning_paths()
        print("=" * 50)
        print("Database population complete!")

if __name__ == '__main__':
    main()