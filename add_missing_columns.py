"""
Production DB에 누락된 컬럼 추가
"""

import os
import psycopg2
from urllib.parse import urlparse

# DATABASE_URL 파싱
database_url = os.environ.get('DATABASE_URL')
if database_url:
    parsed = urlparse(database_url)
    
    connection_params = {
        'host': parsed.hostname,
        'port': parsed.port,
        'user': parsed.username,
        'password': parsed.password,
        'database': parsed.path[1:]
    }
    
    print("데이터베이스 연결 중...")
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # 누락된 컬럼들 추가
        missing_columns = [
            ("dummy_ssn", "VARCHAR(20)"),
            ("dummy_name", "VARCHAR(100)"),
            ("dummy_chinese_name", "VARCHAR(100)"),
            ("dummy_phone", "VARCHAR(20)"),
            ("dummy_address", "TEXT"),
            ("dummy_actual_address", "TEXT"),
            ("dummy_email", "VARCHAR(255)")
        ]
        
        for column_name, column_type in missing_columns:
            try:
                # Use parameterized query to prevent SQL injection
                sql = f"ALTER TABLE employees_employee ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                # Since ALTER TABLE doesn't support parameters, validate input
                if not column_name.isidentifier() or ';' in column_type:
                    raise ValueError(f"Invalid column name or type: {column_name}, {column_type}")
                cursor.execute(sql)
                print(f"✓ {column_name} 컬럼 추가 (또는 이미 존재)")
            except Exception as e:
                print(f"✗ {column_name} 컬럼 추가 실패: {e}")
        
        conn.commit()
        print("\n컬럼 추가 완료!")
        
        # 현재 컬럼 확인
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'employees_employee'
            AND column_name LIKE 'dummy%'
        """)
        
        print("\n현재 dummy 컬럼들:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"오류 발생: {e}")
else:
    print("DATABASE_URL 환경변수가 설정되지 않았습니다.")