from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee

@csrf_exempt
def test_database(request):
    """데이터베이스 상태를 확인하는 테스트 엔드포인트"""
    from django.db import connection
    
    result = {
        'status': 'checking',
        'database_info': {},
        'table_info': {},
        'data_info': {}
    }
    
    # 1. 데이터베이스 정보
    try:
        from django.conf import settings
        db_settings = settings.DATABASES['default']
        result['database_info'] = {
            'engine': db_settings['ENGINE'],
            'name': db_settings.get('NAME', 'N/A')
        }
    except:
        pass
    
    # 2. 테이블 구조 확인
    try:
        with connection.cursor() as cursor:
            # 테이블 존재 확인
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees_employee'")
            table_exists = cursor.fetchone()
            result['table_info']['exists'] = bool(table_exists)
            
            if table_exists:
                # 컬럼 정보
                cursor.execute("PRAGMA table_info(employees_employee)")
                columns = cursor.fetchall()
                result['table_info']['columns'] = [col[1] for col in columns]
                result['table_info']['has_user_id'] = 'user_id' in result['table_info']['columns']
                
                # 레코드 수
                cursor.execute("SELECT COUNT(*) FROM employees_employee")
                result['table_info']['record_count'] = cursor.fetchone()[0]
    except Exception as e:
        result['table_info']['error'] = str(e)
    
    # 3. ORM으로 데이터 접근 시도
    try:
        # select_related 없이 시도
        employees = Employee.objects.all()[:5]
        result['data_info']['orm_count'] = Employee.objects.count()
        
        employee_list = []
        for emp in employees:
            employee_list.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'department': emp.department
            })
        result['data_info']['sample_employees'] = employee_list
        result['status'] = 'success'
        
    except Exception as e:
        result['data_info']['orm_error'] = str(e)
        
        # SQL로 직접 조회 시도
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, name, email, department FROM employees_employee LIMIT 5")
                rows = cursor.fetchall()
                result['data_info']['sql_data'] = [
                    {'id': row[0], 'name': row[1], 'email': row[2], 'department': row[3]}
                    for row in rows
                ]
        except Exception as e2:
            result['data_info']['sql_error'] = str(e2)
        
        result['status'] = 'partial'
    
    return JsonResponse(result)