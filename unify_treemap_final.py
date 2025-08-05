#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 직무체계도 트리맵 UI 최종 단일화 스크립트
- 기존 트리뷰/그리드뷰/리스트뷰 완전 제거
- 트리맵(Tree Map) UI 단일화
- 상단 통계 디자인 일치
- 카드 클릭 시 팝업 상세
"""

import os
import shutil
from datetime import datetime

# 베이스 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_unified_template():
    """통합된 트리맵 템플릿 생성"""
    template_content = '''{% extends "base_simple.html" %}
{% load static %}

{% block extra_css %}
<!-- Font Awesome -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- 통합 CSS -->
<link rel="stylesheet" href="{% static 'css/job_treemap_unified.css' %}">
{% endblock %}

{% block content %}
<div class="treemap-container">
    <!-- 페이지 헤더 -->
    <div class="page-header">
        <h1 class="page-title">
            <i class="fas fa-sitemap"></i>
            직무 체계도
        </h1>
        <p class="page-subtitle">OK금융그룹의 전체 직무 체계를 한눈에 확인하세요</p>
    </div>

    <!-- 통계 카드 -->
    <div class="stats-section">
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-layer-group"></i>
            </div>
            <div class="stat-content">
                <div class="stat-number">{{ total_categories }}</div>
                <div class="stat-label">직군</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
            </div>
            <div class="stat-content">
                <div class="stat-number">{{ total_job_types }}</div>
                <div class="stat-label">직종</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-user-tie"></i>
            </div>
            <div class="stat-content">
                <div class="stat-number">{{ total_job_roles }}</div>
                <div class="stat-label">직무</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="stat-content">
                <div class="stat-number">{{ total_profiles }}</div>
                <div class="stat-label">직무기술서</div>
            </div>
        </div>
    </div>

    <!-- 검색 및 필터 -->
    <div class="controls-section">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="searchInput" placeholder="직무명으로 검색..." class="search-input">
        </div>
        <div class="filter-buttons">
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

    <!-- 트리맵 컨텐츠 -->
    <div class="treemap-content">
        <!-- Non-PL 직군 -->
        <div class="group-section non-pl-group" data-group="non-pl">
            <h2 class="group-title">
                <i class="fas fa-users"></i>
                Non-PL 직군
            </h2>
            <div id="non-pl-content" class="group-content">
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>데이터를 불러오는 중...</span>
                </div>
            </div>
        </div>

        <!-- PL 직군 -->
        <div class="group-section pl-group" data-group="pl">
            <h2 class="group-title">
                <i class="fas fa-user-shield"></i>
                PL 직군
            </h2>
            <div id="pl-content" class="group-content">
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <span>데이터를 불러오는 중...</span>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 직무 상세 모달 -->
<div id="jobDetailModal" class="modal">
    <div class="modal-content">
        <div class="modal-header">
            <h2 id="modalTitle">직무 상세 정보</h2>
            <button class="modal-close" onclick="closeModal()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body" id="modalBody">
            <!-- 동적 컨텐츠 -->
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/job_treemap_unified.js' %}"></script>
{% endblock %}'''
    
    return template_content

def create_unified_css():
    """통합된 CSS 생성"""
    css_content = '''/* 직무 트리맵 통합 스타일 */
:root {
    --primary-color: #2E86DE;
    --secondary-color: #FF6B6B;
    --success-color: #26DE81;
    --warning-color: #FED330;
    --info-color: #4BCFFA;
    --dark-color: #2C3E50;
    --light-color: #F5F6FA;
    --border-radius: 12px;
    --transition: all 0.3s ease;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
    --shadow-hover: 0 4px 16px rgba(0,0,0,0.15);
}

/* 기본 레이아웃 */
.treemap-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
}

/* 페이지 헤더 */
.page-header {
    text-align: center;
    margin-bottom: 40px;
}

.page-title {
    font-size: 36px;
    font-weight: 700;
    color: var(--dark-color);
    margin-bottom: 8px;
}

.page-title i {
    color: var(--primary-color);
    margin-right: 12px;
}

.page-subtitle {
    font-size: 18px;
    color: #7f8c8d;
}

/* 통계 섹션 */
.stats-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-bottom: 40px;
}

.stat-card {
    background: white;
    border-radius: var(--border-radius);
    padding: 24px;
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    gap: 20px;
    transition: var(--transition);
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
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

.stat-card:nth-child(1) .stat-icon { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-card:nth-child(2) .stat-icon { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-card:nth-child(3) .stat-icon { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-card:nth-child(4) .stat-icon { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-content {
    flex: 1;
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: var(--dark-color);
    line-height: 1;
}

.stat-label {
    font-size: 14px;
    color: #7f8c8d;
    margin-top: 4px;
}

/* 컨트롤 섹션 */
.controls-section {
    background: white;
    border-radius: var(--border-radius);
    padding: 20px;
    box-shadow: var(--shadow);
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
    color: #7f8c8d;
}

.search-input {
    width: 100%;
    padding: 12px 16px 12px 44px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 16px;
    transition: var(--transition);
}

.search-input:focus {
    outline: none;
    border-color: var(--primary-color);
}

.filter-buttons {
    display: flex;
    gap: 8px;
}

.filter-btn {
    padding: 10px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    color: var(--dark-color);
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition);
}

.filter-btn:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.filter-btn.active {
    background: var(--primary-color);
    border-color: var(--primary-color);
    color: white;
}

/* 트리맵 컨텐츠 */
.treemap-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

.group-section {
    background: white;
    border-radius: var(--border-radius);
    padding: 24px;
    box-shadow: var(--shadow);
}

.group-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 2px solid #e0e0e0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.non-pl-group .group-title {
    color: var(--primary-color);
    border-bottom-color: var(--primary-color);
}

.pl-group .group-title {
    color: var(--secondary-color);
    border-bottom-color: var(--secondary-color);
}

/* 카테고리 섹션 */
.category-section {
    margin-bottom: 24px;
    padding: 20px;
    background: var(--light-color);
    border-radius: var(--border-radius);
}

.category-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}

.category-icon {
    width: 48px;
    height: 48px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
}

.category-info h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--dark-color);
    margin: 0;
}

.category-stats {
    font-size: 14px;
    color: #7f8c8d;
}

/* 직종 섹션 */
.job-type-section {
    margin-bottom: 16px;
}

.job-type-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--dark-color);
    margin-bottom: 12px;
    padding-left: 16px;
    border-left: 4px solid;
}

/* 직무 그리드 */
.jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
}

.job-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    cursor: pointer;
    transition: var(--transition);
}

.job-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

.job-card.has-profile {
    border-color: var(--success-color);
}

.job-card-icon {
    font-size: 24px;
    margin-bottom: 8px;
}

.job-card-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--dark-color);
    margin-bottom: 4px;
}

.job-card-status {
    font-size: 11px;
    color: #7f8c8d;
}

.job-card.has-profile .job-card-status {
    color: var(--success-color);
}

/* 모달 */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1000;
    padding: 20px;
    overflow-y: auto;
}

.modal.show {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    background: white;
    border-radius: var(--border-radius);
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}

.modal-header {
    padding: 24px;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h2 {
    margin: 0;
    font-size: 24px;
    color: var(--dark-color);
}

.modal-close {
    width: 36px;
    height: 36px;
    border: none;
    background: var(--light-color);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
}

.modal-close:hover {
    background: #e0e0e0;
}

.modal-body {
    padding: 24px;
}

/* 로딩 */
.loading {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
}

.loading i {
    font-size: 32px;
    margin-bottom: 12px;
}

/* 카테고리별 색상 */
.cat-it { background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%); }
.cat-management { background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%); }
.cat-finance { background: linear-gradient(135deg, #10B981 0%, #34D399 100%); }
.cat-sales { background: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%); }
.cat-service { background: linear-gradient(135deg, #EF4444 0%, #F87171 100%); }

.color-it { color: #3B82F6; border-color: #3B82F6; }
.color-management { color: #8B5CF6; border-color: #8B5CF6; }
.color-finance { color: #10B981; border-color: #10B981; }
.color-sales { color: #F59E0B; border-color: #F59E0B; }
.color-service { color: #EF4444; border-color: #EF4444; }

/* 반응형 */
@media (max-width: 1024px) {
    .treemap-content {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .stats-section {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .controls-section {
        flex-direction: column;
    }
    
    .search-box {
        min-width: 100%;
    }
    
    .jobs-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    }
}'''
    
    return css_content

def create_unified_js():
    """통합된 JavaScript 생성"""
    js_content = '''// 직무 트리맵 통합 JavaScript
(function() {
    'use strict';
    
    // 전역 변수
    let treeData = null;
    let currentFilter = 'all';
    let searchTerm = '';
    
    // 초기화
    document.addEventListener('DOMContentLoaded', function() {
        loadTreeMapData();
        initializeControls();
    });
    
    // 트리맵 데이터 로드
    async function loadTreeMapData() {
        try {
            const response = await fetch('/job-profiles/api/tree-map-data/', {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const result = await response.json();
            if (result.success) {
                treeData = result.data;
                renderTreeMap();
            } else {
                showError(result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            showError('데이터를 불러오는데 실패했습니다.');
        }
    }
    
    // 트리맵 렌더링
    function renderTreeMap() {
        // Non-PL 렌더링
        const nonPlContent = document.getElementById('non-pl-content');
        nonPlContent.innerHTML = renderGroup(treeData['Non-PL'] || {});
        
        // PL 렌더링
        const plContent = document.getElementById('pl-content');
        plContent.innerHTML = renderGroup(treeData['PL'] || {});
        
        // 필터 적용
        applyFilters();
    }
    
    // 그룹 렌더링
    function renderGroup(groupData) {
        let html = '';
        
        Object.entries(groupData).forEach(([categoryName, categoryData]) => {
            const categoryClass = getCategoryClass(categoryName);
            const colorClass = getColorClass(categoryName);
            
            html += `
                <div class="category-section" data-category="${categoryName}">
                    <div class="category-header">
                        <div class="category-icon ${categoryClass}">
                            <i class="fas ${getIcon(categoryData.icon)}"></i>
                        </div>
                        <div class="category-info">
                            <h3>${categoryName}</h3>
                            <div class="category-stats">
                                ${Object.keys(categoryData.jobs).length}개 직종 · 
                                ${countJobs(categoryData.jobs)}개 직무
                            </div>
                        </div>
                    </div>
                    ${renderJobTypes(categoryData.jobs, colorClass)}
                </div>
            `;
        });
        
        return html || '<p class="no-data">데이터가 없습니다.</p>';
    }
    
    // 직종 렌더링
    function renderJobTypes(jobTypes, colorClass) {
        let html = '';
        
        Object.entries(jobTypes).forEach(([jobTypeName, jobs]) => {
            html += `
                <div class="job-type-section">
                    <h4 class="job-type-title ${colorClass}">${jobTypeName}</h4>
                    <div class="jobs-grid">
                        ${jobs.map(job => renderJobCard(job, colorClass)).join('')}
                    </div>
                </div>
            `;
        });
        
        return html;
    }
    
    // 직무 카드 렌더링
    function renderJobCard(job, colorClass) {
        const hasProfile = job.has_profile;
        const cardClass = hasProfile ? 'has-profile' : '';
        
        return `
            <div class="job-card ${cardClass}" 
                 data-job-name="${job.name.toLowerCase()}"
                 onclick="showJobDetail('${job.id}', '${job.name}', ${hasProfile})">
                <div class="job-card-icon ${colorClass}">
                    <i class="fas ${hasProfile ? 'fa-file-alt' : 'fa-file'}"></i>
                </div>
                <div class="job-card-name">${job.name}</div>
                <div class="job-card-status">
                    ${hasProfile ? '기술서 완료' : '미작성'}
                </div>
            </div>
        `;
    }
    
    // 직무 상세 보기
    window.showJobDetail = async function(jobId, jobName, hasProfile) {
        if (!hasProfile) {
            alert(`'${jobName}' 직무의 기술서가 아직 작성되지 않았습니다.`);
            return;
        }
        
        try {
            const response = await fetch(`/job-profiles/api/job-detail-modal/${jobId}/`, {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const result = await response.json();
            if (result.success) {
                displayModal(result.data);
            } else {
                alert('직무 정보를 불러올 수 없습니다.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('직무 정보를 불러오는데 실패했습니다.');
        }
    };
    
    // 모달 표시
    function displayModal(data) {
        const modal = document.getElementById('jobDetailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = data.job.name;
        
        let content = `
            <div class="job-detail">
                <div class="detail-section">
                    <h3><i class="fas fa-info-circle"></i> 기본 정보</h3>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <label>직군</label>
                            <span>${data.job.category}</span>
                        </div>
                        <div class="detail-item">
                            <label>직종</label>
                            <span>${data.job.job_type}</span>
                        </div>
                        <div class="detail-item">
                            <label>직무명</label>
                            <span>${data.job.name}</span>
                        </div>
                    </div>
                </div>
        `;
        
        if (data.profile) {
            content += `
                <div class="detail-section">
                    <h3><i class="fas fa-tasks"></i> 핵심 역할 및 책임</h3>
                    <div class="detail-content">
                        ${data.profile.role_responsibility}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3><i class="fas fa-check-circle"></i> 자격 요건</h3>
                    <div class="detail-content">
                        ${data.profile.qualification}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3><i class="fas fa-star"></i> 필요 역량</h3>
                    <div class="skill-tags">
                        <h4>기본 역량</h4>
                        <div class="tags">
                            ${data.profile.basic_skills.map(skill => 
                                `<span class="tag">${skill}</span>`
                            ).join('')}
                        </div>
                        <h4>우대 역량</h4>
                        <div class="tags">
                            ${data.profile.applied_skills.map(skill => 
                                `<span class="tag tag-preferred">${skill}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
                
                <div class="detail-actions">
                    <a href="/job-profiles/${data.profile.id}/" class="btn btn-primary">
                        <i class="fas fa-eye"></i> 상세보기
                    </a>
                    <a href="/job-profiles/edit/${data.job.id}/" class="btn btn-secondary">
                        <i class="fas fa-edit"></i> 편집
                    </a>
                </div>
            `;
        }
        
        content += '</div>';
        modalBody.innerHTML = content;
        
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    // 모달 닫기
    window.closeModal = function() {
        const modal = document.getElementById('jobDetailModal');
        modal.classList.remove('show');
        document.body.style.overflow = '';
    };
    
    // 컨트롤 초기화
    function initializeControls() {
        // 검색
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function(e) {
            searchTerm = e.target.value.toLowerCase();
            applyFilters();
        });
        
        // 필터 버튼
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.dataset.filter;
                applyFilters();
            });
        });
        
        // 모달 외부 클릭 시 닫기
        document.getElementById('jobDetailModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }
    
    // 필터 적용
    function applyFilters() {
        // 그룹 필터
        document.querySelectorAll('.group-section').forEach(section => {
            const group = section.dataset.group;
            if (currentFilter === 'all' || currentFilter === group) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
        
        // 검색 필터
        document.querySelectorAll('.job-card').forEach(card => {
            const jobName = card.dataset.jobName;
            if (searchTerm && !jobName.includes(searchTerm)) {
                card.style.display = 'none';
            } else {
                card.style.display = 'block';
            }
        });
    }
    
    // 유틸리티 함수
    function getCategoryClass(categoryName) {
        const classMap = {
            'IT/디지털': 'cat-it',
            '경영지원': 'cat-management',
            '금융': 'cat-finance',
            '영업': 'cat-sales',
            '고객서비스': 'cat-service'
        };
        return classMap[categoryName] || 'cat-it';
    }
    
    function getColorClass(categoryName) {
        const classMap = {
            'IT/디지털': 'color-it',
            '경영지원': 'color-management',
            '금융': 'color-finance',
            '영업': 'color-sales',
            '고객서비스': 'color-service'
        };
        return classMap[categoryName] || 'color-it';
    }
    
    function getIcon(iconName) {
        const iconMap = {
            'laptop': 'fa-laptop',
            'briefcase': 'fa-briefcase',
            'dollar-sign': 'fa-dollar-sign',
            'users': 'fa-users',
            'headphones': 'fa-headphones'
        };
        return iconMap[iconName] || 'fa-folder';
    }
    
    function countJobs(jobTypes) {
        return Object.values(jobTypes).reduce((sum, jobs) => sum + jobs.length, 0);
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    function showError(message) {
        const content = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
        document.getElementById('non-pl-content').innerHTML = content;
        document.getElementById('pl-content').innerHTML = '';
    }
})();'''
    
    return js_content

def create_unified_views():
    """통합된 뷰 생성"""
    views_content = '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Q, Prefetch
from django.views.decorators.csrf import csrf_exempt
import json

from .models import JobCategory, JobType, JobRole, JobProfile
from .serializers import JobRoleSerializer, JobProfileSerializer

class JobTreeMapView(TemplateView):
    """통합된 직무 트리맵 뷰"""
    template_name = 'job_profiles/job_treemap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 데이터
        context['total_categories'] = JobCategory.objects.count()
        context['total_job_types'] = JobType.objects.count()
        context['total_job_roles'] = JobRole.objects.count()
        context['total_profiles'] = JobProfile.objects.filter(is_active=True).count()
        
        return context

def job_tree_map_data_api(request):
    """트리맵 데이터 API"""
    try:
        # 카테고리를 Non-PL과 PL로 분류
        non_pl_categories = ['IT/디지털', '경영지원', '금융', '영업', '고객서비스']
        pl_categories = ['PL']
        
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
        
        # 모든 카테고리 조회
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
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
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
        
        # 프로필 정보 추가
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
    job_role = get_object_or_404(JobRole, id=job_role_id)
    
    # GET 요청: 편집 페이지 표시
    if request.method == 'GET':
        profile = None
        if hasattr(job_role, 'profile'):
            profile = job_role.profile
        
        context = {
            'job': job_role,
            'profile': profile or {}
        }
        return render(request, 'job_profiles/job_profile_edit.html', context)
    
    # POST 요청: 저장 처리
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 프로필 생성 또는 업데이트
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

def create_unified_urls():
    """통합된 URL 패턴 생성"""
    urls_content = '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 메인 트리맵 뷰
    path('', views.JobTreeMapView.as_view(), name='list'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]'''
    
    return urls_content

def backup_existing_files():
    """기존 파일 백업"""
    backup_dir = os.path.join(BASE_DIR, 'backup_treemap_unification')
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_tree_map_simple.html',
        'job_profiles/views.py',
        'job_profiles/urls.py'
    ]
    
    for file_path in files_to_backup:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            backup_path = os.path.join(backup_dir, file_path.replace('/', '_'))
            shutil.copy2(full_path, backup_path)
            print(f"백업됨: {file_path}")

def delete_legacy_files():
    """레거시 파일 삭제"""
    files_to_delete = [
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_profile_list.html',
        'static/js/JobProfileTreeMap.js',
        'static/css/JobProfileTreeMap.css'
    ]
    
    for file_path in files_to_delete:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"삭제됨: {file_path}")

def write_files():
    """파일 생성"""
    # 템플릿 생성
    template_path = os.path.join(BASE_DIR, 'job_profiles/templates/job_profiles/job_treemap.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_template())
    print(f"생성됨: {template_path}")
    
    # CSS 생성
    css_path = os.path.join(BASE_DIR, 'static/css/job_treemap_unified.css')
    os.makedirs(os.path.dirname(css_path), exist_ok=True)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_css())
    print(f"생성됨: {css_path}")
    
    # JavaScript 생성
    js_path = os.path.join(BASE_DIR, 'static/js/job_treemap_unified.js')
    os.makedirs(os.path.dirname(js_path), exist_ok=True)
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_js())
    print(f"생성됨: {js_path}")
    
    # Views 생성
    views_path = os.path.join(BASE_DIR, 'job_profiles/views.py')
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_views())
    print(f"생성됨: {views_path}")
    
    # URLs 생성
    urls_path = os.path.join(BASE_DIR, 'job_profiles/urls.py')
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_urls())
    print(f"생성됨: {urls_path}")

def main():
    print("=== OK금융그룹 직무체계도 트리맵 UI 최종 단일화 ===")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. 백업
    print("\n1. 기존 파일 백업 중...")
    backup_existing_files()
    
    # 2. 레거시 파일 삭제
    print("\n2. 레거시 파일 삭제 중...")
    delete_legacy_files()
    
    # 3. 새 파일 생성
    print("\n3. 통합 파일 생성 중...")
    write_files()
    
    print("\n=== 완료 ===")
    print("다음 단계:")
    print("1. python manage.py collectstatic")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/job-profiles/ 접속하여 확인")

if __name__ == '__main__':
    main()