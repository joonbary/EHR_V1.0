#!/usr/bin/env python
"""
dummy_ssn 컬럼 문제 해결 스크립트
"""
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def fix_dummy_ssn():
    """dummy_ssn 컬럼 제거"""
    print("Fixing dummy_ssn column issue...")
    
    with connection.cursor() as cursor:
        try:
            # PostgreSQL에서 컬럼 존재 여부 확인
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'employees_employee' 
                AND column_name = 'dummy_ssn'
            """)
            
            if cursor.fetchone():
                print("Found dummy_ssn column, removing it...")
                cursor.execute("ALTER TABLE employees_employee DROP COLUMN IF EXISTS dummy_ssn")
                print("✓ Removed dummy_ssn column")
            else:
                print("dummy_ssn column not found")
                
        except Exception as e:
            print(f"Error: {e}")
            
        # job_profiles_jobrole 테이블도 확인
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'job_profiles_jobrole'
            """)
            
            if not cursor.fetchone():
                print("job_profiles_jobrole table missing, creating it...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_profiles_jobrole (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print("✓ Created job_profiles_jobrole table")
                
        except Exception as e:
            print(f"Error with job_profiles_jobrole: {e}")

if __name__ == "__main__":
    fix_dummy_ssn()