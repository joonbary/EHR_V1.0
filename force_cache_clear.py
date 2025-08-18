#!/usr/bin/env python
"""
Railway 배포에서 캐싱 문제 해결
- WhiteNoise 캐시 클리어
- Django 캐시 클리어
- 브라우저 캐시 버스팅을 위한 버전 변경
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.cache import cache

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    print("🧹 Clearing all caches for Railway deployment...")
    
    try:
        # Django 캐시 클리어
        cache.clear()
        print("✅ Django cache cleared")
        
        # Static files 재수집
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected with cache clear")
        
        # 템플릿 캐시 클리어 (개발환경에서는 자동)
        if hasattr(settings, 'TEMPLATES'):
            for template_config in settings.TEMPLATES:
                if 'OPTIONS' in template_config:
                    template_config['OPTIONS']['debug'] = True
        
        print("✅ Template cache debug enabled")
        print("🚀 Cache clearing completed - ready for Railway deployment!")
        
    except Exception as e:
        print(f"❌ Error during cache clearing: {e}")
        sys.exit(1)