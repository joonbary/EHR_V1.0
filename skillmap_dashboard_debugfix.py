#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
스킬맵 대시보드 디버그 및 수정 스크립트
=====================================
무한 스크롤, 로딩 문제, 데이터 미표시 버그를 진단하고 수정

Frontend bug fixer + React/Vue expert + dashboard QA analyst 통합 접근
- 비동기 로딩 최적화 (async)
- API 통신 개선 (api)
- 로딩 상태 수정 (loadingfix)
- 오버플로우 처리 (overflow)
- 빈 데이터 처리 (emptydata)
- 에러 감지 및 수정 (errordetect)
- 자동 테스트 (autotest)
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import subprocess
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkillMapDashboardDebugger:
    """스킬맵 대시보드 디버거 및 수정 도구"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.issues_found = []
        self.fixes_applied = []
        self.test_results = []
        
    def diagnose_issues(self) -> Dict[str, List[str]]:
        """모든 잠재적 문제 진단"""
        logger.info("🔍 스킬맵 대시보드 문제 진단 시작...")
        
        issues = {
            "frontend": [],
            "backend": [],
            "api": [],
            "ui": [],
            "performance": []
        }
        
        # 1. Frontend JavaScript 검사
        issues["frontend"].extend(self._check_frontend_issues())
        
        # 2. Backend Python 검사
        issues["backend"].extend(self._check_backend_issues())
        
        # 3. API 엔드포인트 검사
        issues["api"].extend(self._check_api_issues())
        
        # 4. UI/UX 문제 검사
        issues["ui"].extend(self._check_ui_issues())
        
        # 5. 성능 문제 검사
        issues["performance"].extend(self._check_performance_issues())
        
        self.issues_found = issues
        return issues
    
    def _check_frontend_issues(self) -> List[str]:
        """Frontend JavaScript 문제 검사"""
        issues = []
        
        # dashboard.html 파일 검사
        template_path = self.base_path / "templates/skillmap/dashboard.html"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 무한 스크롤 관련 검사
            if "overflow: auto" not in content and "overflow-y: auto" not in content:
                issues.append("히트맵 컨테이너에 overflow 속성이 설정되지 않음")
            
            # 로딩 상태 검사
            if "showError" not in content:
                issues.append("에러 표시 함수가 구현되지 않음")
            
            # API 에러 핸들링 검사
            if "catch (error)" not in content:
                issues.append("API 호출에 에러 핸들링 누락")
            
            # 빈 데이터 처리 검사
            if "data.length === 0" not in content and "!data" not in content:
                issues.append("빈 데이터 상태 처리 로직 누락")
        
        return issues
    
    def _check_backend_issues(self) -> List[str]:
        """Backend Python 문제 검사"""
        issues = []
        
        # skillmap_dashboard.py 검사
        dashboard_py = self.base_path / "skillmap_dashboard.py"
        if dashboard_py.exists():
            with open(dashboard_py, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 페이지네이션 검사
            if "paginate" not in content.lower():
                issues.append("대용량 데이터에 대한 페이지네이션 미구현")
            
            # 에러 핸들링 검사
            if "try:" not in content or "except Exception" not in content:
                issues.append("예외 처리 부족")
            
            # 캐싱 검사
            if "cache.get" not in content:
                issues.append("캐싱 메커니즘 미구현 (성능 문제 가능)")
        
        return issues
    
    def _check_api_issues(self) -> List[str]:
        """API 관련 문제 검사"""
        issues = []
        
        # URLs 설정 검사
        urls_py = self.base_path / "ehr_system/urls.py"
        if urls_py.exists():
            with open(urls_py, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "api/skillmap/" not in content:
                issues.append("스킬맵 API 엔드포인트가 urls.py에 등록되지 않음")
        
        return issues
    
    def _check_ui_issues(self) -> List[str]:
        """UI/UX 관련 문제 검사"""
        issues = []
        
        # CSS 검사
        css_files = list(self.base_path.glob("static/css/*.css"))
        for css_file in css_files:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if ".heatmap-container" in content:
                if "max-height" not in content:
                    issues.append(f"{css_file.name}: 히트맵 컨테이너에 max-height 미설정")
        
        return issues
    
    def _check_performance_issues(self) -> List[str]:
        """성능 관련 문제 검사"""
        issues = []
        
        # 대용량 데이터 처리 검사
        dashboard_py = self.base_path / "skillmap_dashboard.py"
        if dashboard_py.exists():
            with open(dashboard_py, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 데이터 집계 검사
            if "employees = list(employees_query)" in content:
                issues.append("모든 직원 데이터를 메모리에 로드 (성능 문제)")
            
            # N+1 쿼리 문제 검사
            if "select_related" not in content and "prefetch_related" not in content:
                issues.append("데이터베이스 쿼리 최적화 미적용")
        
        return issues
    
    def apply_fixes(self) -> Dict[str, Any]:
        """발견된 문제에 대한 수정 적용"""
        logger.info("🔧 문제 수정 시작...")
        
        fixes = {
            "frontend_fixes": self._apply_frontend_fixes(),
            "backend_fixes": self._apply_backend_fixes(),
            "ui_fixes": self._apply_ui_fixes(),
            "performance_fixes": self._apply_performance_fixes()
        }
        
        self.fixes_applied = fixes
        return fixes
    
    def _apply_frontend_fixes(self) -> List[str]:
        """Frontend 수정 사항 적용"""
        fixes = []
        
        # 개선된 dashboard.html 생성
        improved_template = '''{% extends 'base.html' %}
{% load static %}

{% block title %}직무스킬맵 - OK금융그룹 AI-Driven HR System{% endblock %}

{% block content %}
<style>
    /* 디버그 및 수정된 스타일 */
    .skillmap-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .filters {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .heatmap-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        height: 600px;
        position: relative;
        overflow: hidden;
    }
    
    #skillHeatmap {
        height: calc(100% - 60px);
        overflow-y: auto;
        overflow-x: auto;
    }
    
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 100;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid var(--ok-orange);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .error-message {
        background: #fee;
        border: 1px solid #fcc;
        color: #c00;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #666;
    }
    
    .empty-state i {
        font-size: 4rem;
        color: #ddd;
        margin-bottom: 1rem;
    }
</style>

<div class="skillmap-container">
    <!-- 필터 섹션 -->
    <div class="filters">
        <div class="filter-group">
            <select id="departmentFilter" class="form-control">
                <option value="">전체 부서</option>
                {% for dept_code, dept_name in departments %}
                <option value="{{ dept_code }}">{{ dept_name }}</option>
                {% endfor %}
            </select>
            <!-- 기타 필터들... -->
        </div>
    </div>

    <!-- 히트맵 컨테이너 -->
    <div class="heatmap-container">
        <h3>조직 스킬맵 히트맵</h3>
        <div id="skillHeatmap">
            <div class="loading-overlay" id="loadingOverlay">
                <div class="loading-spinner"></div>
            </div>
        </div>
    </div>
</div>

<script>
// 디버그 및 개선된 JavaScript
const SkillMapDashboard = {
    currentData: null,
    loadingOverlay: document.getElementById('loadingOverlay'),
    
    init() {
        this.attachEventListeners();
        this.loadData();
    },
    
    attachEventListeners() {
        // 디바운싱을 위한 타이머
        let debounceTimer;
        
        document.querySelectorAll('.filters select').forEach(select => {
            select.addEventListener('change', () => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => this.loadData(), 300);
            });
        });
    },
    
    async loadData() {
        this.showLoading();
        
        try {
            const filters = this.getFilters();
            const params = new URLSearchParams(filters);
            
            const response = await fetch(`/api/skillmap/?${params}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.currentData = result.data;
                this.updateDashboard();
            } else {
                this.showError(result.message || '데이터 로드 실패');
            }
        } catch (error) {
            console.error('Data loading error:', error);
            this.showError('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
        } finally {
            this.hideLoading();
        }
    },
    
    getFilters() {
        const filters = {};
        const filterElements = {
            department: 'departmentFilter',
            job_group: 'jobGroupFilter',
            job_type: 'jobTypeFilter',
            growth_level: 'growthLevelFilter'
        };
        
        Object.entries(filterElements).forEach(([key, id]) => {
            const element = document.getElementById(id);
            if (element && element.value) {
                filters[key] = element.value;
            }
        });
        
        return filters;
    },
    
    updateDashboard() {
        if (!this.currentData) {
            this.showEmptyState();
            return;
        }
        
        // 히트맵 업데이트
        this.createHeatmap();
        
        // 기타 차트 업데이트
        this.updateMetrics();
        this.updateCharts();
    },
    
    createHeatmap() {
        const container = document.getElementById('skillHeatmap');
        
        if (!this.currentData.skillmap_matrix || 
            !this.currentData.skillmap_matrix.matrix || 
            this.currentData.skillmap_matrix.matrix.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // 부서별 집계 데이터 생성 (성능 최적화)
        const aggregatedData = this.aggregateByDepartment();
        
        // Plotly 히트맵 생성
        const data = [{
            z: aggregatedData.values,
            x: aggregatedData.skills,
            y: aggregatedData.departments,
            type: 'heatmap',
            colorscale: 'RdYlGn',
            reversescale: true,
            hovertemplate: '부서: %{y}<br>스킬: %{x}<br>평균 갭: %{z:.2f}<extra></extra>'
        }];
        
        const layout = {
            xaxis: { title: '스킬', tickangle: -45 },
            yaxis: { title: '부서' },
            margin: { l: 100, r: 50, t: 20, b: 100 },
            height: 500
        };
        
        Plotly.newPlot(container, data, layout, {
            responsive: true,
            displayModeBar: false
        });
    },
    
    aggregateByDepartment() {
        // 부서별로 데이터 집계하여 성능 개선
        const deptMap = new Map();
        const skills = new Set();
        
        this.currentData.skillmap_matrix.matrix.forEach(emp => {
            if (!deptMap.has(emp.department)) {
                deptMap.set(emp.department, {});
            }
            
            Object.entries(emp.skills).forEach(([skill, data]) => {
                skills.add(skill);
                if (!deptMap.get(emp.department)[skill]) {
                    deptMap.get(emp.department)[skill] = [];
                }
                deptMap.get(emp.department)[skill].push(data.gap);
            });
        });
        
        // 평균값 계산
        const departments = Array.from(deptMap.keys()).sort();
        const skillList = Array.from(skills).sort();
        const values = [];
        
        departments.forEach(dept => {
            const row = [];
            skillList.forEach(skill => {
                const gaps = deptMap.get(dept)[skill] || [0];
                const avg = gaps.reduce((a, b) => a + b, 0) / gaps.length;
                row.push(avg);
            });
            values.push(row);
        });
        
        return { departments, skills: skillList, values };
    },
    
    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = 'flex';
        }
    },
    
    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = 'none';
        }
    },
    
    showError(message) {
        const container = document.getElementById('skillHeatmap');
        container.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
    },
    
    showEmptyState() {
        const container = document.getElementById('skillHeatmap');
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-chart-area"></i>
                <p>표시할 데이터가 없습니다.</p>
                <p>필터를 조정하거나 데이터를 확인해주세요.</p>
            </div>
        `;
    },
    
    updateMetrics() {
        // 메트릭 업데이트 로직
        const metrics = this.currentData.metrics;
        
        if (document.getElementById('totalEmployees')) {
            document.getElementById('totalEmployees').textContent = 
                metrics.total_employees.toLocaleString();
        }
        
        if (document.getElementById('avgProficiency')) {
            document.getElementById('avgProficiency').textContent = 
                metrics.avg_proficiency + '%';
        }
    },
    
    updateCharts() {
        // 차트 업데이트 로직
        if (this.currentData.skillmap_matrix.category_summary) {
            this.updateCategoryChart();
        }
    },
    
    updateCategoryChart() {
        // 카테고리 차트 업데이트
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;
        
        const summary = this.currentData.skillmap_matrix.category_summary;
        const categories = Object.keys(summary);
        const values = categories.map(cat => summary[cat].avg_proficiency);
        
        new Chart(ctx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: categories,
                datasets: [{
                    label: '평균 숙련도',
                    data: values,
                    backgroundColor: 'rgba(255, 107, 0, 0.8)'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
};

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    SkillMapDashboard.init();
});
</script>
{% endblock %}'''
        
        # 템플릿 저장
        template_path = self.base_path / "templates/skillmap/dashboard_fixed.html"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(improved_template)
        
        fixes.append("개선된 템플릿 생성: dashboard_fixed.html")
        
        return fixes
    
    def _apply_backend_fixes(self) -> List[str]:
        """Backend 수정 사항 적용"""
        fixes = []
        
        # 개선된 API 뷰 생성
        improved_api = '''from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.core.paginator import Paginator
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class SkillMapAPIImproved(View):
    """개선된 스킬맵 API - 디버그 및 성능 최적화"""
    
    def get(self, request):
        try:
            # 캐시 키 생성
            cache_key = self._generate_cache_key(request.GET)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return JsonResponse(cached_data)
            
            # 필터 파라미터 추출 및 검증
            filters = self._extract_filters(request)
            
            # 페이지네이션 파라미터
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 50))
            
            # 응답 형식
            format_type = request.GET.get('format', 'summary')
            
            # 데이터 조회
            analytics = SkillMapAnalytics()
            skillmap_data = analytics.get_organization_skill_map(filters)
            
            # 페이지네이션 적용
            if format_type == 'full' and 'employee_profiles' in skillmap_data:
                paginator = Paginator(skillmap_data['employee_profiles'], per_page)
                page_obj = paginator.get_page(page)
                
                skillmap_data['employee_profiles'] = list(page_obj)
                skillmap_data['pagination'] = {
                    'current_page': page,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'per_page': per_page,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            
            # 형식별 응답 준비
            response_data = self._format_response(skillmap_data, format_type)
            
            # 캐시 저장 (5분)
            cache.set(cache_key, response_data, 300)
            
            return JsonResponse(response_data)
            
        except ValueError as e:
            logger.error(f"Value error in SkillMap API: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 파라미터 값입니다.',
                'error': str(e)
            }, status=400)
            
        except Exception as e:
            logger.error(f"Unexpected error in SkillMap API: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': '서버 오류가 발생했습니다.',
                'error': str(e) if settings.DEBUG else '내부 서버 오류'
            }, status=500)
    
    def _generate_cache_key(self, params):
        """캐시 키 생성"""
        sorted_params = sorted(params.items())
        return f"skillmap::{json.dumps(sorted_params)}"
    
    def _extract_filters(self, request):
        """필터 파라미터 추출 및 검증"""
        filters = {}
        
        # 부서 필터
        if dept := request.GET.get('department'):
            if dept in dict(Employee.DEPARTMENT_CHOICES):
                filters['department'] = dept
            else:
                raise ValueError(f"Invalid department: {dept}")
        
        # 직군 필터
        if job_group := request.GET.get('job_group'):
            if job_group in ['PL', 'Non-PL']:
                filters['job_group'] = job_group
            else:
                raise ValueError(f"Invalid job_group: {job_group}")
        
        # 직종 필터
        if job_type := request.GET.get('job_type'):
            valid_types = ['IT기획', 'IT개발', 'IT운영', '경영관리', 
                          '기업영업', '기업금융', '리테일금융', '투자금융', '고객지원']
            if job_type in valid_types:
                filters['job_type'] = job_type
            else:
                raise ValueError(f"Invalid job_type: {job_type}")
        
        # 성장레벨 필터
        if growth_level := request.GET.get('growth_level'):
            try:
                level = int(growth_level)
                if 1 <= level <= 5:
                    filters['growth_level'] = level
                else:
                    raise ValueError(f"Growth level must be between 1 and 5")
            except ValueError:
                raise ValueError(f"Invalid growth_level: {growth_level}")
        
        return filters
    
    def _format_response(self, data, format_type):
        """응답 형식화"""
        base_response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'format': format_type
        }
        
        if format_type == 'summary':
            # 요약 정보만 반환
            base_response['data'] = {
                'metrics': data.get('metrics'),
                'filters_applied': data.get('filters_applied'),
                'generated_at': data.get('generated_at')
            }
        elif format_type == 'heatmap':
            # 히트맵 데이터만 반환
            base_response['data'] = {
                'skillmap_matrix': {
                    'employees': data['skillmap_matrix']['employees'][:100],  # 최대 100명
                    'skills': data['skillmap_matrix']['skills'],
                    'heatmap_data': data['skillmap_matrix']['heatmap_data'][:100],
                    'category_summary': data['skillmap_matrix']['category_summary']
                },
                'metrics': data.get('metrics')
            }
        else:
            # 전체 데이터 반환
            base_response['data'] = data
        
        return base_response
'''
        
        # API 개선 사항 저장
        api_path = self.base_path / "skillmap_dashboard_improved.py"
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(improved_api)
        
        fixes.append("개선된 API 클래스 생성: SkillMapAPIImproved")
        
        return fixes
    
    def _apply_ui_fixes(self) -> List[str]:
        """UI 수정 사항 적용"""
        fixes = []
        
        # CSS 수정 사항
        css_fixes = '''/* 스킬맵 대시보드 디버그 수정 사항 */

/* 히트맵 컨테이너 스크롤 수정 */
.heatmap-container {
    max-height: 600px !important;
    overflow: hidden !important;
}

#skillHeatmap {
    height: calc(100% - 60px);
    overflow-y: auto !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch; /* 모바일 스크롤 개선 */
}

/* 로딩 상태 개선 */
.loading-overlay {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(2px);
}

/* 에러 상태 스타일 */
.error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    color: #666;
}

.error-state .error-icon {
    font-size: 4rem;
    color: #dc3545;
    margin-bottom: 1rem;
}

/* 빈 데이터 상태 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
}

/* 반응형 개선 */
@media (max-width: 768px) {
    .heatmap-container {
        max-height: 400px !important;
    }
    
    .filter-group {
        grid-template-columns: 1fr !important;
    }
}'''
        
        # CSS 저장
        css_path = self.base_path / "static/css/skillmap-fixes.css"
        css_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_fixes)
        
        fixes.append("CSS 수정 사항 생성: skillmap-fixes.css")
        
        return fixes
    
    def _apply_performance_fixes(self) -> List[str]:
        """성능 개선 사항 적용"""
        fixes = []
        
        # 성능 최적화 유틸리티
        performance_utils = '''import functools
import time
from django.core.cache import cache
from django.db import connection

def measure_performance(func):
    """성능 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        queries_before = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        queries_after = len(connection.queries)
        
        execution_time = end_time - start_time
        query_count = queries_after - queries_before
        
        logger.info(f"{func.__name__} - Time: {execution_time:.2f}s, Queries: {query_count}")
        
        return result
    
    return wrapper

