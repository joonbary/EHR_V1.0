import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import resolve
from django.urls.exceptions import Resolver404

urls_to_test = [
    '/evaluations/',
    '/evaluations/my-evaluations/',
    '/evaluations/evaluator/',
    '/evaluations/test-my-evaluations/',
]

print("=== URL Resolution Test ===")
for url in urls_to_test:
    try:
        match = resolve(url)
        print(f"\nURL: {url}")
        print(f"  View: {match.func.__name__}")
        print(f"  Module: {match.func.__module__}")
        print(f"  URL Name: {match.url_name}")
        print(f"  App Name: {match.app_name}")
    except Resolver404:
        print(f"\nURL: {url} - NOT FOUND")