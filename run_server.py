import os
import sys
import django
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

if __name__ == '__main__':
    # URL 패턴 확인
    django.setup()
    from django.urls import get_resolver
    resolver = get_resolver()
    
    print("=== Checking URL patterns ===")
    for pattern in resolver.url_patterns:
        pattern_str = str(pattern.pattern)
        if 'job' in pattern_str:
            print(f"Found: {pattern_str}")
    
    print("\n=== Starting server ===")
    execute_from_command_line(['manage.py', 'runserver'])