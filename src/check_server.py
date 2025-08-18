import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import reverse, resolve
from django.urls.exceptions import NoReverseMatch, Resolver404

print("=== Django URL Configuration Check ===\n")

# Check if job-profiles URL exists
test_urls = [
    '/job-profiles/',
    '/job-profiles/test/',
    '/employees/',
    '/'
]

for url in test_urls:
    try:
        match = resolve(url)
        print(f"[OK] {url} -> {match.view_name}")
    except Resolver404:
        print(f"[FAIL] {url} -> NOT FOUND")

print("\n=== Reverse URL Check ===")
try:
    print(f"job_profiles:list -> {reverse('job_profiles:list')}")
    print(f"job_profiles:test -> {reverse('job_profiles:test')}")
except NoReverseMatch as e:
    print(f"Error: {e}")

# Check installed apps
from django.conf import settings
print("\n=== Job Profiles in INSTALLED_APPS ===")
print('job_profiles' in settings.INSTALLED_APPS)