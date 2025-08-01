import pandas as pd
import os

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

if os.path.exists(file_path):
    print(f"파일 확인: {file_path}")
    
    df_raw = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    print(f"\n전체 행 수: {len(df_raw)}")
    print(f"전체 열 수: {len(df_raw.columns)}")
    
    print("\n=== 10행 (헤더) ===")
    print(df_raw.iloc[10])
    
    staff_counts = {'상주': 0, '비상주': 0, '프로젝트': 0, '기타': 0}
    details = []
    
    print("\n=== 데이터 분석 ===")
    current_company = None
    
    for i in range(11, len(df_raw)):
        row = df_raw.iloc[i]
        
        if pd.notna(row.iloc[0]):
            current_company = str(row.iloc[0]).strip()
        
        if pd.notna(row.iloc[2]):
            try:
                headcount = int(float(row.iloc[2]))
            except:
                continue
                
            staff_type_str = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ''
            project_name = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else ''
            
            if headcount > 0 and project_name and '소계' not in staff_type_str and '합계' not in staff_type_str:
                detail = {
                    'row': i + 1,
                    'company': current_company,
                    'type_col': staff_type_str,
                    'headcount': headcount,
                    'project': project_name[:30] + '...' if len(project_name) > 30 else project_name
                }
                details.append(detail)
                
                if '비상주' in staff_type_str:
                    staff_counts['비상주'] += headcount
                elif '프로젝트' in staff_type_str:
                    staff_counts['프로젝트'] += headcount
                elif staff_type_str == '' or '상주' in staff_type_str:
                    staff_counts['상주'] += headcount
                else:
                    staff_counts['기타'] += headcount
    
    print(f"\n=== 파싱 결과 요약 ===")
    print(f"상주: {staff_counts['상주']}명")
    print(f"비상주: {staff_counts['비상주']}명") 
    print(f"프로젝트: {staff_counts['프로젝트']}명")
    print(f"기타: {staff_counts['기타']}명")
    print(f"총 인원: {sum(staff_counts.values())}명")
    
    print(f"\n=== 처음 10개 데이터 ===")
    for i, detail in enumerate(details[:10]):
        print(f"{detail['row']}행: {detail['company']} | '{detail['type_col']}' | {detail['headcount']}명 | {detail['project']}")
    
    print(f"\n=== 비상주 데이터 ===")
    non_resident = [d for d in details if '비상주' in d['type_col']]
    for detail in non_resident[:5]:
        print(f"{detail['row']}행: {detail['company']} | '{detail['type_col']}' | {detail['headcount']}명")
    
    print(f"\n=== 프로젝트 데이터 ===")
    project = [d for d in details if '프로젝트' in d['type_col']]
    for detail in project[:5]:
        print(f"{detail['row']}행: {detail['company']} | '{detail['type_col']}' | {detail['headcount']}명")
        
else:
    print(f"파일을 찾을 수 없습니다: {file_path}")