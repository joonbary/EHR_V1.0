#!/usr/bin/env python
"""
Railway 전용 안전 마이그레이션 스크립트
기존 데이터를 보존하면서 마이그레이션만 실행
"""
import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def check_table_exists(table_name):
    """테이블이 존재하는지 확인"""
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = %s
                )
            """, [table_name])
            return cursor.fetchone()[0]
    return False

def safe_migrate():
    """데이터를 보존하면서 안전하게 마이그레이션"""
    print("\n" + "=" * 60)
    print("Railway 안전 마이그레이션 시작")
    print("=" * 60)
    
    # django_migrations 테이블 확인
    if not check_table_exists('django_migrations'):
        print("새로운 데이터베이스입니다. 전체 마이그레이션을 실행합니다.")
        call_command('migrate', '--skip-checks', verbosity=1)
    else:
        print("기존 데이터베이스입니다. 새로운 마이그레이션만 적용합니다.")
        # 기존 데이터를 보존하면서 마이그레이션
        call_command('migrate', '--skip-checks', verbosity=1)
    
    # 데이터 수 확인
    from employees.models import Employee
    employee_count = Employee.objects.count()
    print(f"\n현재 직원 수: {employee_count}명")
    
    if employee_count == 0:
        print("직원 데이터가 없습니다. load_ok_employees.py를 실행합니다.")
    
    print("\n" + "=" * 60)
    print("Railway 안전 마이그레이션 완료!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        success = safe_migrate()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)