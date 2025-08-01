
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Sum, Q
from django.core.cache import cache
import logging
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def workforce_comp_summary_api(request):
    '''인력/보상 현황 대시보드 API - 안전한 데이터 처리'''
    
    logger.info(f"[API] Workforce compensation summary requested by {request.user}")
    
    try:
        # 캐시 확인
        cache_key = f'workforce_comp_summary_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.info("[API] Returning cached data")
            return JsonResponse(cached_data)
        
        # 인력 현황 데이터
        workforce_data = get_workforce_summary()
        
        # 보상 현황 데이터
        compensation_data = get_compensation_summary()
        
        # 부서별 데이터
        department_data = get_department_summary()
        
        # 응답 데이터 구성
        response_data = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'workforce': workforce_data,
            'compensation': compensation_data,
            'departments': department_data,
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'data_quality': check_data_quality()
            }
        }
        
        # 캐시 저장 (5분)
        cache.set(cache_key, response_data, 300)
        
        logger.info("[API] Successfully generated workforce compensation summary")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"[API] Error in workforce_comp_summary: {str(e)}", exc_info=True)
        
        # 에러 시에도 기본 구조 반환
        return JsonResponse({
            'success': False,
            'error': str(e),
            'workforce': {
                'total_employees': 0,
                'active_employees': 0,
                'new_hires_month': 0,
                'terminations_month': 0,
                'change_percent': 0
            },
            'compensation': {
                'total_payroll': 0,
                'avg_salary': 0,
                'salary_range': {'min': 0, 'max': 0, 'median': 0},
                'benefits_cost': 0,
                'salary_growth': 0
            },
            'departments': []
        }, status=500)


def get_workforce_summary():
    '''인력 현황 요약 - NULL 안전 처리'''
    try:
        from employees.models import Employee
        
        # 전체 직원수
        total_employees = Employee.objects.count()
        
        # 재직 중인 직원
        active_employees = Employee.objects.filter(
            employment_status='재직'
        ).count()
        
        # 이번 달 신규 채용
        current_month = datetime.now().replace(day=1)
        new_hires = Employee.objects.filter(
            hire_date__gte=current_month,
            hire_date__lt=current_month + timedelta(days=32)
        ).count()
        
        # 이번 달 퇴사자
        terminations = Employee.objects.filter(
            termination_date__gte=current_month,
            termination_date__lt=current_month + timedelta(days=32)
        ).count()
        
        # 전월 대비 변동률
        last_month = current_month - timedelta(days=1)
        last_month_start = last_month.replace(day=1)
        last_month_employees = Employee.objects.filter(
            hire_date__lt=last_month_start,
            Q(termination_date__isnull=True) | Q(termination_date__gte=last_month_start)
        ).count()
        
        change_percent = 0
        if last_month_employees > 0:
            change_percent = ((active_employees - last_month_employees) / last_month_employees) * 100
        
        return {
            'total_employees': total_employees,
            'active_employees': active_employees,
            'new_hires_month': new_hires,
            'terminations_month': terminations,
            'change_percent': round(change_percent, 2),
            'hiring_trend': round((new_hires - terminations) / max(active_employees, 1) * 100, 2)
        }
        
    except Exception as e:
        logger.error(f"Error in get_workforce_summary: {e}")
        return {
            'total_employees': 0,
            'active_employees': 0,
            'new_hires_month': 0,
            'terminations_month': 0,
            'change_percent': 0,
            'hiring_trend': 0
        }


