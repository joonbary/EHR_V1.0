"""
전체 파싱 프로세스 테스트
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_system.settings")
import django
django.setup()

from employees.services.excel_parser import HRExcelAutoParser
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    parser = HRExcelAutoParser()
    print("파서 초기화 완료")
    
    results = parser.parse_outsourced_staff(file_path)
    print(f"\n파싱 결과: {len(results)}개 항목")
    
    if results:
        print(f"\n첫 번째 항목:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")
            
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()