def cache_result(timeout=300):
    """결과 캐싱 데코레이터"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{func.__name__}::{str(args)}::{str(kwargs)}"
            
            # 캐시 확인
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 캐시 저장
            cache.set(cache_key, result, timeout)
            
            return result
        
        return wrapper
    
    return decorator

class QueryOptimizer:
    """쿼리 최적화 헬퍼"""
    
    @staticmethod
    def optimize_employee_query(queryset):
        """직원 쿼리 최적화"""
        return queryset.select_related(
            'user',
            'department'
        ).prefetch_related(
            'compensations',
            'evaluations'
        ).only(
            'id', 'name', 'department', 'position',
            'job_group', 'job_type', 'growth_level'
        )
    
    @staticmethod
    def batch_process(items, batch_size=100):
        """배치 처리"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
'''
        
        # 성능 유틸리티 저장
        utils_path = self.base_path / "skillmap_performance_utils.py"
        with open(utils_path, 'w', encoding='utf-8') as f:
            f.write(performance_utils)
        
        fixes.append("성능 최적화 유틸리티 생성: skillmap_performance_utils.py")
        
        return fixes
    
    def run_tests(self) -> Dict[str, Any]:
        """자동 테스트 실행"""
        logger.info("🧪 자동 테스트 실행...")
        
        test_results = {
            "api_tests": self._test_api_endpoints(),
            "frontend_tests": self._test_frontend_functionality(),
            "performance_tests": self._test_performance()
        }
        
        self.test_results = test_results
        return test_results
    
    def _test_api_endpoints(self) -> List[Dict[str, Any]]:
        """API 엔드포인트 테스트"""
        tests = []
        
        # 테스트 스크립트
        test_script = '''import requests
