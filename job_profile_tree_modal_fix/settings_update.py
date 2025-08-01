# settings.py 업데이트 내용

# 인증 관련 설정 제거/수정
# LOGIN_URL = '/login/'  # 제거
# LOGIN_REDIRECT_URL = '/'  # 제거
# LOGOUT_REDIRECT_URL = '/'  # 제거

# 미들웨어에서 인증 관련 제거 (선택사항)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',  # 필요시 제거
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 정적 파일 설정
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                # 'django.contrib.auth.context_processors.auth',  # 필요시 제거
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# INSTALLED_APPS에서 불필요한 앱 제거 (선택사항)
INSTALLED_APPS = [
    'django.contrib.admin',
    # 'django.contrib.auth',  # 필요시 제거
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 로컬 앱
    'job_profiles',
    # 다른 앱들...
]
