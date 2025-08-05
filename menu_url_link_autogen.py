"""
EHR 시스템 미연동 기능 자동 연결 및 신규 페이지 생성 시스템
========================================================

현재 연결되지 않은 주요 기능들을 자동으로 진단하고 UI/URL/메뉴에 통합
"""

import os
import json
from typing import Dict, List, Tuple
from datetime import datetime


class MissingFeatureAnalyzer:
    """미연동 기능 분석기"""
    
    def __init__(self):
        self.missing_features = {}
        self.existing_urls = []
        self.menu_structure = {}
        
    def analyze_missing_features(self):
        """미연동 기능 분석"""
        self.missing_features = {
            'testing_system': {
                'name': '통합 테스트 시스템',
                'description': '시나리오별 QA 및 AI 품질/성능/보안 테스트',
                'files': ['integrated_test_system.py'],
                'url_pattern': 'testing/',
                'menu_category': 'dev_tools',
                'icon': 'flask',
                'priority': 'high',
                'features': [
                    '시나리오별 자동화 테스트',
                    'AI 품질 검증',
                    '성능 벤치마크',
                    '보안 취약점 스캔',
                    '테스트 리포트 생성'
                ]
            },
            'job_matching': {
                'name': '직무 매칭 시스템',
                'description': '직무-인재 자동 매칭 및 추천',
                'files': ['job_profiles/matching_engine.py', 'job_search_recommend_api.py'],
                'url_pattern': 'matching/',
                'menu_category': 'talent_management',
                'icon': 'users-cog',
                'priority': 'high',
                'features': [
                    '직무 요구사항 분석',
                    '인재 역량 매칭',
                    'AI 기반 추천',
                    '매칭 점수 산출'
                ]
            },
            'certification_system': {
                'name': '자격증 관리',
                'description': '자격증 및 성장레벨 관리 시스템',
                'files': ['certifications/', 'certifications/certification_engine.py'],
                'url_pattern': 'certifications/',
                'menu_category': 'talent_management',
                'icon': 'certificate',
                'priority': 'medium',
                'features': [
                    '자격증 등록/관리',
                    '성장레벨 추적',
                    '자격증 검증',
                    '만료 알림'
                ]
            },
            'ess_extensions': {
                'name': 'ESS 확장 기능',
                'description': '개인 성장경로 및 맞춤 추천',
                'files': ['job_profiles/ess_leader_api.py'],
                'url_pattern': 'ess-plus/',
                'menu_category': 'self_service',
                'icon': 'user-plus',
                'priority': 'medium',
                'features': [
                    '개인 성장 경로',
                    '맞춤 교육 추천',
                    '경력 개발 계획',
                    '멘토링 매칭'
                ]
            },
            'analytics_tools': {
                'name': '고급 분석 도구',
                'description': '전략 리포트 및 승진 분석',
                'files': ['leader_strategy_reportgen.py', 'promotions/promotion_analyzer.py'],
                'url_pattern': 'analytics/',
                'menu_category': 'analytics',
                'icon': 'chart-bar',
                'priority': 'medium',
                'features': [
                    '전략 리포트 생성',
                    '승진 후보 분석',
                    '조직 효율성 분석',
                    '인재 리스크 예측'
                ]
            }
        }
        
        return self.missing_features