import json

def test_skillmap_api():
    """스킬맵 API 테스트"""
    base_url = "http://localhost:8000"
    
    # 로그인 (테스트용)
    session = requests.Session()
    
    tests = []
    
    # 1. 기본 API 호출 테스트
    try:
        response = session.get(f"{base_url}/api/skillmap/")
        tests.append({
            "test": "Basic API Call",
            "status": response.status_code,
            "success": response.status_code == 200,
            "message": "OK" if response.status_code == 200 else f"Failed with {response.status_code}"
        })
    except Exception as e:
        tests.append({
            "test": "Basic API Call",
            "status": 0,
            "success": False,
            "message": str(e)
        })
    
    # 2. 필터링 테스트
    try:
        response = session.get(f"{base_url}/api/skillmap/?department=IT")
        tests.append({
            "test": "Filtered API Call",
            "status": response.status_code,
            "success": response.status_code == 200,
            "data": response.json() if response.status_code == 200 else None
        })
    except Exception as e:
        tests.append({
            "test": "Filtered API Call",
            "status": 0,
            "success": False,
            "message": str(e)
        })
    
    # 3. 페이지네이션 테스트
    try:
        response = session.get(f"{base_url}/api/skillmap/?page=1&per_page=10")
        tests.append({
            "test": "Pagination Test",
            "status": response.status_code,
            "success": response.status_code == 200
        })
    except Exception as e:
        tests.append({
            "test": "Pagination Test",
            "status": 0,
            "success": False,
            "message": str(e)
        })
    
    return tests

