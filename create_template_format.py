"""
템플릿과 동일한 형식으로 1790명 데이터 생성
"""

import pandas as pd
from datetime import datetime, timedelta
import random

# 원본 파일 읽기
print("원본 Excel 파일 읽기...")
df_original = pd.read_excel('OK_employee_full_data.xlsx')

# 새로운 형식으로 변환
data = []
columns = list(df_original.columns)

for index, row in df_original.iterrows():
    # 기본 정보
    name = row[columns[3]] if len(columns) > 3 else f"직원{index+1}"  # dummy_이름
    email = row[columns[34]] if len(columns) > 34 else f"emp{index+1:04d}@okfg.co.kr"  # dummy_e-mail
    phone = row[columns[46]] if len(columns) > 46 else "010-0000-0000"  # dummy_휴대폰
    
    # 회사 정보
    company = row[columns[6]] if len(columns) > 6 else 'OK'  # 회사
    headquarters1 = row[columns[7]] if len(columns) > 7 else 'IT본부'  # 본부1
    headquarters2 = row[columns[8]] if len(columns) > 8 else ''  # 본부2
    
    # 소속 정보
    dept1 = row[columns[9]] if len(columns) > 9 else '경영관리'  # 소속1(본부)
    dept2 = row[columns[10]] if len(columns) > 10 else ''  # 소속2(부)
    dept3 = row[columns[11]] if len(columns) > 11 else ''  # 소속3(그룹/테스크/센터)
    
    # 최종소속 결정
    final_dept = dept3 if pd.notna(dept3) and str(dept3).strip() else (
        dept2 if pd.notna(dept2) and str(dept2).strip() else (
            dept1 if pd.notna(dept1) and str(dept1).strip() else '경영관리'
        )
    )
    
    # 직급/직책
    position = row[columns[16]] if len(columns) > 16 else '사원'  # 현직급
    responsibility = row[columns[17]] if len(columns) > 17 else ''  # 직책
    
    # 개인 정보
    gender = row[columns[5]] if len(columns) > 5 else 'M'  # 성별
    age = row[columns[4]] if len(columns) > 4 else 35  # 나이
    
    # 입사일 생성
    if pd.notna(age):
        try:
            age_int = int(age)
            years_of_service = min(age_int - 25, 15) if age_int > 25 else 1
            days_ago = years_of_service * 365 + random.randint(-180, 180)
            hire_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        except:
            hire_date = '2020-01-01'
    else:
        hire_date = '2020-01-01'
    
    # 직군/직종
    job_group = 'PL' if position in ['팀장', '지점장', '본부장'] else 'Non-PL'
    job_types = ['IT개발', 'IT기획', 'IT운영', '경영관리', '기업영업', '기업금융', '리테일금융', '투자금융', '고객지원']
    job_type = random.choice(job_types)
    
    # 데이터 행 생성 (템플릿과 동일한 순서)
    data.append([
        name,           # 이름
        email,          # 이메일
        hire_date,      # 입사일
        phone,          # 전화번호
        company,        # 회사
        headquarters1,  # 본부1
        headquarters2,  # 본부2
        final_dept,     # 최종소속
        position,       # 직급
        responsibility, # 직책
        gender,         # 성별
        int(age) if pd.notna(age) else 35,  # 나이
        '재직',         # 재직상태
        job_group,      # 직군/계열
        job_type        # 직종
    ])

# DataFrame 생성
template_columns = ['이름', '이메일', '입사일', '전화번호', '회사', '본부1', '본부2', 
                   '최종소속', '직급', '직책', '성별', '나이', '재직상태', '직군/계열', '직종']
df_new = pd.DataFrame(data, columns=template_columns)

# 파일 저장
output_file = 'OK_employee_template_format.xlsx'
df_new.to_excel(output_file, index=False)

print(f"\n✅ 파일 생성 완료!")
print(f"📁 파일: {output_file}")
print(f"📊 총 {len(df_new)}개 레코드")
print("\n처음 5개 레코드:")
print(df_new.head())

# 회사별 통계
print("\n회사별 통계:")
print(df_new['회사'].value_counts())