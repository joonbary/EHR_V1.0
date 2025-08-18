#!/usr/bin/env python
"""
프로젝트 정리 및 외장하드 이관 스크립트
"""
import os
import shutil
import json
from datetime import datetime

# 정리할 파일/폴더 패턴
CLEANUP_PATTERNS = {
    'cache_files': [
        '__pycache__',
        '*.pyc',
        '.pytest_cache',
        '.coverage',
        'htmlcov',
        '.mypy_cache',
    ],
    'logs': [
        '*.log',
        'logs/',
        'server.log',
        'debug.log',
    ],
    'temp_files': [
        '*.tmp',
        '*.temp',
        '.DS_Store',
        'Thumbs.db',
        '~*',
    ],
    'backup_files': [
        '*.bak',
        '*.backup',
        '*_backup*',
        '*_old*',
        '*_test*',
    ],
    'build_artifacts': [
        'dist/',
        'build/',
        '*.egg-info',
        'node_modules/',
    ],
    'ide_files': [
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
    ],
    'test_data': [
        'test_*.xlsx',
        'test_*.json',
        'dummy_*.xlsx',
        '*_test.py',
    ],
    'duplicate_templates': [
        'dashboard_old.html',
        'dashboard_backup.html',
        'dashboard_test.html',
        'dashboard_debug.html',
        'dashboard_v2.html',
    ]
}

# 보존할 중요 파일
KEEP_FILES = [
    'requirements.txt',
    'manage.py',
    'railway.json',
    'Procfile',
    'runtime.txt',
    '.env.example',
    'README.md',
]

# 보존할 중요 폴더
KEEP_DIRS = [
    'employees',
    'evaluations',
    'job_profiles',
    'trainings',
    'certifications',
    'ehr_system',
    'core',
    'templates',
    'static',
    'media',
]

def cleanup_project(source_dir):
    """프로젝트 정리"""
    cleanup_report = {
        'removed_files': [],
        'removed_dirs': [],
        'total_size_saved': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    # 1. 캐시 파일 제거
    print("1. 캐시 파일 정리 중...")
    for root, dirs, files in os.walk(source_dir):
        # __pycache__ 폴더 제거
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                size = get_dir_size(cache_path)
                shutil.rmtree(cache_path)
                cleanup_report['removed_dirs'].append(cache_path)
                cleanup_report['total_size_saved'] += size
                print(f"   제거: {cache_path}")
            except Exception as e:
                print(f"   오류: {cache_path} - {e}")
        
        # .pyc 파일 제거
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleanup_report['removed_files'].append(file_path)
                    cleanup_report['total_size_saved'] += size
                except Exception as e:
                    print(f"   오류: {file_path} - {e}")
    
    # 2. 로그 파일 제거
    print("2. 로그 파일 정리 중...")
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.log'):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleanup_report['removed_files'].append(file_path)
                    cleanup_report['total_size_saved'] += size
                    print(f"   제거: {file_path}")
                except Exception as e:
                    print(f"   오류: {file_path} - {e}")
    
    # 3. 백업 파일 제거
    print("3. 백업 및 테스트 파일 정리 중...")
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if any(pattern in file for pattern in ['_backup', '_old', '.bak', '.backup']):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleanup_report['removed_files'].append(file_path)
                    cleanup_report['total_size_saved'] += size
                    print(f"   제거: {file_path}")
                except Exception as e:
                    print(f"   오류: {file_path} - {e}")
    
    # 4. 중복 템플릿 제거
    print("4. 중복 템플릿 정리 중...")
    for template in CLEANUP_PATTERNS['duplicate_templates']:
        for root, dirs, files in os.walk(source_dir):
            if template in files:
                file_path = os.path.join(root, template)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleanup_report['removed_files'].append(file_path)
                    cleanup_report['total_size_saved'] += size
                    print(f"   제거: {file_path}")
                except Exception as e:
                    print(f"   오류: {file_path} - {e}")
    
    # 5. .git 폴더 제거 (자동 제외)
    git_path = os.path.join(source_dir, '.git')
    if os.path.exists(git_path):
        print("5. .git 폴더 발견... (복사에서 제외됨)")
    
    # 정리 보고서 저장
    report_path = os.path.join(source_dir, 'cleanup_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(cleanup_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n정리 완료!")
    print(f"제거된 파일: {len(cleanup_report['removed_files'])}개")
    print(f"제거된 폴더: {len(cleanup_report['removed_dirs'])}개")
    print(f"절약된 공간: {cleanup_report['total_size_saved'] / 1024 / 1024:.2f} MB")
    print(f"보고서 저장: {report_path}")
    
    return cleanup_report

def get_dir_size(path):
    """디렉토리 크기 계산"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except Exception:
        pass
    return total

def copy_to_external_drive(source_dir, target_dir):
    """외장하드로 복사"""
    print(f"\n프로젝트를 외장하드로 복사 중...")
    print(f"원본: {source_dir}")
    print(f"대상: {target_dir}")
    
    # 제외할 패턴
    exclude_patterns = ['.git', '__pycache__', '*.pyc', '*.log', '*.bak', '.vscode', '.idea']
    
    # 대상 디렉토리 생성
    os.makedirs(target_dir, exist_ok=True)
    
    # 복사 진행
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(source_dir):
        # 제외할 디렉토리 필터링
        dirs[:] = [d for d in dirs if d not in exclude_patterns]
        
        # 상대 경로 계산
        rel_path = os.path.relpath(root, source_dir)
        target_root = os.path.join(target_dir, rel_path)
        
        # 디렉토리 생성
        os.makedirs(target_root, exist_ok=True)
        
        # 파일 복사
        for file in files:
            # 제외할 파일 패턴 체크
            if any(file.endswith(ext) for ext in ['.pyc', '.log', '.bak']) or file.startswith('.'):
                continue
                
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_root, file)
            
            try:
                shutil.copy2(source_file, target_file)
                total_files += 1
                total_size += os.path.getsize(source_file)
                
                if total_files % 100 == 0:
                    print(f"   {total_files}개 파일 복사됨...")
            except Exception as e:
                print(f"   오류: {file} - {e}")
    
    print(f"\n복사 완료!")
    print(f"총 파일: {total_files}개")
    print(f"총 크기: {total_size / 1024 / 1024:.2f} MB")
    
    return total_files, total_size

if __name__ == "__main__":
    source_dir = r"C:\Users\apro\OneDrive\Desktop\EHR_V1.0"
    target_dir = r"D:\AIRISS_project"
    
    print("EHR 프로젝트 정리 및 이관 스크립트")
    print("=" * 50)
    
    # 1단계: 프로젝트 정리
    print("\n[1단계] 프로젝트 정리")
    cleanup_report = cleanup_project(source_dir)
    
    # 2단계: 외장하드로 복사
    print("\n[2단계] 외장하드로 복사")
    print("외장하드로 복사를 시작합니다...")
    
    # D 드라이브 확인
    if os.path.exists('D:\\'):
        total_files, total_size = copy_to_external_drive(source_dir, target_dir)
        
        print("\n모든 작업이 완료되었습니다!")
        print(f"프로젝트가 다음 위치로 이관되었습니다: {target_dir}")
    else:
        print("\nD 드라이브를 찾을 수 없습니다. 외장하드가 연결되었는지 확인해주세요.")