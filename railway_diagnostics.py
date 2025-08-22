#!/usr/bin/env python
"""
Railway 환경 상세 진단 스크립트
API 오류 원인 파악을 위한 종합 점검
"""

import os
import sys
import json
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("=== Railway 진단 시작 ===")
print(f"Python 버전: {sys.version}")
print(f"Django 설정: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"Railway 환경: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not Railway')}")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")

try:
    django.setup()
    print("[OK] Django 초기화 성공")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def check_database():
    """데이터베이스 연결 및 테이블 확인"""
    print("\n=== 데이터베이스 점검 ===")
    
    from django.db import connection
    
    try:
        with connection.cursor() as cursor:
            # PostgreSQL 버전 확인
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] DB 연결 성공: {version[0][:50]}...")
            
            # 테이블 목록 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"\n전체 테이블 수: {len(tables)}")
            
            # 주요 테이블 확인
            important_tables = [
                'employees_employee',
                'employees_organizationstructure',
                'employees_organizationuploadhistory',
                'employees_hremployee',
                'auth_user',
                'django_migrations'
            ]
            
            table_names = [t[0] for t in tables]
            for table in important_tables:
                if table in table_names:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (누락)")
                    
    except Exception as e:
        print(f"[ERROR] 데이터베이스 점검 실패: {e}")
        return False
    
    return True

def check_models():
    """모델 import 및 app_label 확인"""
    print("\n=== 모델 점검 ===")
    
    models_to_check = [
        ('employees.models', 'Employee'),
        ('employees.models_organization', 'OrganizationStructure'),
        ('employees.models_organization', 'OrganizationUploadHistory'),
        ('employees.models_hr', 'HREmployee'),
        ('employees.models_workforce', 'WeeklyWorkforceSnapshot'),
    ]
    
    for module_name, model_name in models_to_check:
        try:
            module = __import__(module_name, fromlist=[model_name])
            model_class = getattr(module, model_name)
            
            # app_label 확인
            app_label = getattr(model_class._meta, 'app_label', None)
            if app_label == 'employees':
                print(f"  ✓ {module_name}.{model_name} (app_label: {app_label})")
            else:
                print(f"  ✗ {module_name}.{model_name} (app_label: {app_label} - 잘못됨)")
                
            # 테이블 존재 확인
            try:
                count = model_class.objects.count()
                print(f"    레코드 수: {count}")
            except Exception as e:
                print(f"    레코드 조회 실패: {str(e)[:50]}...")
                
        except Exception as e:
            print(f"  ✗ {module_name}.{model_name} import 실패: {str(e)[:50]}...")

def check_migrations():
    """마이그레이션 상태 확인"""
    print("\n=== 마이그레이션 상태 ===")
    
    from django.core.management import call_command
    from io import StringIO
    
    output = StringIO()
    try:
        call_command('showmigrations', 'employees', stdout=output, no_color=True)
        migrations = output.getvalue()
        
        # 적용된 마이그레이션 수 계산
        applied = migrations.count('[X]')
        not_applied = migrations.count('[ ]')
        
        print(f"적용됨: {applied}, 미적용: {not_applied}")
        
        if not_applied > 0:
            print("\n[WARNING] 미적용 마이그레이션 존재!")
            print("다음 명령 실행 필요: python manage.py migrate")
            
    except Exception as e:
        print(f"[ERROR] 마이그레이션 상태 확인 실패: {e}")

def check_api_functions():
    """API 함수 직접 테스트"""
    print("\n=== API 함수 테스트 ===")
    
    # organization-stats API 테스트
    try:
        from employees.models_organization import OrganizationStructure
        from employees.models import Employee
        
        stats = {
            'total_organizations': OrganizationStructure.objects.count(),
            'active_organizations': OrganizationStructure.objects.filter(status='active').count(),
            'total_employees': Employee.objects.filter(employment_status='재직').count(),
        }
        
        print(f"[OK] organization-stats 데이터:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"[ERROR] organization-stats 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # upload-organization-structure API 준비 상태
    print("\n[INFO] upload-organization-structure 요구사항:")
    try:
        from employees.models_organization import OrganizationStructure
        
        # 레벨별 조직 수 확인
        for level in range(1, 6):
            count = OrganizationStructure.objects.filter(org_level=level).count()
            level_name = ['그룹', '계열사', '본부', '부', '팀'][level-1]
            print(f"  레벨 {level} ({level_name}): {count}개")
            
        if OrganizationStructure.objects.count() == 0:
            print("\n[WARNING] 조직 데이터 없음 - 초기 데이터 생성 필요")
            
    except Exception as e:
        print(f"[ERROR] 조직 구조 확인 실패: {e}")

def check_settings():
    """Django 설정 확인"""
    print("\n=== Django 설정 점검 ===")
    
    from django.conf import settings
    
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"INSTALLED_APPS에 'employees': {'employees' in settings.INSTALLED_APPS}")
    
    # CORS 설정 확인
    if hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
    
    # CSRF 설정 확인
    if hasattr(settings, 'CSRF_TRUSTED_ORIGINS'):
        print(f"CSRF_TRUSTED_ORIGINS: {settings.CSRF_TRUSTED_ORIGINS}")

def suggest_fixes():
    """문제 해결 제안"""
    print("\n=== 해결 방안 제안 ===")
    
    print("""
1. Railway CLI에서 실행:
   railway run python railway_diagnostics.py
   
2. 마이그레이션 실행:
   railway run python manage.py migrate
   
3. 초기 데이터 생성:
   railway run python initialize_organization_data.py
   
4. 서버 재시작:
   railway restart
   
5. 환경 변수 확인:
   railway variables
   
6. 로그 확인:
   railway logs --tail 100
""")

if __name__ == '__main__':
    print("\n" + "="*50)
    
    # 각 점검 실행
    db_ok = check_database()
    check_models()
    check_migrations()
    check_api_functions()
    check_settings()
    suggest_fixes()
    
    print("\n" + "="*50)
    print("진단 완료!")