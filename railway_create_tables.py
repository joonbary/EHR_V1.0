#!/usr/bin/env python
"""
Railway 환경에서 누락된 테이블 생성 스크립트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 테이블 생성 스크립트")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화 성공\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection, migrations
from django.core.management import call_command

def create_tables_manually():
    """수동으로 테이블 생성"""
    print("테이블 수동 생성 시작...")
    
    with connection.cursor() as cursor:
        # 1. OrganizationStructure 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                id SERIAL PRIMARY KEY,
                org_code VARCHAR(50) UNIQUE NOT NULL,
                org_name VARCHAR(200) NOT NULL,
                org_level INTEGER NOT NULL,
                parent_id INTEGER REFERENCES employees_organizationstructure(id),
                status VARCHAR(20) DEFAULT 'active',
                sort_order INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("[OK] employees_organizationstructure 테이블 생성")
        
        # 2. OrganizationUploadHistory 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_organizationuploadhistory (
                id SERIAL PRIMARY KEY,
                uploaded_by_id INTEGER REFERENCES auth_user(id),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_name VARCHAR(255),
                total_records INTEGER DEFAULT 0,
                success_records INTEGER DEFAULT 0,
                failed_records INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT
            );
        """)
        print("[OK] employees_organizationuploadhistory 테이블 생성")
        
        # 3. EmployeeOrganizationMapping 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_employeeorganizationmapping (
                id SERIAL PRIMARY KEY,
                employee_id INTEGER REFERENCES employees_employee(id),
                organization_id INTEGER REFERENCES employees_organizationstructure(id),
                is_primary BOOLEAN DEFAULT FALSE,
                assigned_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, organization_id)
            );
        """)
        print("[OK] employees_employeeorganizationmapping 테이블 생성")
        
        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_org_parent 
            ON employees_organizationstructure(parent_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_org_level 
            ON employees_organizationstructure(org_level);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_org_status 
            ON employees_organizationstructure(status);
        """)
        print("[OK] 인덱스 생성 완료")

def main():
    """메인 실행"""
    
    # 1. 먼저 마이그레이션 시도
    print("\n1. 마이그레이션 실행 시도...")
    try:
        call_command('migrate', 'employees', verbosity=2)
        print("[OK] 마이그레이션 성공")
    except Exception as e:
        print(f"[WARNING] 마이그레이션 실패: {e}")
        print("\n2. 수동 테이블 생성 시도...")
        try:
            create_tables_manually()
            print("[OK] 수동 테이블 생성 성공")
        except Exception as e2:
            print(f"[ERROR] 수동 생성도 실패: {e2}")
            return False
    
    # 3. 테이블 확인
    print("\n3. 생성된 테이블 확인...")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"\n현재 employees 테이블 ({len(tables)}개):")
        for table in tables:
            print(f"  - {table[0]}")
    
    # 4. 초기 데이터 생성
    print("\n4. 초기 데이터 생성...")
    try:
        from employees.models_organization import OrganizationStructure
        
        if OrganizationStructure.objects.count() == 0:
            # 그룹
            group = OrganizationStructure.objects.create(
                org_code='GRP001',
                org_name='OK금융그룹',
                org_level=1,
                status='active',
                sort_order=1,
                description='OK금융그룹 지주회사'
            )
            print(f"  [OK] {group.org_name} 생성")
            
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
            print(f"  [OK] {company.org_name} 생성")
            
            print("\n[SUCCESS] 초기 데이터 생성 완료")
        else:
            print(f"[INFO] 이미 {OrganizationStructure.objects.count()}개의 조직 존재")
            
    except Exception as e:
        print(f"[WARNING] 초기 데이터 생성 실패: {e}")
    
    print("\n" + "="*60)
    print("완료! 다음 명령을 실행하세요:")
    print("="*60)
    print("1. railway restart")
    print("2. railway logs --tail 50")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)