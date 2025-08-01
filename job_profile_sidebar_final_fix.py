#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 HRIS 사이드바 메뉴 및 직무체계도 최종 정리
- 사이드바 최상단 메뉴를 '대시보드'로 변경
- '직무기술서' 메뉴명을 '직무체계도'로 변경
- 직무체계도는 트리맵 UI만 제공 (/job-profiles/)
- 모든 레거시 메뉴, URL, 코드 삭제
"""

import os
import re
import shutil
from datetime import datetime

# 베이스 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def update_base_simple_template():
    """base_simple.html 사이드바 메뉴 업데이트"""
    template_content = '''{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OK금융그룹 HRIS{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/design-system.css' %}">
    
    {% block extra_css %}{% endblock %}
    
    <style>
    /* 사이드바 스타일 */
    .sidebar {
        min-height: 100vh;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        width: 260px;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
        transition: all 0.3s;
    }
    
    .sidebar-header {
        padding: 20px;
        text-align: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-logo {
        font-size: 24px;
        font-weight: 700;
        color: white;
        text-decoration: none;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .sidebar-menu {
        padding: 20px 0;
    }
    
    .menu-item {
        padding: 0 20px;
        margin-bottom: 5px;
    }
    
    .menu-link {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        color: rgba(255, 255, 255, 0.9);
        text-decoration: none;
        border-radius: 8px;
        transition: all 0.3s;
        font-size: 15px;
    }
    
    .menu-link:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    .menu-link.active {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        font-weight: 600;
    }
    
    .menu-link i {
        width: 20px;
        text-align: center;
    }
    
    .main-content {
        margin-left: 260px;
        padding: 20px;
        min-height: 100vh;
        background: #f8f9fa;
    }
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .sidebar {
            transform: translateX(-100%);
        }
        
        .sidebar.active {
            transform: translateX(0);
        }
        
        .main-content {
            margin-left: 0;
        }
    }
    </style>
</head>
<body>
    <!-- 사이드바 -->
    <nav class="sidebar">
        <div class="sidebar-header">
            <a href="{% url 'home' %}" class="sidebar-logo">
                <i class="fas fa-building"></i>
                <span>OK금융그룹 HRIS</span>
            </a>
        </div>
        
        <div class="sidebar-menu">
            <!-- 대시보드 (최상단) -->
            <div class="menu-item">
                <a href="{% url 'home' %}" class="menu-link {% if request.resolver_match.url_name == 'home' %}active{% endif %}">
                    <i class="fas fa-dashboard"></i>
                    <span>대시보드</span>
                </a>
            </div>
            
            <!-- HR 관리 섹션 -->
            <div class="menu-section mt-4">
                <div class="menu-section-title px-4 text-uppercase text-muted small mb-2">
                    HR 관리
                </div>
                
                <!-- 직무체계도 (기존 직무기술서) -->
                <div class="menu-item">
                    <a href="{% url 'job_profiles:list' %}" class="menu-link {% if 'job_profiles' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-sitemap"></i>
                        <span>직무체계도</span>
                    </a>
                </div>
                
                <!-- 직원관리 -->
                <div class="menu-item">
                    <a href="{% url 'employees:list' %}" class="menu-link {% if 'employees' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-users"></i>
                        <span>직원관리</span>
                    </a>
                </div>
                
                <!-- 평가관리 -->
                <div class="menu-item">
                    <a href="{% url 'evaluations:dashboard' %}" class="menu-link {% if 'evaluations' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-chart-line"></i>
                        <span>평가관리</span>
                    </a>
                </div>
                
                <!-- 보상관리 -->
                <div class="menu-item">
                    <a href="{% url 'compensation:dashboard' %}" class="menu-link {% if 'compensation' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-coins"></i>
                        <span>보상관리</span>
                    </a>
                </div>
                
                <!-- 승진관리 -->
                <div class="menu-item">
                    <a href="{% url 'promotions:dashboard' %}" class="menu-link {% if 'promotions' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-award"></i>
                        <span>승진관리</span>
                    </a>
                </div>
            </div>
            
            <!-- 셀프서비스 섹션 -->
            <div class="menu-section mt-4">
                <div class="menu-section-title px-4 text-uppercase text-muted small mb-2">
                    셀프서비스
                </div>
                
                <!-- 내 정보 -->
                <div class="menu-item">
                    <a href="{% url 'selfservice:dashboard' %}" class="menu-link {% if 'selfservice' in request.resolver_match.url_name %}active{% endif %}">
                        <i class="fas fa-user-circle"></i>
                        <span>내 정보</span>
                    </a>
                </div>
            </div>
        </div>
    </nav>
    
    <!-- 메인 컨텐츠 -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    {% block extra_js %}{% endblock %}
    
    <script>
    // 모바일 사이드바 토글
    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.querySelector('.sidebar');
        const toggleBtn = document.querySelector('.sidebar-toggle');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                sidebar.classList.toggle('active');
            });
        }
    });
    </script>
</body>
</html>'''
    
    return template_content

def update_job_profiles_views():
    """job_profiles/views.py 최종 정리"""
    views_content = '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch
import json

from .models import JobCategory, JobType, JobRole, JobProfile

class JobTreeMapView(TemplateView):
    """직무체계도 트리맵 뷰 (유일한 뷰)"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터
        context['total_categories'] = JobCategory.objects.filter(is_active=True).count()
        context['total_job_types'] = JobType.objects.filter(is_active=True).count()
        context['total_job_roles'] = JobRole.objects.filter(is_active=True).count()
        context['total_profiles'] = JobProfile.objects.filter(is_active=True).count()
        
        return context

