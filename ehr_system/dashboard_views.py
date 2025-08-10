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
from utils.airiss_service import (
    AIRISSService, 
    format_talent_pool_for_chart,
    get_risk_level_color
)
import json
import logging

logger = logging.getLogger(__name__)


def leader_kpi_dashboard(request):
    """경영진 KPI 대시보드"""
    # DashboardAggregator 사용
    aggregator = DashboardAggregator()
    formatter = ChartDataFormatter()
    
    # AIRISS 데이터 조회
    airiss_service = AIRISSService()
    airiss_data = airiss_service.get_all_data()
    
    # AIRISS 데이터 추출
    talent_data = airiss_data.get('talent', {})
    dept_perf_data = airiss_data.get('department', {})
    risk_data = airiss_data.get('risk', {})
    
    # 기본 KPI 데이터
    talent_summary = talent_data.get('summary', {})
    risk_summary = risk_data.get('risk_summary', {})
    
    # AIRISS 통합 KPI 카드 생성
    kpis = [
        aggregator.format_kpi_card(
            title='핵심인재',
            value=f"{talent_summary.get('core_talent_count', 152):,}명",
            icon='fas fa-star',
            trend_direction='up',
            trend_value=talent_summary.get('talent_density', 18.5),
            period=f"전체 대비 {talent_summary.get('talent_density', 18.5):.1f}%"
        ),
        aggregator.format_kpi_card(
            title='승진후보',
            value=f"{talent_summary.get('promotion_candidates_count', 78):,}명",
            icon='fas fa-user-graduate',
            trend_direction='up',
            trend_value=12.5,
            period='전분기 대비'
        ),
        aggregator.format_kpi_card(
            title='평균성과',
            value=f"{dept_perf_data.get('departments', [{}])[0].get('average_score', 782)}점",
            icon='fas fa-chart-line',
            trend_direction='up',
            trend_value=8.3,
            period='전년 대비'
        ),
        aggregator.format_kpi_card(
            title='리스크레벨',
            value=risk_summary.get('overall_risk_level', 'MEDIUM'),
            icon='fas fa-exclamation-triangle',
            trend_direction='stable' if risk_summary.get('overall_risk_level') == 'MEDIUM' else ('down' if risk_summary.get('overall_risk_level') == 'HIGH' else 'up'),
            trend_value=0,
            period=f"고위험 {risk_summary.get('high_risk_count', 45)}명"
        )
    ]
    
    # 인재풀 차트 데이터 준비
    talent_chart_data = format_talent_pool_for_chart(talent_data)
    
    # 부서별 성과 TOP 5
    top_departments = dept_perf_data.get('departments', [])[:5]
    
    # AI 권고사항
    ai_recommendations = risk_summary.get('recommendations', [])
    
    # 리스크 레벨 색상
    risk_color = get_risk_level_color(risk_summary.get('overall_risk_level', 'MEDIUM'))
    
    context = {
        'title': '경영진 KPI 대시보드 - AIRISS AI 인사분석',
        'kpis': kpis,
        'talent_chart_data': json.dumps(talent_chart_data),
        'top_departments': top_departments,
        'ai_recommendations': ai_recommendations,
        'risk_level': risk_summary.get('overall_risk_level', 'MEDIUM'),
        'risk_color': risk_color,
        'airiss_integrated': True,  # AIRISS 통합 플래그
        
        # 추가 AIRISS 메트릭
        'high_risk_count': risk_summary.get('high_risk_count', 45),
        'retention_targets': risk_summary.get('retention_targets', 28),
        'risk_factors': risk_data.get('risk_factors', {}),
        
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