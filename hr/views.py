"""
HR 관리 시스템 Views
"""

from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required  # 로그인 기능 나중에 구현
from django.db.models import Count, Sum, Avg, Q
from django.contrib import messages
from datetime import datetime, date
from decimal import Decimal

from employees.models import Employee
from .models import (
    JobFamily, JobCategory, JobPosition, JobGrade,
    SalaryGrade, BaseSalary, PerformanceBonus, Allowance,
    CareerHistory, PromotionHistory,
    Education, Certification, Training,
    PerformanceEvaluation,
    Benefit, EmployeeBenefit,
    MonthlySalary
)

# @login_required  # 로그인 기능 나중에 구현
def hr_dashboard(request):
    """HR 대시보드"""
    context = {
        'total_employees': Employee.objects.filter(employment_status='재직').count(),
        'job_families': JobFamily.objects.filter(is_active=True).count(),
        'job_grades': JobGrade.objects.filter(is_active=True).count(),
        'salary_grades': SalaryGrade.objects.filter(is_active=True).count(),
        
        # 급여 통계
        'avg_salary': BaseSalary.objects.filter(is_active=True).aggregate(
            avg=Avg('base_amount')
        )['avg'] or 0,
        
        # 최근 승진
        'recent_promotions': PromotionHistory.objects.select_related(
            'employee', 'from_grade', 'to_grade'
        ).order_by('-promotion_date')[:5],
        
        # 교육 통계
        'total_trainings': Training.objects.filter(
            start_date__year=datetime.now().year
        ).count(),
        
        # 평가 통계
        'recent_evaluations': PerformanceEvaluation.objects.select_related(
            'employee'
        ).order_by('-created_at')[:5],
        
        # 복리후생
        'active_benefits': Benefit.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'hr/dashboard.html', context)


# @login_required  # 로그인 기능 나중에 구현
def job_structure(request):
    """직급/직군 체계 관리"""
    
    # 직군별 통계
    job_families = JobFamily.objects.filter(is_active=True).annotate(
        category_count=Count('categories'),
        employee_count=Count('categories__positions')
    )
    
    # 직급 목록
    job_grades = JobGrade.objects.filter(is_active=True).order_by('level')
    
    context = {
        'job_families': job_families,
        'job_grades': job_grades,
        'total_positions': JobPosition.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'hr/job_structure.html', context)


# @login_required  # 로그인 기능 나중에 구현
def salary_management(request):
    """급여 관리"""
    
    # 급여 등급
    salary_grades = SalaryGrade.objects.filter(is_active=True).order_by('grade_code')
    
    # 직원별 현재 기본급
    employees_with_salary = Employee.objects.filter(
        employment_status='재직'
    ).prefetch_related('base_salaries').annotate(
        current_salary=Sum('base_salaries__base_amount', 
                          filter=Q(base_salaries__is_active=True))
    )
    
    # 최근 성과급
    recent_bonuses = PerformanceBonus.objects.select_related(
        'employee'
    ).order_by('-payment_date')[:10]
    
    context = {
        'salary_grades': salary_grades,
        'employees': employees_with_salary,
        'recent_bonuses': recent_bonuses,
        'total_monthly_salary': MonthlySalary.objects.filter(
            year=datetime.now().year,
            month=datetime.now().month
        ).aggregate(total=Sum('gross_amount'))['total'] or 0,
    }
    
    return render(request, 'hr/salary_management.html', context)


# @login_required  # 로그인 기능 나중에 구현
def employee_salary_detail(request, employee_id):
    """직원 급여 상세"""
    employee = get_object_or_404(Employee, pk=employee_id)
    
    # 기본급 이력
    salary_history = BaseSalary.objects.filter(
        employee=employee
    ).order_by('-effective_date')
    
    # 수당 내역
    allowances = Allowance.objects.filter(
        employee=employee,
        is_active=True
    )
    
    # 성과급 이력
    bonuses = PerformanceBonus.objects.filter(
        employee=employee
    ).order_by('-payment_date')[:12]
    
    # 월급여 내역
    monthly_salaries = MonthlySalary.objects.filter(
        employee=employee
    ).order_by('-year', '-month')[:12]
    
    context = {
        'employee': employee,
        'salary_history': salary_history,
        'allowances': allowances,
        'bonuses': bonuses,
        'monthly_salaries': monthly_salaries,
    }
    
    return render(request, 'hr/employee_salary_detail.html', context)


# @login_required  # 로그인 기능 나중에 구현
def education_management(request):
    """교육/자격증 관리"""
    
    # 학력 통계
    education_stats = Education.objects.values('degree').annotate(
        count=Count('id')
    ).order_by('degree')
    
    # 자격증 목록
    certifications = Certification.objects.filter(
        is_valid=True
    ).select_related('employee').order_by('-issue_date')[:20]
    
    # 최근 교육
    recent_trainings = Training.objects.select_related(
        'employee'
    ).order_by('-start_date')[:20]
    
    context = {
        'education_stats': education_stats,
        'certifications': certifications,
        'recent_trainings': recent_trainings,
        'total_training_hours': Training.objects.filter(
            start_date__year=datetime.now().year,
            is_completed=True
        ).aggregate(total=Sum('hours'))['total'] or 0,
    }
    
    return render(request, 'hr/education_management.html', context)


# @login_required  # 로그인 기능 나중에 구현
def evaluation_list(request):
    """평가 관리"""
    
    evaluations = PerformanceEvaluation.objects.select_related(
        'employee', 'evaluator'
    ).order_by('-evaluation_period')
    
    # 등급별 통계
    rating_stats = PerformanceEvaluation.objects.filter(
        is_finalized=True
    ).values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    context = {
        'evaluations': evaluations[:50],
        'rating_stats': rating_stats,
        'pending_count': PerformanceEvaluation.objects.filter(
            is_finalized=False
        ).count(),
    }
    
    return render(request, 'hr/evaluation_list.html', context)


# @login_required  # 로그인 기능 나중에 구현
def benefits_management(request):
    """복리후생 관리"""
    
    # 복리후생 목록
    benefits = Benefit.objects.filter(is_active=True).annotate(
        employee_count=Count('employeebenefit', 
                            filter=Q(employeebenefit__is_active=True))
    )
    
    # 직원별 복리후생
    employee_benefits = EmployeeBenefit.objects.filter(
        is_active=True
    ).select_related('employee', 'benefit').order_by('-enrollment_date')[:30]
    
    context = {
        'benefits': benefits,
        'employee_benefits': employee_benefits,
        'total_usage': EmployeeBenefit.objects.filter(
            is_active=True
        ).aggregate(total=Sum('usage_amount'))['total'] or 0,
    }
    
    return render(request, 'hr/benefits_management.html', context)
