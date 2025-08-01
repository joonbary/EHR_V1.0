"""
해외인력 엑셀 파일 구조 분석
"""
import pandas as pd
import os

# 엑셀 파일 경로
file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\employee_global_250801.xlsx"

if os.path.exists(file_path):
    # 엑셀 파일 읽기
    try:
        # 모든 시트 이름 확인
        xl_file = pd.ExcelFile(file_path)
        print("=== 시트 목록 ===")
        for sheet_name in xl_file.sheet_names:
            print(f"- {sheet_name}")
        
        # 첫 번째 시트 데이터 확인
        df = pd.read_excel(file_path, sheet_name=0)
        
        print("\n=== 데이터 구조 ===")
        print(f"행 수: {len(df)}")
        print(f"열 수: {len(df.columns)}")
        
        print("\n=== 처음 10행 원본 데이터 ===")
        for i in range(min(10, len(df))):
            print(f"행 {i}:")
            for j, val in enumerate(df.iloc[i]):
                if pd.notna(val):
                    print(f"  열 {j}: {val}")
        
        # 특정 셀의 값 확인
        print("\n=== 특정 셀 값 확인 ===")
        print(f"B1: {df.iloc[0, 1] if len(df) > 0 else 'N/A'}")
        print(f"B3: {df.iloc[2, 1] if len(df) > 2 else 'N/A'}")
        
        # 법인명이 있을 것으로 예상되는 행 찾기
        print("\n=== 법인명 찾기 ===")
        for i, row in df.iterrows():
            for val in row:
                if pd.notna(val) and any(keyword in str(val) for keyword in ['OK Bank', 'OK Asset', 'PPCB', '천진법인', '캄보디아']):
                    print(f"행 {i}: {val}")
                
    except Exception as e:
        print(f"엑셀 파일 읽기 오류: {e}")
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")