"""
단계별 파싱 테스트
"""
import pandas as pd
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽어서 직접 처리
df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

# 10행이 헤더, 11행부터 데이터
headers = df_raw.iloc[10].values
df = df_raw.iloc[11:].copy()
df.columns = headers
df.reset_index(drop=True, inplace=True)

# 컬럼명 정규화
df.columns = [col.strip() if isinstance(col, str) else str(col) for col in df.columns]

print("=== 컬럼 정보 ===")
print(f"컬럼: {list(df.columns)}")
print(f"데이터 행 수: {len(df)}")

print("\n=== 첫 5행 데이터 ===")
for i in range(min(5, len(df))):
    row = df.iloc[i]
    print(f"\n행 {i}:")
    print(f"  담당: {row.get('담당')}")
    print(f"  Unnamed: 1: {row.get('Unnamed: 1')}")
    print(f"  인원: {row.get('인원')}")
    print(f"  내용: {row.get('내용')}")
    print(f"  업체: {row.get('업체')}")

# 파싱 테스트
staff_list = []
current_company = None

for idx, row in df.iterrows():
    # 담당 회사 업데이트
    if pd.notna(row.get('담당')):
        company_value = str(row.get('담당')).strip()
        print(f"\n[회사 발견] {company_value}")
        if 'OKDS' in company_value:
            current_company = 'OK데이터시스템'
        else:
            current_company = company_value
    
    # 인원 수가 있는 행만 처리
    if pd.notna(row.get('인원')):
        headcount = int(float(row.get('인원')))
        project_name = str(row.get('내용', '')).strip() if pd.notna(row.get('내용')) else ''
        
        if current_company and project_name:
            print(f"  -> 추가: {current_company} - {project_name} ({headcount}명)")
            staff_list.append({
                'company_name': current_company,
                'project_name': project_name,
                'headcount': headcount
            })

print(f"\n\n총 {len(staff_list)}개 항목 파싱됨")