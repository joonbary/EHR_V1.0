"""
중복되지 않는 새로운 이메일로 Excel 재생성
"""

import pandas as pd
import random
from datetime import datetime

# 기존 파일들 읽기
df1 = pd.read_excel('OK_employee_part1.xlsx')
df2 = pd.read_excel('OK_employee_part2.xlsx')

# 전체 데이터 합치기
df = pd.concat([df1, df2], ignore_index=True)

# 새로운 이메일 생성 (타임스탬프 포함)
timestamp = datetime.now().strftime('%m%d')

for index, row in df.iterrows():
    company = row['회사']
    # 회사별 도메인
    domains = {
        'OK': 'okfg.co.kr',
        'OCI': 'okci.co.kr', 
        'OC': 'okcapital.co.kr',
        'OFI': 'okfi.co.kr',
        'OKDS': 'okds.co.kr',
        'OKH': 'okholdings.co.kr',
        'ON': 'oknetworks.co.kr',
        'OKIP': 'okip.co.kr',
        'OT': 'oktrust.co.kr',
        'OKV': 'okventures.co.kr',
        'EX': 'okex.co.kr'
    }
    domain = domains.get(company, 'okfg.co.kr')
    
    # 새로운 이메일: emp + 타임스탬프 + 순번
    df.at[index, '이메일'] = f"emp{timestamp}{index+1:04d}@{domain}"

# dummy_ssn 관련 컬럼이 있다면 제거
columns_to_remove = [col for col in df.columns if 'dummy_ssn' in col.lower() or '주민번호' in col]
if columns_to_remove:
    df = df.drop(columns=columns_to_remove)
    print(f"제거된 컬럼: {columns_to_remove}")

# 다시 분할
df1_new = df.iloc[:900]
df2_new = df.iloc[900:]

# 저장
df1_new.to_excel('OK_employee_new_part1.xlsx', index=False)
df2_new.to_excel('OK_employee_new_part2.xlsx', index=False)

print(f"새로운 파일 생성 완료!")
print(f"Part 1: {len(df1_new)}개 레코드")
print(f"Part 2: {len(df2_new)}개 레코드")
print(f"\n샘플 이메일:")
print(df1_new['이메일'].head(5).tolist())