"""
외주인력 파싱 문제 해결
"""
import pandas as pd
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    # 실제 데이터는 10행부터 시작
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=10)
    
    print("=== 디버깅 정보 ===")
    print(f"첫 번째 행 '담당' 값: {df.iloc[0].get('담당')}")
    print(f"첫 번째 행 '내용' 값: {df.iloc[0].get('내용')}")
    print(f"첫 번째 행 '인원' 값: {df.iloc[0].get('인원')}")
    
    # 문자열 인코딩 문제 확인
    if pd.notna(df.iloc[0].get('내용')):
        content = str(df.iloc[0].get('내용'))
        print(f"\n내용 문자열 길이: {len(content)}")
        print(f"내용 repr: {repr(content)}")
    
    # 모든 컬럼명 출력
    print("\n=== 모든 컬럼명 (repr) ===")
    for col in df.columns:
        print(f"'{col}' -> {repr(col)}")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()