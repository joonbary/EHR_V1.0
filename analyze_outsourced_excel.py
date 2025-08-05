"""
외주 현황 Excel 파일 구조 분석
"""
import pandas as pd
import numpy as np

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    # Excel 파일의 모든 시트 확인
    xls = pd.ExcelFile(file_path)
    print(f"시트 목록: {xls.sheet_names}")
    print("=" * 80)
    
    for sheet_name in xls.sheet_names:
        print(f"\n[{sheet_name} 시트 분석]")
        
        # 시트 읽기 (헤더 없이)
        df_raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        print(f"전체 크기: {df_raw.shape}")
        
        # 처음 20행 출력하여 구조 파악
        print("\n처음 20행:")
        for i in range(min(20, len(df_raw))):
            row_values = []
            for j in range(min(10, len(df_raw.columns))):
                val = df_raw.iloc[i, j]
                if pd.notna(val):
                    row_values.append(f"{j}: {val}")
            if row_values:
                print(f"행 {i}: {' | '.join(row_values)}")
        
        # 헤더로 보이는 행 찾기
        print("\n헤더 후보 행 검색:")
        for i in range(min(30, len(df_raw))):
            row = df_raw.iloc[i]
            row_str = ' '.join([str(val) for val in row if pd.notna(val)])
            if any(keyword in row_str for keyword in ['담당', '업체', '프로젝트', '역할', '기간', '계열사']):
                print(f"행 {i}: {row_str[:200]}...")
        
        print("\n" + "=" * 80)
    
    xls.close()
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()