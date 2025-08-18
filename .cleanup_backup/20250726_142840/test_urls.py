import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import reverse

try:
    url = reverse('job_profiles:list')
    print(f"job_profiles:list URL: {url}")
except Exception as e:
    print(f"Error: {e}")

# URL 패턴 직접 확인
from django.urls import get_resolver
resolver = get_resolver()

print("\n=== All URL patterns ===")
for pattern in resolver.url_patterns:
    print(f"{pattern.pattern}")