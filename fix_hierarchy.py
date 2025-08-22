#!/usr/bin/env python
"""
조직구조 계층 문제 수정 스크립트
"""

import pandas as pd
from datetime import datetime

def fix_hierarchy_issues():
    """계층구조 문제를 수정합니다."""
    
    print("=== 조직구조 계층 문제 수정 시작 ===")
    
    # Excel 파일 읽기
    df = pd.read_excel('조직구조_업로드.xlsx')
    
    # 백업 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f'조직구조_업로드_hierarchy_backup_{timestamp}.xlsx'
    df.to_excel(backup_path, index=False)
    print(f"[OK] 백업 파일 생성: {backup_path}")
    
    # 문제 수정: 홍보CSR팀을 레벨 4로 변경
    problem_index = df[df['조직명'] == '홍보CSR팀'].index
    if len(problem_index) > 0:
        idx = problem_index[0]
        old_level = df.at[idx, '조직레벨']
        df.at[idx, '조직레벨'] = 4
        
        # 조직코드도 적절히 변경 (TEAM001 -> DEPT001_1)
        df.at[idx, '조직코드'] = 'DEPT001_1'
        
        # 설명도 수정
        df.at[idx, '설명'] = '부서 홍보CSR팀 - ESG 및 기업 홍보 활동을 담당하는 부서'
        
        print(f"[FIX] 홍보CSR팀: 레벨 {old_level} -> 4로 수정")
        print(f"[FIX] 조직코드: TEAM001 -> DEPT001_1로 수정")
    
    # 전체 계층구조 재검증
    print("\n=== 계층구조 재검증 ===")
    level_issues = []
    for _, row in df.iterrows():
        if pd.notna(row['상위조직코드']):
            parent_row = df[df['조직코드'] == row['상위조직코드']]
            if len(parent_row) > 0:
                parent_level = parent_row.iloc[0]['조직레벨']
                if row['조직레벨'] != parent_level + 1:
                    level_issues.append(f"{row['조직명']} (레벨 {row['조직레벨']}) -> 상위: {parent_row.iloc[0]['조직명']} (레벨 {parent_level})")
    
    if level_issues:
        print(f"[WARNING] 계층구조 문제: {len(level_issues)}개")
        for issue in level_issues:
            print(f"  - {issue}")
    else:
        print("[OK] 계층구조 검증 완료 - 문제 없음")
    
    # 수정된 파일 저장
    df.to_excel('조직구조_업로드.xlsx', index=False)
    print(f"\n[OK] 수정된 파일 저장 완료")
    
    # 최종 통계
    print(f"\n=== 수정 후 통계 ===")
    print(f"- 총 조직 수: {len(df)}")
    print(f"- 그룹(레벨1): {len(df[df['조직레벨'] == 1])}")
    print(f"- 계열사(레벨2): {len(df[df['조직레벨'] == 2])}")
    print(f"- 본부(레벨3): {len(df[df['조직레벨'] == 3])}")
    print(f"- 부서(레벨4): {len(df[df['조직레벨'] == 4])}")
    print(f"- 팀(레벨5): {len(df[df['조직레벨'] == 5])}")
    
    return True

if __name__ == '__main__':
    fix_hierarchy_issues()
    print("\n[SUCCESS] 계층구조 수정 완료!")