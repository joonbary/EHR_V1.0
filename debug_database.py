#!/usr/bin/env python
"""
데이터베이스 연결 상태 디버깅 스크립트
Railway 환경에서 DATABASE_URL 설정 확인
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def debug_database_connection():
    """데이터베이스 연결 디버깅"""
    print("=" * 60)
    print("DATABASE CONNECTION DEBUG")
    print("=" * 60)
    
    # 1. 환경 변수 확인
    print("1. Environment Variables:")
    database_url = os.getenv('DATABASE_URL', '')
    railway_env = os.getenv('RAILWAY_ENVIRONMENT', '')
    
    print(f"   RAILWAY_ENVIRONMENT: {railway_env}")
    print(f"   DATABASE_URL exists: {bool(database_url)}")
    print(f"   DATABASE_URL length: {len(database_url) if database_url else 0}")
    
    # 모든 환경 변수 중 DATABASE 관련 찾기
    db_vars = {k: v for k, v in os.environ.items() if 'DATABASE' in k.upper()}
    print(f"   All DATABASE vars: {list(db_vars.keys())}")
    
    if database_url:
        # 중요한 정보는 마스킹
        masked_url = database_url
        if '@' in masked_url:
            parts = masked_url.split('@')
            if len(parts) == 2:
                auth_part = parts[0]
                if ':' in auth_part:
                    user_pass = auth_part.split('://')[-1]
                    masked_auth = user_pass.split(':')[0] + ':***'
                    masked_url = masked_url.replace(user_pass, masked_auth)
        print(f"   DATABASE_URL: {masked_url}")
        print(f"   Starts with postgres: {database_url.startswith(('postgres://', 'postgresql://'))}")
    else:
        print("   DATABASE_URL: Not set")
    
    # 2. Django 설정 확인
    print("\n2. Django Database Settings:")
    from django.conf import settings
    db_config = settings.DATABASES['default']
    print(f"   Engine: {db_config['ENGINE']}")
    print(f"   Name: {db_config.get('NAME', 'N/A')}")
    
    # 3. 실제 연결 테스트
    print("\n3. Database Connection Test:")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("   ✓ Database connection successful")
        
        # 데이터베이스 타입 확인
        if 'sqlite' in db_config['ENGINE']:
            print("   Database Type: SQLite")
        elif 'postgresql' in db_config['ENGINE']:
            print("   Database Type: PostgreSQL")
        else:
            print(f"   Database Type: {db_config['ENGINE']}")
            
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
    
    # 4. 직원 데이터 확인
    print("\n4. Employee Data Check:")
    try:
        from employees.models import Employee
        count = Employee.objects.count()
        print(f"   Total employees: {count}")
        
        if count > 0:
            sample = Employee.objects.first()
            print(f"   Sample employee: {sample.name} ({sample.email})")
    except Exception as e:
        print(f"   ❌ Employee data access failed: {e}")
    
    print("\n" + "=" * 60)
    
    # 5. 해결 방법 안내
    if not database_url or database_url == '://':
        print("SOLUTION: Set DATABASE_URL in Railway Variables")
        print("1. Go to Railway Dashboard → Your Project")
        print("2. Settings tab → Variables section")
        print("3. Add new variable:")
        print("   Name: DATABASE_URL")
        print("   Value: postgresql://username:password@host/database?sslmode=require")
        print("4. Deploy again")
    elif not database_url.startswith(('postgres://', 'postgresql://')):
        print("SOLUTION: Fix DATABASE_URL format")
        print("Must start with 'postgresql://' or 'postgres://'")
    
    print("=" * 60)

if __name__ == "__main__":
    debug_database_connection()