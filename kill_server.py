import os
import signal
import psutil

# 모든 Python 프로세스 찾기
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Python 프로세스이고 manage.py runserver를 실행 중인 경우
        if proc.info['name'] and 'python' in proc.info['name'].lower():
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('manage.py' in arg and 'runserver' in str(cmdline) for arg in cmdline):
                print(f"Killing Django server process: PID {proc.info['pid']}")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

print("Django server processes killed.")