import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

# job_profiles 앱이 제대로 설치되었는지 확인
from django.apps import apps
print("Installed apps:")
for app in apps.get_app_configs():
    print(f"  - {app.name}")

# job_profiles.urls 모듈이 임포트 가능한지 확인
try:
    import job_profiles.urls
    print("\njob_profiles.urls import: OK")
    print("URL patterns in job_profiles.urls:")
    for pattern in job_profiles.urls.urlpatterns:
        print(f"  - {pattern}")
except Exception as e:
    print(f"\njob_profiles.urls import error: {e}")

# 메인 urls.py 확인
try:
    import ehr_system.urls
    print("\nehr_system.urls patterns:")
    for pattern in ehr_system.urls.urlpatterns:
        print(f"  - {pattern}")
except Exception as e:
    print(f"\nehr_system.urls import error: {e}")