"""
대시보드 뷰 함수들
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils import timezone
from employees.models import Employee
from compensation.models import EmployeeCompensation
from django.db.models import Count, Avg, Sum, Max, Min
import json
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 5)  # 5분 캐시
def leader_kpi_dashboard(request):
    """경영진 KPI 대시보드"""
    # KPI 데이터 수집
    total_employees = Employee.objects.count()
    avg_salary = EmployeeCompensation.objects.aggregate(
        avg=Avg('total_compensation')
    )['avg'] or 0
    
    # 부서별 인원 통계
    dept_stats = Employee.objects.values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # KPI 목록
    kpis = [
        {
            'title': '총 직원수',
            'value': f'{total_employees:,}',
            'icon': 'fas fa-users',
            'trend_direction': 'up',
            'trend_value': 5.2,
            'period': '전월 대비'
        },
        {
            'title': '평균 급여',
            'value': f'₩{int(avg_salary):,}',
            'icon': 'fas fa-won-sign',
            'trend_direction': 'up',
            'trend_value': 3.1,
            'period': '전년 대비'
        },
        {
            'title': '부서 수',
            'value': dept_stats.count(),
            'icon': 'fas fa-building',
            'trend_direction': 'up',
            'trend_value': 0,
            'period': '변동 없음'
        },
        {
            'title': '평균 근속연수',
            'value': '5.2년',
            'icon': 'fas fa-calendar-alt',
            'trend_direction': 'up',
            'trend_value': 2.5,
            'period': '전년 대비'
        }
    ]
    
    # 차트 데이터
    chart_data = {
        'labels': [dept['department'] for dept in dept_stats[:5]],
        'datasets': [{
            'label': '부서별 인원',
            'data': [dept['count'] for dept in dept_stats[:5]],
            'backgroundColor': [
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 99, 132, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)'
            ]
        }]
    }
    
    context = {
        'title': '경영진 KPI 대시보드',
        'kpis': kpis,
        'chart_data': json.dumps(chart_data)
    }
    
    return render(request, 'dashboards/leader_kpi.html', context)


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
        # 인력 통계
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(employment_status='재직').count()
        
        # 부서별 분포
        dept_data = Employee.objects.values('department').annotate(
            employee_count=Count('id'),
            avg_salary=Avg('compensations__total_compensation')
        ).order_by('-employee_count')
        
        # 부서 데이터 변환 (snake_case → camelCase)
        departments = []
        for dept in dept_data:
            departments.append({
                'departmentName': dept.get('department') or 'Unknown',
                'employeeCount': dept.get('employee_count', 0),
                'avgSalary': float(dept.get('avg_salary') or 0)
            })
        
        # 보상 통계
        compensation_stats = EmployeeCompensation.objects.aggregate(
            total=Sum('total_compensation'),
            average=Avg('total_compensation'),
            max_comp=Max('total_compensation'),
            min_comp=Min('total_compensation')
        )
        
        # 월별 신규 입사자
        current_month = timezone.now().replace(day=1)
        new_hires = Employee.objects.filter(
            hire_date__gte=current_month
        ).count()
        
        # 응답 데이터 구조화
        response_data = {
            'success': True,
            'data': {
                'workforce': {
                    'totalEmployees': total_employees,
                    'activeEmployees': active_employees,
                    'newHiresMonth': new_hires,
                    'terminationsMonth': 0,  # 실제 데이터로 대체 필요
                },
                'compensation': {
                    'totalPayroll': float(compensation_stats.get('total') or 0),
                    'avgSalary': float(compensation_stats.get('average') or 0),
                    'maxSalary': float(compensation_stats.get('max_comp') or 0),
                    'minSalary': float(compensation_stats.get('min_comp') or 0),
                },
                'departments': departments
            },
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in workforce_comp_api: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'data': {
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
            }
        }, status=500)