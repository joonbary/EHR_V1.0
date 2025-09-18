"""
템플릿 디버깅 뷰
"""
from django.http import JsonResponse
from django.urls import reverse

def debug_urls(request):
    """URL reverse 결과를 JSON으로 반환"""
    results = {}
    
    urls_to_test = [
        'evaluations:dashboard',
        'evaluations:contribution_guide',
        'evaluations:contribution_employees',
        'evaluations:expertise_guide',
        'evaluations:expertise_employees',
        'evaluations:impact_guide',
        'evaluations:impact_employees',
    ]
    
    for url_name in urls_to_test:
        try:
            resolved_url = reverse(url_name)
            results[url_name] = {
                'status': 'success',
                'url': resolved_url
            }
        except Exception as e:
            results[url_name] = {
                'status': 'error',
                'error': str(e)
            }
    
    # 템플릿 정보 추가
    from django.template.loader import get_template
    try:
        template = get_template('evaluations/dashboard_revolutionary.html')
        results['template_info'] = {
            'name': template.origin.name if template.origin else 'Unknown',
            'template_dirs': str(template.engine.dirs) if hasattr(template, 'engine') else 'Unknown'
        }
    except Exception as e:
        results['template_info'] = {'error': str(e)}
    
    return JsonResponse(results, json_dumps_params={'indent': 2})