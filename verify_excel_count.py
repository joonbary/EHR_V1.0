#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
엑셀 파일의 실제 유효 직원 수 확인
"""
import pandas as pd
import os

files = [
    'OK_employee_new_part1_08051039.xlsx',
    'OK_employee_new_part2_08051039.xlsx',
]

total_valid = 0
all_emails = set()

for file_path in files:
    if not os.path.exists(file_path):
        print(f"파일 없음: {file_path}")
        continue
    
    print(f"\n파일: {file_path}")
    df = pd.read_excel(file_path)
    print(f"  전체 행: {len(df)}")
    
    valid_count = 0
    for idx, row in df.iterrows():
        name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
        
        # 유효한 데이터만 카운트
        if name and name not in ['성명', '이름', 'nan'] and email and '@' in email:
            valid_count += 1
            all_emails.add(email)
    
    print(f"  유효한 직원: {valid_count}명")
    total_valid += valid_count

print(f"\n" + "=" * 60)
print(f"총 유효 직원 수: {total_valid}명")
print(f"고유 이메일 수: {len(all_emails)}개")

# 중복 확인
if total_valid != len(all_emails):
    print(f"중복 이메일: {total_valid - len(all_emails)}개")
else:
    print("중복 이메일 없음")