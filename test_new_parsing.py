"""
수정된 파싱 로직 테스트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.services.excel_parser import HRExcelAutoParser

# 파서 초기화
parser = HRExcelAutoParser()

# 테스트 파일 경로
file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

print("=== 외주인력 파싱 테스트 ===")

# 파싱 실행
result = parser.parse_outsourced_staff(file_path)

# 결과 분석
staff_counts = {'resident': 0, 'non_resident': 0, 'project': 0}
company_counts = {}

for staff in result:
    # 인력 구분별 집계
    staff_counts[staff['staff_type']] += staff['headcount']
    
    # 회사별 집계
    company = staff['company_name']
    if company not in company_counts:
        company_counts[company] = {'resident': 0, 'non_resident': 0, 'project': 0}
    company_counts[company][staff['staff_type']] += staff['headcount']

print(f"\n=== 전체 집계 ===")
print(f"상주: {staff_counts['resident']}명")
print(f"비상주: {staff_counts['non_resident']}명")
print(f"프로젝트: {staff_counts['project']}명")
print(f"총 인원: {sum(staff_counts.values())}명")

print(f"\n=== 회사별 집계 ===")
for company, counts in company_counts.items():
    total = sum(counts.values())
    print(f"{company}: 총 {total}명 (상주 {counts['resident']}, 비상주 {counts['non_resident']}, 프로젝트 {counts['project']})")

# 비상주/프로젝트 샘플 출력
print(f"\n=== 비상주 인력 샘플 ===")
non_resident_list = [s for s in result if s['staff_type'] == 'non_resident']
for staff in non_resident_list[:3]:
    print(f"  {staff['company_name']} - {staff['project_name']}: {staff['headcount']}명")

print(f"\n=== 프로젝트 인력 샘플 ===")
project_list = [s for s in result if s['staff_type'] == 'project']
for staff in project_list[:3]:
    print(f"  {staff['company_name']} - {staff['project_name']}: {staff['headcount']}명")