"""Delete incomplete assessment and allow user to start fresh"""
import sys
sys.path.insert(0, 'e:\\conv ai\\ConversationalAI\\language-learning-platform')

from app import create_app, db
from app.models import ProficiencyAssessment

app = create_app()

with app.app_context():
    # Find incomplete assessments
    incomplete = ProficiencyAssessment.query.filter_by(completed_at=None).all()
    
    print(f"Found {len(incomplete)} incomplete assessment(s)")
    
    for assessment in incomplete:
        print(f"\nAssessment ID: {assessment.id}")
        print(f"User ID: {assessment.user_id}")
        print(f"Type: {assessment.assessment_type}")
        print(f"Created: {assessment.created_at}")
        
        questions = assessment.questions_asked or []
        responses = assessment.user_responses or {}
        
        print(f"Questions: {len(questions)}")
        print(f"Responses: {len(responses)}")
        
        # Check for duplicate question texts
        if questions:
            question_texts = [q.get('question_text', '')[:50] for q in questions]
            unique_texts = set(question_texts)
            if len(unique_texts) < len(question_texts):
                print(f"⚠️ WARNING: Only {len(unique_texts)}/{len(questions)} unique questions!")
                print("This assessment has repeated questions.")
        
        # Ask to delete
        delete = input(f"\nDelete assessment ID {assessment.id}? (yes/no): ").lower()
        if delete == 'yes':
            db.session.delete(assessment)
            db.session.commit()
            print(f"✅ Deleted assessment ID {assessment.id}")
        else:
            print(f"Skipped assessment ID {assessment.id}")
    
    print("\n✅ Done!")
