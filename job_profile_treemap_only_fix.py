#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK Financial Group HRIS - Job Profile Tree Map Only Unification
==============================================================

1. 기존 트리뷰/그리드뷰/리스트뷰 완전 제거
2. 트리맵 UI로 단일화
3. 상단 통계 디자인 일치
4. 카드 클릭시 팝업 상세
5. 메뉴/URL 정비

Author: HR Information Design + UI/UX Consistency Expert + React/Django Frontend Developer
Date: 2025-01-27
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class JobProfileTreeMapOnlyFix:
    """직무 프로필 트리맵 단일화 시스템"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # OK금융그룹 통일 컬러 시스템
        self.color_scheme = {
            "primary": {
                "IT/디지털": "#3B82F6",
                "경영지원": "#8B5CF6",
                "금융": "#10B981",
                "영업": "#F59E0B", 
                "고객서비스": "#EF4444"
            },
            "gradient": {
                "IT/디지털": "linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)",
                "경영지원": "linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)",
                "금융": "linear-gradient(135deg, #10B981 0%, #34D399 100%)",
                "영업": "linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)",
                "고객서비스": "linear-gradient(135deg, #EF4444 0%, #F87171 100%)"
            },
            "neutral": {
                "50": "#f8fafc",
                "100": "#f1f5f9",
                "200": "#e5e7eb",
                "300": "#d1d5db",
                "400": "#9ca3af",
                "500": "#6b7280",
                "600": "#4b5563",
                "700": "#374151",
                "800": "#1f2937",
                "900": "#111827"
            }
        }
        
    def generate_all(self):
        """모든 파일 생성 및 정리"""
        print("OK금융그룹 직무 프로필 트리맵 단일화 시작...\n")
        
        # 1. 통합 트리맵 템플릿 생성
        self._generate_unified_treemap_template()
        
        # 2. 통합 스타일시트 생성
        self._generate_unified_styles()
        
        # 3. 통합 JavaScript 생성
        self._generate_unified_javascript()
        
        # 4. 단순화된 뷰 생성
        self._generate_simplified_views()
        
        # 5. URL 패턴 정리
        self._generate_cleaned_urls()
        
        # 6. 베이스 템플릿 개선
        self._generate_improved_base_template()
        
        # 7. 삭제할 파일 목록
        self._generate_deletion_script()
        
        print("\n[완료] 모든 파일 생성 완료!")
        print(f"[정보] 생성된 디렉토리: job_profile_treemap_only_fix/")
        
    def _generate_unified_treemap_template(self):
        """통합 트리맵 템플릿 생성"""
        template_content = '''{% extends "base_unified.html" %}
{% load static %}

{% block title %}직무 체계도 - OK금융그룹{% endblock %}

{% block page_header %}
<!-- 페이지 헤더 (베이스 템플릿에서 처리) -->
{% endblock %}

{% block content %}
<div class="treemap-page">
    <!-- 상단 통계 카드 (트리맵과 동일한 스타일) -->
    <div class="stats-container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon" style="background: {{ gradient_it }}">
                    <i class="fas fa-sitemap"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">{{ total_categories }}</div>
                    <div class="stat-label">직군</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon" style="background: {{ gradient_management }}">
                    <i class="fas fa-layer-group"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">{{ total_job_types }}</div>
                    <div class="stat-label">직종</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon" style="background: {{ gradient_finance }}">
                    <i class="fas fa-briefcase"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">{{ total_job_roles }}</div>
                    <div class="stat-label">직무</div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon" style="background: {{ gradient_sales }}">
                    <i class="fas fa-file-alt"></i>
                </div>
                <div class="stat-content">
                    <div class="stat-value">{{ total_profiles }}</div>
                    <div class="stat-label">직무기술서</div>
                </div>
            </div>
        </div>
    </div>

    <!-- 검색 및 필터 바 -->
    <div class="control-bar">
        <div class="search-container">
            <i class="fas fa-search"></i>
            <input type="text" 
                   id="jobSearch" 
                   class="search-input" 
                   placeholder="직무명으로 검색..."
                   autocomplete="off">
        </div>
        
        <div class="filter-container">
            <button class="filter-chip active" data-filter="all">
                전체
                <span class="chip-count">{{ total_job_roles }}</span>
            </button>
            <button class="filter-chip" data-filter="with-profile">
                <i class="fas fa-check-circle"></i>
                기술서 있음
                <span class="chip-count">{{ total_profiles }}</span>
            </button>
            <button class="filter-chip" data-filter="no-profile">
                <i class="fas fa-times-circle"></i>
                기술서 없음
                <span class="chip-count">{{ jobs_without_profile }}</span>
            </button>
        </div>
    </div>

    <!-- 트리맵 메인 영역 -->
    <div class="treemap-container">
        <!-- Non-PL 직군 -->
        <section class="group-section non-pl">
            <div class="group-header">
                <div class="group-badge">Non-PL</div>
                <h2 class="group-title">일반 직군</h2>
                <span class="group-count" id="non-pl-count">0개 직무</span>
            </div>
            
            <div id="non-pl-content" class="group-content">
                <div class="loading-skeleton">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </section>

        <!-- PL 직군 -->
        <section class="group-section pl">
            <div class="group-header">
                <div class="group-badge">PL</div>
                <h2 class="group-title">고객서비스 직군</h2>
                <span class="group-count" id="pl-count">0개 직무</span>
            </div>
            
            <div id="pl-content" class="group-content">
                <div class="loading-skeleton">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </section>
    </div>
</div>

<!-- 직무 상세 모달 -->
<div id="jobDetailModal" class="modal-backdrop" style="display: none;">
    <div class="modal-container">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title-wrapper">
                    <h2 id="modalJobTitle" class="modal-title"></h2>
                    <p id="modalJobPath" class="modal-subtitle"></p>
                </div>
                <button class="modal-close" onclick="closeJobModal()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            
            <div id="modalJobContent" class="modal-body">
                <!-- 동적 컨텐츠 -->
            </div>
            
            <div class="modal-footer">
                <button class="btn btn-primary" id="editJobBtn" style="display: none;">
                    <i class="fas fa-edit"></i>
                    편집
                </button>
                <button class="btn btn-secondary" onclick="closeJobModal()">
                    닫기
                </button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="stylesheet" href="{% static 'css/job_treemap_unified.css' %}">
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/job_treemap_unified.js' %}"></script>
{% endblock %}'''

        # 파일 저장
        os.makedirs("job_profile_treemap_only_fix/templates/job_profiles", exist_ok=True)
        
        with open("job_profile_treemap_only_fix/templates/job_profiles/job_treemap.html", "w", encoding="utf-8") as f:
            f.write(template_content)
            
        print("[완료] 통합 트리맵 템플릿 생성")

    def _generate_unified_styles(self):
        """통합 스타일시트 생성"""
        
        css_content = '''/* OK Financial Group - Job Tree Map Unified Styles */

/* CSS 변수 정의 */
:root {
    /* 브랜드 컬러 */
    --color-it: #3B82F6;
    --color-management: #8B5CF6;
    --color-finance: #10B981;
    --color-sales: #F59E0B;
    --color-service: #EF4444;
    
    /* 그라디언트 */
    --gradient-it: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
    --gradient-management: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
    --gradient-finance: linear-gradient(135deg, #10B981 0%, #34D399 100%);
    --gradient-sales: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
    --gradient-service: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
    
    /* 중립 컬러 */
    --neutral-50: #f8fafc;
    --neutral-100: #f1f5f9;
    --neutral-200: #e5e7eb;
    --neutral-300: #d1d5db;
    --neutral-400: #9ca3af;
    --neutral-500: #6b7280;
    --neutral-600: #4b5563;
    --neutral-700: #374151;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
    
    /* 여백 */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    
    /* 둥글기 */
    --radius-sm: 0.5rem;
    --radius-md: 0.75rem;
    --radius-lg: 1rem;
    --radius-xl: 1.25rem;
    --radius-2xl: 1.5rem;
    
    /* 그림자 */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

/* 페이지 컨테이너 */
.treemap-page {
    padding: var(--spacing-xl);
    background: var(--neutral-50);
    min-height: 100vh;
}

/* 상단 통계 컨테이너 */
.stats-container {
    margin-bottom: var(--spacing-2xl);
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
}

.stat-card {
    background: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    transition: all 0.3s ease;
    border: 1px solid var(--neutral-200);
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    border-color: var(--neutral-300);
}

.stat-icon {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    flex-shrink: 0;
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--neutral-900);
    line-height: 1;
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--neutral-500);
    font-weight: 500;
}

/* 컨트롤 바 */
.control-bar {
    background: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    flex-wrap: wrap;
    border: 1px solid var(--neutral-200);
}

.search-container {
    flex: 1;
    min-width: 300px;
    position: relative;
}

.search-container i {
    position: absolute;
    left: var(--spacing-md);
    top: 50%;
    transform: translateY(-50%);
    color: var(--neutral-400);
}

.search-input {
    width: 100%;
    padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) var(--spacing-2xl);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    transition: all 0.2s ease;
}

.search-input:focus {
    outline: none;
    border-color: var(--color-it);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-container {
    display: flex;
    gap: var(--spacing-sm);
}

.filter-chip {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-2xl);
    background: white;
    color: var(--neutral-600);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.filter-chip:hover {
    border-color: var(--color-it);
    color: var(--color-it);
    background: var(--neutral-50);
}

.filter-chip.active {
    background: var(--color-it);
    border-color: var(--color-it);
    color: white;
}

.chip-count {
    background: rgba(255, 255, 255, 0.2);
    padding: 2px 8px;
    border-radius: var(--radius-md);
    font-size: 0.75rem;
}

.filter-chip.active .chip-count {
    background: rgba(255, 255, 255, 0.3);
}

/* 트리맵 컨테이너 */
.treemap-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-xl);
}

/* 그룹 섹션 */
.group-section {
    background: white;
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
    border: 2px solid;
    transition: all 0.3s ease;
}

.group-section.non-pl {
    border-color: var(--color-it);
    border-opacity: 0.3;
}

.group-section.pl {
    border-color: var(--color-service);
    border-opacity: 0.3;
}

.group-header {
    padding: var(--spacing-xl);
    background: var(--neutral-50);
    border-bottom: 1px solid var(--neutral-200);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.group-badge {
    padding: var(--spacing-xs) var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.non-pl .group-badge {
    background: var(--gradient-it);
    color: white;
}

.pl .group-badge {
    background: var(--gradient-service);
    color: white;
}

.group-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--neutral-900);
    flex: 1;
}

.group-count {
    font-size: 0.875rem;
    color: var(--neutral-500);
}

.group-content {
    padding: var(--spacing-xl);
    min-height: 400px;
}

/* 카테고리 섹션 */
.category-section {
    margin-bottom: var(--spacing-2xl);
    padding: var(--spacing-lg);
    background: var(--neutral-50);
    border-radius: var(--radius-lg);
    border: 1px solid var(--neutral-200);
}

.category-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.category-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
    flex-shrink: 0;
}

.category-info {
    flex: 1;
}

.category-name {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-xs);
}

.category-stats {
    font-size: 0.875rem;
    color: var(--neutral-500);
}

/* 직종 섹션 */
.job-type-section {
    margin-bottom: var(--spacing-lg);
}

.job-type-header {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: var(--spacing-md);
    padding-left: var(--spacing-md);
    border-left: 4px solid;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.job-type-count {
    font-size: 0.75rem;
    font-weight: 500;
    padding: 2px 8px;
    background: white;
    border-radius: var(--radius-sm);
}

/* 직무 그리드 */
.jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: var(--spacing-md);
    padding-left: var(--spacing-lg);
}

/* 직무 카드 */
.job-card {
    background: white;
    border: 2px solid var(--neutral-200);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.job-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--card-color, var(--neutral-300));
    transition: height 0.3s ease;
}

.job-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--card-color, var(--neutral-300));
}

.job-card:hover::before {
    height: 8px;
}

.job-card.has-profile {
    border-color: var(--card-color);
}

.job-card.no-profile {
    opacity: 0.8;
}

.job-card-icon {
    font-size: 28px;
    margin-bottom: var(--spacing-sm);
    color: var(--card-color);
}

.job-card-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--neutral-800);
    margin-bottom: var(--spacing-xs);
    line-height: 1.4;
}

.job-card-status {
    font-size: 0.75rem;
    color: var(--neutral-500);
}

.job-card.has-profile .job-card-status {
    color: var(--color-finance);
    font-weight: 500;
}

/* 로딩 스켈레톤 */
.loading-skeleton {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    color: var(--neutral-400);
}

.loading-skeleton i {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
}

/* 모달 */
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl);
    animation: fadeIn 0.2s ease;
}

.modal-container {
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    display: flex;
}

.modal-content {
    background: white;
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-xl);
    width: 100%;
    display: flex;
    flex-direction: column;
    animation: slideIn 0.3s ease;
}

.modal-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--neutral-200);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--spacing-lg);
}

.modal-title-wrapper {
    flex: 1;
}

.modal-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-xs);
}

.modal-subtitle {
    font-size: 0.875rem;
    color: var(--neutral-500);
}

.modal-close {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--neutral-100);
    border-radius: var(--radius-lg);
    color: var(--neutral-600);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.modal-close:hover {
    background: var(--neutral-200);
    color: var(--neutral-800);
}

.modal-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-xl);
}

.modal-footer {
    padding: var(--spacing-xl);
    border-top: 1px solid var(--neutral-200);
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
}

/* 버튼 */
.btn {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--radius-lg);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.btn-primary {
    background: var(--color-it);
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

.btn-secondary {
    background: var(--neutral-200);
    color: var(--neutral-700);
}

.btn-secondary:hover {
    background: var(--neutral-300);
}

/* 애니메이션 */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 반응형 */
@media (max-width: 1024px) {
    .treemap-container {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 640px) {
    .treemap-page {
        padding: var(--spacing-md);
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .control-bar {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-container {
        min-width: 100%;
    }
    
    .filter-container {
        width: 100%;
        justify-content: space-between;
    }
    
    .jobs-grid {
        grid-template-columns: 1fr;
        padding-left: 0;
    }
    
    .modal-container {
        padding: var(--spacing-md);
    }
}

/* 프린트 */
@media print {
    .control-bar,
    .modal-backdrop {
        display: none !important;
    }
    
    .treemap-page {
        background: white;
        padding: 0;
    }
    
    .job-card {
        break-inside: avoid;
    }
}'''

        os.makedirs("job_profile_treemap_only_fix/static/css", exist_ok=True)
        
        with open("job_profile_treemap_only_fix/static/css/job_treemap_unified.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        print("[완료] 통합 스타일시트 생성")

    def _generate_unified_javascript(self):
        """통합 JavaScript 생성"""
        
        js_content = '''// Job Tree Map Unified JavaScript

// 전역 변수
let treeData = {};
let currentFilter = 'all';
let currentJobId = null;

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    loadTreeMapData();
    initializeEventListeners();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 검색
    const searchInput = document.getElementById('jobSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
    
    // 필터
    document.querySelectorAll('.filter-chip').forEach(chip => {
        chip.addEventListener('click', handleFilter);
    });
    
    // 모달 외부 클릭
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeJobModal();
            }
        });
    }
    
    // ESC 키
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeJobModal();
        }
    });
}

// 트리맵 데이터 로드
async function loadTreeMapData() {
    try {
        const response = await fetch('/job-profiles/api/tree-map-data/', {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        const result = await response.json();
        
        if (result.success) {
            treeData = result.data;
            renderTreeMap(result.data);
            updateStatistics(result.statistics);
        } else {
            throw new Error(result.error || '알 수 없는 오류');
        }
    } catch (error) {
        console.error('Error loading tree map data:', error);
        showError('데이터를 불러올 수 없습니다.');
    }
}

// 트리맵 렌더링
function renderTreeMap(data) {
    // Non-PL 렌더링
    const nonPlContent = document.getElementById('non-pl-content');
    if (nonPlContent) {
        nonPlContent.innerHTML = renderGroup(data['Non-PL'] || {}, 'Non-PL');
    }
    
    // PL 렌더링
    const plContent = document.getElementById('pl-content');
    if (plContent) {
        plContent.innerHTML = renderGroup(data['PL'] || {}, 'PL');
    }
    
    // 카운트 업데이트
    updateGroupCounts();
    
    // 애니메이션 적용
    animateCards();
}

// 그룹 렌더링
function renderGroup(groupData, groupType) {
    if (!groupData || Object.keys(groupData).length === 0) {
        return '<div class="empty-message">데이터가 없습니다.</div>';
    }
    
    let html = '';
    
    for (const [categoryName, categoryData] of Object.entries(groupData)) {
        html += `
            <div class="category-section" data-category="${categoryName}">
                <div class="category-header">
                    <div class="category-icon" style="background: ${getCategoryGradient(categoryName)}">
                        <i class="fas ${getCategoryIcon(categoryData.icon)}"></i>
                    </div>
                    <div class="category-info">
                        <div class="category-name">${categoryName}</div>
                        <div class="category-stats">
                            ${Object.keys(categoryData.jobs || {}).length}개 직종 · 
                            ${countTotalJobs(categoryData.jobs)}개 직무
                        </div>
                    </div>
                </div>
                
                <div class="job-types-wrapper">
                    ${renderJobTypes(categoryData.jobs || {}, categoryName)}
                </div>
            </div>
        `;
    }
    
    return html;
}

// 직종별 직무 렌더링
function renderJobTypes(jobTypes, categoryName) {
    if (!jobTypes || Object.keys(jobTypes).length === 0) {
        return '';
    }
    
    let html = '';
    const categoryColor = getCategoryColor(categoryName);
    
    for (const [jobTypeName, jobs] of Object.entries(jobTypes)) {
        html += `
            <div class="job-type-section">
                <h4 class="job-type-header" style="border-color: ${categoryColor}">
                    ${jobTypeName}
                    <span class="job-type-count">${jobs.length}</span>
                </h4>
                <div class="jobs-grid">
                    ${jobs.map(job => renderJobCard(job, categoryName)).join('')}
                </div>
            </div>
        `;
    }
    
    return html;
}

// 직무 카드 렌더링
function renderJobCard(job, categoryName) {
    const hasProfile = job.has_profile;
    const cardClass = hasProfile ? 'has-profile' : 'no-profile';
    const color = getCategoryColor(categoryName);
    
    return `
        <div class="job-card ${cardClass}" 
             data-job-id="${job.id}"
             data-has-profile="${hasProfile}"
             data-category="${categoryName}"
             onclick="showJobDetail('${job.id}')"
             style="--card-color: ${color}">
            <div class="job-card-icon">
                <i class="fas ${hasProfile ? 'fa-file-alt' : 'fa-file'}"></i>
            </div>
            <div class="job-card-name">${job.name}</div>
            <div class="job-card-status">
                ${hasProfile ? '✓ 작성완료' : '미작성'}
            </div>
        </div>
    `;
}

// 직무 상세 표시
async function showJobDetail(jobId) {
    currentJobId = jobId;
    
    try {
        const response = await fetch(`/job-profiles/api/job-detail/${jobId}/`, {
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error('상세 정보 로드 실패');
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayJobDetail(result.data);
        } else {
            throw new Error(result.error || '알 수 없는 오류');
        }
    } catch (error) {
        console.error('Error loading job detail:', error);
        alert('직무 정보를 불러올 수 없습니다.');
    }
}

// 직무 상세 정보 표시
function displayJobDetail(data) {
    const { job, profile } = data;
    
    // 모달 제목 설정
    document.getElementById('modalJobTitle').textContent = job.name;
    document.getElementById('modalJobPath').textContent = job.full_path || `${job.category} > ${job.job_type} > ${job.name}`;
    
    // 편집 버튼 표시
    const editBtn = document.getElementById('editJobBtn');
    if (editBtn) {
        editBtn.style.display = profile ? 'inline-flex' : 'none';
        editBtn.onclick = () => {
            window.location.href = `/job-profiles/${job.id}/edit/`;
        };
    }
    
    // 상세 내용 HTML
    let contentHTML = `
        <div class="job-detail-wrapper">
            <!-- 기본 정보 -->
            <section class="detail-section">
                <h3 class="section-title">
                    <i class="fas fa-info-circle"></i>
                    기본 정보
                </h3>
                <div class="info-grid">
                    <div class="info-item">
                        <label>직군</label>
                        <span>${job.category}</span>
                    </div>
                    <div class="info-item">
                        <label>직종</label>
                        <span>${job.job_type}</span>
                    </div>
                    <div class="info-item">
                        <label>직무명</label>
                        <span>${job.name}</span>
                    </div>
                    <div class="info-item">
                        <label>상태</label>
                        <span class="${profile ? 'text-success' : 'text-muted'}">
                            ${profile ? '기술서 작성완료' : '기술서 미작성'}
                        </span>
                    </div>
                </div>
            </section>
    `;
    
    if (profile) {
        contentHTML += `
            <!-- 역할 및 책임 -->
            <section class="detail-section">
                <h3 class="section-title">
                    <i class="fas fa-tasks"></i>
                    핵심 역할 및 책임
                </h3>
                <div class="content-box">
                    ${formatTextToHTML(profile.role_responsibility)}
                </div>
            </section>
            
            <!-- 자격 요건 -->
            <section class="detail-section">
                <h3 class="section-title">
                    <i class="fas fa-check-circle"></i>
                    자격 요건
                </h3>
                <div class="content-box">
                    ${formatTextToHTML(profile.qualification)}
                </div>
            </section>
            
            <!-- 역량 -->
            <section class="detail-section">
                <h3 class="section-title">
                    <i class="fas fa-star"></i>
                    필요 역량
                </h3>
                <div class="skills-grid">
                    <div class="skill-group">
                        <h4>기본 역량</h4>
                        <div class="skill-tags">
                            ${profile.basic_skills.map(skill => 
                                `<span class="skill-tag basic">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="skill-group">
                        <h4>우대 역량</h4>
                        <div class="skill-tags">
                            ${profile.applied_skills.map(skill => 
                                `<span class="skill-tag preferred">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            </section>
        `;
        
        if (profile.growth_path) {
            contentHTML += `
                <!-- 성장 경로 -->
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-route"></i>
                        성장 경로
                    </h3>
                    <div class="content-box">
                        ${formatTextToHTML(profile.growth_path)}
                    </div>
                </section>
            `;
        }
        
        if (profile.related_certifications && profile.related_certifications.length > 0) {
            contentHTML += `
                <!-- 관련 자격증 -->
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-certificate"></i>
                        관련 자격증
                    </h3>
                    <div class="skill-tags">
                        ${profile.related_certifications.map(cert => 
                            `<span class="skill-tag cert">${cert}</span>`
                        ).join('')}
                    </div>
                </section>
            `;
        }
    } else {
        contentHTML += `
            <div class="empty-profile">
                <i class="fas fa-file-circle-plus"></i>
                <p>아직 작성된 직무기술서가 없습니다.</p>
                <button class="btn btn-primary" onclick="createJobProfile('${job.id}')">
                    <i class="fas fa-plus"></i>
                    직무기술서 작성
                </button>
            </div>
        `;
    }
    
    contentHTML += '</div>';
    
    // 내용 설정
    document.getElementById('modalJobContent').innerHTML = contentHTML;
    
    // 모달 표시
    openJobModal();
}

// 모달 열기
function openJobModal() {
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

// 모달 닫기
function closeJobModal() {
    const modal = document.getElementById('jobDetailModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
        currentJobId = null;
    }
}

// 직무기술서 생성
function createJobProfile(jobId) {
    window.location.href = `/job-profiles/create/?job_role=${jobId}`;
}

// 검색 처리
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    document.querySelectorAll('.job-card').forEach(card => {
        const jobName = card.querySelector('.job-card-name').textContent.toLowerCase();
        const shouldShow = jobName.includes(searchTerm);
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 섹션 숨기기
    updateEmptySections();
    updateGroupCounts();
}

// 필터 처리
function handleFilter(e) {
    const chip = e.target.closest('.filter-chip');
    if (!chip) return;
    
    currentFilter = chip.dataset.filter;
    
    // 활성 칩 변경
    document.querySelectorAll('.filter-chip').forEach(c => {
        c.classList.remove('active');
    });
    chip.classList.add('active');
    
    // 필터 적용
    document.querySelectorAll('.job-card').forEach(card => {
        const hasProfile = card.dataset.hasProfile === 'true';
        let shouldShow = true;
        
        if (currentFilter === 'with-profile') {
            shouldShow = hasProfile;
        } else if (currentFilter === 'no-profile') {
            shouldShow = !hasProfile;
        }
        
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 섹션 처리
    updateEmptySections();
    updateGroupCounts();
}

// 빈 섹션 업데이트
function updateEmptySections() {
    // 직종 섹션
    document.querySelectorAll('.job-type-section').forEach(section => {
        const visibleCards = section.querySelectorAll('.job-card:not([style*="display: none"])');
        section.style.display = visibleCards.length > 0 ? '' : 'none';
    });
    
    // 카테고리 섹션
    document.querySelectorAll('.category-section').forEach(section => {
        const visibleTypes = section.querySelectorAll('.job-type-section:not([style*="display: none"])');
        section.style.display = visibleTypes.length > 0 ? '' : 'none';
    });
}

// 그룹 카운트 업데이트
function updateGroupCounts() {
    // Non-PL 카운트
    const nonPlCards = document.querySelectorAll('#non-pl-content .job-card:not([style*="display: none"])');
    const nonPlCount = document.getElementById('non-pl-count');
    if (nonPlCount) {
        nonPlCount.textContent = `${nonPlCards.length}개 직무`;
    }
    
    // PL 카운트
    const plCards = document.querySelectorAll('#pl-content .job-card:not([style*="display: none"])');
    const plCount = document.getElementById('pl-count');
    if (plCount) {
        plCount.textContent = `${plCards.length}개 직무`;
    }
}

// 통계 업데이트
function updateStatistics(stats) {
    if (!stats) return;
    
    // 전체 통계
    const totalStats = {
        categories: (stats['Non-PL']?.categories || 0) + (stats['PL']?.categories || 0),
        jobTypes: (stats['Non-PL']?.job_types || 0) + (stats['PL']?.job_types || 0),
        jobs: (stats['Non-PL']?.jobs || 0) + (stats['PL']?.jobs || 0)
    };
    
    // 칩 카운트 업데이트
    const allChip = document.querySelector('[data-filter="all"] .chip-count');
    if (allChip) {
        allChip.textContent = totalStats.jobs;
    }
}

// 카드 애니메이션
function animateCards() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.3s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 50);
                
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.job-card').forEach(card => {
        observer.observe(card);
    });
}

// 유틸리티 함수들
function getCategoryColor(category) {
    const colors = {
        'IT/디지털': '#3B82F6',
        '경영지원': '#8B5CF6',
        '금융': '#10B981',
        '영업': '#F59E0B',
        '고객서비스': '#EF4444'
    };
    return colors[category] || '#6B7280';
}

function getCategoryGradient(category) {
    const gradients = {
        'IT/디지털': 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
        '경영지원': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
        '금융': 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
        '영업': 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)',
        '고객서비스': 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)'
    };
    return gradients[category] || 'linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%)';
}

function getCategoryIcon(iconName) {
    const iconMap = {
        'laptop': 'fa-laptop',
        'briefcase': 'fa-briefcase',
        'dollar-sign': 'fa-dollar-sign',
        'users': 'fa-users',
        'headphones': 'fa-headphones'
    };
    return iconMap[iconName] || 'fa-folder';
}

function countTotalJobs(jobTypes) {
    if (!jobTypes) return 0;
    return Object.values(jobTypes).reduce((total, jobs) => total + jobs.length, 0);
}

function formatTextToHTML(text) {
    if (!text) return '';
    return text.split('\\n').map(line => `<p>${line}</p>`).join('');
}

function showError(message) {
    const nonPlContent = document.getElementById('non-pl-content');
    const plContent = document.getElementById('pl-content');
    
    const errorHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <button class="btn btn-primary" onclick="location.reload()">
                <i class="fas fa-redo"></i>
                다시 시도
            </button>
        </div>
    `;
    
    if (nonPlContent) nonPlContent.innerHTML = errorHTML;
    if (plContent) plContent.innerHTML = '';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}'''

        os.makedirs("job_profile_treemap_only_fix/static/js", exist_ok=True)
        
        with open("job_profile_treemap_only_fix/static/js/job_treemap_unified.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        print("[완료] 통합 JavaScript 생성")

    def _generate_simplified_views(self):
        """단순화된 뷰 생성"""
        
        views_content = '''from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.db.models import Count, Prefetch, Q
from job_profiles.models import JobCategory, JobType, JobRole, JobProfile


class JobTreeMapView(TemplateView):
    """직무 트리맵 뷰 (단일 뷰)"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
            'jobs_without_profile': JobRole.objects.filter(
                is_active=True,
                profile__isnull=True
            ).count(),
            
            # 그라디언트 색상
            'gradient_it': 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
            'gradient_management': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
            'gradient_finance': 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
            'gradient_sales': 'linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%)',
        })
        
        return context


