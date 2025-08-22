#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
조직구조 Excel 파일의 조직레벨 문제 수정
D열이 조직코드로 잘못 입력되어 있는 문제 해결
"""

import pandas as pd
import os

def fix_organization_levels():
    """조직레벨 자동 수정"""
    
    input_file = r'D:\EHR_project\조직구조_업로드_최종.xlsx'
    output_file = r'D:\EHR_project\조직구조_업로드_수정본.xlsx'
    
    print("="*60)
    print("조직구조 Excel 파일 조직레벨 수정")
    print("="*60)
    
    # Excel 파일 읽기
    df = pd.read_excel(input_file, engine='openpyxl')
    print(f"[OK] 파일 로드: {len(df)}개 행")
    
    # 컬럼명 변경 (A, B, C... -> 한글)
    df.columns = ['조직코드', '조직명', '조직경로', '조직레벨', '상위조직코드', '상태', '정렬순서', '설명']
    
    # 조직코드 패턴으로 레벨 자동 판별
    def get_level_from_code(code):
        """조직코드로부터 레벨 추출"""
        if pd.isna(code):
            return None
        code = str(code).upper()
        if code.startswith('GRP'):
            return 1  # 그룹
        elif code.startswith('COM'):
            return 2  # 계열사
        elif code.startswith('HQ'):
            return 3  # 본부
        elif code.startswith('DEPT'):
            return 4  # 부서
        elif code.startswith('TEAM'):
            return 5  # 팀
        else:
            return None
    
    # 조직레벨 수정
    print("\n조직레벨 수정 중...")
    for idx, row in df.iterrows():
        org_code = row['조직코드']
        old_level = row['조직레벨']
        new_level = get_level_from_code(org_code)
        
        if new_level:
            df.at[idx, '조직레벨'] = new_level
            if str(old_level) != str(new_level):
                print(f"  [수정] {org_code}: {old_level} -> {new_level}")
    
    # 상위조직 관계 재구성
    print("\n상위조직 관계 검증...")
    
    # 레벨별로 그룹화
    level_groups = {
        1: df[df['조직레벨'] == 1]['조직코드'].tolist(),
        2: df[df['조직레벨'] == 2]['조직코드'].tolist(),
        3: df[df['조직레벨'] == 3]['조직코드'].tolist(),
        4: df[df['조직레벨'] == 4]['조직코드'].tolist(),
        5: df[df['조직레벨'] == 5]['조직코드'].tolist()
    }
    
    # 상위조직 자동 설정 (문제가 있는 경우)
    for idx, row in df.iterrows():
        org_code = row['조직코드']
        org_level = row['조직레벨']
        parent_code = row['상위조직코드']
        
        if pd.notna(org_level):
            # 레벨 1(그룹)은 상위조직 없음
            if org_level == 1:
                df.at[idx, '상위조직코드'] = None
            # 레벨 2(계열사)는 그룹이 상위
            elif org_level == 2 and parent_code not in level_groups[1]:
                if level_groups[1]:
                    df.at[idx, '상위조직코드'] = level_groups[1][0]  # 첫 번째 그룹
                    print(f"  [상위수정] {org_code}: {parent_code} -> {level_groups[1][0]}")
            # 레벨 3(본부)는 계열사가 상위
            elif org_level == 3 and parent_code not in level_groups[2]:
                if level_groups[2]:
                    df.at[idx, '상위조직코드'] = level_groups[2][0]  # 첫 번째 계열사
                    print(f"  [상위수정] {org_code}: {parent_code} -> {level_groups[2][0]}")
            # 레벨 4(부서)는 본부가 상위
            elif org_level == 4:
                # 조직경로에서 본부 찾기
                org_path = str(row['조직경로']) if pd.notna(row['조직경로']) else ''
                matched_hq = None
                for hq in level_groups[3]:
                    hq_name = df[df['조직코드'] == hq]['조직명'].iloc[0] if len(df[df['조직코드'] == hq]) > 0 else ''
                    if hq_name in org_path:
                        matched_hq = hq
                        break
                if matched_hq and parent_code != matched_hq:
                    df.at[idx, '상위조직코드'] = matched_hq
                    print(f"  [상위수정] {org_code}: {parent_code} -> {matched_hq}")
            # 레벨 5(팀)는 부서가 상위
            elif org_level == 5:
                # 조직경로에서 부서 찾기
                org_path = str(row['조직경로']) if pd.notna(row['조직경로']) else ''
                matched_dept = None
                for dept in level_groups[4]:
                    dept_name = df[df['조직코드'] == dept]['조직명'].iloc[0] if len(df[df['조직코드'] == dept]) > 0 else ''
                    if dept_name in org_path:
                        matched_dept = dept
                        break
                if matched_dept and parent_code != matched_dept:
                    df.at[idx, '상위조직코드'] = matched_dept
                    print(f"  [상위수정] {org_code}: {parent_code} -> {matched_dept}")
    
    # 파일 저장
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"\n[OK] 수정된 파일 저장: {output_file}")
    
    # 통계 출력
    print("\n레벨별 조직 수:")
    level_counts = df['조직레벨'].value_counts().sort_index()
    level_names = {1: '그룹', 2: '계열사', 3: '본부', 4: '부서', 5: '팀'}
    for level, count in level_counts.items():
        if pd.notna(level) and int(level) in level_names:
            print(f"  레벨 {int(level)} ({level_names[int(level)]}): {count}개")
    
    print("\n="*60)
    print("수정 완료!")
    print("="*60)

if __name__ == "__main__":
    fix_organization_levels()