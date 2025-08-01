"""
외주인력 테이블을 상주/비상주/프로젝트 3가지 구분으로 변경
"""

import os
import sys
import django
import sqlite3

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        # 1. 현재 테이블 구조 확인
        cursor.execute("PRAGMA table_info(hr_outsourced_staff)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print("현재 컬럼:", column_names)
        
        # 2. staff_type 컬럼이 없으면 추가
        if 'staff_type' not in column_names:
            print("staff_type 컬럼 추가 중...")
            cursor.execute("""
                ALTER TABLE hr_outsourced_staff 
                ADD COLUMN staff_type VARCHAR(20) DEFAULT 'resident'
            """)
            
        # 3. is_resident 데이터를 staff_type으로 마이그레이션
        if 'is_resident' in column_names:
            print("기존 데이터 마이그레이션 중...")
            cursor.execute("""
                UPDATE hr_outsourced_staff 
                SET staff_type = CASE 
                    WHEN is_resident = 1 THEN 'resident'
                    ELSE 'non_resident'
                END
            """)
            
        # 4. 인덱스 업데이트
        try:
            # 기존 인덱스 삭제 (있는 경우)
            cursor.execute("DROP INDEX IF EXISTS hr_outsourc_is_resi_7b0e90_idx")
        except:
            pass
            
        # 새 인덱스 생성
        try:
            cursor.execute("CREATE INDEX hr_outsourc_staff_t_97860e_idx ON hr_outsourced_staff (staff_type)")
            print("인덱스 생성 완료")
        except:
            print("인덱스가 이미 존재합니다")
        
        # 5. 데이터 확인
        cursor.execute("SELECT company_name, project_name, staff_type, headcount FROM hr_outsourced_staff LIMIT 5")
        results = cursor.fetchall()
        print("\n업데이트된 데이터 샘플:")
        for row in results:
            print(f"  {row[0]} - {row[1]}: {row[2]} ({row[3]}명)")
            
        print("\n외주인력 테이블 업데이트 완료!")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()