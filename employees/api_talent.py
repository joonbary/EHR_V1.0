"""
인재 관리 API 뷰
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models_talent import TalentPool, TalentCategory, PromotionCandidate, RetentionRisk


@require_GET
def talent_pool_api(request):
    """인재풀 데이터 API"""
    try:
        # 통계 데이터
        statistics = {
            'core_talent': TalentPool.objects.filter(
                category__category_code='CORE_TALENT',
                status='ACTIVE'
            ).count(),
            'promotion_candidate': PromotionCandidate.objects.filter(
                is_active=True
            ).count(),
            'retention_risk': RetentionRisk.objects.filter(
                risk_level__in=['CRITICAL', 'HIGH'],
                action_status__in=['PENDING', 'IN_PROGRESS']
            ).count(),
            'needs_attention': TalentPool.objects.filter(
                category__category_code='NEEDS_ATTENTION',
                status__in=['ACTIVE', 'MONITORING']
            ).count()
        }
        
        # 카테고리 필터
        category_filter = request.GET.get('category', '')
        
        # 인재풀 데이터
        talent_pool_qs = TalentPool.objects.select_related(
            'employee', 'category'
        ).filter(status__in=['ACTIVE', 'MONITORING'])
        
        if category_filter:
            talent_pool_qs = talent_pool_qs.filter(category__category_code=category_filter)
        
        talent_pool_data = []
        for tp in talent_pool_qs[:20]:  # 최대 20개
            talent_pool_data.append({
                'id': tp.id,
                'name': tp.employee.name if tp.employee else 'Unknown',
                'department': tp.employee.department if tp.employee else '-',
                'position': tp.employee.position if tp.employee else '-',
                'category': tp.category.get_category_code_display(),
                'ai_score': round(tp.ai_score, 1),
                'confidence': round(tp.confidence_level * 100, 0),
                'status': tp.status,
                'analyzed_date': tp.added_at.strftime('%Y-%m-%d')
            })
        
        # 승진 후보자 데이터
        promotion_candidates = []
        for pc in PromotionCandidate.objects.filter(is_active=True).select_related('employee')[:10]:
            promotion_candidates.append({
                'id': pc.id,
                'name': pc.employee.name,
                'current_position': pc.current_position,
                'target_position': pc.target_position,
                'readiness': pc.get_readiness_level_display(),
                'ai_score': round(pc.ai_recommendation_score, 1),
                'expected_date': pc.expected_promotion_date.strftime('%Y-%m-%d') if pc.expected_promotion_date else '-',
                'plan': pc.development_plan.get('summary', '개발 계획 수립 중') if isinstance(pc.development_plan, dict) else '개발 계획 수립 중'
            })
        
        # 이직 위험 데이터
        retention_risks = []
        for rr in RetentionRisk.objects.filter(
            risk_level__in=['CRITICAL', 'HIGH']
        ).select_related('employee', 'assigned_to')[:10]:
            retention_risks.append({
                'id': rr.id,
                'name': rr.employee.name,
                'department': rr.employee.department or '-',
                'risk_level': rr.get_risk_level_display(),
                'risk_score': round(rr.risk_score, 1),
                'factors': ', '.join(rr.risk_factors[:2]) if rr.risk_factors else '분석 중',
                'strategy': rr.retention_strategy[:50] + '...' if len(rr.retention_strategy) > 50 else rr.retention_strategy,
                'status': rr.get_action_status_display(),
                'assigned': rr.assigned_to.username if rr.assigned_to else '미지정'
            })
        
        return JsonResponse({
            'success': True,
            'statistics': statistics,
            'talent_pool': talent_pool_data,
            'promotion_candidates': promotion_candidates,
            'retention_risks': retention_risks
        })
        
    except Exception as e:
        # 에러 발생 시 실제 DB 데이터만 반환 (목업 데이터 제거)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'statistics': {
                'core_talent': 0,
                'promotion_candidate': 0,
                'retention_risk': 0,
                'needs_attention': 0
            },
            'talent_pool': [],
            'promotion_candidates': [],
            'retention_risks': []
        }, status=500)


@require_GET
def talent_detail_api(request, employee_id):
    """특정 직원의 인재 관리 상세 정보"""
    try:
        from employees.models import Employee
        
        employee = Employee.objects.get(id=employee_id)
        
        # 인재풀 정보
        talent_pool = TalentPool.objects.filter(employee=employee).first()
        
        # 승진 후보 정보
        promotion = PromotionCandidate.objects.filter(employee=employee, is_active=True).first()
        
        # 이직 위험 정보
        retention = RetentionRisk.objects.filter(employee=employee).first()
        
        data = {
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'department': employee.department,
                'position': employee.position,
                'hire_date': employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else None
            },
            'talent_pool': None,
            'promotion': None,
            'retention_risk': None
        }
        
        if talent_pool:
            data['talent_pool'] = {
                'category': talent_pool.category.get_category_code_display(),
                'ai_score': round(talent_pool.ai_score, 1),
                'confidence': round(talent_pool.confidence_level * 100, 0),
                'strengths': talent_pool.strengths,
                'development_areas': talent_pool.development_areas,
                'recommendations': talent_pool.recommendations,
                'status': talent_pool.status,
                'analyzed_date': talent_pool.added_at.strftime('%Y-%m-%d')
            }
        
        if promotion:
            data['promotion'] = {
                'current_position': promotion.current_position,
                'target_position': promotion.target_position,
                'readiness': promotion.get_readiness_level_display(),
                'performance_score': round(promotion.performance_score, 1),
                'potential_score': round(promotion.potential_score, 1),
                'ai_score': round(promotion.ai_recommendation_score, 1),
                'expected_date': promotion.expected_promotion_date.strftime('%Y-%m-%d') if promotion.expected_promotion_date else None,
                'development_plan': promotion.development_plan,
                'completed_requirements': promotion.completed_requirements,
                'pending_requirements': promotion.pending_requirements
            }
        
        if retention:
            data['retention_risk'] = {
                'risk_level': retention.get_risk_level_display(),
                'risk_score': round(retention.risk_score, 1),
                'risk_factors': retention.risk_factors,
                'strategy': retention.retention_strategy,
                'action_items': retention.action_items,
                'status': retention.get_action_status_display(),
                'assigned_to': retention.assigned_to.username if retention.assigned_to else None
            }
        
        return JsonResponse(data)
        
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employee not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)