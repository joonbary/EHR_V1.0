
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
