#!/usr/bin/env python
"""
SQL 직접 실행 스크립트
"""

import os
import sys
import django
from django.db import connection

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

try:
    django.setup()
    print("[OK] Django 초기화")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def execute_sql():
    """SQL 파일 실행"""
    with open('create_org_tables.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read()
    
    # SQL을 개별 명령으로 분리 (세미콜론 기준)
    commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
    
    with connection.cursor() as cursor:
        for i, command in enumerate(commands, 1):
            if command and not command.startswith('--'):
                try:
                    cursor.execute(command)
                    print(f"[{i}/{len(commands)}] 실행 완료")
                except Exception as e:
                    print(f"[{i}/{len(commands)}] 오류: {e}")
    
    print("\n모든 SQL 명령 실행 완료!")

if __name__ == "__main__":
    execute_sql()