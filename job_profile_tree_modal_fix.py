#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OK Financial Group HRIS - Job Profile Tree Map Simplification & Auth Removal
============================================================================

1. 트리맵을 심플버전으로 단일화
2. 직무 클릭시 모달 팝업 및 전체화면 상세보기 구현
3. UI 디자인 일관성 (컬러, 폰트, 여백) 개선
4. 로그인/인증 기능 완전 제거
5. 모든 화면을 반응형/심플/모던 디자인으로 통일

Author: UX Designer + React/Django Frontend + Security Architect
Date: 2025-01-27
"""

import os
import json
from pathlib import Path
from datetime import datetime

class JobProfileTreeModalFix:
    """직무 트리맵 단일화 및 인증 제거 시스템"""
    
    def __init__(self):
        self.base_path = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # OK금융그룹 브랜드 컬러
        self.color_scheme = {
            "primary": {
                "IT/디지털": "#3B82F6",
                "경영지원": "#8B5CF6", 
                "금융": "#10B981",
                "영업": "#F59E0B",
                "고객서비스": "#EF4444"
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
        """모든 파일 생성"""
        print("OK금융그룹 직무 트리맵 단일화 및 인증 제거 시작...\n")
        
        # 1. 단순화된 트리맵 뷰 생성
        self._generate_simplified_tree_view()
        
        # 2. 모달 및 상세화면 컴포넌트 생성
        self._generate_modal_components()
        
        # 3. 인증 제거된 뷰 생성
        self._generate_no_auth_views()
        
        # 4. URL 패턴 재설계
        self._generate_new_urls()
        
        # 5. 일관된 CSS 스타일 생성
        self._generate_unified_styles()
        
        # 6. 베이스 템플릿 개선
        self._generate_base_template()
        
        # 7. 설정 파일 업데이트
        self._generate_settings_update()
        
        print("\n[완료] 모든 파일 생성 완료!")
        print(f"[정보] 생성된 디렉토리: job_profile_tree_modal_fix/")
        
    def _generate_simplified_tree_view(self):
        """단순화된 트리맵 뷰 생성"""
        template_content = '''{% extends "base_modern.html" %}
{% load static %}

{% block title %}직무 체계도 - OK금융그룹{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="stylesheet" href="{% static 'css/job_tree_unified.css' %}">
{% endblock %}

{% block content %}
<div class="job-tree-container">
    <!-- 페이지 헤더 -->
    <header class="page-header">
        <h1 class="page-title">
            <i class="fas fa-sitemap"></i>
            OK금융그룹 직무 체계도
        </h1>
        <p class="page-subtitle">직군 → 직종 → 직무 구조를 한눈에 확인하세요</p>
    </header>

    <!-- 통계 카드 -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{{ total_categories }}</div>
            <div class="stat-label">직군</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ total_job_types }}</div>
            <div class="stat-label">직종</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ total_job_roles }}</div>
            <div class="stat-label">직무</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ total_profiles }}</div>
            <div class="stat-label">직무기술서</div>
        </div>
    </div>

    <!-- 필터 바 -->
    <div class="filter-bar">
        <div class="search-box">
            <i class="fas fa-search"></i>
            <input type="text" id="jobSearch" placeholder="직무 검색...">
        </div>
        <div class="filter-chips">
            <button class="chip active" data-filter="all">전체</button>
            <button class="chip" data-filter="with-profile">기술서 있음</button>
            <button class="chip" data-filter="no-profile">기술서 없음</button>
        </div>
    </div>

    <!-- 트리맵 메인 컨텐츠 -->
    <div class="tree-map-content">
        <!-- Non-PL 직군 -->
        <section class="job-group non-pl-group">
            <h2 class="group-title">
                <span class="group-badge non-pl">Non-PL</span>
                일반 직군
            </h2>
            <div id="non-pl-content" class="group-content">
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </section>

        <!-- PL 직군 -->
        <section class="job-group pl-group">
            <h2 class="group-title">
                <span class="group-badge pl">PL</span>
                고객서비스 직군
            </h2>
            <div id="pl-content" class="group-content">
                <div class="loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>데이터를 불러오는 중...</p>
                </div>
            </div>
        </section>
    </div>
</div>

<!-- 직무 상세 모달 -->
<div id="jobDetailModal" class="modal" role="dialog" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle" class="modal-title"></h2>
                <div class="modal-actions">
                    <button class="btn-icon" onclick="toggleFullscreen()" title="전체화면">
                        <i class="fas fa-expand"></i>
                    </button>
                    <button class="btn-icon" onclick="closeModal()" title="닫기">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div id="modalBody" class="modal-body">
                <!-- 동적 콘텐츠 -->
            </div>
            <div class="modal-footer">
                <button class="btn btn-primary" onclick="editJobProfile()">
                    <i class="fas fa-edit"></i> 편집
                </button>
                <button class="btn btn-danger" onclick="deleteJobProfile()">
                    <i class="fas fa-trash"></i> 삭제
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">닫기</button>
            </div>
        </div>
    </div>
</div>

<!-- 전체화면 상세보기 -->
<div id="fullscreenDetail" class="fullscreen-detail" style="display: none;">
    <div class="fullscreen-header">
        <button class="btn-back" onclick="exitFullscreen()">
            <i class="fas fa-arrow-left"></i> 돌아가기
        </button>
        <h1 id="fullscreenTitle"></h1>
        <div class="fullscreen-actions">
            <button class="btn btn-primary" onclick="editJobProfile()">
                <i class="fas fa-edit"></i> 편집
            </button>
            <button class="btn btn-danger" onclick="deleteJobProfile()">
                <i class="fas fa-trash"></i> 삭제
            </button>
        </div>
    </div>
    <div id="fullscreenBody" class="fullscreen-body">
        <!-- 동적 콘텐츠 -->
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/job_tree_unified.js' %}"></script>
{% endblock %}'''

        # JavaScript 파일 생성
        js_content = '''// 전역 변수
let currentJobId = null;
let jobData = {};
let isFullscreen = false;

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    loadTreeData();
    initializeEventListeners();
});

// 이벤트 리스너 초기화
function initializeEventListeners() {
    // 검색 기능
    document.getElementById('jobSearch').addEventListener('input', handleSearch);
    
    // 필터 칩
    document.querySelectorAll('.filter-chips .chip').forEach(chip => {
        chip.addEventListener('click', handleFilter);
    });
    
    // 모달 외부 클릭시 닫기
    document.getElementById('jobDetailModal').addEventListener('click', function(e) {
        if (e.target === this) closeModal();
    });
    
    // ESC 키로 모달/전체화면 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (isFullscreen) exitFullscreen();
            else closeModal();
        }
    });
}

// 트리 데이터 로드
async function loadTreeData() {
    try {
        const response = await fetch('/api/job-tree-data/');
        const result = await response.json();
        
        if (result.success) {
            jobData = result.data;
            renderTreeMap(result.data);
        } else {
            showError('데이터를 불러올 수 없습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('서버 연결에 실패했습니다.');
    }
}

// 트리맵 렌더링
function renderTreeMap(data) {
    // Non-PL 렌더링
    const nonPlContent = document.getElementById('non-pl-content');
    nonPlContent.innerHTML = renderGroup(data['Non-PL'], 'Non-PL');
    
    // PL 렌더링
    const plContent = document.getElementById('pl-content');
    plContent.innerHTML = renderGroup(data['PL'], 'PL');
    
    // 애니메이션 적용
    animateCards();
}

// 그룹 렌더링
function renderGroup(groupData, groupType) {
    if (!groupData || Object.keys(groupData).length === 0) {
        return '<div class="empty-state">데이터가 없습니다.</div>';
    }
    
    let html = '';
    
    for (const [categoryName, categoryData] of Object.entries(groupData)) {
        html += `
            <div class="category-section" data-category="${categoryName}">
                <div class="category-header">
                    <div class="category-icon" style="background: ${getCategoryGradient(categoryName)}">
                        <i class="fas ${getIcon(categoryData.icon)}"></i>
                    </div>
                    <div class="category-info">
                        <h3 class="category-title">${categoryName}</h3>
                        <span class="category-stats">
                            ${Object.keys(categoryData.jobs).length}개 직종 · 
                            ${countJobs(categoryData.jobs)}개 직무
                        </span>
                    </div>
                </div>
                
                <div class="job-types-container">
                    ${renderJobTypes(categoryData.jobs, categoryName)}
                </div>
            </div>
        `;
    }
    
    return html;
}

// 직종별 직무 렌더링
function renderJobTypes(jobTypes, categoryName) {
    let html = '';
    
    for (const [jobTypeName, jobs] of Object.entries(jobTypes)) {
        html += `
            <div class="job-type-section">
                <h4 class="job-type-title" style="border-color: ${getCategoryColor(categoryName)}">
                    ${jobTypeName}
                    <span class="job-count">${jobs.length}</span>
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
             onclick="showJobDetail('${job.id}')"
             style="--card-color: ${color}">
            <div class="job-card-icon">
                <i class="fas ${hasProfile ? 'fa-file-alt' : 'fa-file'}"></i>
            </div>
            <h5 class="job-card-title">${job.name}</h5>
            <span class="job-card-status">
                ${hasProfile ? '✓ 작성완료' : '미작성'}
            </span>
        </div>
    `;
}

// 직무 상세 표시
async function showJobDetail(jobId) {
    currentJobId = jobId;
    
    try {
        const response = await fetch(`/api/job-detail/${jobId}/`);
        const result = await response.json();
        
        if (result.success) {
            displayJobDetail(result.data);
        } else {
            alert('직무 정보를 불러올 수 없습니다.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 오류가 발생했습니다.');
    }
}

// 직무 상세 정보 표시
function displayJobDetail(data) {
    const { job, profile } = data;
    
    // 모달 제목 설정
    document.getElementById('modalTitle').textContent = job.name;
    document.getElementById('fullscreenTitle').textContent = job.name;
    
    // 상세 내용 HTML 생성
    const detailHTML = `
        <div class="job-detail-container">
            <!-- 기본 정보 -->
            <section class="detail-section">
                <h3 class="section-title">
                    <i class="fas fa-info-circle"></i> 기본 정보
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
                        <label>경로</label>
                        <span>${job.full_path}</span>
                    </div>
                </div>
                ${job.description ? `
                    <div class="description">
                        <label>설명</label>
                        <p>${job.description}</p>
                    </div>
                ` : ''}
            </section>
            
            ${profile ? `
                <!-- 직무기술서 -->
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-tasks"></i> 핵심 역할 및 책임
                    </h3>
                    <div class="content-box">
                        ${formatText(profile.role_responsibility)}
                    </div>
                </section>
                
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-check-circle"></i> 자격 요건
                    </h3>
                    <div class="content-box">
                        ${formatText(profile.qualification)}
                    </div>
                </section>
                
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-star"></i> 역량
                    </h3>
                    <div class="skills-container">
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
                
                ${profile.growth_path ? `
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-route"></i> 성장 경로
                    </h3>
                    <div class="content-box">
                        ${formatText(profile.growth_path)}
                    </div>
                </section>
                ` : ''}
                
                ${profile.related_certifications && profile.related_certifications.length > 0 ? `
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-certificate"></i> 관련 자격증
                    </h3>
                    <div class="skill-tags">
                        ${profile.related_certifications.map(cert => 
                            `<span class="skill-tag cert">${cert}</span>`
                        ).join('')}
                    </div>
                </section>
                ` : ''}
            ` : `
                <div class="empty-profile">
                    <i class="fas fa-file-circle-plus fa-3x"></i>
                    <p>아직 작성된 직무기술서가 없습니다.</p>
                    <button class="btn btn-primary" onclick="createJobProfile('${job.id}')">
                        <i class="fas fa-plus"></i> 직무기술서 작성
                    </button>
                </div>
            `}
            
            ${data.related_jobs && data.related_jobs.length > 0 ? `
                <section class="detail-section">
                    <h3 class="section-title">
                        <i class="fas fa-link"></i> 관련 직무
                    </h3>
                    <div class="related-jobs">
                        ${data.related_jobs.map(related => `
                            <button class="related-job-chip ${related.has_profile ? 'has-profile' : ''}"
                                    onclick="showJobDetail('${related.id}')">
                                ${related.name}
                                ${related.has_profile ? '<i class="fas fa-check-circle"></i>' : ''}
                            </button>
                        `).join('')}
                    </div>
                </section>
            ` : ''}
        </div>
    `;
    
    // 모달과 전체화면 모두에 내용 설정
    document.getElementById('modalBody').innerHTML = detailHTML;
    document.getElementById('fullscreenBody').innerHTML = detailHTML;
    
    // 모달 표시
    openModal();
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
    return Object.values(jobTypes).reduce((total, jobs) => total + jobs.length, 0);
}

function formatText(text) {
    if (!text) return '';
    return text.split('\\n').map(line => `<p>${line}</p>`).join('');
}

// 모달 제어
function openModal() {
    const modal = document.getElementById('jobDetailModal');
    modal.style.display = 'block';
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
}

function closeModal() {
    const modal = document.getElementById('jobDetailModal');
    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
    currentJobId = null;
}

// 전체화면 제어
function toggleFullscreen() {
    if (!isFullscreen) {
        closeModal();
        document.getElementById('fullscreenDetail').style.display = 'flex';
        document.body.classList.add('fullscreen-open');
        isFullscreen = true;
    } else {
        exitFullscreen();
    }
}

function exitFullscreen() {
    document.getElementById('fullscreenDetail').style.display = 'none';
    document.body.classList.remove('fullscreen-open');
    isFullscreen = false;
}

// 편집/삭제 기능
function editJobProfile() {
    if (currentJobId) {
        window.location.href = `/job-profiles/${currentJobId}/edit/`;
    }
}

function deleteJobProfile() {
    if (currentJobId && confirm('정말로 이 직무기술서를 삭제하시겠습니까?')) {
        // 삭제 API 호출
        fetch(`/api/job-profiles/${currentJobId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('삭제되었습니다.');
                closeModal();
                loadTreeData(); // 데이터 새로고침
            } else {
                alert('삭제에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('서버 오류가 발생했습니다.');
        });
    }
}

function createJobProfile(jobId) {
    window.location.href = `/job-profiles/create/?job_role=${jobId}`;
}

// 검색 기능
function handleSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    
    document.querySelectorAll('.job-card').forEach(card => {
        const jobName = card.querySelector('.job-card-title').textContent.toLowerCase();
        const shouldShow = jobName.includes(searchTerm);
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 직종 숨기기
    document.querySelectorAll('.job-type-section').forEach(section => {
        const visibleCards = section.querySelectorAll('.job-card:not([style*="display: none"])');
        section.style.display = visibleCards.length > 0 ? '' : 'none';
    });
    
    // 빈 카테고리 숨기기
    document.querySelectorAll('.category-section').forEach(section => {
        const visibleTypes = section.querySelectorAll('.job-type-section:not([style*="display: none"])');
        section.style.display = visibleTypes.length > 0 ? '' : 'none';
    });
}

// 필터 기능
function handleFilter(e) {
    const chip = e.target;
    const filter = chip.dataset.filter;
    
    // 활성 칩 변경
    document.querySelectorAll('.filter-chips .chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    
    // 필터 적용
    document.querySelectorAll('.job-card').forEach(card => {
        const hasProfile = card.dataset.hasProfile === 'true';
        let shouldShow = true;
        
        if (filter === 'with-profile') shouldShow = hasProfile;
        else if (filter === 'no-profile') shouldShow = !hasProfile;
        
        card.style.display = shouldShow ? '' : 'none';
    });
    
    // 빈 섹션 처리
    handleSearch({ target: document.getElementById('jobSearch') });
}

// 카드 애니메이션
function animateCards() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.job-card').forEach(card => {
        observer.observe(card);
    });
}

// 에러 표시
function showError(message) {
    const errorHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <button class="btn btn-primary" onclick="loadTreeData()">
                <i class="fas fa-redo"></i> 다시 시도
            </button>
        </div>
    `;
    
    document.getElementById('non-pl-content').innerHTML = errorHTML;
    document.getElementById('pl-content').innerHTML = '';
}'''

        # 파일 저장
        os.makedirs("job_profile_tree_modal_fix/templates", exist_ok=True)
        os.makedirs("job_profile_tree_modal_fix/static/js", exist_ok=True)
        
        with open("job_profile_tree_modal_fix/templates/job_tree_unified.html", "w", encoding="utf-8") as f:
            f.write(template_content)
            
        with open("job_profile_tree_modal_fix/static/js/job_tree_unified.js", "w", encoding="utf-8") as f:
            f.write(js_content)
            
        print("[완료] 단순화된 트리맵 뷰 생성 완료")

    def _generate_modal_components(self):
        """모달 및 상세화면 컴포넌트 생성"""
        
        # 직무 편집 폼 템플릿
        edit_template = '''{% extends "base_modern.html" %}
{% load static %}

{% block title %}직무기술서 편집 - {{ job.name }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/job_tree_unified.css' %}">
{% endblock %}

{% block content %}
<div class="edit-container">
    <header class="edit-header">
        <button class="btn-back" onclick="history.back()">
            <i class="fas fa-arrow-left"></i> 돌아가기
        </button>
        <h1 class="edit-title">
            <i class="fas fa-edit"></i>
            {{ job.name }} 직무기술서 편집
        </h1>
    </header>

    <form id="editForm" method="post" class="edit-form">
        <!-- 기본 정보 (읽기 전용) -->
        <section class="form-section">
            <h2 class="section-title">기본 정보</h2>
            <div class="info-grid readonly">
                <div class="info-item">
                    <label>직군</label>
                    <span>{{ job.category }}</span>
                </div>
                <div class="info-item">
                    <label>직종</label>
                    <span>{{ job.job_type }}</span>
                </div>
                <div class="info-item">
                    <label>직무명</label>
                    <span>{{ job.name }}</span>
                </div>
            </div>
        </section>

        <!-- 직무기술서 내용 -->
        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-tasks"></i> 핵심 역할 및 책임
            </h2>
            <textarea name="role_responsibility" 
                      class="form-textarea" 
                      rows="8" 
                      required
                      placeholder="이 직무의 핵심 역할과 책임을 구체적으로 작성해주세요.">{{ profile.role_responsibility }}</textarea>
        </section>

        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-check-circle"></i> 자격 요건
            </h2>
            <textarea name="qualification" 
                      class="form-textarea" 
                      rows="6" 
                      required
                      placeholder="필수 자격 요건을 작성해주세요.">{{ profile.qualification }}</textarea>
        </section>

        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-star"></i> 역량
            </h2>
            
            <div class="form-group">
                <label>기본 역량</label>
                <input type="text" 
                       name="basic_skills" 
                       class="form-input tags-input" 
                       value="{{ profile.basic_skills|join:', ' }}"
                       placeholder="예: Python, 데이터 분석, 프로젝트 관리 (쉼표로 구분)">
                <small class="form-help">쉼표(,)로 구분하여 입력해주세요.</small>
            </div>
            
            <div class="form-group">
                <label>우대 역량</label>
                <input type="text" 
                       name="applied_skills" 
                       class="form-input tags-input" 
                       value="{{ profile.applied_skills|join:', ' }}"
                       placeholder="예: AWS, Docker, 영어 회화 (쉼표로 구분)">
            </div>
        </section>

        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-route"></i> 성장 경로
            </h2>
            <textarea name="growth_path" 
                      class="form-textarea" 
                      rows="5"
                      placeholder="이 직무에서의 경력 개발 및 성장 경로를 작성해주세요.">{{ profile.growth_path }}</textarea>
        </section>

        <section class="form-section">
            <h2 class="section-title">
                <i class="fas fa-certificate"></i> 관련 자격증
            </h2>
            <input type="text" 
                   name="related_certifications" 
                   class="form-input tags-input" 
                   value="{{ profile.related_certifications|join:', ' }}"
                   placeholder="예: 정보처리기사, CPA, PMP (쉼표로 구분)">
        </section>

        <!-- 액션 버튼 -->
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-lg">
                <i class="fas fa-save"></i> 저장
            </button>
            <button type="button" class="btn btn-secondary btn-lg" onclick="history.back()">
                취소
            </button>
        </div>
    </form>
</div>

<script>
// 폼 제출 처리
document.getElementById('editForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = {};
    
    // FormData를 JSON으로 변환
    for (let [key, value] of formData.entries()) {
        if (key.includes('skills') || key === 'related_certifications') {
            // 태그 입력 필드는 배열로 변환
            data[key] = value.split(',').map(v => v.trim()).filter(v => v);
        } else {
            data[key] = value;
        }
    }
    
    try {
        const response = await fetch('{{ request.path }}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('저장되었습니다.');
            window.location.href = '/job-profiles/';
        } else {
            alert('저장에 실패했습니다: ' + (result.error || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('서버 오류가 발생했습니다.');
    }
});

// 태그 입력 미리보기
document.querySelectorAll('.tags-input').forEach(input => {
    input.addEventListener('input', function() {
        // 태그 미리보기 로직 추가 가능
    });
});
</script>
{% endblock %}'''

        with open("job_profile_tree_modal_fix/templates/job_profile_edit.html", "w", encoding="utf-8") as f:
            f.write(edit_template)
            
        print("[완료] 모달 및 편집 컴포넌트 생성 완료")

    def _generate_no_auth_views(self):
        """인증 제거된 뷰 생성"""
        
        views_content = '''from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Prefetch, Q
import json

from job_profiles.models import JobCategory, JobType, JobRole, JobProfile


class JobTreeView(TemplateView):
    """직무 트리맵 메인 뷰 (인증 불필요)"""
    template_name = 'job_tree_unified.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 통계 정보
        context.update({
            'total_categories': JobCategory.objects.filter(is_active=True).count(),
            'total_job_types': JobType.objects.filter(is_active=True).count(),
            'total_job_roles': JobRole.objects.filter(is_active=True).count(),
            'total_profiles': JobProfile.objects.filter(is_active=True).count(),
        })
        
        return context


def job_tree_data_api(request):
    """트리맵 데이터 API (인증 불필요)"""
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
                        has_profile = bool(job_role.profile)
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
        
        return JsonResponse({
            'success': True,
            'data': tree_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_detail_api(request, job_role_id):
    """직무 상세 정보 API (인증 불필요)"""
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
        
        # 관련 직무 조회
        related_jobs = JobRole.objects.filter(
            job_type=job_role.job_type,
            is_active=True
        ).exclude(id=job_role.id).select_related('profile')[:5]
        
        # 응답 데이터 구성
        data = {
            'job': {
                'id': str(job_role.id),
                'name': job_role.name,
                'description': job_role.description,
                'full_path': job_role.full_path,
                'category': job_role.job_type.category.name,
                'job_type': job_role.job_type.name,
            },
            'profile': None,
            'related_jobs': []
        }
        
        # 직무기술서 정보
        try:
            profile = job_role.profile
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
        
        # 관련 직무 정보
        for related in related_jobs:
            try:
                has_profile = bool(related.profile)
            except JobProfile.DoesNotExist:
                has_profile = False
                
            data['related_jobs'].append({
                'id': str(related.id),
                'name': related.name,
                'has_profile': has_profile
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except JobRole.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '직무를 찾을 수 없습니다.'
        }, status=404)


def job_profile_edit(request, job_role_id):
    """직무기술서 편집 (인증 불필요)"""
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    try:
        profile = job_role.profile
    except JobProfile.DoesNotExist:
        # 프로필이 없으면 새로 생성
        profile = JobProfile(job_role=job_role)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 데이터 업데이트
            profile.role_responsibility = data.get('role_responsibility', '')
            profile.qualification = data.get('qualification', '')
            profile.basic_skills = data.get('basic_skills', [])
            profile.applied_skills = data.get('applied_skills', [])
            profile.growth_path = data.get('growth_path', '')
            profile.related_certifications = data.get('related_certifications', [])
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 편집 페이지 렌더링
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': profile.role_responsibility if profile.id else '',
            'qualification': profile.qualification if profile.id else '',
            'basic_skills': profile.basic_skills if profile.id else [],
            'applied_skills': profile.applied_skills if profile.id else [],
            'growth_path': profile.growth_path if profile.id else '',
            'related_certifications': profile.related_certifications if profile.id else [],
        }
    }
    
    return render(request, 'job_profile_edit.html', context)


@csrf_exempt
def job_profile_delete_api(request, job_role_id):
    """직무기술서 삭제 API (인증 불필요)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST 메서드만 허용됩니다.'}, status=405)
    
    try:
        job_role = get_object_or_404(JobRole, id=job_role_id)
        
        # 직무기술서가 있으면 삭제
        try:
            profile = job_role.profile
            profile.delete()
            message = '직무기술서가 삭제되었습니다.'
        except JobProfile.DoesNotExist:
            message = '삭제할 직무기술서가 없습니다.'
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def job_profile_create(request):
    """직무기술서 생성 (인증 불필요)"""
    job_role_id = request.GET.get('job_role')
    
    if not job_role_id:
        return redirect('/')
    
    job_role = get_object_or_404(JobRole, id=job_role_id, is_active=True)
    
    # 이미 프로필이 있으면 편집 페이지로 리다이렉트
    try:
        profile = job_role.profile
        return redirect('job_profile_edit', job_role_id=job_role_id)
    except JobProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 새 프로필 생성
            profile = JobProfile(
                job_role=job_role,
                role_responsibility=data.get('role_responsibility', ''),
                qualification=data.get('qualification', ''),
                basic_skills=data.get('basic_skills', []),
                applied_skills=data.get('applied_skills', []),
                growth_path=data.get('growth_path', ''),
                related_certifications=data.get('related_certifications', [])
            )
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': '직무기술서가 생성되었습니다.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # GET 요청시 생성 페이지 렌더링 (편집 템플릿 재사용)
    context = {
        'job': {
            'id': str(job_role.id),
            'name': job_role.name,
            'category': job_role.job_type.category.name,
            'job_type': job_role.job_type.name,
        },
        'profile': {
            'role_responsibility': '',
            'qualification': '',
            'basic_skills': [],
            'applied_skills': [],
            'growth_path': '',
            'related_certifications': [],
        },
        'is_create': True
    }
    
    return render(request, 'job_profile_edit.html', context)
