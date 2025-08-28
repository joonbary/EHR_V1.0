#!/usr/bin/env python
"""
Railway 배포 후 강제 재시작 스크립트
URL 패턴이 제대로 로드되지 않을 때 사용
"""
import os
import sys
import django

# Django 설정 로드
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

# URL 패턴 재로드
from django.urls import clear_url_caches
from django.core.management import call_command

print("=" * 60)
print("Force Restart Script")
print("=" * 60)

# URL 캐시 클리어
print("1. Clearing URL caches...")
clear_url_caches()

# 시스템 체크
print("2. Running system checks...")
call_command('check', '--deploy')

# URL 패턴 확인
print("3. Verifying URL patterns...")
from employees import urls as employees_urls
url_count = len(employees_urls.urlpatterns)
print(f"   - Found {url_count} URL patterns in employees app")

# 특정 URL 확인
from django.urls import reverse
try:
    advanced_org_chart_url = reverse('employees:advanced_organization_chart')
    print(f"   ✓ Advanced org chart URL: {advanced_org_chart_url}")
except:
    print("   ✗ Advanced org chart URL not found!")

try:
    org_tree_api_url = reverse('employees:org_tree_api')
    print(f"   ✓ Org tree API URL: {org_tree_api_url}")
except:
    print("   ✗ Org tree API URL not found!")

print("=" * 60)
print("Restart complete!")
print("=" * 60)