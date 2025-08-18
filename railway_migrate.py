#!/usr/bin/env python
"""
Railway 배포 환경에서 마이그레이션을 실행하는 스크립트
필요할 때만 수동으로 실행
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_system.settings")
    django.setup()
    
    # 특정 앱만 마이그레이션하거나 fake 옵션 사용 가능
    # execute_from_command_line(["manage.py", "migrate", "--fake"])
    # execute_from_command_line(["manage.py", "migrate", "employees", "0001"])
    
    # 전체 마이그레이션
    execute_from_command_line(["manage.py", "migrate"])