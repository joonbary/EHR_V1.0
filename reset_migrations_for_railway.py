#!/usr/bin/env python
"""
Railway 배포를 위한 마이그레이션 리셋 스크립트
모든 마이그레이션 파일을 삭제하고 새로 생성합니다.
"""

import os
import shutil
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
import django
django.setup()

def reset_migrations():
    """모든 앱의 마이그레이션 파일을 리셋합니다."""
    
    # 마이그레이션을 리셋할 앱 목록
    apps_to_reset = [
        'employees',
        'organization', 
        'evaluations',
        'notifications',
        'compensation',
        'job_profiles',
        'permissions',
        'promotions',
        'reports',
        'selfservice',
        'certifications',
        'ai_insights',
        'ai_predictions',
        'ai_coaching',
        'ai_interviewer',
        'ai_team_optimizer',
        'airiss'
    ]
    
    print("1. 기존 마이그레이션 파일 삭제 중...")
    for app in apps_to_reset:
        migrations_dir = os.path.join(app, 'migrations')
        if os.path.exists(migrations_dir):
            # __pycache__ 디렉토리 삭제
            pycache_dir = os.path.join(migrations_dir, '__pycache__')
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir)
                print(f"   - {app}/__pycache__ 삭제됨")
            
            # 마이그레이션 파일 삭제 (__init__.py 제외)
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
                    print(f"   - {app}/{filename} 삭제됨")
            
            # __init__.py 파일이 없으면 생성
            init_file = os.path.join(migrations_dir, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'a').close()
                print(f"   - {app}/__init__.py 생성됨")
    
    print("\n2. 새로운 마이그레이션 파일 생성 중...")
    from django.core.management import call_command
    
    # 각 앱별로 마이그레이션 생성
    for app in apps_to_reset:
        try:
            call_command('makemigrations', app, verbosity=0)
            print(f"   ✓ {app} 마이그레이션 생성됨")
        except Exception as e:
            print(f"   ✗ {app} 마이그레이션 실패: {e}")
    
    print("\n✅ 마이그레이션 리셋 완료!")
    print("\n다음 명령어로 마이그레이션을 적용하세요:")
    print("   python manage.py migrate")

if __name__ == '__main__':
    reset_migrations()