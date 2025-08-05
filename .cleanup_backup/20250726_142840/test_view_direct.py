import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from evaluations.views import my_evaluations_dashboard, evaluation_dashboard

# RequestFactory 생성
factory = RequestFactory()

# 테스트용 request 생성
request = factory.get('/evaluations/my-evaluations/')

# 사용자 설정 (첫 번째 superuser 사용)
request.user = User.objects.filter(is_superuser=True).first()

if request.user:
    print(f"Testing with user: {request.user.username}")
    
    # my_evaluations_dashboard 직접 호출
    print("\n=== Calling my_evaluations_dashboard directly ===")
    try:
        response = my_evaluations_dashboard(request)
        print(f"Response status: {response.status_code}")
        print(f"Response type: {type(response)}")
        if hasattr(response, 'url'):
            print(f"Redirect URL: {response.url}")
        else:
            print(f"Content preview: {str(response.content[:100])}")
    except Exception as e:
        print(f"Error: {e}")
    
    # evaluation_dashboard 호출
    print("\n=== Calling evaluation_dashboard directly ===")
    try:
        response = evaluation_dashboard(request)
        print(f"Response status: {response.status_code}")
        print(f"Response type: {type(response)}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No superuser found!")