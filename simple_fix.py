#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
간단한 해결책 - dashboard.html만 수정
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent

def fix_dashboard_only():
    """dashboard.html이 base_simple.html을 사용하도록 변경"""
    dashboard_path = BASE_DIR / 'templates' / 'dashboard.html'
    
    dashboard_content = '''{% extends "base_simple.html" %}
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
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    
    print("✓ dashboard.html이 base_simple.html을 사용하도록 변경됨")

def main():
    print("="*60)
    print("간단한 해결책 - Dashboard 템플릿만 수정")
    print("="*60)
    
    fix_dashboard_only()
    
    print("\n완료!")
    print("서버를 재시작하세요: python manage.py runserver")
    print("="*60)

if __name__ == '__main__':
    main()