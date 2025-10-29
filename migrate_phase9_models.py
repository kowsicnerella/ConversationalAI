#!/usr/bin/env python3
"""
Phase 9 Model Migration Script

This script renames Phase 9 models to avoid conflicts with existing models:
- DailyChallenge → GamificationChallenge
- Achievement → GamificationAchievement
- LearningStreak → GamificationStreak

It also updates all references in the service and routes files.

Usage:
    python migrate_phase9_models.py
"""

import os
import re
from pathlib import Path

# Define paths
BASE_DIR = Path(r"d:\ConversationalAI\language-learning-platform")
MODEL_FILE = BASE_DIR / "app" / "models" / "gamification_enhanced.py"
SERVICE_FILE = BASE_DIR / "app" / "services" / "gamification_service.py"
ROUTES_FILE = BASE_DIR / "app" / "routes" / "gamification_routes.py"
SEED_FILE = BASE_DIR / "seed_achievements.py"

# Define model renaming map
MODEL_RENAMES = {
    "DailyChallenge": "GamificationChallenge",
    "Achievement": "GamificationAchievement",
    "LearningStreak": "GamificationStreak",
}

# Table name renames to avoid database conflicts
TABLE_RENAMES = {
    "daily_challenges": "gamification_challenges",
    "achievements": "gamification_achievements",
    "learning_streaks": "gamification_streaks",
}


def backup_file(filepath):
    """Create a backup of the file before modifying."""
    backup_path = f"{filepath}.backup"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backed up: {backup_path}")


def rename_models_in_file(filepath, renames):
    """Rename model class names in a file."""
    print(f"\n📝 Processing: {filepath.name}")
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False
    
    # Backup first
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Rename class definitions
    for old_name, new_name in renames.items():
        # Match class definitions: class OldName(
        pattern = rf'class {old_name}\('
        replacement = f'class {new_name}('
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            count = len(re.findall(pattern, content))
            print(f"  ✓ Renamed class definition: {old_name} → {new_name} ({count} occurrence(s))")
            changes_made += count
            content = new_content
    
    # Rename table names in __tablename__
    for old_table, new_table in TABLE_RENAMES.items():
        pattern = rf"__tablename__\s*=\s*['\"]?{old_table}['\"]?"
        replacement = f'__tablename__ = "{new_table}"'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            print(f"  ✓ Renamed table: {old_table} → {new_table}")
            changes_made += 1
            content = new_content
    
    # Rename model references (not in strings)
    # This matches model names used as types, not in quoted strings
    for old_name, new_name in renames.items():
        # Match model references: OldName.query, OldName(), isinstance(x, OldName)
        patterns = [
            (rf'\b{old_name}\.', f'{new_name}.'),  # OldName.query
            (rf'\b{old_name}\(', f'{new_name}('),  # OldName()
            (rf'isinstance\([^,]+,\s*{old_name}\)', lambda m: m.group(0).replace(old_name, new_name)),  # isinstance
            (rf':\s*{old_name}\b', f': {new_name}'),  # Type hints: var: OldName
            (rf'List\[{old_name}\]', f'List[{new_name}]'),  # List[OldName]
            (rf'Optional\[{old_name}\]', f'Optional[{new_name}]'),  # Optional[OldName]
        ]
        
        for pattern, replacement in patterns:
            if callable(replacement):
                # For complex patterns with lambda
                matches = list(re.finditer(pattern, content))
                for match in reversed(matches):  # Reverse to maintain positions
                    new_content = content[:match.start()] + replacement(match) + content[match.end():]
                    content = new_content
                if matches:
                    print(f"  ✓ Updated {len(matches)} reference(s): {old_name} → {new_name}")
                    changes_made += len(matches)
            else:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    count = len(re.findall(pattern, content))
                    print(f"  ✓ Updated {count} reference(s): {old_name} → {new_name}")
                    changes_made += count
                    content = new_content
    
    # Write updated content if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {filepath.name} ({changes_made} total changes)")
        return True
    else:
        print(f"ℹ️  No changes needed in {filepath.name}")
        return False


def update_imports_in_file(filepath, renames):
    """Update import statements in a file."""
    if not filepath.exists():
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Update imports like: from app.models.gamification_enhanced import Achievement
    for old_name, new_name in renames.items():
        # Pattern: import OldName or from ... import OldName
        patterns = [
            (rf'from\s+[^\s]+\s+import\s+([^,\n]*\b{old_name}\b[^,\n]*)', 
             lambda m: m.group(0).replace(old_name, new_name)),
            (rf'import\s+{old_name}\b', f'import {new_name}'),
        ]
        
        for pattern, replacement in patterns:
            if callable(replacement):
                matches = list(re.finditer(pattern, content))
                for match in reversed(matches):
                    new_content = content[:match.start()] + replacement(match) + content[match.end():]
                    content = new_content
            else:
                content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """Main migration function."""
    print("=" * 70)
    print("🔄 Phase 9 Model Migration Script")
    print("=" * 70)
    
    print("\n📋 Model Renames:")
    for old, new in MODEL_RENAMES.items():
        print(f"   {old} → {new}")
    
    print("\n📋 Table Renames:")
    for old, new in TABLE_RENAMES.items():
        print(f"   {old} → {new}")
    
    input("\n⚠️  Press Enter to continue or Ctrl+C to cancel...")
    
    success_count = 0
    
    # 1. Update model definitions
    if rename_models_in_file(MODEL_FILE, MODEL_RENAMES):
        success_count += 1
    
    # 2. Update service file
    if rename_models_in_file(SERVICE_FILE, MODEL_RENAMES):
        success_count += 1
    
    # 3. Update routes file
    if rename_models_in_file(ROUTES_FILE, MODEL_RENAMES):
        success_count += 1
    
    # 4. Update seed file
    if rename_models_in_file(SEED_FILE, {"Achievement": "GamificationAchievement"}):
        success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Migration Complete! Updated {success_count}/4 files")
    print("=" * 70)
    
    print("\n📝 Next Steps:")
    print("   1. Review the changes in each file")
    print("   2. Update app/models/__init__.py to import new model names")
    print("   3. Register blueprint in app/__init__.py")
    print("   4. Run: flask db migrate -m 'Add Phase 9 gamification models'")
    print("   5. Run: flask db upgrade")
    print("   6. Run: python seed_achievements.py")
    print("\n   ⚠️  Backup files created with .backup extension")
    print("   You can restore from backups if needed.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Migration cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
