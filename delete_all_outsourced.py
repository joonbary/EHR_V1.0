"""
외주인력 데이터 모두 삭제
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models_hr import OutsourcedStaff

# 모든 데이터 삭제
count = OutsourcedStaff.objects.count()
OutsourcedStaff.objects.all().delete()
print(f"{count}개의 레코드를 삭제했습니다.")