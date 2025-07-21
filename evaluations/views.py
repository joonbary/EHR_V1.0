from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import json

from employees.models import Employee
from .models import (
    EvaluationPeriod, Task, ContributionEvaluation, 
    ExpertiseEvaluation, ImpactEvaluation, ComprehensiveEvaluation,
    CONTRIBUTION_SCORING_CHART, EXPERTISE_SCORING_CHART, IMPACT_SCORING_CHART
)


@login_required
def evaluation_dashboard(request):
    """평가 대시보드 - 4단계 진행상황 표시"""
    # 활성화된 평가 기간
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.warning(request, "활성화된 평가 기간이 없습니다.")
        return render(request, 'evaluations/dashboard.html')
    
    # 현재 사용자의 평가 진행상황
    employee = request.user.employee if hasattr(request.user, 'employee') else None
    
    if not employee:
        messages.error(request, "직원 정보를 찾을 수 없습니다.")
        return render(request, 'evaluations/dashboard.html')
    
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
    
    return render(request, 'evaluations/dashboard.html', context)


@login_required
def contribution_evaluation(request, employee_id):
    """기여도 평가 - Task 기반 + Scoring Chart"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluation_dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ContributionEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={'evaluator': request.user.employee if hasattr(request.user, 'employee') else None}
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
            return redirect('evaluation_dashboard')
    
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


@login_required
def expertise_evaluation(request, employee_id):
    """전문성 평가 - 10개 체크리스트"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluation_dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ExpertiseEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={
            'evaluator': request.user.employee if hasattr(request.user, 'employee') else None,
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
            return redirect('evaluation_dashboard')
    
    context = {
        'employee': employee,
        'active_period': active_period,
        'evaluation': evaluation,
        'scoring_chart': EXPERTISE_SCORING_CHART,
    }
    
    return render(request, 'evaluations/expertise_evaluation.html', context)


@login_required
def impact_evaluation(request, employee_id):
    """영향력 평가 - 6개 항목"""
    employee = get_object_or_404(Employee, id=employee_id)
    active_period = EvaluationPeriod.objects.filter(is_active=True).first()
    
    if not active_period:
        messages.error(request, "활성화된 평가 기간이 없습니다.")
        return redirect('evaluation_dashboard')
    
    # 기존 평가 가져오기 또는 새로 생성
    evaluation, created = ImpactEvaluation.objects.get_or_create(
        employee=employee,
        evaluation_period=active_period,
        defaults={
            'evaluator': request.user.employee if hasattr(request.user, 'employee') else None,
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
            return redirect('evaluation_dashboard')
    
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
        data = json.loads(request.body)
        evaluation_type = data.get('type')
        
        if evaluation_type == 'contribution':
            # 기여도 점수 계산
            method = data.get('method')
            scope = data.get('scope')
            achievement_rate = data.get('achievement_rate', 100)
            
            if scope in CONTRIBUTION_SCORING_CHART and method in CONTRIBUTION_SCORING_CHART[scope]:
                base_score = CONTRIBUTION_SCORING_CHART[scope][method]
                
                # 달성률에 따른 조정
                if achievement_rate >= 100:
                    final_score = base_score
                elif achievement_rate >= 90:
                    final_score = base_score - 0.5
                elif achievement_rate >= 80:
                    final_score = base_score - 1.0
                elif achievement_rate >= 70:
                    final_score = base_score - 1.5
                else:
                    final_score = max(1.0, base_score - 2.0)
                
                return JsonResponse({'score': round(final_score, 1)})
        
        elif evaluation_type == 'expertise':
            # 전문성 점수 계산
            scores = data.get('scores', [])
            if scores:
                avg_score = sum(scores) / len(scores)
                return JsonResponse({'score': round(avg_score, 1)})
        
        elif evaluation_type == 'impact':
            # 영향력 점수 계산
            scope = data.get('scope')
            values_practice = data.get('values_practice')
            leadership = data.get('leadership')
            
            if scope in IMPACT_SCORING_CHART:
                scope_chart = IMPACT_SCORING_CHART[scope]
                values_score = scope_chart.get(values_practice, 2)
                leadership_score = scope_chart.get(leadership, 2)
                final_score = (values_score + leadership_score) / 2
                return JsonResponse({'score': round(final_score, 1)})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
