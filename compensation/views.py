from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Count, Sum, Q
from decimal import Decimal
import json

# Conditional imports to handle missing models
try:
    from employees.models import Employee
except ImportError:
    Employee = None

try:
    from compensation.models import EmployeeCompensation, SalaryTable, CompetencyPayTable
except ImportError:
    EmployeeCompensation = None
    SalaryTable = None
    CompetencyPayTable = None

try:
    from evaluations.models import ComprehensiveEvaluation
except ImportError:
    ComprehensiveEvaluation = None


def compensation_dashboard(request):
    """보상 분석 대시보드"""
    
    # Check if models exist
    if not all([Employee, EmployeeCompensation, ComprehensiveEvaluation]):
        # Return basic template with no data
        context = {
            'total_employees': 0,
            'avg_base_salary': 0,
            'avg_total_compensation': 0,
            'total_pi': 0,
            'grade_stats': [],
            'no_data': True
        }
        return render(request, 'compensation/dashboard_revolutionary_v2.html', context)
    
    try:
        # 기본 통계
        compensations = EmployeeCompensation.objects.all()
        employees = Employee.objects.all()
        
        # 총 직원 수
        total_employees = employees.count()
        
        # 평균 기본급
        avg_base_salary = compensations.aggregate(
            avg=Avg('base_salary')
        )['avg'] or 0
        
        # 평균 총 보상
        avg_total_compensation = compensations.aggregate(
            avg=Avg('total_compensation')
        )['avg'] or 0
        
        # 총 성과급
        total_pi = compensations.aggregate(
            sum=Sum('pi_amount')
        )['sum'] or 0
        
        # 평가등급별 보상 분포
        grade_stats = []
        grades = ['S', 'A+', 'A', 'B+', 'B', 'C', 'D']
    
        for grade in grades:
            # 해당 등급의 직원들 찾기
            employees_with_grade = ComprehensiveEvaluation.objects.filter(
                manager_grade=grade
            ).values_list('employee_id', flat=True)
            
            # 해당 직원들의 보상 데이터
            grade_compensation = compensations.filter(
                employee_id__in=employees_with_grade
            ).aggregate(
                avg_compensation=Avg('total_compensation')
            )['avg_compensation'] or 0
            
            grade_stats.append({
                'grade': grade,
                'avg_compensation': float(grade_compensation)
            })
        
        # 직종별 평균 보상 - N+1 쿼리 문제 해결 (단일 쿼리로 처리)
        job_stats = compensations.values('employee__job_type').annotate(
            avg_compensation=Avg('total_compensation')
        ).exclude(employee__job_type__isnull=True).values(
            'employee__job_type', 'avg_compensation'
        ).order_by('-avg_compensation')
        
        job_stats = [
            {
                'job_type': stat['employee__job_type'],
                'avg_compensation': float(stat['avg_compensation'] or 0)
            }
            for stat in job_stats
        ]
        
        # 부서별 평균 보상 - N+1 쿼리 문제 해결 (단일 쿼리로 처리)
        department_stats = compensations.values('employee__department').annotate(
            avg_compensation=Avg('total_compensation')
        ).exclude(employee__department__isnull=True).values(
            'employee__department', 'avg_compensation'
        ).order_by('-avg_compensation')
        
        department_stats = [
            {
                'department': stat['employee__department'],
                'avg_compensation': float(stat['avg_compensation'] or 0)
            }
            for stat in department_stats
        ]
        
        # 직급별 보상 분포 - N+1 쿼리 문제 해결 (단일 쿼리로 처리)
        position_stats = compensations.values('employee__position').annotate(
            avg_compensation=Avg('total_compensation')
        ).exclude(employee__position__isnull=True).values(
            'employee__position', 'avg_compensation'
        ).order_by('-avg_compensation')
        
        position_stats = [
            {
                'position': stat['employee__position'],
                'avg_compensation': float(stat['avg_compensation'] or 0)
            }
            for stat in position_stats
        ]
        
        # 인사이트 데이터
        top_compensation_employee = employees.filter(
            compensations__isnull=False
        ).annotate(
            total_comp=Sum('compensations__total_compensation')
        ).order_by('-total_comp').first()
        
        top_employee_name = top_compensation_employee.name if top_compensation_employee else "없음"
        
        # 평균 성과급 비율
        avg_pi_ratio = 0
        if avg_total_compensation > 0:
            avg_pi_ratio = (total_pi / (avg_total_compensation * total_employees)) * 100
        
        # 보상 격차
        max_compensation = compensations.aggregate(max=Sum('total_compensation'))['max'] or 0
        min_compensation = compensations.aggregate(min=Sum('total_compensation'))['min'] or 0
        compensation_gap = max_compensation - min_compensation
        
        # 차트 데이터 준비
        grade_labels = [item['grade'] for item in grade_stats]
        grade_data = [item['avg_compensation'] for item in grade_stats]
        
        job_labels = [item['job_type'] for item in job_stats]
        job_data = [item['avg_compensation'] for item in job_stats]
        
        department_labels = [item['department'] for item in department_stats]
        department_data = [item['avg_compensation'] for item in department_stats]
        
        position_labels = [item['position'] for item in position_stats]
        position_data = [item['avg_compensation'] for item in position_stats]
        
        context = {
            'title': '보상 분석 대시보드',
            'total_employees': total_employees,
            'avg_base_salary': avg_base_salary,
            'avg_total_compensation': avg_total_compensation,
            'total_pi': total_pi,
            'top_compensation_employee': top_employee_name,
            'avg_pi_ratio': avg_pi_ratio,
            'compensation_gap': compensation_gap,
            'grade_labels': json.dumps(grade_labels),
            'grade_data': json.dumps(grade_data),
            'job_labels': json.dumps(job_labels),
            'job_data': json.dumps(job_data),
            'department_labels': json.dumps(department_labels),
            'department_data': json.dumps(department_data),
            'position_labels': json.dumps(position_labels),
            'position_data': json.dumps(position_data),
            }
        
        return render(request, 'compensation/dashboard_revolutionary_v2.html', context)
        
    except Exception as e:
        # Handle any database errors
        context = {
            'total_employees': 0,
            'avg_base_salary': 0,
            'avg_total_compensation': 0,
            'total_pi': 0,
            'grade_stats': [],
            'no_data': True,
            'error_message': str(e)
        }
        return render(request, 'compensation/dashboard_revolutionary_v2.html', context)


