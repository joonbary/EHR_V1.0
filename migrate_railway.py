#!/usr/bin/env python
"""
Railway 프로덕션 환경에서 마이그레이션 실행 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """마이그레이션 실행"""
    print("=" * 50)
    print("Railway 마이그레이션 시작")
    print("=" * 50)
    
    # 마이그레이션 상태 확인
    print("\n현재 마이그레이션 상태:")
    execute_from_command_line(['manage.py', 'showmigrations'])
    
    # 마이그레이션 실행
    print("\n마이그레이션 실행 중...")
    execute_from_command_line(['manage.py', 'migrate', '--verbosity', '2'])
    
    print("\n=" * 50)
    print("마이그레이션 완료!")
    print("=" * 50)

if __name__ == '__main__':
    main()