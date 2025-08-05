#!/usr/bin/env python
import os
import sys
import subprocess

def main():
    """서버 시작 스크립트"""
    
    # 환경 변수 설정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    
    # 포트 설정
    port = os.environ.get('PORT', '8000')
    
    print(f"Starting server on port {port}...", flush=True)
    
    # 마이그레이션 실행
    print("Running migrations...", flush=True)
    try:
        subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
        print("Migrations completed successfully", flush=True)
    except Exception as e:
        print(f"Migration error: {e}", flush=True)
    
    # 정적 파일 수집
    print("Collecting static files...", flush=True)
    try:
        subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'], check=True)
        print("Static files collected successfully", flush=True)
    except Exception as e:
        print(f"Static file collection error: {e}", flush=True)
    
    # Gunicorn 시작
    print(f"Starting Gunicorn on 0.0.0.0:{port}...", flush=True)
    
    # exec를 사용하여 현재 프로세스를 Gunicorn으로 교체
    os.execvp('gunicorn', [
        'gunicorn',
        'ehr_system.wsgi:application',
        '--bind', f'0.0.0.0:{port}',
        '--workers', '2',
        '--timeout', '120',
        '--access-logfile', '-',
        '--error-logfile', '-',
        '--log-level', 'info',
        '--preload'
    ])

if __name__ == '__main__':
    main()