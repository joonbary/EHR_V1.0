"""
날짜 파싱 테스트
"""
import re
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 현재 로직 테스트
date_match = re.search(r'(\d{6})', file_path)
if date_match:
    date_str = date_match.group(1)
    print(f"추출된 문자열: {date_str}")
    
    # 문자열 분리
    year_part = date_str[:2]
    month_part = date_str[2:4]
    day_part = date_str[4:6]
    
    print(f"연도 부분: {year_part}")
    print(f"월 부분: {month_part}")
    print(f"일 부분: {day_part}")
    
    # 변환
    year = 2000 + int(year_part)
    month = int(month_part)
    day = int(day_part)
    
    print(f"\n변환 결과: {year}년 {month}월 {day}일")
    
    try:
        report_date = datetime(year, month, day).date()
        print(f"날짜 객체: {report_date}")
    except Exception as e:
        print(f"오류: {e}")

# 다른 패턴 테스트
date_match2 = re.search(r'_(\d{6})\.', file_path)
if date_match2:
    print(f"\n다른 패턴으로 추출: {date_match2.group(1)}")