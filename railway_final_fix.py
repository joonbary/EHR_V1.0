#!/usr/bin/env python
"""
Railway 500 오류 최종 수정 스크립트
모든 알려진 문제를 체계적으로 해결
"""

import os
import sys
import django
import traceback
import json
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 500 오류 최종 수정")
print(f"실행 시간: {datetime.now()}")
print("="*60)

# 환경 감지
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
print(f"\n[환경] {'Railway' if is_railway else 'Local'} 환경에서 실행 중")

try:
    django.setup()
    print("[OK] Django 초기화 성공")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    traceback.print_exc()
    sys.exit(1)

def step1_check_database():
    """Step 1: 데이터베이스 연결 및 테이블 확인"""
    print("\n" + "="*60)
    print("Step 1: 데이터베이스 확인")
    print("="*60)
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            if is_railway:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"[OK] PostgreSQL 연결: {version[0][:50]}...")
                
                # 테이블 확인
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'employees_%'
                    ORDER BY table_name;
                """)
            else:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"[OK] SQLite 연결: {version[0]}")
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'employees_%'
                    ORDER BY name;
                """)
            
            tables = cursor.fetchall()
            print(f"\n[INFO] employees 앱 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 필수 테이블 확인
            required_tables = [
                'employees_employee',
                'employees_organizationstructure',
                'employees_organizationuploadhistory',
                'employees_employeeorganizationmapping'
            ]
            
            table_names = [t[0] for t in tables]
            missing_tables = []
            for req_table in required_tables:
                if req_table not in table_names:
                    missing_tables.append(req_table)
            
            if missing_tables:
                print(f"\n[WARNING] 누락된 테이블:")
                for table in missing_tables:
                    print(f"  - {table}")
                print("\n[ACTION] 마이그레이션 실행 필요")
                return False
            else:
                print("\n[OK] 모든 필수 테이블 존재")
                return True
                
    except Exception as e:
        print(f"\n[ERROR] 데이터베이스 오류: {e}")
        traceback.print_exc()
        return False

def step2_fix_model_imports():
    """Step 2: 모델 import 문제 수정"""
    print("\n" + "="*60)
    print("Step 2: 모델 Import 수정")
    print("="*60)
    
    success = True
    
    # 1. OrganizationStructure 모델
    try:
        from employees.models_organization import OrganizationStructure
        count = OrganizationStructure.objects.count()
        print(f"[OK] OrganizationStructure 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] OrganizationStructure import 실패: {e}")
        success = False
    
    # 2. OrganizationUploadHistory 모델
    try:
        from employees.models_organization import OrganizationUploadHistory
        count = OrganizationUploadHistory.objects.count()
        print(f"[OK] OrganizationUploadHistory 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] OrganizationUploadHistory import 실패: {e}")
        success = False
    
    # 3. EmployeeOrganizationMapping 모델
    try:
        from employees.models_organization import EmployeeOrganizationMapping
        count = EmployeeOrganizationMapping.objects.count()
        print(f"[OK] EmployeeOrganizationMapping 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] EmployeeOrganizationMapping import 실패: {e}")
        success = False
    
    # 4. Employee 모델
    try:
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"[OK] Employee 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] Employee import 실패: {e}")
        success = False
    
    return success

