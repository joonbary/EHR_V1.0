"""
백그라운드 작업 관리 모듈
태스크 매니저 MCP를 활용한 비동기 작업 처리
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import threading
import queue
import time


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """작업 우선순위"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class BackgroundTask:
    """백그라운드 작업 클래스"""
    
    def __init__(self, task_id: str, task_type: str, priority: TaskPriority = TaskPriority.NORMAL):
        self.task_id = task_id
        self.task_type = task_type
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = timezone.now()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
        self.result = None
        self.progress = 0
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type,
            'priority': self.priority.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'progress': self.progress,
            'metadata': self.metadata
        }


class TaskManager:
    """태스크 매니저 - 백그라운드 작업 관리"""
    
    def __init__(self):
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_handlers = {}
        self.worker_threads = []
        self.is_running = False
        self.max_workers = 4
        
        # 작업 핸들러 등록
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """기본 작업 핸들러 등록"""
        self.register_handler('evaluation_processing', self._handle_evaluation_processing)
        self.register_handler('report_generation', self._handle_report_generation)
        self.register_handler('email_notification', self._handle_email_notification)
        self.register_handler('data_export', self._handle_data_export)
        self.register_handler('promotion_analysis', self._handle_promotion_analysis)
        self.register_handler('compensation_calculation', self._handle_compensation_calculation)
    
    def register_handler(self, task_type: str, handler: Callable):
        """작업 핸들러 등록"""
        self.task_handlers[task_type] = handler
    
    def start(self):
        """태스크 매니저 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 워커 스레드 생성
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, name=f"TaskWorker-{i+1}")
            worker.daemon = True
            worker.start()
            self.worker_threads.append(worker)
        
        logger.info(f"TaskManager started with {self.max_workers} workers")
    
    def stop(self):
        """태스크 매니저 중지"""
        self.is_running = False
        
        # 모든 워커 스레드 종료 대기
        for worker in self.worker_threads:
            worker.join(timeout=5)
        
        logger.info("TaskManager stopped")
    
    def _worker(self):
        """워커 스레드 - 작업 처리"""
        while self.is_running:
            try:
                # 우선순위 큐에서 작업 가져오기
                priority, task = self.task_queue.get(timeout=1)
                
                # 작업 시작
                task.status = TaskStatus.RUNNING
                task.started_at = timezone.now()
                self.active_tasks[task.task_id] = task
                
                logger.info(f"Starting task {task.task_id} (type: {task.task_type})")
                
                # 작업 핸들러 실행
                handler = self.task_handlers.get(task.task_type)
                if handler:
                    try:
                        result = handler(task)
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        logger.info(f"Task {task.task_id} completed successfully")
                    except Exception as e:
                        task.status = TaskStatus.FAILED
                        task.error_message = str(e)
                        logger.error(f"Task {task.task_id} failed: {e}")
                else:
                    task.status = TaskStatus.FAILED
                    task.error_message = f"No handler for task type: {task.task_type}"
                
                # 작업 완료
                task.completed_at = timezone.now()
                del self.active_tasks[task.task_id]
                self.completed_tasks[task.task_id] = task
                
                # 작업 완료 알림
                self._notify_task_completion(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def submit_task(self, task_type: str, metadata: Dict = None, priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """작업 제출"""
        task_id = f"{task_type}_{int(time.time() * 1000)}"
        task = BackgroundTask(task_id, task_type, priority)
        
        if metadata:
            task.metadata = metadata
        
        # 우선순위 큐에 추가 (낮은 숫자가 높은 우선순위)
        self.task_queue.put((-priority.value, task))
        
        logger.info(f"Task {task_id} submitted (priority: {priority.name})")
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        # 활성 작업 확인
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # 완료된 작업 확인
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].to_dict()
        
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        # 대기 중인 작업만 취소 가능
        # 실행 중인 작업은 취소 불가 (구현 복잡도)
        # TODO: 실행 중 작업 취소 기능 구현
        return False
    
    def _notify_task_completion(self, task: BackgroundTask):
        """작업 완료 알림"""
        # 이메일 알림, 웹소켓 알림 등 구현
        pass
    
    # 작업 핸들러들
    def _handle_evaluation_processing(self, task: BackgroundTask) -> Dict:
        """평가 처리 작업"""
        from utils.evaluation_processor import EvaluationProcessor
        
        period_id = task.metadata.get('period_id')
        if not period_id:
            raise ValueError("period_id is required")
        
        processor = EvaluationProcessor()
        
        # 진행률 업데이트
        task.progress = 20
        
        # 평가 데이터 수집
        eval_data = processor._collect_evaluation_data(period_id)
        task.progress = 40
        
        # 점수 계산
        calculated_scores = processor._calculate_scores(eval_data)
        task.progress = 60
        
        # 상대평가 적용
        relative_grades = processor._apply_relative_evaluation(calculated_scores)
        task.progress = 80
        
        # Calibration 준비
        calibration_data = processor._prepare_calibration(relative_grades)
        task.progress = 90
        
        # 결과 저장
        processor._save_evaluation_results(calibration_data)
        task.progress = 100
        
        return {
            'total_processed': calibration_data['total_evaluations'],
            'adjustment_needed': len(calibration_data['adjustment_needed'])
        }
    
    def _handle_report_generation(self, task: BackgroundTask) -> Dict:
        """리포트 생성 작업"""
        from reports.utils import ExcelReportGenerator
        from employees.models import Employee
        
        report_type = task.metadata.get('report_type', 'employee_list')
        
        # 리포트 생성
        if report_type == 'employee_list':
            employees = Employee.objects.all()
            generator = ExcelReportGenerator("직원 명부")
            
            # 헤더 추가
            headers = ['사번', '이름', '부서', '직급', '입사일']
            generator.add_headers(headers)
            
            # 데이터 추가
            total = employees.count()
            for idx, emp in enumerate(employees):
                generator.add_data_row([
                    emp.employee_number,
                    emp.name,
                    emp.department,
                    emp.position,
                    emp.hire_date.strftime('%Y-%m-%d') if emp.hire_date else ''
                ])
                
                # 진행률 업데이트
                task.progress = int((idx + 1) / total * 100)
            
            # 파일 저장
            filename = f"employee_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = generator.save_to_file(filename)
            
            return {
                'file_path': file_path,
                'record_count': total
            }
        
        return {}
    
    def _handle_email_notification(self, task: BackgroundTask) -> Dict:
        """이메일 알림 작업"""
        recipients = task.metadata.get('recipients', [])
        subject = task.metadata.get('subject', '')
        message = task.metadata.get('message', '')
        
        if not recipients:
            raise ValueError("No recipients specified")
        
        # 이메일 발송
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False
        )
        
        return {
            'sent_to': len(recipients),
            'timestamp': timezone.now().isoformat()
        }
    
    def _handle_data_export(self, task: BackgroundTask) -> Dict:
        """데이터 내보내기 작업"""
        export_type = task.metadata.get('export_type')
        filters = task.metadata.get('filters', {})
        
        # 내보내기 로직 구현
        # ...
        
        return {
            'export_type': export_type,
            'status': 'completed'
        }
    
    def _handle_promotion_analysis(self, task: BackgroundTask) -> Dict:
        """승진 분석 작업"""
        from promotions.promotion_analyzer import PromotionAnalyzer
        
        target_year = task.metadata.get('target_year')
        
        analyzer = PromotionAnalyzer()
        
        # 승진 후보자 분석
        task.progress = 30
        analysis_result = analyzer.analyze_promotion_candidates(target_year)
        
        # 예측 생성
        task.progress = 60
        forecast = analyzer.generate_promotion_forecast(years=3)
        
        task.progress = 100
        
        return {
            'candidates_count': analysis_result['total_candidates'],
            'eligible_now': analysis_result['eligible_now'],
            'forecast': forecast
        }
    
    def _handle_compensation_calculation(self, task: BackgroundTask) -> Dict:
        """보상 계산 작업"""
        from compensation.models import EmployeeCompensation
        from employees.models import Employee
        
        employee_ids = task.metadata.get('employee_ids', [])
        
        if not employee_ids:
            # 전체 직원 대상
            employees = Employee.objects.filter(is_active=True)
        else:
            employees = Employee.objects.filter(id__in=employee_ids)
        
        total = employees.count()
        updated_count = 0
        
        for idx, employee in enumerate(employees):
            try:
                # 보상 계산 로직
                compensation, created = EmployeeCompensation.objects.get_or_create(
                    employee=employee,
                    defaults={'effective_date': timezone.now().date()}
                )
                
                # 계산 로직 실행
                # compensation.calculate_total_compensation()
                # compensation.save()
                
                updated_count += 1
                
                # 진행률 업데이트
                task.progress = int((idx + 1) / total * 100)
                
            except Exception as e:
                logger.error(f"Failed to calculate compensation for {employee.id}: {e}")
        
        return {
            'total_processed': total,
            'updated_count': updated_count
        }


class ScheduledTaskManager:
    """정기 작업 스케줄러"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.scheduled_tasks = []
        self.scheduler_thread = None
        self.is_running = False
    
    def add_scheduled_task(self, task_type: str, schedule: Dict, metadata: Dict = None):
        """정기 작업 추가"""
        scheduled_task = {
            'task_type': task_type,
            'schedule': schedule,
            'metadata': metadata or {},
            'last_run': None,
            'next_run': self._calculate_next_run(schedule)
        }
        
        self.scheduled_tasks.append(scheduled_task)
    
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("ScheduledTaskManager started")
    
    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("ScheduledTaskManager stopped")
    
    def _scheduler_loop(self):
        """스케줄러 루프"""
        while self.is_running:
            try:
                now = timezone.now()
                
                for scheduled_task in self.scheduled_tasks:
                    if scheduled_task['next_run'] and now >= scheduled_task['next_run']:
                        # 작업 실행
                        task_id = self.task_manager.submit_task(
                            scheduled_task['task_type'],
                            scheduled_task['metadata'],
                            TaskPriority.NORMAL
                        )
                        
                        logger.info(f"Scheduled task submitted: {task_id}")
                        
                        # 다음 실행 시간 계산
                        scheduled_task['last_run'] = now
                        scheduled_task['next_run'] = self._calculate_next_run(
                            scheduled_task['schedule'], now
                        )
                
                # 1분마다 체크
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
    
    def _calculate_next_run(self, schedule: Dict, from_time: datetime = None) -> Optional[datetime]:
        """다음 실행 시간 계산"""
        if not from_time:
            from_time = timezone.now()
        
        schedule_type = schedule.get('type')
        
        if schedule_type == 'daily':
            # 매일 특정 시간
            hour = schedule.get('hour', 0)
            minute = schedule.get('minute', 0)
            
            next_run = from_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= from_time:
                next_run += timedelta(days=1)
            
            return next_run
        
        elif schedule_type == 'weekly':
            # 매주 특정 요일
            weekday = schedule.get('weekday', 0)  # 0=월요일
            hour = schedule.get('hour', 0)
            minute = schedule.get('minute', 0)
            
            days_ahead = weekday - from_time.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            
            next_run = from_time + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_run
        
        elif schedule_type == 'monthly':
            # 매월 특정 일
            day = schedule.get('day', 1)
            hour = schedule.get('hour', 0)
            minute = schedule.get('minute', 0)
            
            next_run = from_time.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= from_time:
                # 다음 달로
                if from_time.month == 12:
                    next_run = next_run.replace(year=from_time.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=from_time.month + 1)
            
            return next_run
        
        return None


# 전역 태스크 매니저 인스턴스
task_manager = TaskManager()
scheduled_task_manager = ScheduledTaskManager(task_manager)


def setup_default_scheduled_tasks():
    """기본 정기 작업 설정"""
    # 매일 오전 9시 평가 마감 알림
    scheduled_task_manager.add_scheduled_task(
        'email_notification',
        {'type': 'daily', 'hour': 9, 'minute': 0},
        {
            'subject': '평가 마감 알림',
            'template': 'evaluation_reminder'
        }
    )
    
    # 매주 월요일 오전 8시 주간 리포트 생성
    scheduled_task_manager.add_scheduled_task(
        'report_generation',
        {'type': 'weekly', 'weekday': 0, 'hour': 8, 'minute': 0},
        {
            'report_type': 'weekly_summary'
        }
    )
    
    # 매월 1일 오전 6시 월간 보상 계산
    scheduled_task_manager.add_scheduled_task(
        'compensation_calculation',
        {'type': 'monthly', 'day': 1, 'hour': 6, 'minute': 0},
        {
            'calculation_type': 'monthly'
        }
    )