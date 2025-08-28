"""
Railway 배포 환경 디버그 뷰
"""
from django.http import JsonResponse
from django.urls import get_resolver
import sys
import os

def deployment_debug(request):
    """배포 환경 디버그 정보"""
    
    # URL 패턴 확인 - 더 정확한 방법
    from django.urls import reverse, NoReverseMatch
    url_patterns = []
    url_names = []
    
    # employees 앱의 실제 URL 체크
    try:
        # employees 앱의 urlpatterns 직접 확인
        from employees import urls as employees_urls
        for pattern in employees_urls.urlpatterns:
            if hasattr(pattern, 'pattern'):
                url_patterns.append(str(pattern.pattern))
                if hasattr(pattern, 'name'):
                    url_names.append(pattern.name)
    except Exception as e:
        url_patterns = [f"Error loading patterns: {e}"]
    
    # 특정 URL reverse 테스트
    specific_urls = {}
    try:
        specific_urls['advanced_org_chart'] = reverse('employees:advanced_organization_chart')
    except NoReverseMatch:
        specific_urls['advanced_org_chart'] = 'Not found'
    
    try:
        specific_urls['org_tree_api'] = reverse('employees:org_tree_api')
    except NoReverseMatch:
        specific_urls['org_tree_api'] = 'Not found'
    
    # 시스템 정보
    debug_info = {
        'deployment_status': 'OK',
        'python_version': sys.version,
        'django_version': '5.0.1',
        'working_directory': os.getcwd(),
        'employees_url_patterns': url_patterns[:30],  # 처음 30개
        'employees_url_names': url_names[:30],
        'specific_urls': specific_urls,
        'advanced_org_chart_available': 'advanced-org-chart/' in str(url_patterns),
        'api_org_root_available': 'api/org/root' in str(url_patterns),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
        'last_deploy': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
    }
    
    # 특정 뷰 함수 확인
    try:
        from employees.views import advanced_organization_chart
        debug_info['advanced_org_chart_view'] = 'Found'
    except ImportError:
        debug_info['advanced_org_chart_view'] = 'Not Found'
    
    try:
        from employees.views import org_tree_api
        debug_info['org_tree_api_view'] = 'Found'
    except ImportError:
        debug_info['org_tree_api_view'] = 'Not Found'
    
    # 모델 확인
    try:
        from employees.models_organization import OrganizationStructure
        count = OrganizationStructure.objects.count()
        debug_info['organization_structure_model'] = f'Found ({count} records)'
    except Exception as e:
        debug_info['organization_structure_model'] = f'Error: {str(e)}'
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})