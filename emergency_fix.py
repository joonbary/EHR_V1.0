#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
긴급 직원 데이터 수정
"""
import pandas as pd

# 엑셀 파일 읽기
file1 = 'OK_employee_new_part1_08051039.xlsx'
file2 = 'OK_employee_new_part2_08051039.xlsx'

print("엑셀 파일 확인:")

# 파일 1
df1 = pd.read_excel(file1)
print(f"\n{file1}:")
print(f"  - 총 {len(df1)}명")
print(f"  - 컬럼: {list(df1.columns)}")
print("\n샘플 데이터 (처음 3명):")
for idx in range(min(3, len(df1))):
    row = df1.iloc[idx]
    print(f"  {idx+1}. 이름: {row.get('성명', '없음')}, 이메일: {row.get('이메일', '없음')}, 회사: {row.get('회사', '없음')}, 부서: {row.get('최종소속', '없음')}")

# 파일 2  
df2 = pd.read_excel(file2)
print(f"\n{file2}:")
print(f"  - 총 {len(df2)}명")
print(f"  - 컬럼: {list(df2.columns)}")
print("\n샘플 데이터 (처음 3명):")
for idx in range(min(3, len(df2))):
    row = df2.iloc[idx]
    print(f"  {idx+1}. 이름: {row.get('성명', '없음')}, 이메일: {row.get('이메일', '없음')}, 회사: {row.get('회사', '없음')}, 부서: {row.get('최종소속', '없음')}")

print(f"\n전체 직원 수: {len(df1) + len(df2)}명")