"""
간단한 직원 데이터 생성 스크립트
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def create_employees():
    """직원 데이터 직접 생성"""
    
    cursor = connection.cursor()
    
    # 테이블 컬럼 확인
    cursor.execute("PRAGMA table_info(employees_employee)")
    columns = cursor.fetchall()
    print("Columns:", [col[1] for col in columns])
    
    departments = ['IT개발본부', '영업본부', '마케팅본부', '재무본부', '인사본부', '전략기획본부', '리스크관리본부']
    positions = ['사원', '대리', '차장', '부장', '팀장', '이사', '상무']
    
    # 간단한 INSERT 문 생성
    created_count = 0
    
    # PL직군 700명
    for i in range(700):
        try:
            cursor.execute("""
                INSERT INTO employees_employee (
                    name, email, department, position, hire_date, 
                    created_at, updated_at, employment_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f'PL직원{i+1:04d}',
                f'pl{i+1:04d}@okfn.com',
                random.choice(departments),
                f'PL{random.randint(1, 5)}',
                datetime.now().date(),
                datetime.now(),
                datetime.now(),
                '재직'
            ))
            created_count += 1
        except Exception as e:
            print(f"Error creating PL employee {i}: {e}")
            continue
    
    # Non-PL직군 1,000명
    non_pl_distribution = [
        ('사원', 80),
        ('대리', 300),
        ('차장', 270),
        ('부장', 90),
        ('팀장', 160),
        ('부장(직책)', 70),
        ('이사', 10),
        ('상무', 10),
        ('전무', 7),
        ('부사장', 3),
    ]
    
    employee_count = 0
    for position, count in non_pl_distribution:
        for i in range(count):
            employee_count += 1
            try:
                cursor.execute("""
                    INSERT INTO employees_employee (
                        name, email, department, position, hire_date,
                        created_at, updated_at, employment_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f'직원{employee_count:04d}',
                    f'emp{employee_count:04d}@okfn.com',
                    random.choice(departments),
                    position,
                    datetime.now().date(),
                    datetime.now(),
                    datetime.now(),
                    '재직'
                ))
                created_count += 1
            except Exception as e:
                print(f"Error creating employee {employee_count}: {e}")
                continue
    
    connection.commit()
    print(f"Successfully created {created_count} employees")

if __name__ == '__main__':
    create_employees()