#!/usr/bin/env python
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

import django
django.setup()

# airiss views 임포트 테스트
try:
    from airiss import views
    print("[OK] airiss.views imported successfully")
    print(f"Views module path: {views.__file__}")
    
    # dashboard 함수 확인
    if hasattr(views, 'dashboard'):
        print("[OK] dashboard function exists")
        print(f"Dashboard function: {views.dashboard}")
    else:
        print("[ERROR] dashboard function NOT found")
        
    # airiss urls 임포트 테스트
    from airiss import urls
    print("\n[OK] airiss.urls imported successfully")
    print(f"URLs module path: {urls.__file__}")
    print(f"URL patterns count: {len(urls.urlpatterns)}")
    
    # URL 패턴 출력
    print("\nURL patterns in airiss:")
    for pattern in urls.urlpatterns[:10]:  # 처음 10개만
        print(f"  - {pattern}")
        
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()