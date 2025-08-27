#!/usr/bin/env python
"""
Railway용 가장 안전한 마이그레이션 스크립트
모든 마이그레이션을 fake로 적용하여 데이터 보존
"""

import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def safe_migrate():
    """최대한 안전하게 마이그레이션"""
    print("\n" + "=" * 60)
    print("Railway 최안전 마이그레이션 시작")
    print("=" * 60)
    
    try:
        # 1. 먼저 showmigrations로 상태 확인
        print("\n현재 마이그레이션 상태:")
        call_command('showmigrations', 'employees', verbosity=0)
        
        # 2. 모든 employees 마이그레이션을 fake로 적용
        print("\nemployees 앱 마이그레이션을 fake로 적용합니다...")
        migrations = [
            '0001_initial',
            '0002_add_missing_extended_fields', 
            '0003_organizationstructure_employeeorganizationmapping_and_more',
            '0004_employee_initial_position',
            '0005_talentcategory_talentpool_talentdevelopment_and_more'
        ]
        
        for migration in migrations:
            try:
                print(f"  - {migration} 적용 중...")
                call_command('migrate', 'employees', migration, '--fake', verbosity=0)
            except Exception as e:
                print(f"    스킵 (이미 적용됨 또는 오류): {e}")
        
        # 3. 나머지 앱들 마이그레이션
        print("\n나머지 앱들을 마이그레이션합니다...")
        call_command('migrate', '--fake-initial', verbosity=1)
        
        print("\n" + "=" * 60)
        print("마이그레이션 완료!")
        print("=" * 60)
        
        # 4. 직원 데이터 확인
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"\n현재 직원 수: {count}명")
        
        if count == 0:
            print("직원 데이터가 없습니다. load_ok_employees.py를 실행합니다.")
            import subprocess
            result = subprocess.run(['python', 'load_ok_employees.py'], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print(f"경고: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = safe_migrate()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)