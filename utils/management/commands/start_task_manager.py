"""
Django 관리 명령어 - 태스크 매니저 시작
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import signal
import sys
import time
from utils.background_tasks import task_manager, scheduled_task_manager, setup_default_scheduled_tasks


class Command(BaseCommand):
    help = '백그라운드 태스크 매니저를 시작합니다.'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--workers',
            type=int,
            default=4,
            help='워커 스레드 수 (기본값: 4)'
        )
        
        parser.add_argument(
            '--no-scheduler',
            action='store_true',
            help='스케줄러 비활성화'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('태스크 매니저를 시작합니다...'))
        
        # 워커 수 설정
        task_manager.max_workers = options['workers']
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        
        try:
            # 태스크 매니저 시작
            task_manager.start()
            self.stdout.write(
                self.style.SUCCESS(
                    f'태스크 매니저가 {task_manager.max_workers}개의 워커로 시작되었습니다.'
                )
            )
            
            # 스케줄러 시작
            if not options['no_scheduler']:
                setup_default_scheduled_tasks()
                scheduled_task_manager.start()
                self.stdout.write(self.style.SUCCESS('스케줄러가 시작되었습니다.'))
            
            # 메인 루프
            while self.running:
                # 상태 출력 (옵션)
                active_count = len(task_manager.active_tasks)
                completed_count = len(task_manager.completed_tasks)
                
                self.stdout.write(
                    f'\r활성 작업: {active_count}, 완료된 작업: {completed_count}',
                    ending=''
                )
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            self.stdout.write('\n중단 신호를 받았습니다.')
        
        finally:
            self._shutdown()
    
    def _shutdown_handler(self, signum, frame):
        """시그널 핸들러"""
        self.running = False
    
    def _shutdown(self):
        """종료 처리"""
        self.stdout.write(self.style.WARNING('\n태스크 매니저를 종료합니다...'))
        
        # 스케줄러 중지
        if scheduled_task_manager.is_running:
            scheduled_task_manager.stop()
            self.stdout.write('스케줄러가 중지되었습니다.')
        
        # 태스크 매니저 중지
        task_manager.stop()
        self.stdout.write('태스크 매니저가 중지되었습니다.')
        
        self.stdout.write(self.style.SUCCESS('정상적으로 종료되었습니다.'))