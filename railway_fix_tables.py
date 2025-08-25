#!/usr/bin/env python
"""
Railway 테이블 생성 문제 해결 - 올바른 순서로 테이블 생성
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway 테이블 수정")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def create_organization_structure_table():
    """OrganizationStructure 테이블 먼저 생성"""
    print("1. OrganizationStructure 테이블 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 먼저 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'employees_organizationstructure'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("employees_organizationstructure 테이블 생성 중...")
            
            # 테이블 생성 (외래키 없이)
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
                    created_by_id INTEGER
                );
            """)
            print("[OK] employees_organizationstructure 테이블 생성")
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX idx_org_parent ON employees_organizationstructure(parent_id);")
            cursor.execute("CREATE INDEX idx_org_level ON employees_organizationstructure(org_level);")
            cursor.execute("CREATE INDEX idx_org_code ON employees_organizationstructure(org_code);")
            print("[OK] 인덱스 생성")
            
            # 자기 참조 외래키 추가
            cursor.execute("""
                ALTER TABLE employees_organizationstructure 
                ADD CONSTRAINT fk_parent 
                FOREIGN KEY (parent_id) 
                REFERENCES employees_organizationstructure(id);
            """)
            print("[OK] 자기 참조 외래키 추가")
        else:
            print("[OK] employees_organizationstructure 테이블이 이미 존재")

def create_other_tables():
    """나머지 테이블 생성"""
    print("\n2. 나머지 테이블 생성")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # OrganizationUploadHistory
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
        
        # EmployeeOrganizationMapping
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

def insert_initial_data():
    """초기 데이터 삽입"""
    print("\n3. 초기 데이터 삽입")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("조직 데이터 생성 중...")
            
            # 1. 그룹
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('GRP001', 'OK금융그룹', 1, NULL, 'active', 1, 'OK금융그룹 지주회사', 'OK금융그룹')
                RETURNING id;
            """)
            group_id = cursor.fetchone()[0]
            print(f"[OK] OK금융그룹 생성 (ID: {group_id})")
            
            # 2. 계열사
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('COM001', 'OK저축은행', 2, %s, 'active', 1, 'OK저축은행', 'OK금융그룹 > OK저축은행')
                RETURNING id;
            """, [group_id])
            company_id = cursor.fetchone()[0]
            print(f"[OK] OK저축은행 생성 (ID: {company_id})")
            
            # 3. 본부
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('HQ001', '리테일본부', 3, %s, 'active', 1, '리테일 금융 서비스', 
                 'OK금융그룹 > OK저축은행 > 리테일본부')
                RETURNING id;
            """, [company_id])
            hq_id = cursor.fetchone()[0]
            print(f"[OK] 리테일본부 생성 (ID: {hq_id})")
            
            # 4. 부서
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('DEPT001', 'IT개발부', 4, %s, 'active', 1, 'IT개발부', 
                 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부')
                RETURNING id;
            """, [hq_id])
            dept_id = cursor.fetchone()[0]
            print(f"[OK] IT개발부 생성 (ID: {dept_id})")
            
            # 5. 팀
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('TEAM001', '개발1팀', 5, %s, 'active', 1, '개발1팀', 
                 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발1팀'),
                ('TEAM002', '개발2팀', 5, %s, 'active', 2, '개발2팀', 
                 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부 > 개발2팀');
            """, [dept_id, dept_id])
            print("[OK] 개발1팀, 개발2팀 생성")
            
            print("\n[SUCCESS] 5단계 조직 구조 생성 완료")
        else:
            print(f"[INFO] 이미 {count}개의 조직 데이터 존재")

def verify_tables():
    """테이블 검증"""
    print("\n4. 테이블 검증")
    print("-" * 40)
    
    with connection.cursor() as cursor:
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

def test_api():
    """API 테스트"""
    print("\n5. API 테스트")
    print("-" * 40)
    
    try:
        from employees.models_organization import OrganizationStructure
        from employees.models import Employee
        
        org_count = OrganizationStructure.objects.count()
        active_count = OrganizationStructure.objects.filter(status='active').count()
        
        # Employee 테이블에서 직원 수 확인
        emp_count = 0
        try:
            emp_count = Employee.objects.filter(employment_status='재직').count()
        except:
            emp_count = Employee.objects.count()
        
        print("Stats API 데이터:")
        print(f"  - 전체 조직: {org_count}")
        print(f"  - 활성 조직: {active_count}")
        print(f"  - 재직 직원: {emp_count}")
        
        print("\n[SUCCESS] API 데이터 준비 완료")
        
    except Exception as e:
        print(f"[WARNING] API 테스트: {str(e)[:100]}")

def main():
    """메인 실행"""
    
    print("\n시작: 테이블 생성 및 데이터 설정\n")
    
    # 1. OrganizationStructure 테이블 먼저 생성
    create_organization_structure_table()
    
    # 2. 나머지 테이블 생성
    create_other_tables()
    
    # 3. 초기 데이터 삽입
    insert_initial_data()
    
    # 4. 검증
    verify_tables()
    
    # 5. API 테스트
    test_api()
    
    print("\n" + "="*60)
    print("✅ 테이블 생성 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. railway restart")
    print("2. 브라우저에서 조직 구조 페이지 테스트")
    print("\nExcel 업로드 URL:")
    print("https://[your-app].up.railway.app/employees/organization-structure/")

if __name__ == "__main__":
    main()