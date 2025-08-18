from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Department, Position, OrganizationChart, 
    DepartmentHistory, EmployeeTransfer, TeamAssignment
)
from employees.models import Employee


def organization_dashboard(request):
    """조직관리 대시보드"""
    context = {
        # 조직 현황
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_positions': Position.objects.filter(is_active=True).count(),
        'total_employees': Employee.objects.filter(employment_status='재직').count(),
        
        # 최근 인사이동
        'recent_transfers': EmployeeTransfer.objects.select_related(
            'employee', 'old_department', 'new_department'
        ).order_by('-transfer_date')[:10],
        
        # 부서별 인원 현황
        'dept_employee_counts': Department.objects.filter(
            is_active=True
        ).annotate(
            employee_count=Count('employees', filter=Q(employees__employment_status='재직'))
        ).order_by('-employee_count')[:10],
        
        # 현재 조직도
        'current_org_chart': OrganizationChart.objects.filter(is_active=True).first(),
        
        # 승진 대상자 (성장레벨이 직위의 최대 레벨에 도달한 직원)
        'promotion_candidates': Employee.objects.filter(
            employment_status='재직',
            growth_level__gte=5
        ).select_related('manager')[:10],
    }
    
    return render(request, 'organization/dashboard_revolutionary.html', context)


def department_list(request):
    """부서 목록"""
    departments = Department.objects.filter(is_active=True).select_related('parent', 'manager')
    
    # 트리 구조로 변환
    def build_tree(parent=None):
        items = []
        for dept in departments.filter(parent=parent):
            items.append({
                'department': dept,
                'children': build_tree(dept),
                'employee_count': dept.get_employee_count()
            })
        return items
    
    context = {
        'department_tree': build_tree(),
        'total_departments': departments.count(),
    }
    
    return render(request, 'organization/department_list.html', context)


def department_detail(request, department_id):
    """부서 상세 정보"""
    department = get_object_or_404(Department, id=department_id)
    
    # 부서 직원 목록
    employees = Employee.objects.filter(
        department=department.code,
        employment_status='재직'
    ).select_related('manager').order_by('growth_level', 'name')
    
    # 하위 부서
    sub_departments = department.children.filter(is_active=True).annotate(
        employee_count=Count('employees', filter=Q(employees__employment_status='재직'))
    )
    
    # 부서 변경 이력
    history = department.history.select_related(
        'organization_chart', 'old_parent', 'new_parent'
    ).order_by('-changed_date')[:10]
    
    context = {
        'department': department,
        'employees': employees,
        'sub_departments': sub_departments,
        'history': history,
        'full_path': department.get_full_path(),
    }
    
    return render(request, 'organization/department_detail.html', context)


@require_http_methods(["GET", "POST"])
def department_create(request):
    """부서 생성"""
    if request.method == 'POST':
        try:
            department = Department.objects.create(
                code=request.POST.get('code'),
                name=request.POST.get('name'),
                name_en=request.POST.get('name_en', ''),
                parent_id=request.POST.get('parent_id') if request.POST.get('parent_id') else None,
                department_type=request.POST.get('department_type'),
                level=int(request.POST.get('level', 1)),
                description=request.POST.get('description', ''),
                location=request.POST.get('location', ''),
                phone=request.POST.get('phone', ''),
                email=request.POST.get('email', ''),
                manager_id=request.POST.get('manager_id') if request.POST.get('manager_id') else None,
                created_by=request.user
            )
            
            messages.success(request, f'{department.name} 부서가 생성되었습니다.')
            return redirect('organization:department_detail', department_id=department.id)
            
        except Exception as e:
            messages.error(request, f'부서 생성 중 오류가 발생했습니다: {str(e)}')
    
    context = {
        'departments': Department.objects.filter(is_active=True),
        'managers': Employee.objects.filter(
            employment_status='재직',
            new_position__in=['팀장', '부장', '본부장']
        ),
        'department_types': Department.DEPARTMENT_TYPE_CHOICES,
    }
    
    return render(request, 'organization/department_form.html', context)


def position_list(request):
    """직위 목록"""
    # Position 모델과 Employee 모델이 직접 연결되지 않았으므로
    # 각 직위별 직원 수를 별도로 계산
    positions = Position.objects.filter(is_active=True).order_by('rank')
    
    # 각 직위별 직원 수 계산
    for position in positions:
        position.employee_count = Employee.objects.filter(
            new_position=position.name,
            employment_status='재직'
        ).count()
    
    context = {
        'positions': positions,
    }
    
    return render(request, 'organization/position_list.html', context)


def position_detail(request, position_id):
    """직위 상세 정보"""
    position = get_object_or_404(Position, id=position_id)
    
    # 해당 직위 직원 목록
    employees = Employee.objects.filter(
        new_position=position.name,
        employment_status='재직'
    ).select_related('manager').order_by('growth_level', 'name')
    
    context = {
        'position': position,
        'employees': employees,
        'employee_count': employees.count(),
    }
    
    return render(request, 'organization/position_detail.html', context)


