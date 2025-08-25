#!/usr/bin/env python
"""
Railway 최종 점검 - API 500 오류 원인 파악
"""

import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 최종 점검")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def check_api_error():
    """API 오류 원인 파악"""
    print("1. API 오류 상세 확인")
    print("-" * 40)
    
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    
    factory = RequestFactory()
    
    # Mock request
    request = factory.get('/employees/api/organization-stats/')
    
    # Mock user (optional)
    try:
        user = User.objects.first()
        if user:
            request.user = user
    except:
        pass
    
    # API 함수 직접 호출
    try:
        from employees.views import get_organization_stats
        
        print("get_organization_stats 함수 호출 중...")
        response = get_organization_stats(request)
        
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 500:
            print("\n[ERROR] 500 오류 발생")
            print("응답 내용:")
            print(response.content.decode('utf-8'))
        elif response.status_code == 200:
            print("[SUCCESS] API 정상 작동")
            import json
            data = json.loads(response.content)
            for key, value in data.items():
                print(f"  - {key}: {value}")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] API 호출 실패:")
        print(f"에러 타입: {type(e).__name__}")
        print(f"에러 메시지: {str(e)}")
        print("\n상세 스택 트레이스:")
        traceback.print_exc()
        
        # 구체적인 원인 분석
        error_msg = str(e).lower()
        if 'employment_status' in error_msg:
            print("\n[원인] Employee 모델에 employment_status 필드 없음")
            print("[해결] employment_status 필드 추가 필요")
        elif 'updated_at' in error_msg:
            print("\n[원인] OrganizationStructure 모델에 updated_at 필드 없음")
            print("[해결] updated_at 필드 추가 필요")
        elif 'does not exist' in error_msg:
            print("\n[원인] 테이블 또는 필드가 존재하지 않음")
            print("[해결] 마이그레이션 실행 필요")

def check_models():
    """모델 필드 확인"""
    print("\n2. 모델 필드 확인")
    print("-" * 40)
    
    try:
        from employees.models import Employee
        from employees.models_organization import OrganizationStructure
        
        # Employee 필드
        print("Employee 모델 필드:")
        emp_fields = [f.name for f in Employee._meta.get_fields()]
        if 'employment_status' in emp_fields:
            print("  [OK] employment_status 필드 존재")
        else:
            print("  [ERROR] employment_status 필드 없음")
        
        # OrganizationStructure 필드
        print("\nOrganizationStructure 모델 필드:")
        org_fields = [f.name for f in OrganizationStructure._meta.get_fields()]
        if 'updated_at' in org_fields:
            print("  [OK] updated_at 필드 존재")
        else:
            print("  [ERROR] updated_at 필드 없음")
        
        # 실제 쿼리 테스트
        print("\n실제 쿼리 테스트:")
        
        # 1. OrganizationStructure count
        try:
            count = OrganizationStructure.objects.count()
            print(f"  [OK] OrganizationStructure 카운트: {count}")
        except Exception as e:
            print(f"  [ERROR] OrganizationStructure 쿼리 실패: {e}")
        
        # 2. Active orgs
        try:
            active = OrganizationStructure.objects.filter(status='active').count()
            print(f"  [OK] Active 조직: {active}")
        except Exception as e:
            print(f"  [ERROR] Active 조직 쿼리 실패: {e}")
        
        # 3. Employee count
        try:
            emp_count = Employee.objects.filter(employment_status='재직').count()
            print(f"  [OK] 재직 직원: {emp_count}")
        except Exception as e:
            print(f"  [ERROR] 재직 직원 쿼리 실패: {e}")
            # Fallback
            try:
                emp_count = Employee.objects.count()
                print(f"  [OK] 전체 직원 (fallback): {emp_count}")
            except Exception as e2:
                print(f"  [ERROR] 전체 직원 쿼리도 실패: {e2}")
        
        # 4. Last update
        try:
            last_org = OrganizationStructure.objects.order_by('-updated_at').first()
            if last_org:
                print(f"  [OK] 최종 업데이트: {last_org.updated_at}")
            else:
                print("  [INFO] 조직 데이터 없음")
        except Exception as e:
            print(f"  [ERROR] 최종 업데이트 쿼리 실패: {e}")
            
    except Exception as e:
        print(f"[ERROR] 모델 import 실패: {e}")
        traceback.print_exc()

def fix_missing_fields():
    """누락된 필드 수정"""
    print("\n3. 누락된 필드 자동 수정")
    print("-" * 40)
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Employee.employment_status 필드
        try:
            cursor.execute("""
                ALTER TABLE employees_employee 
                ADD COLUMN IF NOT EXISTS employment_status VARCHAR(20) DEFAULT '재직';
            """)
            print("[OK] employment_status 필드 추가/확인")
        except Exception as e:
            print(f"[INFO] employment_status: {str(e)[:50]}")
        
        # OrganizationStructure.updated_at 필드
        try:
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """)
            print("[OK] updated_at 필드 추가/확인")
        except Exception as e:
            print(f"[INFO] updated_at: {str(e)[:50]}")
        
        # 기본값 설정
        cursor.execute("""
            UPDATE employees_employee 
            SET employment_status = '재직' 
            WHERE employment_status IS NULL;
        """)
        
        cursor.execute("""
            UPDATE employees_organizationstructure 
            SET updated_at = CURRENT_TIMESTAMP 
            WHERE updated_at IS NULL;
        """)
        print("[OK] 기본값 설정 완료")

def main():
    """메인 실행"""
    
    print("\n시작: Railway 최종 점검\n")
    
    # 1. 누락된 필드 수정
    fix_missing_fields()
    
    # 2. 모델 확인
    check_models()
    
    # 3. API 테스트
    check_api_error()
    
    print("\n" + "="*60)
    print("점검 완료")
    print("="*60)
    print("\n권장 사항:")
    print("1. railway restart - 서버 재시작")
    print("2. 브라우저 캐시 삭제 후 재접속")
    print("3. https://ehrv10-production.up.railway.app/employees/organization/structure/")

if __name__ == "__main__":
    main()