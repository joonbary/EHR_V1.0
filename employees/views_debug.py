"""
디버그용 뷰 - 직원 데이터 표시 문제 해결
"""
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from .models import Employee
import json

def debug_employee_count(request):
    """데이터베이스의 실제 직원 수 확인"""
    try:
        total = Employee.objects.count()
        first_10 = list(Employee.objects.all()[:10].values('id', 'name', 'department'))
        
        return JsonResponse({
            'total_count': total,
            'first_10_employees': first_10,
            'database_backend': str(Employee.objects.db),
            'model_name': str(Employee._meta.db_table)
        }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        return JsonResponse({'error': str(e)})

def debug_employee_list(request):
    """간단한 HTML로 직원 목록 표시"""
    try:
        # values()를 사용하여 특정 필드만 선택
        employees = Employee.objects.values('id', 'no', 'name', 'department', 'position', 'email')[:20]
        total = Employee.objects.count()
        
        html = f"""
        <html>
        <head><title>Debug Employee List</title></head>
        <body>
            <h1>직원 디버그 페이지</h1>
            <h2>총 {total}명</h2>
            <table border="1">
                <tr>
                    <th>ID</th>
                    <th>사번</th>
                    <th>이름</th>
                    <th>부서</th>
                    <th>직급</th>
                    <th>이메일</th>
                </tr>
        """
        
        for emp in employees:
            html += f"""
                <tr>
                    <td>{emp.get('id', '-')}</td>
                    <td>{emp.get('no', '-')}</td>
                    <td>{emp.get('name', '-')}</td>
                    <td>{emp.get('department', '-')}</td>
                    <td>{emp.get('position', '-')}</td>
                    <td>{emp.get('email', '-')}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return HttpResponse(html)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def debug_template_context(request):
    """ListView와 동일한 컨텍스트로 테스트"""
    from django.views.generic import ListView
    
    class TestListView(ListView):
        model = Employee
        template_name = 'employees/debug_list.html'
        context_object_name = 'employees'
        paginate_by = 20
        
        def get_queryset(self):
            return Employee.objects.all().order_by('name')
    
    view = TestListView.as_view()
    return view(request)