#!/usr/bin/env python
"""
API 엔드포인트의 모델 import 문제 수정
"""

import os

def fix_api_imports():
    """views.py 파일의 import 문제 수정"""
    
    views_file = r'D:\EHR_project\employees\views.py'
    
    print("="*60)
    print("API Import 문제 수정")
    print("="*60)
    
    # 파일 읽기
    with open(views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 파일 상단에 필요한 import 추가
    imports_to_add = """from .models_organization import OrganizationStructure, OrganizationUploadHistory, EmployeeOrganizationMapping
from .models_hr import HREmployee
from .models_workforce import WeeklyWorkforceSnapshot
"""
    
    # 기존 import 라인 찾기
    import_line_end = content.find('from utils.file_manager import ExcelFileHandler')
    if import_line_end > 0:
        import_line_end = content.find('\n', import_line_end) + 1
        
        # OrganizationStructure import가 이미 있는지 확인
        if 'from .models_organization import' not in content[:import_line_end]:
            # import 추가
            new_content = content[:import_line_end] + imports_to_add + content[import_line_end:]
            
            # 파일 저장
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("[OK] Import 문 추가 완료")
        else:
            print("[INFO] Import 문이 이미 존재합니다")
    
    # upload_organization_structure 함수 수정
    print("\nupload_organization_structure 함수 수정...")
    
    # 함수 내부의 import 제거하고 상단 import 사용
    old_import_pattern = "            from .models_organization import OrganizationStructure, OrganizationUploadHistory"
    if old_import_pattern in content:
        content = content.replace(old_import_pattern, "            # Models imported at top of file")
        
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] 함수 내부 import 제거")
    
    # get_organization_stats 함수 수정
    print("\nget_organization_stats 함수 수정...")
    
    old_import_pattern2 = "        from .models_organization import OrganizationStructure"
    if old_import_pattern2 in content:
        content = content.replace(old_import_pattern2, "        # Models imported at top of file")
        
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] 함수 내부 import 제거")
    
    print("\n="*60)
    print("수정 완료!")
    print("="*60)

if __name__ == "__main__":
    fix_api_imports()