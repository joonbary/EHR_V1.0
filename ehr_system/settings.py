"""
Django settings for ehr_system project.
환경에 따라 적절한 설정 파일을 선택합니다.
"""

import os

# 환경 결정
ENVIRONMENT = os.getenv('DJANGO_ENV', 'local')

# Railway 환경 감지
if os.getenv('RAILWAY_ENVIRONMENT'):
    ENVIRONMENT = 'railway'

# 환경별 설정 임포트
if ENVIRONMENT == 'railway':
    from .settings_railway import *
elif ENVIRONMENT == 'production':
    from .settings_railway import *  # Production도 Railway 설정 사용
elif ENVIRONMENT == 'local':
    from .settings_local import *
else:
    # 기본값은 로컬 설정
    from .settings_local import *

print(f"Environment: {ENVIRONMENT}")