"""
Phase 4: Performance Tracking Database Migration Script
Creates all new performance tracking tables
"""
from app import create_app
from app.models import db
from app.models.performance_tracking import (
    ListeningPerformance,
    SpeakingPerformance,
    ReadingPerformance,
    WritingPerformance,
    RealWorldPerformance,
    SkillTrajectory
)


def create_performance_tables():
    """Create all Phase 4 performance tracking tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating Phase 4 Performance Tracking tables...")
        
        # Create all tables
        db.create_all()
        
        print("✓ ListeningPerformance table created")
        print("✓ SpeakingPerformance table created")
        print("✓ ReadingPerformance table created")
        print("✓ WritingPerformance table created")
        print("✓ RealWorldPerformance table created")
        print("✓ SkillTrajectory table created")
        
        print("\n✅ Phase 4 Performance Tracking tables created successfully!")
        print("\nNew tables:")
        print("  - listening_performance")
        print("  - speaking_performance")
        print("  - reading_performance")
        print("  - writing_performance")
        print("  - real_world_performance")
        print("  - skill_trajectories")
        
        # Verify tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'listening_performance',
            'speaking_performance',
            'reading_performance',
            'writing_performance',
            'real_world_performance',
            'skill_trajectories'
        ]
        
        print("\nVerification:")
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ {table} exists")
            else:
                print(f"  ✗ {table} NOT FOUND")


if __name__ == "__main__":
    create_performance_tables()
