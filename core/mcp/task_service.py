"""
MCP 태스크 매니저 통합 서비스
백그라운드 작업 관리를 위한 통합 인터페이스
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import threading
import queue
from django.utils import timezone
from django.conf import settings

from core.exceptions import EHRBaseException


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


class Task:
    """작업 객체"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        handler: Callable,
        data: Dict = None,
        priority: TaskPriority = TaskPriority.NORMAL
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.handler = handler
        self.data = data or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = timezone.now()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None
        self.progress = 0
        self.metadata = {}


class MCPTaskService:
    """태스크 관리 서비스"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.task_queue = queue.PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.task_handlers = {}
        self.scheduled_tasks = []
        self.workers = []
        self.is_running = False
        self.max_workers = getattr(settings, 'TASK_MANAGER_WORKERS', 4)
        
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """기본 작업 핸들러 등록"""
        self.register_handler('evaluation_processing', self._handle_evaluation_processing)
        self.register_handler('report_generation', self._handle_report_generation)
        self.register_handler('bulk_import', self._handle_bulk_import)
        self.register_handler('data_export', self._handle_data_export)
        self.register_handler('notification', self._handle_notification)
        self.register_handler('cleanup', self._handle_cleanup)
    
    def register_handler(self, task_type: str, handler: Callable):
        """작업 핸들러 등록"""
        self.task_handlers[task_type] = handler
        logger.info(f"Task handler registered: {task_type}")
    
    def submit_task(
        self,
        task_type: str,
        data: Dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0
    ) -> str:
        """작업 제출"""
        task_id = f"{task_type}_{int(timezone.now().timestamp() * 1000)}"
        
        if task_type not in self.task_handlers:
            raise ValueError(f"Unknown task type: {task_type}")
        
        handler = self.task_handlers[task_type]
        task = Task(task_id, task_type, handler, data, priority)
        
        if delay_seconds > 0:
            # 지연 실행
            task.metadata['scheduled_for'] = timezone.now() + timedelta(seconds=delay_seconds)
            self.scheduled_tasks.append(task)
        else:
            # 즉시 실행
            self.task_queue.put((-priority.value, task))
        
        logger.info(f"Task submitted: {task_id} (priority: {priority.name})")
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        # 활성 작업 확인
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
        # 완료된 작업 확인
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        else:
            return None
        
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'status': task.status.value,
            'progress': task.progress,
            'created_at': task.created_at.isoformat(),
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'result': task.result,
            'error': str(task.error) if task.error else None
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """작업 취소"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            return True
        return False
    
    def start(self):
        """서비스 시작"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 워커 스레드 시작
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker,
                name=f"TaskWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # 스케줄러 스레드 시작
        scheduler = threading.Thread(
            target=self._scheduler,
            name="TaskScheduler",
            daemon=True
        )
        scheduler.start()
        
        logger.info(f"Task service started with {self.max_workers} workers")
    
    def stop(self):
        """서비스 중지"""
        self.is_running = False
        logger.info("Task service stopped")
    
    def _worker(self):
        """워커 스레드"""
        while self.is_running:
            try:
                # 작업 가져오기
                priority, task = self.task_queue.get(timeout=1)
                
                # 작업 시작
                task.status = TaskStatus.RUNNING
                task.started_at = timezone.now()
                self.active_tasks[task.task_id] = task
                
                logger.info(f"Task started: {task.task_id}")
                
                try:
                    # 핸들러 실행
                    result = task.handler(task)
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    logger.info(f"Task completed: {task.task_id}")
                    
                except Exception as e:
                    task.error = e
                    task.status = TaskStatus.FAILED
                    logger.error(f"Task failed: {task.task_id} - {str(e)}")
                
                finally:
                    # 작업 완료
                    task.completed_at = timezone.now()
                    del self.active_tasks[task.task_id]
                    self.completed_tasks[task.task_id] = task
                    
                    # 완료된 작업 수 제한
                    if len(self.completed_tasks) > 1000:
                        oldest_id = min(self.completed_tasks.keys())
                        del self.completed_tasks[oldest_id]
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
    
    def _scheduler(self):
        """스케줄러 스레드"""
        while self.is_running:
            try:
                now = timezone.now()
                
                # 예약된 작업 확인
                ready_tasks = []
                for task in self.scheduled_tasks:
                    scheduled_time = task.metadata.get('scheduled_for')
                    if scheduled_time and now >= scheduled_time:
                        ready_tasks.append(task)
                
                # 준비된 작업 큐에 추가
                for task in ready_tasks:
                    self.task_queue.put((-task.priority.value, task))
                    self.scheduled_tasks.remove(task)
                
                # 1초 대기
                threading.Event().wait(1)
                
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
    
    # 기본 핸들러 구현
    def _handle_evaluation_processing(self, task: Task) -> Dict:
        """평가 처리"""
        from core.mcp import MCPSequentialService
        
        period_id = task.data.get('period_id')
        if not period_id:
            raise ValueError("평가 기간 ID가 필요합니다.")
        
        # 시퀀셜 서비스 사용
        sequential_service = MCPSequentialService()
        
        # 진행 상황 업데이트
        task.progress = 20
        
        # 평가 프로세스 실행
        context = sequential_service.execute_process(
            'evaluation_complete',
            {'period_id': period_id}
        )
        
        task.progress = 100
        
        return context.get_summary()
    
    def _handle_report_generation(self, task: Task) -> Dict:
        """리포트 생성"""
        from core.mcp import MCPFileService
        
        report_type = task.data.get('report_type')
        filters = task.data.get('filters', {})
        
        file_service = MCPFileService()
        
        # 리포트 데이터 수집
        task.progress = 30
        data = self._collect_report_data(report_type, filters)
        
        # Excel 파일 생성
        task.progress = 70
        filename = f"{report_type}_report.xlsx"
        file_path = file_service.generate_excel_export(data, filename)
        
        task.progress = 100
        
        return {
            'file_path': file_path,
            'record_count': len(data),
            'generated_at': timezone.now().isoformat()
        }
    
    def _collect_report_data(self, report_type: str, filters: Dict) -> List[Dict]:
        """리포트 데이터 수집"""
        # TODO: 실제 데이터 수집 로직 구현
        return []
    
    def _handle_bulk_import(self, task: Task) -> Dict:
        """대량 데이터 임포트"""
        from core.mcp import MCPFileService
        
        file_path = task.data.get('file_path')
        import_type = task.data.get('import_type')
        
        file_service = MCPFileService()
        
        # 파일 처리
        task.progress = 20
        df, stats = file_service.process_excel_import(
            file_path,
            required_columns=['name', 'email', 'department']
        )
        
        # 데이터 검증 및 저장
        task.progress = 50
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 데이터 저장 로직
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append({
                    'row': index + 2,
                    'error': str(e)
                })
            
            # 진행률 업데이트
            task.progress = 50 + int((index + 1) / len(df) * 50)
        
        return {
            'total_rows': len(df),
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors[:10]  # 최대 10개 에러만
        }
    
    def _handle_data_export(self, task: Task) -> Dict:
        """데이터 내보내기"""
        export_type = task.data.get('export_type')
        
        # TODO: 실제 내보내기 로직 구현
        
        return {
            'export_type': export_type,
            'status': 'completed'
        }
    
    def _handle_notification(self, task: Task) -> Dict:
        """알림 처리"""
        notification_type = task.data.get('type')
        recipients = task.data.get('recipients', [])
        
        # TODO: 실제 알림 로직 구현
        
        return {
            'notification_type': notification_type,
            'recipients_count': len(recipients),
            'sent_at': timezone.now().isoformat()
        }
    
    def _handle_cleanup(self, task: Task) -> Dict:
        """정리 작업"""
        from core.mcp import MCPFileService
        
        file_service = MCPFileService()
        
        # 임시 파일 정리
        cleaned_count = file_service.cleanup_temp_files()
        
        # 오래된 완료 작업 정리
        cutoff_date = timezone.now() - timedelta(days=30)
        old_tasks = [
            task_id for task_id, task in self.completed_tasks.items()
            if task.completed_at < cutoff_date
        ]
        
        for task_id in old_tasks:
            del self.completed_tasks[task_id]
        
        return {
            'temp_files_cleaned': cleaned_count,
            'old_tasks_cleaned': len(old_tasks),
            'cleaned_at': timezone.now().isoformat()
        }
    
    def schedule_recurring_task(
        self,
        task_type: str,
        data: Dict,
        schedule: str,
        priority: TaskPriority = TaskPriority.NORMAL
    ):
        """정기 작업 스케줄링"""
        # TODO: cron 스타일 스케줄링 구현
        pass
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        return {
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'scheduled_tasks': len(self.scheduled_tasks),
            'queue_size': self.task_queue.qsize(),
            'workers': self.max_workers,
            'is_running': self.is_running
        }


# 싱글톤 인스턴스
task_service = MCPTaskService()