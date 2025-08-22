#!/usr/bin/env python
"""
로컬 환경에서 API 테스트
"""

import os
import sys
import django
import traceback

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("로컬 API 테스트")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화 성공")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def test_models_import():
    """모델 import 테스트"""
    print("\n=== 1. 모델 Import 테스트 ===")
    
    errors = []
    
    # 1. Employee 모델
    try:
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"[OK] Employee 모델: {count}개 레코드")
    except Exception as e:
        error_msg = f"Employee 모델 import 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    # 2. OrganizationStructure 모델
    try:
        from employees.models_organization import OrganizationStructure
        count = OrganizationStructure.objects.count()
        print(f"[OK] OrganizationStructure 모델: {count}개 레코드")
    except Exception as e:
        error_msg = f"OrganizationStructure 모델 import 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    # 3. OrganizationUploadHistory 모델
    try:
        from employees.models_organization import OrganizationUploadHistory
        count = OrganizationUploadHistory.objects.count()
        print(f"[OK] OrganizationUploadHistory 모델: {count}개 레코드")
    except Exception as e:
        error_msg = f"OrganizationUploadHistory 모델 import 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_api_views_import():
    """API 뷰 import 테스트"""
    print("\n=== 2. API Views Import 테스트 ===")
    
    errors = []
    
    try:
        from employees import views
        print("[OK] employees.views import 성공")
        
        # 각 API 함수 확인
        api_functions = [
            'get_organization_stats',
            'upload_organization_structure',
            'get_organization_tree',
            'save_organization',
        ]
        
        for func_name in api_functions:
            if hasattr(views, func_name):
                print(f"  [OK] {func_name} 함수 존재")
            else:
                error_msg = f"{func_name} 함수 없음"
                print(f"  [ERROR] {error_msg}")
                errors.append(error_msg)
                
    except Exception as e:
        error_msg = f"views import 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_api_functionality():
    """API 기능 테스트"""
    print("\n=== 3. API 기능 테스트 ===")
    
    errors = []
    
    try:
        from django.test import RequestFactory
        from employees.views import get_organization_stats
        
        factory = RequestFactory()
        request = factory.get('/api/organization-stats/')
        
        # 실제 API 호출
        try:
            response = get_organization_stats(request)
            print(f"[OK] organization-stats API 응답: {response.status_code}")
            
            if response.status_code == 200:
                import json
                data = json.loads(response.content)
                print(f"  - 전체 조직: {data.get('total_orgs', 0)}개")
                print(f"  - 활성 조직: {data.get('active_orgs', 0)}개")
                print(f"  - 전체 직원: {data.get('total_employees', 0)}개")
            else:
                error_msg = f"API 응답 코드: {response.status_code}"
                errors.append(error_msg)
                
        except Exception as e:
            error_msg = f"API 호출 실패: {str(e)}"
            print(f"[ERROR] {error_msg}")
            errors.append(error_msg)
            traceback.print_exc()
            
    except Exception as e:
        error_msg = f"API 테스트 설정 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    return len(errors) == 0, errors

def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("\n=== 4. 데이터베이스 연결 테스트 ===")
    
    errors = []
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # SQLite 버전 확인
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"[OK] SQLite 버전: {version[0]}")
            
            # 테이블 목록
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name;
            """)
            tables = cursor.fetchall()
            
            print(f"[OK] 전체 테이블 수: {len(tables)}개")
            
            # 주요 테이블 확인
            important_tables = [
                'employees_employee',
                'employees_organizationstructure',
                'employees_organizationuploadhistory',
                'auth_user',
                'django_migrations'
            ]
            
            table_names = [t[0] for t in tables]
            for table in important_tables:
                if table in table_names:
                    print(f"  [OK] {table}")
                else:
                    error_msg = f"테이블 없음: {table}"
                    print(f"  [X] {error_msg}")
                    errors.append(error_msg)
                    
    except Exception as e:
        error_msg = f"데이터베이스 연결 실패: {str(e)}"
        print(f"[ERROR] {error_msg}")
        errors.append(error_msg)
        traceback.print_exc()
    
    return len(errors) == 0, errors

def generate_debug_report(all_errors):
    """디버그 리포트 생성"""
    print("\n" + "="*60)
    print("디버그 리포트")
    print("="*60)
    
    if not all_errors:
        print("\n[SUCCESS] 모든 테스트 통과!")
        print("로컬 환경에서는 문제가 없습니다.")
        print("\n다음 단계:")
        print("1. Railway 환경 변수 확인")
        print("2. Railway 데이터베이스 마이그레이션 상태 확인")
        print("3. Railway 로그 확인")
    else:
        print("\n[ERROR] 발견된 문제들:")
        for i, error in enumerate(all_errors, 1):
            print(f"{i}. {error}")
        
        print("\n해결 방안:")
        
        if any("import 실패" in e for e in all_errors):
            print("- 모델 import 문제:")
            print("  - python manage.py makemigrations")
            print("  - python manage.py migrate")
        
        if any("테이블 없음" in e for e in all_errors):
            print("- 테이블 누락 문제:")
            print("  - python manage.py migrate --run-syncdb")
        
        if any("API" in e for e in all_errors):
            print("- API 문제:")
            print("  - views.py 파일의 import 문 확인")
            print("  - 함수 정의 확인")

def main():
    """메인 실행 함수"""
    all_errors = []
    
    # 1. 모델 테스트
    success, errors = test_models_import()
    all_errors.extend(errors)
    
    # 2. API Views 테스트
    success, errors = test_api_views_import()
    all_errors.extend(errors)
    
    # 3. API 기능 테스트
    success, errors = test_api_functionality()
    all_errors.extend(errors)
    
    # 4. 데이터베이스 테스트
    success, errors = test_database_connection()
    all_errors.extend(errors)
    
    # 5. 리포트 생성
    generate_debug_report(all_errors)
    
    return len(all_errors) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)