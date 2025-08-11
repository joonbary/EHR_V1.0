from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
# from django.contrib.auth.decorators import login_required  # 로그인 기능은 나중에 구현
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction, models
from decimal import Decimal
from datetime import date
import json

from employees.models import Employee
from .models import (
    EvaluationPeriod, Task, ContributionEvaluation, 
    ExpertiseEvaluation, ImpactEvaluation, ComprehensiveEvaluation,
    CalibrationSession, CONTRIBUTION_SCORING_CHART, EXPERTISE_SCORING_CHART, 
    IMPACT_SCORING_CHART, GRADE_CHOICES
)
from django.utils import timezone


def contribution_list(request):
    """기여도 평가 대상자 목록"""
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 평가 대상 직원들 - N+1 쿼리 문제 해결
    from django.db.models import Prefetch, Count, Q
    
    employees = Employee.objects.filter(
        employment_status='재직'
    ).select_related(
        'user', 'manager'
    ).prefetch_related(
        Prefetch(
            'contribution_evaluations',
            queryset=ContributionEvaluation.objects.filter(evaluation_period=active_period),
            to_attr='period_contributions'
        ),
        Prefetch(
            'tasks',
            queryset=Task.objects.filter(evaluation_period=active_period),
            to_attr='period_tasks'
        )
    ).order_by('department', 'name')
    
    employee_data = []
    for employee in employees:
        # 기여도 평가 상태 확인 (prefetched data 사용)
        contribution_eval = employee.period_contributions[0] if employee.period_contributions else None
        
        # Task 개수 및 완료율 (prefetched data 사용)
        tasks = employee.period_tasks
        
        total_tasks = len(tasks) if hasattr(tasks, '__len__') else 0
        completed_tasks = len([t for t in tasks if t.status == 'COMPLETED']) if tasks else 0
        task_completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
        
        # 평가 상태
        if contribution_eval and contribution_eval.is_achieved:
            status = 'completed'
        elif contribution_eval:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'contribution_eval': contribution_eval,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'task_completion_rate': task_completion_rate,
            'contribution_score': contribution_eval.contribution_score if contribution_eval else None,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/contribution_list_revolutionary.html', context)


def expertise_list(request):
    """전문성 평가 대상자 목록"""
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 평가 대상 직원들
    employees = Employee.objects.filter(employment_status='재직').order_by('department', 'name')
    
    employee_data = []
    for employee in employees:
        # 전문성 평가 상태 확인
        expertise_eval = ExpertiseEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first()
        
        # 평가 상태
        if expertise_eval and expertise_eval.is_achieved:
            status = 'completed'
        elif expertise_eval:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'expertise_eval': expertise_eval,
            'total_score': expertise_eval.total_score if expertise_eval else None,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/expertise_list.html', context)


def impact_list(request):
    """영향력 평가 대상자 목록"""
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 평가 대상 직원들
    employees = Employee.objects.filter(employment_status='재직').order_by('department', 'name')
    
    employee_data = []
    for employee in employees:
        # 영향력 평가 상태 확인
        impact_eval = ImpactEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first()
        
        # 평가 상태
        if impact_eval and impact_eval.is_achieved:
            status = 'completed'
        elif impact_eval:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'impact_eval': impact_eval,
            'total_score': impact_eval.total_score if impact_eval else None,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/impact_list.html', context)


def evaluation_dashboard(request):
    """평가 대시보드 - 4단계 진행상황 표시"""
    # 활성화된 평가 기간
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/dashboard_revolutionary.html')
    
    # 현재 사용자의 평가 진행상황
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return render(request, 'evaluations/dashboard_revolutionary.html')
    
    # 각 평가 단계별 상태 확인
    contribution_eval = ContributionEvaluation.objects.filter(
        employee=employee, evaluation_period=active_period
    ).first()
    
    expertise_eval = ExpertiseEvaluation.objects.filter(
        employee=employee, evaluation_period=active_period
    ).first()
    
    impact_eval = ImpactEvaluation.objects.filter(
        employee=employee, evaluation_period=active_period
    ).first()
    
    comprehensive_eval = ComprehensiveEvaluation.objects.filter(
        employee=employee, evaluation_period=active_period
    ).first()
    
    # 진행률 계산
    progress = {
        'contribution': 25 if contribution_eval else 0,
        'expertise': 25 if expertise_eval else 0,
        'impact': 25 if impact_eval else 0,
        'comprehensive': 25 if comprehensive_eval else 0,
    }
    
    total_progress = sum(progress.values())
    
    context = {
        'active_period': active_period,
        'employee': employee,
        'progress': progress,
        'total_progress': total_progress,
        'contribution_eval': contribution_eval,
        'expertise_eval': expertise_eval,
        'impact_eval': impact_eval,
        'comprehensive_eval': comprehensive_eval,
    }
    
    return render(request, 'evaluations/dashboard_enhanced.html', context)