class URLPatternGenerator:
    """URL 패턴 자동 생성기"""
    
    @staticmethod
    def generate_url_patterns():
        """누락된 기능들의 URL 패턴 생성"""
        url_patterns = """
# === 신규 추가 URL 패턴 ===

# 1. 통합 테스트 시스템
path('testing/', include([
    path('', testing_views.test_dashboard, name='test_dashboard'),
    path('run-scenario/<str:scenario>/', testing_views.run_scenario_test, name='run_scenario_test'),
    path('ai-quality/', testing_views.ai_quality_test, name='ai_quality_test'),
    path('performance/', testing_views.performance_test, name='performance_test'),
    path('security/', testing_views.security_test, name='security_test'),
    path('api/results/', testing_views.test_results_api, name='test_results_api'),
])),

# 2. 직무 매칭 시스템
path('matching/', include([
    path('', matching_views.matching_dashboard, name='matching_dashboard'),
    path('job-search/', matching_views.job_search, name='job_search'),
    path('talent-pool/', matching_views.talent_pool, name='talent_pool'),
    path('recommendations/', matching_views.recommendations, name='matching_recommendations'),
    path('api/match/', matching_views.matching_api, name='matching_api'),
    path('api/recommend/', matching_views.recommend_api, name='recommend_api'),
])),

# 3. 자격증 관리 시스템
path('certifications/', include([
    path('', certification_views.certification_dashboard, name='certification_dashboard'),
    path('my-certifications/', certification_views.my_certifications, name='my_certifications'),
    path('growth-level/', certification_views.growth_level, name='growth_level'),
    path('verification/', certification_views.verification, name='certification_verification'),
    path('api/growth-status/', certification_views.growth_status_api, name='growth_status_api'),
])),

# 4. ESS 확장 기능
path('ess-plus/', include([
    path('', ess_views.ess_plus_dashboard, name='ess_plus_dashboard'),
    path('growth-path/', ess_views.growth_path, name='growth_path'),
    path('training-recommendations/', ess_views.training_recommendations, name='training_recommendations'),
    path('career-planning/', ess_views.career_planning, name='career_planning'),
    path('mentoring/', ess_views.mentoring_match, name='mentoring_match'),
])),

# 5. 고급 분석 도구
path('analytics/', include([
    path('', analytics_views.analytics_dashboard, name='analytics_dashboard'),
    path('strategy-report/', analytics_views.strategy_report, name='strategy_report'),
    path('promotion-analysis/', analytics_views.promotion_analysis, name='promotion_analysis'),
    path('talent-risk/', analytics_views.talent_risk_analysis, name='talent_risk_analysis'),
    path('api/generate-report/', analytics_views.generate_report_api, name='generate_report_api'),
])),
"""
        return url_patterns


