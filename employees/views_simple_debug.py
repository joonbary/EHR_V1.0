"""
간단한 디버그 뷰 - 최소한의 정보만 제공
"""
from django.http import JsonResponse
import os

def simple_debug(request):
    """최소한의 디버그 정보"""
    
    # 현재 작업 디렉토리
    cwd = os.getcwd()
    
    # employees 앱 디렉토리
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 템플릿 디렉토리 경로들
    paths = {
        'working_dir': cwd,
        'app_dir': app_dir,
        'template_path_1': os.path.join(app_dir, 'templates', 'employees'),
        'template_path_2': os.path.join(cwd, 'employees', 'templates', 'employees'),
    }
    
    # 각 경로에서 파일 확인
    results = {}
    for name, path in paths.items():
        results[name] = {
            'path': path,
            'exists': os.path.exists(path)
        }
        
        if name.startswith('template_path') and os.path.exists(path):
            target_file = os.path.join(path, 'advanced_organization_chart.html')
            results[name]['advanced_chart_exists'] = os.path.exists(target_file)
            if os.path.exists(target_file):
                results[name]['file_size'] = os.path.getsize(target_file)
    
    # Django 템플릿 로더 테스트
    template_test = {}
    try:
        from django.template.loader import get_template
        template = get_template('employees/advanced_organization_chart.html')
        template_test['status'] = 'success'
        template_test['name'] = template.origin.name if hasattr(template, 'origin') else 'found'
    except Exception as e:
        template_test['status'] = 'failed'
        template_test['error'] = str(e)
    
    return JsonResponse({
        'paths': results,
        'template_loader': template_test
    }, json_dumps_params={'indent': 2})