def contribution_evaluation(request, employee_id):
    """기여도 평가 - Task 기반 + Scoring Chart"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ContributionEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={'evaluator': Employee.objects.filter(employment_status='재직').first()}
    )
    
    # Task 목록
    tasks = Task.objects.filter(employee=employee, evaluation_period=active_period)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Task 업데이트
            for task in tasks:
                task_id = str(task.id)
                if f'task_{task_id}_title' in request.POST:
                    task.title = request.POST[f'task_{task_id}_title']
                    task.description = request.POST.get(f'task_{task_id}_description', '')
                    task.weight = Decimal(request.POST[f'task_{task_id}_weight'])
                    task.contribution_method = request.POST[f'task_{task_id}_method']
                    task.contribution_scope = request.POST[f'task_{task_id}_scope']
                    task.target_value = Decimal(request.POST[f'task_{task_id}_target']) if request.POST[f'task_{task_id}_target'] else None
                    task.actual_value = Decimal(request.POST[f'task_{task_id}_actual']) if request.POST[f'task_{task_id}_actual'] else None
                    task.target_unit = request.POST.get(f'task_{task_id}_unit', '')
                    task.save()
            
            # 평가 계산
            evaluation.calculate_from_tasks()
            evaluation.comments = request.POST.get('comments', '')
            evaluation.evaluated_date = active_period.end_date
            evaluation.save()
            
            messages.success(request, "기여도 평가가 저장되었습니다.")
            return redirect('evaluations:dashboard')
    
    # Scoring Chart 정보
    scoring_info = {
        'contribution_chart': CONTRIBUTION_SCORING_CHART,
        'method_choices': Task._meta.get_field('contribution_method').choices,
        'scope_choices': Task._meta.get_field('contribution_scope').choices,
    }
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'evaluation': evaluation,
        'tasks': tasks,
        'scoring_info': scoring_info,
    }
    
    return render(request, 'evaluations/contribution_evaluation.html', context)


def expertise_evaluation(request, employee_id):
    """전문성 평가 - 10개 체크리스트"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ExpertiseEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={
            'evaluator': Employee.objects.filter(employment_status='재직').first(),
            'required_level': employee.growth_level,
            # 기본값 설정
            'creative_solution': 2, 'technical_innovation': 2, 'process_improvement': 2,
            'knowledge_sharing': 2, 'mentoring': 2, 'cross_functional': 2,
            'strategic_thinking': 2, 'business_acumen': 2, 'industry_trend': 2,
            'continuous_learning': 2,
            'strategic_contribution': 2, 'interactive_contribution': 2,
            'technical_expertise': 2, 'business_understanding': 2,
        }
    )
    
    if request.method == 'POST':
        with transaction.atomic():
            # 체크리스트 항목 업데이트
            checklist_fields = [
                'creative_solution', 'technical_innovation', 'process_improvement',
                'knowledge_sharing', 'mentoring', 'cross_functional',
                'strategic_thinking', 'business_acumen', 'industry_trend',
                'continuous_learning'
            ]
            
            for field in checklist_fields:
                if field in request.POST:
                    setattr(evaluation, field, int(request.POST[field]))
            
            # 기존 필드들도 업데이트
            legacy_fields = ['strategic_contribution', 'interactive_contribution', 
                           'technical_expertise', 'business_understanding']
            for field in legacy_fields:
                if field in request.POST:
                    setattr(evaluation, field, int(request.POST[field]))
            
            # 전문성 초점
            evaluation.expertise_focus = request.POST.get('expertise_focus', 'balanced')
            
            # 점수 계산
            evaluation.calculate_total_score()
            evaluation.comments = request.POST.get('comments', '')
            evaluation.evaluated_date = active_period.end_date
            evaluation.save()
            
            messages.success(request, "전문성 평가가 저장되었습니다.")
            return redirect('evaluations:dashboard')
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'evaluation': evaluation,
        'scoring_chart': EXPERTISE_SCORING_CHART,
    }
    
    return render(request, 'evaluations/expertise_evaluation.html', context)


