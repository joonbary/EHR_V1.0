#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK금융그룹 직무체계도 TreeMap UI 완전 단일화 스크립트
- 모든 레거시 뷰/템플릿/URL 완전 삭제
- job_treemap.html 단일 인터페이스만 유지
- 통계, 검색/필터, 상세 모달만 포함
- 모든 잘못된 링크와 참조 제거
"""

import os
import shutil
from datetime import datetime
import re

# 베이스 디렉토리
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_unified_treemap_template():
    """통합된 TreeMap 템플릿 (job_treemap.html)"""
    return '''{% extends "base_simple.html" %}
{% load static %}

{% block title %}직무 체계도 - OK금융그룹{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-layer-group"></i>
            </div>
            <div class="stat-body">
                <div class="stat-number">{{ total_categories }}</div>
                <div class="stat-label">직군</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-briefcase"></i>
            </div>
            <div class="stat-body">
                <div class="stat-number">{{ total_job_types }}</div>
                <div class="stat-label">직종</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-user-tie"></i>
            </div>
            <div class="stat-body">
                <div class="stat-number">{{ total_job_roles }}</div>
                <div class="stat-label">직무</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">
                <i class="fas fa-file-alt"></i>
            </div>
            <div class="stat-body">
                <div class="stat-number">{{ total_profiles }}</div>
                <div class="stat-label">직무기술서</div>
            </div>
        </div>
    </div>

    <!-- 검색 및 필터 -->
    <div class="controls-wrapper">
        <div class="search-container">
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

    <!-- TreeMap 메인 컨텐츠 -->
    <div class="treemap-main">
        <!-- Non-PL 섹션 -->
        <div class="group-container non-pl-section" data-group="non-pl">
            <div class="group-header">
                <h2 class="group-title">
                    <i class="fas fa-users"></i>
                    Non-PL 직군
                </h2>
            </div>
            <div id="nonPlContent" class="group-body">
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </div>

        <!-- PL 섹션 -->
        <div class="group-container pl-section" data-group="pl">
            <div class="group-header">
                <h2 class="group-title">
                    <i class="fas fa-user-shield"></i>
                    PL 직군
                </h2>
            </div>
            <div id="plContent" class="group-body">
                <div class="loading-state">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 직무 상세 모달 -->
<div id="jobDetailModal" class="modal-overlay">
    <div class="modal-container">
        <div class="modal-header">
            <h2 id="modalTitle">직무 상세 정보</h2>
            <button class="modal-close" onclick="closeModal()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="modal-body" id="modalContent">
            <!-- 동적 컨텐츠 -->
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/job_treemap_unified.js' %}"></script>
{% endblock %}'''

def create_unified_css():
    """통합된 CSS (job_treemap_unified.css)"""
    return '''/* OK금융그룹 직무체계도 TreeMap 통합 스타일 */

/* 변수 정의 */
:root {
    --primary: #2E86DE;
    --secondary: #FF6B6B;
    --success: #26DE81;
    --warning: #FED330;
    --info: #4BCFFA;
    --dark: #2C3E50;
    --light: #F8F9FA;
    --gray: #6C757D;
    --white: #FFFFFF;
    
    --radius: 12px;
    --radius-sm: 8px;
    --radius-lg: 16px;
    
    --shadow: 0 2px 8px rgba(0,0,0,0.08);
    --shadow-hover: 0 4px 16px rgba(0,0,0,0.12);
    --shadow-modal: 0 8px 32px rgba(0,0,0,0.16);
    
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 전역 스타일 초기화 */
* {
    box-sizing: border-box;
}

/* 메인 컨테이너 */
.treemap-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
    min-height: 100vh;
}

/* 페이지 헤더 */
.page-header {
    text-align: center;
    margin-bottom: 48px;
}

.page-title {
    font-size: 42px;
    font-weight: 700;
    color: var(--dark);
    margin: 0 0 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
}

.page-title i {
    color: var(--primary);
}

.page-subtitle {
    font-size: 18px;
    color: var(--gray);
    margin: 0;
}

/* 통계 그리드 */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 24px;
    margin-bottom: 40px;
}

.stat-card {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 28px;
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    gap: 24px;
    transition: var(--transition);
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
}

.stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    color: var(--white);
    flex-shrink: 0;
}

.stat-card:nth-child(1) .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card:nth-child(2) .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-card:nth-child(3) .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-card:nth-child(4) .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.stat-body {
    flex: 1;
}

.stat-number {
    font-size: 36px;
    font-weight: 700;
    color: var(--dark);
    line-height: 1;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 16px;
    color: var(--gray);
}

/* 컨트롤 영역 */
.controls-wrapper {
    background: var(--white);
    border-radius: var(--radius-lg);
    padding: 24px;
    box-shadow: var(--shadow);
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
}

.search-container {
    flex: 1;
    min-width: 320px;
    position: relative;
}

.search-container i {
    position: absolute;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--gray);
    font-size: 18px;
}

.search-input {
    width: 100%;
    padding: 14px 20px 14px 52px;
    border: 2px solid #E9ECEF;
    border-radius: var(--radius);
    font-size: 16px;
    transition: var(--transition);
}

.search-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(46, 134, 222, 0.1);
}

.filter-group {
    display: flex;
    gap: 8px;
}

.filter-btn {
    padding: 12px 24px;
    border: 2px solid #E9ECEF;
    border-radius: var(--radius);
    background: var(--white);
    color: var(--dark);
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition);
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-btn:hover {
    border-color: var(--primary);
    color: var(--primary);
}

.filter-btn.active {
    background: var(--primary);
    border-color: var(--primary);
    color: var(--white);
}

/* TreeMap 메인 레이아웃 */
.treemap-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;
}

.group-container {
    background: var(--white);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    overflow: hidden;
}

.group-header {
    padding: 24px;
    border-bottom: 2px solid #E9ECEF;
}

.group-title {
    font-size: 24px;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.non-pl-section .group-title {
    color: var(--primary);
}

.pl-section .group-title {
    color: var(--secondary);
}

.group-body {
    padding: 24px;
}

/* 카테고리 블록 */
.category-block {
    margin-bottom: 24px;
    padding: 20px;
    background: var(--light);
    border-radius: var(--radius);
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
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--white);
    font-size: 20px;
}

.category-info h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--dark);
    margin: 0 0 4px;
}

.category-stats {
    font-size: 14px;
    color: var(--gray);
}

/* 직종 섹션 */
.job-type-block {
    margin-bottom: 16px;
}

.job-type-header {
    font-size: 16px;
    font-weight: 600;
    color: var(--dark);
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
    background: var(--white);
    border: 2px solid #E9ECEF;
    border-radius: var(--radius-sm);
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
    border-color: var(--success);
}

.job-icon {
    font-size: 24px;
    margin-bottom: 8px;
}

.job-name {
    font-size: 13px;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 4px;
}

.job-status {
    font-size: 11px;
    color: var(--gray);
}

.job-card.has-profile .job-status {
    color: var(--success);
}

/* 카테고리 색상 */
.cat-it { background: linear-gradient(135deg, #3B82F6, #60A5FA); }
.cat-management { background: linear-gradient(135deg, #8B5CF6, #A78BFA); }
.cat-finance { background: linear-gradient(135deg, #10B981, #34D399); }
.cat-sales { background: linear-gradient(135deg, #F59E0B, #FCD34D); }
.cat-service { background: linear-gradient(135deg, #EF4444, #F87171); }

.color-it { color: #3B82F6; border-color: #3B82F6; }
.color-management { color: #8B5CF6; border-color: #8B5CF6; }
.color-finance { color: #10B981; border-color: #10B981; }
.color-sales { color: #F59E0B; border-color: #F59E0B; }
.color-service { color: #EF4444; border-color: #EF4444; }

/* 모달 */
.modal-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    z-index: 9999;
    padding: 20px;
    overflow-y: auto;
}

.modal-overlay.show {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-container {
    background: var(--white);
    border-radius: var(--radius-lg);
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow: hidden;
    box-shadow: var(--shadow-modal);
}

.modal-header {
    padding: 24px;
    border-bottom: 1px solid #E9ECEF;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-header h2 {
    margin: 0;
    font-size: 24px;
    color: var(--dark);
}

.modal-close {
    width: 40px;
    height: 40px;
    border: none;
    background: var(--light);
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
}

.modal-close:hover {
    background: #E9ECEF;
}

.modal-body {
    padding: 32px;
    overflow-y: auto;
    max-height: calc(90vh - 100px);
}

/* 로딩 상태 */
.loading-state {
    text-align: center;
    padding: 60px;
    color: var(--gray);
}

.loading-state i {
    font-size: 36px;
    margin-bottom: 16px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* 반응형 */
@media (max-width: 1024px) {
    .treemap-main {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .treemap-container {
        padding: 16px;
    }
    
    .page-title {
        font-size: 32px;
    }
    
    .controls-wrapper {
        flex-direction: column;
    }
    
    .search-container {
        min-width: 100%;
    }
    
    .filter-group {
        width: 100%;
        justify-content: center;
    }
    
    .jobs-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    }
}'''

def create_unified_js():
    """통합된 JavaScript (job_treemap_unified.js)"""
    return '''// OK금융그룹 직무체계도 TreeMap 통합 JavaScript
(function() {
    'use strict';
    
    // 전역 상태
    const state = {
        treeData: null,
        currentFilter: 'all',
        searchTerm: ''
    };
    
    // DOM 요소
    const elements = {
        nonPlContent: null,
        plContent: null,
        searchInput: null,
        filterBtns: null,
        modal: null,
        modalTitle: null,
        modalContent: null
    };
    
    // 초기화
    document.addEventListener('DOMContentLoaded', function() {
        initializeElements();
        initializeEventListeners();
        loadTreeMapData();
    });
    
    // DOM 요소 초기화
    function initializeElements() {
        elements.nonPlContent = document.getElementById('nonPlContent');
        elements.plContent = document.getElementById('plContent');
        elements.searchInput = document.getElementById('searchInput');
        elements.filterBtns = document.querySelectorAll('.filter-btn');
        elements.modal = document.getElementById('jobDetailModal');
        elements.modalTitle = document.getElementById('modalTitle');
        elements.modalContent = document.getElementById('modalContent');
    }
    
    // 이벤트 리스너 초기화
    function initializeEventListeners() {
        // 검색
        elements.searchInput.addEventListener('input', handleSearch);
        
        // 필터
        elements.filterBtns.forEach(btn => {
            btn.addEventListener('click', handleFilter);
        });
        
        // 모달 외부 클릭
        elements.modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // ESC 키
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && elements.modal.classList.contains('show')) {
                closeModal();
            }
        });
    }
    
    // TreeMap 데이터 로드
    async function loadTreeMapData() {
        try {
            const response = await fetch('/job-profiles/api/tree-map-data/', {
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                state.treeData = result.data;
                renderTreeMap();
            } else {
                showError(result.error || '데이터 로드 실패');
            }
        } catch (error) {
            console.error('Error loading tree map data:', error);
            showError('데이터를 불러오는데 실패했습니다.');
        }
    }
    
    // TreeMap 렌더링
    function renderTreeMap() {
        if (!state.treeData) return;
        
        elements.nonPlContent.innerHTML = renderGroup(state.treeData['Non-PL'] || {});
        elements.plContent.innerHTML = renderGroup(state.treeData['PL'] || {});
        
        applyFilters();
    }
    
    // 그룹 렌더링
    function renderGroup(groupData) {
        if (!groupData || Object.keys(groupData).length === 0) {
            return '<p class="no-data">데이터가 없습니다.</p>';
        }
        
        let html = '';
        
        Object.entries(groupData).forEach(([categoryName, categoryData]) => {
            const categoryClass = getCategoryClass(categoryName);
            const colorClass = getColorClass(categoryName);
            
            html += `
                <div class="category-block" data-category="${categoryName}">
                    <div class="category-header">
                        <div class="category-icon ${categoryClass}">
                            <i class="fas ${getIcon(categoryData.icon)}"></i>
                        </div>
                        <div class="category-info">
                            <h3>${categoryName}</h3>
                            <div class="category-stats">
                                ${Object.keys(categoryData.jobs || {}).length}개 직종 · 
                                ${countJobs(categoryData.jobs)}개 직무
                            </div>
                        </div>
                    </div>
                    ${renderJobTypes(categoryData.jobs || {}, colorClass)}
                </div>
            `;
        });
        
        return html;
    }
    
    // 직종 렌더링
    function renderJobTypes(jobTypes, colorClass) {
        if (!jobTypes || Object.keys(jobTypes).length === 0) {
            return '';
        }
        
        let html = '';
        
        Object.entries(jobTypes).forEach(([jobTypeName, jobs]) => {
            if (!jobs || jobs.length === 0) return;
            
            html += `
                <div class="job-type-block">
                    <h4 class="job-type-header ${colorClass}">${jobTypeName}</h4>
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
        const hasProfile = job.has_profile === true;
        const cardClass = hasProfile ? 'has-profile' : '';
        
        return `
            <div class="job-card ${cardClass}" 
                 data-job-name="${(job.name || '').toLowerCase()}"
                 onclick="handleJobClick('${job.id}', '${escapeHtml(job.name)}', ${hasProfile})">
                <div class="job-icon ${colorClass}">
                    <i class="fas ${hasProfile ? 'fa-file-alt' : 'fa-file'}"></i>
                </div>
                <div class="job-name">${escapeHtml(job.name)}</div>
                <div class="job-status">
                    ${hasProfile ? '기술서 완료' : '미작성'}
                </div>
            </div>
        `;
    }
    
    // 직무 클릭 핸들러
    window.handleJobClick = async function(jobId, jobName, hasProfile) {
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
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                showJobDetailModal(result.data);
            } else {
                alert(result.error || '직무 정보를 불러올 수 없습니다.');
            }
        } catch (error) {
            console.error('Error loading job detail:', error);
            alert('직무 정보를 불러오는데 실패했습니다.');
        }
    };
    
    // 직무 상세 모달 표시
    function showJobDetailModal(data) {
        const job = data.job || {};
        const profile = data.profile;
        
        elements.modalTitle.textContent = job.name || '직무 상세 정보';
        
        let content = `
            <div class="job-detail">
                <div class="detail-section">
                    <h3><i class="fas fa-info-circle"></i> 기본 정보</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>직군</label>
                            <span>${escapeHtml(job.category || '-')}</span>
                        </div>
                        <div class="info-item">
                            <label>직종</label>
                            <span>${escapeHtml(job.job_type || '-')}</span>
                        </div>
                        <div class="info-item">
                            <label>직무명</label>
                            <span>${escapeHtml(job.name || '-')}</span>
                        </div>
                    </div>
                </div>
        `;
        
        if (profile) {
            content += `
                <div class="detail-section">
                    <h3><i class="fas fa-tasks"></i> 핵심 역할 및 책임</h3>
                    <div class="detail-text">
                        ${escapeHtml(profile.role_responsibility || '내용이 없습니다.')}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3><i class="fas fa-check-circle"></i> 자격 요건</h3>
                    <div class="detail-text">
                        ${escapeHtml(profile.qualification || '내용이 없습니다.')}
                    </div>
                </div>
                
                <div class="detail-section">
                    <h3><i class="fas fa-star"></i> 필요 역량</h3>
                    <div class="skills-wrapper">
                        <div class="skill-group">
                            <h4>기본 역량</h4>
                            <div class="skill-tags">
                                ${(profile.basic_skills || []).map(skill => 
                                    `<span class="skill-tag">${escapeHtml(skill)}</span>`
                                ).join('')}
                            </div>
                        </div>
                        <div class="skill-group">
                            <h4>우대 역량</h4>
                            <div class="skill-tags">
                                ${(profile.applied_skills || []).map(skill => 
                                    `<span class="skill-tag preferred">${escapeHtml(skill)}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="detail-actions">
                    <a href="/job-profiles/edit/${job.id}/" class="btn btn-primary">
                        <i class="fas fa-edit"></i> 편집하기
                    </a>
                </div>
            `;
        } else {
            content += `
                <div class="no-profile">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>직무기술서가 아직 작성되지 않았습니다.</p>
                    <a href="/job-profiles/edit/${job.id}/" class="btn btn-primary">
                        <i class="fas fa-plus"></i> 작성하기
                    </a>
                </div>
            `;
        }
        
        content += '</div>';
        elements.modalContent.innerHTML = content;
        
        elements.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    // 모달 닫기
    window.closeModal = function() {
        elements.modal.classList.remove('show');
        document.body.style.overflow = '';
    };
    
    // 검색 핸들러
    function handleSearch(e) {
        state.searchTerm = e.target.value.toLowerCase();
        applyFilters();
    }
    
    // 필터 핸들러
    function handleFilter(e) {
        elements.filterBtns.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        state.currentFilter = e.target.dataset.filter;
        applyFilters();
    }
    
    // 필터 적용
    function applyFilters() {
        // 그룹 필터
        document.querySelectorAll('.group-container').forEach(container => {
            const group = container.dataset.group;
            if (state.currentFilter === 'all' || state.currentFilter === group) {
                container.style.display = 'block';
            } else {
                container.style.display = 'none';
            }
        });
        
        // 검색 필터
        document.querySelectorAll('.job-card').forEach(card => {
            const jobName = card.dataset.jobName || '';
            if (state.searchTerm && !jobName.includes(state.searchTerm)) {
                card.style.display = 'none';
            } else {
                card.style.display = 'block';
            }
        });
        
        // 빈 카테고리 숨기기
        document.querySelectorAll('.category-block').forEach(category => {
            const visibleCards = category.querySelectorAll('.job-card:not([style*="display: none"])');
            category.style.display = visibleCards.length > 0 ? 'block' : 'none';
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
            'headphones': 'fa-headphones',
            'user-shield': 'fa-user-shield'
        };
        return iconMap[iconName] || 'fa-folder';
    }
    
    function countJobs(jobTypes) {
        if (!jobTypes) return 0;
        return Object.values(jobTypes).reduce((sum, jobs) => {
            return sum + (Array.isArray(jobs) ? jobs.length : 0);
        }, 0);
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
    
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return (text || '').toString().replace(/[&<>"']/g, m => map[m]);
    }
    
    function showError(message) {
        const errorHtml = `
            <div class="error-state">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${escapeHtml(message)}</p>
                <button onclick="location.reload()" class="btn btn-primary">
                    <i class="fas fa-redo"></i> 다시 시도
                </button>
            </div>
        `;
        elements.nonPlContent.innerHTML = errorHtml;
        elements.plContent.innerHTML = '';
    }
})();'''

def create_minimal_views():
    """최소한의 뷰만 포함"""
    return '''from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count, Prefetch
import json

from .models import JobCategory, JobType, JobRole, JobProfile

class JobTreeMapView(TemplateView):
    """직무 체계도 TreeMap 뷰 (유일한 뷰)"""
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
    """TreeMap 데이터 API"""
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
        
        # 카테고리 조회 (최적화된 쿼리)
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

def create_minimal_urls():
    """최소한의 URL만 포함"""
    return '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # TreeMap 메인 뷰 (유일한 뷰)
    path('', views.JobTreeMapView.as_view(), name='list'),
    
    # API 엔드포인트
    path('api/tree-map-data/', views.job_tree_map_data_api, name='tree_map_data'),
    path('api/job-detail-modal/<uuid:job_role_id>/', views.job_detail_modal_api, name='job_detail_modal'),
    
    # 편집
    path('edit/<uuid:job_role_id>/', views.job_profile_edit_view, name='edit'),
]'''

def update_base_template():
    """base_simple.html에서 job_profiles 관련 메뉴 업데이트"""
    base_template_path = os.path.join(BASE_DIR, 'templates/base_simple.html')
    
    if os.path.exists(base_template_path):
        with open(base_template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기존 job_profiles 관련 링크 제거 및 단일 링크로 교체
        # 정규식으로 모든 job_profiles 관련 메뉴 찾기
        patterns = [
            r'<a[^>]*href="[^"]*job_profiles[^"]*"[^>]*>.*?</a>',
            r'<li[^>]*>.*?job_profiles.*?</li>',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 새로운 단일 메뉴 추가 (필요한 경우)
        # 이 부분은 템플릿 구조에 따라 조정 필요
        
        with open(base_template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("base_simple.html 업데이트됨")

def create_cleanup_script():
    """레거시 파일 정리 스크립트"""
    return '''#!/bin/bash
# 레거시 파일 삭제 스크립트

echo "레거시 파일 삭제 중..."

# 템플릿 파일 삭제
rm -f job_profiles/templates/job_profiles/job_tree.html
rm -f job_profiles/templates/job_profiles/job_tree_map.html
rm -f job_profiles/templates/job_profiles/job_tree_map_simple.html
rm -f job_profiles/templates/job_profiles/job_profile_list.html
rm -f job_profiles/templates/job_profiles/job_profile_detail.html

# 레거시 static 파일 삭제
rm -f static/js/JobProfileTreeMap.js
rm -f static/css/JobProfileTreeMap.css
rm -f static/js/job_tree_unified.js
rm -f static/css/job_tree_unified.css

# 레거시 Python 파일 백업
mv job_profiles/views_old.py job_profiles/views_old.py.bak 2>/dev/null
mv job_profiles/urls_old.py job_profiles/urls_old.py.bak 2>/dev/null

echo "레거시 파일 삭제 완료!"'''

def main():
    print("="*60)
    print("OK금융그룹 직무체계도 TreeMap UI 완전 단일화")
    print("="*60)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    # 백업 디렉토리 생성
    backup_dir = os.path.join(BASE_DIR, f'backup_treemap_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. 기존 파일 백업
    print("\n1. 기존 파일 백업 중...")
    files_to_backup = [
        'job_profiles/templates/job_profiles/',
        'job_profiles/views.py',
        'job_profiles/urls.py',
        'static/js/job_tree*',
        'static/css/job_tree*',
        'static/js/JobProfile*',
        'static/css/JobProfile*'
    ]
    
    for pattern in files_to_backup:
        if '*' in pattern:
            import glob
            for file_path in glob.glob(os.path.join(BASE_DIR, pattern)):
                if os.path.exists(file_path):
                    rel_path = os.path.relpath(file_path, BASE_DIR)
                    backup_path = os.path.join(backup_dir, rel_path)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copy2(file_path, backup_path)
                    print(f"  백업: {rel_path}")
        else:
            full_path = os.path.join(BASE_DIR, pattern)
            if os.path.exists(full_path):
                if os.path.isdir(full_path):
                    shutil.copytree(full_path, os.path.join(backup_dir, pattern))
                else:
                    backup_path = os.path.join(backup_dir, pattern)
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    shutil.copy2(full_path, backup_path)
                print(f"  백업: {pattern}")
    
    # 2. 새 파일 생성
    print("\n2. 새 파일 생성 중...")
    
    # 템플릿 디렉토리 확인 및 생성
    template_dir = os.path.join(BASE_DIR, 'job_profiles/templates/job_profiles')
    os.makedirs(template_dir, exist_ok=True)
    
    # job_treemap.html 생성
    template_path = os.path.join(template_dir, 'job_treemap.html')
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_treemap_template())
    print(f"  생성: job_treemap.html")
    
    # CSS 생성
    css_dir = os.path.join(BASE_DIR, 'static/css')
    os.makedirs(css_dir, exist_ok=True)
    css_path = os.path.join(css_dir, 'job_treemap_unified.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_css())
    print(f"  생성: job_treemap_unified.css")
    
    # JavaScript 생성
    js_dir = os.path.join(BASE_DIR, 'static/js')
    os.makedirs(js_dir, exist_ok=True)
    js_path = os.path.join(js_dir, 'job_treemap_unified.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(create_unified_js())
    print(f"  생성: job_treemap_unified.js")
    
    # Views 생성
    views_path = os.path.join(BASE_DIR, 'job_profiles/views.py')
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(create_minimal_views())
    print(f"  생성: views.py (최소 구성)")
    
    # URLs 생성
    urls_path = os.path.join(BASE_DIR, 'job_profiles/urls.py')
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(create_minimal_urls())
    print(f"  생성: urls.py (최소 구성)")
    
    # 3. 레거시 파일 삭제
    print("\n3. 레거시 파일 삭제 중...")
    legacy_files = [
        'job_profiles/templates/job_profiles/job_tree.html',
        'job_profiles/templates/job_profiles/job_tree_map.html',
        'job_profiles/templates/job_profiles/job_tree_map_simple.html',
        'job_profiles/templates/job_profiles/job_profile_list.html',
        'job_profiles/templates/job_profiles/job_profile_detail.html',
        'static/js/JobProfileTreeMap.js',
        'static/css/JobProfileTreeMap.css',
        'static/js/job_tree_unified.js',
        'static/css/job_tree_unified.css'
    ]
    
    for file_path in legacy_files:
        full_path = os.path.join(BASE_DIR, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"  삭제: {file_path}")
    
    # 4. 정리 스크립트 생성
    cleanup_script_path = os.path.join(BASE_DIR, 'cleanup_legacy.sh')
    with open(cleanup_script_path, 'w', encoding='utf-8') as f:
        f.write(create_cleanup_script())
    os.chmod(cleanup_script_path, 0o755)
    print(f"\n  생성: cleanup_legacy.sh")
    
    # 5. base 템플릿 업데이트
    print("\n4. 메뉴 및 링크 업데이트 중...")
    update_base_template()
    
    print("\n" + "="*60)
    print("완료! 다음 단계:")
    print("="*60)
    print("1. python manage.py collectstatic --noinput")
    print("2. python manage.py runserver")
    print("3. http://localhost:8000/job-profiles/ 접속")
    print("\n주의사항:")
    print("- 모든 레거시 뷰와 템플릿이 제거되었습니다")
    print("- /job-profiles/ 경로만 사용 가능합니다")
    print("- 백업 파일은 다음 위치에 저장됨:", backup_dir)
    print("-"*60)

if __name__ == '__main__':
    main()