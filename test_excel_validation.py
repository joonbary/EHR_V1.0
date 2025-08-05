"""
Excel 파일 검증 테스트
"""

import pandas as pd
from utils.file_manager import ExcelFileHandler

# Excel 파일 읽기
df = pd.read_excel('OK_employee_simple_format.xlsx')

print("Excel 파일 정보:")
print(f"- 총 레코드: {len(df)}")
print(f"- 컬럼: {list(df.columns)}")
print()

# 필수 컬럼 확인
required_columns = ['이름', '이메일', '부서', '직급']
missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    print(f"❌ 필수 컬럼 누락: {missing_columns}")
else:
    print("✅ 모든 필수 컬럼 존재")

# 첫 5개 레코드 확인
print("\n첫 5개 레코드:")
for idx, row in df.head(5).iterrows():
    print(f"{idx+1}. 이름={row.get('이름')}, 부서={row.get('부서')}, 직급={row.get('직급')}, 이메일={row.get('이메일')}")

# 빈 값 확인
print("\n빈 값 확인:")
for col in ['이름', '이메일', '부서', '직급']:
    null_count = df[col].isna().sum()
    empty_count = (df[col] == '').sum()
    print(f"- {col}: NaN={null_count}, 빈문자열={empty_count}")

# 부서가 '-'인 경우 확인
dash_dept = (df['부서'] == '-').sum()
print(f"\n부서가 '-'인 레코드: {dash_dept}개")

# 직급 값 확인
print("\n직급 분포:")
print(df['직급'].value_counts().head(10))