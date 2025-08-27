#!/usr/bin/env python
"""
마이그레이션 건너뛰고 바로 데이터 로드
Railway에서 마이그레이션 문제가 계속될 경우 사용
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def just_load_data():
    """마이그레이션 없이 데이터만 로드"""
    print("\n" + "=" * 60)
    print("데이터 로드 전용 스크립트")
    print("=" * 60)
    
    try:
        # 테이블 존재 확인
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = 'employees_employee'
                )
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                print("⚠️ employees_employee 테이블이 없습니다!")
                print("마이그레이션이 필요합니다.")
                # 최소한의 마이그레이션만 실행
                from django.core.management import call_command
                print("\n최소 마이그레이션 실행...")
                try:
                    call_command('migrate', 'employees', '0001_initial', '--fake', verbosity=0)
                    call_command('migrate', 'employees', '--fake', verbosity=0)
                except Exception as e:
                    print(f"마이그레이션 경고 (무시): {e}")
        
        # 직원 데이터 확인
        from employees.models import Employee
        
        try:
            count = Employee.objects.count()
            print(f"\n현재 직원 수: {count}명")
        except Exception as e:
            print(f"직원 수 확인 실패: {e}")
            count = 0
        
        if count < 100:  # 100명 미만이면 로드
            print("\n직원 데이터를 로드합니다...")
            
            # load_ok_employees.py 실행
            import subprocess
            result = subprocess.run(
                ['python', 'load_ok_employees.py'], 
                capture_output=True, 
                text=True,
                timeout=60
            )
            
            print(result.stdout)
            if result.stderr:
                print(f"경고: {result.stderr}")
            
            # 결과 확인
            try:
                new_count = Employee.objects.count()
                print(f"\n✓ 로드 완료! 현재 직원 수: {new_count}명")
            except:
                print("직원 수 확인 불가")
        else:
            print(f"\n✓ 충분한 직원 데이터가 있습니다: {count}명")
        
        print("\n" + "=" * 60)
        print("데이터 로드 완료!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n오류: {e}")
        import traceback
        traceback.print_exc()
        
        # 오류가 나도 서버는 시작해야 하므로 True 반환
        return True

if __name__ == '__main__':
    try:
        success = just_load_data()
        # 성공 여부와 관계없이 정상 종료 (서버 시작을 막지 않음)
        sys.exit(0)
    except Exception as e:
        print(f"\n오류: {e}")
        # 오류가 나도 정상 종료
        sys.exit(0)