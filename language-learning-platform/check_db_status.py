"""
Check Database Status - Verify all tables and data
"""
from app import create_app, db
from sqlalchemy import text, inspect

def check_database_status():
    app = create_app()
    with app.app_context():
        print("\n" + "="*60)
        print("  DATABASE STATUS CHECK")
        print("="*60 + "\n")
        
        # Check tables
        inspector = inspect(db.engine)
        tables = sorted(inspector.get_table_names())
        print(f"✓ Total tables: {len(tables)}")
        
        # Check Phase 3 tables specifically
        phase3_tables = [t for t in tables if t.startswith('phase3_')]
        print(f"✓ Phase 3 tables: {len(phase3_tables)}")
        for table in phase3_tables:
            print(f"  - {table}")
        
        print("\n" + "-"*60)
        print("  DATA COUNTS")
        print("-"*60 + "\n")
        
        # Check data in key tables
        tables_to_check = [
            ('users', 'Users'),
            ('activities', 'Activities'),
            ('phase3_curriculum_levels', 'CEFR Levels'),
            ('phase3_skill_domains', 'Skill Domains'),
            ('phase3_learning_nodes', 'Learning Nodes'),
            ('vocabulary_words', 'Vocabulary Words'),
            ('courses', 'Courses'),
            ('chapters', 'Chapters')
        ]
        
        for table_name, display_name in tables_to_check:
            try:
                result = db.session.execute(text(f'SELECT COUNT(*) FROM {table_name}'))
                count = result.scalar()
                status = "✓" if count > 0 else "✗"
                print(f"{status} {display_name}: {count}")
            except Exception as e:
                print(f"✗ {display_name}: Error - {str(e)[:50]}")
        
        print("\n" + "="*60)
        print("  DATABASE CHECK COMPLETE")
        print("="*60 + "\n")

if __name__ == "__main__":
    check_database_status()
