#!/usr/bin/env python
import os
import sys
import signal
import psutil
import time

def kill_django_processes():
    """모든 Django 개발 서버 프로세스 종료"""
    killed = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('manage.py' in str(arg) and 'runserver' in str(arg) for arg in cmdline):
                print(f"[INFO] Killing Django process: PID {proc.info['pid']}")
                proc.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if killed > 0:
        print(f"[OK] Killed {killed} Django processes")
        time.sleep(2)  # 프로세스 정리를 위한 대기
    else:
        print("[INFO] No Django processes found")

def clear_python_cache():
    """Python 캐시 파일 삭제"""
    import shutil
    
    removed = 0
    for root, dirs, files in os.walk('.'):
        # __pycache__ 디렉토리 삭제
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                removed += 1
            except:
                pass
        
        # .pyc 파일 삭제
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                    removed += 1
                except:
                    pass
    
    print(f"[OK] Removed {removed} cache files/directories")

if __name__ == "__main__":
    print("=" * 50)
    print("Django Server Force Restart Tool")
    print("=" * 50)
    
    # 1. 기존 Django 프로세스 종료
    print("\n1. Killing existing Django processes...")
    kill_django_processes()
    
    # 2. Python 캐시 제거
    print("\n2. Clearing Python cache...")
    clear_python_cache()
    
    # 3. Django 캐시 제거
    print("\n3. Clearing Django cache...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    import django
    django.setup()
    from django.core.cache import cache
    cache.clear()
    print("[OK] Django cache cleared")
    
    print("\n" + "=" * 50)
    print("Ready to start fresh Django server!")
    print("Run: python manage.py runserver 8000")
    print("=" * 50)