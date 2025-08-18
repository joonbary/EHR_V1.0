
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
