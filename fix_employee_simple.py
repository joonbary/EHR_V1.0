#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Employee 테이블에 누락된 컬럼 추가
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def add_missing_column():
    """Employee 테이블에 dummy_chinese_name 컬럼 추가"""
    
    with connection.cursor() as cursor:
        try:
            # 현재 컬럼 확인 (PostgreSQL)
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee'
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print("Current columns:", len(columns))
            
            # 필요한 컬럼들 확인 및 추가 (데이터 타입 포함)
            required_columns = {
                'dummy_chinese_name': 'VARCHAR(100)',
                'dummy_name': 'VARCHAR(100)',
                'dummy_mobile': 'VARCHAR(20)',
                'dummy_registered_address': 'TEXT',
                'dummy_residence_address': 'TEXT',
                'dummy_email': 'VARCHAR(254)'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in columns:
                    # 컬럼 추가
                    cursor.execute(f"ALTER TABLE employees_employee ADD COLUMN {col_name} {col_type} NULL")
                    print(f"Added {col_name} column ({col_type})")
                    
                    # 기본값 설정
                    default_value = 'dummy@example.com' if 'email' in col_name else '익명화'
                    cursor.execute(f"UPDATE employees_employee SET {col_name} = %s WHERE {col_name} IS NULL", [default_value])
                    print(f"Updated {col_name} values")
                else:
                    print(f"{col_name} column already exists")
                
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    add_missing_column()