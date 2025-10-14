"""
Service Health Check Script
Checks all services for proper configuration and functionality
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*80)
print("  SERVICE HEALTH CHECK")
print("="*80 + "\n")

# Check 1: Environment Variables
print("1. ENVIRONMENT VARIABLES")
print("-" * 40)
env_vars = ['GEMINI_API_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL', 'OPENAI_API_KEY']
for var in env_vars:
    value = os.getenv(var)
    if value:
        masked_value = value[:8] + "..." if len(value) > 8 else "***"
        print(f"✓ {var}: {masked_value}")
    else:
        print(f"✗ {var}: NOT SET")

# Check 2: Import all services
print("\n2. SERVICE IMPORTS")
print("-" * 40)

services_to_check = [
    ('ActivityGeneratorService', 'app.services.activity_generator_service'),
    ('ActivityService', 'app.services.activity_service'),
    ('AdaptiveLearningService', 'app.services.adaptive_learning_service'),
    ('AnalyticsService', 'app.services.analytics_service'),
    ('ChatService', 'app.services.chat_service'),
    ('ComprehensiveAssessmentService', 'app.services.comprehensive_assessment_service'),
    ('GamificationService', 'app.services.gamification_service'),
    ('GoalService', 'app.services.goal_service'),
    ('ImageService', 'app.services.image_service'),
    ('InitialAssessmentService', 'app.services.initial_assessment_service'),
    ('LearningPathService', 'app.services.learning_path_service'),
    ('Mem0Service', 'app.services.mem0_service'),
    ('NotificationService', 'app.services.notification_service'),
    ('PersonalizationService', 'app.services.personalization_service'),
    ('PracticeAgentService', 'app.services.practice_agent_service'),
    ('ProgressService', 'app.services.progress_service'),
]

for service_name, module_path in services_to_check:
    try:
        module = __import__(module_path, fromlist=[service_name])
        service_class = getattr(module, service_name)
        print(f"✓ {service_name}: OK")
    except Exception as e:
        print(f"✗ {service_name}: FAILED - {str(e)}")

# Check 3: Database Models
print("\n3. DATABASE MODELS")
print("-" * 40)

try:
    from app.models import (
        User, Profile, Activity, UserActivityLog, Badge, UserBadge,
        LearningPath, Achievement, UserGoal, ProficiencyAssessment,
        VocabularyWord, MistakePattern, LearningSession, DailyChallenge,
        UserDailyChallengeCompletion, Chapter, UserChapterProgress,
        PracticeSession, UserNotes, TestAssessment, ChapterDependency,
        AIConversationContext
    )
    
    models = [
        'User', 'Profile', 'Activity', 'UserActivityLog', 'Badge', 'UserBadge',
        'LearningPath', 'Achievement', 'UserGoal', 'ProficiencyAssessment',
        'VocabularyWord', 'MistakePattern', 'LearningSession', 'DailyChallenge',
        'UserDailyChallengeCompletion', 'Chapter', 'UserChapterProgress',
        'PracticeSession', 'UserNotes', 'TestAssessment', 'ChapterDependency',
        'AIConversationContext'
    ]
    
    for model in models:
        print(f"✓ {model}: OK")
        
except Exception as e:
    print(f"✗ Models Import Failed: {str(e)}")
    traceback.print_exc()

# Check 4: API Routes
print("\n4. API ROUTES")
print("-" * 40)

routes_to_check = [
    'activities_routes',
    'activity_routes',
    'adaptive_learning_routes',
    'analytics_routes',
    'assessment_routes',
    'auth_routes',
    'chapter_routes',
    'chat_routes',
    'chat_tutor_routes',
    'gamification_routes',
    'goals_routes',
    'learning_path_routes',
    'notifications_routes',
    'onboarding_routes',
    'personalization_routes',
    'practice_routes',
    'user_routes',
]

for route in routes_to_check:
    try:
        module = __import__(f'app.api.{route}', fromlist=['*'])
        print(f"✓ {route}: OK")
    except Exception as e:
        print(f"✗ {route}: FAILED - {str(e)}")

# Check 5: Database Connection
print("\n5. DATABASE CONNECTION")
print("-" * 40)

try:
    from app import create_app
    from app.models import db, User, Chapter, Activity
    
    app = create_app('development')
    with app.app_context():
        # Test basic queries
        user_count = User.query.count()
        chapter_count = Chapter.query.count()
        activity_count = Activity.query.count()
        
        print(f"✓ Database Connection: OK")
        print(f"  - Users: {user_count}")
        print(f"  - Chapters: {chapter_count}")
        print(f"  - Activities: {activity_count}")
except Exception as e:
    print(f"✗ Database Connection: FAILED - {str(e)}")

# Check 6: AI Service Configuration
print("\n6. AI SERVICES CONFIGURATION")
print("-" * 40)

try:
    import google.generativeai as genai
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        print(f"✓ Google Gemini API: Configured")
    else:
        print(f"✗ Google Gemini API: API key not set")
except Exception as e:
    print(f"✗ Google Gemini API: FAILED - {str(e)}")

try:
    from openai import OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"✓ OpenAI API: Configured")
    else:
        print(f"✗ OpenAI API: API key not set")
except Exception as e:
    print(f"✗ OpenAI API: FAILED - {str(e)}")

try:
    from mem0 import Memory
    print(f"✓ Mem0: Installed")
except Exception as e:
    print(f"✗ Mem0: FAILED - {str(e)}")

print("\n" + "="*80)
print("  HEALTH CHECK COMPLETE")
print("="*80 + "\n")
