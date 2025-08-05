from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import date, timedelta
import json

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from .models import (
    PromotionRequirement, PromotionRequest, JobTransfer, OrganizationChart
)


@login_required
def promotion_dashboard(request):
    """승진 심사 대시보드"""
    # 승진 대상자 자동 추출
    eligible_employees = []
    
    # 모든 직원에 대해 승진 가능성 확인
    employees = Employee.objects.all()
    
    for employee in employees:
        current_level = employee.growth_level
        if current_level < 6:  # 최고 레벨이 아닌 경우
            target_level = current_level + 1
            
            # 승진 요건 확인
            requirement = PromotionRequirement.objects.filter(
                from_level=current_level,
                to_level=target_level
            ).first()
            
            if requirement:
                # 임시 승진 요청 객체 생성하여 요건 계산
                temp_request = PromotionRequest(
                    employee=employee,
                    current_level=current_level,
                    target_level=target_level
                )
                temp_request.calculate_requirements()
                
                if temp_request.is_eligible_for_promotion():
                    eligible_employees.append({
                        'employee': employee,
                        'current_level': current_level,
                        'target_level': target_level,
                        'years_of_service': temp_request.years_of_service,
                        'consecutive_a_grades': temp_request.consecutive_a_grades,
                        'average_performance_score': temp_request.average_performance_score,
                        'requirement': requirement
                    })
    
    # 승진 요청 현황
    promotion_requests = PromotionRequest.objects.all().order_by('-created_at')
    
    # 통계
    stats = {
        'total_requests': promotion_requests.count(),
        'pending_requests': promotion_requests.filter(status='PENDING').count(),
        'approved_requests': promotion_requests.filter(status='APPROVED').count(),
        'rejected_requests': promotion_requests.filter(status='REJECTED').count(),
        'eligible_count': len(eligible_employees)
    }
    
    context = {
        'eligible_employees': eligible_employees,
        'promotion_requests': promotion_requests[:10],  # 최근 10개
        'stats': stats,
    }
    
    return render(request, 'promotions/dashboard.html', context)


@login_required
def promotion_request_list(request):
    """승진 요청 목록"""
    requests = PromotionRequest.objects.all().order_by('-created_at')
    
    # 필터링
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    level_filter = request.GET.get('level')
    if level_filter:
        requests = requests.filter(current_level=level_filter)
    
    # 검색
    search = request.GET.get('search')
    if search:
        requests = requests.filter(
            Q(employee__name__icontains=search) |
            Q(employee__employee_id__icontains=search)
        )
    
    # 페이징
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': PromotionRequest._meta.get_field('status').choices,
    }
    
    return render(request, 'promotions/request_list.html', context)


