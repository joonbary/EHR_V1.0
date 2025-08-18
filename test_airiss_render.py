#!/usr/bin/env python
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')

import django
django.setup()

from django.template.loader import get_template
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser

# 가짜 request 객체 생성
request = HttpRequest()
request.user = AnonymousUser()
request.META = {'HTTP_HOST': '127.0.0.1:8000'}
request.resolver_match = type('obj', (object,), {'url_name': 'dashboard'})()

# 템플릿 로드 및 렌더링
try:
    template = get_template('airiss/dashboard.html')
    context = {
        'request': request,
        'user': request.user,
        'total_analyses': 1234,
        'active_insights': 45,
        'total_conversations': 5678,
        'recent_analyses': [],
        'high_priority_insights': []
    }
    html_content = template.render(context)
    
    # JavaScript 관련 내용 검색
    if 'AIRISS Modern Dashboard' in html_content:
        print("[OK] JavaScript 코드가 템플릿에 포함되어 있습니다.")
    else:
        print("[ERROR] JavaScript 코드가 템플릿에 포함되지 않았습니다.")
    
    # extra_js 블록 확인
    if 'window.showAISettings' in html_content:
        print("[OK] extra_js 블록의 JavaScript가 렌더링되었습니다.")
    else:
        print("[ERROR] extra_js 블록이 렌더링되지 않았습니다.")
    
    # 렌더링된 HTML 일부 출력
    print("\n렌더링된 HTML에서 </body> 근처 내용:")
    body_index = html_content.rfind('</body>')
    if body_index > 0:
        print(html_content[max(0, body_index-500):body_index+10])
    
    # HTML 파일로 저장
    with open('test_rendered_airiss.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("\n[OK] 렌더링된 HTML이 test_rendered_airiss.html 파일로 저장되었습니다.")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()