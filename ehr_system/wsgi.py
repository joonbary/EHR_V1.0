"""
WSGI config for ehr_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

# Railway 환경에서 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehr_system.settings")

# 디버그 출력
print(f"WSGI: Python path: {sys.path}", flush=True)
print(f"WSGI: DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}", flush=True)
print(f"WSGI: Current directory: {os.getcwd()}", flush=True)

application = get_wsgi_application()
print("WSGI: Application loaded successfully", flush=True)
