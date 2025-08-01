
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
