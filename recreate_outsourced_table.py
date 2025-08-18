"""
외주인력 테이블 재생성
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # 1. 기존 테이블 삭제
        print("기존 테이블 삭제 중...")
        cursor.execute("DROP TABLE IF EXISTS hr_outsourced_staff")
        
        # 2. 새 테이블 생성
        print("새 테이블 생성 중...")
        cursor.execute("""
            CREATE TABLE hr_outsourced_staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name VARCHAR(100) NOT NULL,
                project_name VARCHAR(200) NOT NULL,
                staff_type VARCHAR(20) NOT NULL DEFAULT 'resident',
                headcount INTEGER NOT NULL DEFAULT 0,
                report_date DATE NOT NULL,
                base_type VARCHAR(20) NOT NULL DEFAULT 'week',
                previous_headcount INTEGER NOT NULL DEFAULT 0,
                headcount_change INTEGER NOT NULL DEFAULT 0,
                change_rate DECIMAL(5,2) NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                uploaded_by_id INTEGER
            )
        """)
        
        # 3. 인덱스 생성
        print("인덱스 생성 중...")
        cursor.execute("CREATE INDEX hr_outsourc_company_name_idx ON hr_outsourced_staff (company_name)")
        cursor.execute("CREATE INDEX hr_outsourc_report_date_idx ON hr_outsourced_staff (report_date)")
        cursor.execute("CREATE INDEX hr_outsourc_staff_type_idx ON hr_outsourced_staff (staff_type)")
        cursor.execute("CREATE UNIQUE INDEX hr_outsourc_unique_idx ON hr_outsourced_staff (company_name, project_name, report_date, staff_type)")
        
        print("외주인력 테이블 재생성 완료!")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()