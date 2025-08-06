#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Railway 데이터베이스 간단 리셋
"""

import os
import sys
import django
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def main():
    print("Starting simple database setup...")
    
    try:
        # 모든 마이그레이션을 fake로 실행 (테이블이 이미 있다고 가정)
        print("Applying migrations with fake flag...")
        call_command('migrate', '--fake', verbosity=1)
        
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
        else:
            print("Superuser already exists")
        
        # 직무기술서 데이터 로드
        print("\nLoading job profiles data...")
        call_command('load_job_profiles')
        
        print("\nSetup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == '__main__':
    main()