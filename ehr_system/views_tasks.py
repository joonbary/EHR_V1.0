"""
백그라운드 작업 관리 뷰
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.generic import View, TemplateView
from django.utils import timezone
import json

from utils.background_tasks import task_manager, TaskPriority, scheduled_task_manager


class TaskDashboardView(TemplateView):
    """작업 대시보드"""
    template_name = 'tasks/dashboard.html'
    
    @user_passes_test(lambda u: u.is_staff)
    def get(self, request):
        # 활성 작업
        active_tasks = [task.to_dict() for task in task_manager.active_tasks.values()]
        
        # 최근 완료 작업 (최근 20개)
        completed_tasks = sorted(
            [task.to_dict() for task in task_manager.completed_tasks.values()],
            key=lambda x: x['completed_at'] or '',
            reverse=True
        )[:20]
        
        # 예약된 작업
        scheduled_tasks = []
        for task in scheduled_task_manager.scheduled_tasks:
            scheduled_tasks.append({
                'task_type': task['task_type'],
                'schedule': task['schedule'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None,
                'next_run': task['next_run'].isoformat() if task['next_run'] else None
            })
        
        context = {
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'scheduled_tasks': scheduled_tasks,
            'is_running': task_manager.is_running,
            'worker_count': task_manager.max_workers
        }
        
        return render(request, self.template_name, context)


class SubmitTaskView(View):
    """작업 제출"""
    
    @user_passes_test(lambda u: u.is_staff)
    def post(self, request):
        try:
            data = json.loads(request.body)
            task_type = data.get('task_type')
            metadata = data.get('metadata', {})
            priority = data.get('priority', 'NORMAL')
            
            # 우선순위 변환
            priority_map = {
                'LOW': TaskPriority.LOW,
                'NORMAL': TaskPriority.NORMAL,
                'HIGH': TaskPriority.HIGH,
                'CRITICAL': TaskPriority.CRITICAL
            }
            
            task_priority = priority_map.get(priority, TaskPriority.NORMAL)
            
            # 작업 제출
            task_id = task_manager.submit_task(task_type, metadata, task_priority)
            
            return JsonResponse({
                'success': True,
                'task_id': task_id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


class TaskStatusView(View):
    """작업 상태 조회"""
    
    @login_required
    def get(self, request, task_id):
        task_status = task_manager.get_task_status(task_id)
        
        if task_status:
            return JsonResponse({
                'success': True,
                'task': task_status
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Task not found'
            }, status=404)


class BatchTasksView(View):
    """배치 작업 실행"""
    
    @user_passes_test(lambda u: u.is_staff)
    def post(self, request):
        """특정 배치 작업 실행"""
        batch_type = request.POST.get('batch_type')
        
        if batch_type == 'evaluation_processing':
            # 모든 활성 평가 기간에 대해 처리
            from evaluations.models import EvaluationPeriod
            
            active_periods = EvaluationPeriod.objects.filter(
                is_active=True,
                end_date__lt=timezone.now().date()
            )
            
            task_ids = []
            for period in active_periods:
                task_id = task_manager.submit_task(
                    'evaluation_processing',
                    {'period_id': period.id},
                    TaskPriority.HIGH
                )
                task_ids.append(task_id)
            
            return JsonResponse({
                'success': True,
                'message': f'{len(task_ids)}개의 평가 처리 작업이 제출되었습니다.',
                'task_ids': task_ids
            })
        
        elif batch_type == 'monthly_reports':
            # 월간 리포트 생성
            task_id = task_manager.submit_task(
                'report_generation',
                {
                    'report_type': 'monthly_summary',
                    'month': timezone.now().month,
                    'year': timezone.now().year
                },
                TaskPriority.NORMAL
            )
            
            return JsonResponse({
                'success': True,
                'message': '월간 리포트 생성 작업이 제출되었습니다.',
                'task_id': task_id
            })
        
        elif batch_type == 'promotion_analysis':
            # 승진 분석
            task_id = task_manager.submit_task(
                'promotion_analysis',
                {'target_year': timezone.now().year + 1},
                TaskPriority.NORMAL
            )
            
            return JsonResponse({
                'success': True,
                'message': '승진 분석 작업이 제출되었습니다.',
                'task_id': task_id
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unknown batch type: {batch_type}'
            }, status=400)


@login_required
@user_passes_test(lambda u: u.is_staff)
def task_statistics_api(request):
    """작업 통계 API"""
    # 작업 유형별 통계
    task_type_stats = {}
    
    # 완료된 작업 통계
    for task in task_manager.completed_tasks.values():
        task_type = task.task_type
        if task_type not in task_type_stats:
            task_type_stats[task_type] = {
                'completed': 0,
                'failed': 0,
                'total_duration': 0,
                'count': 0
            }
        
        stats = task_type_stats[task_type]
        stats['count'] += 1
        
        if task.status.value == 'completed':
            stats['completed'] += 1
        elif task.status.value == 'failed':
            stats['failed'] += 1
        
        # 실행 시간 계산
        if task.started_at and task.completed_at:
            duration = (task.completed_at - task.started_at).total_seconds()
            stats['total_duration'] += duration
    
    # 평균 실행 시간 계산
    for stats in task_type_stats.values():
        if stats['count'] > 0:
            stats['avg_duration'] = stats['total_duration'] / stats['count']
        else:
            stats['avg_duration'] = 0
    
    # 시간대별 작업 분포
    hourly_distribution = [0] * 24
    for task in task_manager.completed_tasks.values():
        if task.created_at:
            hour = task.created_at.hour
            hourly_distribution[hour] += 1
    
    return JsonResponse({
        'task_type_stats': task_type_stats,
        'hourly_distribution': hourly_distribution,
        'total_completed': len(task_manager.completed_tasks),
        'total_active': len(task_manager.active_tasks)
    })