def get_compensation_summary():
    '''보상 현황 요약 - NULL 안전 처리'''
    try:
        from employees.models import Employee
        from compensation.models import Salary
        
        # 활성 직원의 급여 정보
        active_salaries = Salary.objects.filter(
            employee__employment_status='재직',
            is_active=True
        )
        
        # 집계 데이터 (NULL 체크 포함)
        salary_stats = active_salaries.aggregate(
            total=Sum('base_salary'),
            avg=Avg('base_salary'),
            min_salary=Min('base_salary'),
            max_salary=Max('base_salary')
        )
        
        # NULL 처리
        total_payroll = salary_stats.get('total') or 0
        avg_salary = salary_stats.get('avg') or 0
        min_salary = salary_stats.get('min_salary') or 0
        max_salary = salary_stats.get('max_salary') or 0
        
        # 중간값 계산
        median_salary = calculate_median_salary(active_salaries)
        
        # 복리후생비 (예상)
        benefits_cost = total_payroll * 0.2  # 급여의 20%로 가정
        
        # 전년 대비 급여 성장률
        last_year = datetime.now() - timedelta(days=365)
        last_year_avg = Salary.objects.filter(
            created_at__lt=last_year,
            is_active=True
        ).aggregate(avg=Avg('base_salary'))['avg'] or avg_salary
        
        salary_growth = 0
        if last_year_avg > 0:
            salary_growth = ((avg_salary - last_year_avg) / last_year_avg) * 100
        
        return {
            'total_payroll': float(total_payroll),
            'avg_salary': float(avg_salary),
            'salary_range': {
                'min': float(min_salary),
                'max': float(max_salary),
                'median': float(median_salary)
            },
            'benefits_cost': float(benefits_cost),
            'salary_growth': round(salary_growth, 2),
            'payroll_growth': round(salary_growth * 0.8, 2)  # 간소화된 계산
        }
        
    except Exception as e:
        logger.error(f"Error in get_compensation_summary: {e}")
        return {
            'total_payroll': 0,
            'avg_salary': 0,
            'salary_range': {'min': 0, 'max': 0, 'median': 0},
            'benefits_cost': 0,
            'salary_growth': 0,
            'payroll_growth': 0
        }


def get_department_summary():
    '''부서별 요약 - NULL 안전 처리'''
    try:
        from employees.models import Employee, Department
        
        departments = []
        
        for dept in Department.objects.all():
            # 부서별 직원 수
            dept_employees = Employee.objects.filter(
                department=dept,
                employment_status='재직'
            )
            
            employee_count = dept_employees.count()
            
            if employee_count == 0:
                continue
            
            # 부서별 급여 통계
            salary_stats = dept_employees.aggregate(
                avg_salary=Avg('current_salary'),
                total_salary=Sum('current_salary')
            )
            
            avg_salary = salary_stats.get('avg_salary') or 0
            total_salary = salary_stats.get('total_salary') or 0
            
            # 전월 대비 변동
            last_month = datetime.now() - timedelta(days=30)
            last_month_count = dept_employees.filter(
                hire_date__lt=last_month
            ).count()
            
            change = 0
            if last_month_count > 0:
                change = ((employee_count - last_month_count) / last_month_count) * 100
            
            departments.append({
                'id': str(dept.id),
                'name': dept.name or 'Unknown',
                'employee_count': employee_count,
                'avg_salary': float(avg_salary),
                'total_salary': float(total_salary),
                'change': round(change, 2)
            })
        
        # 직원 수 기준 정렬
        departments.sort(key=lambda x: x['employee_count'], reverse=True)
        
        return departments
        
    except Exception as e:
        logger.error(f"Error in get_department_summary: {e}")
        return []


def calculate_median_salary(salaries_qs):
    '''중간값 계산 - NULL 안전'''
    try:
        salaries = list(salaries_qs.values_list('base_salary', flat=True))
        salaries = [s for s in salaries if s is not None]
        
        if not salaries:
            return 0
            
        salaries.sort()
        n = len(salaries)
        
        if n % 2 == 0:
            return (salaries[n//2 - 1] + salaries[n//2]) / 2
        else:
            return salaries[n//2]
            
    except Exception as e:
        logger.error(f"Error calculating median: {e}")
        return 0


def check_data_quality():
    '''데이터 품질 체크'''
    try:
        from employees.models import Employee
        
        total = Employee.objects.count()
        
        if total == 0:
            return {'score': 0, 'issues': ['No employee data']}
        
        # NULL 값 체크
        null_salary = Employee.objects.filter(
            employment_status='재직',
            current_salary__isnull=True
        ).count()
        
        null_department = Employee.objects.filter(
            employment_status='재직',
            department__isnull=True
        ).count()
        
        issues = []
        if null_salary > 0:
            issues.append(f'{null_salary} employees without salary data')
        if null_department > 0:
            issues.append(f'{null_department} employees without department')
        
        # 품질 점수 (0-100)
        score = 100
        score -= (null_salary / total) * 50
        score -= (null_department / total) * 30
        
        return {
            'score': max(0, round(score)),
            'issues': issues
        }
        
    except Exception as e:
        logger.error(f"Error checking data quality: {e}")
        return {'score': 0, 'issues': ['Unable to check data quality']}
