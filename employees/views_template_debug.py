"""
템플릿 로딩 디버그 뷰
"""
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import os

def template_debug(request):
    """템플릿 로딩 상태 확인"""
    
    debug_info = {
        'status': 'checking',
        'templates': {},
        'template_dirs': [],
        'file_system_check': {}
    }
    
    # Django 템플릿 디렉토리 확인
    from django.conf import settings
    debug_info['template_dirs'] = settings.TEMPLATES[0].get('DIRS', [])
    
    # 템플릿 로딩 테스트
    templates_to_check = [
        'employees/advanced_organization_chart.html',
        'employees/organization_chart.html',
        'base.html',
        'base_revolutionary.html'
    ]
    
    for template_name in templates_to_check:
        try:
            template = get_template(template_name)
            debug_info['templates'][template_name] = {
                'status': 'found',
                'path': template.origin.name if hasattr(template, 'origin') else 'unknown'
            }
        except TemplateDoesNotExist:
            debug_info['templates'][template_name] = {
                'status': 'not_found',
                'path': None
            }
    
    # 파일 시스템 직접 확인
    app_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(app_dir, 'templates', 'employees')
    
    debug_info['file_system_check']['template_dir'] = template_dir
    debug_info['file_system_check']['dir_exists'] = os.path.exists(template_dir)
    
    if os.path.exists(template_dir):
        files = os.listdir(template_dir)
        debug_info['file_system_check']['files'] = files[:20]  # 처음 20개만
        debug_info['file_system_check']['advanced_exists'] = 'advanced_organization_chart.html' in files
    else:
        debug_info['file_system_check']['files'] = []
        debug_info['file_system_check']['advanced_exists'] = False
    
    # 실제 경로에서 파일 존재 확인
    advanced_path = os.path.join(template_dir, 'advanced_organization_chart.html')
    debug_info['file_system_check']['advanced_full_path'] = advanced_path
    debug_info['file_system_check']['advanced_file_exists'] = os.path.exists(advanced_path)
    
    if os.path.exists(advanced_path):
        debug_info['file_system_check']['advanced_file_size'] = os.path.getsize(advanced_path)
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})

def render_advanced_org_chart(request):
    """고급 조직도 페이지 강제 렌더링"""
    try:
        # 템플릿 직접 로드 시도
        from django.template.loader import render_to_string
        html_content = render_to_string('employees/advanced_organization_chart.html')
        return HttpResponse(html_content)
    except TemplateDoesNotExist as e:
        return JsonResponse({
            'error': 'Template not found',
            'details': str(e),
            'template_name': 'employees/advanced_organization_chart.html'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': 'Rendering error',
            'details': str(e),
            'type': type(e).__name__
        }, status=500)