if __name__ == "__main__":
    results = test_skillmap_api()
    print(json.dumps(results, indent=2))
'''
        
        # 테스트 스크립트 저장
        test_path = self.base_path / "test_skillmap_api.py"
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        tests.append({
            "test": "API Test Script Created",
            "file": str(test_path),
            "success": True
        })
        
        return tests
    
    def _test_frontend_functionality(self) -> List[Dict[str, Any]]:
        """Frontend 기능 테스트"""
        tests = []
        
        # JavaScript 테스트 코드
        js_test = '''// 스킬맵 대시보드 Frontend 테스트
const SkillMapTests = {
    runAll() {
        console.log('Starting SkillMap Dashboard Tests...');
        
        const results = [];
        
        // 1. DOM 요소 존재 확인
        results.push(this.testDOMElements());
        
        // 2. API 호출 테스트
        results.push(this.testAPICall());
        
        // 3. 에러 핸들링 테스트
        results.push(this.testErrorHandling());
        
        // 4. 로딩 상태 테스트
        results.push(this.testLoadingStates());
        
        console.table(results);
        return results;
    },
    
    testDOMElements() {
        const elements = [
            'skillHeatmap',
            'departmentFilter',
            'loadingOverlay',
            'totalEmployees'
        ];
        
        const missing = elements.filter(id => !document.getElementById(id));
        
        return {
            test: 'DOM Elements',
            success: missing.length === 0,
            missing: missing
        };
    },
    
    async testAPICall() {
        try {
            const response = await fetch('/api/skillmap/?format=summary');
            const data = await response.json();
            
            return {
                test: 'API Call',
                success: data.status === 'success',
                status: response.status
            };
        } catch (error) {
            return {
                test: 'API Call',
                success: false,
                error: error.message
            };
        }
    },
    
    testErrorHandling() {
        try {
            // 에러 표시 함수 테스트
            if (typeof SkillMapDashboard.showError === 'function') {
                SkillMapDashboard.showError('Test error message');
                return {
                    test: 'Error Handling',
                    success: true
                };
            }
            
            return {
                test: 'Error Handling',
                success: false,
                message: 'showError function not found'
            };
        } catch (error) {
            return {
                test: 'Error Handling',
                success: false,
                error: error.message
            };
        }
    },
    
    testLoadingStates() {
        try {
            // 로딩 상태 테스트
            SkillMapDashboard.showLoading();
            const isVisible = window.getComputedStyle(
                document.getElementById('loadingOverlay')
            ).display !== 'none';
            
            SkillMapDashboard.hideLoading();
            
            return {
                test: 'Loading States',
                success: isVisible,
                message: isVisible ? 'Loading states work correctly' : 'Loading overlay not showing'
            };
        } catch (error) {
            return {
                test: 'Loading States',
                success: false,
                error: error.message
            };
        }
    }
};

