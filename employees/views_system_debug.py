"""
System debug views for Railway deployment troubleshooting
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from employees.models import Employee
from django.conf import settings
import os
from datetime import datetime

@csrf_exempt
def system_debug_info(request):
    """Complete system debugging information"""
    try:
        from django.db import connection
        
        # Database connection info
        db_info = {
            'engine': settings.DATABASES['default']['ENGINE'],
            'host': settings.DATABASES['default'].get('HOST', 'N/A'),
            'name': settings.DATABASES['default'].get('NAME', 'N/A'),
            'vendor': connection.vendor,
        }
        
        # Environment info
        env_info = {
            'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'Not set'),
            'DATABASE_URL': 'Set' if os.environ.get('DATABASE_URL') else 'Not set',
            'DEBUG': settings.DEBUG,
            'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE'),
        }
        
        # Employee data check
        employee_count = Employee.objects.count()
        
        # Get sample employees
        sample_employees = []
        if employee_count > 0:
            for emp in Employee.objects.all()[:5]:
                sample_employees.append({
                    'id': emp.id,
                    'no': emp.no,
                    'name': emp.name,
                    'company': emp.company,
                    'headquarters1': emp.headquarters1,
                    'department': emp.department
                })
        
        # Check table existence
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename = 'employees_employee'
            """)
            table_exists = cursor.fetchone() is not None
            
            # Get row count directly from SQL
            if table_exists:
                cursor.execute("SELECT COUNT(*) FROM employees_employee")
                sql_count = cursor.fetchone()[0]
            else:
                sql_count = 0
        
        # Statistics by company
        company_stats = {}
        if employee_count > 0:
            from django.db.models import Count
            stats = Employee.objects.values('company').annotate(count=Count('id'))
            for stat in stats:
                company_stats[stat['company'] or 'Unknown'] = stat['count']
        
        # Statistics by headquarters
        hq_stats = {}
        if employee_count > 0:
            stats = Employee.objects.values('headquarters1').annotate(count=Count('id'))
            for stat in stats:
                hq_stats[stat['headquarters1'] or 'Unknown'] = stat['count']
        
        response_data = {
            'timestamp': datetime.now().isoformat(),
            'status': 'OK',
            'database': db_info,
            'environment': env_info,
            'employee_data': {
                'django_count': employee_count,
                'sql_count': sql_count,
                'table_exists': table_exists,
                'sample_employees': sample_employees,
                'company_distribution': company_stats,
                'headquarters_distribution': hq_stats,
            },
            'debug_message': f"Employee table exists: {table_exists}, Django count: {employee_count}, SQL count: {sql_count}"
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }, status=500, json_dumps_params={'ensure_ascii': False, 'indent': 2})

@csrf_exempt
def force_load_employees(request):
    """Force load OK employees data"""
    try:
        import subprocess
        
        # Run the load script
        result = subprocess.run(
            ['python', 'load_ok_employees.py'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Get current count
        employee_count = Employee.objects.count()
        
        return JsonResponse({
            'status': 'completed',
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode,
            'current_employee_count': employee_count,
            'timestamp': datetime.now().isoformat()
        }, json_dumps_params={'ensure_ascii': False, 'indent': 2})
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }, status=500, json_dumps_params={'ensure_ascii': False, 'indent': 2})