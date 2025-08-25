#!/usr/bin/env python
"""
Railway 테이블 복원 - 테이블이 삭제된 경우 재생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 테이블 복원")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def check_and_create_tables():
    """테이블 존재 확인 및 생성"""
    print("1. 테이블 상태 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 현재 테이블 목록
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        existing_tables = [t[0] for t in cursor.fetchall()]
        
        print(f"현재 테이블 ({len(existing_tables)}개):")
        for table in existing_tables:
            print(f"  - {table}")
        
        # 필수 테이블 체크
        required_tables = {
            'employees_organizationstructure': False,
            'employees_organizationuploadhistory': False,
            'employees_employeeorganizationmapping': False,
            'employees_employee': False
        }
        
        for table in existing_tables:
            if table in required_tables:
                required_tables[table] = True
        
        print("\n필수 테이블 상태:")
        for table, exists in required_tables.items():
            status = "✓" if exists else "✗"
            print(f"  {status} {table}")
        
        # 누락된 테이블 생성
        print("\n2. 누락된 테이블 생성")
        print("-" * 40)
        
        # 1. OrganizationStructure 테이블
        if not required_tables['employees_organizationstructure']:
            print("OrganizationStructure 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE employees_organizationstructure (
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
                    created_by_id INTEGER,
                    CONSTRAINT fk_parent FOREIGN KEY (parent_id) 
                        REFERENCES employees_organizationstructure(id)
                );
            """)
            
            # 인덱스
            cursor.execute("CREATE INDEX idx_org_parent ON employees_organizationstructure(parent_id);")
            cursor.execute("CREATE INDEX idx_org_level ON employees_organizationstructure(org_level);")
            cursor.execute("CREATE INDEX idx_org_code ON employees_organizationstructure(org_code);")
            cursor.execute("CREATE INDEX idx_org_status ON employees_organizationstructure(status);")
            
            print("[OK] employees_organizationstructure 생성 완료")
        
        # 2. OrganizationUploadHistory 테이블
        if not required_tables['employees_organizationuploadhistory']:
            print("OrganizationUploadHistory 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE employees_organizationuploadhistory (
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
            print("[OK] employees_organizationuploadhistory 생성 완료")
        
        # 3. EmployeeOrganizationMapping 테이블
        if not required_tables['employees_employeeorganizationmapping']:
            print("EmployeeOrganizationMapping 테이블 생성 중...")
            cursor.execute("""
                CREATE TABLE employees_employeeorganizationmapping (
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
            
            # 인덱스
            cursor.execute("CREATE INDEX idx_emp_org_emp ON employees_employeeorganizationmapping(employee_id);")
            cursor.execute("CREATE INDEX idx_emp_org_org ON employees_employeeorganizationmapping(organization_id);")
            
            print("[OK] employees_employeeorganizationmapping 생성 완료")

def insert_basic_data():
    """기본 데이터 삽입"""
    print("\n3. 기본 데이터 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 데이터 존재 확인
        cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("5단계 조직 구조 생성 중...")
            
            # 그룹
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, 
                 description, full_path, group_name)
                VALUES 
                ('GRP001', 'OK금융그룹', 1, NULL, 'active', 1, 
                 'OK금융그룹 지주회사', 'OK금융그룹', 'OK금융그룹')
                RETURNING id;
            """)
            group_id = cursor.fetchone()[0]
            print(f"  [OK] OK금융그룹 (ID: {group_id})")
            
            # 계열사
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, 
                 description, full_path, group_name, company_name)
                VALUES 
                ('COM001', 'OK저축은행', 2, %s, 'active', 1, 
                 'OK저축은행', 'OK금융그룹 > OK저축은행', 'OK금융그룹', 'OK저축은행')
                RETURNING id;
            """, [group_id])
            company_id = cursor.fetchone()[0]
            print(f"  [OK] OK저축은행 (ID: {company_id})")
            
            # 본부
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, 
                 description, full_path, group_name, company_name, headquarters_name)
                VALUES 
                ('HQ001', '리테일본부', 3, %s, 'active', 1, 
                 '리테일 금융 서비스', 'OK금융그룹 > OK저축은행 > 리테일본부',
                 'OK금융그룹', 'OK저축은행', '리테일본부')
                RETURNING id;
            """, [company_id])
            hq_id = cursor.fetchone()[0]
            print(f"  [OK] 리테일본부 (ID: {hq_id})")
            
            # 부서
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, 
                 description, full_path, group_name, company_name, 
                 headquarters_name, department_name)
                VALUES 
                ('DEPT001', 'IT개발부', 4, %s, 'active', 1, 
                 'IT개발부', 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부',
                 'OK금융그룹', 'OK저축은행', '리테일본부', 'IT개발부')
                RETURNING id;
            """, [hq_id])
            dept_id = cursor.fetchone()[0]
            print(f"  [OK] IT개발부 (ID: {dept_id})")
            
            # 팀
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, 
                 description, full_path, group_name, company_name, 
                 headquarters_name, department_name, team_name)
                VALUES 
                ('TEAM001', '개발1팀', 5, %s, 'active', 1, 
                 '개발1팀', 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발1팀',
                 'OK금융그룹', 'OK저축은행', '리테일본부', 'IT개발부', '개발1팀'),
                ('TEAM002', '개발2팀', 5, %s, 'active', 2, 
                 '개발2팀', 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발2팀',
                 'OK금융그룹', 'OK저축은행', '리테일본부', 'IT개발부', '개발2팀');
            """, [dept_id, dept_id])
            print(f"  [OK] 개발1팀, 개발2팀")
            
            print("\n[SUCCESS] 5단계 조직 구조 생성 완료")
        else:
            print(f"[INFO] 이미 {count}개의 조직 데이터 존재")

