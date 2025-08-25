#!/usr/bin/env python
"""
스마트 마이그레이션 스크립트
기존 테이블과 충돌을 자동으로 감지하고 해결합니다.
"""

import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def check_table_exists(table_name):
    """테이블이 존재하는지 확인"""
    with connection.cursor() as cursor:
        # SQLite와 PostgreSQL 구분
        if connection.vendor == 'sqlite':
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, [table_name])
            return cursor.fetchone() is not None
        else:  # PostgreSQL
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename = %s
                )
            """, [table_name])
            return cursor.fetchone()[0]

def get_migration_state():
    """현재 마이그레이션 상태를 확인"""
    with connection.cursor() as cursor:
        # django_migrations 테이블이 있는지 확인
        if not check_table_exists('django_migrations'):
            return 'fresh'  # 완전히 새로운 데이터베이스
        
        # 마이그레이션 기록 확인
        cursor.execute("""
            SELECT COUNT(*) 
            FROM django_migrations 
            WHERE app NOT IN ('contenttypes', 'auth', 'admin', 'sessions')
        """)
        custom_migrations = cursor.fetchone()[0]
        
        if custom_migrations == 0:
            return 'django_only'  # Django 기본 앱만 마이그레이션됨
        
        # 문제가 있는 테이블 확인
        problem_tables = [
            'certifications_growthlevelrequirement',
            'evaluations_evaluation',
            'notifications_notification'
        ]
        
        problems = []
        for table in problem_tables:
            if check_table_exists(table):
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                if count > 0:
                    problems.append(f"{table} (rows: {count})")
        
        if problems:
            return 'has_data'  # 데이터가 있는 테이블이 존재
        
        return 'partial'  # 부분적으로 마이그레이션됨

def handle_existing_tables():
    """기존 테이블 처리"""
    print("\n기존 테이블 처리 중...")
    
    with connection.cursor() as cursor:
        # 문제가 될 수 있는 테이블들 확인 및 처리
        tables_to_check = [
            'certifications_growthlevelrequirement',
            'certifications_certificationchecklog',
            'evaluations_growthlevel',
            'evaluations_growthlevelrequirement'
        ]
        
        for table in tables_to_check:
            if check_table_exists(table):
                print(f"  - {table} 테이블 발견, 삭제 중...")
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                print(f"    {table} 삭제 완료")

def ensure_organization_tables():
    """OrganizationStructure 테이블들이 존재하는지 확인하고 생성"""
    org_tables = [
        'employees_organizationstructure',
        'employees_organizationuploadhistory', 
        'employees_employeeorganizationmapping'
    ]
    
    missing_tables = []
    for table in org_tables:
        if not check_table_exists(table):
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\n조직구조 테이블이 누락되어 있습니다: {missing_tables}")
        print("테이블을 생성합니다...")
        
        with connection.cursor() as cursor:
            try:
                # OrganizationStructure 테이블
                if 'employees_organizationstructure' in missing_tables:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                            id SERIAL PRIMARY KEY,
                            org_code VARCHAR(50) UNIQUE NOT NULL,
                            org_name VARCHAR(100) NOT NULL,
                            org_level INTEGER NOT NULL DEFAULT 1,
                            parent_id INTEGER REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                            full_path VARCHAR(500) DEFAULT '',
                            group_name VARCHAR(100) DEFAULT '',
                            company_name VARCHAR(100) DEFAULT '',
                            headquarters_name VARCHAR(100) DEFAULT '',
                            department_name VARCHAR(100) DEFAULT '',
                            team_name VARCHAR(100) DEFAULT '',
                            description TEXT DEFAULT '',
                            establishment_date DATE,
                            status VARCHAR(20) DEFAULT 'active',
                            leader_id INTEGER,
                            sort_order INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            created_by_id INTEGER
                        )
                    """)
                    print("  - employees_organizationstructure 생성")
                
                # OrganizationUploadHistory 테이블
                if 'employees_organizationuploadhistory' in missing_tables:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS employees_organizationuploadhistory (
                            id SERIAL PRIMARY KEY,
                            file_name VARCHAR(255) NOT NULL,
                            file_path VARCHAR(100),
                            status VARCHAR(20) DEFAULT 'pending',
                            total_rows INTEGER DEFAULT 0,
                            processed_rows INTEGER DEFAULT 0,
                            success_count INTEGER DEFAULT 0,
                            error_count INTEGER DEFAULT 0,
                            error_details JSONB DEFAULT '[]'::jsonb,
                            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            processed_at TIMESTAMP,
                            uploaded_by_id INTEGER,
                            options JSONB DEFAULT '{}'::jsonb
                        )
                    """)
                    print("  - employees_organizationuploadhistory 생성")
                
                # EmployeeOrganizationMapping 테이블
                if 'employees_employeeorganizationmapping' in missing_tables:
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
                            id SERIAL PRIMARY KEY,
                            employee_id INTEGER NOT NULL,
                            organization_id INTEGER NOT NULL REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                            is_primary BOOLEAN DEFAULT TRUE,
                            role VARCHAR(50),
                            start_date DATE DEFAULT CURRENT_DATE,
                            end_date DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    print("  - employees_employeeorganizationmapping 생성")
                
                # Employee 테이블에 organization_id 추가
                if check_table_exists('employees_employee'):
                    cursor.execute("""
                        ALTER TABLE employees_employee 
                        ADD COLUMN IF NOT EXISTS organization_id INTEGER
                    """)
                    print("  - employees_employee.organization_id 추가")
                
                # 마이그레이션 레코드 추가
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES ('employees', '0003_organizationstructure_employeeorganizationmapping_and_more', CURRENT_TIMESTAMP)
                    ON CONFLICT DO NOTHING
                """)
                
                # 샘플 데이터
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, status, sort_order, group_name, full_path) 
                    VALUES ('GRP001', 'OK금융그룹', 1, 'active', 1, 'OK금융그룹', 'OK금융그룹')
                    ON CONFLICT (org_code) DO NOTHING
                """)
                
                print("조직구조 테이블 생성 완료!")
                
            except Exception as e:
                print(f"조직구조 테이블 생성 오류: {e}")

def smart_migrate():
    """스마트 마이그레이션 실행"""
    print("\n" + "=" * 60)
    print("스마트 마이그레이션 시작")
    print("=" * 60)
    
    # 1. 현재 상태 확인
    state = get_migration_state()
    print(f"\n데이터베이스 상태: {state}")
    
    if state == 'fresh':
        print("새로운 데이터베이스입니다. 전체 마이그레이션을 실행합니다.")
        call_command('migrate', verbosity=1)
        
    elif state == 'django_only':
        print("Django 기본 앱만 설치되어 있습니다. 커스텀 앱을 마이그레이션합니다.")
        call_command('migrate', verbosity=1)
        
    elif state == 'has_data':
        print("\n경고: 데이터가 있는 테이블이 발견되었습니다.")
        print("데이터 보존이 필요한 경우 백업을 먼저 수행하세요.")
        
        # Railway 환경에서는 자동으로 처리
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            print("Railway 환경입니다. 자동으로 처리합니다.")
            handle_existing_tables()
            call_command('migrate', '--fake-initial', verbosity=1)
        else:
            response = input("\n계속하시겠습니까? (yes/no): ")
            if response.lower() == 'yes':
                handle_existing_tables()
                call_command('migrate', '--fake-initial', verbosity=1)
            else:
                print("작업이 취소되었습니다.")
                return False
                
    elif state == 'partial':
        print("부분적으로 마이그레이션된 상태입니다. 충돌을 해결합니다.")
        handle_existing_tables()
        
        # 이미 적용된 마이그레이션은 fake로 처리
        call_command('migrate', '--fake-initial', verbosity=1)
    
    # 2. 조직구조 테이블 확인 및 생성
    ensure_organization_tables()
    
    print("\n" + "=" * 60)
    print("스마트 마이그레이션 완료!")
    print("=" * 60)
    
    # 최종 상태 확인
    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        else:
            cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'")
        table_count = cursor.fetchone()[0]
        print(f"\n총 {table_count}개의 테이블이 있습니다.")
    
    return True

if __name__ == '__main__':
    try:
        success = smart_migrate()
        if success:
            print("\n다음 단계:")
            print("1. 초기 데이터 생성: python setup_initial_data.py")
            print("2. 서버 시작: python manage.py runserver")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)