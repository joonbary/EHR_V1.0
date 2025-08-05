#!/usr/bin/env python
"""
AIRISS v4 폴더 크기 분석 및 정리 대상 파악
"""
import os
from collections import defaultdict

def get_folder_size(path):
    """폴더 크기 계산"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total += os.path.getsize(filepath)
            except:
                pass
    return total

def analyze_folder(root_path):
    """폴더 구조 분석"""
    large_folders = []
    node_modules = []
    venv_folders = []
    cache_folders = []
    temp_folders = []
    backup_folders = []
    
    print("폴더 분석 중...")
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_path = os.path.relpath(dirpath, root_path)
        
        # node_modules 찾기
        if 'node_modules' in dirnames:
            node_path = os.path.join(dirpath, 'node_modules')
            size = get_folder_size(node_path)
            node_modules.append((node_path, size))
            print(f"  Found node_modules: {size/1024/1024:.1f} MB")
        
        # venv 폴더 찾기
        for d in dirnames:
            if d.startswith('venv') or d == 'env':
                venv_path = os.path.join(dirpath, d)
                size = get_folder_size(venv_path)
                venv_folders.append((venv_path, size))
                print(f"  Found venv: {d} - {size/1024/1024:.1f} MB")
        
        # 캐시 폴더 찾기
        for d in dirnames:
            if '__pycache__' in d or '.cache' in d:
                cache_path = os.path.join(dirpath, d)
                size = get_folder_size(cache_path)
                cache_folders.append((cache_path, size))
        
        # 임시/백업 폴더 찾기
        for d in dirnames:
            if any(x in d.lower() for x in ['temp', 'tmp', 'backup', 'archive', '_old']):
                folder_path = os.path.join(dirpath, d)
                size = get_folder_size(folder_path)
                if 'backup' in d.lower():
                    backup_folders.append((folder_path, size))
                else:
                    temp_folders.append((folder_path, size))
    
    return {
        'node_modules': node_modules,
        'venv_folders': venv_folders,
        'cache_folders': cache_folders,
        'temp_folders': temp_folders,
        'backup_folders': backup_folders
    }

def main():
    airiss_path = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    
    print("AIRISS v4 폴더 크기 분석")
    print("="*60)
    
    if not os.path.exists(airiss_path):
        print(f"오류: 폴더를 찾을 수 없습니다: {airiss_path}")
        return
    
    # 전체 크기 계산
    print("전체 크기 계산 중...")
    total_size = get_folder_size(airiss_path)
    print(f"\n전체 크기: {total_size/1024/1024/1024:.2f} GB ({total_size/1024/1024:.0f} MB)")
    
    # 상세 분석
    print("\n상세 분석 중...")
    analysis = analyze_folder(airiss_path)
    
    # 결과 출력
    print("\n" + "="*60)
    print("정리 가능한 폴더들:")
    print("="*60)
    
    total_removable = 0
    
    # node_modules
    if analysis['node_modules']:
        print("\n[node_modules 폴더]")
        for path, size in analysis['node_modules']:
            print(f"  {os.path.relpath(path, airiss_path)}: {size/1024/1024:.1f} MB")
            total_removable += size
    
    # venv 폴더
    if analysis['venv_folders']:
        print("\n[가상환경 폴더]")
        for path, size in analysis['venv_folders']:
            print(f"  {os.path.relpath(path, airiss_path)}: {size/1024/1024:.1f} MB")
            total_removable += size
    
    # 백업 폴더
    if analysis['backup_folders']:
        print("\n[백업 폴더]")
        for path, size in analysis['backup_folders']:
            print(f"  {os.path.relpath(path, airiss_path)}: {size/1024/1024:.1f} MB")
            total_removable += size
    
    # 캐시 폴더
    cache_total = sum(size for _, size in analysis['cache_folders'])
    if cache_total > 0:
        print(f"\n[캐시 폴더] 총 {len(analysis['cache_folders'])}개: {cache_total/1024/1024:.1f} MB")
        total_removable += cache_total
    
    # 임시 폴더
    if analysis['temp_folders']:
        print("\n[임시 폴더]")
        for path, size in analysis['temp_folders']:
            print(f"  {os.path.relpath(path, airiss_path)}: {size/1024/1024:.1f} MB")
            total_removable += size
    
    print("\n" + "="*60)
    print(f"정리 가능한 총 크기: {total_removable/1024/1024/1024:.2f} GB ({total_removable/1024/1024:.0f} MB)")
    print(f"정리 후 예상 크기: {(total_size-total_removable)/1024/1024/1024:.2f} GB")
    print("="*60)
    
    # 권장사항
    print("\n권장사항:")
    print("1. node_modules와 venv 폴더를 제외하고 복사")
    print("2. 복사 후 D드라이브에서 다시 설치:")
    print("   - npm install (Frontend)")
    print("   - python -m venv venv && pip install -r requirements.txt (Backend)")

if __name__ == "__main__":
    main()