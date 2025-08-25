"""
Railway production settings for EHR System
Railway 배포 환경용 설정
"""

from .settings_base import *
import dj_database_url

# Debug - False for production
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts - Railway domain
ALLOWED_HOSTS = [
    'ehrv10-production.up.railway.app',
    '.up.railway.app',
    'localhost',
    '127.0.0.1',
]

# Add Railway's internal domain if available
RAILWAY_STATIC_URL = os.getenv('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL:
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)

# Database - PostgreSQL from DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    print(f"Using PostgreSQL database from DATABASE_URL")
else:
    # Fallback to SQLite if no DATABASE_URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("WARNING: No DATABASE_URL found, using SQLite")

# CORS settings for Railway
CORS_ALLOWED_ORIGINS = [
    "https://ehrv10-production.up.railway.app",
    "https://web-production-4066.up.railway.app",  # AIRISS service
]

# Add additional CORS origins from environment
additional_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if additional_origins:
    CORS_ALLOWED_ORIGINS.extend(additional_origins.split(','))

# Static files configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for static files serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (use cloud storage in production)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Security settings for production
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://ehrv10-production.up.railway.app',
    'https://*.up.railway.app',
]

# Email configuration (use environment variables)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ehrv10.com')

# Redis configuration for Channels (if available)
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Fallback to in-memory (not recommended for production)
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }

# Logging configuration for Railway
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',  # Reduce DB query logging
            'propagate': False,
        },
    },
}

# Performance optimizations
CONN_MAX_AGE = 600  # Connection pooling
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'  # Cached sessions

# Health check endpoint
HEALTH_CHECK_URL = '/health/'

print("=" * 60)
print("Running with RAILWAY settings")
print(f"Database: {'PostgreSQL' if DATABASE_URL else 'SQLite'}")
print(f"Debug: {DEBUG}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")
print("=" * 60)