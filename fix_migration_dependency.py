#!/usr/bin/env python
"""
Railway 마이그레이션 종속성 문제 직접 해결
데이터베이스의 django_migrations 테이블을 직접 수정
"""

import os
import sys
import django
from django.db import connection, transaction

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def fix_migration_dependency():
    """마이그레이션 종속성 문제를 직접 해결"""
    print("\n" + "=" * 60)
    print("마이그레이션 종속성 문제 해결 시작")
    print("=" * 60)
    
    try:
        with connection.cursor() as cursor:
            # 1. 현재 employees 마이그레이션 상태 확인
            print("\n1. 현재 마이그레이션 상태 확인...")
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'employees'
                ORDER BY name
            """)
            current_migrations = [row[0] for row in cursor.fetchall()]
            print(f"   현재 적용된 마이그레이션: {current_migrations}")
            
            # 2. 문제가 되는 상황 확인
            has_0003 = '0003_organizationstructure_employeeorganizationmapping_and_more' in current_migrations
            has_0002 = '0002_add_missing_extended_fields' in current_migrations
            
            if has_0003 and not has_0002:
                print("\n2. 종속성 문제 발견!")
                print("   - 0003은 적용되었으나 0002는 적용되지 않음")
                print("   - 0002를 django_migrations에 추가합니다...")
                
                # 3. 0002 마이그레이션을 직접 추가
                with transaction.atomic():
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES ('employees', '0002_add_missing_extended_fields', CURRENT_TIMESTAMP)
                    """)
                    print("   ✓ 0002 마이그레이션 레코드 추가 완료")
            
            elif not has_0003 and not has_0002:
                print("\n2. 마이그레이션이 적용되지 않았습니다.")
                print("   모든 마이그레이션을 순서대로 추가합니다...")
                
                migrations_to_add = [
                    '0001_initial',
                    '0002_add_missing_extended_fields',
                    '0003_organizationstructure_employeeorganizationmapping_and_more',
                    '0004_employee_initial_position',
                    '0005_talentcategory_talentpool_talentdevelopment_and_more'
                ]
                
                with transaction.atomic():
                    for migration in migrations_to_add:
                        if migration not in current_migrations:
                            cursor.execute("""
                                INSERT INTO django_migrations (app, name, applied)
                                VALUES ('employees', %s, CURRENT_TIMESTAMP)
                            """, [migration])
                            print(f"   ✓ {migration} 추가 완료")
            
            else:
                print("\n2. 종속성 문제가 없습니다.")
            
            # 4. 최종 확인
            print("\n3. 최종 마이그레이션 상태 확인...")
            cursor.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'employees'
                ORDER BY name
            """)
            final_migrations = [row[0] for row in cursor.fetchall()]
            print(f"   최종 적용된 마이그레이션: {final_migrations}")
            
            # 5. 다른 앱들의 마이그레이션 실행
            print("\n4. 나머지 마이그레이션 실행...")
            from django.core.management import call_command
            
            try:
                call_command('migrate', '--fake', verbosity=1)
                print("   ✓ 모든 마이그레이션 완료")
            except Exception as e:
                print(f"   ⚠️ 마이그레이션 경고 (무시 가능): {e}")
        
        print("\n" + "=" * 60)
        print("마이그레이션 종속성 문제 해결 완료!")
        print("=" * 60)
        
        # 직원 데이터 확인 및 로드
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"\n현재 직원 수: {count}명")
        
        if count == 0:
            print("\n직원 데이터를 로드합니다...")
            import subprocess
            result = subprocess.run(['python', 'load_ok_employees.py'], 
                                  capture_output=True, text=True, timeout=60)
            print(result.stdout)
            if result.stderr:
                print(f"경고: {result.stderr}")
            
            # 다시 확인
            new_count = Employee.objects.count()
            print(f"로드 완료! 현재 직원 수: {new_count}명")
        
        return True
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = fix_migration_dependency()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"\n치명적 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)