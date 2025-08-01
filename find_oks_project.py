"""
OKS 프로젝트 인력 찾기
"""

import pandas as pd

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

# 헤더 없이 읽기
df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)

print("OKS 관련 행 찾기:")
print("="*50)

for i in range(len(df)):
    row = df.iloc[i]
    row_str = str(row.values)
    
    # OKS가 포함된 행 찾기
    if 'OKS' in row_str or 'OK저축' in row_str:
        print(f"\n행 {i}:")
        for j in range(min(7, len(row))):
            val = row.iloc[j]
            if pd.notna(val):
                print(f"  [{j}]: {val}")
        
        # 다음 몇 행도 출력
        for k in range(i+1, min(i+15, len(df))):
            next_row = df.iloc[k]
            # 프로젝트가 있는지 확인
            if pd.notna(next_row.iloc[1]) and '프로젝트' in str(next_row.iloc[1]):
                print(f"\n>>> 행 {k}에서 프로젝트 발견:")
                for j in range(min(7, len(next_row))):
                    val = next_row.iloc[j]
                    if pd.notna(val):
                        print(f"  [{j}]: {val}")
                
                # 프로젝트 데이터 출력
                for m in range(k+1, min(k+10, len(df))):
                    data_row = df.iloc[m]
                    if pd.notna(data_row.iloc[2]) and pd.notna(data_row.iloc[3]):
                        try:
                            count = int(float(data_row.iloc[2]))
                            if count > 0:
                                print(f"\n프로젝트 데이터 (행 {m}):")
                                for j in range(min(7, len(data_row))):
                                    val = data_row.iloc[j]
                                    if pd.notna(val):
                                        print(f"  [{j}]: {val}")
                        except:
                            pass
                    
                    # 소계나 합계가 나오면 중단
                    if pd.notna(data_row.iloc[1]) and ('소계' in str(data_row.iloc[1]) or '합계' in str(data_row.iloc[1])):
                        break
                break