def organization_chart(request):
    """고급 조직도 (React 기반)"""
    from .models_enhanced import OrgUnit, OrgScenario
    
    # 기본 통계 정보
    total_units = OrgUnit.objects.count()
    total_scenarios = OrgScenario.objects.count()
    
    # 회사별 조직 수
    company_stats = {}
    for company in ['OK저축은행', 'OK캐피탈', 'OK금융그룹']:
        company_stats[company] = OrgUnit.objects.filter(company=company).count()
    
    # 최근 시나리오
    recent_scenarios = OrgScenario.objects.order_by('-created_at')[:5]
    
    context = {
        'total_units': total_units,
        'total_scenarios': total_scenarios,
        'company_stats': company_stats,
        'recent_scenarios': recent_scenarios,
        
        # 기존 호환성을 위한 데이터
        'current_chart': OrganizationChart.objects.filter(is_active=True).first(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_employees': Employee.objects.filter(employment_status='재직').count(),
    }
    
    return render(request, 'organization/organization_chart.html', context)


def transfer_list(request):
    """인사이동 목록"""
    transfers = EmployeeTransfer.objects.select_related(
        'employee', 'old_department', 'new_department', 'approved_by'
    ).order_by('-transfer_date')
    
    # 필터링
    transfer_type = request.GET.get('type')
    if transfer_type:
        transfers = transfers.filter(transfer_type=transfer_type)
    
    start_date = request.GET.get('start_date')
    if start_date:
        transfers = transfers.filter(transfer_date__gte=start_date)
    
    end_date = request.GET.get('end_date')
    if end_date:
        transfers = transfers.filter(transfer_date__lte=end_date)
    
    context = {
        'transfers': transfers[:100],  # 최근 100건
        'transfer_types': EmployeeTransfer.TRANSFER_TYPE_CHOICES,
        'selected_type': transfer_type,
    }
    
    return render(request, 'organization/transfer_list.html', context)


@require_http_methods(["GET", "POST"])
def transfer_create(request):
    """인사이동 생성"""
    if request.method == 'POST':
        try:
            transfer = EmployeeTransfer.objects.create(
                employee_id=request.POST.get('employee_id'),
                transfer_type=request.POST.get('transfer_type'),
                transfer_date=request.POST.get('transfer_date'),
                old_department_id=request.POST.get('old_department_id'),
                old_position=request.POST.get('old_position'),
                old_growth_level=int(request.POST.get('old_growth_level')),
                new_department_id=request.POST.get('new_department_id'),
                new_position=request.POST.get('new_position'),
                new_growth_level=int(request.POST.get('new_growth_level')),
                reason=request.POST.get('reason'),
                remarks=request.POST.get('remarks', ''),
                created_by=request.user
            )
            
            messages.success(request, '인사이동이 등록되었습니다.')
            return redirect('organization:transfer_detail', transfer_id=transfer.id)
            
        except Exception as e:
            messages.error(request, f'인사이동 등록 중 오류가 발생했습니다: {str(e)}')
    
    context = {
        'employees': Employee.objects.filter(employment_status='재직'),
        'departments': Department.objects.filter(is_active=True),
        'positions': Position.objects.filter(is_active=True),
        'transfer_types': EmployeeTransfer.TRANSFER_TYPE_CHOICES,
    }
    
    return render(request, 'organization/transfer_form.html', context)


def transfer_detail(request, transfer_id):
    """인사이동 상세"""
    transfer = get_object_or_404(
        EmployeeTransfer.objects.select_related(
            'employee', 'old_department', 'new_department', 
            'approved_by', 'created_by'
        ),
        id=transfer_id
    )
    
    context = {
        'transfer': transfer,
    }
    
    return render(request, 'organization/transfer_detail.html', context)


@require_http_methods(["POST"])
def transfer_approve(request, transfer_id):
    """인사이동 승인"""
    transfer = get_object_or_404(EmployeeTransfer, id=transfer_id)
    
    if not transfer.approved_date:
        transfer.approved_by = request.user
        transfer.approved_date = timezone.now()
        transfer.save()
        
        # 인사이동 실행
        if transfer.execute_transfer():
            messages.success(request, '인사이동이 승인되고 실행되었습니다.')
        else:
            messages.warning(request, '인사이동이 승인되었지만 실행에 실패했습니다.')
    else:
        messages.info(request, '이미 승인된 인사이동입니다.')
    
    return redirect('organization:transfer_detail', transfer_id=transfer_id)


def team_assignment_list(request):
    """팀 배치 목록"""
    assignments = TeamAssignment.objects.select_related(
        'employee', 'department'
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now().date())
    ).order_by('employee__name', '-is_primary')
    
    context = {
        'assignments': assignments,
    }
    
    return render(request, 'organization/team_assignment_list.html', context)


# API Views
@require_http_methods(["GET"])
def api_department_employees(request, department_id):
    """부서 직원 목록 API"""
    department = get_object_or_404(Department, id=department_id)
    employees = Employee.objects.filter(
        department=department.code,
        employment_status='재직'
    ).values('id', 'name', 'new_position', 'growth_level')
    
    return JsonResponse({
        'department': {
            'id': str(department.id),
            'name': department.name,
            'code': department.code,
        },
        'employees': list(employees),
        'count': employees.count()
    })


@require_http_methods(["GET"])
def api_organization_tree(request):
    """조직도 트리 데이터 API"""
    departments = Department.objects.filter(is_active=True).select_related('manager')
    
    def build_tree(parent=None):
        items = []
        for dept in departments.filter(parent=parent):
            items.append({
                'id': str(dept.id),
                'name': dept.name,
                'code': dept.code,
                'type': dept.department_type,
                'manager': dept.manager.name if dept.manager else None,
                'employee_count': dept.get_employee_count(),
                'children': build_tree(dept)
            })
        return items
    
    return JsonResponse({
        'data': build_tree(),
        'total_departments': departments.count(),
        'total_employees': Employee.objects.filter(employment_status='재직').count()
    })