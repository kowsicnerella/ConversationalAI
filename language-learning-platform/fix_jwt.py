#!/usr/bin/env python3
"""
Fix JWT identity handling across all API route files
"""
import os
import re

def fix_jwt_identity_in_file(file_path):
    """Fix get_jwt_identity() calls in a single file"""
    try:
        # Read with UTF-8 encoding to handle Telugu text
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace all instances, but skip auth_routes.py as it uses current_user_id
        if 'auth_routes.py' in file_path:
            # In auth_routes.py, convert current_user_id to int when needed
            content = re.sub(r'current_user_id = get_jwt_identity\(\)', 'current_user_id = int(get_jwt_identity())', content)
        else:
            # In other files, convert user_id to int
            content = re.sub(r'user_id = get_jwt_identity\(\)', 'user_id = int(get_jwt_identity())', content)
        
        # Write back with UTF-8 encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'✅ Fixed JWT identity calls in {file_path}')
        return True
        
    except Exception as e:
        print(f'❌ Error processing {file_path}: {e}')
        return False

def main():
    """Fix JWT identity handling in all API route files"""
    api_dir = 'app/api'
    files_to_fix = [
        'auth_routes.py',
        'chat_routes.py',
        'course_routes.py',
        'media_routes.py',
        'analytics_routes.py',
        'personalization_routes.py',
        'activity_routes.py',
        'gamification_routes.py'
    ]
    
    fixed_count = 0
    for filename in files_to_fix:
        file_path = os.path.join(api_dir, filename)
        if os.path.exists(file_path):
            if fix_jwt_identity_in_file(file_path):
                fixed_count += 1
        else:
            print(f'⚠️  File not found: {file_path}')
    
    print(f'\n🎉 Fixed JWT identity handling in {fixed_count} files')
    print('✅ All endpoints should now work properly with JWT authentication!')

if __name__ == '__main__':
    main()