def step3_create_initial_data():
    """Step 3: 초기 데이터 생성"""
    print("\n" + "="*60)
    print("Step 3: 초기 데이터 생성")
    print("="*60)
    
    try:
        from employees.models_organization import OrganizationStructure
        from django.contrib.auth.models import User
        
        # 조직 데이터 확인
        if OrganizationStructure.objects.count() > 0:
            print(f"[INFO] 이미 {OrganizationStructure.objects.count()}개의 조직이 존재합니다")
        else:
            print("[INFO] 초기 조직 데이터 생성 중...")
            
            # 그룹 레벨
            group = OrganizationStructure.objects.create(
                org_code='GRP001',
                org_name='OK금융그룹',
                org_level=1,
                status='active',
                sort_order=1,
                description='OK금융그룹 지주회사'
            )
            print("  [OK] OK금융그룹 생성")
            
            # 계열사 레벨
            company = OrganizationStructure.objects.create(
                org_code='COM001',
                org_name='OK저축은행',
                org_level=2,
                parent=group,
                status='active',
                sort_order=1,
                description='OK저축은행'
            )
            print("  [OK] OK저축은행 생성")
            
            # 본부 레벨
            hq = OrganizationStructure.objects.create(
                org_code='HQ001',
                org_name='리테일본부',
                org_level=3,
                parent=company,
                status='active',
                sort_order=1,
                description='리테일 금융 서비스 본부'
            )
            print("  [OK] 리테일본부 생성")
            
            print("\n[OK] 초기 조직 데이터 생성 완료")
        
        # Admin 사용자 확인
        if not User.objects.filter(username='admin').exists():
            print("\n[INFO] Admin 사용자 생성 중...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("[OK] Admin 사용자 생성 완료 (admin/admin123)")
        else:
            print("[INFO] Admin 사용자가 이미 존재합니다")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 초기 데이터 생성 실패: {e}")
        traceback.print_exc()
        return False

def step4_test_api_endpoints():
    """Step 4: API 엔드포인트 테스트"""
    print("\n" + "="*60)
    print("Step 4: API 엔드포인트 테스트")
    print("="*60)
    
    from django.test import RequestFactory
    from django.contrib.auth.models import User
    
    factory = RequestFactory()
    
    # Mock user for request
    try:
        user = User.objects.first()
    except:
        user = None
    
    success = True
    
    # 1. organization-stats API
    print("\n[테스트] GET /api/organization-stats/")
    try:
        from employees.views import get_organization_stats
        
        request = factory.get('/api/organization-stats/')
        if user:
            request.user = user
        
        response = get_organization_stats(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [OK] API 정상 작동")
            print(f"    - 전체 조직: {data.get('total_orgs', 0)}개")
            print(f"    - 활성 조직: {data.get('active_orgs', 0)}개")
            print(f"    - 전체 직원: {data.get('total_employees', 0)}개")
        else:
            print(f"  [ERROR] 비정상 응답 코드")
            success = False
            
    except Exception as e:
        print(f"  [ERROR] API 호출 실패: {e}")
        traceback.print_exc()
        success = False
    
    # 2. upload-organization-structure API
    print("\n[테스트] POST /api/upload-organization-structure/")
    try:
        from employees.views import upload_organization_structure
        
        test_data = {
            'data': [
                {
                    '조직코드': 'TEST001',
                    '조직명': '테스트조직',
                    '조직레벨': 1,
                    '상위조직코드': None,
                    '상태': 'active',
                    '정렬순서': 999,
                    '설명': '테스트'
                }
            ]
        }
        
        request = factory.post(
            '/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        if user:
            request.user = user
        
        # CSRF 제외 설정
        request._dont_enforce_csrf_checks = True
        
        response = upload_organization_structure(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  [OK] API 정상 작동")
            print(f"    - success: {data.get('success')}")
            print(f"    - created: {data.get('created', 0)}")
            print(f"    - updated: {data.get('updated', 0)}")
        else:
            print(f"  [ERROR] 비정상 응답 코드")
            if response.status_code == 400:
                print(f"  응답 내용: {response.content.decode('utf-8')}")
            success = False
            
    except Exception as e:
        print(f"  [ERROR] API 호출 실패: {e}")
        traceback.print_exc()
        success = False
    
    return success

def step5_generate_solution():
    """Step 5: 해결 방안 제시"""
    print("\n" + "="*60)
    print("Step 5: 해결 방안")
    print("="*60)
    
    if is_railway:
        print("""
Railway 환경에서 다음 명령들을 순서대로 실행하세요:

1. 이 스크립트 실행 (이미 실행됨):
   railway run python railway_final_fix.py

2. 마이그레이션 확인:
   railway run python manage.py showmigrations employees

3. 마이그레이션 실행 (필요시):
   railway run python manage.py migrate

4. 정적 파일 수집:
   railway run python manage.py collectstatic --noinput

5. 서버 재시작:
   railway restart

6. 로그 확인:
   railway logs --tail 100

문제가 지속되면:
- DATABASE_URL 환경변수 확인
- DJANGO_SETTINGS_MODULE이 'ehr_system.settings'인지 확인
- employees 앱이 INSTALLED_APPS에 포함되어 있는지 확인
""")
    else:
        print("""
로컬 환경에서 다음 명령들을 실행하세요:

1. 마이그레이션 실행:
   python manage.py migrate

2. 초기 데이터 생성:
   python railway_final_fix.py

3. 서버 실행:
   python manage.py runserver

4. 브라우저에서 테스트:
   http://localhost:8000/employees/organization-structure/
""")

def main():
    """메인 실행 함수"""
    
    results = {
        'database': False,
        'models': False,
        'data': False,
        'api': False
    }
    
    # Step 1: 데이터베이스 확인
    results['database'] = step1_check_database()
    
    # Step 2: 모델 import 수정
    results['models'] = step2_fix_model_imports()
    
    # Step 3: 초기 데이터 생성
    if results['models']:
        results['data'] = step3_create_initial_data()
    
    # Step 4: API 테스트
    if results['models']:
        results['api'] = step4_test_api_endpoints()
    
    # Step 5: 해결 방안 제시
    step5_generate_solution()
    
    # 최종 결과
    print("\n" + "="*60)
    print("최종 결과")
    print("="*60)
    
    for key, value in results.items():
        status = "[OK]" if value else "[FAIL]"
        print(f"{status} {key.capitalize()}")
    
    if all(results.values()):
        print("\n[SUCCESS] 모든 검사 통과! API가 정상 작동해야 합니다.")
    else:
        print("\n[WARNING] 일부 문제가 발견되었습니다. 위의 해결 방안을 따라주세요.")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)