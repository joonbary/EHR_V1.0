"""
Excel 파일 상세 분석 - 정확한 구조 파악
"""
import pandas as pd
import os

file_path = r'C:\Users\apro\OneDrive\Desktop\인사자료\월간인력현황 _ 250703 - 02.송부용.xlsx'

if os.path.exists(file_path):
    df = pd.read_excel(file_path, sheet_name='인력현황', header=None)
    
    print(f"=== 전체 데이터 크기: {df.shape} ===\n")
    
    # 헤더 행 분석 (회사명 위치 파악)
    print("=== 헤더 행 분석 (2-3행) ===")
    for col in range(min(35, df.shape[1])):
        cell2 = df.iloc[2, col] if pd.notna(df.iloc[2, col]) else ""
        cell3 = df.iloc[3, col] if pd.notna(df.iloc[3, col]) else ""
        if cell2 or cell3:
            print(f"Col {col}: [{cell2}] [{cell3}]")
    
    print("\n=== 데이터 행 분석 (4-25행) ===")
    for row_idx in range(4, 26):
        row_data = []
        for col in [0, 1, 3, 7, 11, 16, 20, 25, 30]:  # 주요 컬럼만
            val = df.iloc[row_idx, col]
            row_data.append(str(val) if pd.notna(val) else "")
        print(f"Row {row_idx}: {row_data}")
    
    print("\n=== 실제 데이터 값 확인 ===")
    # Non-PL 부장 행 데이터
    print("Non-PL 부장 (Row 4):")
    for company, col in [('OK홀딩스', 3), ('OK저축은행(서울)', 7), ('OK저축은행(부산)', 11)]:
        val = df.iloc[4, col]
        print(f"  {company} 현원: {val}")
    
    # PL 직원 데이터
    print("\nPL 직원 데이터:")
    for row in range(9, 14):
        col0 = df.iloc[row, 0]
        col1 = df.iloc[row, 1]
        val_holding = df.iloc[row, 3]
        print(f"  Row {row}: [{col0}] [{col1}] - OK홀딩스: {val_holding}")
    
    # 별정직/기타 데이터
    print("\n별정직/기타 데이터:")
    for row in range(15, 24):
        col0 = df.iloc[row, 0]
        col1 = df.iloc[row, 1]
        val_holding = df.iloc[row, 3]
        print(f"  Row {row}: [{col0}] [{col1}] - OK홀딩스: {val_holding}")
        
    # 총 인원 계산
    print("\n=== 회사별 총 인원 (현원 기준) ===")
    companies = {
        'OK홀딩스': 3,
        'OK저축은행(서울)': 7,
        'OK저축은행(부산/본사)': 11,
        'OK넥스트': 16,  
        'OK캐피탈': 20,
        'OK신용정보': 25,
        'OK데이터시스템': 30
    }
    
    grand_total = 0
    for company, col_idx in companies.items():
        total = 0
        # 모든 데이터 행 확인 (4-23행)
        for row_idx in range(4, 24):
            try:
                val = df.iloc[row_idx, col_idx]
                # 숫자인지 확인 (소계/합계 행 제외)
                col1 = str(df.iloc[row_idx, 1]) if pd.notna(df.iloc[row_idx, 1]) else ""
                if '소계' not in col1 and '합계' not in col1:
                    if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                        num_val = int(float(val))
                        if num_val > 0:
                            total += num_val
            except:
                pass
        print(f"{company}: {total}명")
        grand_total += total
    
    print(f"\n전체 합계: {grand_total}명")

else:
    print("파일을 찾을 수 없습니다")
EOF < /dev/null
