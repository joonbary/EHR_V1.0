#!/usr/bin/env python
"""
Railway 영구 수정 - 마이그레이션 강제 실행 및 테이블 생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 영구 수정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection
from django.core.management import call_command

def force_migrations():
    """마이그레이션 강제 실행"""
    print("1. 마이그레이션 강제 실행")
    print("-" * 40)
    
    try:
        # 현재 마이그레이션 상태 확인
        print("현재 마이그레이션 상태:")
        call_command('showmigrations', 'employees')
        
        # 마이그레이션 실행
        print("\n마이그레이션 실행 중...")
        call_command('migrate', 'employees', '0003_organizationstructure_employeeorganizationmapping_and_more', verbosity=2)
        print("[OK] 마이그레이션 0003 실행")
        
        # 전체 마이그레이션
        call_command('migrate', verbosity=1)
        print("[OK] 전체 마이그레이션 완료")
        
    except Exception as e:
        print(f"[WARNING] 마이그레이션 실패: {e}")
        print("테이블을 수동으로 생성합니다...")
        return False
    
    return True

def create_tables_manually():
    """테이블 수동 생성"""
    print("\n2. 테이블 수동 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 테이블 존재 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'employees_organizationstructure';
        """)
        
        if cursor.fetchone():
            print("[OK] employees_organizationstructure 테이블이 이미 존재")
            return True
        
        print("테이블 생성 중...")
        
        # 1. OrganizationStructure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                id SERIAL PRIMARY KEY,
                org_code VARCHAR(50) UNIQUE NOT NULL,
                org_name VARCHAR(100) NOT NULL,
                org_level INTEGER NOT NULL,
                parent_id INTEGER,
                full_path VARCHAR(500),
                group_name VARCHAR(100),
                company_name VARCHAR(100),
                headquarters_name VARCHAR(100),
                department_name VARCHAR(100),
                team_name VARCHAR(100),
                description TEXT,
                establishment_date DATE,
                status VARCHAR(20) DEFAULT 'active',
                leader_id INTEGER,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by_id INTEGER
            );
        """)
        print("[OK] employees_organizationstructure 생성")
        
        # 외래키 추가
        cursor.execute("""
            ALTER TABLE employees_organizationstructure 
            ADD CONSTRAINT fk_org_parent 
            FOREIGN KEY (parent_id) 
            REFERENCES employees_organizationstructure(id) 
            ON DELETE CASCADE;
        """)
        
        # 인덱스
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_parent ON employees_organizationstructure(parent_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_level ON employees_organizationstructure(org_level);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_code ON employees_organizationstructure(org_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_status ON employees_organizationstructure(status);")
        print("[OK] 인덱스 생성")
        
        # 2. OrganizationUploadHistory
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
        print("[OK] employees_organizationuploadhistory 생성")
        
        # 3. EmployeeOrganizationMapping
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
        print("[OK] employees_employeeorganizationmapping 생성")
        
        return True

def fix_employee_table():
    """Employee 테이블 수정"""
    print("\n3. Employee 테이블 수정")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # employment_status 필드
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee' 
            AND column_name = 'employment_status';
        """)
        
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE employees_employee 
                ADD COLUMN employment_status VARCHAR(20) DEFAULT '재직';
            """)
            print("[OK] employment_status 필드 추가")
        else:
            print("[OK] employment_status 필드 존재")
        
        # 기본값 설정
        cursor.execute("""
            UPDATE employees_employee 
            SET employment_status = '재직' 
            WHERE employment_status IS NULL;
        """)

def insert_data():
    """기본 데이터 삽입"""
    print("\n4. 기본 데이터 생성")
    print("-" * 40)
    
    from employees.models_organization import OrganizationStructure
    
    # 데이터 확인
    if OrganizationStructure.objects.count() > 0:
        print(f"[INFO] 이미 {OrganizationStructure.objects.count()}개의 조직 존재")
        return
    
    print("5단계 조직 구조 생성 중...")
    
    # 그룹
    grp = OrganizationStructure.objects.create(
        org_code='GRP001',
        org_name='OK금융그룹',
        org_level=1,
        status='active',
        sort_order=1,
        description='OK금융그룹 지주회사',
        full_path='OK금융그룹'
    )
    print(f"  [OK] {grp.org_name}")
    
    # 계열사
    com = OrganizationStructure.objects.create(
        org_code='COM001',
        org_name='OK저축은행',
        org_level=2,
        parent=grp,
        status='active',
        sort_order=1,
        description='OK저축은행',
        full_path='OK금융그룹 > OK저축은행'
    )
    print(f"  [OK] {com.org_name}")
    
    # 본부
    hq = OrganizationStructure.objects.create(
        org_code='HQ001',
        org_name='리테일본부',
        org_level=3,
        parent=com,
        status='active',
        sort_order=1,
        description='리테일 금융 서비스',
        full_path='OK금융그룹 > OK저축은행 > 리테일본부'
    )
    print(f"  [OK] {hq.org_name}")
    
    # 부서
    dept = OrganizationStructure.objects.create(
        org_code='DEPT001',
        org_name='IT개발부',
        org_level=4,
        parent=hq,
        status='active',
        sort_order=1,
        description='IT개발부',
        full_path='OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부'
    )
    print(f"  [OK] {dept.org_name}")
    
    # 팀
    team1 = OrganizationStructure.objects.create(
        org_code='TEAM001',
        org_name='개발1팀',
        org_level=5,
        parent=dept,
        status='active',
        sort_order=1,
        description='개발1팀',
        full_path='OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발1팀'
    )
    print(f"  [OK] {team1.org_name}")
    
    team2 = OrganizationStructure.objects.create(
        org_code='TEAM002',
        org_name='개발2팀',
        org_level=5,
        parent=dept,
        status='active',
        sort_order=2,
        description='개발2팀',
        full_path='OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발2팀'
    )
    print(f"  [OK] {team2.org_name}")
    
    print("\n[SUCCESS] 6개 조직 생성 완료")

def verify():
    """최종 검증"""
    print("\n5. 최종 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"employees 테이블 ({len(tables)}개):")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 레코드")

def main():
    """메인 실행"""
    
    print("\n시작: Railway 영구 수정\n")
    
    # 1. 마이그레이션 시도
    if not force_migrations():
        # 2. 실패 시 수동 생성
        create_tables_manually()
    
    # 3. Employee 테이블 수정
    fix_employee_table()
    
    # 4. 데이터 생성
    insert_data()
    
    # 5. 검증
    verify()
    
    print("\n" + "="*60)
    print("✅ 영구 수정 완료!")
    print("="*60)
    print("\n중요: Railway 웹 대시보드에서:")
    print("1. Settings → Deploy → Restart 클릭")
    print("2. 또는 railway up 실행")
    print("3. 브라우저 캐시 삭제")

if __name__ == "__main__":
    main()