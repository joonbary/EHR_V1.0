#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway 데이터베이스 완전 리셋 스크립트
"""

import os
import sys
import django
from django.core.management import call_command
from django.db import connection

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def reset_database():
    """데이터베이스 완전 리셋"""
    print("=" * 50)
    print("Railway Database Reset Starting")
    print("=" * 50)
    
    with connection.cursor() as cursor:
        # 모든 테이블 삭제 (CASCADE로 의존성 해결)
        cursor.execute("""
            DO $$ 
            DECLARE 
                r RECORD;
            BEGIN
                -- 모든 테이블 삭제
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    RAISE NOTICE 'Dropped table: %', r.tablename;
                END LOOP;
            END $$;
        """)
        print("OK: All tables dropped")
        
    print("\nRunning migrations...")
    
    # 마이그레이션 실행 (순서대로)
    try:
        # 기본 Django 앱 먼저
        call_command('migrate', 'contenttypes', verbosity=1)
        call_command('migrate', 'auth', verbosity=1)
        call_command('migrate', 'admin', verbosity=1)
        call_command('migrate', 'sessions', verbosity=1)
        
        # employees 먼저 마이그레이션 (다른 앱들이 의존)
        call_command('migrate', 'employees', verbosity=1)
        
        # 나머지 앱들
        call_command('migrate', verbosity=1)
        
        # sync unmigrated apps
        call_command('migrate', '--run-syncdb', verbosity=1)
        
        print("OK: Migrations completed")
    except Exception as e:
        print(f"ERROR: Migration failed - {e}")
        return False
    
    print("\nCreating superuser...")
    
    # 슈퍼유저 생성
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@okfg.com',
            password='admin123!@#'
        )
        print("OK: Superuser created (admin / admin123!@#)")
    
    print("\n" + "=" * 50)
    print("Database Reset Complete!")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    
    print("\nWARNING: This will delete all data!")
    confirm = input("Continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Operation cancelled.")