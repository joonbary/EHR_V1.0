#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
엑셀 파일에서 중복 이메일 찾기
"""
import pandas as pd
import os
from collections import Counter

files = [
    'OK_employee_new_part1_08051039.xlsx',
    'OK_employee_new_part2_08051039.xlsx',
]

all_records = []

for file_path in files:
    if not os.path.exists(file_path):
        continue
    
    df = pd.read_excel(file_path)
    
    for idx, row in df.iterrows():
        name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
        email = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
        
        if name and name not in ['성명', '이름', 'nan'] and email and '@' in email:
            all_records.append((name, email, file_path))

# 이메일별로 카운트
email_counts = Counter([r[1] for r in all_records])

# 중복된 이메일 찾기
duplicates = {email: count for email, count in email_counts.items() if count > 1}

print(f"전체 레코드: {len(all_records)}개")
print(f"고유 이메일: {len(email_counts)}개")
print(f"중복 이메일: {len(duplicates)}개")

if duplicates:
    print("\n중복 이메일 샘플 (상위 10개):")
    for email, count in list(duplicates.items())[:10]:
        print(f"  {email}: {count}번 중복")
        # 해당 이메일의 레코드들 표시
        for name, rec_email, file in all_records:
            if rec_email == email:
                print(f"    - {name} ({file.split('_')[-1][:5]})")

# 파일별 중복 확인
print("\n파일별 분석:")
for file_path in files:
    file_records = [(n, e) for n, e, f in all_records if f == file_path]
    file_emails = [e for n, e in file_records]
    unique_emails = set(file_emails)
    print(f"{file_path}:")
    print(f"  전체: {len(file_records)}개")
    print(f"  고유: {len(unique_emails)}개")
    print(f"  파일 내 중복: {len(file_records) - len(unique_emails)}개")