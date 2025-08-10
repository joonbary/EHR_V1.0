"""
대시보드 뷰 함수들
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils import timezone
from employees.models import Employee
from compensation.models import EmployeeCompensation
from utils.dashboard_utils import (
    DashboardAggregator, 
    ChartDataFormatter,
    format_currency,
    format_percentage
)
from utils.file_upload import create_standard_response
import json
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 5)  # 5분 캐시
def leader_kpi_dashboard(request):
    """경영진 KPI 대시보드"""
    # DashboardAggregator 사용
    aggregator = DashboardAggregator()
    formatter = ChartDataFormatter()
    
    # 직원 통계
    employee_stats = aggregator.get_employee_statistics(Employee.objects.all())
    
    # 보상 통계
    comp_stats = aggregator.get_compensation_statistics(EmployeeCompensation.objects.all())
    
    # 부서별 요약
    dept_summary = aggregator.get_department_summary(Employee.objects.all())
    
    # KPI 카드 생성
    kpis = [
        aggregator.format_kpi_card(
            title='총 직원수',
            value=f"{employee_stats['total_employees']:,}",
            icon='fas fa-users',
            trend_direction='up',
            trend_value=5.2,
            period='전월 대비'
        ),
        aggregator.format_kpi_card(
            title='평균 급여',
            value=format_currency(comp_stats['avg_salary']),
            icon='fas fa-won-sign',
            trend_direction='up',
            trend_value=3.1,
            period='전년 대비'
        ),
        aggregator.format_kpi_card(
            title='부서 수',
            value=len(dept_summary),
            icon='fas fa-building',
            trend_direction='stable',
            trend_value=0,
            period='변동 없음'
        ),
        aggregator.format_kpi_card(
            title='평균 근속연수',
            value='5.2년',
            icon='fas fa-calendar-alt',
            trend_direction='up',
            trend_value=2.5,
            period='전년 대비'
        )
    ]
    
    # 차트 데이터 포맷팅
    chart_data = formatter.format_bar_chart(
        labels=[dept['department_name'] for dept in dept_summary[:5]],
        data=[dept['employee_count'] for dept in dept_summary[:5]],
        label='부서별 인원'
    )
    
    context = {
        'title': '경영진 KPI 대시보드',
        'kpis': kpis,
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'dashboards/leader_kpi_dashboard_revolutionary.html', context)


def workforce_comp_dashboard(request):
    """인력/보상 통합 대시보드"""
    # 인력 통계
    total_employees = Employee.objects.count()
    dept_distribution = Employee.objects.values('department').annotate(
        count=Count('id'),
        avg_salary=Avg('compensations__total_compensation')
    ).order_by('-count')
    
    # 보상 통계
    compensation_stats = EmployeeCompensation.objects.aggregate(
        total=Sum('total_compensation'),
        average=Avg('total_compensation'),
        max_comp=Max('total_compensation'),
        min_comp=Min('total_compensation')
    )
    
    context = {
        'title': '인력/보상 현황',
        'total_employees': total_employees,
        'dept_distribution': dept_distribution,
        'compensation_stats': compensation_stats,
    }
    
    return render(request, 'dashboards/workforce_comp.html', context)


def skillmap_dashboard(request):
    """스킬맵 대시보드"""
    # 기본 필터 옵션
    context = {
        'title': '직무스킬맵',
        'departments': Employee.DEPARTMENT_CHOICES,
        'job_groups': [('PL', 'PL'), ('Non-PL', 'Non-PL')],
        'job_types': [
            ('IT기획', 'IT기획'), ('IT개발', 'IT개발'), ('IT운영', 'IT운영'),
            ('경영관리', '경영관리'), ('기업영업', '기업영업'), ('기업금융', '기업금융'),
            ('리테일금융', '리테일금융'), ('투자금융', '투자금융'), ('고객지원', '고객지원')
        ],
        'growth_levels': [(i, f'Level {i}') for i in range(1, 6)]
    }
    
    # Use the main dashboard template
    return render(request, 'skillmap/dashboard.html', context)


# API 엔드포인트
def export_dashboard(request):
    """대시보드 데이터 내보내기"""
    export_type = request.GET.get('type', 'pdf')
    
    # 실제 구현에서는 PDF/Excel 생성 로직 추가
    return JsonResponse({
        'success': True,
        'message': f'{export_type.upper()} 파일 생성 중...'
    })


def workforce_comp_api(request):
    """인력/보상 대시보드 API - 개선된 데이터 바인딩"""
    try:
        # DashboardAggregator 사용
        aggregator = DashboardAggregator()
        
        # 직원 통계
        employee_stats = aggregator.get_employee_statistics(Employee.objects.all())
        
        # 보상 통계
        comp_stats = aggregator.get_compensation_statistics(EmployeeCompensation.objects.all())
        
        # 부서별 요약 (camelCase 변환)
        dept_summary = aggregator.get_department_summary(Employee.objects.all())
        departments = []
        for dept in dept_summary:
            departments.append({
                'departmentName': dept['department_name'],
                'employeeCount': dept['employee_count'],
                'avgSalary': dept.get('avg_salary', 0)
            })
        
        # 응답 데이터 구조화
        response_data = {
            'success': True,
            'data': {
                'workforce': {
                    'totalEmployees': employee_stats['total_employees'],
                    'activeEmployees': employee_stats['active_employees'],
                    'newHiresMonth': employee_stats['new_hires_month'],
                    'terminationsMonth': employee_stats['resignations_month'],
                },
                'compensation': {
                    'totalPayroll': comp_stats['total_payroll'],
                    'avgSalary': comp_stats['avg_salary'],
                    'maxSalary': comp_stats['max_salary'],
                    'minSalary': comp_stats['min_salary'],
                },
                'departments': departments
            },
            'timestamp': timezone.now().isoformat()
        }
        
        return create_standard_response(
            success=True,
            data=response_data['data']
        )
        
    except Exception as e:
        logger.error(f"Error in workforce_comp_api: {str(e)}", exc_info=True)
        return create_standard_response(
            success=False,
            error=str(e),
            data={
                'workforce': {
                    'totalEmployees': 0,
                    'activeEmployees': 0,
                    'newHiresMonth': 0,
                    'terminationsMonth': 0,
                },
                'compensation': {
                    'totalPayroll': 0,
                    'avgSalary': 0,
                    'maxSalary': 0,
                    'minSalary': 0,
                },
                'departments': []
            },
            status_code=500
        )