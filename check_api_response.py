"""
API 응답 테스트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models_hr import OutsourcedStaff
from django.db.models import Sum, Count, Q, Case, When, IntegerField

# 최신 데이터 조회
latest_date = OutsourcedStaff.objects.latest('report_date').report_date

print(f"최신 날짜: {latest_date}")
print("\n=== 데이터베이스 현황 ===")

# 회사별 프로젝트 인력
companies = OutsourcedStaff.objects.values('company_name').distinct()
for company in companies:
    company_name = company['company_name']
    records = OutsourcedStaff.objects.filter(company_name=company_name, report_date=latest_date)
    
    print(f"\n{company_name}:")
    for record in records:
        print(f"  - {record.project_name} | {record.staff_type} | {record.headcount}명")

# API와 동일한 집계 쿼리
print("\n=== API 집계 방식 ===")
summary = OutsourcedStaff.objects.filter(report_date=latest_date).aggregate(
    total_headcount=Sum('headcount'),
    total_resident=Sum(Case(
        When(staff_type='resident', then='headcount'),
        default=0,
        output_field=IntegerField()
    )),
    total_non_resident=Sum(Case(
        When(staff_type='non_resident', then='headcount'),
        default=0,
        output_field=IntegerField()
    )),
    total_project=Sum(Case(
        When(staff_type='project', then='headcount'),
        default=0,
        output_field=IntegerField()
    ))
)

print(f"전체: {summary['total_headcount']}명")
print(f"상주: {summary['total_resident']}명")
print(f"비상주: {summary['total_non_resident']}명")
print(f"프로젝트: {summary['total_project']}명")

# 프로젝트 타입만 따로 조회
print("\n=== 프로젝트 타입 레코드 ===")
project_records = OutsourcedStaff.objects.filter(staff_type='project', report_date=latest_date)
for record in project_records:
    print(f"{record.company_name} - {record.project_name}: {record.headcount}명")
print(f"프로젝트 총계: {project_records.aggregate(Sum('headcount'))['headcount__sum'] or 0}명")