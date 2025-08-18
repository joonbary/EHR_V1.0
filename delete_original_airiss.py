#!/usr/bin/env python
"""
원본 AIRISS v4 폴더 삭제
"""
import shutil
import os
import time

def main():
    source_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"
    
    print("원본 AIRISS v4 폴더 삭제")
    print("="*60)
    print(f"삭제할 폴더: {source_dir}")
    print("\n[주의] 이 작업은 되돌릴 수 없습니다!")
    print("D드라이브에 복사가 완료되었는지 확인하세요.")
    print(f"복사된 위치: D:\\AIRISS_project_clean")
    print("\n5초 후 삭제가 시작됩니다. 취소하려면 Ctrl+C를 누르세요...")
    
    for i in range(5, 0, -1):
        print(f"{i}초...", end='\r')
        time.sleep(1)
    
    print("\n삭제 중...")
    
    try:
        # 읽기 전용 속성 제거
        def remove_readonly(func, path, exc_info):
            import stat
            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)
        
        shutil.rmtree(source_dir, onerror=remove_readonly)
        print("\n[완료] 원본 폴더가 삭제되었습니다!")
        
        # AIRISS 폴더가 비어있으면 삭제
        airiss_dir = r"C:\Users\apro\OneDrive\Desktop\AIRISS"
        if os.path.exists(airiss_dir) and not os.listdir(airiss_dir):
            os.rmdir(airiss_dir)
            print("[완료] AIRISS 폴더도 삭제되었습니다!")
            
    except Exception as e:
        print(f"\n[오류] 삭제 실패: {e}")
        return
    
    print("\n" + "="*60)
    print("모든 작업이 완료되었습니다!")
    print("AIRISS v4 프로젝트가 D드라이브로 이동되었습니다.")
    print("새 위치: D:\\AIRISS_project_clean")
    print("="*60)

if __name__ == "__main__":
    main()