def impact_evaluation(request, employee_id):
    """영향력 평가 - 6개 항목"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ImpactEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={
            'evaluator': Employee.objects.filter(employment_status='재직').first(),
            # 기본값 설정
            'customer_focus': 2, 'collaboration': 2, 'innovation': 2,
            'team_leadership': 2, 'organizational_impact': 2, 'external_networking': 2,
        }
    )
    
    if request.method == 'POST':
        with transaction.atomic():
            # 영향력 범위 및 핵심가치/리더십 평가
            evaluation.impact_scope = request.POST.get('impact_scope', 'org')
            evaluation.core_values_practice = request.POST.get('core_values_practice', 'limited_values')
            evaluation.leadership_demonstration = request.POST.get('leadership_demonstration', 'limited_leadership')
            
            # 기존 평가 항목들
            legacy_fields = ['customer_focus', 'collaboration', 'innovation',
                           'team_leadership', 'organizational_impact', 'external_networking']
            for field in legacy_fields:
                if field in request.POST:
                    setattr(evaluation, field, int(request.POST[field]))
            
            # 점수 계산
            evaluation.calculate_total_score()
            evaluation.comments = request.POST.get('comments', '')
            evaluation.evaluated_date = active_period.end_date
            evaluation.save()
            
            messages.success(request, "영향력 평가가 저장되었습니다.")
            return redirect('evaluations:dashboard')
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'evaluation': evaluation,
        'scoring_chart': IMPACT_SCORING_CHART,
    }
    
    return render(request, 'evaluations/impact_evaluation.html', context)


@csrf_exempt
def calculate_score_ajax(request):
    """AJAX를 통한 실시간 점수 계산"""
    if request.method == 'POST':
        try:
            from .services import EvaluationScoreCalculator
            
            data = json.loads(request.body)
            evaluation_type = data.get('type')
            
            if evaluation_type == 'contribution':
                # 기여도 점수 계산
                method = data.get('method')
                scope = data.get('scope')
                achievement_rate = float(data.get('achievement_rate', 100))
                
                base_score, final_score = EvaluationScoreCalculator.calculate_contribution_score(
                    scope, method, achievement_rate
                )
                
                return JsonResponse({
                    'score': final_score,
                    'base_score': base_score,
                    'achievement_rate': achievement_rate
                })
            
            elif evaluation_type == 'expertise':
                # 전문성 점수 계산
                scores = data.get('scores', {})
                expertise_focus = data.get('expertise_focus', 'balanced')
                
                total_score, is_achieved = EvaluationScoreCalculator.calculate_expertise_score(
                    scores, expertise_focus
                )
                
                return JsonResponse({
                    'score': total_score,
                    'is_achieved': is_achieved
                })
            
            elif evaluation_type == 'impact':
                # 영향력 점수 계산
                scope = data.get('scope')
                values_practice = data.get('values_practice')
                leadership = data.get('leadership')
                
                total_score, is_achieved = EvaluationScoreCalculator.calculate_impact_score(
                    scope, values_practice, leadership
                )
                
                return JsonResponse({
                    'score': total_score,
                    'is_achieved': is_achieved
                })
            
            else:
                return JsonResponse({'error': 'Invalid evaluation type'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def my_evaluations_dashboard(request):
    """피평가자 대시보드 - 나의 평가 현황"""
    
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    # 활성 평가 기간
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    # 나의 목표(Task) 현황
    my_tasks = Task.objects.filter(
        employee=employee,
        evaluation_period=active_period
    ) if active_period else []
    
    # 평가 진행 상황
    evaluations = {
        'contribution': ContributionEvaluation.objects.filter(
            employee=employee, 
            evaluation_period=active_period
        ).first() if active_period else None,
        'expertise': ExpertiseEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first() if active_period else None,
        'impact': ImpactEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period  
        ).first() if active_period else None,
        'comprehensive': ComprehensiveEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first() if active_period else None,
    }
    
    # 과거 평가 이력
    past_evaluations = ComprehensiveEvaluation.objects.filter(
        employee=employee,
        status='COMPLETED'
    ).order_by('-evaluation_period__year', '-evaluation_period__period_type')[:5]
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'my_tasks': my_tasks,
        'evaluations': evaluations,
        'past_evaluations': past_evaluations,
    }
    
    return render(request, 'evaluations/my_evaluations_dashboard.html', context)


def my_goals(request):
    """나의 목표 관리"""
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:my_evaluations')
    
    tasks = Task.objects.filter(
        employee=employee,
        evaluation_period=active_period
    ).order_by('-weight', 'title')
    
    # 총 가중치 계산
    total_weight = sum(task.weight for task in tasks)
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'tasks': tasks,
        'total_weight': total_weight,
        'remaining_weight': 100 - total_weight,
    }
    
    return render(request, 'evaluations/my_goals.html', context)


def create_goal(request):
    """새 목표 생성"""
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:my_goals')
    
    if request.method == 'POST':
        try:
            # 현재 총 가중치 확인
            current_weight = Task.objects.filter(
                employee=employee,
                evaluation_period=active_period
            ).aggregate(models.Sum('weight'))['weight__sum'] or 0
            
            new_weight = Decimal(request.POST.get('weight', 0))
            
            if current_weight + new_weight > 100:
                messages.error(request, f"가중치 합이 100%를 초과합니다. (현재: {current_weight}%)")
                return redirect('evaluations:my_goals')
            
            task = Task.objects.create(
                employee=employee,
                evaluation_period=active_period,
                title=request.POST['title'],
                description=request.POST.get('description', ''),
                weight=new_weight,
                contribution_method=request.POST.get('contribution_method', 'leading'),
                contribution_scope=request.POST.get('contribution_scope', 'independent'),
                target_value=Decimal(request.POST['target_value']) if request.POST.get('target_value') else None,
                target_unit=request.POST.get('target_unit', ''),
                status='PLANNED'
            )
            
            messages.success(request, "목표가 성공적으로 생성되었습니다.")
            return redirect('evaluations:my_goals')
            
        except Exception as e:
            messages.error(request, f"목표 생성 중 오류가 발생했습니다: {str(e)}")
            return redirect('evaluations:my_goals')
    
    # 현재 총 가중치 계산
    current_weight = Task.objects.filter(
        employee=employee,
        evaluation_period=active_period
    ).aggregate(models.Sum('weight'))['weight__sum'] or 0
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'remaining_weight': 100 - current_weight,
        'contribution_methods': Task._meta.get_field('contribution_method').choices,
        'contribution_scopes': Task._meta.get_field('contribution_scope').choices,
    }
    
    return render(request, 'evaluations/create_goal.html', context)


def update_goal(request, task_id):
    """목표 수정"""
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    task = get_object_or_404(Task, id=task_id, employee=employee)
    
    if request.method == 'POST':
        try:
            # 실적 업데이트
            task.actual_value = Decimal(request.POST['actual_value']) if request.POST.get('actual_value') else None
            task.status = request.POST.get('status', task.status)
            
            # 달성률 계산
            if task.target_value and task.actual_value:
                task.achievement_rate = round((task.actual_value / task.target_value) * 100, 2)
            
            task.save()
            
            messages.success(request, "목표가 성공적으로 업데이트되었습니다.")
            return redirect('evaluations:my_goals')
            
        except Exception as e:
            messages.error(request, f"목표 업데이트 중 오류가 발생했습니다: {str(e)}")
    
    return redirect('evaluations:my_goals')


def my_evaluation_results(request):
    """나의 평가 결과 확인"""
    # 임시로 첫 번째 직원 사용 (나중에 로그인 기능 구현 시 수정)
    employee = Employee.objects.filter(employment_status='재직').first()
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    # 완료된 평가 결과들
    comprehensive_evaluations = ComprehensiveEvaluation.objects.filter(
        employee=employee,
        status__in=['COMPLETED', 'IN_REVIEW']
    ).select_related(
        'evaluation_period',
        'contribution_evaluation',
        'expertise_evaluation', 
        'impact_evaluation'
    ).order_by('-evaluation_period__year', '-evaluation_period__period_type')
    
    context = {
        'employee': employee,
        'evaluations': comprehensive_evaluations,
    }
    
    return render(request, 'evaluations/my_evaluation_results.html', context)


def evaluator_dashboard(request):
    """평가자 대시보드"""
    # 임시로 첫 번째 직원을 평가자로 사용 (나중에 로그인 기능 구현 시 수정)
    evaluator = Employee.objects.filter(employment_status='재직').first()
    if not evaluator:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    # 활성 평가 기간
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    # 내가 평가해야 할 직원들 (내 부하직원들)
    subordinates = Employee.objects.filter(
        manager=evaluator,
        employment_status='재직'
    )
    
    # 평가 진행 상황
    evaluation_status = []
    for subordinate in subordinates:
        status = {
            'employee': subordinate,
            'contribution': ContributionEvaluation.objects.filter(
                employee=subordinate,
                evaluation_period=active_period
            ).exists() if active_period else False,
            'expertise': ExpertiseEvaluation.objects.filter(
                employee=subordinate,
                evaluation_period=active_period
            ).exists() if active_period else False,
            'impact': ImpactEvaluation.objects.filter(
                employee=subordinate,
                evaluation_period=active_period
            ).exists() if active_period else False,
        }
        status['completed'] = all([status['contribution'], status['expertise'], status['impact']])
        evaluation_status.append(status)
    
    context = {
        'evaluator': evaluator,
        'active_period': active_period,
        'evaluation_status': evaluation_status,
        'total_count': len(subordinates),
        'completed_count': sum(1 for s in evaluation_status if s['completed']),
    }
    
    return render(request, 'evaluations/evaluator_dashboard.html', context)


def evaluate_employee(request, employee_id):
    """직원 평가 통합 화면"""
    # 임시로 첫 번째 직원을 평가자로 사용 (나중에 로그인 기능 구현 시 수정)
    evaluator = Employee.objects.filter(employment_status='재직').first()
    if not evaluator:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return redirect('home')
    
    employee = get_object_or_404(Employee, id=employee_id)
    
    # 임시로 권한 확인 스킵 (나중에 로그인 기능 구현 시 수정)
    # if employee.manager != evaluator:
    #     messages.error(request, "해당 직원을 평가할 권한이 없습니다.")
    #     return redirect('evaluations:evaluator_dashboard')
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:evaluator_dashboard')
    
    # 각 평가 항목별 현황
    evaluations = {
        'contribution': ContributionEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first(),
        'expertise': ExpertiseEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first(),
        'impact': ImpactEvaluation.objects.filter(
            employee=employee,
            evaluation_period=active_period
        ).first(),
    }
    
    # 직원의 목표(Task) 목록
    tasks = Task.objects.filter(
        employee=employee,
        evaluation_period=active_period
    )
    
    context = {
        'evaluator': evaluator,
        'employee': employee,
        'active_period': active_period,
        'evaluations': evaluations,
        'tasks': tasks,
    }
    
    return render(request, 'evaluations/evaluate_employee.html', context)


def hr_admin_dashboard(request):
    """인사담당자 대시보드"""
    # 임시로 권한 체크 스킵 (나중에 로그인 기능 구현 시 수정)
    # 현재는 모든 사용자가 접근 가능
    
    # 활성 평가 기간
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    all_periods = EvaluationPeriod.objects.all().order_by('-year', '-period_type')
    
    # 전체 통계
    total_employees = Employee.objects.filter(employment_status='재직').count()
    
    if active_period:
        # 평가 진행 현황
        contribution_count = ContributionEvaluation.objects.filter(
            evaluation_period=active_period
        ).count()
        expertise_count = ExpertiseEvaluation.objects.filter(
            evaluation_period=active_period
        ).count()
        impact_count = ImpactEvaluation.objects.filter(
            evaluation_period=active_period
        ).count()
        comprehensive_count = ComprehensiveEvaluation.objects.filter(
            evaluation_period=active_period
        ).count()
        
        # 등급별 분포
        grade_distribution = ComprehensiveEvaluation.objects.filter(
            evaluation_period=active_period,
            final_grade__isnull=False
        ).values('final_grade').annotate(
            count=models.Count('id')
        ).order_by('final_grade')
        
        # 부서별 평가 진행률
        department_stats = []
        departments = Employee.objects.filter(
            employment_status='재직'
        ).values_list('department', flat=True).distinct()
        
        for dept in departments:
            dept_employees = Employee.objects.filter(
                department=dept,
                employment_status='재직'
            )
            dept_evaluated = ComprehensiveEvaluation.objects.filter(
                employee__department=dept,
                evaluation_period=active_period
            ).count()
            
            department_stats.append({
                'department': dept,
                'total': dept_employees.count(),
                'evaluated': dept_evaluated,
                'progress': round((dept_evaluated / dept_employees.count() * 100) if dept_employees.count() > 0 else 0, 1)
            })
    else:
        contribution_count = expertise_count = impact_count = comprehensive_count = 0
        grade_distribution = []
        department_stats = []
    
    context = {
        'active_period': active_period,
        'all_periods': all_periods,
        'total_employees': total_employees,
        'contribution_count': contribution_count,
        'expertise_count': expertise_count,
        'impact_count': impact_count,
        'comprehensive_count': comprehensive_count,
        'grade_distribution': grade_distribution,
        'department_stats': department_stats,
    }
    
    return render(request, 'evaluations/hr_admin_dashboard.html', context)


def period_management(request):
    """평가 기간 관리"""
    # 임시로 권한 체크 스킵 (나중에 로그인 기능 구현 시 수정)
    # 현재는 모든 사용자가 접근 가능
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            # 새 평가 기간 생성
            try:
                # 기존 활성 기간 비활성화
                EvaluationPeriod.objects.filter(is_active=True).update(is_active=False)
                
                period = EvaluationPeriod.objects.create(
                    year=int(request.POST['year']),
                    period_type=request.POST['period_type'],
                    start_date=request.POST['start_date'],
                    end_date=request.POST['end_date'],
                    is_active=True,
                    status='ONGOING'
                )
                messages.success(request, f"{period} 평가 기간이 생성되었습니다.")
            except Exception as e:
                messages.error(request, f"평가 기간 생성 중 오류가 발생했습니다: {str(e)}")
        
        elif action == 'activate':
            # 평가 기간 활성화
            period_id = request.POST.get('period_id')
            try:
                EvaluationPeriod.objects.filter(is_active=True).update(is_active=False)
                period = EvaluationPeriod.objects.get(id=period_id)
                period.is_active = True
                period.status = 'ONGOING'
                period.save()
                messages.success(request, f"{period} 평가 기간이 활성화되었습니다.")
            except Exception as e:
                messages.error(request, f"평가 기간 활성화 중 오류가 발생했습니다: {str(e)}")
        
        elif action == 'complete':
            # 평가 기간 완료
            period_id = request.POST.get('period_id')
            try:
                period = EvaluationPeriod.objects.get(id=period_id)
                period.is_active = False
                period.status = 'COMPLETED'
                period.save()
                messages.success(request, f"{period} 평가 기간이 완료 처리되었습니다.")
            except Exception as e:
                messages.error(request, f"평가 기간 완료 처리 중 오류가 발생했습니다: {str(e)}")
        
        return redirect('evaluations:period_management')
    
    # 모든 평가 기간 조회
    periods = EvaluationPeriod.objects.all().order_by('-year', '-period_type')
    
    context = {
        'periods': periods,
        'current_year': date.today().year,
        'period_types': EvaluationPeriod._meta.get_field('period_type').choices,
    }
    
    return render(request, 'evaluations/period_management.html', context)


def evaluation_statistics(request):
    """평가 통계 및 분석"""
    # 임시로 권한 체크 스킵 (나중에 로그인 기능 구현 시 수정)
    # 현재는 모든 사용자가 접근 가능
    
    # 선택된 평가 기간 (기본값: 활성 기간)
    period_id = request.GET.get('period_id')
    if period_id:
        selected_period = get_object_or_404(EvaluationPeriod, id=period_id)
    else:
        selected_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if selected_period:
        # 전체 평가 대상자
        total_employees = Employee.objects.filter(employment_status='재직').count()
        
        # 평가 완료율
        comprehensive_count = ComprehensiveEvaluation.objects.filter(
            evaluation_period=selected_period
        ).count()
        completion_rate = round((comprehensive_count / total_employees * 100) if total_employees > 0 else 0, 1)
        
        # 평가 항목별 달성률
        contribution_achieved = ContributionEvaluation.objects.filter(
            evaluation_period=selected_period,
            is_achieved=True
        ).count()
        expertise_achieved = ExpertiseEvaluation.objects.filter(
            evaluation_period=selected_period,
            is_achieved=True
        ).count()
        impact_achieved = ImpactEvaluation.objects.filter(
            evaluation_period=selected_period,
            is_achieved=True
        ).count()
        
        # 등급별 분포
        grade_distribution = ComprehensiveEvaluation.objects.filter(
            evaluation_period=selected_period,
            final_grade__isnull=False
        ).values('final_grade').annotate(
            count=models.Count('id')
        ).order_by('final_grade')
        
        # 부서별 통계
        department_stats = []
        departments = Employee.objects.filter(
            employment_status='재직'
        ).values_list('department', flat=True).distinct()
        
        for dept in departments:
            dept_evals = ComprehensiveEvaluation.objects.filter(
                employee__department=dept,
                evaluation_period=selected_period,
                final_grade__isnull=False
            )
            
            dept_grades = dept_evals.values('final_grade').annotate(
                count=models.Count('id')
            )
            
            department_stats.append({
                'department': dept,
                'total': dept_evals.count(),
                'grades': {g['final_grade']: g['count'] for g in dept_grades}
            })
        
        # 상위/하위 성과자
        top_performers = ComprehensiveEvaluation.objects.filter(
            evaluation_period=selected_period,
            final_grade__in=['S', 'A+', 'A']
        ).select_related('employee').order_by('final_grade')[:10]
        
        low_performers = ComprehensiveEvaluation.objects.filter(
            evaluation_period=selected_period,
            final_grade__in=['C', 'D']
        ).select_related('employee').order_by('-final_grade')[:10]
        
    else:
        total_employees = comprehensive_count = completion_rate = 0
        contribution_achieved = expertise_achieved = impact_achieved = 0
        grade_distribution = department_stats = []
        top_performers = low_performers = []
    
    # 모든 평가 기간 (선택용)
    all_periods = EvaluationPeriod.objects.all().order_by('-year', '-period_type')
    
    context = {
        'selected_period': selected_period,
        'all_periods': all_periods,
        'total_employees': total_employees,
        'comprehensive_count': comprehensive_count,
        'completion_rate': completion_rate,
        'contribution_achieved': contribution_achieved,
        'expertise_achieved': expertise_achieved,
        'impact_achieved': impact_achieved,
        'grade_distribution': list(grade_distribution),
        'department_stats': department_stats,
        'top_performers': top_performers,
        'low_performers': low_performers,
    }
    
    return render(request, 'evaluations/evaluation_statistics.html', context)


# 평가 목록 뷰들
def contribution_list(request):
    """기여도 평가 대상자 목록"""
    employees = Employee.objects.filter(employment_status='재직').order_by('employee_id')
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    # 평가 완료 여부 확인
    if active_period:
        for emp in employees:
            emp.is_evaluated = ContributionEvaluation.objects.filter(
                employee=emp, 
                evaluation_period=active_period
            ).exists()
    
    context = {
        'title': '기여도 평가',
        'employees': employees,
        'evaluation_url': '/evaluations/contribution/',
    }
    return render(request, 'evaluations/evaluation_list.html', context)


def expertise_list(request):
    """전문성 평가 대상자 목록"""
    employees = Employee.objects.filter(employment_status='재직').order_by('employee_id')
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    # 평가 완료 여부 확인
    if active_period:
        for emp in employees:
            emp.is_evaluated = ExpertiseEvaluation.objects.filter(
                employee=emp,
                evaluation_period=active_period
            ).exists()
    
    context = {
        'title': '전문성 평가',
        'employees': employees,
        'evaluation_url': '/evaluations/expertise/',
    }
    return render(request, 'evaluations/evaluation_list.html', context)


def impact_list(request):
    """영향력 평가 대상자 목록"""
    employees = Employee.objects.filter(employment_status='재직').order_by('employee_id')
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    # 평가 완료 여부 확인
    if active_period:
        for emp in employees:
            emp.is_evaluated = ImpactEvaluation.objects.filter(
                employee=emp,
                evaluation_period=active_period
            ).exists()
    
    context = {
        'title': '영향력 평가',
        'employees': employees,
        'evaluation_url': '/evaluations/impact/',
    }
    return render(request, 'evaluations/evaluation_list.html', context)


# Task Check-in 관련 뷰
@csrf_exempt
def task_checkin(request, task_id):
    """Task Check-in 수행"""
    if request.method == 'POST':
        try:
            task = get_object_or_404(Task, id=task_id)
            
            # Check-in 수행
            progress_note = request.POST.get('progress_note', '')
            task.checkin(progress_note)
            
            # 실적값 업데이트
            if 'actual_value' in request.POST:
                task.actual_value = Decimal(request.POST['actual_value'])
                task.calculate_achievement_rate()
                task.calculate_contribution_score()
                task.save()
            
            return JsonResponse({
                'success': True,
                'checkin_count': task.checkin_count,
                'last_checkin': task.last_checkin_date.strftime('%Y-%m-%d %H:%M') if task.last_checkin_date else None,
                'achievement_rate': float(task.achievement_rate) if task.achievement_rate else 0,
                'final_score': float(task.final_score) if task.final_score else 0
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def task_checkin_history(request, task_id):
    """Task Check-in 이력 조회"""
    task = get_object_or_404(Task, id=task_id)
    
    # TODO: Check-in 이력 모델 구현 후 실제 이력 조회
    # 현재는 간단한 정보만 반환
    checkin_info = {
        'task': task,
        'total_checkins': task.checkin_count,
        'last_checkin': task.last_checkin_date,
        'status': task.get_status_display(),
    }
    
    return render(request, 'evaluations/task_checkin_history.html', checkin_info)


def task_update_status(request, task_id):
    """Task 상태 업데이트"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        new_status = request.POST.get('status')
        
        if new_status in ['PLANNED', 'IN_PROGRESS', 'COMPLETED']:
            task.status = new_status
            
            # 완료 시 달성률 100%로 설정
            if new_status == 'COMPLETED' and not task.achievement_rate:
                task.achievement_rate = 100
                task.calculate_contribution_score()
            
            task.save()
            
            messages.success(request, f"Task '{task.title}'의 상태가 업데이트되었습니다.")
        else:
            messages.error(request, "유효하지 않은 상태입니다.")
    
    return redirect(request.META.get('HTTP_REFERER', 'evaluations:dashboard'))


