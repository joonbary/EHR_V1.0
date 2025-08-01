
# Django 통합 설정

# Redis 설정
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery 설정
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'

# Elasticsearch 설정
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

# OpenAI 설정
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 직무 통합 시스템 설정
JOB_INTEGRATION = {
    'CACHE_TTL': 3600,
    'SEARCH_PAGE_SIZE': 20,
    'FUZZY_MATCH_THRESHOLD': 0.7,
    'CHATBOT_MAX_TOKENS': 500,
    'SYNC_BATCH_SIZE': 100
}

# 추가된 앱
INSTALLED_APPS += [
    'django_redis',
    'elasticsearch_dsl',
    'job_profiles',
]

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'job_integration.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'JobProfileStandardizer': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'JobSearchService': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'JobChatbotService': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
