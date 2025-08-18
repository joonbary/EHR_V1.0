"""
외주인력 데이터 확인
"""

import os
import sys
import django
from datetime import datetime

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models_hr import OutsourcedStaff

print("=== 외주인력 데이터 확인 ===")

# 전체 데이터 수
total = OutsourcedStaff.objects.count()
print(f"\n전체 레코드 수: {total}개")

# 날짜별 데이터
from django.db.models import Count
date_counts = OutsourcedStaff.objects.values('report_date').annotate(count=Count('id')).order_by('-report_date')

print("\n날짜별 데이터:")
for item in date_counts[:5]:
    print(f"  {item['report_date']}: {item['count']}개")

# 회사별 집계
from django.db.models import Sum
company_stats = OutsourcedStaff.objects.values('company_name', 'staff_type').annotate(
    total=Sum('headcount')
).order_by('company_name', 'staff_type')

print("\n회사별 인력 현황:")
current_company = None
for stat in company_stats:
    if current_company != stat['company_name']:
        if current_company:
            print()
        current_company = stat['company_name']
        print(f"{current_company}:")
    print(f"  {stat['staff_type']}: {stat['total']}명")

# 최근 데이터 샘플
print("\n최근 데이터 샘플:")
recent = OutsourcedStaff.objects.order_by('-created_at')[:5]
for staff in recent:
    print(f"  {staff.company_name} - {staff.project_name}: {staff.staff_type} {staff.headcount}명 ({staff.report_date})")

# 2025-07-01 데이터 확인
target_date = datetime(2025, 7, 1).date()
july_data = OutsourcedStaff.objects.filter(report_date=target_date)
print(f"\n2025-07-01 데이터: {july_data.count()}개")

if july_data.exists():
    print("이미 해당 날짜의 데이터가 존재합니다. 업로드 시 기존 데이터가 업데이트됩니다.")