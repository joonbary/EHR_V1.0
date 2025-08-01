"""
에러 원인 찾기
"""
from datetime import datetime

# 파일명 예시
file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 250701을 파싱
import re
date_match = re.search(r'(\d{6})', file_path)
if date_match:
    date_str = date_match.group(1)
    print(f"추출된 문자열: {date_str}")
    
    # 이상한 경우 체크
    if "70" in date_str:
        print("70이 포함되어 있음!")
        
# 다른 정규식 패턴으로 시도
pattern2 = r'_(\d{2})(\d{2})(\d{2})'
match2 = re.search(pattern2, file_path)
if match2:
    year, month, day = match2.groups()
    print(f"\n다른 패턴: 년={year}, 월={month}, 일={day}")
    
    # 변환
    full_year = 2000 + int(year)
    month_int = int(month)
    day_int = int(day)
    
    print(f"변환: {full_year}년 {month_int}월 {day_int}일")
    
    # 날짜 생성 테스트
    try:
        date_obj = datetime(full_year, month_int, day_int)
        print(f"성공: {date_obj}")
    except Exception as e:
        print(f"실패: {e}")