'''

        with open("job_profile_tree_modal_fix/views.py", "w", encoding="utf-8") as f:
            f.write(views_content)
            
        print("[완료] 인증 제거된 뷰 생성 완료")

    def _generate_new_urls(self):
        """URL 패턴 재설계"""
        
        urls_content = '''from django.urls import path
from . import views

app_name = 'job_profiles'

urlpatterns = [
    # 메인 트리맵 (루트 경로)
    path('', views.JobTreeView.as_view(), name='tree'),
    
    # API 엔드포인트
    path('api/job-tree-data/', views.job_tree_data_api, name='tree_data_api'),
    path('api/job-detail/<uuid:job_role_id>/', views.job_detail_api, name='job_detail_api'),
    path('api/job-profiles/<uuid:job_role_id>/delete/', views.job_profile_delete_api, name='delete_api'),
    
    # 편집/생성 페이지
    path('job-profiles/<uuid:job_role_id>/edit/', views.job_profile_edit, name='edit'),
    path('job-profiles/create/', views.job_profile_create, name='create'),
]
'''

        # 프로젝트 루트 URL 설정
        root_urls_content = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from job_profiles.views import JobTreeView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 루트 경로를 직무 트리맵으로 설정
    path('', JobTreeView.as_view(), name='home'),
    
    # 앱별 URL
    path('', include('job_profiles.urls')),
    
    # 기타 앱들 (필요시 추가)
    # path('employees/', include('employees.urls')),
    # path('evaluations/', include('evaluations.urls')),
]

# 정적 파일 및 미디어 파일 서빙 (개발 환경)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
'''

        with open("job_profile_tree_modal_fix/urls.py", "w", encoding="utf-8") as f:
            f.write(urls_content)
            
        with open("job_profile_tree_modal_fix/root_urls.py", "w", encoding="utf-8") as f:
            f.write(root_urls_content)
            
        print("[완료] URL 패턴 재설계 완료")

    def _generate_unified_styles(self):
        """일관된 CSS 스타일 생성"""
        
        css_content = '''/* OK Financial Group - Unified Design System */

/* 변수 정의 */
:root {
    /* 브랜드 컬러 */
    --color-it: #3B82F6;
    --color-management: #8B5CF6;
    --color-finance: #10B981;
    --color-sales: #F59E0B;
    --color-service: #EF4444;
    
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
    
    /* 그라디언트 */
    --gradient-it: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
    --gradient-management: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
    --gradient-finance: linear-gradient(135deg, #10B981 0%, #34D399 100%);
    --gradient-sales: linear-gradient(135deg, #F59E0B 0%, #FCD34D 100%);
    --gradient-service: linear-gradient(135deg, #EF4444 0%, #F87171 100%);
    
    /* 타이포그래피 */
    --font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-size-xs: 0.75rem;
    --font-size-sm: 0.875rem;
    --font-size-base: 1rem;
    --font-size-lg: 1.125rem;
    --font-size-xl: 1.25rem;
    --font-size-2xl: 1.5rem;
    --font-size-3xl: 1.875rem;
    --font-size-4xl: 2.25rem;
    
    /* 여백 */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    --spacing-3xl: 4rem;
    
    /* 둥글기 */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;
    --radius-full: 9999px;
    
    /* 그림자 */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

/* 글로벌 스타일 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    color: var(--neutral-800);
    background-color: var(--neutral-50);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* 컨테이너 */
.job-tree-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-xl);
}

/* 페이지 헤더 */
.page-header {
    text-align: center;
    margin-bottom: var(--spacing-3xl);
}

.page-title {
    font-size: var(--font-size-4xl);
    font-weight: 800;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
}

.page-subtitle {
    font-size: var(--font-size-lg);
    color: var(--neutral-500);
}

/* 통계 카드 */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}

.stat-card {
    background: white;
    padding: var(--spacing-xl);
    border-radius: var(--radius-xl);
    border: 1px solid var(--neutral-200);
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.stat-value {
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: var(--font-size-sm);
    color: var(--neutral-500);
    font-weight: 500;
}

/* 필터 바 */
.filter-bar {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
    flex-wrap: wrap;
}

.search-box {
    flex: 1;
    min-width: 300px;
    position: relative;
}

.search-box i {
    position: absolute;
    left: var(--spacing-md);
    top: 50%;
    transform: translateY(-50%);
    color: var(--neutral-400);
}

.search-box input {
    width: 100%;
    padding: var(--spacing-md) var(--spacing-md) var(--spacing-md) var(--spacing-3xl);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-lg);
    font-size: var(--font-size-base);
    transition: all 0.3s ease;
}

.search-box input:focus {
    outline: none;
    border-color: var(--color-it);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-chips {
    display: flex;
    gap: var(--spacing-sm);
}

.chip {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-full);
    background: white;
    color: var(--neutral-600);
    font-size: var(--font-size-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.chip:hover {
    border-color: var(--color-it);
    color: var(--color-it);
}

.chip.active {
    background: var(--color-it);
    border-color: var(--color-it);
    color: white;
}

/* 트리맵 컨텐츠 */
.tree-map-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: var(--spacing-xl);
}

.job-group {
    background: white;
    border-radius: var(--radius-2xl);
    padding: var(--spacing-2xl);
    border: 2px solid var(--neutral-200);
}

.non-pl-group {
    border-color: var(--color-it);
    border-opacity: 0.2;
}

.pl-group {
    border-color: var(--color-service);
    border-opacity: 0.2;
}

.group-title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-xl);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.group-badge {
    padding: var(--spacing-xs) var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);
    font-weight: 600;
}

.group-badge.non-pl {
    background: var(--gradient-it);
    color: white;
}

.group-badge.pl {
    background: var(--gradient-service);
    color: white;
}

/* 카테고리 섹션 */
.category-section {
    margin-bottom: var(--spacing-2xl);
    padding: var(--spacing-xl);
    background: var(--neutral-50);
    border-radius: var(--radius-xl);
    border: 1px solid var(--neutral-200);
}

.category-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.category-icon {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    box-shadow: var(--shadow-md);
}

.category-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--neutral-900);
}

.category-stats {
    font-size: var(--font-size-sm);
    color: var(--neutral-500);
}

/* 직종 섹션 */
.job-type-section {
    margin-bottom: var(--spacing-lg);
}

.job-type-title {
    font-size: var(--font-size-lg);
    font-weight: 600;
    margin-bottom: var(--spacing-md);
    padding-left: var(--spacing-md);
    border-left: 4px solid;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.job-count {
    padding: var(--spacing-xs) var(--spacing-sm);
    background: white;
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);
    font-weight: 500;
}

/* 직무 그리드 */
.jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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

.job-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
    border-color: var(--card-color);
}

.job-card.has-profile {
    border-color: var(--card-color);
    opacity: 1;
}

.job-card.no-profile {
    opacity: 0.7;
}

.job-card-icon {
    font-size: 28px;
    margin-bottom: var(--spacing-sm);
    color: var(--card-color);
}

.job-card-title {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--neutral-800);
    margin-bottom: var(--spacing-xs);
}

.job-card-status {
    font-size: var(--font-size-xs);
    color: var(--neutral-500);
}

.job-card.has-profile .job-card-status {
    color: var(--color-finance);
    font-weight: 500;
}

/* 모달 */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    backdrop-filter: blur(4px);
}

.modal-dialog {
    position: relative;
    max-width: 900px;
    margin: 50px auto;
    animation: slideIn 0.3s ease;
}

.modal-content {
    background: white;
    border-radius: var(--radius-2xl);
    box-shadow: var(--shadow-xl);
    max-height: calc(100vh - 100px);
    display: flex;
    flex-direction: column;
}

.modal-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--neutral-200);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.modal-title {
    font-size: var(--font-size-2xl);
    font-weight: 700;
    color: var(--neutral-900);
}

.modal-actions {
    display: flex;
    gap: var(--spacing-sm);
}

.modal-body {
    padding: var(--spacing-xl);
    overflow-y: auto;
    flex: 1;
}

.modal-footer {
    padding: var(--spacing-xl);
    border-top: 1px solid var(--neutral-200);
    display: flex;
    gap: var(--spacing-md);
    justify-content: flex-end;
}

/* 버튼 */
.btn {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--radius-lg);
    font-size: var(--font-size-base);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
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

.btn-danger {
    background: var(--color-service);
    color: white;
}

.btn-danger:hover {
    background: #dc2626;
}

.btn-icon {
    width: 40px;
    height: 40px;
    padding: 0;
    border: none;
    border-radius: var(--radius-lg);
    background: var(--neutral-100);
    color: var(--neutral-600);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.btn-icon:hover {
    background: var(--neutral-200);
    color: var(--neutral-800);
}

/* 전체화면 */
.fullscreen-detail {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: white;
    z-index: 2000;
    display: flex;
    flex-direction: column;
}

.fullscreen-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--neutral-200);
    display: flex;
    align-items: center;
    gap: var(--spacing-xl);
}

.fullscreen-body {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-2xl);
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}

/* 직무 상세 */
.job-detail-container {
    max-width: 800px;
    margin: 0 auto;
}

.detail-section {
    margin-bottom: var(--spacing-2xl);
}

.section-title {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--neutral-900);
    margin-bottom: var(--spacing-lg);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
}

.info-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.info-item label {
    font-size: var(--font-size-sm);
    color: var(--neutral-500);
    font-weight: 500;
}

.info-item span {
    font-size: var(--font-size-base);
    color: var(--neutral-800);
}

.content-box {
    padding: var(--spacing-lg);
    background: var(--neutral-50);
    border-radius: var(--radius-lg);
    border: 1px solid var(--neutral-200);
}

.content-box p {
    margin-bottom: var(--spacing-md);
}

.content-box p:last-child {
    margin-bottom: 0;
}

/* 스킬 태그 */
.skills-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
}

.skill-group h4 {
    font-size: var(--font-size-base);
    font-weight: 600;
    color: var(--neutral-700);
    margin-bottom: var(--spacing-md);
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.skill-tag {
    padding: var(--spacing-xs) var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);
    font-weight: 500;
}

.skill-tag.basic {
    background: var(--color-it);
    color: white;
}

.skill-tag.preferred {
    background: var(--color-management);
    color: white;
}

.skill-tag.cert {
    background: var(--color-finance);
    color: white;
}

/* 관련 직무 */
.related-jobs {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-sm);
}

.related-job-chip {
    padding: var(--spacing-sm) var(--spacing-lg);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-full);
    background: white;
    color: var(--neutral-700);
    font-size: var(--font-size-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.related-job-chip:hover {
    border-color: var(--color-it);
    color: var(--color-it);
}

.related-job-chip.has-profile {
    border-color: var(--color-finance);
    color: var(--color-finance);
}

/* 편집 폼 */
.edit-container {
    max-width: 900px;
    margin: 0 auto;
    padding: var(--spacing-2xl);
}

.edit-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
}

.edit-title {
    font-size: var(--font-size-3xl);
    font-weight: 700;
    color: var(--neutral-900);
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.edit-form {
    background: white;
    border-radius: var(--radius-2xl);
    padding: var(--spacing-2xl);
    box-shadow: var(--shadow-lg);
}

.form-section {
    margin-bottom: var(--spacing-2xl);
}

.form-section:last-child {
    margin-bottom: 0;
}

.form-group {
    margin-bottom: var(--spacing-lg);
}

.form-group label {
    display: block;
    font-size: var(--font-size-base);
    font-weight: 500;
    color: var(--neutral-700);
    margin-bottom: var(--spacing-sm);
}

.form-input,
.form-textarea {
    width: 100%;
    padding: var(--spacing-md);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-lg);
    font-size: var(--font-size-base);
    font-family: var(--font-family);
    transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--color-it);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
    resize: vertical;
    min-height: 120px;
}

.form-help {
    font-size: var(--font-size-sm);
    color: var(--neutral-500);
    margin-top: var(--spacing-xs);
}

.form-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    margin-top: var(--spacing-2xl);
    padding-top: var(--spacing-2xl);
    border-top: 1px solid var(--neutral-200);
}

/* 로딩 상태 */
.loading {
    text-align: center;
    padding: var(--spacing-3xl);
    color: var(--neutral-500);
}

.loading i {
    font-size: 48px;
    margin-bottom: var(--spacing-lg);
    color: var(--color-it);
}

/* 빈 상태 */
.empty-state,
.empty-profile {
    text-align: center;
    padding: var(--spacing-3xl);
    color: var(--neutral-500);
}

.empty-profile i {
    font-size: 64px;
    margin-bottom: var(--spacing-lg);
    color: var(--neutral-300);
}

/* 에러 상태 */
.error-state {
    text-align: center;
    padding: var(--spacing-3xl);
    color: var(--color-service);
}

.error-state i {
    font-size: 48px;
    margin-bottom: var(--spacing-lg);
}

/* 애니메이션 */
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.animate-in {
    animation: fadeIn 0.5s ease;
}

/* 반응형 */
@media (max-width: 1024px) {
    .tree-map-content {
        grid-template-columns: 1fr;
    }
    
    .skills-container {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .job-tree-container {
        padding: var(--spacing-lg);
    }
    
    .page-title {
        font-size: var(--font-size-3xl);
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .filter-bar {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-box {
        min-width: 100%;
    }
    
    .jobs-grid {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }
    
    .modal-dialog {
        margin: 20px;
    }
    
    .form-actions {
        flex-direction: column;
    }
    
    .btn {
        width: 100%;
        justify-content: center;
    }
}

@media (max-width: 480px) {
    .page-title {
        font-size: var(--font-size-2xl);
        flex-direction: column;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .jobs-grid {
        grid-template-columns: 1fr;
    }
    
    .group-title {
        font-size: var(--font-size-xl);
    }
    
    .category-header {
        flex-direction: column;
        text-align: center;
    }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
    :root {
        --neutral-50: #0f172a;
        --neutral-100: #1e293b;
        --neutral-200: #334155;
        --neutral-300: #475569;
        --neutral-400: #64748b;
        --neutral-500: #94a3b8;
        --neutral-600: #cbd5e1;
        --neutral-700: #e2e8f0;
        --neutral-800: #f1f5f9;
        --neutral-900: #f8fafc;
    }
    
    body {
        background-color: var(--neutral-50);
        color: var(--neutral-800);
    }
    
    .job-card,
    .stat-card,
    .modal-content,
    .edit-form {
        background: var(--neutral-100);
    }
    
    .category-section,
    .content-box {
        background: var(--neutral-200);
    }
}

/* 프린트 스타일 */
@media print {
    .filter-bar,
    .modal-actions,
    .form-actions,
    .btn-back {
        display: none !important;
    }
    
    body {
        background: white;
    }
    
    .job-tree-container {
        max-width: 100%;
        padding: 0;
    }
    
    .job-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}

/* 접근성 */
.job-card:focus,
.btn:focus,
.chip:focus {
    outline: 3px solid var(--color-it);
    outline-offset: 2px;
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border-width: 0;
}

/* 유틸리티 클래스 */
.text-center {
    text-align: center;
}

.text-left {
    text-align: left;
}

.text-right {
    text-align: right;
}

.mt-1 { margin-top: var(--spacing-xs); }
.mt-2 { margin-top: var(--spacing-sm); }
.mt-3 { margin-top: var(--spacing-md); }
.mt-4 { margin-top: var(--spacing-lg); }
.mt-5 { margin-top: var(--spacing-xl); }

.mb-1 { margin-bottom: var(--spacing-xs); }
.mb-2 { margin-bottom: var(--spacing-sm); }
.mb-3 { margin-bottom: var(--spacing-md); }
.mb-4 { margin-bottom: var(--spacing-lg); }
.mb-5 { margin-bottom: var(--spacing-xl); }

.flex {
    display: flex;
}

.items-center {
    align-items: center;
}

.justify-center {
    justify-content: center;
}

.justify-between {
    justify-content: space-between;
}

.gap-1 { gap: var(--spacing-xs); }
.gap-2 { gap: var(--spacing-sm); }
.gap-3 { gap: var(--spacing-md); }
.gap-4 { gap: var(--spacing-lg); }
.gap-5 { gap: var(--spacing-xl); }

/* Body 클래스 */
body.modal-open,
body.fullscreen-open {
    overflow: hidden;
}'''

        os.makedirs("job_profile_tree_modal_fix/static/css", exist_ok=True)
        
        with open("job_profile_tree_modal_fix/static/css/job_tree_unified.css", "w", encoding="utf-8") as f:
            f.write(css_content)
            
        print("[완료] 일관된 CSS 스타일 생성 완료")

    def _generate_base_template(self):
        """베이스 템플릿 개선"""
        
        base_template = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="OK금융그룹 인사관리 시스템">
    <title>{% block title %}OK금융그룹 HRIS{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="{% static 'images/favicon.png' %}">
    
    <!-- 폰트 -->
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.8/dist/web/static/pretendard.css" />
    
    <!-- 기본 CSS -->
    <link rel="stylesheet" href="{% static 'css/normalize.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- 심플 헤더 (로그인 없음) -->
    <header class="main-header">
        <div class="header-container">
            <div class="header-logo">
                <a href="/">
                    <img src="{% static 'images/logo.png' %}" alt="OK금융그룹" height="40">
                </a>
            </div>
            <nav class="header-nav">
                <a href="/" class="nav-link active">
                    <i class="fas fa-sitemap"></i> 직무 체계도
                </a>
                <!-- 필요시 다른 메뉴 추가 -->
            </nav>
        </div>
    </header>

    <!-- 메인 컨텐츠 -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>

    <!-- 푸터 -->
    <footer class="main-footer">
        <div class="footer-container">
            <p>&copy; 2025 OK금융그룹. All rights reserved.</p>
        </div>
    </footer>

    <!-- 기본 JavaScript -->
    {% block extra_js %}{% endblock %}
    
    <!-- 글로벌 스타일 -->
    <style>
        /* 헤더 스타일 */
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
        
        .header-nav {
            display: flex;
            gap: 2rem;
        }
        
        .nav-link {
            color: #6b7280;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .nav-link:hover,
        .nav-link.active {
            color: #3B82F6;
        }
        
        /* 메인 컨텐츠 */
        .main-content {
            min-height: calc(100vh - 120px);
        }
        
        /* 푸터 */
        .main-footer {
            background: #f8fafc;
            border-top: 1px solid #e5e7eb;
            padding: 2rem;
            text-align: center;
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        /* 반응형 */
        @media (max-width: 768px) {
            .header-container {
                padding: 1rem;
            }
            
            .header-nav {
                display: none;
            }
        }
    </style>
</body>
</html>'''

        with open("job_profile_tree_modal_fix/templates/base_modern.html", "w", encoding="utf-8") as f:
            f.write(base_template)
            
        print("[완료] 베이스 템플릿 개선 완료")

    def _generate_settings_update(self):
        """설정 파일 업데이트"""
        
        settings_update = '''# settings.py 업데이트 내용

# 인증 관련 설정 제거/수정
# LOGIN_URL = '/login/'  # 제거
# LOGIN_REDIRECT_URL = '/'  # 제거
# LOGOUT_REDIRECT_URL = '/'  # 제거

# 미들웨어에서 인증 관련 제거 (선택사항)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',  # 필요시 제거
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 정적 파일 설정
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',  # 필요시 제거
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# INSTALLED_APPS에서 불필요한 앱 제거 (선택사항)
INSTALLED_APPS = [
    'django.contrib.admin',
    # 'django.contrib.auth',  # 필요시 제거
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 로컬 앱
    'job_profiles',
    # 다른 앱들...
]
'''

        # 마이그레이션 가이드
        migration_guide = '''# 마이그레이션 가이드

## 1. 기존 로그인 기능 제거

### 1.1 URL 패턴 수정
```python
# ehr_system/urls.py

from django.contrib import admin
from django.urls import path, include
from job_profiles.views import JobTreeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', JobTreeView.as_view(), name='home'),  # 루트를 직무 트리맵으로
    path('', include('job_profiles.urls')),
    
    # 로그인 관련 URL 제거
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

### 1.2 뷰에서 @login_required 데코레이터 제거
```python
# 모든 뷰에서 @login_required 제거
# from django.contrib.auth.decorators import login_required  # 제거

def some_view(request):  # @login_required 제거
    # 뷰 로직
    pass
```

### 1.3 템플릿에서 로그인 체크 제거
```html
<!-- 기존 -->
{% if user.is_authenticated %}
    <!-- 로그인한 사용자 -->
{% else %}
    <!-- 로그인하지 않은 사용자 -->
{% endif %}

<!-- 변경 후 -->
<!-- 모든 사용자가 접근 가능하므로 조건문 제거 -->
```

## 2. 데이터베이스 마이그레이션

```bash
# 새로운 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate

# 정적 파일 수집
python manage.py collectstatic
```

## 3. 서버 재시작

```bash
# 개발 서버 재시작
python manage.py runserver
```

## 4. 확인사항

1. 루트 URL(/)이 직무 트리맵으로 연결되는지 확인
2. 모든 페이지가 로그인 없이 접근 가능한지 확인
3. 직무 상세 모달이 정상 작동하는지 확인
4. 편집/삭제 기능이 정상 작동하는지 확인
'''

        with open("job_profile_tree_modal_fix/settings_update.py", "w", encoding="utf-8") as f:
            f.write(settings_update)
            
        with open("job_profile_tree_modal_fix/MIGRATION_GUIDE.md", "w", encoding="utf-8") as f:
            f.write(migration_guide)
            
        # README 생성
        readme_content = '''# OK금융그룹 직무 트리맵 단일화 및 인증 제거

## 개요

OK금융그룹 HRIS 시스템의 직무 트리맵을 심플 버전으로 단일화하고, 로그인 기능을 완전히 제거하여 접근성을 개선한 버전입니다.

## 주요 변경사항

### 1. 트리맵 단일화
- React 버전 제거, 순수 JavaScript 버전으로 통일
- 직관적인 카드형 UI
- 빠른 로딩 속도

### 2. 모달/전체화면 상세보기
- 직무 클릭시 모달 팝업으로 상세 정보 표시
- 전체화면 모드 지원
- 편집/삭제 기능 통합

### 3. UI 일관성 개선
- OK금융그룹 브랜드 컬러 시스템
- 통일된 폰트 (Pretendard)
- 일관된 여백과 둥글기
- 다크모드 지원

### 4. 로그인 기능 제거
- 모든 페이지 공개 접근 가능
- 인증 미들웨어 제거
- 루트 경로를 직무 트리맵으로 변경

### 5. 반응형 디자인
- 모바일, 태블릿, 데스크톱 완벽 지원
- 터치 제스처 지원
- 프린트 최적화

## 기술 스택

- **Frontend**: Vanilla JavaScript, CSS3
- **Backend**: Django 4.x
- **Icons**: Font Awesome 6.x
- **Font**: Pretendard

## 설치 방법

1. 파일 복사
```bash
cp -r job_profile_tree_modal_fix/* /path/to/your/project/
```

2. 설정 업데이트
- `settings.py` 파일 수정 (settings_update.py 참고)
- URL 패턴 변경 (root_urls.py 참고)

3. 마이그레이션
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

4. 서버 실행
```bash
python manage.py runserver
```

## 사용 방법

1. **메인 화면**: 브라우저에서 `http://localhost:8000/` 접속
2. **직무 검색**: 상단 검색창에서 직무명 검색
3. **필터링**: 기술서 있음/없음 필터 사용
4. **상세보기**: 직무 카드 클릭
5. **편집**: 모달에서 편집 버튼 클릭
6. **전체화면**: 모달에서 전체화면 버튼 클릭

## 디렉토리 구조

```
job_profile_tree_modal_fix/
├── templates/
│   ├── base_modern.html          # 모던 베이스 템플릿
│   ├── job_tree_unified.html     # 통합 트리맵 템플릿
│   └── job_profile_edit.html     # 직무기술서 편집 템플릿
├── static/
│   ├── css/
│   │   └── job_tree_unified.css  # 통합 스타일시트
│   └── js/
│       └── job_tree_unified.js   # 통합 JavaScript
├── views.py                       # 인증 제거된 뷰
├── urls.py                        # 앱 URL 패턴
├── root_urls.py                   # 프로젝트 URL 패턴
├── settings_update.py             # 설정 파일 업데이트 가이드
└── MIGRATION_GUIDE.md             # 마이그레이션 가이드
```

## 브라우저 지원

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari 14+
- Chrome for Android 90+

## 라이선스

© 2025 OK금융그룹. All rights reserved.
'''

        with open("job_profile_tree_modal_fix/README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
            
        print("[완료] 설정 파일 업데이트 가이드 생성 완료")

# 실행
if __name__ == "__main__":
    fixer = JobProfileTreeModalFix()
    fixer.generate_all()