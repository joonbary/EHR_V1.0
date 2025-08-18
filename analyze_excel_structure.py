import pandas as pd
import os

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

if os.path.exists(file_path):
    print(f"파일 확인: {file_path}")
    
    df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    print(f"\n전체 행 수: {len(df_raw)}")
    print(f"전체 열 수: {len(df_raw.columns)}")
    
    # 헤더 확인
    print("\n=== 10행 (헤더) ===")
    for i, val in enumerate(df_raw.iloc[10]):
        print(f"  {i}번 열: '{val}'")
    
    # 1번 열의 고유값 확인
    print("\n=== 1번 열 고유값 ===")
    col1_values = df_raw.iloc[11:, 1].dropna().unique()
    for val in col1_values:
        count = (df_raw.iloc[11:, 1] == val).sum()
        print(f"  '{val}': {count}개")
    
    # 빈 값 카운트
    empty_count = df_raw.iloc[11:, 1].isna().sum()
    print(f"  (빈 값): {empty_count}개")
    
    # 실제 데이터 샘플 확인
    print("\n=== 데이터 샘플 (15개) ===")
    for i in range(11, min(26, len(df_raw))):
        row = df_raw.iloc[i]
        company = row.iloc[0] if pd.notna(row.iloc[0]) else '(이전 회사)'
        staff_type = row.iloc[1] if pd.notna(row.iloc[1]) else '(빈값)'
        headcount = row.iloc[2] if pd.notna(row.iloc[2]) else '(빈값)'
        project = row.iloc[3] if pd.notna(row.iloc[3]) else '(빈값)'
        
        print(f"{i+1}행: {company} | {staff_type} | {headcount} | {project}")
        
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")