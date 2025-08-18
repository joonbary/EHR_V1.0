#!/usr/bin/env python
"""
AIRISS v4 프로젝트를 D드라이브로 완전 이동
"""
import os
import shutil
import time
from datetime import datetime

def main():
    source_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    target_dir = r"D:\AIRISS_project"
    
    print("AIRISS v4 프로젝트 이동 스크립트")
    print("="*60)
    print(f"원본: {source_dir}")
    print(f"대상: {target_dir}")
    
    # 원본 확인
    if not os.path.exists(source_dir):
        print(f"\n[오류] 원본 폴더를 찾을 수 없습니다: {source_dir}")
        return
    
    # 파일 개수 확인
    file_count = sum(1 for _, _, files in os.walk(source_dir) for _ in files)
    print(f"\n[확인] 이동할 파일: {file_count}개")
    
    # D드라이브 확인
    if not os.path.exists("D:\\"):
        print("\n[오류] D 드라이브를 찾을 수 없습니다.")
        return
    
    # 대상 폴더가 이미 존재하면 확인
    if os.path.exists(target_dir):
        print(f"\n[경고] 대상 폴더가 이미 존재합니다: {target_dir}")
        print("기존 폴더를 삭제하고 새로 복사합니다...")
        try:
            shutil.rmtree(target_dir)
            print("[완료] 기존 폴더 삭제 완료")
        except Exception as e:
            print(f"[오류] 기존 폴더 삭제 실패: {e}")
            return
    
    print("\n이동을 시작합니다...")
    print("[단계 1/2] 파일 복사 중...")
    
    try:
        # 복사 실행
        shutil.copytree(source_dir, target_dir)
        print("[완료] 파일 복사 완료!")
        
        # 복사 확인
        copied_files = sum(1 for _, _, files in os.walk(target_dir) for _ in files)
        print(f"[확인] 복사된 파일: {copied_files}개")
        
        # 원본 삭제
        print("\n[단계 2/2] 원본 삭제 중...")
        print("5초 후 원본이 삭제됩니다. 취소하려면 Ctrl+C를 누르세요...")
        
        for i in range(5, 0, -1):
            print(f"{i}초...", end='\r')
            time.sleep(1)
        
        print("\n원본 삭제 중...")
        shutil.rmtree(source_dir)
        print("[완료] 원본 삭제 완료!")
        
    except Exception as e:
        print(f"\n[오류] 작업 중 오류 발생: {e}")
        return
    
    # 완료 정보
    info = f"""# AIRISS v4 프로젝트 이동 완료

## 이동 정보
- 이동 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 원본 위치: {source_dir} (삭제됨)
- 현재 위치: {target_dir}
- 파일 개수: {copied_files}개

## 개발 환경 설정

### VS Code에서 열기
1. VS Code 실행
2. File > Open Folder
3. D:\\AIRISS_project 선택

### 터미널에서 이동
```bash
cd /d D:\\AIRISS_project
```

### 가상환경 재생성 (필요시)
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

### 서버 실행
```bash
python app.py
# 또는
python main.py
```
"""
    
    # 정보 파일 저장
    info_path = os.path.join(target_dir, "MIGRATION_INFO.md")
    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(info)
    
    print("\n" + "="*60)
    print("[성공] AIRISS v4 프로젝트가 D드라이브로 완전히 이동되었습니다!")
    print(f"새 위치: {target_dir}")
    print(f"정보 파일: {info_path}")
    print("="*60)

if __name__ == "__main__":
    main()