#!/usr/bin/env python
"""
Railway API 오류 상세 디버깅
"""

import os
import sys
import django
import json
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway API 디버깅")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def test_organization_stats():
    """organization-stats API 테스트"""
    print("1. Organization Stats API (500 오류)")
    print("-" * 40)
    
    try:
        from employees.views import get_organization_stats
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        factory = RequestFactory()
        request = factory.get('/employees/api/organization-stats/')
        
        # Mock user
        try:
            user = User.objects.first()
            if user:
                request.user = user
        except:
            pass
        
        print("API 호출 시도...")
        response = get_organization_stats(request)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 500:
            content = response.content.decode('utf-8')
            print(f"\n[ERROR] 500 오류 내용:")
            print(content)
            
            # JSON 파싱 시도
            try:
                error_data = json.loads(content)
                if 'error' in error_data:
                    print(f"\n오류 메시지: {error_data['error']}")
            except:
                pass
        elif response.status_code == 200:
            data = json.loads(response.content)
            print("[SUCCESS] API 정상")
            print(f"데이터: {data}")
            
    except Exception as e:
        print(f"\n[EXCEPTION] API 호출 중 예외:")
        print(f"타입: {type(e).__name__}")
        print(f"메시지: {str(e)}")
        print("\n스택 트레이스:")
        traceback.print_exc()
        
        # 구체적 원인 분석
        analyze_error(str(e))

def test_upload_api():
    """upload-organization-structure API 테스트"""
    print("\n2. Upload Organization API (400 오류)")
    print("-" * 40)
    
    try:
        from employees.views import upload_organization_structure
        from employees.models_organization import OrganizationStructure
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        factory = RequestFactory()
        
        # 테스트 데이터
        test_data = {
            'data': [
                {
                    '조직코드': 'TEST001',
                    '조직명': '테스트조직',
                    '조직레벨': 3,
                    '상위조직코드': 'COM001',  # 존재하는 상위 조직
                    '상태': 'active',
                    '정렬순서': 999,
                    '설명': '테스트'
                }
            ]
        }
        
        print(f"테스트 데이터: {test_data}")
        
        request = factory.post(
            '/employees/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Mock user
        try:
            user = User.objects.first()
            if user:
                request.user = user
        except:
            pass
        
        request._dont_enforce_csrf_checks = True
        
        print("\nAPI 호출 시도...")
        response = upload_organization_structure(request)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 400:
            content = response.content.decode('utf-8')
            print(f"\n[ERROR] 400 오류 내용:")
            print(content)
            
            # JSON 파싱
            try:
                error_data = json.loads(content)
                if 'error' in error_data:
                    print(f"\n오류 메시지: {error_data['error']}")
                if 'errors' in error_data:
                    print("상세 오류:")
                    for err in error_data['errors'][:5]:
                        print(f"  - {err}")
            except:
                pass
        elif response.status_code == 200:
            data = json.loads(response.content)
            print("[SUCCESS] API 정상")
            print(f"결과: {data}")
            
    except Exception as e:
        print(f"\n[EXCEPTION] API 호출 중 예외:")
        print(f"타입: {type(e).__name__}")
        print(f"메시지: {str(e)}")
        print("\n스택 트레이스:")
        traceback.print_exc()
        
        analyze_error(str(e))

def check_database_state():
    """데이터베이스 상태 확인"""
    print("\n3. 데이터베이스 상태")
    print("-" * 40)
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # 테이블 존재 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'employees_employee',
                'employees_organizationstructure',
                'employees_organizationuploadhistory',
                'employees_employeeorganizationmapping'
            )
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("필수 테이블:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {table_name}: {count} 레코드")
        
        # OrganizationStructure 데이터 확인
        cursor.execute("""
            SELECT org_code, org_name, org_level 
            FROM employees_organizationstructure 
            ORDER BY org_level, sort_order 
            LIMIT 10;
        """)
        orgs = cursor.fetchall()
        
        if orgs:
            print("\n현재 조직:")
            for org in orgs:
                print(f"  레벨{org[2]}: {org[0]} - {org[1]}")
        else:
            print("\n[WARNING] 조직 데이터 없음")

