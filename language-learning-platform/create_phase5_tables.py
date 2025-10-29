"""
Phase 5: Vocabulary Mastery System - Table Creation Script
Creates database tables for comprehensive vocabulary learning with spaced repetition
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.vocabulary_mastery import (
    VocabularyItem,
    UserVocabulary,
    VocabularyReview,
    WordRelationship,
    VocabularyPracticeSession,
)

def create_phase5_tables():
    """Create all Phase 5 vocabulary mastery tables"""
    
    app = create_app("development")
    
    with app.app_context():
        print("\n" + "="*70)
        print("Phase 5: Vocabulary Mastery System - Table Creation")
        print("="*70 + "\n")
        
        # Create tables
        print("Creating Phase 5 tables...\n")
        
        try:
            # Create all vocabulary mastery tables
            db.create_all()
            
            # Verify each table
            tables = [
                ('vocabulary_items', VocabularyItem),
                ('user_vocabulary', UserVocabulary),
                ('vocabulary_reviews', VocabularyReview),
                ('word_relationships', WordRelationship),
                ('vocabulary_practice_sessions', VocabularyPracticeSession),
            ]
            
            created_count = 0
            for table_name, model in tables:
                if db.inspect(db.engine).has_table(table_name):
                    print(f"✓ {model.__name__} table created")
                    created_count += 1
                else:
                    print(f"✗ {model.__name__} table FAILED")
            
            print(f"\n{created_count}/{len(tables)} tables created successfully\n")
            
            # Display table details
            print("="*70)
            print("Table Details:")
            print("="*70 + "\n")
            
            print("1. vocabulary_items:")
            print("   - Stores global vocabulary database")
            print("   - Word definitions, translations, pronunciation")
            print("   - Examples, collocations, usage notes")
            print("   - Categorization by difficulty, topic, frequency")
            print("   - Audio/visual media links\n")
            
            print("2. user_vocabulary:")
            print("   - User's personal vocabulary with SM-2 algorithm")
            print("   - Spaced repetition scheduling")
            print("   - Mastery levels: new → learning → familiar → mastered")
            print("   - Performance tracking: accuracy, response time")
            print("   - Retention metrics: streaks, forgotten count\n")
            
            print("3. vocabulary_reviews:")
            print("   - Individual practice/review attempts")
            print("   - Quality ratings for SM-2 algorithm")
            print("   - Response times and accuracy")
            print("   - Context tracking (where/how reviewed)\n")
            
            print("4. word_relationships:")
            print("   - Semantic connections between words")
            print("   - Types: synonyms, antonyms, collocations, derivatives")
            print("   - Relationship strength and frequency")
            print("   - Enables word network visualization\n")
            
            print("5. vocabulary_practice_sessions:")
            print("   - Grouped vocabulary practice tracking")
            print("   - Session types: daily review, targeted practice, mastery test")
            print("   - Performance metrics and time tracking\n")
            
            print("="*70)
            print("SM-2 Spaced Repetition Algorithm:")
            print("="*70)
            print("Quality Rating (0-5):")
            print("  0 = Complete blackout")
            print("  1 = Incorrect response, correct one seemed familiar")
            print("  2 = Incorrect response, correct one remembered")
            print("  3 = Correct response with difficulty")
            print("  4 = Correct response with hesitation")
            print("  5 = Perfect recall")
            print("\nReview Schedule:")
            print("  Quality < 3: Restart (1 day)")
            print("  Quality >= 3: Increase interval")
            print("    - First review: 1 day")
            print("    - Second review: 6 days")
            print("    - Further reviews: interval × easiness_factor")
            print("\nMastery Progression:")
            print("  new → learning (1-2 reviews)")
            print("  learning → familiar (3-5 reviews, confidence > 60%)")
            print("  familiar → mastered (6+ reviews, confidence > 80%)\n")
            
            print("="*70)
            print("✅ Phase 5 Table Creation Complete!")
            print("="*70)
            print("\nNext Steps:")
            print("1. Implement VocabularyMasteryEngine service")
            print("2. Create vocabulary API routes")
            print("3. Integrate vocabulary tracking with activities")
            print("4. Build vocabulary practice UI components")
            print("5. Add vocabulary analytics and insights\n")
            
        except Exception as e:
            print(f"\n❌ Error creating tables: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == "__main__":
    success = create_phase5_tables()
    sys.exit(0 if success else 1)
