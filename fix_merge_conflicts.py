#!/usr/bin/env python
"""Fix Git merge conflicts in Python files by keeping the second option."""

import os
import re
from pathlib import Path

def fix_merge_conflict(filepath):
    """Fix merge conflicts in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match merge conflicts
        pattern = r'<<<<<<< HEAD.*?=======\n(.*?)>>>>>>> [a-f0-9]+'
        
        # Replace conflicts with the second option (after =======)
        def replace_conflict(match):
            # Return the content between ======= and >>>>>>>
            return match.group(1).rstrip()
        
        fixed_content = re.sub(pattern, replace_conflict, content, flags=re.DOTALL)
        
        # Write back if changes were made
        if fixed_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all Python files with merge conflicts."""
    files_to_fix = [
        "evaluations/admin.py",
        "evaluations/migrations/0001_initial.py",
        "evaluations/models.py",
        "evaluations/urls.py",
        "evaluations/views.py",
        "notifications/admin.py",
        "notifications/migrations/0001_initial.py",
        "notifications/models.py",
        "notifications/views.py",
    ]
    
    fixed_count = 0
    for filepath in files_to_fix:
        full_path = Path(filepath)
        if full_path.exists():
            if fix_merge_conflict(full_path):
                fixed_count += 1
        else:
            print(f"File not found: {filepath}")
    
    print(f"\nFixed {fixed_count} files with merge conflicts.")

if __name__ == "__main__":
    main()