"""
외주 현황 Excel 파일 상세 구조 분석
"""
import pandas as pd
import numpy as np
from datetime import datetime

file_path = r"C:\Users\apro\OneDrive\Desktop\인사자료\OK금융그룹 외주 현황_250701.xlsx"

try:
    # Sheet1 분석
    df = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    
    print("=== OK금융그룹 외주 현황 파일 구조 분석 ===\n")
    
    # 1. 전체 외주 인력 현황 (행 10부터 시작)
    print("1. 전체 외주 인력 현황 분석:")
    header_row = 10
    df_detail = pd.read_excel(file_path, sheet_name='Sheet1', header=header_row)
    
    print(f"컬럼: {list(df_detail.columns)}")
    print(f"데이터 행 수: {len(df_detail)}")
    
    # 2. 데이터 샘플 출력
    print("\n2. 데이터 샘플:")
    for idx in range(min(5, len(df_detail))):
        row = df_detail.iloc[idx]
        print(f"\n행 {idx+1}:")
        for col in df_detail.columns:
            if pd.notna(row[col]):
                print(f"  {col}: {row[col]}")
    
    # 3. 회사별 통계 (상단 요약)
    print("\n3. 상단 요약 정보:")
    print(f"전체 인원: {df.iloc[4, 2]} ({df.iloc[4, 3]})")  # 98명
    print(f"  - 상주: {df.iloc[4, 2]}")
    print(f"  - 프로젝트: {df.iloc[5, 2]}")
    print(f"  - 비상주: {df.iloc[6, 2]}")
    
    # 4. 파싱 가능한 데이터 구조 제안
    print("\n4. 파싱 가능한 데이터 구조:")
    print("- 담당 컬럼: 계열사 구분 (OKDS, OK홀딩스 등)")
    print("- Unnamed: 1: 구분 (상주/비상주)")
    print("- 인원: 인원수")
    print("- 내용: 프로젝트명/업무내용")
    print("- 업체: 외주업체명")
    print("- 투입부: 투입부서")
    print("- 기간: 계약기간 (있는 경우)")
    
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()