class ViewFunctionGenerator:
    """뷰 함수 자동 생성기"""
    
    @staticmethod
    def generate_testing_views():
        """테스트 시스템 뷰 함수"""
        return '''
# testing_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .integrated_test_system import IntegratedTestEngine, ScenarioTestSuite, AIQualityTestSuite
import json

@login_required
@user_passes_test(lambda u: u.is_staff)
def test_dashboard(request):
    """통합 테스트 대시보드"""
    context = {
        'title': '통합 테스트 시스템',
        'scenarios': [
            {'id': 'employee_lifecycle', 'name': '직원 생명주기', 'description': '신규 등록부터 퇴직까지'},
            {'id': 'ai_chatbot', 'name': 'AI 챗봇', 'description': '챗봇 응답 품질 및 정확성'},
            {'id': 'dashboard_access', 'name': '대시보드 접근성', 'description': '모든 대시보드 로딩 테스트'}
        ],
        'test_categories': [
            {'id': 'quality', 'name': 'AI 품질', 'icon': 'fas fa-brain'},
            {'id': 'performance', 'name': '성능', 'icon': 'fas fa-tachometer-alt'},
            {'id': 'security', 'name': '보안', 'icon': 'fas fa-shield-alt'}
        ]
    }
    return render(request, 'testing/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def run_scenario_test(request, scenario):
    """시나리오 테스트 실행"""
    engine = IntegratedTestEngine()
    engine.login(request.user.username, 'dummy')  # 실제로는 현재 세션 사용
    
    suite = ScenarioTestSuite(engine)
    
    if scenario == 'employee_lifecycle':
        results = suite.test_employee_lifecycle_scenario()
    elif scenario == 'ai_chatbot':
        results = suite.test_ai_chatbot_scenario()
    elif scenario == 'dashboard_access':
        results = suite.test_dashboard_scenario()
    else:
        return JsonResponse({'error': 'Unknown scenario'}, status=400)
    
    return JsonResponse({
        'success': True,
        'scenario': scenario,
        'results': [r.__dict__ for r in results]
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def ai_quality_test(request):
    """AI 품질 테스트"""
    engine = IntegratedTestEngine()
    suite = AIQualityTestSuite(engine)
    
    results = suite.test_ai_response_quality()
    
    return JsonResponse({
        'success': True,
        'test_type': 'ai_quality',
        'results': [r.__dict__ for r in results]
    })
'''

    @staticmethod
    def generate_matching_views():
        """매칭 시스템 뷰 함수"""
        return '''
# matching_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from job_profiles.matching_engine import JobMatchingEngine
from employees.models import Employee
import json

@login_required
def matching_dashboard(request):
    """직무 매칭 대시보드"""
    context = {
        'title': '직무 매칭 시스템',
        'stats': {
            'open_positions': 15,
            'candidates': 234,
            'recent_matches': 8,
            'avg_match_score': 85.2
        }
    }
    return render(request, 'matching/dashboard.html', context)

@login_required
def job_search(request):
    """직무 검색 및 매칭"""
    positions = [
        {'id': 1, 'title': '시니어 백엔드 개발자', 'department': 'IT', 'match_score': 92},
        {'id': 2, 'title': 'HR 매니저', 'department': 'HR', 'match_score': 87},
        {'id': 3, 'title': '데이터 분석가', 'department': 'Analytics', 'match_score': 79}
    ]
    
    context = {
        'title': '직무 검색',
        'positions': positions
    }
    return render(request, 'matching/job_search.html', context)

@login_required
def matching_api(request):
    """매칭 API 엔드포인트"""
    if request.method == 'POST':
        data = json.loads(request.body)
        job_id = data.get('job_id')
        employee_id = data.get('employee_id')
        
        # 실제 매칭 로직 실행
        match_score = 85  # 예시 점수
        
        return JsonResponse({
            'success': True,
            'match_score': match_score,
            'recommendations': [
                'Python 스킬 향상 필요',
                '리더십 교육 추천'
            ]
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
'''

    @staticmethod
    def generate_certification_views():
        """자격증 관리 뷰 함수"""
        return '''
# certification_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from certifications.models import Certification, EmployeeCertification
from datetime import datetime

@login_required
def certification_dashboard(request):
    """자격증 관리 대시보드"""
    context = {
        'title': '자격증 관리 시스템',
        'my_certifications': [],  # 실제로는 DB에서 조회
        'available_certifications': [],
        'growth_level': {
            'current': 'Intermediate',
            'progress': 65,
            'next_level': 'Advanced'
        }
    }
    return render(request, 'certifications/dashboard.html', context)

@login_required
def my_certifications(request):
    """내 자격증 관리"""
    # 실제로는 DB에서 사용자 자격증 조회
    certifications = [
        {
            'name': 'PMP',
            'issuer': 'PMI',
            'issue_date': '2023-03-15',
            'expiry_date': '2026-03-15',
            'status': 'active'
        },
        {
            'name': 'AWS Solutions Architect',
            'issuer': 'Amazon',
            'issue_date': '2022-11-20',
            'expiry_date': '2025-11-20',
            'status': 'active'
        }
    ]
    
    context = {
        'title': '내 자격증',
        'certifications': certifications
    }
    return render(request, 'certifications/my_certifications.html', context)

@login_required
def growth_status_api(request):
    """성장 레벨 상태 API"""
    # 실제로는 복잡한 계산 로직
    growth_data = {
        'employee_id': request.user.employee.id,
        'current_level': 'Intermediate',
        'score': 1250,
        'next_level_score': 2000,
        'progress_percentage': 62.5,
        'achievements': [
            {'name': '첫 자격증 취득', 'date': '2023-03-15'},
            {'name': '5개 교육 이수', 'date': '2023-08-20'}
        ]
    }
    
    return JsonResponse(growth_data)
'''

    @staticmethod
    def generate_ess_views():
        """ESS 확장 기능 뷰 함수"""
        return '''
# ess_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def ess_plus_dashboard(request):
    """ESS 확장 기능 대시보드"""
    context = {
        'title': 'ESS Plus - 나의 성장 관리',
        'features': [
            {'name': '성장 경로', 'icon': 'fas fa-route', 'url': 'growth_path'},
            {'name': '교육 추천', 'icon': 'fas fa-graduation-cap', 'url': 'training_recommendations'},
            {'name': '경력 계획', 'icon': 'fas fa-project-diagram', 'url': 'career_planning'},
            {'name': '멘토링', 'icon': 'fas fa-user-friends', 'url': 'mentoring_match'}
        ]
    }
    return render(request, 'ess_plus/dashboard.html', context)

@login_required
def growth_path(request):
    """개인 성장 경로"""
    context = {
        'title': '나의 성장 경로',
        'current_position': 'Senior Developer',
        'next_positions': [
            {'title': 'Tech Lead', 'requirements': ['리더십 교육', '아키텍처 경험']},
            {'title': 'Solution Architect', 'requirements': ['AWS 자격증', '시스템 설계']}
        ],
        'recommended_actions': [
            {'action': 'AWS 자격증 취득', 'priority': 'high'},
            {'action': '리더십 워크샵 참여', 'priority': 'medium'}
        ]
    }
    return render(request, 'ess_plus/growth_path.html', context)

@login_required
def training_recommendations(request):
    """맞춤 교육 추천"""
    # AI 기반 추천 로직
    recommendations = [
        {
            'course': 'Advanced Python Programming',
            'match_score': 95,
            'duration': '40시간',
            'start_date': '2024-02-01'
        },
        {
            'course': 'Leadership Excellence',
            'match_score': 88,
            'duration': '24시간',
            'start_date': '2024-02-15'
        }
    ]
    
    context = {
        'title': '맞춤 교육 추천',
        'recommendations': recommendations
    }
    return render(request, 'ess_plus/training_recommendations.html', context)
'''

    @staticmethod
    def generate_analytics_views():
        """분석 도구 뷰 함수"""
        return '''
# analytics_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from datetime import datetime
import json

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['HR', 'Executive']).exists())
def analytics_dashboard(request):
    """고급 분석 도구 대시보드"""
    context = {
        'title': '고급 분석 도구',
        'analytics_tools': [
            {'name': '전략 리포트', 'icon': 'fas fa-file-alt', 'url': 'strategy_report'},
            {'name': '승진 분석', 'icon': 'fas fa-user-tie', 'url': 'promotion_analysis'},
            {'name': '인재 리스크', 'icon': 'fas fa-exclamation-triangle', 'url': 'talent_risk_analysis'}
        ]
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='Executive').exists())
def strategy_report(request):
    """전략 리포트 생성"""
    context = {
        'title': '전략 리포트 생성기',
        'report_types': [
            {'id': 'quarterly', 'name': '분기별 인재 현황'},
            {'id': 'annual', 'name': '연간 조직 성과'},
            {'id': 'talent', 'name': '인재 개발 전략'}
        ]
    }
    return render(request, 'analytics/strategy_report.html', context)

@login_required
def generate_report_api(request):
    """리포트 생성 API"""
    if request.method == 'POST':
        data = json.loads(request.body)
        report_type = data.get('report_type')
        
        # 실제 리포트 생성 로직
        report_data = {
            'title': f'{report_type} 리포트',
            'generated_at': datetime.now().isoformat(),
            'summary': '리포트 요약 내용...',
            'download_url': f'/api/download-report/{report_type}/'
        }
        
        return JsonResponse(report_data)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
'''


