"""
데이터베이스 상태 확인 및 파싱 테스트
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from employees.models_hr import OutsourcedStaff
from employees.services.excel_parser import HRExcelAutoParser

# 1. 현재 데이터베이스 상태 확인
print("=== 데이터베이스 상태 ===")
count = OutsourcedStaff.objects.count()
print(f"현재 저장된 레코드 수: {count}개")

if count > 0:
    latest = OutsourcedStaff.objects.order_by('-created_at').first()
    print(f"최근 레코드: {latest.company_name} - {latest.project_name} ({latest.created_at})")

# 2. 파싱 테스트
print("\n=== 파싱 테스트 ===")
parser = HRExcelAutoParser()
file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

if os.path.exists(file_path):
    result = parser.parse_outsourced_staff(file_path)
    print(f"파싱 결과: {len(result)}개 항목")
    
    # 파싱된 데이터를 실제로 저장해보기
    print("\n=== 수동 저장 테스트 ===")
    success = 0
    errors = []
    
    for idx, staff_data in enumerate(result):
        try:
            # 기존 레코드 확인
            existing = OutsourcedStaff.objects.filter(
                company_name=staff_data['company_name'],
                project_name=staff_data['project_name'],
                report_date=staff_data['report_date']
            ).first()
            
            if existing:
                print(f"[{idx+1}] 기존 레코드 업데이트: {staff_data['company_name']} - {staff_data['project_name']}")
                for key, value in staff_data.items():
                    setattr(existing, key, value)
                existing.save()
            else:
                print(f"[{idx+1}] 신규 레코드 생성: {staff_data['company_name']} - {staff_data['project_name']}")
                OutsourcedStaff.objects.create(**staff_data)
            
            success += 1
        except Exception as e:
            error_msg = f"[{idx+1}] 오류: {staff_data['company_name']} - {staff_data['project_name']}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\n결과: 성공 {success}개, 실패 {len(errors)}개")
    
    # 최종 데이터베이스 상태
    final_count = OutsourcedStaff.objects.count()
    print(f"\n최종 레코드 수: {final_count}개")
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")