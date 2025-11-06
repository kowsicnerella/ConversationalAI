"""
Simple script to delete incomplete assessment with duplicate questions
and allow user to start fresh with unique questions.
"""
import sys
import os

# Add the project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import ProficiencyAssessment

def main():
    app = create_app()
    
    with app.app_context():
        # Find all incomplete assessments
        incomplete = ProficiencyAssessment.query.filter_by(completed_at=None).all()
        
        if not incomplete:
            print("✅ No incomplete assessments found.")
            print("You can start a new assessment from the UI.")
            return
        
        print(f"Found {len(incomplete)} incomplete assessment(s)\n")
        
        for assessment in incomplete:
            print("=" * 80)
            print(f"Assessment ID: {assessment.id}")
            print(f"User ID: {assessment.user_id}")
            print(f"Type: {assessment.assessment_type}")
            print(f"Started: {assessment.started_at or 'Not started'}")
            
            questions = assessment.questions_asked or []
            responses = assessment.user_responses or {}
            
            print(f"Total Questions: {len(questions)}")
            print(f"Answered: {len(responses)}")
            
            # Check for duplicate question texts
            if questions:
                question_texts = [q.get('question_text', '') for q in questions]
                unique_texts = set(question_texts)
                duplicates = len(question_texts) - len(unique_texts)
                
                if duplicates > 0:
                    print(f"\n⚠️  WARNING: This assessment has {duplicates} duplicate question(s)!")
                    print(f"   Unique questions: {len(unique_texts)}/{len(questions)}")
                    print(f"\n   This was likely generated with old code that had limited questions.")
                    print(f"   The new code has 108 unique questions (6 per skill × 3 levels × 6 skills).")
                else:
                    print(f"\n✅ All {len(questions)} questions are unique.")
            
            print("=" * 80)
            
        # Ask to delete all
        print("\nTo get assessments with all unique questions, you need to:")
        print("1. Delete the old incomplete assessment(s)")
        print("2. Generate a new assessment from the UI\n")
        
        response = input("Delete all incomplete assessments? (yes/no): ").lower().strip()
        
        if response == 'yes':
            for assessment in incomplete:
                db.session.delete(assessment)
            db.session.commit()
            print(f"\n✅ Deleted {len(incomplete)} incomplete assessment(s)")
            print("✅ You can now generate a new assessment with 36 unique questions!")
        else:
            print("\n❌ No assessments were deleted.")
            print("Note: The current assessment will continue to have duplicate questions.")
            print("      New assessments will have unique questions.")

if __name__ == "__main__":
    main()