class TemplateGenerator:
    """템플릿 자동 생성기"""
    
    @staticmethod
    def generate_test_dashboard_template():
        """테스트 대시보드 템플릿"""
        return '''{% extends 'base.html' %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block extra_css %}
<style>
    .test-category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .test-category-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .test-category-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .test-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }
    
    .test-results {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    
    .result-item {
        padding: 12px;
        border-left: 4px solid #e9ecef;
        margin-bottom: 12px;
    }
    
    .result-item.pass {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .result-item.fail {
        border-left-color: #ef4444;
        background: #fef2f2;
    }
    
    .run-test-btn {
        background: #007bff;
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        transition: background 0.2s;
    }
    
    .run-test-btn:hover {
        background: #0056b3;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="page-header">
        <h1><i class="fas fa-flask"></i> {{ title }}</h1>
        <p class="page-description">시나리오별 QA 및 AI 품질/성능/보안 테스트</p>
    </div>
    
    <!-- 테스트 카테고리 -->
    <h3>테스트 카테고리</h3>
    <div class="test-category-grid">
        {% for category in test_categories %}
        <div class="test-category-card" onclick="runCategoryTest('{{ category.id }}')">
            <div class="test-icon">
                <i class="{{ category.icon }}"></i>
            </div>
            <h4>{{ category.name }}</h4>
            <p>클릭하여 테스트 실행</p>
        </div>
        {% endfor %}
    </div>
    
    <!-- 시나리오 테스트 -->
    <h3>시나리오 테스트</h3>
    <div class="scenario-list">
        {% for scenario in scenarios %}
        <div class="scenario-item">
            <h5>{{ scenario.name }}</h5>
            <p>{{ scenario.description }}</p>
            <button class="run-test-btn" onclick="runScenarioTest('{{ scenario.id }}')">
                <i class="fas fa-play"></i> 테스트 실행
            </button>
        </div>
        {% endfor %}
    </div>
    
    <!-- 테스트 결과 -->
    <div class="test-results" id="testResults" style="display: none;">
        <h3>테스트 결과</h3>
        <div id="resultsList"></div>
    </div>
</div>

<script>
function runCategoryTest(category) {
    showLoading();
    
    let endpoint = '';
    if (category === 'quality') {
        endpoint = '{% url "ai_quality_test" %}';
    } else if (category === 'performance') {
        endpoint = '{% url "performance_test" %}';
    } else if (category === 'security') {
        endpoint = '{% url "security_test" %}';
    }
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data.results);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('테스트 실행 중 오류가 발생했습니다.');
    })
    .finally(() => {
        hideLoading();
    });
}

function runScenarioTest(scenario) {
    showLoading();
    
    fetch(`{% url "run_scenario_test" "SCENARIO" %}`.replace('SCENARIO', scenario), {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data.results);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('테스트 실행 중 오류가 발생했습니다.');
    })
    .finally(() => {
        hideLoading();
    });
}

function displayResults(results) {
    const resultsDiv = document.getElementById('testResults');
    const resultsList = document.getElementById('resultsList');
    
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = `result-item ${result.status.toLowerCase()}`;
        resultItem.innerHTML = `
            <strong>${result.test_name}</strong>
            <span class="status">${result.status}</span>
            <p>${result.message}</p>
        `;
        resultsList.appendChild(resultItem);
    });
    
    resultsDiv.style.display = 'block';
}

function showLoading() {
    // 로딩 표시
}

function hideLoading() {
    // 로딩 숨김
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
</script>
{% endblock %}'''

    @staticmethod
    def generate_matching_dashboard_template():
        """매칭 대시보드 템플릿"""
        return '''{% extends 'base.html' %}
{% load static %}

{% block title %}{{ title }}{% endblock %}

{% block extra_css %}
<style>
    .matching-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #007bff;
        margin-bottom: 8px;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.875rem;
    }
    
    .matching-interface {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 30px;
    }
    
    .job-list, .candidate-list {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-height: 500px;
        overflow-y: auto;
    }
    
    .match-item {
        padding: 16px;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        margin-bottom: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .match-item:hover {
        border-color: #007bff;
        background: #f8f9fa;
    }
    
    .match-score {
        display: inline-block;
        padding: 4px 12px;
        background: #e7f3ff;
        color: #007bff;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .match-score.high {
        background: #d4edda;
        color: #155724;
    }
    
    .match-score.medium {
        background: #fff3cd;
        color: #856404;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="page-header">
        <h1><i class="fas fa-users-cog"></i> {{ title }}</h1>
        <div class="header-actions">
            <button class="btn btn-primary" onclick="showNewJobModal()">
                <i class="fas fa-plus"></i> 새 직무 등록
            </button>
            <button class="btn btn-outline-primary" onclick="runMatching()">
                <i class="fas fa-sync"></i> 매칭 실행
            </button>
        </div>
    </div>
    
    <!-- 통계 카드 -->
    <div class="matching-stats">
        <div class="stat-card">
            <div class="stat-value">{{ stats.open_positions }}</div>
            <div class="stat-label">열린 직무</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ stats.candidates }}</div>
            <div class="stat-label">후보자</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ stats.recent_matches }}</div>
            <div class="stat-label">최근 매칭</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ stats.avg_match_score }}%</div>
            <div class="stat-label">평균 매칭률</div>
        </div>
    </div>
    
    <!-- 매칭 인터페이스 -->
    <div class="matching-interface">
        <div class="job-list">
            <h3>직무 목록</h3>
            <div id="jobList">
                <!-- 동적으로 로드 -->
                <div class="match-item">
                    <h5>시니어 백엔드 개발자</h5>
                    <p>IT팀 • 5년 이상 경력</p>
                    <span class="match-score high">92% 매칭</span>
                </div>
            </div>
        </div>
        
        <div class="candidate-list">
            <h3>추천 후보자</h3>
            <div id="candidateList">
                <!-- 동적으로 로드 -->
                <div class="match-item">
                    <h5>김철수</h5>
                    <p>현재: 백엔드 개발자 • 경력 6년</p>
                    <span class="match-score high">92% 매칭</span>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function runMatching() {
    // 매칭 알고리즘 실행
    fetch('{% url "matching_api" %}', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            job_id: 1,
            filters: {}
        })
    })
    .then(response => response.json())
    .then(data => {
        // 결과 업데이트
        updateMatchingResults(data);
    });
}

function updateMatchingResults(data) {
    // UI 업데이트 로직
}

function showNewJobModal() {
    // 새 직무 등록 모달
}
</script>
{% endblock %}'''


