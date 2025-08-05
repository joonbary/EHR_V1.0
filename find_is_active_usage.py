#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
is_active 필드를 사용하는 모든 파일 찾기
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

def find_is_active_usage():
    """is_active를 사용하는 모든 파일 찾기"""
    print("is_active 필드를 사용하는 파일 검색 중...")
    print("="*60)
    
    # 검색할 패턴들
    patterns = [
        r'\.filter\([^)]*is_active',
        r'\.exclude\([^)]*is_active',
        r'is_active\s*=\s*True',
        r'is_active\s*=\s*False',
        r'\.get\([^)]*is_active',
        r'Q\([^)]*is_active',
    ]
    
    # 제외할 디렉토리
    exclude_dirs = {'__pycache__', '.git', 'venv', 'staticfiles', 'media', 'migrations'}
    
    found_files = {}
    
    for root, dirs, files in os.walk(BASE_DIR):
        # 제외할 디렉토리 스킵
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Employee와 관련된 is_active 사용 찾기
                    if 'Employee' in content:
                        for pattern in patterns:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                if file_path not in found_files:
                                    found_files[file_path] = []
                                
                                # 매치된 라인 찾기
                                lines = content[:match.start()].split('\n')
                                line_no = len(lines)
                                line_content = content.split('\n')[line_no-1].strip()
                                
                                found_files[file_path].append({
                                    'line': line_no,
                                    'content': line_content,
                                    'pattern': pattern
                                })
                                
                except Exception as e:
                    pass
    
    # 결과 출력
    if found_files:
        print(f"\n총 {len(found_files)}개 파일에서 is_active 사용 발견:")
        print("-"*60)
        
        for file_path, matches in found_files.items():
            rel_path = os.path.relpath(file_path, BASE_DIR)
            print(f"\n📄 {rel_path}")
            for match in matches:
                print(f"   L{match['line']}: {match['content']}")
    else:
        print("\nis_active를 사용하는 파일을 찾을 수 없습니다.")
    
    return found_files

def fix_is_active_usage(found_files):
    """is_active를 employment_status='active'로 자동 변경"""
    print("\n" + "="*60)
    print("is_active를 employment_status='active'로 변경할까요?")
    
    if not found_files:
        return
    
    print("\n변경할 파일:")
    for file_path in found_files.keys():
        rel_path = os.path.relpath(file_path, BASE_DIR)
        print(f"  - {rel_path}")
    
    response = input("\n진행하시겠습니까? (y/n): ")
    if response.lower() != 'y':
        print("취소되었습니다.")
        return
    
    # 변경 실행
    for file_path, matches in found_files.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 백업
            backup_path = file_path + '.bak'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # is_active=True를 employment_status='active'로 변경
            content = re.sub(
                r'\.filter\(([^)]*?)is_active=True([^)]*?)\)',
                r".filter(\1employment_status='active'\2)",
                content
            )
            
            # is_active=False를 제거 또는 다른 status로 변경
            content = re.sub(
                r'\.filter\(([^)]*?)is_active=False([^)]*?)\)',
                r".exclude(\1employment_status='active'\2)",
                content
            )
            
            # Q 객체 내의 is_active
            content = re.sub(
                r'Q\(([^)]*?)is_active=True([^)]*?)\)',
                r"Q(\1employment_status='active'\2)",
                content
            )
            
            # 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            rel_path = os.path.relpath(file_path, BASE_DIR)
            print(f"✓ 수정됨: {rel_path}")
            
        except Exception as e:
            print(f"✗ 수정 실패: {file_path} - {e}")

def check_specific_files():
    """특정 파일들 확인"""
    print("\n" + "="*60)
    print("주요 파일 내용 확인")
    print("="*60)
    
    files_to_check = [
        'ehr_system/views.py',
        'employees/views.py',
        'employees/models.py',
        'job_profiles/views.py',
    ]
    
    for file_path in files_to_check:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            print(f"\n📄 {file_path}:")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Employee 관련 필터 찾기
                if 'Employee.objects.filter' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'Employee.objects.filter' in line:
                            print(f"   L{i+1}: {line.strip()}")
                            # 다음 몇 줄도 확인
                            for j in range(1, 3):
                                if i+j < len(lines):
                                    print(f"   L{i+j+1}: {lines[i+j].strip()}")
                else:
                    print("   Employee.objects.filter 사용 없음")
                    
            except Exception as e:
                print(f"   읽기 실패: {e}")

def main():
    print("="*60)
    print("is_active 필드 사용 위치 찾기")
    print("="*60)
    
    # 1. is_active 사용 찾기
    found_files = find_is_active_usage()
    
    # 2. 특정 파일 확인
    check_specific_files()
    
    # 3. 자동 수정 제안
    if found_files:
        fix_is_active_usage(found_files)
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. 수정된 파일 확인")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/ 접속")

if __name__ == '__main__':
    main()