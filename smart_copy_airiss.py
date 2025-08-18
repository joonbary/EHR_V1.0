#!/usr/bin/env python
"""
AIRISS v4 스마트 복사 - 불필요한 파일 제외하고 복사
"""
import os
import shutil
from datetime import datetime

# 제외할 폴더 패턴
EXCLUDE_DIRS = [
    'node_modules',
    'venv',
    'venv311',
    'venv_backup', 
    'venv_new',
    '__pycache__',
    '.git',
    'cleanup_backup',
    '_archive_20250726_143258',
    'temp',
    'temp_data',
    'backups',
    'logs',
    '.cache'
]

# 제외할 파일 확장자
EXCLUDE_EXTENSIONS = [
    '.pyc',
    '.pyo',
    '.log',
    '.tmp',
    '.temp'
]

def should_exclude(path, root):
    """파일/폴더를 제외해야 하는지 확인"""
    rel_path = os.path.relpath(path, root)
    
    # 폴더 제외
    for exclude in EXCLUDE_DIRS:
        if exclude in rel_path.split(os.sep):
            return True
    
    # 파일 확장자 제외
    if os.path.isfile(path):
        for ext in EXCLUDE_EXTENSIONS:
            if path.endswith(ext):
                return True
    
    return False

def smart_copy(src, dst):
    """스마트 복사 - 불필요한 파일 제외"""
    print(f"스마트 복사 시작...")
    print(f"원본: {src}")
    print(f"대상: {dst}")
    
    os.makedirs(dst, exist_ok=True)
    
    copied_files = 0
    copied_size = 0
    skipped_files = 0
    skipped_size = 0
    
    for root, dirs, files in os.walk(src):
        # 제외할 디렉토리 필터링
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), src)]
        
        # 상대 경로 계산
        rel_path = os.path.relpath(root, src)
        if rel_path == '.':
            target_root = dst
        else:
            target_root = os.path.join(dst, rel_path)
        
        # 디렉토리 생성
        if not os.path.exists(target_root):
            os.makedirs(target_root)
        
        # 파일 복사
        for file in files:
            src_file = os.path.join(root, file)
            
            if should_exclude(src_file, src):
                try:
                    size = os.path.getsize(src_file)
                    skipped_files += 1
                    skipped_size += size
                except:
                    pass
                continue
            
            dst_file = os.path.join(target_root, file)
            
            try:
                shutil.copy2(src_file, dst_file)
                size = os.path.getsize(src_file)
                copied_files += 1
                copied_size += size
                
                if copied_files % 100 == 0:
                    print(f"  {copied_files}개 파일 복사됨... ({copied_size/1024/1024:.1f} MB)")
            except Exception as e:
                print(f"  오류: {file} - {e}")
    
    return copied_files, copied_size, skipped_files, skipped_size

def main():
    src = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    dst = r"D:\AIRISS_project"
    
    print("AIRISS v4 스마트 복사")
    print("="*60)
    print("불필요한 파일을 제외하고 복사합니다.")
    print("제외: node_modules, venv, 백업, 캐시 등")
    print("="*60)
    
    start_time = datetime.now()
    
    # 기존 폴더 처리
    if os.path.exists(dst):
        print(f"\n[경고] 대상 폴더가 이미 존재합니다: {dst}")
        # 새 폴더명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = f"{dst}_{timestamp}"
        print(f"새 폴더로 복사합니다: {dst}")
    
    # 스마트 복사 실행
    print("\n복사 시작...")
    copied_files, copied_size, skipped_files, skipped_size = smart_copy(src, dst)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 결과 출력
    print("\n" + "="*60)
    print("복사 완료!")
    print(f"복사된 파일: {copied_files}개 ({copied_size/1024/1024:.1f} MB)")
    print(f"제외된 파일: {skipped_files}개 ({skipped_size/1024/1024:.1f} MB)")
    print(f"소요 시간: {duration:.1f}초")
    print("="*60)
    
    # 설치 가이드 생성
    guide = """# AIRISS v4 설치 가이드

프로젝트가 D:\\AIRISS_project로 복사되었습니다.

## 다음 단계:

### 1. Backend 설정
```bash
cd D:\\AIRISS_project
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Frontend 설정
```bash
cd D:\\AIRISS_project\\airiss-v4-frontend
npm install
```

### 3. 서버 실행
```bash
# Backend
cd D:\\AIRISS_project
python app.py

# Frontend (새 터미널)
cd D:\\AIRISS_project\\airiss-v4-frontend
npm start
```
"""
    
    guide_path = os.path.join(dst, "SETUP_GUIDE.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\n설치 가이드: {guide_path}")

if __name__ == "__main__":
    main()