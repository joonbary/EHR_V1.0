"""
Excel 파싱만 테스트
"""

import pandas as pd
import os

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽기
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("=== Excel 파일 프로젝트 섹션 분석 ===\n")

current_company = None
current_section = 'resident'
project_count = 0
project_details = []

for i in range(11, len(df)):  # 11행부터 시작
    row = df.iloc[i]
    
    # 회사명 감지
    if pd.notna(row.iloc[0]):
        company = str(row.iloc[0]).strip()
        if company in ['OKDS', 'OKIP', 'OC', 'OK'] or 'OK' in company:
            current_company = company
            print(f"\n회사 변경: {company} (행 {i})")
    
    # 섹션 변경 감지
    if pd.notna(row.iloc[1]):
        section = str(row.iloc[1]).strip()
        if '프로젝트' in section:
            current_section = 'project'
            print(f"  → 프로젝트 섹션 시작 (행 {i}): '{section}'")
        elif '상주' in section:
            current_section = 'resident'
            print(f"  → 상주 섹션으로 변경 (행 {i})")
        elif '비상주' in section:
            current_section = 'non_resident'
            print(f"  → 비상주 섹션으로 변경 (행 {i})")
    
    # 프로젝트 데이터 수집
    if current_section == 'project' and pd.notna(row.iloc[2]):
        try:
            count = int(float(row.iloc[2]))
            if count > 0 and pd.notna(row.iloc[3]):
                project_name = str(row.iloc[3]).strip()
                vendor = str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else ''
                
                print(f"    [프로젝트 발견] {current_company} - {project_name} ({vendor}): {count}명")
                project_count += count
                project_details.append({
                    'company': current_company,
                    'project': project_name,
                    'vendor': vendor,
                    'count': count,
                    'row': i
                })
        except:
            pass

print(f"\n\n=== 프로젝트 인력 총계: {project_count}명 ===")
print("\n상세 내역:")
for p in project_details:
    print(f"  - {p['company']} | {p['project']} ({p['vendor']}): {p['count']}명 (행 {p['row']})")