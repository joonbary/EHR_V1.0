
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q
import logging
import json

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def skillmap_heatmap_api(request, department_id):
    '''스킬맵 히트맵 데이터 API with 완전한 에러 처리'''
    
    logger.info(f"[HEATMAP_API] Request for department: {department_id}")
    
    try:
        # 데이터 조회
        employees = Employee.objects.filter(
            department=department_id,
            employment_status='재직'
        ).prefetch_related('skills')
        
        logger.info(f"[HEATMAP_API] Found {employees.count()} employees")
        
        # 히트맵 데이터 생성
        heatmap_data = []
        
        for employee in employees:
            for skill in employee.skills.all():
                # NaN 체크 및 기본값 처리
                proficiency = skill.proficiency_level
                if proficiency is None or not isinstance(proficiency, (int, float)):
                    proficiency = 0
                elif proficiency < 0 or proficiency > 100:
                    proficiency = max(0, min(100, proficiency))
                
                heatmap_data.append({
                    'employee': employee.name,
                    'skill': skill.skill_name,
                    'proficiency': proficiency,
                    'skill_category': skill.skill_category
                })
        
        logger.info(f"[HEATMAP_API] Generated {len(heatmap_data)} data points")
        
        return JsonResponse({
            'status': 'success',
            'department': department_id,
            'results': heatmap_data,
            'count': len(heatmap_data)
        })
        
    except Exception as e:
        logger.error(f"[HEATMAP_API] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'results': []
        }, status=500)


@require_http_methods(["GET"])
def employees_by_department_api(request, department_id):
    '''부서별 직원 목록 API with 스킬 카운트'''
    
    logger.info(f"[EMPLOYEES_API] Request for department: {department_id}")
    
    try:
        # 직원 조회 with 스킬 카운트
        employees = Employee.objects.filter(
            department=department_id,
            employment_status='재직'
        ).annotate(
            skill_count=Count('skills')
        ).order_by('name')
        
        logger.info(f"[EMPLOYEES_API] Found {employees.count()} employees")
        
        # 직원 데이터 직렬화
        employee_data = []
        for emp in employees:
            employee_data.append({
                'id': str(emp.id),
                'name': emp.name,
                'job_title': emp.job_title,
                'skill_count': emp.skill_count,
                'email': emp.email,
                'hire_date': emp.hire_date.isoformat() if emp.hire_date else None
            })
        
        return JsonResponse({
            'status': 'success',
            'department': department_id,
            'results': employee_data,
            'count': len(employee_data)
        })
        
    except Exception as e:
        logger.error(f"[EMPLOYEES_API] Error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'results': []
        }, status=500)
