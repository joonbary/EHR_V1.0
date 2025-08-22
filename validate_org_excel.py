#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
조직구조 Excel 파일 검증 및 Railway API 호환성 확인
"""

import pandas as pd
import json
from datetime import datetime

def validate_organization_excel():
    """Excel 파일 검증 및 API 형식 변환"""
    
    file_path = r'D:\EHR_project\조직구조_업로드_수정본.xlsx'
    
    print("="*60)
    print("조직구조 Excel 파일 검증")
    print("="*60)
    
    # 1. Excel 파일 읽기
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"\n[OK] Excel 파일 로드 성공: {len(df)}개 행")
    except Exception as e:
        print(f"[ERROR] 파일 읽기 실패: {e}")
        return
    
    # 2. 컬럼 확인
    print(f"\n현재 컬럼: {df.columns.tolist()}")
    
    # 컬럼명을 한글로 변경 (API가 기대하는 형식)
    column_mapping = {
        'A': '조직코드',
        'B': '조직명',
        'C': '조직경로',
        'D': '조직레벨',
        'E': '상위조직코드',
        'F': '상태',
        'G': '정렬순서',
        'H': '설명'
    }
    
    # 컬럼명이 A, B, C 형식인 경우 한글로 변경
    if 'A' in df.columns:
        df = df.rename(columns=column_mapping)
        print(f"[OK] 컬럼명 한글로 변경 완료")
        print(f"   변경된 컬럼: {df.columns.tolist()}")
    
    # 3. 필수 컬럼 확인
    required_columns = ['조직코드', '조직명', '조직레벨']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"\n[ERROR] 필수 컬럼 누락: {missing_columns}")
        return
    else:
        print(f"\n[OK] 필수 컬럼 모두 존재")
    
    # 4. 데이터 타입 및 값 검증
    print(f"\n데이터 검증:")
    
    # 조직레벨 검증
    if '조직레벨' in df.columns:
        unique_levels = df['조직레벨'].unique()
        print(f"  조직레벨 종류: {list(unique_levels)}")
        
        # 레벨이 숫자가 아닌 경우 확인
        non_numeric_levels = []
        for level in df['조직레벨']:
            try:
                if pd.notna(level):
                    int(level)
            except (ValueError, TypeError):
                non_numeric_levels.append(level)
        
        if non_numeric_levels:
            print(f"  [WARNING] 숫자가 아닌 레벨: {list(set(non_numeric_levels))[:5]}")
    
    # 5. 상위조직 참조 검증
    print(f"\n상위조직 참조 검증:")
    all_org_codes = set(df['조직코드'].dropna())
    parent_codes = set(df['상위조직코드'].dropna())
    missing_parents = parent_codes - all_org_codes
    
    if missing_parents:
        print(f"  [ERROR] 존재하지 않는 상위조직 참조: {list(missing_parents)[:10]}")
    else:
        print(f"  [OK] 모든 상위조직 참조 유효")
    
    # 6. 레벨별 통계
    print(f"\n레벨별 조직 수:")
    level_counts = df['조직레벨'].value_counts().sort_index()
    for level, count in level_counts.items():
        try:
            level_int = int(level) if pd.notna(level) else 0
            level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
            if level_int in level_names:
                print(f"  레벨 {level_int} ({level_names[level_int]}): {count}개")
            else:
                print(f"  레벨 {level}: {count}개")
        except:
            print(f"  레벨 {level}: {count}개")
    
    # 7. API 전송 형식으로 변환
    print(f"\nAPI 전송 데이터 준비:")
    api_data = []
    
    for idx, row in df.iterrows():
        # NaN 값을 None으로 변환
        org_data = {
            '조직코드': str(row['조직코드']) if pd.notna(row['조직코드']) else None,
            '조직명': str(row['조직명']) if pd.notna(row['조직명']) else None,
            '조직경로': str(row['조직경로']) if pd.notna(row['조직경로']) else None,
            '조직레벨': int(row['조직레벨']) if pd.notna(row['조직레벨']) and str(row['조직레벨']).isdigit() else None,
            '상위조직코드': str(row['상위조직코드']) if pd.notna(row['상위조직코드']) else None,
            '상태': str(row['상태']) if pd.notna(row['상태']) else 'active',
            '정렬순서': int(row['정렬순서']) if pd.notna(row['정렬순서']) else idx + 1,
            '설명': str(row['설명']) if pd.notna(row['설명']) else ''
        }
        
        # 필수 필드 확인
        if org_data['조직코드'] and org_data['조직명'] and org_data['조직레벨']:
            api_data.append(org_data)
        else:
            print(f"  [WARNING] 행 {idx+1} 스킵 (필수 필드 누락)")
    
    print(f"  [OK] API 전송 가능한 데이터: {len(api_data)}개")
    
    # 8. 샘플 데이터 출력
    print(f"\n샘플 데이터 (처음 3개):")
    for i, data in enumerate(api_data[:3]):
        print(f"\n  [{i+1}] {data['조직코드']} - {data['조직명']}")
        print(f"      레벨: {data['조직레벨']}, 상위: {data['상위조직코드']}")
        print(f"      설명: {data['설명'][:50]}..." if data['설명'] else "      설명: (없음)")
    
    # 9. JSON 파일로 저장 (테스트용)
    output_file = r'D:\EHR_project\organization_api_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({'data': api_data}, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] API 데이터 저장: {output_file}")
    
    # 10. 문제점 요약
    print(f"\n="*60)
    print("검증 결과 요약:")
    print(f"  - 전체 행: {len(df)}개")
    print(f"  - 유효한 데이터: {len(api_data)}개")
    print(f"  - 누락된 상위조직: {len(missing_parents)}개")
    
    if len(api_data) < len(df):
        print(f"\n[WARNING] 주의: 일부 데이터가 유효하지 않아 스킵되었습니다.")
        print(f"   원인: 필수 필드(조직코드, 조직명, 조직레벨) 누락 또는 잘못된 형식")
    
    print("="*60)
    
    return api_data

if __name__ == "__main__":
    validate_organization_excel()