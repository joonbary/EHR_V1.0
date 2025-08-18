"""
OK_employee_full_data.xlsx를 BulkUploadView 형식으로 변환
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# 원본 파일 읽기
print("원본 Excel 파일 읽기...")
df = pd.read_excel('OK_employee_full_data.xlsx')

# 컬럼명 확인
print("컬럼명:", list(df.columns))
print()

# 새로운 형식으로 변환
simple_df = pd.DataFrame()

# 컬럼 인덱스로 접근 (인코딩 문제 해결)
columns = list(df.columns)

# 이름 (dummy_이름 = 3번 인덱스)
simple_df['이름'] = df[columns[3]] if len(columns) > 3 else 'Unknown'

# 부서 (소속1 = 9번 인덱스)
if len(columns) > 9:
    simple_df['부서'] = df[columns[9]].fillna('경영관리')
    # '-' 값을 실제 부서명으로 변경
    simple_df['부서'] = simple_df['부서'].replace('-', '경영관리')
    simple_df['부서'] = simple_df['부서'].replace('', '경영관리')
else:
    simple_df['부서'] = '경영관리'

# 직급 (현직급 = 17번째 컬럼)
positions_map = {
    '수석': 'SENIOR',
    '책임': 'PRINCIPAL', 
    '선임': 'SENIOR_STAFF',
    '사원': 'STAFF',
    '대리': 'ASSISTANT_MANAGER',
    '과장': 'MANAGER',
    '차장': 'DEPUTY_MANAGER',
    '부장': 'GENERAL_MANAGER'
}

# 직급 변환
if len(columns) > 16:
    simple_df['직급'] = df[columns[16]].apply(lambda x: positions_map.get(x, 'STAFF') if pd.notna(x) else 'STAFF')
else:
    simple_df['직급'] = 'STAFF'

# 입사일 생성 (나이 기반으로 추정)
def generate_hire_date(age):
    if pd.isna(age):
        age = 35
    # 나이에 따라 근속년수 추정
    years_of_service = min(int(age) - 25, 15) if age > 25 else 1
    days_ago = years_of_service * 365 + random.randint(-180, 180)
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

# 입사일 생성 (나이 = 4번 인덱스)
if len(columns) > 4:
    simple_df['입사일'] = df[columns[4]].apply(generate_hire_date)
else:
    simple_df['입사일'] = '2020-01-01'

# 이메일 (dummy_e-mail = 34번 인덱스)
simple_df['이메일'] = df[columns[34]] if len(columns) > 34 else 'unknown@okfg.co.kr'

# 전화번호 (dummy_휴대폰 = 46번 인덱스)
simple_df['전화번호'] = df[columns[46]] if len(columns) > 46 else '010-0000-0000'

# 파일 저장
output_file = 'OK_employee_simple_format.xlsx'
simple_df.to_excel(output_file, index=False)

print(f"\n변환 완료!")
print(f"파일: {output_file}")
print(f"총 {len(simple_df)}개 레코드")
print("\n처음 5개 레코드:")
print(simple_df[['이름', '부서', '직급', '이메일']].head())