def comprehensive_evaluation(request, employee_id):
    """종합평가 관리"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    # 종합평가 가져오기 또는 생성
    comprehensive, created = ComprehensiveEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={
            'manager': Employee.objects.filter(employment_status='재직').first(),
            'status': 'DRAFT'
        }
    )
    
    # 3대 평가 연결
    if not comprehensive.contribution_evaluation:
        comprehensive.contribution_evaluation = ContributionEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
    
    if not comprehensive.expertise_evaluation:
        comprehensive.expertise_evaluation = ExpertiseEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
    
    if not comprehensive.impact_evaluation:
        comprehensive.impact_evaluation = ImpactEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
    
    # 점수 동기화
    comprehensive.sync_evaluation_scores()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'manager_evaluation':
            # 1차 평가 저장
            comprehensive.manager_grade = request.POST.get('manager_grade')
            comprehensive.manager_comments = request.POST.get('manager_comments', '')
            comprehensive.manager_evaluated_date = date.today()
            comprehensive.save()
            
            messages.success(request, "1차 평가가 저장되었습니다.")
            
        elif action == 'submit_evaluation':
            # 평가 제출
            if comprehensive.manager_grade:
                comprehensive.status = 'SUBMITTED'
                comprehensive.save()
                messages.success(request, "평가가 제출되었습니다.")
            else:
                messages.error(request, "1차 평가를 완료해주세요.")
        
        return redirect('evaluations:comprehensive_evaluation', employee_id=employee_id)
    
    # 달성 개수 계산
    achieved_count = sum([
        comprehensive.contribution_achieved,
        comprehensive.expertise_achieved, 
        comprehensive.impact_achieved
    ])
    
    # 진행률 계산
    progress_steps = [
        comprehensive.contribution_evaluation is not None,
        comprehensive.expertise_evaluation is not None,
        comprehensive.impact_evaluation is not None,
        comprehensive.manager_grade is not None
    ]
    progress_percent = sum(progress_steps) * 25


def growth_level_dashboard(request, employee_id):
    """성장레벨 대시보드"""
    try:
        from .services import GrowthLevelAnalyzer
        from .models import GrowthLevel, EmployeeGrowthHistory, PerformanceTrend, GrowthLevelRequirement
        import json
        
        employee = get_object_or_404(Employee, id=employee_id)
        active_period = EvaluationPeriod.objects.filter(is_active=True).first()
        
        if not active_period:
            messages.warning(request, "활성화된 평가 기간이 없습니다.")
            return redirect('evaluations:dashboard')
        
        # 현재 성장레벨
        current_level = GrowthLevel.objects.filter(level=employee.growth_level).first()
        if not current_level:
            current_level = GrowthLevel.objects.filter(level=1).first()
        
        # 다음 레벨
        next_level = None
        if current_level:
            next_level = GrowthLevel.objects.filter(level=current_level.level + 1).first()
        
        # 최신 성장 이력
        latest_history = EmployeeGrowthHistory.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date').first()
        
        # 성장 이력 (최근 5개)
        growth_history = EmployeeGrowthHistory.objects.filter(
            employee=employee
        ).select_related('evaluation_period', 'current_level', 'previous_level').order_by('-evaluation_period__end_date')[:5]
        
        # 최신 트렌드
        latest_trend = PerformanceTrend.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date').first()
        
        # 승급 진행도 계산
        promotion_progress = 0
        promotion_requirements_remaining = 0
        promotion_consecutive_required = 3  # 기본값
        
        if latest_history and next_level:
            if latest_history.meets_score_requirement:
                promotion_progress = min(100, (latest_history.consecutive_achievements / promotion_consecutive_required) * 100)
            else:
                # 점수 기반 진행도
                if latest_history.overall_score:
                    promotion_progress = min(100, (latest_history.overall_score / 3.5) * 100)
        
        # 다음 레벨 요구사항
        next_level_requirements = []
        if next_level:
            requirements = GrowthLevelRequirement.objects.filter(growth_level=next_level)
            for req in requirements:
                is_met = False
                current_value = None
                
                # 요구사항 충족 여부 확인 (실제 로직은 요구사항 유형에 따라 다름)
                if latest_history:
                    if req.requirement_type == 'SCORE' and latest_history.overall_score:
                        current_value = latest_history.overall_score
                        is_met = latest_history.overall_score >= float(req.required_value or 3.0)
                    elif req.requirement_type == 'CONSECUTIVE' and latest_history.consecutive_achievements:
                        current_value = latest_history.consecutive_achievements
                        is_met = latest_history.consecutive_achievements >= int(req.required_value or 3)
                
                next_level_requirements.append({
                    'description': req.description,
                    'is_met': is_met,
                    'current_value': current_value,
                    'required_value': req.required_value
                })
            
            promotion_requirements_remaining = len([r for r in next_level_requirements if not r['is_met']])
        
        # 트렌드 차트 데이터 준비
        trend_chart_data = {
            'labels': [],
            'contribution': [],
            'expertise': [],
            'impact': []
        }
        
        # 최근 6개월 데이터
        recent_history = list(growth_history)[:6]
        recent_history.reverse()  # 시간순 정렬
        
        for history in recent_history:
            period_label = history.evaluation_period.name if hasattr(history.evaluation_period, 'name') else str(history.evaluation_period)
            trend_chart_data['labels'].append(period_label)
            trend_chart_data['contribution'].append(float(history.contribution_score or 0))
            trend_chart_data['expertise'].append(float(history.expertise_score or 0))
            trend_chart_data['impact'].append(float(history.impact_score or 0))
        
        context = {
            'employee': employee,
            'active_period': active_period,
            'current_level': current_level,
            'next_level': next_level,
            'latest_history': latest_history,
            'growth_history': growth_history,
            'latest_trend': latest_trend,
            'promotion_progress': promotion_progress,
            'promotion_requirements_remaining': promotion_requirements_remaining,
            'promotion_consecutive_required': promotion_consecutive_required,
            'next_level_requirements': next_level_requirements,
            'trend_chart_data': json.dumps(trend_chart_data),
        }
        
        return render(request, 'evaluations/growth_level_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"성장레벨 대시보드 조회 중 오류가 발생했습니다: {str(e)}")
        return redirect('evaluations:dashboard')
    progress_offset = 439.82 - (progress_percent / 100 * 439.82)
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'comprehensive': comprehensive,
        'achieved_count': achieved_count,
        'progress_percent': progress_percent,
        'progress_offset': progress_offset,
        'grade_choices': GRADE_CHOICES,
    }
    
    return render(request, 'evaluations/comprehensive_evaluation.html', context)


def calibration_session(request, session_id):
    """Calibration Session 관리"""
    session = get_object_or_404(CalibrationSession, id=session_id)
    
    # 세션 대상 평가들
    evaluations = ComprehensiveEvaluation.objects.filter(
        evaluation_period=session.evaluation_period,
        status__in=['SUBMITTED', 'IN_REVIEW']
    ).select_related('employee')
    
    # 부서별 필터링
    if session.department:
        evaluations = evaluations.filter(employee__department=session.department)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'update_status':
                # 세션 상태 업데이트
                new_status = data.get('status')
                if new_status in ['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']:
                    session.status = new_status
                    session.save()
                    return JsonResponse({'success': True})
                
            elif action == 'update_grade':
                # 평가 등급 업데이트
                evaluation_id = data.get('evaluation_id')
                final_grade = data.get('final_grade')
                
                evaluation = get_object_or_404(ComprehensiveEvaluation, id=evaluation_id)
                evaluation.final_grade = final_grade
                evaluation.calibration_session = session
                evaluation.status = 'IN_REVIEW'
                evaluation.save()
                
                return JsonResponse({'success': True})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # 현재 등급 분포 계산
    current_distribution = session.get_grade_distribution()
    
    context = {
        'session': session,
        'evaluations': evaluations,
        'current_distribution': current_distribution,
        'grade_choices': GRADE_CHOICES,
    }
    
    return render(request, 'evaluations/calibration_session.html', context)


def create_calibration_session(request):
    """Calibration Session 생성"""
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluations:dashboard')
    
    if request.method == 'POST':
        try:
            session = CalibrationSession.objects.create(
                evaluation_period=active_period,
                session_name=request.POST['session_name'],
                session_date=request.POST['session_date'],
                facilitator=Employee.objects.filter(employment_status='재직').first(),
                agenda=request.POST.get('agenda', ''),
                s_grade_ratio=request.POST.get('s_grade_ratio', 10),
                a_grade_ratio=request.POST.get('a_grade_ratio', 30),
                b_grade_ratio=request.POST.get('b_grade_ratio', 50),
                c_grade_ratio=request.POST.get('c_grade_ratio', 10),
            )
            
            # 참여자 추가
            participant_ids = request.POST.getlist('participants')
            if participant_ids:
                participants = Employee.objects.filter(id__in=participant_ids)
                session.participants.set(participants)
            
            messages.success(request, "Calibration Session이 생성되었습니다.")
            return redirect('evaluations:calibration_session', session_id=session.id)
            
        except Exception as e:
            messages.error(request, f"Calibration Session 생성 중 오류가 발생했습니다: {str(e)}")
    
    # 참여 가능한 직원들 (관리자급)
    potential_participants = Employee.objects.filter(
        employment_status='재직',
        position__in=['부장', '차장', '과장']  # 실제 조직에 맞게 수정
    )
    
    context = {
        'active_period': active_period,
        'potential_participants': potential_participants,
    }
    
    return render(request, 'evaluations/create_calibration_session.html', context)


def calibration_list(request):
    """Calibration Session 목록"""
    sessions = CalibrationSession.objects.all().order_by('-session_date')
    
    context = {
        'sessions': sessions,
    }
    
    return render(request, 'evaluations/calibration_list.html', context)


def comprehensive_list(request):
    """종합평가 대상자 목록"""
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/comprehensive_list.html', {'employees': []})
    
    # 모든 직원에 대한 평가 현황 수집
    # 임시: 모든 직원 표시 (데이터 부족 문제)
    employees = Employee.objects.all().order_by('department', 'name')
    employee_data = []
    
    for employee in employees:
        # 각 평가 완료 여부 확인
        contribution_eval = ContributionEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
        expertise_eval = ExpertiseEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
        impact_eval = ImpactEvaluation.objects.filter(
            employee=employee, evaluation_period=active_period
        ).first()
        
        # 종합평가 가져오기 또는 생성
        comprehensive, created = ComprehensiveEvaluation.objects.get_or_create(
            employee=employee,
            evaluation_period=active_period,
            defaults={'status': 'DRAFT'}
        )
        
        # 평가 연결 및 점수 동기화
        if contribution_eval:
            comprehensive.contribution_evaluation = contribution_eval
        if expertise_eval:
            comprehensive.expertise_evaluation = expertise_eval
        if impact_eval:
            comprehensive.impact_evaluation = impact_eval
        
        comprehensive.sync_evaluation_scores()
        
        # 진행률 계산
        progress_steps = [
            contribution_eval is not None,
            expertise_eval is not None,
            impact_eval is not None,
            comprehensive.manager_grade is not None
        ]
        progress = sum(progress_steps) * 25
        
        # 상태 결정
        if comprehensive.status == 'COMPLETED':
            status = 'completed'
        elif any(progress_steps):
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'comprehensive': comprehensive,
            'contribution_completed': contribution_eval is not None,
            'expertise_completed': expertise_eval is not None,
            'impact_completed': impact_eval is not None,
            'progress': progress,
            'status': status
        })
    
    # 통계 계산
    total_employees = len(employee_data)
    completed_count = sum(1 for data in employee_data if data['status'] == 'completed')
    in_progress_count = sum(1 for data in employee_data if data['status'] == 'in-progress')
    completion_rate = round((completed_count / total_employees * 100) if total_employees > 0 else 0, 1)
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
        'total_employees': total_employees,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'evaluations/comprehensive_list.html', context)


def analytics_dashboard(request):
    """평가 데이터 분석 대시보드"""
    try:
        from .analytics import EvaluationReportGenerator
        import json
        from decimal import Decimal
        
        active_period = EvaluationPeriod.objects.filter(is_active=True).first()
        
        if not active_period:
            messages.warning(request, "활성화된 평가 기간이 없습니다.")
            return redirect('evaluations:dashboard')
        
        if request.method == 'POST':
            # 리포트 갱신 요청
            data = json.loads(request.body)
            if data.get('action') == 'regenerate':
                # 리포트 재생성 로직
                report = EvaluationReportGenerator.generate_comprehensive_report(active_period)
                return JsonResponse({'success': True})
        
        # 종합 리포트 생성
        report = EvaluationReportGenerator.generate_comprehensive_report(active_period)
        
        if not report:
            messages.error(request, "리포트 생성에 실패했습니다.")
            return redirect('evaluations:dashboard')
        
        # JSON 직렬화를 위한 데이터 변환
        def json_serializable(obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            elif hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return str(obj)
        
        # 템플릿에서 사용할 JSON 데이터 준비
        context = {
            'report': report,
            'json_data': {
                'organization_summary': json.dumps(report['analysis_data']['organization_summary'], default=json_serializable),
                'department_analysis': json.dumps(report['analysis_data']['department_analysis'], default=json_serializable),
                'growth_insights': json.dumps(report['analysis_data']['growth_insights'], default=json_serializable),
                'performance_trends': json.dumps(report['analysis_data']['performance_trends'], default=json_serializable),
            }
        }
        
        return render(request, 'evaluations/analytics_dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f"분석 대시보드 조회 중 오류가 발생했습니다: {str(e)}")
        return redirect('evaluations:dashboard')


def contribution_list(request):
    """기여도 평가 대상자 목록"""
    from django.db.models import Prefetch, Count, Q
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/contribution_list.html', {'employees': []})
    
    # 최적화된 쿼리: select_related와 prefetch_related 사용
    # 임시: 모든 직원 표시 (데이터 부족 문제)
    employees = Employee.objects.all().select_related(
        'user', 'manager'
    ).prefetch_related(
        Prefetch(
            'contribution_evaluations',
            queryset=ContributionEvaluation.objects.filter(evaluation_period=active_period),
            to_attr='period_contributions'
        ),
        Prefetch(
            'tasks',
            queryset=Task.objects.filter(evaluation_period=active_period).annotate(
                is_completed=Q(status='COMPLETED')
            ),
            to_attr='period_tasks'
        )
    ).order_by('department', 'name')
    
    employee_data = []
    
    for employee in employees:
        # Prefetch된 데이터 사용
        contribution_eval = employee.period_contributions[0] if employee.period_contributions else None
        
        # Task 정보 (이미 로드됨)
        total_tasks = len(employee.period_tasks)
        completed_tasks = sum(1 for task in employee.period_tasks if hasattr(task, 'is_completed') and task.is_completed)
        task_completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        # 상태 결정
        if contribution_eval and contribution_eval.is_achieved:
            status = 'completed'
        elif contribution_eval or total_tasks > 0:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'contribution_eval': contribution_eval,
            'contribution_score': contribution_eval.contribution_score if contribution_eval else None,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'task_completion_rate': task_completion_rate,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/contribution_list.html', context)


def expertise_list(request):
    """전문성 평가 대상자 목록"""
    from django.db.models import Prefetch
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/expertise_list.html', {'employees': []})
    
    # 최적화된 쿼리
    # 임시: 모든 직원 표시 (데이터 부족 문제)
    employees = Employee.objects.all().select_related(
        'user', 'manager'
    ).prefetch_related(
        Prefetch(
            'expertise_evaluations',
            queryset=ExpertiseEvaluation.objects.filter(evaluation_period=active_period),
            to_attr='period_expertise'
        )
    ).order_by('department', 'name')
    
    employee_data = []
    
    for employee in employees:
        # Prefetch된 데이터 사용
        expertise_eval = employee.period_expertise[0] if employee.period_expertise else None
        
        # 상태 결정
        if expertise_eval and expertise_eval.is_achieved:
            status = 'completed'
        elif expertise_eval:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'expertise_eval': expertise_eval,
            'total_score': expertise_eval.total_score if expertise_eval else None,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/expertise_list.html', context)


def impact_list(request):
    """영향력 평가 대상자 목록"""
    from django.db.models import Prefetch
    
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/impact_list.html', {'employees': []})
    
    # 최적화된 쿼리
    # 임시: 모든 직원 표시 (데이터 부족 문제)
    employees = Employee.objects.all().select_related(
        'user', 'manager'
    ).prefetch_related(
        Prefetch(
            'impact_evaluations',
            queryset=ImpactEvaluation.objects.filter(evaluation_period=active_period),
            to_attr='period_impact'
        )
    ).order_by('department', 'name')
    
    employee_data = []
    
    for employee in employees:
        # Prefetch된 데이터 사용
        impact_eval = employee.period_impact[0] if employee.period_impact else None
        
        # 상태 결정
        if impact_eval and impact_eval.is_achieved:
            status = 'completed'
        elif impact_eval:
            status = 'in-progress'
        else:
            status = 'not-started'
        
        employee_data.append({
            'employee': employee,
            'impact_eval': impact_eval,
            'total_score': impact_eval.total_score if impact_eval else None,
            'status': status
        })
    
    context = {
        'active_period': active_period,
        'employees': employee_data,
    }
    
    return render(request, 'evaluations/impact_list.html', context)

