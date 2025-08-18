#!/usr/bin/env python
"""
Railway 배포용 Static Files 수집 스크립트
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    print("🔄 Collecting static files for Railway deployment...")
    
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully!")
        
        # Static files 디렉토리 확인
        static_root = settings.STATIC_ROOT
        if os.path.exists(static_root):
            file_count = sum([len(files) for r, d, files in os.walk(static_root)])
            print(f"📁 Static files directory: {static_root}")
            print(f"📊 Total static files: {file_count}")
        else:
            print("❌ Static files directory not found!")
            
    except Exception as e:
        print(f"❌ Error collecting static files: {e}")
        sys.exit(1)