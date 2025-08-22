#!/usr/bin/env python
"""
조직구조 Excel 파일 H열(설명) 자동 완성 및 데이터 품질 개선 스크립트
"""

import pandas as pd
import sys
from datetime import datetime

def create_organization_descriptions():
    """조직별 맞춤형 설명을 생성합니다."""
    
    # 조직 레벨별 기본 설명 템플릿
    level_templates = {
        1: "그룹 {name} - 전체 그룹을 총괄하는 최상위 조직",
        2: "계열사 {name} - {parent}의 핵심 사업 계열사",
        3: "본부 {name} - {business_area} 관련 업무를 총괄하는 본부",
        4: "부서 {name} - {business_area} 업무를 전문적으로 수행하는 부서",
        5: "팀 {name} - {business_area} 업무의 실무진이 소속된 최일선 조직"
    }
    
    # 업무 영역별 특화 설명
    business_area_mapping = {
        # CSR 관련
        'CSR': 'ESG 경영 및 사회적 책임',
        '홍보CSR': '기업 홍보 및 사회공헌',
        '사회환경경영': 'ESG 및 지속가능경영',
        
        # 영업 관련
        '영업지원': '영업 활동 지원 및 전략',
        '영업기획': '영업 전략 수립 및 기획',
        '영업1': '개인 및 소상공인 대상 영업',
        '영업2': '중소기업 대상 영업',
        '영업3': '대기업 대상 영업',
        '자금운용': '자금 운용 및 투자',
        '여신': '대출 및 신용 관리',
        '인사': '인적자원 관리',
        'IT기획': 'IT 전략 및 시스템 기획',
        
        # IB 관련
        'IB영업': 'Investment Banking 영업',
        
        # 영업점 관련
        '영업점마케팅': '지점 영업 및 마케팅',
        '개인영업기획': '개인고객 영업 전략',
        '영업점운영': '지점 운영 관리',
        '영업점영업': '지점 영업 활동',
        '영업점지원': '지점 업무 지원',
        '상품기획': '금융상품 기획 개발',
        '영업관리': '영업 성과 관리',
        '영업FRONT': '고객 접점 영업',
        '영업점심사': '지점 대출 심사',
        '영업점운영': '지점 운영 총괄',
        '영업점기획': '지점 전략 기획',
        '보험영업': '보험상품 영업',
        
        # IT 관련
        '디지털혁신': 'DX 및 디지털 전환',
        'AI': '인공지능 기술 및 서비스',
        'RPA': '업무 자동화 및 프로세스 혁신',
        'IT통합운영': 'IT 인프라 통합 운영',
        '모바일플랫폼': '모바일 서비스 플랫폼',
        
        # 여신 관련
        '여신': '대출 및 신용 업무',
        '개인여신': '개인대출 업무',
        '여신기획': '여신 정책 및 전략',
        '중금여신': '중금리 대출 업무',
        
        # 디지털 관련
        '디지털본부': '디지털 혁신 및 온라인 서비스',
        '개발': '시스템 개발 및 구축',
        '앱개발': '모바일 앱 개발',
        'UI/UX': '사용자 경험 및 인터페이스 설계',
        '디지털기획': '디지털 서비스 기획',
        '디지털운영관리': '디지털 채널 운영',
        '디지털운영': '디지털 서비스 운영',
        
        # 자산 관련
        '자산영업': '자산 관리 및 운용',
        '자산기획': '자산 전략 기획',
        'CSS영업': 'Customer Service & Sales',
        '자산운영': '자산 포트폴리오 운영',
        
        # 소비자금융 관련
        '소비자금융기획': '개인금융 상품 기획',
        '채널기획': '금융 채널 전략',
        '상품시스템기획': '상품 시스템 기획',
        '영업관리': '영업 성과 및 프로세스 관리',
        
        # 리스크 관련
        '리스크관리': '위험 관리 및 통제',
        '감사': '내부 감사 및 점검',
        '검사': '업무 검사 및 모니터링',
        '신용관리': '신용 위험 관리',
        '법무컴플라이언스': '법무 및 규제 준수',
        '리스크관리': '통합 위험 관리',
        '리스크본부보고': '리스크 보고 체계',
        '리스크운영': '리스크 운영 실무'
    }
    
    return level_templates, business_area_mapping

def extract_business_area(org_name):
    """조직명에서 업무 영역을 추출합니다."""
    
    # 업무 영역 키워드 매핑
    area_keywords = {
        'CSR': ['CSR', '사회환경경영', '홍보'],
        '영업': ['영업', '마케팅'],
        'IT': ['IT', 'AI', 'RPA', '디지털', '개발', 'UI', 'UX', '모바일', '플랫폼'],
        '여신': ['여신', '대출', '신용'],
        '자산': ['자산', 'CSS'],
        '소비자금융': ['소비자금융', '개인금융', '채널', '상품'],
        '리스크': ['리스크', '감사', '검사', '법무', '컴플라이언스'],
        'IB': ['IB'],
        '기획': ['기획', '전략'],
        '운영': ['운영', '관리', '지원'],
        '심사': ['심사', '승인']
    }
    
    for area, keywords in area_keywords.items():
        for keyword in keywords:
            if keyword in org_name:
                return area
    
    return '일반업무'

