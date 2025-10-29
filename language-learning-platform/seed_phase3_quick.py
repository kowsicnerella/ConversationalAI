"""
Quick Phase 3 Data Seeding Script - Direct Database Access
"""
import sys
import os

# Add the parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Flask app environment variable
os.environ['FLASK_APP'] = 'app.py'

from app import create_app, db
from app.models.learning_node import CurriculumLevel, SkillDomain, LearningNode

print("\n" + "="*60)
print("  PHASE 3 DATA SEEDING - Quick Version")
print("="*60 + "\n")

app = create_app()

with app.app_context():
    print("Seeding CEFR Levels...")
    
    # Check if levels exist
    existing_levels = CurriculumLevel.query.count()
    print(f"  Current CEFR levels in database: {existing_levels}")
    
    if existing_levels == 0:
        levels = [
            {'cefr_level': 'A1', 'level_name': 'Beginner', 'vocabulary_range_min': 0, 'vocabulary_range_max': 500, 'level_order': 1},
            {'cefr_level': 'A2', 'level_name': 'Elementary', 'vocabulary_range_min': 500, 'vocabulary_range_max': 1000, 'level_order': 2},
            {'cefr_level': 'B1', 'level_name': 'Intermediate', 'vocabulary_range_min': 1000, 'vocabulary_range_max': 2000, 'level_order': 3},
            {'cefr_level': 'B2', 'level_name': 'Upper-Intermediate', 'vocabulary_range_min': 2000, 'vocabulary_range_max': 4000, 'level_order': 4},
            {'cefr_level': 'C1', 'level_name': 'Advanced', 'vocabulary_range_min': 4000, 'vocabulary_range_max': 8000, 'level_order': 5},
            {'cefr_level': 'C2', 'level_name': 'Proficient', 'vocabulary_range_min': 8000, 'vocabulary_range_max': 16000, 'level_order': 6},
        ]
        
        for level_data in levels:
            level = CurriculumLevel(**level_data)
            db.session.add(level)
            print(f"  ✓ Created: {level_data['cefr_level']} - {level_data['level_name']}")
        
        db.session.commit()
        print(f"  ✅ Created {len(levels)} CEFR levels\n")
    else:
        print(f"  ⊘ Skipped: {existing_levels} levels already exist\n")
    
    print("Seeding Skill Domains...")
    
    # Check if domains exist
    existing_domains = SkillDomain.query.count()
    print(f"  Current skill domains in database: {existing_domains}")
    
    if existing_domains == 0:
        domains = [
            {'domain_name': 'Listening', 'icon': '🎧', 'color': '#4A90E2', 'order': 1},
            {'domain_name': 'Speaking', 'icon': '🗣️', 'color': '#F5A623', 'order': 2},
            {'domain_name': 'Reading', 'icon': '📖', 'color': '#7ED321', 'order': 3},
            {'domain_name': 'Writing', 'icon': '✍️', 'color': '#BD10E0', 'order': 4},
            {'domain_name': 'Vocabulary', 'icon': '📚', 'color': '#50E3C2', 'order': 5},
            {'domain_name': 'Grammar', 'icon': '📝', 'color': '#FF6B6B', 'order': 6},
        ]
        
        for domain_data in domains:
            domain = SkillDomain(**domain_data)
            db.session.add(domain)
            print(f"  ✓ Created: {domain_data['domain_name']} - {domain_data['icon']}")
        
        db.session.commit()
        print(f"  ✅ Created {len(domains)} skill domains\n")
    else:
        print(f"  ⊘ Skipped: {existing_domains} domains already exist\n")
    
    print("="*60)
    print("  ✅ SEEDING COMPLETE!")
    print("="*60)
    
    # Summary
    total_levels = CurriculumLevel.query.count()
    total_domains = SkillDomain.query.count()
    total_nodes = LearningNode.query.count()
    
    print(f"\nDatabase Summary:")
    print(f"  - CEFR Levels: {total_levels}")
    print(f"  - Skill Domains: {total_domains}")
    print(f"  - Learning Nodes: {total_nodes}")
    print()
