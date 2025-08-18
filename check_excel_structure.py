#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
엑셀 파일 구조와 실제 데이터 확인
"""
import pandas as pd
import os

files = ['OK_employee_new_part1_08051039.xlsx']

for file_path in files:
    if not os.path.exists(file_path):
        continue
    
    print(f"\n파일: {file_path}")
    print("=" * 60)
    
    df = pd.read_excel(file_path)
    
    # 컬럼 정보 출력
    print("\n컬럼 정보:")
    for i, col in enumerate(df.columns):
        print(f"  {i}: {col}")
    
    # 처음 3개 행 데이터 확인
    print("\n샘플 데이터 (처음 3행):")
    for idx in range(min(3, len(df))):
        print(f"\n행 {idx}:")
        row = df.iloc[idx]
        for i, val in enumerate(row):
            if pd.notna(val) and str(val).strip():
                print(f"  [{i}] {df.columns[i]}: {val}")
    
    # 부서와 직급 관련 컬럼 찾기
    print("\n부서/직급 관련 컬럼 분석:")
    for i, col in enumerate(df.columns):
        col_str = str(col)
        if any(keyword in col_str for keyword in ['부서', '소속', '조직', '팀', '직급', '직책', '직위']):
            print(f"\n컬럼 {i}: {col}")
            # 고유값 샘플
            unique_vals = df.iloc[:, i].dropna().unique()[:10]
            print(f"  샘플 값: {list(unique_vals)}")