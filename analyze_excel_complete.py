"""
엑셀 파일 전체 구조 분석
"""
import pandas as pd
import os

file_path = r'C:\Users\apro\OneDrive\Desktop\인사자료\월간인력현황 _ 250703 - 02.송부용.xlsx'

if os.path.exists(file_path):
    # 인력현황 시트 읽기
    df = pd.read_excel(file_path, sheet_name='인력현황', header=None)
    
    print(f"=== 전체 데이터 크기: {df.shape} ===\n")
    
    # 모든 행 분석 (특히 별정직, 개인사업자 등)
    print("=== 전체 행 데이터 (0열: 구분, 1열: 직급) ===")
    for row_idx in range(4, min(df.shape[0], 40)):  # 4행부터 40행까지
        col0 = df.iloc[row_idx, 0]  # 구분
        col1 = df.iloc[row_idx, 1]  # 직급
        col3 = df.iloc[row_idx, 3]  # OK홀딩스 현원
        
        if pd.notna(col0) or pd.notna(col1):
            print(f"Row {row_idx}: [{col0}] [{col1}] - OK홀딩스: {col3}")
    
    print("\n=== 회사별 현원 합계 확인 ===")
    # 각 회사의 현원 컬럼 위치
    company_cols = {
        'OK홀딩스': 3,
        'OK저축은행(서울)': 7,
        'OK저축은행(부산/본사)': 11,
        'OK넥스트': 16,
        'OK캐피탈': 20,
        'OK신용정보': 25,
        'OK데이터시스템': 30
    }
    
    for company, col_idx in company_cols.items():
        total = 0
        for row_idx in range(4, df.shape[0]):
            val = df.iloc[row_idx, col_idx]
            try:
                if pd.notna(val) and str(val).replace('.', '').isdigit():
                    total += int(float(val))
            except:
                pass
        print(f"{company}: {total}명")
    
    print("\n=== 특수 직급/신분 확인 ===")
    # 별정직, 개인사업자 등 찾기
    for row_idx in range(15, min(df.shape[0], 40)):
        col0 = df.iloc[row_idx, 0]
        col1 = df.iloc[row_idx, 1]
        
        if pd.notna(col0) and ('별정' in str(col0) or '개인' in str(col0) or '기타' in str(col0)):
            print(f"Row {row_idx}: 구분=[{col0}] 직급=[{col1}]")
            # 해당 행의 데이터 출력
            data = []
            for col_idx in [3, 7, 11, 16, 20, 25, 30]:
                val = df.iloc[row_idx, col_idx]
                data.append(f"{val}")
            print(f"  데이터: {data}")
    
else:
    print("파일을 찾을 수 없습니다")