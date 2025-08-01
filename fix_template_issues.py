#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
템플릿 및 URL 네임스페이스 문제 해결
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_dashboard_template():
    """dashboard.html이 올바른 base 템플릿을 사용하도록 수정"""
    dashboard_path = BASE_DIR / 'templates' / 'dashboard.html'
    
    if dashboard_path.exists():
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # base.html을 base_simple.html로 변경
        if 'extends "base.html"' in content:
            content = content.replace('extends "base.html"', 'extends "base_simple.html"')
            
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ dashboard.html 수정됨 - base_simple.html 사용")
        else:
            print("  dashboard.html은 이미 올바른 템플릿 사용 중")

def fix_base_template():
    """base.html에서 reports URL 제거 또는 수정"""
    base_path = BASE_DIR / 'templates' / 'base.html'
    
    if base_path.exists():
        # 백업
        backup_path = str(base_path) + '.bak'
        with open(base_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # reports:dashboard URL 제거 또는 주석 처리
        lines = content.split('\n')
        new_lines = []
        skip_count = 0
        
        for i, line in enumerate(lines):
            if skip_count > 0:
                skip_count -= 1
                continue
                
            if "reports:dashboard" in line:
                # 이 li 태그 전체를 주석 처리
                if '<li' in lines[i-2] if i >= 2 else False:
                    new_lines.append('                    <!-- Reports 메뉴 제거됨')
                    new_lines.append('                    ' + lines[i-2].strip())
                if '<li' in lines[i-1] if i >= 1 else False:
                    new_lines.append('                    ' + lines[i-1].strip())
                new_lines.append('                    ' + line.strip())
                
                # 다음 몇 줄도 확인
                for j in range(1, 5):
                    if i + j < len(lines) and '</li>' in lines[i + j]:
                        new_lines.append('                    ' + lines[i + j].strip())
                        new_lines.append('                    -->')
                        skip_count = j
                        break
            else:
                new_lines.append(line)
        
        # 저장
        with open(base_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✓ base.html 수정됨 - reports URL 제거")

def add_reports_urls():
    """reports URL 추가 (필요한 경우)"""
    main_urls_path = BASE_DIR / 'ehr_system' / 'urls.py'
    
    if main_urls_path.exists():
        with open(main_urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # reports URL이 없으면 추가
        if "path('reports/'," not in content:
            # urlpatterns 찾기
            if 'urlpatterns = [' in content:
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    new_lines.append(line)
                    # selfservice 다음에 reports 추가
                    if "path('selfservice/'," in line:
                        new_lines.append("    path('reports/', include('reports.urls')),")
                
                content = '\n'.join(new_lines)
                
                with open(main_urls_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✓ ehr_system/urls.py에 reports URL 추가됨")

def create_reports_urls():
    """reports/urls.py 생성"""
    reports_dir = BASE_DIR / 'reports'
    if reports_dir.exists():
        urls_path = reports_dir / 'urls.py'
        
        if not urls_path.exists():
            urls_content = '''from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
]'''
            
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(urls_content)
            
            print("✓ reports/urls.py 생성됨")
        
        # views.py도 확인
        views_path = reports_dir / 'views.py'
        if views_path.exists():
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'ReportDashboardView' not in content:
                # 기본 뷰 추가
                views_content = '''from django.shortcuts import render
from django.views.generic import TemplateView


class ReportDashboardView(TemplateView):
    """리포트 대시보드 뷰"""
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
'''
                
                with open(views_path, 'w', encoding='utf-8') as f:
                    f.write(views_content)
                
                print("✓ reports/views.py 수정됨")
        
        # 템플릿 디렉토리 생성
        templates_dir = reports_dir / 'templates' / 'reports'
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 기본 템플릿 생성
        dashboard_template_path = templates_dir / 'dashboard.html'
        if not dashboard_template_path.exists():
            template_content = '''{% extends "base_simple.html" %}
{% load static %}

{% block title %}리포트 - OK금융그룹{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1>리포트</h1>
    <p>리포트 기능은 준비 중입니다.</p>
</div>
{% endblock %}'''
            
            with open(dashboard_template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            print("✓ reports/templates/reports/dashboard.html 생성됨")

def main():
    print("="*60)
    print("템플릿 및 URL 문제 해결")
    print("="*60)
    
    print("\n1. 대시보드 템플릿 수정...")
    fix_dashboard_template()
    
    print("\n2. base.html 수정...")
    fix_base_template()
    
    print("\n3. reports URL 설정...")
    add_reports_urls()
    create_reports_urls()
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print("\n해결 방법:")
    print("1. dashboard.html이 base_simple.html을 사용하도록 변경")
    print("2. base.html에서 reports 메뉴 제거")
    print("3. reports 앱의 URL 구조 생성")
    print("\n다음 단계:")
    print("1. python manage.py runserver")
    print("2. http://localhost:8000/ 접속")
    print("="*60)

if __name__ == '__main__':
    main()