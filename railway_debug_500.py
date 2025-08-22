#!/usr/bin/env python
"""
Railway 500 오류 상세 디버깅 스크립트
"""

import os
import sys
import django
import traceback
import json

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 500 오류 디버깅")
print("="*60)

# 환경 정보
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
print(f"\n[환경 정보]")
print(f"Railway 환경: {is_railway}")
print(f"Python 버전: {sys.version}")
print(f"Django 설정: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

if is_railway:
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    print(f"RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT')}")
    print(f"RAILWAY_PROJECT_ID: {os.environ.get('RAILWAY_PROJECT_ID')}")

try:
    django.setup()
    print("\n[OK] Django 초기화 성공")
except Exception as e:
    print(f"\n[ERROR] Django 초기화 실패: {e}")
    traceback.print_exc()
    sys.exit(1)

def test_database():
    """데이터베이스 연결 테스트"""
    print("\n" + "="*60)
    print("1. 데이터베이스 연결 테스트")
    print("="*60)
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            if is_railway:
                # PostgreSQL
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"[OK] PostgreSQL 버전: {version[0][:50]}...")
                
                # 테이블 확인
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE 'employees_%'
                    ORDER BY table_name;
                """)
            else:
                # SQLite
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"[OK] SQLite 버전: {version[0]}")
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE 'employees_%'
                    ORDER BY name;
                """)
            
            tables = cursor.fetchall()
            print(f"\n[INFO] employees 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # 필수 테이블 확인
            required_tables = [
                'employees_employee',
                'employees_organizationstructure',
                'employees_organizationuploadhistory'
            ]
            
            table_names = [t[0] for t in tables]
            missing_tables = []
            for req_table in required_tables:
                if req_table not in table_names:
                    missing_tables.append(req_table)
            
            if missing_tables:
                print(f"\n[ERROR] 누락된 테이블:")
                for table in missing_tables:
                    print(f"  - {table}")
                return False
            else:
                print(f"\n[OK] 모든 필수 테이블 존재")
                return True
                
    except Exception as e:
        print(f"\n[ERROR] 데이터베이스 오류: {e}")
        traceback.print_exc()
        return False

def test_model_imports():
    """모델 import 테스트"""
    print("\n" + "="*60)
    print("2. 모델 Import 테스트")
    print("="*60)
    
    success = True
    
    # Employee 모델
    try:
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"[OK] Employee 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] Employee 모델 import 실패:")
        print(f"  {str(e)}")
        traceback.print_exc()
        success = False
    
    # OrganizationStructure 모델
    try:
        from employees.models_organization import OrganizationStructure
        count = OrganizationStructure.objects.count()
        print(f"[OK] OrganizationStructure 모델: {count}개 레코드")
        
        if count == 0:
            print("\n[WARNING] OrganizationStructure 테이블이 비어있음")
            print("  초기 데이터 생성이 필요합니다.")
            
    except Exception as e:
        print(f"[ERROR] OrganizationStructure 모델 import 실패:")
        print(f"  {str(e)}")
        traceback.print_exc()
        success = False
    
    # OrganizationUploadHistory 모델
    try:
        from employees.models_organization import OrganizationUploadHistory
        count = OrganizationUploadHistory.objects.count()
        print(f"[OK] OrganizationUploadHistory 모델: {count}개 레코드")
    except Exception as e:
        print(f"[ERROR] OrganizationUploadHistory 모델 import 실패:")
        print(f"  {str(e)}")
        traceback.print_exc()
        success = False
    
    return success

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n" + "="*60)
    print("3. API 엔드포인트 테스트")
    print("="*60)
    
    from django.test import RequestFactory
    
    factory = RequestFactory()
    
    # 1. organization-stats API
    print("\n[테스트] GET /api/organization-stats/")
    try:
        from employees.views import get_organization_stats
        
        request = factory.get('/api/organization-stats/')
        response = get_organization_stats(request)
        
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  응답 데이터:")
            print(f"    - total_orgs: {data.get('total_orgs')}")
            print(f"    - active_orgs: {data.get('active_orgs')}")
            print(f"    - total_employees: {data.get('total_employees')}")
            print(f"  [OK] API 정상 작동")
        else:
            print(f"  [ERROR] 비정상 응답 코드")
            print(f"  응답 내용: {response.content}")
            
    except Exception as e:
        print(f"  [ERROR] API 호출 실패:")
        print(f"    {str(e)}")
        traceback.print_exc()
    
    # 2. upload-organization-structure API
    print("\n[테스트] POST /api/upload-organization-structure/")
    try:
        from employees.views import upload_organization_structure
        
        # 테스트 데이터
        test_data = {
            'data': [
                {
                    '조직코드': 'TEST001',
                    '조직명': '테스트조직',
                    '조직레벨': 1,
                    '상위조직코드': None,
                    '상태': 'active',
                    '정렬순서': 1,
                    '설명': '테스트'
                }
            ]
        }
        
        request = factory.post(
            '/api/upload-organization-structure/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        response = upload_organization_structure(request)
        print(f"  응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"  응답 데이터:")
            print(f"    - success: {data.get('success')}")
            print(f"    - created: {data.get('created')}")
            print(f"    - updated: {data.get('updated')}")
            print(f"  [OK] API 정상 작동")
        else:
            print(f"  [ERROR] 비정상 응답 코드")
            print(f"  응답 내용: {response.content}")
            
    except Exception as e:
        print(f"  [ERROR] API 호출 실패:")
        print(f"    {str(e)}")
        traceback.print_exc()

def check_settings():
    """Django 설정 확인"""
    print("\n" + "="*60)
    print("4. Django 설정 확인")
    print("="*60)
    
    from django.conf import settings
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # INSTALLED_APPS 확인
    if 'employees' in settings.INSTALLED_APPS:
        print("[OK] 'employees' 앱 등록됨")
    else:
        print("[ERROR] 'employees' 앱이 INSTALLED_APPS에 없음")
    
    # MIDDLEWARE 확인
    print(f"\nMIDDLEWARE 수: {len(settings.MIDDLEWARE)}개")
    
    # CORS 설정
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    
    # CSRF 설정
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

def create_initial_data():
    """초기 데이터 생성"""
    print("\n" + "="*60)
    print("5. 초기 데이터 생성 시도")
    print("="*60)
    
    try:
        from employees.models_organization import OrganizationStructure
        
        if OrganizationStructure.objects.count() > 0:
            print("[INFO] 이미 조직 데이터가 존재합니다")
            return
        
        print("[INFO] 초기 조직 데이터 생성 중...")
        
        # 그룹
        group = OrganizationStructure.objects.create(
            org_code='GRP001',
            org_name='OK금융그룹',
            org_level=1,
            status='active',
            sort_order=1,
            description='OK금융그룹 지주회사'
        )
        print("  [OK] OK금융그룹 생성")
        
        # 계열사
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
        
        print("\n[OK] 초기 데이터 생성 완료")
        
    except Exception as e:
        print(f"[ERROR] 초기 데이터 생성 실패:")
        print(f"  {str(e)}")
        traceback.print_exc()

def generate_solution():
    """해결 방안 제시"""
    print("\n" + "="*60)
    print("해결 방안")
    print("="*60)
    
    print("""
Railway에서 다음 명령들을 순서대로 실행하세요:

1. 마이그레이션 실행:
   railway run python manage.py migrate

2. 초기 데이터 생성:
   railway run python railway_debug_500.py

3. 서버 재시작:
   railway restart

4. 로그 확인:
   railway logs --tail 100

5. 환경 변수 확인:
   railway variables

문제가 지속되면:
- DATABASE_URL이 올바른지 확인
- DJANGO_SETTINGS_MODULE이 'ehr_system.settings'인지 확인
- 마이그레이션 파일이 모두 커밋되었는지 확인
""")

def main():
    """메인 실행"""
    
    # 1. 데이터베이스 테스트
    db_ok = test_database()
    
    # 2. 모델 테스트
    models_ok = test_model_imports()
    
    # 3. API 테스트
    test_api_endpoints()
    
    # 4. 설정 확인
    check_settings()
    
    # 5. 초기 데이터 생성
    if db_ok and models_ok:
        create_initial_data()
    
    # 6. 해결 방안
    generate_solution()

if __name__ == "__main__":
    main()