import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()

def show_urls(urllist=None, depth=0):
    if urllist is None:
        urllist = []
    
    if depth > 10:
        return urllist
        
    for pattern in resolver.url_patterns:
        try:
            if hasattr(pattern, 'url_patterns'):
                show_urls(pattern.url_patterns, depth+1)
            else:
                if hasattr(pattern, '_route'):
                    route = pattern._route
                    if 'organization' in route:
                        print(f"/{route}")
        except:
            pass

# 직접 employees 앱의 URL 확인
from employees import urls as emp_urls
print("\nEmployees app organization URLs:")
for pattern in emp_urls.urlpatterns:
    if hasattr(pattern, '_route') and 'organization' in pattern._route:
        print(f"  /employees/{pattern._route}")

