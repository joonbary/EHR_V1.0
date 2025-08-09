#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
엑셀 파일 구조 상세 분석
"""
import pandas as pd
import os

def inspect_excel_files():
    """모든 엑셀 파일 구조 분석"""
    
    excel_files = [
        'emp_upload_250801.xlsx',
        'OK_employee_new_part1_08051039.xlsx',
        'OK_employee_new_part2_08051039.xlsx',
    ]
    
    for file_path in excel_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"\n{'='*80}")
        print(f"파일: {file_path}")
        print('='*80)
        
        try:
            # 헤더 있는 버전
            df_with_header = pd.read_excel(file_path)
            print(f"\n[헤더 있는 버전]")
            print(f"컬럼 수: {len(df_with_header.columns)}")
            print(f"행 수: {len(df_with_header)}")
            print(f"컬럼명 (처음 10개): {list(df_with_header.columns)[:10]}")
            print(f"\n첫 3행:")
            print(df_with_header.head(3))
            
            # 헤더 없는 버전
            df_no_header = pd.read_excel(file_path, header=None)
            print(f"\n[헤더 없는 버전]")
            print(f"컬럼 수: {len(df_no_header.columns)}")
            print(f"행 수: {len(df_no_header)}")
            print(f"\n첫 5행 (인덱스로 접근):")
            for i in range(min(5, len(df_no_header))):
                row = df_no_header.iloc[i]
                print(f"\n행 {i}:")
                for j in range(min(10, len(row))):
                    val = row.iloc[j]
                    if pd.notna(val):
                        print(f"  컬럼{j}: {str(val)[:50]}")
        
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    inspect_excel_files()