def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        # 카테고리 분류
        non_pl_categories = ['IT/디지털', '경영지원', '금융', '영업', '고객서비스']
        
        # 아이콘 매핑
        icon_map = {
            'IT/디지털': 'laptop',
            '경영지원': 'briefcase', 
            '금융': 'dollar-sign',
            '영업': 'users',
            '고객서비스': 'headphones',
            'PL': 'user-shield'
        }
        
        tree_data = {'Non-PL': {}, 'PL': {}}
        
        # 최적화된 쿼리로 데이터 조회
        categories = JobCategory.objects.prefetch_related(
            Prefetch('job_types', 
                queryset=JobType.objects.prefetch_related(
                    Prefetch('job_roles',
                        queryset=JobRole.objects.select_related('profile').filter(is_active=True)
                    )
                ).filter(is_active=True)
            )
        ).filter(is_active=True)
        
        for category in categories:
            category_data = {
                'name': category.name,
                'icon': icon_map.get(category.name, 'folder'),
                'jobs': {}
            }
            
            for job_type in category.job_types.all():
                jobs = []
                for job_role in job_type.job_roles.all():
                    jobs.append({
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': hasattr(job_role, 'profile') and job_role.profile.is_active
                    })
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # 카테고리 분류
            if category.name in non_pl_categories:
                tree_data['Non-PL'][category.name] = category_data
            else:
                tree_data['PL'][category.name] = category_data
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def job_detail_modal_api(request, job_role_id):
    """직무 상세 정보 모달 API"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
        
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
                'description': job_role.description,
                'full_path': f"{job_role.job_type.category.name} > {job_role.job_type.name} > {job_role.name}"
            }
        }
        
        # 프로필 정보
        if hasattr(job_role, 'profile') and job_role.profile.is_active:
            profile = job_role.profile
            data['profile'] = {
                'id': str(profile.id),
                'role_responsibility': profile.role_responsibility,
                'qualification': profile.qualification,
                'basic_skills': profile.basic_skills or [],
                'applied_skills': profile.applied_skills or [],
                'growth_path': profile.growth_path,
                'related_certifications': profile.related_certifications or []
            }
        else:
            data['profile'] = None
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def job_profile_edit_view(request, job_role_id):
    """직무기술서 편집 뷰"""
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    if request.method == 'GET':
        profile = getattr(job_role, 'profile', None)
        context = {
            'job': job_role,
            'profile': profile
        }
        return render(request, 'job_profiles/job_profile_edit.html', context)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            profile, created = JobProfile.objects.update_or_create(
                job_role=job_role,
                defaults={
                    'role_responsibility': data.get('role_responsibility', ''),
                    'qualification': data.get('qualification', ''),
                    'basic_skills': data.get('basic_skills', []),
                    'applied_skills': data.get('applied_skills', []),
                    'growth_path': data.get('growth_path', ''),
                    'related_certifications': data.get('related_certifications', []),
                    'is_active': True
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.',
                'profile_id': str(profile.id)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)'''
    
    return views_content

def update_job_profiles_urls():
    """job_profiles/urls.py 최종 정리"""
    urls_content = '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 직무체계도 트리맵 뷰 (메인)
    path('', views.JobTreeMapView.as_view(), name='list'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]'''
    
    return urls_content

def update_main_urls():
    """ehr_system/urls.py 업데이트"""
    urls_content = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import DashboardView

urlpatterns = [
    # 관리자
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
    
    return urls_content

def create_dashboard_view():
    """ehr_system/views.py - 대시보드 뷰"""
    views_content = '''from django.views.generic import TemplateView
from django.db.models import Count, Q
from datetime import datetime, timedelta

from employees.models import Employee
from job_profiles.models import JobRole, JobProfile
from evaluations.models import Evaluation
from compensation.models import Compensation


class DashboardView(TemplateView):
    """메인 대시보드 뷰"""
    template_name = 'dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 현재 날짜
        today = datetime.now().date()
        month_ago = today - timedelta(days=30)
        
        # 통계 데이터
        context['stats'] = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_departments': Employee.objects.filter(is_active=True).values('department').distinct().count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'completed_profiles': JobProfile.objects.filter(is_active=True).count(),
            'pending_evaluations': Evaluation.objects.filter(
                status='pending',
                created_at__gte=month_ago
            ).count(),
            'recent_hires': Employee.objects.filter(
                hire_date__gte=month_ago,
                is_active=True
            ).count(),
        }
        
        # 최근 활동
        context['recent_activities'] = []
        
        # 차트 데이터
        context['chart_data'] = self.get_chart_data()
        
        return context
    
    def get_chart_data(self):
        """대시보드 차트 데이터"""
        # 부서별 직원 수
        dept_data = Employee.objects.filter(is_active=True).values('department').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # 직급별 분포
        position_data = Employee.objects.filter(is_active=True).values('position').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'departments': list(dept_data),
            'positions': list(position_data)
        }'''
    
    return views_content

def create_dashboard_template():
    """templates/dashboard.html - 대시보드 템플릿"""
    template_content = '''{% extends "base_simple.html" %}
{% load static %}

{% block title %}대시보드 - OK금융그룹 HRIS{% endblock %}

{% block extra_css %}
<style>
.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 32px;
}

.page-title {
    font-size: 32px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 8px;
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
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    color: white;
    margin-bottom: 16px;
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 14px;
    color: #6c757d;
}

.stat-card:nth-child(1) .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card:nth-child(2) .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-card:nth-child(3) .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-card:nth-child(4) .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }
.stat-card:nth-child(5) .stat-icon { background: linear-gradient(135deg, #fa709a, #fee140); }
.stat-card:nth-child(6) .stat-icon { background: linear-gradient(135deg, #30cfd0, #330867); }

.quick-links {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 32px;
}

.quick-links-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #2c3e50;
}

.quick-links-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
}

.quick-link {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    text-decoration: none;
    color: #2c3e50;
    transition: all 0.3s;
}

.quick-link:hover {
    background: #e9ecef;
    transform: translateX(4px);
}

.quick-link i {
    font-size: 20px;
    color: #2e86de;
}
</style>
{% endblock %}

{% block content %}
<div class="dashboard-container">
    <!-- 페이지 헤더 -->
    <div class="page-header">
        <h1 class="page-title">
            <i class="fas fa-dashboard text-primary"></i>
            대시보드
        </h1>
        <p class="text-muted">OK금융그룹 인사관리시스템에 오신 것을 환영합니다</p>
    </div>
    
    <!-- 통계 카드 -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-users"></i>
            </div>
            <div class="stat-value">{{ stats.total_employees|default:"0" }}</div>
            <div class="stat-label">전체 직원</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-building"></i>
            </div>
            <div class="stat-value">{{ stats.total_departments|default:"0" }}</div>
            <div class="stat-label">부서</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
            </div>
            <div class="stat-value">{{ stats.total_job_roles|default:"0" }}</div>
            <div class="stat-label">직무</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="stat-value">{{ stats.completed_profiles|default:"0" }}</div>
            <div class="stat-label">직무기술서</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="stat-value">{{ stats.pending_evaluations|default:"0" }}</div>
            <div class="stat-label">진행중 평가</div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-user-plus"></i>
            </div>
            <div class="stat-value">{{ stats.recent_hires|default:"0" }}</div>
            <div class="stat-label">신규 입사자</div>
        </div>
    </div>
    
    <!-- 빠른 링크 -->
    <div class="quick-links">
        <h2 class="quick-links-title">빠른 메뉴</h2>
        <div class="quick-links-grid">
            <a href="{% url 'job_profiles:list' %}" class="quick-link">
                <i class="fas fa-sitemap"></i>
                <span>직무체계도 보기</span>
            </a>
            <a href="{% url 'employees:list' %}" class="quick-link">
                <i class="fas fa-users"></i>
                <span>직원 목록</span>
            </a>
            <a href="{% url 'evaluations:dashboard' %}" class="quick-link">
                <i class="fas fa-chart-line"></i>
                <span>평가 관리</span>
            </a>
            <a href="{% url 'compensation:dashboard' %}" class="quick-link">
                <i class="fas fa-coins"></i>
                <span>보상 관리</span>
            </a>
            <a href="{% url 'promotions:dashboard' %}" class="quick-link">
                <i class="fas fa-award"></i>
                <span>승진 관리</span>
            </a>
            <a href="{% url 'selfservice:dashboard' %}" class="quick-link">
                <i class="fas fa-user-circle"></i>
                <span>내 정보</span>
            </a>
        </div>
    </div>
</div>
{% endblock %}'''
    
    return template_content

def delete_legacy_files():
    """레거시 파일 삭제 목록"""
    files_to_delete = [
        # 레거시 템플릿
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_tree_map_simple.html',
        'job_profiles/templates/job_profiles/job_profile_list.html',
        'job_profiles/templates/job_profiles/job_profile_detail.html',
        'job_profiles/templates/job_profiles/job_profile_admin.html',
        
        # 레거시 static 파일
        'static/js/JobProfileTreeMap.js',
        'static/css/JobProfileTreeMap.css',
        'static/js/job_tree_unified.js',
        'static/css/job_tree_unified.css',
        
        # 레거시 뷰 파일
        'job_profiles/views_old.py',
        'job_profiles/views_legacy.py',
        'job_profiles/urls_old.py',
        'job_profiles/urls_legacy.py',
    ]
    
    return files_to_delete

def main():
    print("="*70)
    print("OK금융그룹 HRIS 사이드바 메뉴 및 직무체계도 최종 정리")
    print("="*70)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*70)
    
    # 백업 디렉토리
    backup_dir = os.path.join(BASE_DIR, f'backup_sidebar_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. 기존 파일 백업
    print("\n1. 기존 파일 백업 중...")
    files_to_backup = [
        'templates/base_simple.html',
        'templates/dashboard.html',
        'job_profiles/views.py',
        'job_profiles/urls.py',
        'ehr_system/urls.py',
        'ehr_system/views.py',
    ]
    
    for file_path in files_to_backup:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            backup_path = os.path.join(backup_dir, file_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(full_path, backup_path)
            print(f"  백업: {file_path}")
    
    # 2. 새 파일 생성/업데이트
    print("\n2. 파일 업데이트 중...")
    
    # base_simple.html 업데이트
    base_template_path = os.path.join(BASE_DIR, 'templates/base_simple.html')
    os.makedirs(os.path.dirname(base_template_path), exist_ok=True)
    with open(base_template_path, 'w', encoding='utf-8') as f:
        f.write(update_base_simple_template())
    print("  업데이트: templates/base_simple.html")
    
    # dashboard.html 생성
    dashboard_template_path = os.path.join(BASE_DIR, 'templates/dashboard.html')
    with open(dashboard_template_path, 'w', encoding='utf-8') as f:
        f.write(create_dashboard_template())
    print("  생성: templates/dashboard.html")
    
    # job_profiles/views.py 업데이트
    views_path = os.path.join(BASE_DIR, 'job_profiles/views.py')
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(update_job_profiles_views())
    print("  업데이트: job_profiles/views.py")
    
    # job_profiles/urls.py 업데이트
    urls_path = os.path.join(BASE_DIR, 'job_profiles/urls.py')
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(update_job_profiles_urls())
    print("  업데이트: job_profiles/urls.py")
    
    # ehr_system/urls.py 업데이트
    main_urls_path = os.path.join(BASE_DIR, 'ehr_system/urls.py')
    with open(main_urls_path, 'w', encoding='utf-8') as f:
        f.write(update_main_urls())
    print("  업데이트: ehr_system/urls.py")
    
    # ehr_system/views.py 생성/업데이트
    main_views_path = os.path.join(BASE_DIR, 'ehr_system/views.py')
    with open(main_views_path, 'w', encoding='utf-8') as f:
        f.write(create_dashboard_view())
    print("  생성: ehr_system/views.py")
    
    # 3. 레거시 파일 삭제
    print("\n3. 레거시 파일 삭제 중...")
    for file_path in delete_legacy_files():
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"  삭제: {file_path}")
    
    print("\n" + "="*70)
    print("완료! 변경 사항:")
    print("="*70)
    print("✅ 사이드바 최상단 메뉴가 '대시보드'로 변경됨")
    print("✅ '직무기술서' 메뉴가 '직무체계도'로 변경됨")
    print("✅ 직무체계도는 트리맵 UI만 제공 (/job-profiles/)")
    print("✅ 모든 레거시 뷰와 템플릿 삭제됨")
    print("✅ UI 일관성 유지")
    print("-"*70)
    print("\n다음 단계:")
    print("1. python manage.py collectstatic --noinput")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/ 접속하여 대시보드 확인")
    print("4. 사이드바에서 '직무체계도' 클릭하여 트리맵 UI 확인")
    print("-"*70)
    print(f"백업 위치: {backup_dir}")
    print("="*70)

if __name__ == '__main__':
    main()