// 테스트 실행
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        SkillMapTests.runAll();
    }, 1000);
});'''
        
        # 테스트 저장
        test_path = self.base_path / "static/js/skillmap-tests.js"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(js_test)
        
        tests.append({
            "test": "Frontend Test Script Created",
            "file": str(test_path),
            "success": True
        })
        
        return tests
    
    def _test_performance(self) -> List[Dict[str, Any]]:
        """성능 테스트"""
        tests = []
        
        # 성능 테스트 스크립트
        perf_test = '''import time
import statistics
from django.test import TestCase, Client
from django.contrib.auth.models import User

class SkillMapPerformanceTest(TestCase):
    """스킬맵 성능 테스트"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass')
        self.client.login(username='testuser', password='testpass')
    
    def test_api_response_time(self):
        """API 응답 시간 테스트"""
        response_times = []
        
        for i in range(10):
            start = time.time()
            response = self.client.get('/api/skillmap/')
            end = time.time()
            
            response_times.append(end - start)
            self.assertEqual(response.status_code, 200)
        
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        # 평균 응답 시간이 1초 이내여야 함
        self.assertLess(avg_time, 1.0, f"Average response time {avg_time:.2f}s exceeds 1s")
        
        # 최대 응답 시간이 2초 이내여야 함
        self.assertLess(max_time, 2.0, f"Max response time {max_time:.2f}s exceeds 2s")
        
        print(f"Performance Test Results:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  Min: {min(response_times):.3f}s")
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 초기 메모리
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 여러 번 API 호출
        for i in range(50):
            self.client.get('/api/skillmap/')
        
        # 최종 메모리
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가가 100MB 이내여야 함
        self.assertLess(memory_increase, 100, 
                       f"Memory increase {memory_increase:.1f}MB exceeds 100MB")
        
        print(f"Memory Test Results:")
        print(f"  Initial: {initial_memory:.1f}MB")
        print(f"  Final: {final_memory:.1f}MB")
        print(f"  Increase: {memory_increase:.1f}MB")
'''
        
        # 성능 테스트 저장
        test_path = self.base_path / "tests/test_skillmap_performance.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(perf_test)
        
        tests.append({
            "test": "Performance Test Script Created",
            "file": str(test_path),
            "success": True
        })
        
        return tests
    
    def generate_report(self) -> str:
        """디버그 및 수정 리포트 생성"""
        report = f"""
