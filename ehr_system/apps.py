"""
eHR 시스템 앱 설정
"""
from django.apps import AppConfig


class EhrSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ehr_system'
    
    def ready(self):
        """앱 초기화 시 실행"""
        # 시그널 등록
        # import ehr_system.signals
        
        # 백그라운드 태스크 매니저 시작 (선택적)
        # 주의: 개발 서버에서는 reload로 인해 중복 실행될 수 있음
        import os
        if os.environ.get('RUN_MAIN', None) == 'true':
            # 태스크 매니저 자동 시작 (선택적)
            # from utils.background_tasks import task_manager, scheduled_task_manager, setup_default_scheduled_tasks
            # task_manager.start()
            # setup_default_scheduled_tasks()
            # scheduled_task_manager.start()
            pass