def fix_employee_table():
    """Employee 테이블 수정"""
    print("\n4. Employee 테이블 수정")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # employment_status 필드 추가
        try:
            cursor.execute("""
                ALTER TABLE employees_employee 
                ADD COLUMN IF NOT EXISTS employment_status VARCHAR(20) DEFAULT '재직';
            """)
            print("[OK] employment_status 필드 추가/확인")
            
            # 기본값 설정
            cursor.execute("""
                UPDATE employees_employee 
                SET employment_status = '재직' 
                WHERE employment_status IS NULL;
            """)
            print("[OK] employment_status 기본값 설정")
        except Exception as e:
            print(f"[INFO] Employee 테이블: {str(e)[:50]}")

def verify_result():
    """최종 검증"""
    print("\n5. 최종 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 테이블 수 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'employees_%'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"테이블 총 {len(tables)}개:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 레코드")
        
        # 조직 계층 확인
        cursor.execute("""
            SELECT org_level, COUNT(*) 
            FROM employees_organizationstructure 
            GROUP BY org_level 
            ORDER BY org_level;
        """)
        levels = cursor.fetchall()
        
        if levels:
            print("\n조직 계층:")
            level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
            for level, count in levels:
                print(f"  레벨{level} ({level_names.get(level, '기타')}): {count}개")

def main():
    """메인 실행"""
    
    print("\n시작: Railway 테이블 복원\n")
    
    # 1. 테이블 확인 및 생성
    check_and_create_tables()
    
    # 2. 기본 데이터 삽입
    insert_basic_data()
    
    # 3. Employee 테이블 수정
    fix_employee_table()
    
    # 4. 최종 검증
    verify_result()
    
    print("\n" + "="*60)
    print("✅ 테이블 복원 완료!")
    print("="*60)
    print("\n필수 작업:")
    print("1. railway restart - 서버 재시작")
    print("2. railway logs - 로그 확인")
    print("3. 브라우저 캐시 삭제 후 재접속")

if __name__ == "__main__":
    main()