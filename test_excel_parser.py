import os
import pandas as pd
from employees.services.excel_parser import HRExcelAutoParser

# 최근 업로드된 파일 찾기
upload_dir = 'media/hr_uploads'
files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []
print(f"업로드 디렉토리 파일: {files}")

if files:
    # 가장 최근 파일 선택
    latest_file = sorted(files)[-1]
    file_path = os.path.join(upload_dir, latest_file)
    print(f"테스트할 파일: {file_path}")
    
    # 엑셀 파일 직접 읽기
    df = pd.read_excel(file_path, header=None)
    print(f"\n엑셀 파일 정보:")
    print(f"- 행 수: {len(df)}")
    print(f"- 컬럼 수: {len(df.columns)}")
    print(f"\n첫 15행:")
    print(df.head(15))
    
    # 헤더 위치 찾기
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val) for val in row if pd.notna(val)])
        if '성명' in row_str or '업체' in row_str:
            print(f"\n헤더 발견 (행 {idx}): {row_str}")
    
    # 파서 테스트
    parser = HRExcelAutoParser()
    file_type = parser.identify_file_type(file_path)
    print(f"\n파일 타입: {file_type}")
    
    if file_type == 'contractor':
        # 로깅 활성화
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        result = parser.parse_contractor(file_path)
        print(f"\n파싱 결과: {len(result)}개 외주 인력")
        if result:
            print(f"첫 번째 데이터: {result[0]}")
        else:
            print("파싱된 데이터가 없습니다!")
            
            # 직접 파싱 테스트
            print("\n직접 파싱 테스트:")
            df = pd.read_excel(file_path, header=10)
            print(f"컬럼: {list(df.columns)}")
            print(f"데이터 행 수: {len(df)}")
            
            contractors = []
            for idx, row in df.iterrows():
                # 첫 번째 컬럼(담당)이 NaN이어도 Unnamed: 1에 이름이 있으면 처리
                name_value = row.get('Unnamed: 1')
                if pd.notna(name_value) and str(name_value) != 'nan' and str(name_value) != '담당':
                    # 담당 회사 찾기 - 현재 행 또는 이전 행에서
                    company = row.get('담당')
                    if pd.isna(company):
                        # 이전 행들을 거슬러 올라가며 회사명 찾기
                        for prev_idx in range(idx - 1, -1, -1):
                            prev_company = df.iloc[prev_idx].get('담당')
                            if pd.notna(prev_company):
                                company = prev_company
                                break
                    
                    print(f"\n행 {idx}: 담당={company}, 이름={name_value}, 업체={row.get('업체')}")
                    contractors.append({
                        'contractor_name': str(name_value),
                        'company': str(company) if pd.notna(company) else '',
                        'vendor_company': str(row.get('업체', ''))
                    })
            
            print(f"\n수동 파싱 결과: {len(contractors)}개 외주 인력")
            
            # 더 자세한 디버깅
            print("\n디버깅 정보:")
            for col in df.columns:
                print(f"컬럼 '{col}' 값 예시:")
                print(df[col].head(3))
                print()
else:
    print("업로드된 파일이 없습니다.")