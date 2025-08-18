#!/usr/bin/env python
"""
job_profiles_jobrole 테이블 생성 스크립트
"""
import os
import sys
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def create_jobrole_table():
    """job_profiles_jobrole 테이블 생성"""
    print("Creating job_profiles_jobrole table...")
    
    with connection.cursor() as cursor:
        try:
            # 테이블 존재 여부 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'job_profiles_jobrole'
            """)
            
            if cursor.fetchone():
                print("job_profiles_jobrole table already exists")
                return
                
            # 테이블 생성
            cursor.execute("""
                CREATE TABLE job_profiles_jobrole (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✓ Created job_profiles_jobrole table")
            
            # 기본 데이터 삽입
            cursor.execute("""
                INSERT INTO job_profiles_jobrole (name) VALUES 
                ('개발자'),
                ('디자이너'),
                ('기획자'),
                ('마케터'),
                ('운영'),
                ('관리자')
            """)
            print("✓ Inserted default job roles")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    create_jobrole_table()