
# 직무 통합 시스템 배포 가이드

## 1. 환경 설정

### Redis 설치 및 설정
```bash
# Redis 설치
sudo apt install redis-server

# Redis 설정 (/etc/redis/redis.conf)
bind 127.0.0.1
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Elasticsearch 설치 및 설정
```bash
# Elasticsearch 설치
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update && sudo apt install elasticsearch

# 인덱스 생성
curl -X PUT "localhost:9200/job_profiles" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "job_title": {
        "type": "text",
        "fields": {
          "keyword": {"type": "keyword"},
          "completion": {"type": "completion"}
        }
      },
      "job_type": {"type": "keyword"},
      "job_category": {"type": "keyword"},
      "description": {"type": "text"},
      "requirements": {"type": "text"},
      "search_keywords": {"type": "keyword"},
      "is_active": {"type": "boolean"},
      "created_at": {"type": "date"},
      "updated_at": {"type": "date"}
    }
  }
}'
```

### Celery 설정
```python
# settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# celery.py
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

app = Celery('ehr_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

## 2. Django 설정

### URL 패턴
```python
# urls.py
from job_profile_live_integration import (
    JobSearchAPIView, JobChatbotAPIView, JobSyncAPIView
)

urlpatterns = [
    path('api/jobs/search/', JobSearchAPIView.as_view(), name='job_search'),
    path('api/jobs/chatbot/', JobChatbotAPIView.as_view(), name='job_chatbot'),
    path('api/jobs/sync/', JobSyncAPIView.as_view(), name='job_sync'),
]
```

### 모델 업데이트
```python
# models.py
class JobSynonym(models.Model):
    synonym = models.CharField(max_length=100, unique=True)
    standard_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'job_synonyms'
```

## 3. 모니터링 설정

### 로그 설정
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'job_integration.log',
        },
    },
    'loggers': {
        'JobProfileStandardizer': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'JobSearchService': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 성능 모니터링
```python
# monitoring.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        # 성능 로그
        logger.info(f"{func.__name__} 실행시간: {end_time - start_time:.3f}초")
        return result
    return wrapper
```

## 4. 운영 체크리스트

- [ ] Redis 서버 실행 확인
- [ ] Elasticsearch 서버 실행 확인
- [ ] Celery worker 실행 확인
- [ ] 초기 데이터 동기화 실행
- [ ] API 엔드포인트 테스트
- [ ] 검색 성능 테스트
- [ ] 챗봇 응답 품질 확인
- [ ] 로그 모니터링 설정
- [ ] 백업 스케줄 설정

## 5. 트러블슈팅

### 일반적인 문제들
1. Redis 연결 실패 → Redis 서버 상태 확인
2. Elasticsearch 인덱싱 실패 → 인덱스 매핑 확인
3. 검색 성능 저하 → 인덱스 최적화 실행
4. 챗봇 응답 지연 → OpenAI API 제한 확인
5. 동기화 실패 → Celery 워커 상태 확인
