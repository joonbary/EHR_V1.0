
# Celery 설정 파일

import os
from celery import Celery

# Django 설정 모듈 지정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

# Celery 앱 생성
app = Celery('ehr_system')

# Django 설정에서 구성 로드
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django 앱에서 태스크 자동 발견
app.autodiscover_tasks()

# 주기적 태스크 설정
from celery.schedules import crontab

app.conf.beat_schedule = {
    'sync-all-jobs-daily': {
        'task': 'job_profile_live_integration.batch_sync_all_jobs',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
    'cleanup-cache-hourly': {
        'task': 'job_profile_live_integration.cleanup_expired_cache',
        'schedule': crontab(minute=0),  # 매시 정각
    },
}
