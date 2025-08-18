#!/usr/bin/env python
"""
Railway 데이터베이스 리셋 및 데이터 로드
"""
import os
import sys
import django
from django.core.management import call_command
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

def reset_and_load():
    """데이터베이스 리셋 및 데이터 로드"""
    print("=" * 50)
    print("Starting database reset and data load")
    print("=" * 50)
    
    try:
        # 1. 모든 테이블 삭제 시도
        with connection.cursor() as cursor:
            # SQLite의 경우
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                for table in tables:
                    if not table[0].startswith('sqlite_'):
                        try:
                            cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
                            print(f"Dropped table: {table[0]}")
                        except:
                            pass
            except:
                print("Not SQLite or table drop failed")
        
        # 2. 마이그레이션 실행 (새로운 DB에서)
        print("\nRunning migrations on fresh database...")
        call_command('migrate', '--noinput')
        print("Migrations completed")
        
    except Exception as e:
        print(f"Reset failed: {e}")
        print("Trying to continue with existing database...")
    
    # 3. 데이터 로드 시도
    try:
        from employees.models import Employee
        current_count = Employee.objects.count()
        print(f"\nCurrent employee count: {current_count}")
        
        if current_count < 100:  # 100명 미만이면 데이터 로드
            if os.path.exists('employees_only.json'):
                print("Loading employee data...")
                call_command('loaddata', 'employees_only.json')
                new_count = Employee.objects.count()
                print(f"Data loaded. New count: {new_count}")
            else:
                print("employees_only.json not found")
        else:
            print(f"Already have {current_count} employees. Skipping load.")
            
    except Exception as e:
        print(f"Data load error: {e}")
    
    print("=" * 50)
    print("Process completed")
    print("=" * 50)

if __name__ == "__main__":
    reset_and_load()