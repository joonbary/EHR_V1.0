#!/usr/bin/env python
"""
Railway PostgreSQL 데이터베이스 리셋 스크립트
모든 테이블을 삭제하고 마이그레이션을 처음부터 다시 실행합니다.
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def reset_railway_database():
    """Railway PostgreSQL 데이터베이스를 완전히 리셋합니다."""
    
    print("Railway PostgreSQL 데이터베이스 리셋 시작...")
    
    with connection.cursor() as cursor:
        # 1. 모든 테이블 삭제 (CASCADE로 의존성 있는 테이블도 함께 삭제)
        print("\n1. 기존 테이블 삭제 중...")
        
        # 모든 테이블 목록 가져오기
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            # CASCADE로 모든 테이블 삭제
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
                    print(f"   - {table_name} 테이블 삭제됨")
                except Exception as e:
                    print(f"   ! {table_name} 삭제 실패: {e}")
        else:
            print("   - 삭제할 테이블이 없습니다.")
    
    print("\n2. 마이그레이션 다시 실행 중...")
    try:
        # 마이그레이션 실행
        call_command('migrate', verbosity=2)
        print("\n✅ 데이터베이스 리셋 완료!")
    except Exception as e:
        print(f"\n❌ 마이그레이션 실패: {e}")
        return False
    
    return True

if __name__ == '__main__':
    # Railway 환경인지 확인
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("Railway 환경에서 실행 중...")
        reset_railway_database()
    else:
        print("⚠️  경고: 이 스크립트는 Railway 환경에서만 실행해야 합니다.")
        print("로컬에서 실행하려면 RAILWAY_ENVIRONMENT 환경변수를 설정하세요.")
        
        response = input("\n정말로 로컬 데이터베이스를 리셋하시겠습니까? (yes/no): ")
        if response.lower() == 'yes':
            reset_railway_database()
        else:
            print("작업이 취소되었습니다.")