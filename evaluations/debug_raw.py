"""
템플릿 raw 내용 확인
"""
from django.http import HttpResponse
from pathlib import Path

def debug_raw_template(request):
    """템플릿 파일 원본 내용"""
    template_path = Path(__file__).parent / "templates" / "evaluations" / "dashboard_revolutionary.html"
    
    if not template_path.exists():
        return HttpResponse(f"Template not found: {template_path}", content_type='text/plain')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 줄 번호와 함께 출력 (390-430번 줄 주변)
    lines = content.split('\n')
    output = []
    for i, line in enumerate(lines[385:435], start=386):  # 386번째 줄부터 435번째 줄까지
        if 'contribution' in line.lower() or '평가 시작' in line:
            output.append(f">>> {i:4d}: {line}")
        else:
            output.append(f"    {i:4d}: {line}")
    
    return HttpResponse('\n'.join(output), content_type='text/plain; charset=utf-8')