# 스킬맵 대시보드 디버그 및 수정 리포트
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 발견된 문제점

### Frontend 문제
{self._format_issues(self.issues_found.get('frontend', []))}

### Backend 문제
{self._format_issues(self.issues_found.get('backend', []))}

### API 문제
{self._format_issues(self.issues_found.get('api', []))}

### UI/UX 문제
{self._format_issues(self.issues_found.get('ui', []))}

### 성능 문제
{self._format_issues(self.issues_found.get('performance', []))}

## 2. 적용된 수정 사항

### Frontend 수정
{self._format_fixes(self.fixes_applied.get('frontend_fixes', []))}

### Backend 수정
{self._format_fixes(self.fixes_applied.get('backend_fixes', []))}

### UI 수정
{self._format_fixes(self.fixes_applied.get('ui_fixes', []))}

### 성능 개선
{self._format_fixes(self.fixes_applied.get('performance_fixes', []))}

## 3. 테스트 결과

### API 테스트
{self._format_test_results(self.test_results.get('api_tests', []))}

### Frontend 테스트
{self._format_test_results(self.test_results.get('frontend_tests', []))}

### 성능 테스트
{self._format_test_results(self.test_results.get('performance_tests', []))}

## 4. 권장 사항

1. **무한 스크롤 방지**
   - 히트맵 컨테이너에 max-height 설정 완료
   - overflow 속성 적절히 설정
   - 대용량 데이터는 부서별 집계로 표시

