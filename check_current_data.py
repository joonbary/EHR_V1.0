"""
현재 데이터베이스 상태 확인
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models_hr import OutsourcedStaff
from django.db.models import Sum, Count, Q

# 전체 데이터 조회
print("=== 현재 저장된 데이터 ===")
all_records = OutsourcedStaff.objects.all().order_by('company_name', 'staff_type', 'project_name')

for record in all_records:
    print(f"{record.company_name} | {record.project_name} | {record.staff_type} | {record.headcount}명")

# 집계
print("\n=== 집계 ===")
summary = OutsourcedStaff.objects.aggregate(
    total_resident=Sum('headcount', filter=Q(staff_type='resident')),
    total_non_resident=Sum('headcount', filter=Q(staff_type='non_resident')),
    total_project=Sum('headcount', filter=Q(staff_type='project'))
)

print(f"상주: {summary['total_resident'] or 0}명")
print(f"비상주: {summary['total_non_resident'] or 0}명")
print(f"프로젝트: {summary['total_project'] or 0}명")

# 프로젝트 상세
print("\n=== 프로젝트 인력 상세 ===")
project_records = OutsourcedStaff.objects.filter(staff_type='project')
for record in project_records:
    print(f"{record.company_name} - {record.project_name}: {record.headcount}명")
print(f"프로젝트 총계: {project_records.aggregate(Sum('headcount'))['headcount__sum'] or 0}명")

# 비상주 중 자산운용시스템 확인
print("\n=== 자산운용시스템 관련 레코드 ===")
asset_records = OutsourcedStaff.objects.filter(project_name__contains='자산운용')
for record in asset_records:
    print(f"{record.company_name} - {record.project_name} - {record.staff_type}: {record.headcount}명")