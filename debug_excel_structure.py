"""
Excel 파일 구조 디버깅
"""

import pandas as pd
import os

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽기
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print(f"전체 행 수: {len(df)}")
print("\n" + "="*100 + "\n")

# 각 행을 출력
for i in range(len(df)):
    row = df.iloc[i]
    row_str = []
    for j in range(min(7, len(row))):
        val = row.iloc[j]
        if pd.notna(val):
            row_str.append(f"[{j}]: {str(val).strip()}")
        else:
            row_str.append(f"[{j}]: -")
    
    print(f"행 {i:02d}: {' | '.join(row_str)}")
    
    # 특정 키워드가 있는 행은 강조
    if pd.notna(row.iloc[0]):
        if any(keyword in str(row.iloc[0]) for keyword in ['OKDS', 'OKIP', 'OC', 'OKS', 'OK']):
            print("    >>> 회사 시작!")
    
    if pd.notna(row.iloc[1]):
        if any(keyword in str(row.iloc[1]) for keyword in ['상주', '비상주', '프로젝트']):
            print(f"    >>> 섹션 변경: {row.iloc[1]}")