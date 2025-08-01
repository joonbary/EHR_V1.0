import pandas as pd
import os

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

if os.path.exists(file_path):
    print(f"파일 확인: {file_path}")
    
    df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    print("\n=== 프로젝트 인력 디버깅 ===")
    
    # 전체 데이터에서 프로젝트 관련 행 찾기
    project_rows = []
    
    for i in range(len(df_raw)):
        row_str = ' '.join([str(val) for val in df_raw.iloc[i] if pd.notna(val)])
        if '프로젝트' in row_str:
            project_rows.append(i)
            print(f"\n{i+1}행에서 '프로젝트' 발견:")
            for j in range(min(7, len(df_raw.columns))):
                val = df_raw.iloc[i, j]
                print(f"  {j}번 열: '{val}'")
    
    print(f"\n총 {len(project_rows)}개 행에서 '프로젝트' 키워드 발견")
    
    # 프로젝트 행 주변 데이터 확인
    for row_idx in project_rows:
        print(f"\n=== {row_idx+1}행 주변 데이터 ===")
        start = max(0, row_idx - 2)
        end = min(len(df_raw), row_idx + 5)
        
        for i in range(start, end):
            row = df_raw.iloc[i]
            row_display = f"{i+1}행: "
            for j in range(min(5, len(row))):
                val = row.iloc[j] if pd.notna(row.iloc[j]) else '(빈값)'
                row_display += f"{val} | "
            print(row_display)
            
    # 실제 프로젝트 인력 수 계산
    print("\n=== 프로젝트 인력 집계 ===")
    project_count = 0
    
    for i in range(11, len(df_raw)):
        row = df_raw.iloc[i]
        col1_value = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
        
        # 프로젝트 섹션 찾기
        if col1_value == '프로젝트':
            print(f"\n프로젝트 섹션 시작: {i+1}행")
            # 다음 행부터 데이터 확인
            for j in range(i+1, len(df_raw)):
                data_row = df_raw.iloc[j]
                
                # 소계나 다른 섹션이 나오면 중단
                next_col1 = str(data_row.iloc[1]).strip() if pd.notna(data_row.iloc[1]) else ''
                if '소계' in next_col1 or next_col1 in ['상주', '비상주', '프로젝트']:
                    break
                    
                # 인원수 확인
                if pd.notna(data_row.iloc[2]):
                    try:
                        headcount = int(float(data_row.iloc[2]))
                        project_name = str(data_row.iloc[3]).strip() if pd.notna(data_row.iloc[3]) else ''
                        if headcount > 0 and project_name:
                            project_count += headcount
                            print(f"  {j+1}행: {headcount}명 - {project_name}")
                    except:
                        pass
                        
    print(f"\n총 프로젝트 인력: {project_count}명")
        
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")