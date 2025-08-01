"""
월간 인력현황 엑셀 파일 분석
"""
import pandas as pd
import numpy as np
import os

file_path = r'C:\Users\apro\OneDrive\Desktop\인사자료\월간인력현황 _ 250703 - 02.송부용.xlsx'

if os.path.exists(file_path):
    # 시트별로 데이터 분석
    xl_file = pd.ExcelFile(file_path)
    
    # 인력현황 시트 분석
    df = pd.read_excel(file_path, sheet_name='인력현황', header=None)
    
    print("=== 인력현황 시트 구조 ===")
    print(f"전체 크기: {df.shape}")
    
    # 헤더 부분 확인 (첫 몇 행)
    print("\n=== 상단 10행 ===")
    for i in range(min(10, len(df))):
        row_data = []
        for j in range(min(10, len(df.columns))):
            val = df.iloc[i, j]
            if pd.notna(val):
                row_data.append(str(val))
        if row_data:
            print(f"Row {i}: {' | '.join(row_data)}")
    
    # 회사명이 있는 열 찾기
    print("\n=== 회사명 찾기 ===")
    for col_idx in range(len(df.columns)):
        col_data = df.iloc[:, col_idx]
        unique_vals = col_data.dropna().unique()
        if len(unique_vals) > 0:
            # 회사명 패턴 확인
            for val in unique_vals:
                if 'OK' in str(val) or '은행' in str(val) or '캐피탈' in str(val):
                    print(f"Column {col_idx}: {val}")
                    break
    
    # 데이터가 시작되는 행 찾기
    print("\n=== 데이터 시작 위치 찾기 ===")
    for row_idx in range(len(df)):
        row_data = df.iloc[row_idx]
        non_null_count = row_data.notna().sum()
        if non_null_count > 20:  # 데이터가 많은 행
            print(f"Row {row_idx}: {non_null_count} non-null values")
            print(f"Sample data: {list(row_data.dropna().head(5))}")
            if row_idx > 5:
                break
    
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")