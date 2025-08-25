#!/usr/bin/env python
"""
Railway에서 마이그레이션 실행 및 테이블 생성 확인
"""

import os
import sys
import django
from django.db import connection

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("=" * 60)
print("Railway 마이그레이션 실행 스크립트")
print("=" * 60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def check_table_exists(table_name):
    """테이블 존재 여부 확인"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            );
        """, [table_name])
        return cursor.fetchone()[0]

def run_migrations():
    """마이그레이션 실행"""
    from django.core.management import call_command
    
    print("1. 현재 마이그레이션 상태 확인")
    print("-" * 40)
    
    try:
        # 마이그레이션 상태 확인
        call_command('showmigrations', 'employees')
        print()
    except Exception as e:
        print(f"[ERROR] 마이그레이션 상태 확인 실패: {e}\n")
    
    print("2. 마이그레이션 실행")
    print("-" * 40)
    
    try:
        # 마이그레이션 실행
        call_command('migrate', 'employees', verbosity=2)
        print("[OK] 마이그레이션 완료\n")
    except Exception as e:
        print(f"[ERROR] 마이그레이션 실패: {e}\n")
        
        # 개별 마이그레이션 시도
        print("개별 마이그레이션 시도...")
        try:
            call_command('migrate', 'employees', '0001_initial', verbosity=2)
            print("[OK] 0001_initial 적용")
        except:
            pass
            
        try:
            call_command('migrate', 'employees', '0002_add_missing_extended_fields', verbosity=2)
            print("[OK] 0002_add_missing_extended_fields 적용")
        except:
            pass
            
        try:
            call_command('migrate', 'employees', '0003_organizationstructure_employeeorganizationmapping_and_more', verbosity=2)
            print("[OK] 0003_organizationstructure 적용")
        except Exception as e2:
            print(f"[ERROR] 0003 마이그레이션 실패: {e2}")

def verify_tables():
    """테이블 생성 확인"""
    print("\n3. 테이블 생성 확인")
    print("-" * 40)
    
    tables_to_check = [
        'employees_organizationstructure',
        'employees_organizationuploadhistory',
        'employees_employeeorganizationmapping',
    ]
    
    for table_name in tables_to_check:
        exists = check_table_exists(table_name)
        status = "[OK]" if exists else "[MISSING]"
        print(f"{status} {table_name}")
    
    return all(check_table_exists(t) for t in tables_to_check)

def create_tables_manually():
    """수동으로 테이블 생성"""
    print("\n4. 수동 테이블 생성")
    print("-" * 40)
    
    if not check_table_exists('employees_organizationstructure'):
        print("OrganizationStructure 테이블 생성 중...")
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                        id SERIAL PRIMARY KEY,
                        org_code VARCHAR(50) UNIQUE NOT NULL,
                        org_name VARCHAR(100) NOT NULL,
                        org_level INTEGER NOT NULL,
                        parent_id INTEGER REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                        full_path VARCHAR(500),
                        group_name VARCHAR(100),
                        company_name VARCHAR(100),
                        headquarters_name VARCHAR(100),
                        department_name VARCHAR(100),
                        team_name VARCHAR(100),
                        description TEXT,
                        establishment_date DATE,
                        status VARCHAR(20) DEFAULT 'active',
                        leader_id INTEGER REFERENCES employees_employee(id) ON DELETE SET NULL,
                        sort_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL
                    );
                """)
                
                # 인덱스 생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_code ON employees_organizationstructure(org_code);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_level_status ON employees_organizationstructure(org_level, status);")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_parent ON employees_organizationstructure(parent_id);")
                
                print("[OK] OrganizationStructure 테이블 생성")
            except Exception as e:
                print(f"[ERROR] OrganizationStructure 테이블 생성 실패: {e}")
    
    if not check_table_exists('employees_organizationuploadhistory'):
        print("OrganizationUploadHistory 테이블 생성 중...")
        
        with connection.cursor() as cursor:
            try:
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
                        uploaded_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
                        options JSONB DEFAULT '{}'::jsonb
                    );
                """)
                print("[OK] OrganizationUploadHistory 테이블 생성")
            except Exception as e:
                print(f"[ERROR] OrganizationUploadHistory 테이블 생성 실패: {e}")
    
    if not check_table_exists('employees_employeeorganizationmapping'):
        print("EmployeeOrganizationMapping 테이블 생성 중...")
        
        with connection.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
                        id SERIAL PRIMARY KEY,
                        employee_id INTEGER NOT NULL REFERENCES employees_employee(id) ON DELETE CASCADE,
                        organization_id INTEGER NOT NULL REFERENCES employees_organizationstructure(id) ON DELETE CASCADE,
                        is_primary BOOLEAN DEFAULT TRUE,
                        role VARCHAR(50),
                        start_date DATE DEFAULT CURRENT_DATE,
                        end_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(employee_id, organization_id, is_primary)
                    );
                """)
                print("[OK] EmployeeOrganizationMapping 테이블 생성")
            except Exception as e:
                print(f"[ERROR] EmployeeOrganizationMapping 테이블 생성 실패: {e}")

def update_employee_table():
    """Employee 테이블에 organization_id 컬럼 추가"""
    print("\n5. Employee 테이블 업데이트")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # organization_id 컬럼 존재 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            AND column_name = 'organization_id';
        """)
        
        if not cursor.fetchone():
            print("organization_id 컬럼 추가 중...")
            try:
                cursor.execute("""
                    ALTER TABLE employees_employee 
                    ADD COLUMN IF NOT EXISTS organization_id INTEGER 
                    REFERENCES employees_organizationstructure(id) ON DELETE SET NULL;
                """)
                print("[OK] organization_id 컬럼 추가")
            except Exception as e:
                print(f"[ERROR] organization_id 컬럼 추가 실패: {e}")
        else:
            print("[OK] organization_id 컬럼 이미 존재")

def insert_sample_data():
    """샘플 데이터 삽입"""
    print("\n6. 샘플 데이터 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("샘플 조직 구조 데이터 생성 중...")
            
            try:
                # 그룹 레벨
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, status, sort_order) 
                    VALUES ('GRP001', 'OK금융그룹', 1, 'active', 1)
                    ON CONFLICT (org_code) DO NOTHING;
                """)
                
                # 계열사 레벨
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, parent_id, status, sort_order) 
                    VALUES ('COM001', 'OK저축은행', 2, 
                        (SELECT id FROM employees_organizationstructure WHERE org_code='GRP001'),
                        'active', 1)
                    ON CONFLICT (org_code) DO NOTHING;
                """)
                
                # 본부 레벨
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, parent_id, status, sort_order) 
                    VALUES ('HQ001', '리테일본부', 3,
                        (SELECT id FROM employees_organizationstructure WHERE org_code='COM001'),
                        'active', 1)
                    ON CONFLICT (org_code) DO NOTHING;
                """)
                
                print("[OK] 샘플 데이터 생성")
            except Exception as e:
                print(f"[ERROR] 샘플 데이터 생성 실패: {e}")
        else:
            print(f"[INFO] 이미 {count}개의 조직 데이터 존재")

def main():
    """메인 실행"""
    print("\n시작: Railway 마이그레이션 및 테이블 생성\n")
    
    # 1. 마이그레이션 실행
    run_migrations()
    
    # 2. 테이블 확인
    all_exist = verify_tables()
    
    # 3. 테이블이 없으면 수동 생성
    if not all_exist:
        create_tables_manually()
        verify_tables()
    
    # 4. Employee 테이블 업데이트
    update_employee_table()
    
    # 5. 샘플 데이터 생성
    insert_sample_data()
    
    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()