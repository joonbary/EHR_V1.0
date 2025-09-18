"""
템플릿 내용 디버깅 뷰
"""
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Template, Context

def debug_template_content(request):
    """템플릿 내용을 직접 확인"""
    from pathlib import Path
    import os
    
    response_text = []
    response_text.append("=" * 60)
    response_text.append("Template Debug Info")
    response_text.append("=" * 60)
    
    # 템플릿 파일 경로
    template_path = Path(__file__).parent / "templates" / "evaluations" / "dashboard_revolutionary.html"
    response_text.append(f"Template Path: {template_path}")
    response_text.append(f"File Exists: {template_path.exists()}")
    
    if template_path.exists():
        # 파일 읽기
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 평가 시작 버튼 부분 찾기 - 더 정확한 패턴
        import re
        
        # contribution_guide 찾기
        contrib_pattern = r'contribution_guide'
        contrib_matches = re.findall(contrib_pattern, content)
        response_text.append(f"\n'contribution_guide' 텍스트 개수: {len(contrib_matches)}")
        
        # 각 평가 가이드 URL 찾기
        for eval_type in ['contribution', 'expertise', 'impact']:
            pattern = f'{eval_type}_guide'
            matches = re.findall(pattern, content)
            response_text.append(f"'{pattern}' 개수: {len(matches)}")
        
        # 평가 시작 버튼 찾기
        button_pattern = r'평가 시작'
        button_matches = re.findall(button_pattern, content)
        response_text.append(f"\n'평가 시작' 텍스트 개수: {len(button_matches)}")
        
        # 버튼 주변 컨텍스트 확인 (앞뒤 100자)
        for match in re.finditer(button_pattern, content):
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            context = content[start:end]
            response_text.append(f"\n평가 시작 버튼 컨텍스트:")
            response_text.append(context)
    
    # Django 템플릿 로더로 확인
    response_text.append("\n" + "=" * 60)
    response_text.append("Django Template Loader")
    response_text.append("=" * 60)
    
    try:
        template = get_template('evaluations/dashboard_revolutionary.html')
        response_text.append(f"Template Origin: {template.origin.name if template.origin else 'Unknown'}")
        
        # 템플릿 렌더링 테스트
        context = {
            'contribution_progress': 30,
            'expertise_progress': 50,
            'impact_progress': 70,
        }
        rendered = template.render(context, request)
        
        # 렌더링된 HTML에서 버튼 찾기
        matches = re.findall(pattern, rendered, re.DOTALL)
        response_text.append(f"\n렌더링 후 버튼 개수: {len(matches)}")
        for i, match in enumerate(matches, 1):
            response_text.append(f"\n렌더링된 버튼 {i}:")
            response_text.append(match[:200])
            
    except Exception as e:
        response_text.append(f"Template Error: {str(e)}")
    
    return HttpResponse("\n".join(response_text), content_type='text/plain; charset=utf-8')