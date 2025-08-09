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
            
            # 필요한 컬럼들 확인 및 추가
            required_columns = ['dummy_chinese_name', 'dummy_name', 'dummy_mobile']
            
            for col_name in required_columns:
                if col_name not in columns:
                    # 컬럼 추가
                    cursor.execute(f"ALTER TABLE employees_employee ADD COLUMN {col_name} VARCHAR(100) NULL")
                    print(f"Added {col_name} column")
                    
                    # 기본값 설정
                    cursor.execute(f"UPDATE employees_employee SET {col_name} = '익명화' WHERE {col_name} IS NULL")
                    print(f"Updated {col_name} values")
                else:
                    print(f"{col_name} column already exists")
                
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    add_missing_column()