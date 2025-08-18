from django.shortcuts import render
from django.db.models import Count, Avg, Q, F, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation, EvaluationPeriod
from compensation.models import EmployeeCompensation


def executive_dashboard(request):
    """경영진 대시보드 - 핵심 지표 요약"""
    # 전체 인력 현황
    total_employees = Employee.objects.filter(employment_status='재직').count()
    new_hires_month = Employee.objects.filter(
        employment_status='재직',
        hire_date__gte=timezone.now().date() - timedelta(days=30)
    ).count()
    
    # 부서별 인원 (상위 5개)
    dept_summary = Employee.objects.filter(
        employment_status='재직'
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # 평균 근속연수 계산
    avg_tenure = Employee.objects.filter(
        employment_status='재직'
    ).annotate(
        tenure_days=timezone.now().date() - F('hire_date')
    ).aggregate(avg=Avg('tenure_days'))['avg']
    
    avg_tenure_years = avg_tenure.days / 365 if avg_tenure else 0
    
    # 이직률 계산 (최근 3개월)
    three_months_ago = timezone.now().date() - timedelta(days=90)
    resigned_count = Employee.objects.filter(
        employment_status='퇴직',
        updated_at__date__gte=three_months_ago
    ).count()
    turnover_rate = (resigned_count / total_employees * 100) if total_employees > 0 else 0
    
    context = {
        'total_employees': total_employees,
        'new_hires_month': new_hires_month,
        'avg_tenure_years': round(avg_tenure_years, 1),
        'turnover_rate': round(turnover_rate, 1),
        'dept_summary': list(dept_summary),
        'last_updated': timezone.now(),
    }
    
    return render(request, 'dashboard/executive.html', context)


def hr_dashboard(request):
    """HR 대시보드 - 인사 분석"""
    # 기존 AIRISS analytics 내용을 여기로 이동
    total_employees = Employee.objects.filter(employment_status='재직').count()
    
    # 부서별 인원 현황
    dept_distribution = Employee.objects.filter(
        employment_status='재직'
    ).values('department').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 직급별 분포
    position_distribution = Employee.objects.filter(
        employment_status='재직'
    ).values('new_position').annotate(
        count=Count('id')
    ).order_by('growth_level')
    
    # 입퇴사 추세 (최근 6개월)
    hiring_trend = []
    resignation_trend = []
    
    for i in range(6):
        month_start = (timezone.now().date().replace(day=1) - timedelta(days=i*30))
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        hired = Employee.objects.filter(
            hire_date__gte=month_start,
            hire_date__lte=month_end
        ).count()
        
        resigned = Employee.objects.filter(
            employment_status='퇴직',
            updated_at__date__gte=month_start,
            updated_at__date__lte=month_end
        ).count()
        
        hiring_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'hired': hired,
            'resigned': resigned
        })
    
    hiring_trend.reverse()
    
    context = {
        'total_employees': total_employees,
        'dept_distribution': list(dept_distribution),
        'position_distribution': list(position_distribution),
        'hiring_trend': hiring_trend,
    }
    
    return render(request, 'dashboard/hr_analytics.html', context)


def workforce_overview(request):
    """인력 현황 - 상세 인력 분석"""
    # 직군별 분석
    job_group_stats = Employee.objects.filter(
        employment_status='재직'
    ).values('job_group').annotate(
        count=Count('id'),
        avg_level=Avg('growth_level')
    )
    
    # 직종별 분석
    job_type_stats = Employee.objects.filter(
        employment_status='재직'
    ).values('job_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # 고용형태별 분석
    employment_type_stats = Employee.objects.filter(
        employment_status='재직'
    ).values('employment_type').annotate(
        count=Count('id')
    )
    
    # 근속연수 분포
    tenure_distribution = []
    ranges = [(0, 1, '1년 미만'), (1, 3, '1-3년'), (3, 5, '3-5년'), 
              (5, 10, '5-10년'), (10, 100, '10년 이상')]
    
    for min_year, max_year, label in ranges:
        count = Employee.objects.filter(
            employment_status='재직',
            hire_date__lte=timezone.now().date() - timedelta(days=min_year*365),
            hire_date__gt=timezone.now().date() - timedelta(days=max_year*365)
        ).count()
        tenure_distribution.append({'label': label, 'count': count})
    
    context = {
        'job_group_stats': list(job_group_stats),
        'job_type_stats': list(job_type_stats),
        'employment_type_stats': list(employment_type_stats),
        'tenure_distribution': tenure_distribution,
    }
    
    return render(request, 'dashboard/workforce.html', context)


def performance_analytics(request):
    """성과 분석 대시보드"""
    # 성과 등급 분포 (목업 데이터 - 추후 실제 데이터로 교체)
    performance_distribution = [
        {'grade': 'S', 'count': 15, 'percentage': 7.5},
        {'grade': 'A', 'count': 45, 'percentage': 22.5},
        {'grade': 'B', 'count': 120, 'percentage': 60},
        {'grade': 'C', 'count': 15, 'percentage': 7.5},
        {'grade': 'D', 'count': 5, 'percentage': 2.5},
    ]
    
    # 부서별 평균 성과 (목업)
    dept_performance = [
        {'department': 'IT', 'avg_score': 85},
        {'department': 'HR', 'avg_score': 82},
        {'department': 'FINANCE', 'avg_score': 88},
        {'department': 'MARKETING', 'avg_score': 79},
        {'department': 'SALES', 'avg_score': 83},
    ]
    
    context = {
        'performance_distribution': performance_distribution,
        'dept_performance': dept_performance,
        'evaluation_period': '2024년 상반기',  # 임시
    }
    
    return render(request, 'dashboard/performance.html', context)


def compensation_analytics(request):
    """보상 분석 대시보드"""
    # 직급별 평균 급여 (목업 데이터)
    salary_by_position = [
        {'position': '사원', 'avg_salary': 3500, 'min': 3000, 'max': 4000},
        {'position': '대리', 'avg_salary': 4500, 'min': 4000, 'max': 5000},
        {'position': '과장', 'avg_salary': 5500, 'min': 5000, 'max': 6000},
        {'position': '차장', 'avg_salary': 6500, 'min': 6000, 'max': 7000},
        {'position': '부장', 'avg_salary': 8000, 'min': 7000, 'max': 9000},
    ]
    
    # 부서별 평균 급여 (목업)
    salary_by_dept = [
        {'department': 'IT', 'avg_salary': 5800},
        {'department': 'HR', 'avg_salary': 5200},
        {'department': 'FINANCE', 'avg_salary': 6200},
        {'department': 'MARKETING', 'avg_salary': 5500},
        {'department': 'SALES', 'avg_salary': 5700},
    ]
    
    # 급여 분포
    salary_distribution = [
        {'range': '3000-4000', 'count': 25},
        {'range': '4000-5000', 'count': 35},
        {'range': '5000-6000', 'count': 30},
        {'range': '6000-7000', 'count': 10},
        {'range': '7000+', 'count': 3},
    ]
    
    context = {
        'salary_by_position': salary_by_position,
        'salary_by_dept': salary_by_dept,
        'salary_distribution': salary_distribution,
        'total_payroll': 567800000,  # 목업
        'avg_salary': 5500000,  # 목업
    }
    
    return render(request, 'dashboard/compensation.html', context)