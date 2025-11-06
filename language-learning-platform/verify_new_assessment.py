"""Verify the new assessment will have unique questions"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import ProficiencyAssessment
from app.services.initial_assessment_service import InitialAssessmentService

app = create_app()

with app.app_context():
    # Check if there are any incomplete assessments
    incomplete = ProficiencyAssessment.query.filter_by(completed_at=None).all()
    print(f"Incomplete assessments: {len(incomplete)}")
    
    if incomplete:
        print("⚠️ There are still incomplete assessments. Delete them first.")
        for a in incomplete:
            print(f"  - ID {a.id}, Type: {a.assessment_type}, Questions: {len(a.questions_asked or [])}")
    else:
        print("✅ No incomplete assessments found.")
    
    print("\n" + "=" * 80)
    print("TESTING NEW ASSESSMENT GENERATION")
    print("=" * 80)
    
    # Test question generation (without saving to DB)
    service = InitialAssessmentService()
    
    # Simulate comprehensive assessment
    print("\nGenerating comprehensive assessment questions...")
    assessment_data = service._generate_comprehensive_assessment()
    
    questions = assessment_data['questions']
    print(f"Total questions: {len(questions)}")
    print(f"Expected: 36 (6 skills × 3 levels × 2 questions per level)")
    
    # Check uniqueness
    question_texts = [q['question_text'] for q in questions]
    unique_texts = set(question_texts)
    
    print(f"Unique question texts: {len(unique_texts)}")
    
    if len(unique_texts) == len(questions):
        print("\n✅ SUCCESS! All 36 questions are UNIQUE!")
        print("\nSample questions:")
        for i in range(min(5, len(questions))):
            q = questions[i]
            print(f"{i+1}. [{q['skill_area']}:{q['difficulty_level']}] {q['question_text'][:60]}...")
    else:
        duplicates = len(questions) - len(unique_texts)
        print(f"\n❌ PROBLEM: Found {duplicates} duplicate question(s)")
        
        # Show duplicates
        from collections import Counter
        text_counts = Counter(question_texts)
        print("\nDuplicate questions:")
        for text, count in text_counts.items():
            if count > 1:
                print(f"  - '{text[:60]}...' appears {count} times")