def generate_description(row, level_templates, business_area_mapping):
    """개별 조직의 설명을 생성합니다."""
    
    org_name = row['조직명']
    org_level = row['조직레벨']
    
    # 이미 설명이 있는 경우 유지
    if pd.notna(row['설명']) and str(row['설명']).strip():
        return row['설명']
    
    # 업무 영역 추출
    business_area = extract_business_area(org_name)
    
    # 특별한 조직에 대한 개별 설명
    special_descriptions = {
        'OK금융그룹': 'OK금융그룹 지주회사 - 전체 그룹을 총괄하는 최상위 조직',
        'OK저축은행': 'OK저축은행 - 저축은행업을 영위하는 핵심 계열사',
        'CSR본부': 'ESG 경영 및 사회적 책임 활동을 총괄하는 본부',
        '영업지원본부': '전사 영업 활동 지원 및 전략 수립을 담당하는 본부',
        'IB영업본부': 'Investment Banking 업무를 전담하는 본부',
        '영업점본부': '전국 영업점 운영 및 관리를 총괄하는 본부',
        '디지털혁신본부': '디지털 전환 및 혁신 업무를 주도하는 본부',
        '여신본부': '대출 및 신용 업무를 총괄하는 본부',
        '디지털본부': '디지털 서비스 개발 및 운영을 담당하는 본부',
        '자산영업본부': '자산 관리 및 운용 업무를 담당하는 본부',
        '소비자금융본부': '개인금융 상품 및 서비스를 담당하는 본부',
        '리스크관리본부(지원)': '전사 위험 관리 및 내부통제를 담당하는 본부'
    }
    
    if org_name in special_descriptions:
        return special_descriptions[org_name]
    
    # 레벨별 템플릿 기반 설명 생성
    if org_level in level_templates:
        template = level_templates[org_level]
        
        # 업무 영역 상세 설명 매핑
        detailed_area = business_area_mapping.get(business_area, business_area)
        
        description = template.format(
            name=org_name,
            parent='OK금융그룹',
            business_area=detailed_area
        )
        
        return description
    
    return f"{org_name} - {business_area} 관련 업무를 담당"

def update_excel_file():
    """Excel 파일을 업데이트합니다."""
    
    print("=== 조직구조 Excel 파일 업데이트 시작 ===")
    
    try:
        # Excel 파일 읽기
        file_path = '조직구조_업로드.xlsx'
        df = pd.read_excel(file_path)
        
        print(f"[OK] Excel 파일 로드 완료 (총 {len(df)}행)")
        
        # 설명 생성 템플릿 로드
        level_templates, business_area_mapping = create_organization_descriptions()
        
        # 각 행의 설명 업데이트
        updated_count = 0
        for index, row in df.iterrows():
            if pd.isna(row['설명']) or not str(row['설명']).strip():
                new_description = generate_description(row, level_templates, business_area_mapping)
                df.at[index, '설명'] = new_description
                updated_count += 1
                print(f"  - {row['조직명']}: {new_description}")
        
        print(f"\n[OK] 총 {updated_count}개 조직의 설명을 추가했습니다.")
        
        # 데이터 품질 검증
        print("\n=== 데이터 품질 검증 ===")
        
        # 1. 조직코드 중복 검사
        duplicate_codes = df[df.duplicated('조직코드', keep=False)]
        if len(duplicate_codes) > 0:
            print(f"[WARNING] 중복된 조직코드 발견: {len(duplicate_codes)}개")
            for _, row in duplicate_codes.iterrows():
                print(f"  - {row['조직코드']}: {row['조직명']}")
        else:
            print("[OK] 조직코드 중복 없음")
        
        # 2. 조직레벨 검증
        invalid_levels = df[~df['조직레벨'].isin([1, 2, 3, 4, 5])]
        if len(invalid_levels) > 0:
            print(f"[WARNING] 잘못된 조직레벨: {len(invalid_levels)}개")
        else:
            print("[OK] 조직레벨 유효성 검증 완료")
        
        # 3. 상위조직코드 검증
        org_codes = set(df['조직코드'].tolist())
        invalid_parents = df[
            df['상위조직코드'].notna() & 
            ~df['상위조직코드'].isin(org_codes)
        ]
        if len(invalid_parents) > 0:
            print(f"[WARNING] 존재하지 않는 상위조직코드: {len(invalid_parents)}개")
            for _, row in invalid_parents.iterrows():
                print(f"  - {row['조직명']}: 상위조직코드 {row['상위조직코드']}")
        else:
            print("[OK] 상위조직코드 유효성 검증 완료")
        
        # 4. 계층구조 검증
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
            print("[OK] 계층구조 검증 완료")
        
        # 백업 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f'조직구조_업로드_backup_{timestamp}.xlsx'
        
        # 원본 백업
        df_original = pd.read_excel(file_path)
        df_original.to_excel(backup_path, index=False)
        print(f"[OK] 원본 백업 완료: {backup_path}")
        
        # 업데이트된 파일 저장
        df.to_excel(file_path, index=False)
        print(f"[OK] 업데이트된 파일 저장 완료: {file_path}")
        
        # 최종 통계
        print(f"\n=== 최종 통계 ===")
        print(f"- 총 조직 수: {len(df)}")
        print(f"- 그룹(레벨1): {len(df[df['조직레벨'] == 1])}")
        print(f"- 계열사(레벨2): {len(df[df['조직레벨'] == 2])}")
        print(f"- 본부(레벨3): {len(df[df['조직레벨'] == 3])}")
        print(f"- 부서(레벨4): {len(df[df['조직레벨'] == 4])}")
        print(f"- 팀(레벨5): {len(df[df['조직레벨'] == 5])}")
        print(f"- 설명 완료율: {(df['설명'].notna().sum() / len(df) * 100):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = update_excel_file()
    if success:
        print("\n[SUCCESS] 조직구조 Excel 파일 업데이트 완료!")
    else:
        print("\n[FAILED] 업데이트 실패")