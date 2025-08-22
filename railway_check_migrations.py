#!/usr/bin/env python
"""
Railway 마이그레이션 상태 확인 및 강제 실행
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 마이그레이션 체크")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.core.management import call_command
from django.db import connection

def check_migration_status():
    """마이그레이션 상태 확인"""
    print("1. 마이그레이션 상태 확인")
    print("-" * 40)
    
    try:
        # showmigrations 명령 실행
        call_command('showmigrations', 'employees')
    except Exception as e:
        print(f"[ERROR] 마이그레이션 상태 확인 실패: {e}")
        return False
    
    return True

def force_migrate():
    """강제 마이그레이션 실행"""
    print("\n2. 마이그레이션 강제 실행")
    print("-" * 40)
    
    try:
        # 특정 마이그레이션 파일 실행
        migrations = [
            '0001_initial',
            '0002_add_missing_extended_fields',
            '0003_organizationstructure_employeeorganizationmapping_and_more',
            '0004_employee_initial_position'
        ]
        
        for migration in migrations:
            print(f"\n[실행] employees {migration}")
            try:
                call_command('migrate', 'employees', migration, verbosity=2)
                print(f"  [OK] {migration} 완료")
            except Exception as e:
                print(f"  [WARNING] {migration} 실패: {str(e)[:100]}")
        
        # 전체 마이그레이션
        print("\n[실행] 전체 마이그레이션")
        call_command('migrate', verbosity=2)
        print("[OK] 전체 마이그레이션 완료")
        
    except Exception as e:
        print(f"[ERROR] 마이그레이션 실패: {e}")
        return False
    
    return True

def verify_tables():
    """테이블 생성 확인"""
    print("\n3. 테이블 생성 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # PostgreSQL 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n생성된 테이블 ({len(tables)}개):")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        # 필수 테이블 체크
        required = [
            'employees_employee',
            'employees_organizationstructure',
            'employees_organizationuploadhistory',
            'employees_employeeorganizationmapping'
        ]
        
        table_names = [t[0] for t in tables]
        missing = []
        
        print("\n필수 테이블 체크:")
        for req in required:
            if req in table_names:
                print(f"  ✓ {req}")
            else:
                print(f"  ✗ {req} - 누락됨!")
                missing.append(req)
        
        if missing:
            print(f"\n[WARNING] {len(missing)}개 테이블 누락")
            return False
        else:
            print("\n[SUCCESS] 모든 필수 테이블 존재")
            return True

def main():
    """메인 실행"""
    
    # 1. 현재 상태 확인
    check_migration_status()
    
    # 2. 강제 마이그레이션
    if force_migrate():
        print("\n[OK] 마이그레이션 성공")
    else:
        print("\n[WARNING] 마이그레이션 일부 실패")
    
    # 3. 테이블 확인
    if verify_tables():
        print("\n" + "="*60)
        print("성공! API가 정상 작동해야 합니다.")
        print("="*60)
        print("\n다음 명령 실행:")
        print("1. railway restart")
        print("2. 브라우저에서 테스트")
    else:
        print("\n" + "="*60)
        print("테이블 생성 실패 - 수동 생성 필요")
        print("="*60)
        print("\n다음 명령 실행:")
        print("1. railway run python railway_create_tables.py")
        print("2. railway restart")

if __name__ == "__main__":
    main()