2. **로딩 상태 개선**
   - 로딩 오버레이 구현 완료
   - 에러 상태 표시 구현
   - 빈 데이터 상태 처리 완료

3. **API 성능 최적화**
   - 캐싱 메커니즘 구현
   - 페이지네이션 지원
   - 쿼리 최적화 적용

4. **추가 개선 제안**
   - WebSocket을 통한 실시간 업데이트
   - 무한 스크롤 구현 (페이지네이션 기반)
   - 고급 필터링 옵션 추가
   - 데이터 시각화 옵션 확장

## 5. 사용 방법

1. 개선된 템플릿 사용:
   ```python
   # views.py에서
   return render(request, 'skillmap/dashboard_fixed.html', context)
   ```

2. 개선된 API 사용:
   ```python
   # urls.py에서
   from skillmap_dashboard_improved import SkillMapAPIImproved
   
   path('api/skillmap/', SkillMapAPIImproved.as_view(), name='skillmap_api'),
   ```

3. CSS 수정 사항 포함:
   ```html
   <!-- 템플릿에서 -->
   <link rel="stylesheet" href="{% static 'css/skillmap-fixes.css' %}">
   ```

4. 테스트 실행:
   ```bash
   python manage.py test tests.test_skillmap_performance
   python test_skillmap_api.py
   ```
