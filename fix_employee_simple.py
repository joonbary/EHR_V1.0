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
            
            if 'dummy_chinese_name' not in columns:
                # dummy_chinese_name 컬럼 추가
                cursor.execute("ALTER TABLE employees_employee ADD COLUMN dummy_chinese_name VARCHAR(100) NULL")
                print("Added dummy_chinese_name column")
                
                # 기본값 설정
                cursor.execute("UPDATE employees_employee SET dummy_chinese_name = '익명화' WHERE dummy_chinese_name IS NULL")
                print("Updated dummy_chinese_name values")
            else:
                print("dummy_chinese_name column already exists")
                
        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    add_missing_column()