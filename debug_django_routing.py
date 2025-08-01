#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django 라우팅 디버그 스크립트
현재 등록된 모든 URL 패턴을 출력
"""

import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.urls import get_resolver
from django.core.management import execute_from_command_line

def show_urls(urllist, depth=0):
    """재귀적으로 모든 URL 패턴 출력"""
    for entry in urllist:
        print("  " * depth, end="")
        if hasattr(entry, 'url_patterns'):
            # namespace가 있는 경우
            print(f"[{entry.namespace}]" if entry.namespace else "[no namespace]")
            show_urls(entry.url_patterns, depth + 1)
        else:
            # 실제 URL 패턴
            if hasattr(entry, 'pattern'):
                print(f"{entry.pattern} -> {entry.callback}")

def main():
    print("="*60)
    print("Django URL 라우팅 디버그")
    print("="*60)
    
    # 현재 등록된 모든 URL 출력
    print("\n현재 등록된 URL 패턴:")
    print("-"*60)
    
    resolver = get_resolver()
    show_urls(resolver.url_patterns)
    
    print("\n" + "-"*60)
    print("\n주요 URL 확인:")
    
    from django.urls import reverse, NoReverseMatch
    
    test_urls = [
        ('home', '홈페이지'),
        ('dashboard', '대시보드'),
        ('job_profiles:list', '직무체계도'),
        ('employees:list', '직원목록'),
    ]
    
    for url_name, description in test_urls:
        try:
            url = reverse(url_name)
            print(f"✓ {description}: {url}")
        except NoReverseMatch:
            print(f"✗ {description}: URL '{url_name}' 찾을 수 없음")
    
    print("\n" + "="*60)
    
    # 템플릿 경로 확인
    from django.conf import settings
    print("\n템플릿 디렉토리 설정:")
    print("-"*60)
    for template_config in settings.TEMPLATES:
        print(f"DIRS: {template_config.get('DIRS', [])}")
        print(f"APP_DIRS: {template_config.get('APP_DIRS', False)}")
    
    # 실제 템플릿 파일 확인
    print("\n실제 템플릿 파일:")
    print("-"*60)
    
    template_dirs = []
    for template_config in settings.TEMPLATES:
        template_dirs.extend(template_config.get('DIRS', []))
    
    # 앱별 템플릿 디렉토리도 확인
    if template_config.get('APP_DIRS'):
        for app in settings.INSTALLED_APPS:
            if '.' not in app:  # 내부 앱만
                app_template_dir = os.path.join(settings.BASE_DIR, app, 'templates')
                if os.path.exists(app_template_dir):
                    template_dirs.append(app_template_dir)
    
    for template_dir in template_dirs:
        if os.path.exists(template_dir):
            print(f"\n{template_dir}:")
            for root, dirs, files in os.walk(template_dir):
                level = root.replace(str(template_dir), '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    if file.endswith('.html'):
                        print(f"{subindent}{file}")

if __name__ == '__main__':
    main()