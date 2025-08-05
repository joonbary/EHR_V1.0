import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import get_resolver, reverse
from django.urls.resolvers import URLPattern, URLResolver

def show_urls(urllist, depth=0):
    for entry in urllist:
        if isinstance(entry, URLResolver):
            if entry.namespace == 'job_profiles':
                print(" " * depth, f"Namespace: {entry.namespace}, Pattern: {entry.pattern}")
                show_urls(entry.url_patterns, depth + 2)
        elif isinstance(entry, URLPattern):
            if hasattr(entry, 'name') and entry.name:
                print(" " * depth, f"Name: {entry.name}, Pattern: {entry.pattern}")

resolver = get_resolver()
print("=== Job Profiles URLs ===")
show_urls(resolver.url_patterns)

# 직접 URL 확인
try:
    print("\n=== URL Reverse Test ===")
    print("job_profiles:list ->", reverse('job_profiles:list'))
    print("job_profiles:admin_list ->", reverse('job_profiles:admin_list'))
except Exception as e:
    print(f"Error: {e}")

# forms.py가 import 되는지 확인
try:
    from job_profiles.forms import JobProfileForm
    print("\nForms import: OK")
except Exception as e:
    print(f"\nForms import error: {e}")