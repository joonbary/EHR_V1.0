#!/usr/bin/env python
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

import django
django.setup()

from django.urls import reverse, resolve

try:
    # URL 리버스 테스트
    url1 = reverse('airiss:dashboard')
    print(f"[OK] airiss:dashboard URL: {url1}")
    
    url2 = reverse('airiss:dashboard_debug_test')
    print(f"[OK] airiss:dashboard_debug_test URL: {url2}")
    
    # URL resolve 테스트
    match1 = resolve('/airiss/')
    print(f"\n[OK] /airiss/ resolves to: {match1.func}")
    print(f"     View name: {match1.view_name}")
    print(f"     App name: {match1.app_name}")
    
    match2 = resolve('/airiss/debug-test/')
    print(f"\n[OK] /airiss/debug-test/ resolves to: {match2.func}")
    print(f"     View name: {match2.view_name}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 전체 URL 패턴 확인
print("\n[INFO] Checking all URL patterns...")
from django.urls import get_resolver
resolver = get_resolver()

# airiss 관련 URL 패턴만 출력
print("\n[INFO] AIRISS related URLs:")
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'pattern'):
        pattern_str = str(pattern.pattern)
        if 'airiss' in pattern_str:
            print(f"  - {pattern_str}")