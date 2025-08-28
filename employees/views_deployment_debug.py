"""
Railway 배포 환경 디버그 뷰
"""
from django.http import JsonResponse
from django.urls import get_resolver
import sys
import os

def deployment_debug(request):
    """배포 환경 디버그 정보"""
    
    # URL 패턴 확인
    resolver = get_resolver()
    url_patterns = []
    
    # employees 앱의 URL 패턴만 추출
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'pattern'):
            pattern_str = str(pattern.pattern)
            if 'employees/' in pattern_str:
                url_patterns.append(pattern_str)
    
    # 시스템 정보
    debug_info = {
        'deployment_status': 'OK',
        'python_version': sys.version,
        'django_version': '5.0.1',
        'working_directory': os.getcwd(),
        'employees_urls': url_patterns[:20],  # 처음 20개만
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