#!/usr/bin/env python
"""
테이블 강제 생성 스크립트 - 리디렉션 루프 문제 해결
"""

import os
import sys
import django
from django.db import connection

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

try:
    django.setup()
    print("[OK] Django 초기화")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def create_tables():
    """테이블 생성"""
    with connection.cursor() as cursor:
        print("\n1. OrganizationStructure 테이블 생성")
        print("-" * 40)
        
        # 한 번에 전체 CREATE TABLE 실행
        try:
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
            connection.commit()
            print("[OK] OrganizationStructure 테이블 생성")
        except Exception as e:
            print(f"[ERROR] OrganizationStructure: {e}")
        
        print("\n2. OrganizationUploadHistory 테이블 생성")
        print("-" * 40)
        
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
                    uploaded_by_id INTEGER,
                    options JSONB DEFAULT '{}'::jsonb
                )
            """)
            connection.commit()
            print("[OK] OrganizationUploadHistory 테이블 생성")
        except Exception as e:
            print(f"[ERROR] OrganizationUploadHistory: {e}")
        
        print("\n3. EmployeeOrganizationMapping 테이블 생성")
        print("-" * 40)
        
        try:
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
            connection.commit()
            print("[OK] EmployeeOrganizationMapping 테이블 생성")
        except Exception as e:
            print(f"[ERROR] EmployeeOrganizationMapping: {e}")
        
        print("\n4. Employee 테이블 업데이트")
        print("-" * 40)
        
        try:
            cursor.execute("""
                ALTER TABLE employees_employee 
                ADD COLUMN IF NOT EXISTS organization_id INTEGER
            """)
            connection.commit()
            print("[OK] organization_id 컬럼 추가")
        except Exception as e:
            print(f"[ERROR] organization_id: {e}")
        
        print("\n5. 마이그레이션 레코드 추가")
        print("-" * 40)
        
        try:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('employees', '0002_add_missing_extended_fields', CURRENT_TIMESTAMP)
                ON CONFLICT DO NOTHING
            """)
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('employees', '0003_organizationstructure_employeeorganizationmapping_and_more', CURRENT_TIMESTAMP)
                ON CONFLICT DO NOTHING
            """)
            connection.commit()
            print("[OK] 마이그레이션 레코드 추가")
        except Exception as e:
            print(f"[ERROR] 마이그레이션: {e}")
        
        print("\n6. 샘플 데이터 추가")
        print("-" * 40)
        
        try:
            # 그룹 추가
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, status, sort_order, group_name, full_path) 
                VALUES ('GRP001', 'OK금융그룹', 1, 'active', 1, 'OK금융그룹', 'OK금융그룹')
                ON CONFLICT (org_code) DO NOTHING
                RETURNING id
            """)
            result = cursor.fetchone()
            
            if result:
                group_id = result[0]
                
                # 계열사 추가
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, parent_id, status, sort_order, 
                     group_name, company_name, full_path) 
                    VALUES ('COM001', 'OK저축은행', 2, %s, 'active', 1,
                     'OK금융그룹', 'OK저축은행', 'OK금융그룹 > OK저축은행')
                    ON CONFLICT (org_code) DO NOTHING
                    RETURNING id
                """, [group_id])
                
                result = cursor.fetchone()
                if result:
                    company_id = result[0]
                    
                    # 본부 추가
                    cursor.execute("""
                        INSERT INTO employees_organizationstructure 
                        (org_code, org_name, org_level, parent_id, status, sort_order,
                         group_name, company_name, headquarters_name, full_path) 
                        VALUES ('HQ001', '리테일본부', 3, %s, 'active', 1,
                         'OK금융그룹', 'OK저축은행', '리테일본부',
                         'OK금융그룹 > OK저축은행 > 리테일본부')
                        ON CONFLICT (org_code) DO NOTHING
                    """, [company_id])
            
            connection.commit()
            print("[OK] 샘플 데이터 추가")
        except Exception as e:
            print(f"[ERROR] 샘플 데이터: {e}")
        
        print("\n7. 최종 확인")
        print("-" * 40)
        
        try:
            cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure")
            count = cursor.fetchone()[0]
            print(f"[OK] 조직 데이터: {count}개")
        except Exception as e:
            print(f"[ERROR] 확인 실패: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("테이블 강제 생성 스크립트")
    print("=" * 60)
    
    create_tables()
    
    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)