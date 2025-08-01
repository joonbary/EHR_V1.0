"""
모든 프로젝트 인력 찾기
"""

import pandas as pd

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽기
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("모든 '프로젝트' 섹션 찾기:")
print("="*50)

project_total = 0
current_company = None

for i in range(len(df)):
    row = df.iloc[i]
    
    # 회사명 업데이트
    if pd.notna(row.iloc[0]):
        company = str(row.iloc[0]).strip()
        if any(k in company for k in ['OKDS', 'OKIP', 'OC', 'OKS', 'OK']):
            current_company = company
            print(f"\n=== 회사: {company} (행 {i}) ===")
    
    # 프로젝트 섹션 찾기
    if pd.notna(row.iloc[1]) and '프로젝트' in str(row.iloc[1]):
        print(f"\n프로젝트 섹션 발견 (행 {i}):")
        print(f"  현재 회사: {current_company}")
        print(f"  1번 열: {row.iloc[1]}")
        
        # 다음 행들에서 프로젝트 데이터 찾기
        for j in range(i+1, min(i+10, len(df))):
            data_row = df.iloc[j]
            
            # 인원수가 있는 행 찾기
            if pd.notna(data_row.iloc[2]):
                try:
                    count = int(float(data_row.iloc[2]))
                    if count > 0 and pd.notna(data_row.iloc[3]):
                        print(f"  - 프로젝트: {data_row.iloc[3]} / 인원: {count} (행 {j})")
                        project_total += count
                except:
                    pass
            
            # 소계나 다른 섹션이 나오면 중단
            if pd.notna(data_row.iloc[1]) and any(k in str(data_row.iloc[1]) for k in ['소계', '상주', '비상주']):
                break

print(f"\n\n총 프로젝트 인력: {project_total}명")