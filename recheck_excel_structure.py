"""
Excel 구조 재확인
"""
import pandas as pd

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    # 헤더 없이 읽기
    df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    print("=== 실제 데이터 구조 (10-20행) ===")
    for i in range(10, min(20, len(df_raw))):
        row = df_raw.iloc[i]
        print(f"\n행 {i}:")
        for j in range(min(8, len(row))):
            val = row.iloc[j]
            if pd.notna(val):
                print(f"  열 {j}: {val}")
    
    # 헤더를 10행으로 설정하고 데이터 읽기
    print("\n\n=== 헤더를 10행으로 설정 후 ===")
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=10)
    
    # ffill을 사용하여 병합된 셀 처리
    df_filled = df.copy()
    df_filled['담당'] = df_filled['담당'].fillna(method='ffill')
    
    print("\n첫 5행 (fillna 후):")
    for i in range(min(5, len(df_filled))):
        row = df_filled.iloc[i]
        print(f"\n행 {i}:")
        print(f"  담당: {row.get('담당')}")
        print(f"  인원: {row.get('인원')}")
        print(f"  내용: {row.get('내용')}")
        
except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()