#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
누락된 파일 생성 및 레거시 파일 삭제 스크립트
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent

def delete_legacy_files():
    """레거시 파일 삭제"""
    print("1. 레거시 파일 삭제 중...")
    
    legacy_files = [
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_tree_map_simple.html',
        'job_profiles/templates/job_profiles/job_profile_list.html',
        'static/js/JobProfileTreeMap.js',
        'static/css/JobProfileTreeMap.css',
    ]
    
    for file_path in legacy_files:
        full_path = BASE_DIR / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✓ 삭제됨: {file_path}")
            except Exception as e:
                print(f"  ✗ 삭제 실패: {file_path} - {e}")
        else:
            print(f"  - 이미 없음: {file_path}")

def create_job_treemap_template():
    """job_treemap.html 템플릿 생성"""
    content = '''{% extends "base_simple.html" %}
{% load static %}

{% block title %}직무 체계도 - OK금융그룹{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
.treemap-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
}

.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-title {
    font-size: 36px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8px;
}

.page-title i {
    color: #2e86de;
    margin-right: 12px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.stat-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
}

.stat-card:nth-child(1) .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card:nth-child(2) .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-card:nth-child(3) .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-card:nth-child(4) .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #2c3e50;
}

.stat-label {
    font-size: 14px;
    color: #6c757d;
    margin-top: 4px;
}

.controls-wrapper {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}

.search-box {
    flex: 1;
    min-width: 300px;
    position: relative;
}

.search-box i {
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    color: #6c757d;
}

.search-input {
    width: 100%;
    padding: 12px 12px 12px 44px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 16px;
}

.filter-group {
    display: flex;
    gap: 8px;
}

.filter-btn {
    padding: 10px 20px;
    border: 2px solid #e9ecef;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}

.filter-btn.active {
    background: #2e86de;
    border-color: #2e86de;
    color: white;
}

.treemap-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

.group-container {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.group-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #e9ecef;
}

.non-pl-section .group-title {
    color: #2e86de;
    border-bottom-color: #2e86de;
}

.pl-section .group-title {
    color: #ff6b6b;
    border-bottom-color: #ff6b6b;
}

.loading-state {
    text-align: center;
    padding: 40px;
    color: #6c757d;
}

.loading-state i {
    font-size: 32px;
    margin-bottom: 12px;
}

@media (max-width: 1024px) {
    .treemap-main {
        grid-template-columns: 1fr;
    }
}
</style>
{% endblock %}

{% block content %}
<div class="treemap-container">
    <div class="page-header">
        <h1 class="page-title">
            <i class="fas fa-sitemap"></i>
            직무 체계도
        </h1>
        <p class="text-muted">OK금융그룹의 전체 직무 체계를 한눈에 확인하세요</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-layer-group"></i>
            </div>
            <div>
                <div class="stat-number">{{ total_categories|default:"0" }}</div>
                <div class="stat-label">직군</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
            </div>
            <div>
                <div class="stat-number">{{ total_job_types|default:"0" }}</div>
                <div class="stat-label">직종</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-user-tie"></i>
            </div>
            <div>
                <div class="stat-number">{{ total_job_roles|default:"0" }}</div>
                <div class="stat-label">직무</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div>
                <div class="stat-number">{{ total_profiles|default:"0" }}</div>
                <div class="stat-label">직무기술서</div>
            </div>
        </div>
    </div>

    <div class="controls-wrapper">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="searchInput" placeholder="직무명으로 검색..." class="search-input">
        </div>
        <div class="filter-group">
            <button class="filter-btn active" data-filter="all">
                <i class="fas fa-th"></i> 전체
            </button>
            <button class="filter-btn" data-filter="non-pl">
                <i class="fas fa-users"></i> Non-PL
            </button>
            <button class="filter-btn" data-filter="pl">
                <i class="fas fa-user-shield"></i> PL
            </button>
        </div>
    </div>

    <div class="treemap-main">
        <div class="group-container non-pl-section" data-group="non-pl">
            <h2 class="group-title">
                <i class="fas fa-users"></i>
                Non-PL 직군
            </h2>
            <div id="nonPlContent" class="group-body">
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </div>

        <div class="group-container pl-section" data-group="pl">
            <h2 class="group-title">
                <i class="fas fa-user-shield"></i>
                PL 직군
            </h2>
            <div id="plContent" class="group-body">
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 모달은 필요시 JavaScript로 생성 -->
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 간단한 로딩 표시
    setTimeout(() => {
        document.querySelectorAll('.loading-state').forEach(el => {
            el.innerHTML = '<p class="text-muted">데이터가 없습니다.</p>';
        });
    }, 2000);
    
    // 필터 버튼
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
</script>
{% endblock %}'''
    
    # 디렉토리 생성
    template_dir = BASE_DIR / 'job_profiles' / 'templates' / 'job_profiles'
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # 파일 생성
    template_path = template_dir / 'job_treemap.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ 생성됨: job_profiles/templates/job_profiles/job_treemap.html")

