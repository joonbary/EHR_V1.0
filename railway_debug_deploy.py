#!/usr/bin/env python
"""
Railway 배포 후 API 오류 진단
"""

import os
import sys
import django
import json
import traceback
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 배포 후 진단")
print(f"시간: {datetime.now()}")
print("="*60)

# 환경 확인
is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
print(f"\n[환경] {'Railway' if is_railway else 'Local'}")

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def check_database_tables():
    """데이터베이스 테이블 확인"""
    print("1. 데이터베이스 테이블 상태")
    print("-" * 40)
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        if is_railway:
            cursor.execute("""
                SELECT table_name, 
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'employees_%'
                ORDER BY table_name;
            """)
        else:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'employees_%'
                ORDER BY name;
            """)
        
        tables = cursor.fetchall()
        print(f"찾은 테이블 ({len(tables)}개):")
        for table in tables:
            if is_railway:
                print(f"  - {table[0]} (크기: {table[1]})")
            else:
                print(f"  - {table[0]}")
        
        # 각 테이블의 레코드 수 확인
        print("\n레코드 수:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count}개")

def test_organization_api():
    """Organization API 테스트"""
    print("\n2. Organization Stats API 테스트")
    print("-" * 40)
    
    try:
        from django.test import RequestFactory
        from employees.views import get_organization_stats
        
        factory = RequestFactory()
        request = factory.get('/api/organization-stats/')
        
        # API 호출
        response = get_organization_stats(request)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print("[OK] API 정상")
            for key, value in data.items():
                print(f"  - {key}: {value}")
        else:
            print(f"[ERROR] API 오류")
            print(f"내용: {response.content.decode('utf-8')[:500]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"[ERROR] API 테스트 실패:")
        print(str(e))
        traceback.print_exc()
        return False

def test_upload_api():
    """Upload API 테스트"""
    print("\n3. Upload Organization API 테스트")
    print("-" * 40)
    
    try:
        from django.test import RequestFactory
        from employees.views import upload_organization_structure
        
        factory = RequestFactory()
        
        # 테스트 데이터
        test_data = {
            'data': [
                {
                    '조직코드': 'TEST999',
                    '조직명': '테스트조직',
                    '조직레벨': 3,
                    '상위조직코드': 'COM001',
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
        request._dont_enforce_csrf_checks = True
        
        # API 호출
        response = upload_organization_structure(request)
        print(f"응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print("[OK] Upload API 정상")
            for key, value in data.items():
                print(f"  - {key}: {value}")
        else:
            print(f"[ERROR] Upload API 오류")
            content = response.content.decode('utf-8')
            print(f"내용: {content[:500]}")
            
            # 상세 오류 분석
            if response.status_code == 400:
                try:
                    error_data = json.loads(content)
                    if 'error' in error_data:
                        print(f"\n오류 메시지: {error_data['error']}")
                    if 'errors' in error_data:
                        print("상세 오류:")
                        for err in error_data['errors']:
                            print(f"  - {err}")
                except:
                    pass
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"[ERROR] Upload API 테스트 실패:")
        print(str(e))
        traceback.print_exc()
        return False

def check_model_fields():
    """모델 필드 확인"""
    print("\n4. OrganizationStructure 모델 필드")
    print("-" * 40)
    
    try:
        from employees.models_organization import OrganizationStructure
        
        # 모델 필드 목록
        fields = [f.name for f in OrganizationStructure._meta.get_fields()]
        print(f"모델 필드 ({len(fields)}개):")
        for field in sorted(fields):
            print(f"  - {field}")
        
        # 데이터베이스 컬럼과 비교
        from django.db import connection
        with connection.cursor() as cursor:
            if is_railway:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'employees_organizationstructure'
                    ORDER BY column_name;
                """)
            else:
                cursor.execute("""
                    PRAGMA table_info(employees_organizationstructure);
                """)
            
            if is_railway:
                db_columns = [col[0] for col in cursor.fetchall()]
            else:
                db_columns = [col[1] for col in cursor.fetchall()]
            
            print(f"\nDB 컬럼 ({len(db_columns)}개):")
            for col in sorted(db_columns):
                print(f"  - {col}")
            
            # 차이점 찾기
            model_only = set(fields) - set(db_columns)
            db_only = set(db_columns) - set(fields)
            
            if model_only:
                print("\n[WARNING] 모델에만 있는 필드:")
                for field in model_only:
                    print(f"  - {field}")
            
            if db_only:
                print("\n[WARNING] DB에만 있는 컬럼:")
                for col in db_only:
                    print(f"  - {col}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 모델 필드 확인 실패: {e}")
        return False

def check_views_import():
    """views.py import 확인"""
    print("\n5. views.py Import 확인")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    if not os.path.exists(views_path):
        print(f"[ERROR] views.py 파일 없음: {views_path}")
        return False
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 상단 1000자 확인
    header = content[:1000]
    
    required_imports = [
        'from .models_organization import OrganizationStructure',
        'from .models_organization import OrganizationUploadHistory',
        'from .models import Employee'
    ]
    
    print("Import 상태:")
    for imp in required_imports:
        if imp in header:
            print(f"  [OK] {imp}")
        else:
            print(f"  [MISSING] {imp}")
    
    return True

def main():
    """메인 진단"""
    
    results = {}
    
    # 1. 테이블 확인
    check_database_tables()
    
    # 2. 모델 필드 확인
    results['model'] = check_model_fields()
    
    # 3. views.py 확인
    results['views'] = check_views_import()
    
    # 4. API 테스트
    results['stats_api'] = test_organization_api()
    results['upload_api'] = test_upload_api()
    
    # 결과 요약
    print("\n" + "="*60)
    print("진단 결과")
    print("="*60)
    
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}")
    
    if not all(results.values()):
        print("\n추천 조치:")
        if not results['stats_api']:
            print("1. railway run python manage.py migrate --run-syncdb")
        if not results['upload_api']:
            print("2. views.py 파일의 import 문 확인")
            print("3. CSRF 설정 확인")
        print("4. railway restart")
        print("5. railway logs --tail 100")
    else:
        print("\n✅ 모든 테스트 통과!")

if __name__ == "__main__":
    main()