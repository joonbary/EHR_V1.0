#!/usr/bin/env python
"""
조직구조 CSV 파일 분석 및 검증
"""

import pandas as pd
import numpy as np

def analyze_csv_file():
    """CSV 파일 구조 분석"""
    print("=" * 60)
    print("조직구조 CSV 파일 분석")
    print("=" * 60)
    
    # 다양한 인코딩으로 시도
    encodings = ['utf-8', 'cp949', 'euc-kr']
    
    for encoding in encodings:
        try:
            print(f"\n[시도] {encoding} 인코딩으로 파일 읽기...")
            df = pd.read_csv('조직구조_업로드_최종.csv', encoding=encoding)
            print(f"[성공] {encoding} 인코딩으로 읽기 성공!")
            break
        except Exception as e:
            print(f"[실패] {encoding}: {e}")
            continue
    else:
        print("[오류] 모든 인코딩 시도 실패")
        return
    
    # 1. 기본 정보
    print(f"\n1. 기본 정보")
    print("-" * 40)
    print(f"총 행 수: {len(df)}개")
    print(f"총 컬럼 수: {len(df.columns)}개")
    print(f"컬럼명: {list(df.columns)}")
    
    # 2. 컬럼별 분석
    print(f"\n2. 컬럼별 분석")
    print("-" * 40)
    
    # A,B,C,D,E,F,G,H 형식이면 매핑
    if df.columns.tolist() == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        column_mapping = {
            'A': '조직코드',
            'B': '조직명', 
            'C': '조직레벨',
            'D': '상위조직코드',
            'E': '조직장',
            'F': '상태',
            'G': '정렬순서',
            'H': '설명'
        }
        df = df.rename(columns=column_mapping)
        print("컬럼명을 한글로 변환했습니다.")
        print(f"변환 후: {list(df.columns)}")
    
    # 각 컬럼 정보
    for col in df.columns:
        non_null = df[col].notna().sum()
        null_count = df[col].isna().sum()
        unique_count = df[col].nunique()
        print(f"{col}: 데이터 {non_null}개, 빈값 {null_count}개, 고유값 {unique_count}개")
    
    # 3. 조직 레벨 분석
    print(f"\n3. 조직 레벨 분석")
    print("-" * 40)
    
    if '조직레벨' in df.columns:
        level_counts = df['조직레벨'].value_counts().sort_index()
        print("레벨별 개수:")
        level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
        for level, count in level_counts.items():
            level_name = level_names.get(level, f'레벨{level}')
            print(f"  레벨 {level} ({level_name}): {count}개")
    
    # 4. 상위조직 매핑 검증
    print(f"\n4. 상위조직 매핑 검증")
    print("-" * 40)
    
    if '상위조직코드' in df.columns and '조직코드' in df.columns:
        # 모든 조직코드 집합
        all_org_codes = set(df['조직코드'].dropna())
        
        # 상위조직코드 중 빈 값이 아닌 것들
        parent_codes = set(df['상위조직코드'].dropna())
        
        print(f"전체 조직코드: {len(all_org_codes)}개")
        print(f"상위조직코드 (비어있지 않은): {len(parent_codes)}개")
        
        # 존재하지 않는 상위조직코드 찾기
        missing_parents = parent_codes - all_org_codes
        if missing_parents:
            print(f"경고: 존재하지 않는 상위조직코드: {missing_parents}")
        else:
            print("OK: 모든 상위조직코드가 유효합니다")
        
        # 고아 조직 찾기 (레벨 1이 아닌데 상위조직이 없는)
        orphans = df[(df['조직레벨'] > 1) & (df['상위조직코드'].isna())]
        if len(orphans) > 0:
            print(f"경고: 고아 조직 (레벨>1인데 상위조직 없음): {len(orphans)}개")
            print(orphans[['조직코드', '조직명', '조직레벨']].to_string())
        else:
            print("OK: 고아 조직이 없습니다")
    
    # 5. 계층구조 검증
    print(f"\n5. 계층구조 검증")
    print("-" * 40)
    
    if '조직레벨' in df.columns and '상위조직코드' in df.columns:
        issues = []
        
        for idx, row in df.iterrows():
            org_code = row['조직코드']
            org_level = row['조직레벨']
            parent_code = row['상위조직코드']
            
            if pd.notna(parent_code):
                parent_row = df[df['조직코드'] == parent_code]
                if len(parent_row) > 0:
                    parent_level = parent_row.iloc[0]['조직레벨']
                    if parent_level >= org_level:
                        issues.append({
                            '조직코드': org_code,
                            '조직레벨': org_level,
                            '상위조직코드': parent_code,
                            '상위조직레벨': parent_level,
                            '문제': '상위조직 레벨이 같거나 높음'
                        })
        
        if issues:
            print(f"경고: 계층구조 문제: {len(issues)}개")
            for issue in issues[:5]:  # 처음 5개만 표시
                print(f"  - {issue['조직코드']} (레벨{issue['조직레벨']}) -> {issue['상위조직코드']} (레벨{issue['상위조직레벨']})")
        else:
            print("OK: 계층구조가 올바릅니다")
    
    # 6. 샘플 데이터
    print(f"\n6. 샘플 데이터 (처음 5개)")
    print("-" * 40)
    print(df.head()[['조직코드', '조직명', '조직레벨', '상위조직코드']].to_string())
    
    # 7. 시스템 호환성 체크
    print(f"\n7. 시스템 호환성 체크")
    print("-" * 40)
    
    required_fields = ['조직코드', '조직명', '조직레벨']
    missing_fields = [field for field in required_fields if field not in df.columns]
    
    if missing_fields:
        print(f"경고: 필수 필드 누락: {missing_fields}")
    else:
        print("OK: 필수 필드 모두 존재")
    
    # 조직코드 중복 체크
    duplicate_codes = df['조직코드'].duplicated().sum()
    if duplicate_codes > 0:
        print(f"경고: 중복된 조직코드: {duplicate_codes}개")
    else:
        print("OK: 조직코드 중복 없음")
    
    return df

if __name__ == "__main__":
    df = analyze_csv_file()
    
    print("\n" + "=" * 60)
    print("분석 완료!")
    print("=" * 60)