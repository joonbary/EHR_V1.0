
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
