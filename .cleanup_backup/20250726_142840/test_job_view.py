import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import RequestFactory
from job_profiles.views import job_profile_list

# 가짜 요청 생성
factory = RequestFactory()
request = factory.get('/job-profiles/')

# 뷰 직접 호출
try:
    response = job_profile_list(request)
    print(f"Response status: {response.status_code}")
    print(f"Response type: {type(response)}")
    if hasattr(response, 'content'):
        print(f"Content length: {len(response.content)}")
except Exception as e:
    print(f"Error calling view: {e}")
    import traceback
    traceback.print_exc()