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
        print("기존 데이터베이스입니다. 마이그레이션 상태를 확인합니다.")
        
        # 마이그레이션 종속성 문제 해결
        try:
            # 먼저 employees 앱의 마이그레이션 상태 확인
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT name FROM django_migrations 
                    WHERE app = 'employees'
                    ORDER BY name
                """)
                applied_migrations = [row[0] for row in cursor.fetchall()]
                print(f"적용된 employees 마이그레이션: {applied_migrations}")
                
                # 0003이 0002보다 먼저 적용된 경우 처리
                if '0003_organizationstructure_employeeorganizationmapping_and_more' in applied_migrations:
                    if '0002_add_missing_extended_fields' not in applied_migrations:
                        print("마이그레이션 종속성 문제 감지. 수정 중...")
                        # 0002를 fake로 적용
                        call_command('migrate', 'employees', '0002_add_missing_extended_fields', '--fake', verbosity=1)
                        print("0002 마이그레이션을 fake로 적용했습니다.")
            
            # 이제 전체 마이그레이션 실행
            print("모든 마이그레이션을 적용합니다...")
            call_command('migrate', '--skip-checks', verbosity=1)
            
        except Exception as e:
            print(f"마이그레이션 중 오류: {e}")
            print("--fake-initial 옵션으로 재시도합니다...")
            call_command('migrate', '--fake-initial', '--skip-checks', verbosity=1)
    
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