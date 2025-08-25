#!/usr/bin/env python
"""
조직 구조 업로드 0개 생성 문제 디버깅
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

print("="*60)
print("조직 구조 업로드 디버깅")
print("="*60)

try:
    django.setup()
    print("[OK] Django 초기화\n")
except Exception as e:
    print(f"[ERROR] Django 초기화 실패: {e}")
    sys.exit(1)

def enhance_upload_debug():
    """upload_organization_structure 함수에 더 자세한 디버깅 추가"""
    print("1. views.py 디버깅 강화")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    with open(views_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # upload_organization_structure 함수 찾기
    for i, line in enumerate(lines):
        if 'def upload_organization_structure' in line:
            # 디버깅 코드 강화 부분 찾기
            for j in range(i, min(i+200, len(lines))):
                if 'print(f"[DEBUG] 데이터 개수: {len(data)}")' in lines[j]:
                    # 더 자세한 디버깅 추가
                    enhanced_debug = '''        print(f"[DEBUG] 데이터 개수: {len(data)}")
        if data:
            print(f"[DEBUG] 첫 번째 행 키: {list(data[0].keys())}")
            print(f"[DEBUG] 첫 번째 행 데이터: {data[0]}")
            
            # 필드명 매핑 시도
            for idx, row in enumerate(data[:3]):  # 처음 3개만 디버깅
                print(f"[DEBUG] 행 {idx+1}:")
                for key, value in row.items():
                    print(f"  - {key}: {value}")
        
'''
                    lines[j] = enhanced_debug
                    print("[OK] 디버깅 코드 강화")
                    break
            break
    
    # 파일 저장
    with open(views_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def create_field_mapping():
    """필드 매핑 처리 추가"""
    print("\n2. 필드 매핑 로직 추가")
    print("-" * 40)
    
    views_path = os.path.join(os.path.dirname(__file__), 'employees', 'views.py')
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 필드 매핑 로직 추가
    field_mapping = '''
                # 필드명 매핑 (Excel 컬럼명 -> DB 필드명)
                field_map = {
                    'A': '조직코드', 'B': '조직명', 'C': '상위조직코드',
                    'D': '조직레벨', 'E': '조직장', 'F': '상태',
                    'G': '정렬순서', 'H': '설명',
                    # 영문 매핑
                    'org_code': '조직코드', 'org_name': '조직명',
                    'parent_code': '상위조직코드', 'org_level': '조직레벨',
                    'level': '조직레벨', 'status': '상태',
                    'sort_order': '정렬순서', 'description': '설명',
                    # 다양한 변형
                    '코드': '조직코드', '명칭': '조직명', '레벨': '조직레벨',
                    '순서': '정렬순서', '비고': '설명'
                }
                
                # 필드 매핑 적용
                mapped_row = {}
                for key, value in row.items():
                    # 직접 매핑
                    if key in ['조직코드', '조직명', '조직레벨', '상위조직코드', '상태', '정렬순서', '설명']:
                        mapped_row[key] = value
                    # 매핑 테이블 사용
                    elif key in field_map:
                        mapped_row[field_map[key]] = value
                    # A, B, C... 형식
                    elif len(key) == 1 and key in field_map:
                        mapped_row[field_map[key]] = value
                    else:
                        # 알 수 없는 필드는 그대로 사용
                        mapped_row[key] = value
                
                row = mapped_row  # 매핑된 데이터로 교체
'''
    
    # 필드 확인 부분 앞에 매핑 로직 삽입
    if '# 필드명 매핑' not in content:
        content = content.replace(
            '                # 필수 필드 확인',
            field_mapping + '\n                # 필수 필드 확인'
        )
        print("[OK] 필드 매핑 로직 추가")
    else:
        print("[INFO] 필드 매핑 이미 존재")
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_sample_test_data():
    """테스트용 샘플 데이터 생성"""
    print("\n3. 테스트 데이터 생성")
    print("-" * 40)
    
    import pandas as pd
    
    # 한글 컬럼명
    data_korean = {
        '조직코드': ['GRP001', 'COM001', 'HQ001', 'DEPT001', 'TEAM001'],
        '조직명': ['OK금융그룹', 'OK저축은행', '리테일본부', 'IT개발부', '개발1팀'],
        '조직레벨': [1, 2, 3, 4, 5],
        '상위조직코드': ['', 'GRP001', 'COM001', 'HQ001', 'DEPT001'],
        '상태': ['active', 'active', 'active', 'active', 'active'],
        '정렬순서': [1, 1, 1, 1, 1],
        '설명': ['그룹', '계열사', '본부', '부서', '팀']
    }
    
    df_korean = pd.DataFrame(data_korean)
    df_korean.to_excel('test_org_korean.xlsx', index=False)
    print("[OK] test_org_korean.xlsx 생성")
    
    # 영문 컬럼명
    data_english = {
        'org_code': ['GRP001', 'COM001', 'HQ001', 'DEPT001', 'TEAM001'],
        'org_name': ['OK Financial Group', 'OK Savings Bank', 'Retail HQ', 'IT Dev Dept', 'Dev Team 1'],
        'org_level': [1, 2, 3, 4, 5],
        'parent_code': ['', 'GRP001', 'COM001', 'HQ001', 'DEPT001'],
        'status': ['active', 'active', 'active', 'active', 'active'],
        'sort_order': [1, 1, 1, 1, 1],
        'description': ['Group', 'Subsidiary', 'Headquarters', 'Department', 'Team']
    }
    
    df_english = pd.DataFrame(data_english)
    df_english.to_excel('test_org_english.xlsx', index=False)
    print("[OK] test_org_english.xlsx 생성")
    
    # A, B, C 형식
    data_abc = pd.DataFrame([
        ['GRP001', 'OK금융그룹', '', 1, '', 'active', 1, '그룹'],
        ['COM001', 'OK저축은행', 'GRP001', 2, '', 'active', 1, '계열사'],
        ['HQ001', '리테일본부', 'COM001', 3, '', 'active', 1, '본부'],
        ['DEPT001', 'IT개발부', 'HQ001', 4, '', 'active', 1, '부서'],
        ['TEAM001', '개발1팀', 'DEPT001', 5, '', 'active', 1, '팀']
    ])
    data_abc.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    data_abc.to_excel('test_org_abc.xlsx', index=False)
    print("[OK] test_org_abc.xlsx 생성")
    
    print("\n테스트 방법:")
    print("1. 위 3개 파일 중 하나를 업로드해보세요")
    print("2. Railway logs로 디버깅 메시지 확인")
    print("3. 어떤 필드명이 전달되는지 확인")

def main():
    """메인 실행"""
    
    print("\n시작: 조직 구조 업로드 디버깅\n")
    
    # 1. 디버깅 강화
    enhance_upload_debug()
    
    # 2. 필드 매핑 추가
    create_field_mapping()
    
    # 3. 테스트 데이터 생성
    create_sample_test_data()
    
    print("\n" + "="*60)
    print("디버깅 준비 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. git add employees/views.py")
    print("2. git commit -m 'Add detailed debugging for organization upload'")
    print("3. git push")
    print("4. Railway 재배포 후 테스트")
    print("\n디버깅 확인:")
    print("- railway logs로 상세 로그 확인")
    print("- 첫 번째 행의 키와 데이터 확인")
    print("- 필드 매핑이 제대로 되는지 확인")

if __name__ == "__main__":
    main()