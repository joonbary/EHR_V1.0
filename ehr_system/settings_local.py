"""
Local development settings for EHR System
로컬 개발 환경용 설정
"""

from .settings_base import *

# Debug
DEBUG = True

# Allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# Database - SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings for local development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Static and media files
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Channels - In-memory for development
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Logging - More verbose for development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Development-specific apps (optional)
if 'django_extensions' not in INSTALLED_APPS:
    try:
        import django_extensions
        INSTALLED_APPS += ['django_extensions']
    except ImportError:
        pass

# Disable security features for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

print("=" * 60)
print("Running with LOCAL settings")
print(f"Database: SQLite ({DATABASES['default']['NAME']})")
print(f"Debug: {DEBUG}")
print("=" * 60)