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
    
    print(f"Starting server on port {port}...")
    
    # 마이그레이션 실행
    print("Running migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)
    
    # 정적 파일 수집
    print("Collecting static files...")
    subprocess.run([sys.executable, 'manage.py', 'collectstatic', '--noinput', '--clear'], check=True)
    
    # Gunicorn 시작
    print(f"Starting Gunicorn on 0.0.0.0:{port}...")
    os.system(f'gunicorn ehr_system.wsgi:application --bind 0.0.0.0:{port} --workers 2 --timeout 120 --access-logfile - --error-logfile - --log-level info')

if __name__ == '__main__':
    main()