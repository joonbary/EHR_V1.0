#!/usr/bin/env python
"""
EHR_V1.0 프로젝트 복구 스크립트
"""
import os
import shutil

source = r"D:\AIRISS_project"
target = r"C:\Users\apro\OneDrive\Desktop\EHR_V1.0"

print("EHR_V1.0 프로젝트 복구 시작...")
print(f"복구원: {source}")
print(f"복구대상: {target}")

if not os.path.exists(source):
    print("\n[오류] D:\\AIRISS_project를 찾을 수 없습니다!")
else:
    # xcopy 명령어 사용 (Windows에서 더 안정적)
    cmd = f'xcopy "{source}" "{target}" /E /I /Y /Q'
    print(f"\n실행 명령: {cmd}")
    
    result = os.system(cmd)
    
    if result == 0:
        print("\n[성공] 복구가 완료되었습니다!")
    else:
        print("\n[실패] 복구 중 오류가 발생했습니다.")