"""
emp_upload.xlsx 파일 구조 확인 스크립트
"""
import pandas as pd
from datetime import date

# 파일 읽기
df = pd.read_excel('emp_upload.xlsx')

# 열 이름 직접 설정 (한글 인코딩 문제 해결)
df.columns = ['직급구분', '회사', '직책', '직위']

print("=== 파일 구조 ===")
print(f"총 행 수: {len(df)}")
print(f"열 이름: {list(df.columns)}")
print("\n=== 데이터 샘플 ===")
print(df.head(10))

print("\n=== 각 열의 고유 값 ===")
for col in df.columns:
    print(f"\n{col}:")
    print(df[col].value_counts().head(10))

# 회사별 집계
print("\n=== 회사별 인원수 ===")
company_counts = df['회사'].value_counts()
for company, count in company_counts.items():
    print(f"{company}: {count}명")

# 직급구분별 집계
print("\n=== 직급구분별 인원수 ===")
grade_counts = df['직급구분'].value_counts()
for grade, count in grade_counts.items():
    print(f"{grade}: {count}명")

# 기준일자는 파일에 없으므로 현재 날짜 사용
print(f"\n기준일자 (현재): {date.today()}")