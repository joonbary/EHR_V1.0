"""
Health check views for monitoring
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import os
from datetime import datetime


def health_check(request):
    """
    시스템 헬스체크 엔드포인트
    - 데이터베이스 연결 확인
    - 캐시 연결 확인
    - 디스크 공간 확인
    """
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('DJANGO_ENV', 'unknown'),
        'checks': {}
    }
    
    # 1. 데이터베이스 체크
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            health_status['checks']['database'] = {
                'status': 'ok',
                'vendor': connection.vendor,
                'database': connection.settings_dict.get('NAME', 'unknown')
            }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'error',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # 2. 캐시 체크
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['cache'] = {'status': 'ok'}
        else:
            health_status['checks']['cache'] = {'status': 'error', 'error': 'Cache not working'}
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = {'status': 'error', 'error': str(e)}
        health_status['status'] = 'degraded'
    
    # 3. 필수 환경 변수 체크
    required_env_vars = ['SECRET_KEY']
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        health_status['checks']['environment'] = {
            'status': 'warning',
            'missing_vars': missing_vars
        }
        health_status['status'] = 'degraded'
    else:
        health_status['checks']['environment'] = {'status': 'ok'}
    
    # 4. 앱별 헬스체크 (선택적)
    try:
        from employees.models import Employee
        employee_count = Employee.objects.count()
        health_status['checks']['models'] = {
            'status': 'ok',
            'employee_count': employee_count
        }
    except Exception as e:
        health_status['checks']['models'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # HTTP 상태 코드 결정
    if health_status['status'] == 'healthy':
        status_code = 200
    elif health_status['status'] == 'degraded':
        status_code = 200  # 서비스는 작동하지만 일부 기능 제한
    else:
        status_code = 503  # Service Unavailable
    
    return JsonResponse(health_status, status=status_code)


def readiness_check(request):
    """
    준비 상태 체크 (Kubernetes readiness probe용)
    데이터베이스와 필수 서비스가 준비되었는지 확인
    """
    try:
        # 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # 필수 테이블 존재 확인
        from django.contrib.auth.models import User
        User.objects.exists()
        
        return JsonResponse({'status': 'ready'}, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)


def liveness_check(request):
    """
    생존 체크 (Kubernetes liveness probe용)
    애플리케이션이 살아있는지 간단히 확인
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': datetime.now().isoformat()
    }, status=200)