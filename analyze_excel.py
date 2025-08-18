import pandas as pd
import json
import sys
import io

# stdout 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 엑셀 파일 읽기
excel_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK_dummy_employee_250801.xlsx"
df = pd.read_excel(excel_path)

print("=" * 100)
print("엑셀 파일 분석 결과")
print("=" * 100)

# 기본 정보
print(f"\n총 행 수: {len(df)}")
print(f"총 열 수: {len(df.columns)}")

# 컬럼 정보
print("\n컬럼 목록:")
print("-" * 80)
for i, col in enumerate(df.columns, 1):
    dtype = df[col].dtype
    null_count = df[col].isnull().sum()
    unique_count = df[col].nunique()
    print(f"{i:3}. {col:30} | 타입: {str(dtype):10} | Null: {null_count:4} | 고유값: {unique_count:4}")

# dummy_ 로 시작하는 컬럼 확인
dummy_columns = [col for col in df.columns if col.startswith('dummy_')]
print(f"\n\ndummy_ 컬럼 수: {len(dummy_columns)}")
print("dummy_ 컬럼 목록:")
for col in dummy_columns:
    print(f"  - {col}")

# 샘플 데이터 출력 (처음 5행)
print("\n\n샘플 데이터 (처음 5행):")
print("-" * 80)
print(df.head().to_string())

# 부서별 인원 현황
if 'div_nm' in df.columns:
    print("\n\n부서별 인원 현황:")
    print("-" * 80)
    dept_count = df['div_nm'].value_counts()
    for dept, count in dept_count.items():
        print(f"{dept}: {count}명")

# 직급별 인원 현황
if 'class_nm' in df.columns:
    print("\n\n직급별 인원 현황:")
    print("-" * 80)
    position_count = df['class_nm'].value_counts()
    for position, count in position_count.items():
        print(f"{position}: {count}명")

# 직종별 인원 현황
if 'jtype_nm' in df.columns:
    print("\n\n직종별 인원 현황:")
    print("-" * 80)
    jtype_count = df['jtype_nm'].value_counts()
    for jtype, count in jtype_count.items():
        print(f"{jtype}: {count}명")

# 데이터 유형 요약
print("\n\n데이터 유형 요약:")
print("-" * 80)
print(df.dtypes.value_counts())

# 컬럼을 JSON으로 저장
columns_info = {
    "total_rows": len(df),
    "total_columns": len(df.columns),
    "columns": list(df.columns),
    "dummy_columns": dummy_columns,
    "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
}

with open('excel_columns_info.json', 'w', encoding='utf-8') as f:
    json.dump(columns_info, f, ensure_ascii=False, indent=2)

print("\n\ncolumns 정보가 excel_columns_info.json에 저장되었습니다.")