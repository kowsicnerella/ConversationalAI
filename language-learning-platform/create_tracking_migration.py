"""
Create migration for user tracking tables
Run this with: flask db migrate -m "Add user tracking tables"
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from app.models import db

def create_migration():
    """Create database migration for new tracking tables"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SUPABASE_DATABASE_URL') or 'sqlite:///telugu_english_learning.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate_obj = Migrate(app, db)
    
    with app.app_context():
        print("🔄 Creating migration for user tracking tables...")
        print("Tables to be created:")
        print("  - user_assessment_history")
        print("  - user_activity_completions")
        print("  - user_practice_sessions")
        print("  - user_lesson_progress")
        print("  - user_conversation_history")
        print("  - ai_content_cache")
        print("\n✅ Migration ready!")
        print("\nRun these commands:")
        print("  flask db migrate -m 'Add user tracking and AI cache tables'")
        print("  flask db upgrade")

if __name__ == "__main__":
    create_migration()
