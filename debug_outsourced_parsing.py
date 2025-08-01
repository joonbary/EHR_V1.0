"""
외주인력 파싱 디버깅
"""
import pandas as pd
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    # 실제 데이터는 10행부터 시작
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=10)
    
    print("=== 컬럼 정보 ===")
    print(f"컬럼 목록: {list(df.columns)}")
    print(f"전체 행 수: {len(df)}")
    
    print("\n=== 처음 10행 데이터 ===")
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        print(f"\n행 {idx}:")
        for col in df.columns:
            val = row[col]
            if pd.notna(val):
                print(f"  {col}: {val}")
    
    # 실제 파싱 로직 테스트
    print("\n=== 파싱 테스트 ===")
    current_company = None
    staff_count = 0
    
    for idx, row in df.iterrows():
        # 담당 회사 확인
        if pd.notna(row.get('담당')):
            company_value = str(row.get('담당')).strip()
            print(f"\n담당 회사 발견: {company_value}")
            
        # 인원 수가 있는 행 확인
        if pd.notna(row.get('인원')):
            print(f"\n행 {idx}: 인원 = {row.get('인원')}")
            print(f"  Unnamed: 1 = {row.get('Unnamed: 1')}")
            print(f"  내용 = {row.get('내용')}")
            print(f"  업체 = {row.get('업체')}")
            staff_count += 1
            
            if staff_count >= 5:
                break
                
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()