def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        # Non-PL, PL 분류를 위한 데이터 구조
        tree_data = {
            'Non-PL': {},
            'PL': {}
        }
        
        # PL 직군 정의
        pl_categories = ['고객서비스']
        
        # 모든 카테고리 조회
        categories = JobCategory.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'job_types',
                queryset=JobType.objects.filter(is_active=True).prefetch_related(
                    Prefetch(
                        'job_roles',
                        queryset=JobRole.objects.filter(is_active=True).select_related('profile')
                    )
                )
            )
        )
        
        # 색상 및 아이콘 매핑
        category_meta = {
            'IT/디지털': {'color': '#3B82F6', 'icon': 'laptop'},
            '경영지원': {'color': '#8B5CF6', 'icon': 'briefcase'},
            '금융': {'color': '#10B981', 'icon': 'dollar-sign'},
            '영업': {'color': '#F59E0B', 'icon': 'users'},
            '고객서비스': {'color': '#EF4444', 'icon': 'headphones'}
        }
        
        for category in categories:
            # PL/Non-PL 분류
            group = 'PL' if category.name in pl_categories else 'Non-PL'
            
            # 카테고리 데이터 구조
            category_data = {
                'id': str(category.id),
                'name': category.name,
                'color': category_meta.get(category.name, {}).get('color', '#6B7280'),
                'icon': category_meta.get(category.name, {}).get('icon', 'folder'),
                'jobs': {}
            }
            
            # 직종별 직무 정리
            for job_type in category.job_types.all():
                jobs = []
                for job_role in job_type.job_roles.all():
                    try:
                        has_profile = bool(job_role.profile and job_role.profile.is_active)
                        profile_id = str(job_role.profile.id) if has_profile else None
                    except JobProfile.DoesNotExist:
                        has_profile = False
                        profile_id = None
                    
                    job_info = {
                        'id': str(job_role.id),
                        'name': job_role.name,
                        'has_profile': has_profile,
                        'profile_id': profile_id
                    }
                    jobs.append(job_info)
                
                if jobs:
                    category_data['jobs'][job_type.name] = jobs
            
            # 데이터 추가
            if category_data['jobs']:
                tree_data[group][category.name] = category_data
        
        # 통계 정보
        statistics = {
            'Non-PL': {
                'categories': len(tree_data['Non-PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['Non-PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['Non-PL'].values() for jobs in cat['jobs'].values())
            },
            'PL': {
                'categories': len(tree_data['PL']),
                'job_types': sum(len(cat['jobs']) for cat in tree_data['PL'].values()),
                'jobs': sum(len(jobs) for cat in tree_data['PL'].values() for jobs in cat['jobs'].values())
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': tree_data,
            'statistics': statistics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_detail_api(request, job_role_id):
    """직무 상세 정보 API"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
        
        # 응답 데이터
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'full_path': job_role.full_path,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
            },
            'profile': None
        }
        
        # 직무기술서 정보
        try:
            profile = job_role.profile
            if profile and profile.is_active:
                data['profile'] = {
                    'id': str(profile.id),
                    'role_responsibility': profile.role_responsibility,
                    'qualification': profile.qualification,
                    'basic_skills': profile.basic_skills,
                    'applied_skills': profile.applied_skills,
                    'growth_path': profile.growth_path,
                    'related_certifications': profile.related_certifications
                }
        except JobProfile.DoesNotExist:
            pass
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except JobRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '직무를 찾을 수 없습니다.'
        }, status=404)
'''

        with open("job_profile_treemap_only_fix/views.py", "w", encoding="utf-8") as f:
            f.write(views_content)
            
        print("[완료] 단순화된 뷰 생성")

    def _generate_cleaned_urls(self):
        """정리된 URL 패턴 생성"""
        
        urls_content = '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 메인 트리맵 뷰 (단일 진입점)
    path('', views.JobTreeMapView.as_view(), name='main'),
    path('', views.JobTreeMapView.as_view(), name='list'),  # 기존 호환성
    path('', views.JobTreeMapView.as_view(), name='tree'),  # 기존 호환성
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data_api'),
    path('api/job-detail/<uuid:job_role_id>/', views.job_detail_api, name='job_detail_api'),
    
    # 편집/생성은 별도 앱이나 관리자에서 처리
    # path('<uuid:job_role_id>/edit/', views.job_profile_edit, name='edit'),
    # path('create/', views.job_profile_create, name='create'),
]
'''

        with open("job_profile_treemap_only_fix/urls.py", "w", encoding="utf-8") as f:
            f.write(urls_content)
            
        print("[완료] 정리된 URL 패턴 생성")

    def _generate_improved_base_template(self):
        """개선된 베이스 템플릿 생성"""
        
        base_template = '''{% load static %}
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="OK금융그룹 인사관리 시스템">
    <title>{% block title %}OK금융그룹 HR System{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{% static 'images/favicon.png' %}">
    
    <!-- 폰트 -->
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css" />
    
    <!-- 공통 CSS -->
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f8fafc;
            color: #1f2937;
            line-height: 1.6;
        }
        
        /* 헤더 */
        .main-header {
            background: white;
            border-bottom: 1px solid #e5e7eb;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-logo {
            display: flex;
            align-items: center;
            gap: 1rem;
            text-decoration: none;
            color: #1f2937;
        }
        
        .header-logo img {
            height: 40px;
        }
        
        .header-title {
            font-size: 1.25rem;
            font-weight: 700;
        }
        
        .header-nav {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            color: #6b7280;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }
        
        .nav-link:hover,
        .nav-link.active {
            color: #3B82F6;
        }
        
        /* 메인 컨텐츠 */
        .main-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* 페이지 헤더 */
        .page-header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .page-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 0.5rem;
        }
        
        .page-subtitle {
            font-size: 1.125rem;
            color: #6b7280;
        }
        
        /* 반응형 */
        @media (max-width: 768px) {
            .header-container {
                padding: 1rem;
            }
            
            .header-nav {
                display: none;
            }
            
            .main-content {
                padding: 1rem;
            }
            
            .page-title {
                font-size: 2rem;
            }
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 헤더 -->
    <header class="main-header">
        <div class="header-container">
            <a href="/" class="header-logo">
                <img src="{% static 'images/logo.png' %}" alt="OK금융그룹">
                <span class="header-title">직무 체계도</span>
            </a>
            
            <nav class="header-nav">
                <a href="/" class="nav-link active">직무 체계도</a>
                <!-- 필요시 다른 메뉴 추가 -->
            </nav>
        </div>
    </header>

    <!-- 메인 컨텐츠 -->
    <main class="main-content">
        {% block page_header %}
        <div class="page-header">
            <h1 class="page-title">OK금융그룹 직무 체계도</h1>
            <p class="page-subtitle">직군 → 직종 → 직무 구조를 한눈에 확인하세요</p>
        </div>
        {% endblock %}
        
        {% block content %}{% endblock %}
    </main>

    {% block extra_js %}{% endblock %}
</body>
</html>'''

        os.makedirs("job_profile_treemap_only_fix/templates", exist_ok=True)
        
        with open("job_profile_treemap_only_fix/templates/base_unified.html", "w", encoding="utf-8") as f:
            f.write(base_template)
            
        print("[완료] 개선된 베이스 템플릿 생성")

    def _generate_deletion_script(self):
        """삭제할 파일 목록 생성"""
        
        deletion_script = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
기존 파일 삭제 스크립트
"""

import os
import shutil

# 삭제할 파일 목록
files_to_delete = [
    # 기존 템플릿들
    "job_profiles/templates/job_profiles/job_profile_list.html",
    "job_profiles/templates/job_profiles/job_profile_detail.html",
    "job_profiles/templates/job_profiles/job_profile_admin_list.html",
    "job_profiles/templates/job_profiles/job_profile_admin_detail.html",
    "job_profiles/templates/job_profiles/job_profile_form.html",
    "job_profiles/templates/job_profiles/job_profile_confirm_delete.html",
    "job_profiles/templates/job_profiles/job_hierarchy_navigation.html",
    "job_profiles/templates/job_profiles/job_tree.html",
    "job_profiles/templates/job_profiles/job_tree_map.html",
    "job_profiles/templates/job_profiles/job_tree_map_simple.html",
    
    # 기존 정적 파일들
    "static/js/JobProfileTreeMap.js",
    "static/css/JobProfileTreeMap.css",
    
    # 기존 뷰 파일
    "job_profiles/views_simple.py",
]

# 삭제할 디렉토리
dirs_to_delete = [
    "job_profile_tree_overhaul/",
    "generated_templates/",
    "generated_views/",
]

def delete_files():
    """파일 및 디렉토리 삭제"""
    
    # 파일 삭제
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[삭제] {file_path}")
            except Exception as e:
                print(f"[오류] {file_path}: {e}")
        else:
            print(f"[건너뜀] {file_path} (파일 없음)")
    
    # 디렉토리 삭제
    for dir_path in dirs_to_delete:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"[삭제] {dir_path}/")
            except Exception as e:
                print(f"[오류] {dir_path}/: {e}")
        else:
            print(f"[건너뜀] {dir_path}/ (디렉토리 없음)")
    
    print("\n삭제 완료!")

if __name__ == "__main__":
    response = input("정말로 기존 파일들을 삭제하시겠습니까? (yes/no): ")
    if response.lower() == 'yes':
        delete_files()
    else:
        print("취소되었습니다.")
'''

        with open("job_profile_treemap_only_fix/delete_legacy_files.py", "w", encoding="utf-8") as f:
            f.write(deletion_script)
            
        # README 생성
        readme_content = '''# OK금융그룹 직무 트리맵 단일화

## 개요

기존의 트리뷰, 그리드뷰, 리스트뷰를 모두 제거하고 트리맵 UI로 단일화한 버전입니다.

## 주요 변경사항

### 1. 뷰 단일화
- 모든 기존 뷰 제거 (트리뷰, 그리드뷰, 리스트뷰, 관리 목록)
- 트리맵 뷰만 유지
- 단일 진입점: `/job-profiles/`

### 2. UI 일관성
- 상단 통계 카드: 트리맵과 동일한 그라디언트 스타일
- 배경색: #f8fafc (neutral-50)
- 카드 디자인: 일관된 border-radius, shadow, hover 효과
- 브랜드 컬러 시스템 적용

### 3. 팝업 상세
- 카드 클릭시 모달 팝업으로 상세 정보 표시
- 편집 버튼은 기술서가 있는 경우만 표시
- ESC 키 또는 외부 클릭으로 닫기

### 4. URL 정리
- `/job-profiles/` - 메인 트리맵
- `/job-profiles/api/tree-map-data/` - 트리 데이터 API
- `/job-profiles/api/job-detail/<id>/` - 직무 상세 API

### 5. 삭제된 기능
- 리스트 뷰
- 관리자 목록
- 계층 네비게이션
- 그리드 뷰
- 레거시 트리 뷰

## 파일 구조

```
job_profiles/
├── templates/job_profiles/
│   └── job_treemap.html         # 통합 트리맵 템플릿
├── views.py                     # 단순화된 뷰 (트리맵만)
└── urls.py                      # 정리된 URL 패턴

static/
├── css/
│   └── job_treemap_unified.css  # 통합 스타일시트
└── js/
    └── job_treemap_unified.js   # 통합 JavaScript

templates/
└── base_unified.html            # 개선된 베이스 템플릿
```

## 설치 방법

1. 기존 파일 백업
```bash
python delete_legacy_files.py
```

2. 새 파일 복사
```bash
cp -r job_profile_treemap_only_fix/* /path/to/project/
```

3. 서버 재시작
```bash
python manage.py runserver
```

## 색상 시스템

| 직군 | 색상 | 그라디언트 |
|------|------|------------|
| IT/디지털 | #3B82F6 | #3B82F6 → #60A5FA |
| 경영지원 | #8B5CF6 | #8B5CF6 → #A78BFA |
| 금융 | #10B981 | #10B981 → #34D399 |
| 영업 | #F59E0B | #F59E0B → #FCD34D |
| 고객서비스 | #EF4444 | #EF4444 → #F87171 |

## 성능 최적화

- 단일 템플릿으로 로딩 속도 향상
- JavaScript 최적화로 인터랙션 개선
- CSS 애니메이션으로 부드러운 전환
- 불필요한 코드 제거로 번들 크기 감소

## 브라우저 지원

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- 모바일 브라우저 완벽 지원
'''

        with open("job_profile_treemap_only_fix/README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        print("[완료] 삭제 스크립트 및 README 생성")

# 실행
if __name__ == "__main__":
    fixer = JobProfileTreeMapOnlyFix()
    fixer.generate_all()