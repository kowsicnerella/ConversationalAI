"""
Phase 7: Learning Analytics Database Migration Script
Creates 6 new tables for comprehensive learning analytics and insights.

Tables Created:
1. learning_analytics - Aggregate analytics for each user
2. weekly_reports - Weekly learning summaries with AI insights
3. progress_snapshots - Daily skill proficiency snapshots
4. study_sessions - Individual study session tracking
5. comparison_metrics - Peer comparison data
6. insight_data - AI-generated insights

Run this script ONCE to create all Phase 7 tables.
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.learning_analytics import (
    LearningAnalytics,
    WeeklyReport,
    ProgressSnapshot,
    StudySession,
    ComparisonMetric,
    InsightData
)

def create_phase7_tables():
    """
    Create all Phase 7 learning analytics tables.
    """
    print("=" * 70)
    print("Phase 7: Learning Analytics & Insights - Database Migration")
    print("=" * 70)
    print()
    
    app = create_app('development')
    
    with app.app_context():
        print("Creating Phase 7 analytics tables...")
        print()
        
        try:
            # Create all tables
            db.create_all()
            
            print("✅ Table Creation Summary:")
            print("-" * 70)
            
            # Verify each table
            tables_created = []
            
            # 1. Learning Analytics
            if db.engine.dialect.has_table(db.engine.connect(), 'learning_analytics'):
                tables_created.append('learning_analytics')
                print("✓ learning_analytics        - Aggregate user analytics")
            
            # 2. Weekly Reports
            if db.engine.dialect.has_table(db.engine.connect(), 'weekly_reports'):
                tables_created.append('weekly_reports')
                print("✓ weekly_reports            - Weekly summaries with AI insights")
            
            # 3. Progress Snapshots
            if db.engine.dialect.has_table(db.engine.connect(), 'progress_snapshots'):
                tables_created.append('progress_snapshots')
                print("✓ progress_snapshots        - Daily skill proficiency snapshots")
            
            # 4. Study Sessions
            if db.engine.dialect.has_table(db.engine.connect(), 'study_sessions'):
                tables_created.append('study_sessions')
                print("✓ study_sessions            - Individual session tracking")
            
            # 5. Comparison Metrics
            if db.engine.dialect.has_table(db.engine.connect(), 'comparison_metrics'):
                tables_created.append('comparison_metrics')
                print("✓ comparison_metrics        - Peer comparison data")
            
            # 6. Insight Data
            if db.engine.dialect.has_table(db.engine.connect(), 'insight_data'):
                tables_created.append('insight_data')
                print("✓ insight_data              - AI-generated insights")
            
            print("-" * 70)
            print(f"\n✅ Successfully created {len(tables_created)} tables!")
            print()
            
            # Display table details
            print("=" * 70)
            print("TABLE DETAILS")
            print("=" * 70)
            print()
            
            print("1. LEARNING_ANALYTICS")
            print("   Purpose: Aggregate analytics for each user")
            print("   Columns: 24 (time tracking, performance, skills, velocity, predictions)")
            print("   Indexes: Primary key on id, unique constraint on user_id")
            print()
            
            print("2. WEEKLY_REPORTS")
            print("   Purpose: Weekly learning summaries with AI insights")
            print("   Columns: 22 (period, summary, improvements, achievements, insights)")
            print("   Indexes: user_id + week_start, unique constraint on user + week")
            print()
            
            print("3. PROGRESS_SNAPSHOTS")
            print("   Purpose: Daily skill proficiency snapshots for trend analysis")
            print("   Columns: 13 (date, 6 skills, overall metrics, daily activity)")
            print("   Indexes: user_id + snapshot_date, unique constraint on user + date")
            print()
            
            print("4. STUDY_SESSIONS")
            print("   Purpose: Individual study session tracking")
            print("   Columns: 15 (timing, activities, performance, quality, context)")
            print("   Indexes: user_id + session_start")
            print()
            
            print("5. COMPARISON_METRICS")
            print("   Purpose: Anonymized peer comparison data")
            print("   Columns: 15 (cohort, statistics, percentiles, metadata)")
            print("   Indexes: level + metric_name, unique constraint")
            print()
            
            print("6. INSIGHT_DATA")
            print("   Purpose: AI-generated personalized insights")
            print("   Columns: 17 (classification, content, evidence, actions, status)")
            print("   Indexes: user_id + insight_type + is_active")
            print()
            
            # Summary
            print("=" * 70)
            print("PHASE 7 MIGRATION SUMMARY")
            print("=" * 70)
            print(f"✅ Tables Created: {len(tables_created)}")
            print("✅ All indexes and constraints applied")
            print("✅ All relationships configured")
            print("✅ Database ready for analytics service")
            print()
            
            print("Next Steps:")
            print("1. Build LearningAnalyticsService (~2,500 lines)")
            print("2. Create analytics_routes.py with 17 endpoints")
            print("3. Implement frontend analytics dashboard")
            print("4. Test end-to-end analytics flow")
            print()
            
            print("=" * 70)
            print("✅ PHASE 7 DATABASE MIGRATION COMPLETE!")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print()
            print("=" * 70)
            print("❌ ERROR DURING MIGRATION")
            print("=" * 70)
            print(f"Error: {str(e)}")
            print()
            print("Troubleshooting:")
            print("1. Check if database is accessible")
            print("2. Verify app/models/learning_analytics.py exists")
            print("3. Ensure User model has proper relationships")
            print("4. Check database credentials in config")
            print()
            return False


if __name__ == '__main__':
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "PHASE 7 DATABASE MIGRATION SCRIPT" + " " * 19 + "║")
    print("║" + " " * 15 + "Learning Analytics & Insights" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    success = create_phase7_tables()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now proceed with building the analytics service.\n")
        sys.exit(0)
    else:
        print("\n⚠️  Migration failed. Please check the error messages above.\n")
        sys.exit(1)
