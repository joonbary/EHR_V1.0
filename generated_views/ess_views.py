
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
