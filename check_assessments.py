#!/usr/bin/env python
import sys
sys.path.insert(0, r'D:\ConversationalAI\language-learning-platform')

from app import create_app, db
from app.models.assessment import ProficiencyAssessment
from app.models.user import User

app = create_app()

with app.app_context():
    assessments = ProficiencyAssessment.query.all()
    print(f"Total assessments: {len(assessments)}")
    for a in assessments:
        user = User.query.get(a.user_id)
        print(f"  Assessment ID: {a.id}")
        print(f"    User ID: {a.user_id} ({user.email if user else 'Unknown'})")
        print(f"    Completed: {a.completed_at}")
        print(f"    Has responses: {bool(a.user_responses)}")
        print(f"    Has evaluation: {bool(a.ai_evaluation)}")
        print(f"    Score: {a.score}")
        print()
