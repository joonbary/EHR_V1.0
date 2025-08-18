"""
OK금융그룹 전체 직원 엑셀 파일 생성
원본 엑셀의 구조를 유지하면서 dummy 필드만 채움
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, date
import os

# 원본 엑셀 파일 경로
original_file = r'C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx'
output_file = r'C:\Users\apro\OneDrive\Desktop\EHR_V1.0\OK_employee_full_data.xlsx'

print("원본 엑셀 파일 읽기 중...")
df = pd.read_excel(original_file)
print(f"총 {len(df)}개 레코드 발견")

# 더미 데이터 생성용 리스트
korean_last_names = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
                     '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍',
                     '노', '양', '고', '문', '손', '배', '백', '허', '유', '남']

korean_first_names_male = ['민준', '서준', '도윤', '예준', '시우', '주원', '하준', '지호', '지후', '준우',
                           '준서', '건우', '현우', '지훈', '우진', '선우', '서진', '민재', '현준', '연우',
                           '정우', '승우', '승현', '시윤', '준혁', '성민', '재윤', '태양', '진우', '한결']

korean_first_names_female = ['서연', '서윤', '지우', '서현', '민서', '하은', '하윤', '윤서', '지유', '지민',
                             '채원', '수아', '지아', '지윤', '다은', '은서', '예은', '수빈', '소율', '예진',
                             '유진', '수연', '예린', '서영', '민지', '하늘', '소연', '지영', '혜원', '채은']

# 한자 리스트는 더 이상 필요없음 (7자리 사번으로 대체)

districts = ['강남구', '서초구', '송파구', '강동구', '종로구', '중구', '용산구', '성동구', 
             '광진구', '동대문구', '중랑구', '성북구', '강북구', '도봉구', '노원구']

# 각 행에 대해 dummy 필드 채우기
print("Dummy 필드 생성 중...")
for index, row in df.iterrows():
    # 성별 확인 (실제 데이터)
    gender = row.get('성별', '남' if random.random() > 0.5 else '여')
    
    # dummy_이름 생성
    if gender == '남':
        last_name = random.choice(korean_last_names)
        first_name = random.choice(korean_first_names_male)
    else:
        last_name = random.choice(korean_last_names)
        first_name = random.choice(korean_first_names_female)
    
    df.at[index, 'dummy_이름'] = f"{last_name}{first_name}"
    
    # dummy_한자 → 7자리 사번 생성
    # 회사별 사번 prefix 설정 (2자리)
    company_prefix = {
        'OK': '10', 'OCI': '20', 'OC': '30', 'OFI': '40',
        'OKDS': '50', 'OKH': '60', 'ON': '70', 'OKIP': '80',
        'OT': '85', 'OKV': '90', 'EX': '99'
    }
    company = row.get('회사', 'OK')
    prefix = company_prefix.get(company, '10')
    
    # 나머지 5자리는 순차적으로 생성 (10001부터 시작)
    employee_number = f"{prefix}{10000 + index:05d}"
    df.at[index, 'dummy_한자'] = employee_number
    
    # dummy_주민번호 생성
    birth_date = row.get('생일')
    if pd.notna(birth_date):
        if isinstance(birth_date, str):
            try:
                birth_date = pd.to_datetime(birth_date)
            except:
                birth_date = None
    
    if birth_date:
        year_2digit = str(birth_date.year)[2:]
        month = f"{birth_date.month:02d}"
        day = f"{birth_date.day:02d}"
    else:
        # 나이를 기준으로 생년 추정
        age = row.get('나이', 35)
        birth_year = datetime.now().year - age
        year_2digit = str(birth_year)[2:]
        month = f"{random.randint(1, 12):02d}"
        day = f"{random.randint(1, 28):02d}"
    
    # 성별에 따른 주민번호 뒷자리 첫 번째 숫자
    if gender == '남':
        gender_digit = random.choice(['1', '3'])  # 1900년대생 또는 2000년대생
    else:
        gender_digit = random.choice(['2', '4'])
    
    # 나머지 6자리는 랜덤
    remaining = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    df.at[index, 'dummy_주민번호'] = f"{year_2digit}{month}{day}-{gender_digit}{remaining}"
    
    # dummy_휴대폰 생성
    df.at[index, 'dummy_휴대폰'] = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    # dummy_주민등록주소 생성
    district = random.choice(districts)
    df.at[index, 'dummy_주민등록주소'] = f"서울특별시 {district} {random.choice(['대로', '로', '길'])} {random.randint(1, 200)} {random.randint(1, 50)}동 {random.randint(100, 2000)}호"
    
    # dummy_실거주지주소 생성 (70% 확률로 주민등록주소와 동일)
    if random.random() < 0.7:
        df.at[index, 'dummy_실거주지주소'] = df.at[index, 'dummy_주민등록주소']
    else:
        district2 = random.choice(districts)
        df.at[index, 'dummy_실거주지주소'] = f"서울특별시 {district2} {random.choice(['대로', '로', '길'])} {random.randint(1, 200)} {random.randint(1, 50)}동 {random.randint(100, 2000)}호"
    
    # dummy_e-mail 생성
    no = row.get('NO', index + 1)
    company = row.get('회사', 'OK')
    email_domains = {
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
    domain = email_domains.get(company, 'okfg.co.kr')
    df.at[index, 'dummy_e-mail'] = f"emp{no:04d}@{domain}"
    
    if (index + 1) % 100 == 0:
        print(f"  진행: {index + 1}/{len(df)}")

# 엑셀 파일로 저장
print(f"\n엑셀 파일 저장 중: {output_file}")
df.to_excel(output_file, index=False, engine='openpyxl')

# 결과 확인
print("\n" + "="*60)
print("✅ 엑셀 파일 생성 완료!")
print(f"📁 파일 위치: {output_file}")
print(f"📊 총 레코드 수: {len(df)}")

# 회사별 통계
print("\n회사별 직원 수:")
company_counts = df['회사'].value_counts()
for company, count in company_counts.items():
    print(f"  {company}: {count}명")

print("\n이제 이 파일을 사용하여:")
print("1. https://ehrv10-production.up.railway.app/employees/bulk-upload/ 접속")
print("2. 생성된 엑셀 파일 업로드")
print("3. 미리보기 확인 후 저장")

print("\n또는 Railway CLI에서:")
print("railway run python manage.py load_okfg_excel --excel-path=OK_employee_full_data.xlsx")