@login_required
def promotion_request_detail(request, request_id):
    """승진 요청 상세"""
    promotion_request = get_object_or_404(PromotionRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            promotion_request.status = 'APPROVED'
            promotion_request.final_decision = 'APPROVED'
            promotion_request.final_decision_date = date.today()
            promotion_request.final_decision_by = request.user.employee if hasattr(request.user, 'employee') else None
            promotion_request.save()
            messages.success(request, '승진 요청이 승인되었습니다.')
            
        elif action == 'reject':
            promotion_request.status = 'REJECTED'
            promotion_request.final_decision = 'REJECTED'
            promotion_request.final_decision_date = date.today()
            promotion_request.final_decision_by = request.user.employee if hasattr(request.user, 'employee') else None
            promotion_request.save()
            messages.success(request, '승진 요청이 반려되었습니다.')
            
        elif action == 'department_recommend':
            promotion_request.department_recommendation = True
            promotion_request.department_recommender = request.user.employee if hasattr(request.user, 'employee') else None
            promotion_request.department_recommendation_date = date.today()
            promotion_request.department_comments = request.POST.get('comments', '')
            promotion_request.save()
            messages.success(request, '부서장 추천이 완료되었습니다.')
            
        elif action == 'hr_committee':
            promotion_request.hr_committee_decision = request.POST.get('decision')
            promotion_request.hr_committee_date = date.today()
            promotion_request.hr_comments = request.POST.get('comments', '')
            promotion_request.save()
            messages.success(request, 'HR위원회 심사가 완료되었습니다.')
        
        return redirect('promotions:request_detail', request_id=request_id)
    
    context = {
        'promotion_request': promotion_request,
    }
    
    return render(request, 'promotions/request_detail.html', context)


@login_required
def create_promotion_request(request, employee_id):
    """승진 요청 생성"""
    employee = get_object_or_404(Employee, id=employee_id)
    
    if request.method == 'POST':
        current_level = int(request.POST.get('current_level'))
        target_level = int(request.POST.get('target_level'))
        comments = request.POST.get('comments', '')
        
        # 기존 요청이 있는지 확인
        existing_request = PromotionRequest.objects.filter(
            employee=employee,
            status__in=['PENDING', 'UNDER_REVIEW']
        ).first()
        
        if existing_request:
            messages.error(request, '이미 진행 중인 승진 요청이 있습니다.')
            return redirect('promotions:dashboard')
        
        # 새 요청 생성
        promotion_request = PromotionRequest.objects.create(
            employee=employee,
            current_level=current_level,
            target_level=target_level,
            employee_comments=comments
        )
        
        # 요건 계산
        promotion_request.calculate_requirements()
        
        messages.success(request, '승진 요청이 생성되었습니다.')
        return redirect('promotions:request_detail', request_id=promotion_request.id)
    
    # 가능한 승진 레벨
    current_level = employee.growth_level
    if current_level < 6:
        target_level = current_level + 1
    else:
        target_level = current_level
    
    context = {
        'employee': employee,
        'current_level': current_level,
        'target_level': target_level,
    }
    
    return render(request, 'promotions/create_request.html', context)


@login_required
def job_transfer_list(request):
    """인사이동 목록"""
    transfers = JobTransfer.objects.all().order_by('-effective_date')
    
    # 필터링
    transfer_type = request.GET.get('type')
    if transfer_type:
        transfers = transfers.filter(transfer_type=transfer_type)
    
    status_filter = request.GET.get('status')
    if status_filter:
        transfers = transfers.filter(status=status_filter)
    
    # 검색
    search = request.GET.get('search')
    if search:
        transfers = transfers.filter(
            Q(employee__name__icontains=search) |
            Q(from_department__icontains=search) |
            Q(to_department__icontains=search)
        )
    
    # 페이징
    paginator = Paginator(transfers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transfer_types': JobTransfer._meta.get_field('transfer_type').choices,
        'status_choices': JobTransfer._meta.get_field('status').choices,
    }
    
    return render(request, 'promotions/transfer_list.html', context)


@login_required
def create_job_transfer(request):
    """인사이동 생성"""
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        employee = get_object_or_404(Employee, id=employee_id)
        
        transfer = JobTransfer.objects.create(
            employee=employee,
            from_department=request.POST.get('from_department'),
            to_department=request.POST.get('to_department'),
            from_position=request.POST.get('from_position'),
            to_position=request.POST.get('to_position'),
            transfer_type=request.POST.get('transfer_type'),
            effective_date=request.POST.get('effective_date'),
            announcement_date=request.POST.get('announcement_date'),
            reason=request.POST.get('reason'),
            additional_notes=request.POST.get('additional_notes', '')
        )
        
        messages.success(request, '인사이동이 생성되었습니다.')
        return redirect('promotions:transfer_list')
    
    employees = Employee.objects.all()
    departments = Employee.objects.values_list('department', flat=True).distinct()
    positions = Employee.objects.values_list('position', flat=True).distinct()
    
    context = {
        'employees': employees,
        'departments': departments,
        'positions': positions,
        'transfer_types': JobTransfer._meta.get_field('transfer_type').choices,
    }
    
    return render(request, 'promotions/create_transfer.html', context)


@login_required
def organization_chart(request):
    """조직도"""
    departments = OrganizationChart.objects.filter(is_active=True).order_by('display_order')
    
    # 부서별 직원 수 업데이트
    for dept in departments:
        dept.update_employee_count()
    
    # 부서별 직원 목록
    department_employees = {}
    for dept in departments:
        employees = Employee.objects.filter(
            department=dept.department,
            employment_status='active'
        ).order_by('growth_level', 'name')
        department_employees[dept.department] = employees
    
    context = {
        'departments': departments,
        'department_employees': department_employees,
    }
    
    return render(request, 'promotions/organization_chart.html', context)


@login_required
def promotion_analytics(request):
    """승진 분석"""
    # 승진 통계
    promotion_stats = PromotionRequest.objects.aggregate(
        total_requests=Count('id'),
        approved_requests=Count('id', filter=Q(status='APPROVED')),
        rejected_requests=Count('id', filter=Q(status='REJECTED')),
        pending_requests=Count('id', filter=Q(status='PENDING'))
    )
    
    # 레벨별 승진 현황
    level_stats = {}
    for level in range(1, 6):
        level_stats[level] = {
            'total': PromotionRequest.objects.filter(current_level=level).count(),
            'approved': PromotionRequest.objects.filter(
                current_level=level, status='APPROVED'
            ).count(),
            'rejected': PromotionRequest.objects.filter(
                current_level=level, status='REJECTED'
            ).count(),
        }
    
    # 월별 승진 추이
    monthly_stats = []
    for i in range(12):
        month_date = date.today() - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = PromotionRequest.objects.filter(
            created_at__date__range=[month_start, month_end]
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    context = {
        'promotion_stats': promotion_stats,
        'level_stats': level_stats,
        'monthly_stats': monthly_stats,
    }
    
    return render(request, 'promotions/analytics.html', context)
