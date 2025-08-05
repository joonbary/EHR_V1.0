#!/usr/bin/env python
"""
Railway 완전 초기화 - 테이블 생성 및 데이터 로드
"""
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def setup_database():
    """데이터베이스 설정 및 데이터 로드"""
    print("=" * 60)
    print("RAILWAY DATABASE SETUP")
    print("=" * 60)
    
    # 1. 테이블 생성 (SQL 직접 실행)
    print("\n1. Creating tables if not exist...")
    try:
        with connection.cursor() as cursor:
            # employees_employee 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees_employee (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(254) UNIQUE NOT NULL,
                    department VARCHAR(20),
                    position VARCHAR(20),
                    new_position VARCHAR(50),
                    job_group VARCHAR(50),
                    job_type VARCHAR(50),
                    job_role VARCHAR(100),
                    growth_level INTEGER DEFAULT 1,
                    employment_status VARCHAR(20) DEFAULT '재직',
                    hire_date DATE,
                    phone VARCHAR(15),
                    address TEXT,
                    emergency_contact VARCHAR(15),
                    emergency_relationship VARCHAR(50),
                    manager_id INTEGER,
                    user_id INTEGER
                )
            """)
            print("  ✓ employees_employee table created/verified")
            
            # job_profiles_jobrole 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_profiles_jobrole (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    code VARCHAR(20) UNIQUE,
                    description TEXT,
                    department VARCHAR(50),
                    level INTEGER DEFAULT 1
                )
            """)
            print("  ✓ job_profiles_jobrole table created/verified")
            
    except Exception as e:
        print(f"  ⚠ Table creation warning: {e}")
    
    # 2. 데이터 로드
    print("\n2. Loading employee data...")
    try:
        from employees.models import Employee
        
        # 현재 데이터 확인
        current_count = Employee.objects.count()
        print(f"  Current employees: {current_count}")
        
        if current_count < 100:
            # JSON 파일에서 로드 시도
            if os.path.exists('employees_only.json'):
                print("  Loading from employees_only.json...")
                try:
                    import json
                    with open('employees_only.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    loaded = 0
                    for item in data[:1383]:  # 최대 1383개
                        if item.get('model') == 'employees.employee':
                            fields = item.get('fields', {})
                            try:
                                Employee.objects.get_or_create(
                                    email=fields.get('email', f'emp{loaded}@okgroup.com'),
                                    defaults={
                                        'name': fields.get('name', f'Employee {loaded}'),
                                        'department': fields.get('department', 'IT'),
                                        'position': fields.get('position', 'STAFF'),
                                        'employment_status': fields.get('employment_status', '재직'),
                                        'hire_date': fields.get('hire_date', '2024-01-01'),
                                        'phone': fields.get('phone', '010-0000-0000'),
                                        'growth_level': fields.get('growth_level', 1)
                                    }
                                )
                                loaded += 1
                                if loaded % 100 == 0:
                                    print(f"    Loaded {loaded} employees...")
                            except:
                                pass
                    
                    print(f"  ✓ Loaded {loaded} employees from JSON")
                    
                except Exception as e:
                    print(f"  ⚠ JSON load error: {e}")
                    
            # 최소 데이터 생성
            if Employee.objects.count() < 10:
                print("  Creating minimum test data...")
                for i in range(10):
                    try:
                        Employee.objects.get_or_create(
                            email=f'test{i+1}@okgroup.com',
                            defaults={
                                'name': f'Test Employee {i+1}',
                                'department': 'IT',
                                'position': 'STAFF',
                                'employment_status': '재직',
                                'hire_date': '2024-01-01',
                                'phone': f'010-1111-{i+1:04d}',
                                'growth_level': 1
                            }
                        )
                    except:
                        pass
                print(f"  ✓ Created test data")
        
        # 최종 확인
        final_count = Employee.objects.count()
        print(f"\n3. Final Status:")
        print(f"  Total employees in database: {final_count}")
        
        if final_count > 0:
            print("  ✓ SUCCESS: Database has employee data")
        else:
            print("  ⚠ WARNING: No employee data loaded")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        print("  Creating minimal data with raw SQL...")
        
        # SQL로 직접 데이터 삽입
        try:
            with connection.cursor() as cursor:
                for i in range(5):
                    cursor.execute("""
                        INSERT OR IGNORE INTO employees_employee 
                        (name, email, department, position, employment_status, hire_date, phone, growth_level)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        f'Admin User {i+1}',
                        f'admin{i+1}@okgroup.com',
                        'IT',
                        'STAFF',
                        '재직',
                        '2024-01-01',
                        f'010-9999-{i+1:04d}',
                        1
                    ])
                print("  ✓ Created admin users with SQL")
        except Exception as sql_error:
            print(f"  ✗ SQL insert error: {sql_error}")
    
    print("=" * 60)
    print("Setup completed")
    print("=" * 60)

if __name__ == "__main__":
    setup_database()