class MenuIntegrator:
    """메뉴 통합 관리"""
    
    @staticmethod
    def generate_menu_updates():
        """base.html에 추가할 메뉴 항목"""
        return '''
<!-- 인재 관리 섹션 -->
<li class="sidebar-nav-section">
    <span class="sidebar-nav-section-title">인재 관리</span>
</li>

<li class="sidebar-nav-item">
    <a href="{% url 'matching_dashboard' %}" class="sidebar-nav-link {% if 'matching' in request.resolver_match.url_name %}active{% endif %}">
        <i data-lucide="users-cog" class="w-4 h-4"></i>
        <span>직무 매칭</span>
    </a>
</li>

<li class="sidebar-nav-item">
    <a href="{% url 'certification_dashboard' %}" class="sidebar-nav-link {% if 'certification' in request.resolver_match.url_name %}active{% endif %}">
        <i data-lucide="award" class="w-4 h-4"></i>
        <span>자격증 관리</span>
    </a>
</li>

<!-- 개인 성장 섹션 -->
<li class="sidebar-nav-section">
    <span class="sidebar-nav-section-title">개인 성장</span>
</li>

<li class="sidebar-nav-item">
    <a href="{% url 'ess_plus_dashboard' %}" class="sidebar-nav-link {% if 'ess_plus' in request.resolver_match.url_name %}active{% endif %}">
        <i data-lucide="user-plus" class="w-4 h-4"></i>
        <span>ESS Plus</span>
    </a>
</li>

<!-- 분석 도구 섹션 -->
<li class="sidebar-nav-section">
    <span class="sidebar-nav-section-title">분석 도구</span>
</li>

<li class="sidebar-nav-item">
    <a href="{% url 'analytics_dashboard' %}" class="sidebar-nav-link {% if 'analytics' in request.resolver_match.url_name %}active{% endif %}">
        <i data-lucide="bar-chart-3" class="w-4 h-4"></i>
        <span>고급 분석</span>
    </a>
</li>

{% if user.is_staff %}
<!-- 개발자 도구 섹션 -->
<li class="sidebar-nav-section">
    <span class="sidebar-nav-section-title">개발자 도구</span>
</li>

<li class="sidebar-nav-item">
    <a href="{% url 'test_dashboard' %}" class="sidebar-nav-link {% if 'test' in request.resolver_match.url_name %}active{% endif %}">
        <i data-lucide="flask" class="w-4 h-4"></i>
        <span>테스트 시스템</span>
    </a>
</li>
{% endif %}'''


