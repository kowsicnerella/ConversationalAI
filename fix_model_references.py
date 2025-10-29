#!/usr/bin/env python3
"""
Fix script to replace all instances of activity_service.model.generate_content()
with LLMConfig.generate_text() across all route files
"""

import re
import os
from pathlib import Path

def fix_file(filepath):
    """Fix a single file by replacing model.generate_content with LLMConfig"""
    print(f"\n📄 Processing: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_made = 0
    
    # Fix 1: response = activity_service.model.generate_content(var)
    # followed by _extract_json_from_response(response.text)
    pattern = r'response\s*=\s*activity_service\.model\.generate_content\(([^)]+)\)\s*(?:from\s+app\.services\.activity_generator_service\s+import\s+_extract_json_from_response\s+)?(?:\n\s+)?.*?_extract_json_from_response\(response\.text\)'
    
    # Simpler approach - fix line by line
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for activity_service.model.generate_content
        if 'activity_service.model.generate_content' in line:
            print(f"  ✓ Found line {i+1}: {line.strip()[:60]}...")
            
            # Extract the prompt variable
            match = re.search(r'response\s*=\s*activity_service\.model\.generate_content\(([^)]+)\)', line)
            if match:
                prompt_var = match.group(1)
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                
                # Replace with LLMConfig
                new_lines.append(f"{spaces}from app.services.llm_config import LLMConfig")
                new_lines.append(f"{spaces}result = LLMConfig.generate_text({prompt_var}, json_mode=True)")
                new_lines.append(f"{spaces}if not result['success']:")
                new_lines.append(f"{spaces}    return jsonify({{'error': result.get('error', 'Failed to generate response'), 'telugu_error': 'ప్రతిస్పందన రూపొందించడంలో విఫలమైంది'}}), 500")
                new_lines.append(f"{spaces}response_text = result['text']")
                fixes_made += 1
                i += 1
                continue
            
            # Handle ai_response = activity_service.model.generate_content(var)
            match = re.search(r'ai_response\s*=\s*activity_service\.model\.generate_content\(([^)]+)\)', line)
            if match:
                prompt_var = match.group(1)
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * indent
                
                new_lines.append(f"{spaces}from app.services.llm_config import LLMConfig")
                new_lines.append(f"{spaces}result = LLMConfig.generate_text({prompt_var}, json_mode=True)")
                new_lines.append(f"{spaces}if not result['success']:")
                new_lines.append(f"{spaces}    return jsonify({{'error': result.get('error', 'Failed to generate response'), 'telugu_error': 'ప్రతిస్పందన రూపొందించడంలో విఫలమైంది'}}), 500")
                new_lines.append(f"{spaces}ai_response = result['text']")
                fixes_made += 1
                i += 1
                continue
        
        # Also handle response.text -> response_text
        if 'response.text' in line and 'activity_service.model' not in line:
            line = line.replace('response.text', 'response_text')
        
        new_lines.append(line)
        i += 1
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original_content:
        print(f"  ✅ Fixed {fixes_made} occurrences")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    else:
        print(f"  ℹ️  No changes needed")
        return False

# Files to fix
base_dir = Path("D:/ConversationalAI/language-learning-platform")
files_to_fix = [
    "app/api/learning_path_routes.py",
    "app/api/test_routes.py",
    "app/api/practice_routes.py",
    "app/api/media_routes.py",
    "app/api/learning_path_routes_old.py",
    "app/api/chat_routes.py",
    "app/api/chapter_routes.py",
    "app/api/analytics_routes.py",
]

print("=" * 70)
print("ActivityGeneratorService.model.generate_content() Fixer")
print("=" * 70)

fixed_count = 0
for file_rel in files_to_fix:
    filepath = base_dir / file_rel
    if fix_file(str(filepath)):
        fixed_count += 1

print("\n" + "=" * 70)
print(f"✅ SUMMARY: Fixed {fixed_count} files")
print("=" * 70)
