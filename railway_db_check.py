#!/usr/bin/env python
"""
Railway 데이터베이스 직접 확인 및 수정
"""

import os
import sys
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("Railway DB 직접 확인")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

from django.db import connection

def check_database():
    """데이터베이스 직접 쿼리"""
    print("1. 데이터베이스 테이블 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # PostgreSQL 버전
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL: {version[0][:60]}...\n")
        
        # 모든 테이블 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        all_tables = cursor.fetchall()
        
        employees_tables = [t for t in all_tables if t[0].startswith('employees_')]
        
        print(f"employees 테이블 ({len(employees_tables)}개):")
        for table in employees_tables:
            table_name = table[0]
            
            # 레코드 수 확인
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count} 레코드")
            except Exception as e:
                print(f"  - {table_name}: 오류 - {str(e)[:50]}")

def check_organization_structure():
    """OrganizationStructure 테이블 상세 확인"""
    print("\n2. OrganizationStructure 테이블 상세")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 테이블 존재 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'employees_organizationstructure'
            );
        """)
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("[ERROR] employees_organizationstructure 테이블이 없습니다!")
            print("\n테이블 생성 중...")
            
            # 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees_organizationstructure (
                    id SERIAL PRIMARY KEY,
                    org_code VARCHAR(50) UNIQUE NOT NULL,
                    org_name VARCHAR(100) NOT NULL,
                    org_level INTEGER NOT NULL,
                    parent_id INTEGER REFERENCES employees_organizationstructure(id),
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
            print("[OK] 테이블 생성 완료")
            
            # 인덱스 생성
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_parent ON employees_organizationstructure(parent_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_level ON employees_organizationstructure(org_level);")
            print("[OK] 인덱스 생성 완료")
        else:
            print("[OK] employees_organizationstructure 테이블 존재")
            
            # 컬럼 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'employees_organizationstructure'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print(f"\n컬럼 ({len(columns)}개):")
            for col in columns[:10]:  # 처음 10개만
                print(f"  - {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            if len(columns) > 10:
                print(f"  ... 그 외 {len(columns) - 10}개 컬럼")

def check_employee_table():
    """Employee 테이블 확인"""
    print("\n3. Employee 테이블 확인")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # employment_status 컬럼 확인
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee'
            AND column_name = 'employment_status';
        """)
        
        if not cursor.fetchone():
            print("employment_status 컬럼이 없습니다. 추가 중...")
            try:
                cursor.execute("""
                    ALTER TABLE employees_employee 
                    ADD COLUMN employment_status VARCHAR(20) DEFAULT '재직';
                """)
                print("[OK] employment_status 컬럼 추가 완료")
            except Exception as e:
                print(f"[INFO] {str(e)[:100]}")
        else:
            print("[OK] employment_status 컬럼 존재")
        
        # NULL 값 업데이트
        cursor.execute("""
            UPDATE employees_employee 
            SET employment_status = '재직' 
            WHERE employment_status IS NULL;
        """)
        print("[OK] employment_status 기본값 설정")

def insert_test_data():
    """테스트 데이터 삽입"""
    print("\n4. 테스트 데이터 삽입")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        # 기존 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM employees_organizationstructure")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("조직 데이터 생성 중...")
            
            # 그룹
            cursor.execute("""
                INSERT INTO employees_organizationstructure 
                (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                VALUES 
                ('GRP001', 'OK금융그룹', 1, NULL, 'active', 1, 'OK금융그룹', 'OK금융그룹')
                ON CONFLICT (org_code) DO NOTHING
                RETURNING id;
            """)
            group_id = cursor.fetchone()
            
            if group_id:
                print(f"[OK] OK금융그룹 생성 (ID: {group_id[0]})")
                
                # 계열사
                cursor.execute("""
                    INSERT INTO employees_organizationstructure 
                    (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                    VALUES 
                    ('COM001', 'OK저축은행', 2, %s, 'active', 1, 'OK저축은행', 'OK금융그룹 > OK저축은행')
                    ON CONFLICT (org_code) DO NOTHING
                    RETURNING id;
                """, [group_id[0]])
                company_id = cursor.fetchone()
                
                if company_id:
                    print(f"[OK] OK저축은행 생성 (ID: {company_id[0]})")
                    
                    # 본부
                    cursor.execute("""
                        INSERT INTO employees_organizationstructure 
                        (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                        VALUES 
                        ('HQ001', '리테일본부', 3, %s, 'active', 1, '리테일본부', 'OK금융그룹 > OK저축은행 > 리테일본부')
                        ON CONFLICT (org_code) DO NOTHING
                        RETURNING id;
                    """, [company_id[0]])
                    hq_id = cursor.fetchone()
                    
                    if hq_id:
                        print(f"[OK] 리테일본부 생성 (ID: {hq_id[0]})")
                        
                        # 부서
                        cursor.execute("""
                            INSERT INTO employees_organizationstructure 
                            (org_code, org_name, org_level, parent_id, status, sort_order, description, full_path)
                            VALUES 
                            ('DEPT001', 'IT개발부', 4, %s, 'active', 1, 'IT개발부', 'OK금융그룹 > OK저축은행 > 리테일본부 > IT개발부')
                            ON CONFLICT (org_code) DO NOTHING;
                        """, [hq_id[0]])
                        print("[OK] IT개발부 생성")
        else:
            print(f"[INFO] 이미 {count}개의 조직 데이터 존재")
            
            # 데이터 확인
            cursor.execute("""
                SELECT org_code, org_name, org_level 
                FROM employees_organizationstructure 
                ORDER BY org_level, sort_order 
                LIMIT 10;
            """)
            orgs = cursor.fetchall()
            print("\n현재 조직:")
            for org in orgs:
                print(f"  레벨{org[2]}: {org[0]} - {org[1]}")

def test_api_raw():
    """API 직접 테스트"""
    print("\n5. API 원시 테스트")
    print("-" * 40)
    
    try:
        from employees.models_organization import OrganizationStructure
        from employees.models import Employee
        
        # 조직 수
        org_count = OrganizationStructure.objects.count()
        active_count = OrganizationStructure.objects.filter(status='active').count()
        
        # 직원 수
        try:
            emp_count = Employee.objects.filter(employment_status='재직').count()
        except Exception as e:
            print(f"[WARNING] 직원 조회 오류: {str(e)[:100]}")
            emp_count = Employee.objects.count()
        
        print(f"Stats API 데이터:")
        print(f"  - 전체 조직: {org_count}")
        print(f"  - 활성 조직: {active_count}")
        print(f"  - 재직 직원: {emp_count}")
        
        # last_update
        last_org = OrganizationStructure.objects.order_by('-updated_at').first()
        if last_org and hasattr(last_org, 'updated_at'):
            print(f"  - 최종 업데이트: {last_org.updated_at}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] API 테스트 실패:")
        print(str(e))
        traceback.print_exc()
        return False

def main():
    """메인 실행"""
    
    # 1. 데이터베이스 확인
    check_database()
    
    # 2. OrganizationStructure 테이블
    check_organization_structure()
    
    # 3. Employee 테이블
    check_employee_table()
    
    # 4. 테스트 데이터
    insert_test_data()
    
    # 5. API 테스트
    test_api_raw()
    
    print("\n" + "="*60)
    print("DB 확인 완료")
    print("="*60)
    print("\n다음 단계:")
    print("1. railway run python railway_force_fix.py")
    print("2. railway restart")
    print("3. 브라우저에서 테스트")

if __name__ == "__main__":
    main()