class AutoInstaller:
    """자동 설치 및 연결 시스템"""
    
    def __init__(self):
        self.analyzer = MissingFeatureAnalyzer()
        self.url_generator = URLPatternGenerator()
        self.view_generator = ViewFunctionGenerator()
        self.template_generator = TemplateGenerator()
        self.menu_integrator = MenuIntegrator()
        
    def execute_auto_installation(self):
        """전체 자동 설치 프로세스 실행"""
        print("[START] Missing Feature Auto-Link System")
        print("="*60)
        
        # 1. 미연동 기능 분석
        print("\n[1] Analyzing missing features...")
        missing_features = self.analyzer.analyze_missing_features()
        print(f"   Found missing features: {len(missing_features)}")
        
        # 2. URL 패턴 생성
        print("\n[2] Generating URL patterns...")
        url_patterns = self.url_generator.generate_url_patterns()
        self._save_to_file('generated_url_patterns.py', url_patterns)
        print("   [OK] URL patterns generated")
        
        # 3. 뷰 함수 생성
        print("\n[3] Generating view functions...")
        self._generate_all_views()
        print("   [OK] View functions generated")
        
        # 4. 템플릿 생성
        print("\n[4] Generating templates...")
        self._generate_all_templates()
        print("   [OK] Templates generated")
        
        # 5. 메뉴 통합
        print("\n[5] Generating menu integration code...")
        menu_updates = self.menu_integrator.generate_menu_updates()
        self._save_to_file('menu_updates.html', menu_updates)
        print("   [OK] Menu integration code generated")
        
        # 6. 설치 가이드 생성
        self._generate_installation_guide(missing_features)
        
        print("\n[COMPLETE] Auto installation process finished!")
        print("="*60)
        
    def _generate_all_views(self):
        """모든 뷰 함수 생성"""
        views = {
            'testing_views.py': self.view_generator.generate_testing_views(),
            'matching_views.py': self.view_generator.generate_matching_views(),
            'certification_views.py': self.view_generator.generate_certification_views(),
            'ess_views.py': self.view_generator.generate_ess_views(),
            'analytics_views.py': self.view_generator.generate_analytics_views()
        }
        
        for filename, content in views.items():
            self._save_to_file(f'generated_views/{filename}', content)
            
    def _generate_all_templates(self):
        """모든 템플릿 생성"""
        templates = {
            'testing/dashboard.html': self.template_generator.generate_test_dashboard_template(),
            'matching/dashboard.html': self.template_generator.generate_matching_dashboard_template(),
            # 다른 템플릿들도 추가...
        }
        
        for filename, content in templates.items():
            self._save_to_file(f'generated_templates/{filename}', content)
            
    def _save_to_file(self, filename, content):
        """파일로 저장"""
        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
    def _generate_installation_guide(self, features):
        """설치 가이드 생성"""
        guide = f"""
# EHR 시스템 미연동 기능 자동 설치 가이드

## 설치 완료 항목

### 1. 생성된 파일들
- URL 패턴: `generated_url_patterns.py`
- 뷰 함수: `generated_views/` 디렉토리
- 템플릿: `generated_templates/` 디렉토리
- 메뉴 업데이트: `menu_updates.html`

### 2. 수동 작업 필요 항목

#### A. urls.py 업데이트
1. `ehr_system/urls.py` 파일을 열고
2. `generated_url_patterns.py`의 내용을 추가
3. 필요한 import 문 추가

#### B. 뷰 파일 복사
1. `generated_views/` 디렉토리의 파일들을 적절한 앱으로 복사
2. 필요한 import 문 조정

#### C. 템플릿 복사
1. `generated_templates/` 디렉토리의 파일들을 `templates/` 디렉토리로 복사
2. 디렉토리 구조 유지

#### D. base.html 업데이트
1. `templates/base.html` 파일을 열고
2. `menu_updates.html`의 내용을 사이드바 메뉴에 추가
3. 적절한 위치에 삽입 (AI 도구 섹션 다음)

### 3. 마이그레이션 (필요시)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 정적 파일 수집 (프로덕션)
```bash
python manage.py collectstatic
```

### 5. 서버 재시작
```bash
python manage.py runserver
```

## 연결된 기능 목록

총 {len(features)}개 기능이 연결되었습니다:

"""
        for key, feature in features.items():
            guide += f"- **{feature['name']}**: {feature['description']}\n"
            guide += f"  - URL: `/{feature['url_pattern']}`\n"
            guide += f"  - 메뉴: {feature['menu_category']}\n\n"
            
        self._save_to_file('INSTALLATION_GUIDE.md', guide)


if __name__ == "__main__":
    # 자동 설치 실행
    installer = AutoInstaller()
    installer.execute_auto_installation()
    
    print("\n[NEXT STEPS]:")
    print("1. Check INSTALLATION_GUIDE.md for manual tasks")
    print("2. Restart server and verify new features")
    print("3. Add detailed implementation for each feature")