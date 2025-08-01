import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import get_resolver
from pprint import pprint

# URL 패턴 출력
resolver = get_resolver()

print("=== Evaluations URL Patterns ===")
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'pattern') and 'evaluations' in str(pattern.pattern):
        print(f"Pattern: {pattern.pattern}")
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                print(f"  - {sub_pattern.pattern} -> {sub_pattern.callback}")