"""
Script to fix all instances of activity_service.model.generate_content()
Replaces them with LLMConfig.generate_text()
"""
import re
import os

# List of files to fix
files_to_fix = [
    "app/api/test_routes.py",
    "app/api/practice_routes.py",
    "app/api/media_routes.py",
    "app/api/learning_path_routes_old.py",
    "app/api/chat_routes.py",
    "app/api/chapter_routes.py",
    "app/api/analytics_routes.py",
]

base_path = "/app/"  # Will be prepended with full path

def fix_file(filepath):
    """Fix a single file"""
    print(f"\nProcessing: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ⚠️  File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern 1: Simple response assignment
    # response = activity_service.model.generate_content(prompt_var)
    pattern1 = r'response\s*=\s*activity_service\.model\.generate_content\(([^)]+)\)'
    replacement1 = r'''from app.services.llm_config import LLMConfig
        result = LLMConfig.generate_text(\1, json_mode=True)
        if not result['success']:
            return jsonify({"error": "Failed to generate response", "telugu_error": "ప్రతిస్పందన రూపొందించడంలో విఫలమైంది"}), 500
        response_text = result['text']'''
    
    # Pattern 2: Direct text extraction
    # ai_response = activity_service.model.generate_content(prompt)
    pattern2 = r'ai_response\s*=\s*activity_service\.model\.generate_content\(([^)]+)\)'
    replacement2 = r'''from app.services.llm_config import LLMConfig
        result = LLMConfig.generate_text(\1, json_mode=True)
        if not result['success']:
            return jsonify({"error": "Failed to generate response", "telugu_error": "ప్రతిస్పందన రూపొందించడంలో విఫలమైంది"}), 500
        ai_response = result['text']'''
    
    # Apply replacements
    replaced = False
    
    if re.search(pattern1, content):
        print("  ✓ Found pattern 1 (response = ...)")
        # Note: This simple regex replacement may need manual review
        replaced = True
    
    if re.search(pattern2, content):
        print("  ✓ Found pattern 2 (ai_response = ...)")
        replaced = True
    
    if replaced:
        # Instead of auto-replacing (which could break things), just report
        print(f"  ⚠️  Manual fixes needed - this file has {len(re.findall(pattern1, content)) + len(re.findall(pattern2, content))} instances to fix")
        return False
    
    return True

# Main execution
print("=" * 60)
print("ActivityGeneratorService.model.generate_content() Fixer")
print("=" * 60)

base_dir = "D:/ConversationalAI/language-learning-platform"

for file_rel in files_to_fix:
    filepath = os.path.join(base_dir, file_rel)
    fix_file(filepath)

print("\n" + "=" * 60)
print("Summary: Manual fixes required for the following files:")
print("  - These files use activity_service.model.generate_content()")
print("  - Need to replace with LLMConfig.generate_text()")
print("  - See fix_critical_routes.py for pattern")
print("=" * 60)
