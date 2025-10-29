"""
Phase 6: Intelligent Assessment System - Database Table Creation Script

Creates all 7 tables for the intelligent assessment system with IRT support.

Tables:
1. assessments - Master assessment templates
2. assessment_questions - Questions with IRT parameters
3. user_assessment_attempts - User attempt tracking
4. question_responses - Individual question responses
5. assessment_results - Comprehensive results analysis
6. skill_diagnostics - Skill-specific diagnostics
7. adaptive_test_sessions - IRT adaptive testing state

Author: AI Learning Platform
Date: October 20, 2025
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app import create_app
from app.models import db
from app.models.intelligent_assessment import (
    Assessment,
    AssessmentQuestion,
    UserAssessmentAttempt,
    QuestionResponse,
    AssessmentResult,
    SkillDiagnostic,
    AdaptiveTestSession
)

def create_phase6_tables():
    """Create all Phase 6 Intelligent Assessment System tables."""
    
    print("=" * 70)
    print("Phase 6: Intelligent Assessment System - Table Creation")
    print("=" * 70)
    
    app = create_app('development')
    
    with app.app_context():
        print("\nCreating Phase 6 tables...")
        
        try:
            # Import inspect to check table existence
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            # Create tables
            tables_created = []
            
            # 1. Assessments
            if 'assessments' not in existing_tables:
                Assessment.__table__.create(db.engine)
                tables_created.append("assessments")
                print("✓ Assessment table created")
            else:
                print("⚠ Assessment table already exists")
            
            # 2. Assessment Questions
            if 'assessment_questions' not in existing_tables:
                AssessmentQuestion.__table__.create(db.engine)
                tables_created.append("assessment_questions")
                print("✓ AssessmentQuestion table created")
            else:
                print("⚠ AssessmentQuestion table already exists")
            
            # 3. User Assessment Attempts
            if 'user_assessment_attempts' not in existing_tables:
                UserAssessmentAttempt.__table__.create(db.engine)
                tables_created.append("user_assessment_attempts")
                print("✓ UserAssessmentAttempt table created")
            else:
                print("⚠ UserAssessmentAttempt table already exists")
            
            # 4. Question Responses
            if 'question_responses' not in existing_tables:
                QuestionResponse.__table__.create(db.engine)
                tables_created.append("question_responses")
                print("✓ QuestionResponse table created")
            else:
                print("⚠ QuestionResponse table already exists")
            
            # 5. Assessment Results
            if 'assessment_results' not in existing_tables:
                AssessmentResult.__table__.create(db.engine)
                tables_created.append("assessment_results")
                print("✓ AssessmentResult table created")
            else:
                print("⚠ AssessmentResult table already exists")
            
            # 6. Skill Diagnostics
            if 'skill_diagnostics' not in existing_tables:
                SkillDiagnostic.__table__.create(db.engine)
                tables_created.append("skill_diagnostics")
                print("✓ SkillDiagnostic table created")
            else:
                print("⚠ SkillDiagnostic table already exists")
            
            # 7. Adaptive Test Sessions
            if 'adaptive_test_sessions' not in existing_tables:
                AdaptiveTestSession.__table__.create(db.engine)
                tables_created.append("adaptive_test_sessions")
                print("✓ AdaptiveTestSession table created")
            else:
                print("⚠ AdaptiveTestSession table already exists")
            
            db.session.commit()
            
            print(f"\n{len(tables_created)}/{7} tables created successfully")
            
            # Display table details
            print("\n" + "=" * 70)
            print("Table Details:")
            print("=" * 70)
            
            print("\n1. assessments:")
            print("   - Master assessment templates")
            print("   - Types: placement, progress, mastery, certification")
            print("   - Adaptive vs Fixed configuration")
            print("   - IRT parameters and stopping criteria")
            
            print("\n2. assessment_questions:")
            print("   - Individual questions with IRT parameters")
            print("   - 3PL model: discrimination, difficulty, guessing")
            print("   - Multiple question types support")
            print("   - Skill area and sub-skill categorization")
            
            print("\n3. user_assessment_attempts:")
            print("   - Tracks user attempts at assessments")
            print("   - Real-time theta (ability) estimation")
            print("   - Progress and completion status")
            print("   - Skill breakdown and proficiency levels")
            
            print("\n4. question_responses:")
            print("   - Individual question answers")
            print("   - IRT analysis per response")
            print("   - Timing and hint usage tracking")
            print("   - Immediate feedback storage")
            
            print("\n5. assessment_results:")
            print("   - Comprehensive result analysis")
            print("   - Skill scores and comparisons")
            print("   - Percentile rankings")
            print("   - Learning gap identification")
            print("   - Personalized recommendations")
            
            print("\n6. skill_diagnostics:")
            print("   - Detailed skill-specific analysis")
            print("   - Sub-skill performance breakdown")
            print("   - Error pattern analysis")
            print("   - Progress tracking over time")
            print("   - Targeted recommendations")
            
            print("\n7. adaptive_test_sessions:")
            print("   - IRT adaptive testing state")
            print("   - Dynamic theta estimation")
            print("   - Next question selection")
            print("   - Stopping criteria progress")
            
            print("\n" + "=" * 70)
            print("IRT (Item Response Theory) Features:")
            print("=" * 70)
            
            print("\nTheta (θ) - Ability Estimation:")
            print("  Range: -3 (beginner) to +3 (expert)")
            print("  0 = average ability")
            print("  Updates after each question response")
            
            print("\nItem Parameters (3PL Model):")
            print("  a = Discrimination (how well item differentiates)")
            print("  b = Difficulty (on theta scale)")
            print("  c = Guessing (probability of guessing correctly)")
            
            print("\nAdaptive Algorithm:")
            print("  - Maximum Information selection")
            print("  - Dynamic difficulty adjustment")
            print("  - Precision-based stopping")
            print("  - Efficient ability estimation")
            
            print("\n" + "=" * 70)
            print("Assessment Types Supported:")
            print("=" * 70)
            
            print("\n1. Placement Assessment")
            print("   - Initial proficiency determination")
            print("   - Comprehensive skill coverage")
            print("   - Adaptive or fixed format")
            
            print("\n2. Progress Assessment")
            print("   - Periodic skill check")
            print("   - Improvement tracking")
            print("   - Comparison with previous attempts")
            
            print("\n3. Mastery Assessment")
            print("   - Topic/skill mastery verification")
            print("   - High precision requirements")
            print("   - Certification readiness")
            
            print("\n4. Certification Prep")
            print("   - Exam simulation")
            print("   - Readiness determination")
            print("   - Gap analysis")
            
            print("\n" + "=" * 70)
            print("✅ Phase 6 Table Creation Complete!")
            print("=" * 70)
            
            print("\nNext Steps:")
            print("1. Implement IntelligentAssessmentEngine service")
            print("2. Create assessment API routes")
            print("3. Integrate with learning paths")
            print("4. Build frontend assessment components")
            print("5. Add IRT algorithm implementation")
            print("6. Create assessment analytics dashboard")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False


if __name__ == '__main__':
    success = create_phase6_tables()
    sys.exit(0 if success else 1)
