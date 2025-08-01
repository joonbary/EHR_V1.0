"""
업로드 시뮬레이션
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.services.excel_parser import HRExcelAutoParser
from employees.models_hr import OutsourcedStaff

# 모든 데이터 삭제
OutsourcedStaff.objects.all().delete()
print("기존 데이터 삭제 완료")

# 파싱
parser = HRExcelAutoParser()
file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"
result = parser.parse_outsourced_staff(file_path)

print(f"\n파싱 결과: {len(result)}개 항목")
print("\n=== 파싱된 데이터 ===")
for i, data in enumerate(result):
    print(f"{i+1}. {data['company_name']} | {data['project_name']} | {data['staff_type']} | {data['headcount']}명")

# 중복 확인
print("\n=== 중복 확인 ===")
seen = {}
for data in result:
    key = (data['company_name'], data['project_name'], data['report_date'])
    if key in seen:
        print(f"중복 발견: {key}")
        print(f"  기존: {seen[key]['staff_type']} {seen[key]['headcount']}명")
        print(f"  신규: {data['staff_type']} {data['headcount']}명")
    else:
        seen[key] = data

# 저장 시뮬레이션
print("\n=== 저장 시뮬레이션 ===")
for i, data in enumerate(result):
    existing = OutsourcedStaff.objects.filter(
        company_name=data['company_name'],
        project_name=data['project_name'],
        report_date=data['report_date'],
        staff_type=data['staff_type']
    ).first()
    
    if existing:
        print(f"{i+1}. 업데이트: {data['company_name']} - {data['project_name']} ({data['staff_type']})")
    else:
        # staff_type 없이도 확인
        other_type = OutsourcedStaff.objects.filter(
            company_name=data['company_name'],
            project_name=data['project_name'],
            report_date=data['report_date']
        ).first()
        
        if other_type:
            print(f"{i+1}. 다른 타입 존재: {data['company_name']} - {data['project_name']}")
            print(f"     기존: {other_type.staff_type} {other_type.headcount}명")
            print(f"     신규: {data['staff_type']} {data['headcount']}명")
        else:
            print(f"{i+1}. 신규 생성: {data['company_name']} - {data['project_name']} ({data['staff_type']})")
        
        # 실제 저장
        OutsourcedStaff.objects.create(**data)

# 최종 확인
print("\n=== 최종 결과 ===")
summary = OutsourcedStaff.objects.aggregate(
    resident=Sum('headcount', filter=Q(staff_type='resident')),
    non_resident=Sum('headcount', filter=Q(staff_type='non_resident')),
    project=Sum('headcount', filter=Q(staff_type='project'))
)
print(f"상주: {summary['resident'] or 0}명")
print(f"비상주: {summary['non_resident'] or 0}명")
print(f"프로젝트: {summary['project'] or 0}명")

from django.db.models import Sum, Q