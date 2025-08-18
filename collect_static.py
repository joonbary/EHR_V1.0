#!/usr/bin/env python
"""
Static 파일 수집 스크립트
Railway 배포 환경에서 static 파일 업데이트 확인
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.core.management import call_command

print("=" * 60)
print("Static 파일 수집 중...")
print("=" * 60)

try:
    # collectstatic 명령 실행
    call_command('collectstatic', '--noinput', '--clear')
    print("\n✅ Static 파일 수집 완료!")
    
    # static 파일 확인
    from django.conf import settings
    import os
    
    js_file = os.path.join(settings.STATIC_ROOT or 'staticfiles', 'js', 'job_tree_unified.js')
    if os.path.exists(js_file):
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if '/job-profiles/api/tree-map-data/' in content:
                print("✅ JavaScript 파일이 올바르게 업데이트되었습니다.")
            else:
                print("⚠️ JavaScript 파일이 이전 버전입니다.")
                print("   API URL을 확인하세요.")
    else:
        print("⚠️ JavaScript 파일을 찾을 수 없습니다.")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("=" * 60)