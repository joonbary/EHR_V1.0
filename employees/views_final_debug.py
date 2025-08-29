"""
최종 디버그 - 뷰 함수 직접 테스트
"""
from django.http import HttpResponse
from django.shortcuts import render

def test_advanced_org_chart(request):
    """고급 조직도 페이지 - 직접 렌더링"""
    try:
        # 템플릿 직접 렌더링
        return render(request, 'employees/advanced_organization_chart.html')
    except Exception as e:
        return HttpResponse(f"""
        <h1>Error rendering template</h1>
        <p>Error: {str(e)}</p>
        <p>Type: {type(e).__name__}</p>
        <hr>
        <p>Template path: employees/advanced_organization_chart.html</p>
        """)

def verify_view_import(request):
    """뷰 함수 import 검증"""
    results = []
    
    # views.py에서 함수 import 시도
    try:
        from employees.views import advanced_organization_chart
        results.append("✅ advanced_organization_chart imported successfully")
        results.append(f"   Function: {advanced_organization_chart}")
        results.append(f"   Module: {advanced_organization_chart.__module__}")
    except ImportError as e:
        results.append(f"❌ Failed to import advanced_organization_chart: {e}")
    except Exception as e:
        results.append(f"❌ Unexpected error: {e}")
    
    # URL 패턴 확인
    try:
        from django.urls import reverse
        url = reverse('employees:advanced_organization_chart')
        results.append(f"✅ URL reverse successful: {url}")
    except Exception as e:
        results.append(f"❌ URL reverse failed: {e}")
    
    # 템플릿 존재 확인
    try:
        from django.template.loader import get_template
        template = get_template('employees/advanced_organization_chart.html')
        results.append("✅ Template loaded successfully")
    except Exception as e:
        results.append(f"❌ Template loading failed: {e}")
    
    html = "<h1>View Import Verification</h1><ul>"
    for result in results:
        html += f"<li>{result}</li>"
    html += "</ul>"
    
    return HttpResponse(html)