"""
Excel 파일을 1000개 이하로 분할
"""

import pandas as pd

# 전체 파일 읽기
df = pd.read_excel('OK_employee_with_dept.xlsx')
total_rows = len(df)

print(f"전체 레코드: {total_rows}개")

# 파일 분할
chunk_size = 900  # 안전하게 900개씩

# 첫 번째 파일 (1-900)
df1 = df.iloc[:chunk_size]
df1.to_excel('OK_employee_part1.xlsx', index=False)
print(f"\n파일 1 생성: OK_employee_part1.xlsx ({len(df1)}개 레코드)")

# 두 번째 파일 (901-1790)
df2 = df.iloc[chunk_size:]
df2.to_excel('OK_employee_part2.xlsx', index=False)
print(f"파일 2 생성: OK_employee_part2.xlsx ({len(df2)}개 레코드)")

# 각 파일의 회사별 통계
print("\n=== 파일 1 회사별 통계 ===")
print(df1['회사'].value_counts())

print("\n=== 파일 2 회사별 통계 ===")
print(df2['회사'].value_counts())

print("\n업로드 순서:")
print("1. OK_employee_part1.xlsx 업로드")
print("2. OK_employee_part2.xlsx 업로드")