def api_compensation_summary(request):
    """보상 요약 데이터 API"""
    
    # Check if models exist
    if not all([Employee, EmployeeCompensation, ComprehensiveEvaluation]):
        return JsonResponse({
            'error': 'Models not available',
            'data': {
                'avg_base_salary': 0,
                'avg_total_compensation': 0,
                'total_pi_amount': 0,
                'compensation_count': 0
            }
        })
    
    try:
        # 전체 보상 통계
        total_stats = EmployeeCompensation.objects.aggregate(
            avg_base_salary=Avg('base_salary'),
            avg_total_compensation=Avg('total_compensation'),
            avg_pi_amount=Avg('pi_amount'),
            total_pi_amount=Sum('pi_amount')
        )
        
        # 직종별 평균 보상
        job_type_stats = EmployeeCompensation.objects.values(
            'employee__job_type'
        ).annotate(
            avg_compensation=Avg('total_compensation'),
            employee_count=Count('employee', distinct=True)
        ).order_by('-avg_compensation')
        
        # 성장레벨별 평균 보상
        level_stats = EmployeeCompensation.objects.values(
            'employee__growth_level'
        ).annotate(
            avg_compensation=Avg('total_compensation'),
            employee_count=Count('employee', distinct=True)
        ).order_by('employee__growth_level')
        
        return JsonResponse({
            'success': True,
            'total_stats': {
                'avg_base_salary': float(total_stats['avg_base_salary'] or 0),
                'avg_total_compensation': float(total_stats['avg_total_compensation'] or 0),
                'avg_pi_amount': float(total_stats['avg_pi_amount'] or 0),
                'total_pi_amount': float(total_stats['total_pi_amount'] or 0),
            },
            'job_type_stats': list(job_type_stats),
            'level_stats': list(level_stats),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def api_grade_distribution(request):
    """평가등급별 분포 API"""
    try:
        # 평가등급별 직원 수
        grade_distribution = ComprehensiveEvaluation.objects.values(
            'manager_grade'
        ).annotate(
            employee_count=Count('employee')
        ).order_by('manager_grade')
        
        # 평가등급별 평균 보상
        grade_compensation = EmployeeCompensation.objects.filter(
            evaluation__isnull=False
        ).values(
            'evaluation__manager_grade'
        ).annotate(
            avg_compensation=Avg('total_compensation'),
            avg_pi_amount=Avg('pi_amount'),
            employee_count=Count('employee', distinct=True)
        ).order_by('evaluation__manager_grade')
        
        # 고성과자 vs 일반 보상 비교
        high_performers = EmployeeCompensation.objects.filter(
            evaluation__manager_grade__in=['S', 'A+']
        ).aggregate(
            avg_compensation=Avg('total_compensation'),
            avg_pi_amount=Avg('pi_amount')
        )
        
        normal_performers = EmployeeCompensation.objects.filter(
            evaluation__manager_grade__in=['B', 'B+']
        ).aggregate(
            avg_compensation=Avg('total_compensation'),
            avg_pi_amount=Avg('pi_amount')
        )
        
        return JsonResponse({
            'success': True,
            'grade_distribution': list(grade_distribution),
            'grade_compensation': list(grade_compensation),
            'performance_comparison': {
                'high_performers': {
                    'avg_compensation': float(high_performers['avg_compensation'] or 0),
                    'avg_pi_amount': float(high_performers['avg_pi_amount'] or 0),
                },
                'normal_performers': {
                    'avg_compensation': float(normal_performers['avg_compensation'] or 0),
                    'avg_pi_amount': float(normal_performers['avg_pi_amount'] or 0),
                }
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def api_level_comparison(request):
    """성장레벨별 보상 비교 API"""
    try:
        # 성장레벨별 보상 구성 분석
        level_breakdown = []
        
        for level in range(1, 7):
            level_data = EmployeeCompensation.objects.filter(
                employee__growth_level=level
            ).aggregate(
                avg_base_salary=Avg('base_salary'),
                avg_competency_pay=Avg('competency_pay'),
                avg_pi_amount=Avg('pi_amount'),
                avg_position_allowance=Avg('position_allowance'),
                avg_total_compensation=Avg('total_compensation'),
                employee_count=Count('employee', distinct=True)
            )
            
            if level_data['employee_count'] > 0:
                level_breakdown.append({
                    'level': level,
                    'avg_base_salary': float(level_data['avg_base_salary'] or 0),
                    'avg_competency_pay': float(level_data['avg_competency_pay'] or 0),
                    'avg_pi_amount': float(level_data['avg_pi_amount'] or 0),
                    'avg_position_allowance': float(level_data['avg_position_allowance'] or 0),
                    'avg_total_compensation': float(level_data['avg_total_compensation'] or 0),
                    'employee_count': level_data['employee_count']
                })
        
        # 직책자 vs 팀원 보상 비교
        managers = EmployeeCompensation.objects.filter(
            position_allowance__gt=0
        ).aggregate(
            avg_compensation=Avg('total_compensation'),
            avg_position_allowance=Avg('position_allowance'),
            employee_count=Count('employee', distinct=True)
        )
        
        team_members = EmployeeCompensation.objects.filter(
            position_allowance__isnull=True
        ).aggregate(
            avg_compensation=Avg('total_compensation'),
            employee_count=Count('employee', distinct=True)
        )
        
        return JsonResponse({
            'success': True,
            'level_breakdown': level_breakdown,
            'role_comparison': {
                'managers': {
                    'avg_compensation': float(managers['avg_compensation'] or 0),
                    'avg_position_allowance': float(managers['avg_position_allowance'] or 0),
                    'employee_count': managers['employee_count']
                },
                'team_members': {
                    'avg_compensation': float(team_members['avg_compensation'] or 0),
                    'employee_count': team_members['employee_count']
                }
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def api_job_type_analysis(request):
    """직종별 분석 API"""
    try:
        # 직종별 역량급 차이
        job_type_competency = CompetencyPayTable.objects.values(
            'job_type'
        ).annotate(
            avg_competency_pay=Avg('competency_pay'),
            min_competency_pay=Avg('competency_pay'),
            max_competency_pay=Avg('competency_pay')
        ).order_by('-avg_competency_pay')
        
        # 직종별 평균 보상 구성
        job_type_compensation = EmployeeCompensation.objects.values(
            'employee__job_type'
        ).annotate(
            avg_base_salary=Avg('base_salary'),
            avg_competency_pay=Avg('competency_pay'),
            avg_pi_amount=Avg('pi_amount'),
            avg_total_compensation=Avg('total_compensation'),
            employee_count=Count('employee', distinct=True)
        ).order_by('-avg_total_compensation')
        
        return JsonResponse({
            'success': True,
            'job_type_competency': list(job_type_competency),
            'job_type_compensation': list(job_type_compensation),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def compensation_calculator(request):
    """보상 계산기 페이지"""
    context = {
        'page_title': '보상 계산기',
        'description': '직원별 보상을 계산하고 시뮬레이션합니다.',
    }
    return render(request, 'compensation/calculator_revolutionary.html', context)


def compensation_reports(request):
    """보상 리포트 페이지"""
    context = {
        'page_title': '보상 리포트',
        'description': '보상 관련 각종 리포트를 조회합니다.',
    }
    return render(request, 'compensation/reports_revolutionary.html', context)


def compensation_settings(request):
    """보상 설정 페이지"""
    context = {
        'page_title': '보상 설정',
        'description': '보상 테이블 및 정책을 설정합니다.',
    }
    return render(request, 'compensation/settings_revolutionary.html', context)
