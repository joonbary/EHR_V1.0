"""
올바른 파싱 테스트
"""
import pandas as pd
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽기
df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("=== 원본 데이터 (10-15행) ===")
for i in range(10, 16):
    row = df_raw.iloc[i]
    print(f"행 {i}: ", end="")
    for j in range(min(7, len(row))):
        if pd.notna(row.iloc[j]):
            print(f"{j}:{row.iloc[j]} ", end="")
    print()

# 10행을 헤더로, 11행부터 데이터
# 하지만 첫 번째 데이터 행에 OKDS가 있음
staff_list = []
current_company = None
report_date = datetime(2025, 7, 1).date()

# 11행부터 처리
for i in range(11, len(df_raw)):
    row = df_raw.iloc[i]
    
    # 0번 열: 담당 회사
    if pd.notna(row.iloc[0]):
        company_value = str(row.iloc[0]).strip()
        if 'OKDS' in company_value:
            current_company = 'OK데이터시스템'
        elif 'OK' in company_value:
            current_company = 'OK홀딩스'
        elif 'OC' in company_value:
            current_company = 'OK캐피탈'
        elif 'OKS' in company_value:
            current_company = 'OK저축은행'
        else:
            current_company = company_value
        print(f"\n회사: {current_company}")
    
    # 2번 열: 인원
    if pd.notna(row.iloc[2]):
        try:
            headcount = int(float(row.iloc[2]))
            
            # 1번 열: 상주/비상주
            resident_type = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
            is_resident = '비상주' not in resident_type
            
            # 소계는 건너뛰기
            if '소계' in resident_type:
                continue
            
            # 3번 열: 내용/프로젝트명
            project_name = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ''
            
            # 4번 열: 업체
            vendor = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ''
            
            if current_company and project_name:
                staff = {
                    'company_name': current_company,
                    'project_name': f"{project_name} ({vendor})" if vendor else project_name,
                    'is_resident': is_resident,
                    'headcount': headcount,
                    'report_date': report_date
                }
                staff_list.append(staff)
                print(f"  추가: {project_name} - {headcount}명 ({'상주' if is_resident else '비상주'})")
                
        except:
            pass

print(f"\n\n총 {len(staff_list)}개 항목")

# 회사별 집계
companies = {}
for staff in staff_list:
    company = staff['company_name']
    if company not in companies:
        companies[company] = {'상주': 0, '비상주': 0}
    
    if staff['is_resident']:
        companies[company]['상주'] += staff['headcount']
    else:
        companies[company]['비상주'] += staff['headcount']

print("\n=== 회사별 집계 ===")
for company, counts in companies.items():
    print(f"{company}: 상주 {counts['상주']}명, 비상주 {counts['비상주']}명")