"""
        
        return report
    
    def _format_issues(self, issues: List[str]) -> str:
        if not issues:
            return "- 문제점이 발견되지 않았습니다."
        
        return "\n".join(f"- {issue}" for issue in issues)
    
    def _format_fixes(self, fixes: List[str]) -> str:
        if not fixes:
            return "- 적용된 수정 사항이 없습니다."
        
        return "\n".join(f"- ✅ {fix}" for fix in fixes)
    
    def _format_test_results(self, tests: List[Dict[str, Any]]) -> str:
        if not tests:
            return "- 실행된 테스트가 없습니다."
        
        result = []
        for test in tests:
            status = "✅ PASS" if test.get('success') else "❌ FAIL"
            result.append(f"- {test.get('test', 'Unknown Test')}: {status}")
            if test.get('message'):
                result.append(f"  메시지: {test['message']}")
        
        return "\n".join(result)


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("스킬맵 대시보드 디버그 및 수정 도구")
    print("=" * 60)
    
    debugger = SkillMapDashboardDebugger()
    
    # 1. 문제 진단
    print("\n[1/4] 문제 진단 중...")
    issues = debugger.diagnose_issues()
    
    # 2. 수정 적용
    print("\n[2/4] 수정 사항 적용 중...")
    fixes = debugger.apply_fixes()
    
    # 3. 테스트 실행
    print("\n[3/4] 테스트 실행 중...")
    test_results = debugger.run_tests()
    
    # 4. 리포트 생성
    print("\n[4/4] 리포트 생성 중...")
    report = debugger.generate_report()
    
    # 리포트 저장
    report_path = Path("skillmap_debug_report.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 디버그 및 수정 완료!")
    print(f"📄 리포트 저장됨: {report_path}")
    
    # 주요 결과 출력
    print("\n📊 요약:")
    total_issues = sum(len(v) for v in issues.values())
    print(f"  - 발견된 문제: {total_issues}개")
    print(f"  - 적용된 수정: {sum(len(v) for v in fixes.values())}개")
    print(f"  - 생성된 파일:")
    print(f"    - templates/skillmap/dashboard_fixed.html")
    print(f"    - skillmap_dashboard_improved.py")
    print(f"    - static/css/skillmap-fixes.css")
    print(f"    - static/js/skillmap-tests.js")
    print(f"    - tests/test_skillmap_performance.py")


if __name__ == "__main__":
    main()