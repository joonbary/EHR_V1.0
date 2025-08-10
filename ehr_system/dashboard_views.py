"""
대시보드 뷰 함수들
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.db.models import Count, Avg
from employees.models import Employee
from compensation.models import EmployeeCompensation
from utils.dashboard_utils import (
    DashboardAggregator, 
    ChartDataFormatter,
    format_currency,
    format_percentage
)
from utils.file_upload import create_standard_response
from utils.airiss_db_service import AIRISSDBService
import json
import logging

logger = logging.getLogger(__name__)


def leader_kpi_dashboard(request):
    """경영진 KPI 대시보드"""
    # DashboardAggregator 사용
    aggregator = DashboardAggregator()
    formatter = ChartDataFormatter()
    
    # AIRISS 데이터베이스 직접 연결
    airiss_db = AIRISSDBService()
    stats = airiss_db.get_employee_stats()
    risk_level = airiss_db.get_risk_level()
    
    # KPI 카드 생성 (AIRISS 데이터 통합)
    kpis = [
        aggregator.format_kpi_card(
            title='핵심인재',
            value=f"{stats.get('core_talent_count', 152):,}명",
            icon='fas fa-star',
            trend_direction='up',
            trend_value=stats.get('talent_density', 10.1),
            period=f"전체 대비 {stats.get('talent_density', 10.1):.1f}%"
        ),
        aggregator.format_kpi_card(
            title='승진후보',
            value=f"{stats.get('promotion_candidates_count', 78):,}명",
            icon='fas fa-user-graduate',
            trend_direction='up',
            trend_value=12.5,
            period='전분기 대비'
        ),
        aggregator.format_kpi_card(
            title='평균성과',
            value=f"{stats.get('average_score', 782):.0f}점",
            icon='fas fa-chart-line',
            trend_direction='up',
            trend_value=8.3,
            period='전년 대비'
        ),
        aggregator.format_kpi_card(
            title='전체직원',
            value=f"{stats.get('total_employees', 1509):,}명",
            icon='fas fa-users',
            trend_direction='up',
            trend_value=5.2,
            period='전월 대비'
        )
    ]
    
    context = {
        'title': '경영진 KPI 대시보드',
        'kpis': kpis,
        'airiss_integrated': False,  # AIRISS 섹션 비활성화
        
        # 갱신 시간
        'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M')
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