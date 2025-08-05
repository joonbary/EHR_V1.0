#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
모든 앱에서 is_active 사용을 수정
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_all_is_active():
    """모든 is_active 사용을 수정"""
    
    # 수정할 앱 디렉토리들
    app_dirs = [
        'ehr_system',
        'employees', 
        'evaluations',
        'compensation',
        'promotions',
        'selfservice',
        'job_profiles',
        'certifications',
        'trainings',
        'reports'
    ]
    
    fixed_count = 0
    
    for app_dir in app_dirs:
        app_path = BASE_DIR / app_dir
        if not app_path.exists():
            continue
            
        print(f"\n{app_dir} 앱 확인 중...")
        
        # views.py 확인 및 수정
        views_path = app_path / 'views.py'
        if views_path.exists():
            try:
                with open(views_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Employee.objects.filter(is_active=True) 패턴 수정
                content = re.sub(
                    r'Employee\.objects\.filter\(([^)]*?)is_active=True([^)]*?)\)',
                    r"Employee.objects.filter(\1employment_status='active'\2)",
                    content
                )
                
                # Employee.objects.filter(is_active=False) 패턴 수정
                content = re.sub(
                    r'Employee\.objects\.filter\(([^)]*?)is_active=False([^)]*?)\)',
                    r"Employee.objects.exclude(\1employment_status='active'\2)",
                    content
                )
                
                # Q(is_active=True) 패턴 수정
                content = re.sub(
                    r'Q\(is_active=True\)',
                    r"Q(employment_status='active')",
                    content
                )
                
                if content != original_content:
                    # 백업
                    backup_path = str(views_path) + '.bak'
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # 저장
                    with open(views_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  ✓ {app_dir}/views.py 수정됨")
                    fixed_count += 1
                    
            except Exception as e:
                print(f"  ✗ {app_dir}/views.py 수정 실패: {e}")
        
        # 다른 Python 파일들도 확인
        for py_file in app_path.glob('*.py'):
            if py_file.name in ['__init__.py', 'apps.py', 'tests.py']:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'Employee' in content and 'is_active' in content:
                    original_content = content
                    
                    # 수정
                    content = re.sub(
                        r'Employee\.objects\.(filter|get)\(([^)]*?)is_active=True([^)]*?)\)',
                        r"Employee.objects.\1(\2employment_status='active'\3)",
                        content
                    )
                    
                    if content != original_content:
                        # 백업
                        backup_path = str(py_file) + '.bak'
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(original_content)
                        
                        # 저장
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"  ✓ {app_dir}/{py_file.name} 수정됨")
                        fixed_count += 1
                        
            except Exception as e:
                pass
    
    print(f"\n총 {fixed_count}개 파일 수정됨")
    
    # 특별히 확인해야 할 파일
    print("\n특별 확인 파일:")
    special_files = [
        'templates/dashboard.html',
        'templates/base_simple.html',
    ]
    
    for file_path in special_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'is_active' in content:
                    print(f"  ⚠️  {file_path}에 is_active 참조 있음")
                else:
                    print(f"  ✓ {file_path} 정상")
                    
            except Exception as e:
                print(f"  ✗ {file_path} 확인 실패: {e}")

def clear_all_cache():
    """모든 캐시 삭제"""
    print("\n캐시 삭제 중...")
    
    import shutil
    
    # __pycache__ 삭제
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
            except:
                pass
    
    # .pyc 파일 삭제
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
    
    print("  ✓ 캐시 삭제 완료")

def main():
    print("="*60)
    print("모든 is_active 사용 수정")
    print("="*60)
    
    # 1. 모든 is_active 수정
    fix_all_is_active()
    
    # 2. 캐시 삭제
    clear_all_cache()
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. 서버 완전 종료: taskkill /F /IM python.exe")
    print("2. 서버 재시작: python manage.py runserver")
    print("3. http://localhost:8000/ 접속")
    print("="*60)

if __name__ == '__main__':
    main()