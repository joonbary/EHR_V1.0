#!/usr/bin/env python
"""
데이터베이스 필드 확인 스크립트
"""
import os
import sys
import django

# Django 설정 초기화
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.db import connection

def check_airiss_fields():
    """AIRISS 테이블 필드 확인"""
    
    with connection.cursor() as cursor:
        # 테이블 목록 확인 (SQLite)
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' 
            AND name LIKE 'airiss_%'
        """)
        tables = cursor.fetchall()
        
        print("="*60)
        print("AIRISS 관련 테이블:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # AIAnalysisResult 테이블 필드 확인
        try:
            cursor.execute("PRAGMA table_info(airiss_aianalysisresult)")
            columns = cursor.fetchall()
            
            print("\n" + "="*60)
            print("airiss_aianalysisresult 테이블 필드:")
            for col in columns:
                # SQLite PRAGMA table_info 형식: (cid, name, type, notnull, dflt_value, pk)
                print(f"  - {col[1]}: {col[2]}")
                
            # 문제가 되는 필드 확인
            field_names = [col[1] for col in columns]
            
            print("\n" + "="*60)
            print("필드 확인 결과:")
            
            if 'ai_score' in field_names:
                print("  ❌ ai_score 필드 존재 (score로 변경 필요)")
            else:
                print("  ✅ ai_score 필드 없음")
                
            if 'score' in field_names:
                print("  ✅ score 필드 존재")
            else:
                print("  ❌ score 필드 없음")
                
            if 'confidence_score' in field_names:
                print("  ❌ confidence_score 필드 존재 (confidence로 변경 필요)")
            else:
                print("  ✅ confidence_score 필드 없음")
                
            if 'confidence' in field_names:
                print("  ✅ confidence 필드 존재")
            else:
                print("  ❌ confidence 필드 없음")
                
            if 'analyzed_by_id' in field_names:
                print("  ❌ analyzed_by_id 필드 존재 (created_by_id로 변경 필요)")
            else:
                print("  ✅ analyzed_by_id 필드 없음")
                
            if 'created_by_id' in field_names:
                print("  ✅ created_by_id 필드 존재")
            else:
                print("  ❌ created_by_id 필드 없음")
                
        except Exception as e:
            print(f"에러 발생: {e}")
        
        print("="*60)

if __name__ == "__main__":
    check_airiss_fields()