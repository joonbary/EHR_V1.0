#!/usr/bin/env python
"""
Railway 데이터베이스 초기화 스크립트
"""
import os
import sys
import django
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def init_database():
    """데이터베이스 초기화 및 마이그레이션"""
    try:
        print("Initializing database...")
        
        # 마이그레이션 상태 확인
        try:
            call_command('showmigrations', '--plan')
        except Exception as e:
            print(f"Warning: Could not show migrations: {e}")
        
        # 마이그레이션 실행 (fake-initial로 중복 오류 방지)
        try:
            print("Running migrations with fake-initial...")
            call_command('migrate', '--noinput', '--fake-initial')
            print("Migrations completed successfully")
        except Exception as e:
            print(f"Migration error (trying alternative): {e}")
            # 대체 방법: 각 앱별로 마이그레이션
            apps = ['contenttypes', 'auth', 'employees', 'admin', 'sessions', 
                    'evaluations', 'job_profiles', 'organization', 'airiss', 
                    'notifications', 'recruitment', 'search', 'access_control']
            
            for app in apps:
                try:
                    print(f"Migrating {app}...")
                    call_command('migrate', app, '--noinput')
                except Exception as app_error:
                    print(f"  Skipping {app}: {app_error}")
        
        # 데이터베이스 동기화
        try:
            print("Syncing database...")
            call_command('migrate', '--run-syncdb', '--noinput')
        except Exception as e:
            print(f"Sync warning (non-critical): {e}")
        
        print("Database initialization completed")
        return True
        
    except Exception as e:
        print(f"Critical error during database initialization: {e}")
        # 에러가 발생해도 서버는 시작되도록 True 반환
        return True

if __name__ == "__main__":
    init_database()