def check_model_fields():
    """모델 필드 확인"""
    print("\n4. 모델 필드 확인")
    print("-" * 40)
    
    try:
        from employees.models import Employee
        from employees.models_organization import OrganizationStructure
        
        # Employee 필드
        emp_fields = [f.name for f in Employee._meta.get_fields()]
        print("Employee 필드:")
        if 'employment_status' in emp_fields:
            print("  ✓ employment_status")
        else:
            print("  ✗ employment_status (없음!)")
        
        # OrganizationStructure 필드
        org_fields = [f.name for f in OrganizationStructure._meta.get_fields()]
        print("\nOrganizationStructure 필드:")
        if 'updated_at' in org_fields:
            print("  ✓ updated_at")
        else:
            print("  ✗ updated_at (없음!)")
        
        # 실제 쿼리 가능 여부
        print("\n쿼리 테스트:")
        
        try:
            # 전체 조직 수
            total = OrganizationStructure.objects.count()
            print(f"  ✓ 전체 조직: {total}")
        except Exception as e:
            print(f"  ✗ 전체 조직 쿼리 실패: {e}")
        
        try:
            # 활성 조직 수
            active = OrganizationStructure.objects.filter(status='active').count()
            print(f"  ✓ 활성 조직: {active}")
        except Exception as e:
            print(f"  ✗ 활성 조직 쿼리 실패: {e}")
        
        try:
            # 재직 직원 수
            employees = Employee.objects.filter(employment_status='재직').count()
            print(f"  ✓ 재직 직원: {employees}")
        except Exception as e:
            print(f"  ✗ 재직 직원 쿼리 실패: {e}")
            # Fallback
            try:
                employees = Employee.objects.count()
                print(f"  ✓ 전체 직원 (fallback): {employees}")
            except:
                print(f"  ✗ 전체 직원 쿼리도 실패")
        
        try:
            # 최종 업데이트
            last = OrganizationStructure.objects.order_by('-updated_at').first()
            if last:
                print(f"  ✓ 최종 업데이트: {last.updated_at}")
        except Exception as e:
            print(f"  ✗ 최종 업데이트 쿼리 실패: {e}")
            
    except Exception as e:
        print(f"[ERROR] 모델 확인 실패: {e}")

def analyze_error(error_msg):
    """오류 메시지 분석"""
    error_lower = error_msg.lower()
    
    print("\n[원인 분석]")
    if 'employment_status' in error_lower:
        print("- Employee 테이블에 employment_status 필드 없음")
        print("- 해결: ALTER TABLE employees_employee ADD COLUMN employment_status VARCHAR(20) DEFAULT '재직';")
    elif 'updated_at' in error_lower:
        print("- OrganizationStructure 테이블에 updated_at 필드 없음")
        print("- 해결: ALTER TABLE employees_organizationstructure ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")
    elif 'does not exist' in error_lower:
        print("- 테이블 또는 필드가 존재하지 않음")
        print("- 해결: 마이그레이션 실행 또는 테이블 재생성")
    elif 'null' in error_lower:
        print("- NULL 값 관련 오류")
        print("- 해결: 기본값 설정 또는 NULL 체크 추가")
    else:
        print("- 알 수 없는 오류")
        print("- 전체 스택 트레이스 확인 필요")

def main():
    """메인 실행"""
    
    print("\n시작: Railway API 상세 디버깅\n")
    
    # 1. 데이터베이스 상태
    check_database_state()
    
    # 2. 모델 필드 확인
    check_model_fields()
    
    # 3. Stats API 테스트
    test_organization_stats()
    
    # 4. Upload API 테스트
    test_upload_api()
    
    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)
    print("\n권장 조치:")
    print("1. 위 오류 메시지 확인")
    print("2. 필요한 필드 추가")
    print("3. railway restart")

if __name__ == "__main__":
    main()