def create_ehr_system_views():
    """ehr_system/views.py 생성"""
    content = '''from django.views.generic import TemplateView
from django.db.models import Count
from datetime import datetime, timedelta

from employees.models import Employee
from job_profiles.models import JobRole, JobProfile


class DashboardView(TemplateView):
    """메인 대시보드 뷰"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터
        context['stats'] = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_departments': Employee.objects.filter(is_active=True).values('department').distinct().count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'completed_profiles': JobProfile.objects.filter(is_active=True).count(),
        }
        
        return context'''
    
    views_path = BASE_DIR / 'ehr_system' / 'views.py'
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ 생성됨: ehr_system/views.py")

def create_static_files():
    """누락된 static 파일 생성"""
    print("\n3. Static 파일 생성 중...")
    
    # CSS 디렉토리
    css_dir = BASE_DIR / 'static' / 'css'
    css_dir.mkdir(parents=True, exist_ok=True)
    
    # job_treemap_unified.css (최소 버전)
    css_content = '''/* 직무체계도 통합 CSS */
/* 기본 스타일은 인라인으로 처리됨 */'''
    
    css_path = css_dir / 'job_treemap_unified.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print(f"  ✓ 생성됨: static/css/job_treemap_unified.css")
    
    # JS 디렉토리
    js_dir = BASE_DIR / 'static' / 'js'
    js_dir.mkdir(parents=True, exist_ok=True)
    
    # job_treemap_unified.js (최소 버전)
    js_content = '''// 직무체계도 통합 JavaScript
console.log('Job TreeMap Unified JS loaded');'''
    
    js_path = js_dir / 'job_treemap_unified.js'
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"  ✓ 생성됨: static/js/job_treemap_unified.js")

def update_urls():
    """URL 설정 업데이트"""
    print("\n4. URL 설정 업데이트 중...")
    
    # ehr_system/urls.py 업데이트
    main_urls_content = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 메인 대시보드
    path('', DashboardView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # 앱별 URL
    path('job-profiles/', include('job_profiles.urls')),
    path('employees/', include('employees.urls')),
    path('evaluations/', include('evaluations.urls')),
    path('compensation/', include('compensation.urls')),
    path('promotions/', include('promotions.urls')),
    path('selfservice/', include('selfservice.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)'''
    
    main_urls_path = BASE_DIR / 'ehr_system' / 'urls.py'
    with open(main_urls_path, 'w', encoding='utf-8') as f:
        f.write(main_urls_content)
    print(f"  ✓ 업데이트됨: ehr_system/urls.py")
    
    # job_profiles/urls.py 업데이트
    job_urls_content = '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 직무체계도 트리맵 뷰
    path('', views.JobTreeMapView.as_view(), name='list'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]'''
    
    job_urls_path = BASE_DIR / 'job_profiles' / 'urls.py'
    with open(job_urls_path, 'w', encoding='utf-8') as f:
        f.write(job_urls_content)
    print(f"  ✓ 업데이트됨: job_profiles/urls.py")
    
    # job_profiles/views.py 업데이트 (TreeMapView 추가)
    job_views_content = '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch
import json

from .models import JobCategory, JobType, JobRole, JobProfile


class JobTreeMapView(TemplateView):
    """직무체계도 트리맵 뷰"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터
        try:
            context['total_categories'] = JobCategory.objects.filter(is_active=True).count()
            context['total_job_types'] = JobType.objects.filter(is_active=True).count()
            context['total_job_roles'] = JobRole.objects.filter(is_active=True).count()
            context['total_profiles'] = JobProfile.objects.filter(is_active=True).count()
        except:
            # 모델이 없는 경우 기본값
            context['total_categories'] = 0
            context['total_job_types'] = 0
            context['total_job_roles'] = 0
            context['total_profiles'] = 0
        
        return context


def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    return JsonResponse({
        'success': True,
        'data': {'Non-PL': {}, 'PL': {}}
    })


def job_detail_modal_api(request, job_role_id):
    """직무 상세 정보 API"""
    return JsonResponse({
        'success': False,
        'error': 'Not implemented'
    })


def job_profile_edit_view(request, job_role_id):
    """직무기술서 편집 뷰"""
    return render(request, 'job_profiles/job_profile_edit.html', {})'''
    
    job_views_path = BASE_DIR / 'job_profiles' / 'views.py'
    with open(job_views_path, 'w', encoding='utf-8') as f:
        f.write(job_views_content)
    print(f"  ✓ 업데이트됨: job_profiles/views.py")

def main():
    print("="*60)
    print("누락된 파일 생성 및 레거시 파일 삭제")
    print("="*60)
    
    # 1. 레거시 파일 삭제
    delete_legacy_files()
    
    # 2. 누락된 템플릿 생성
    print("\n2. 누락된 템플릿 생성 중...")
    create_job_treemap_template()
    create_ehr_system_views()
    
    # 3. Static 파일 생성
    create_static_files()
    
    # 4. URL 업데이트
    update_urls()
    
    print("\n" + "="*60)
    print("완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. python manage.py collectstatic --noinput")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/ 접속")
    print("="*60)

if __name__ == '__main__':
    main()