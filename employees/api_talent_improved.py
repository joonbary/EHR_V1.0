"""
인재 관리 API - Railway 호환 개선 버전
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging
import json

logger = logging.getLogger(__name__)


@require_GET
def talent_pool_api_improved(request):
    """인재풀 데이터 API - Railway 호환 버전"""
    
    # 기본 응답 구조
    response_data = {
        'success': True,
        'statistics': {
            'core_talent': 0,
            'promotion_candidate': 0,
            'retention_risk': 0,
            'needs_attention': 0
        },
        'talent_pool': [],
        'promotion_candidates': [],
        'retention_risks': [],
        'debug_info': {}
    }
    
    try:
        with connection.cursor() as cursor:
            # 1. 데이터베이스 직접 쿼리로 통계 수집
            
            # 핵심 인재 수
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM employees_talentpool tp
                    JOIN employees_talentcategory tc ON tp.category_id = tc.id
                    WHERE tc.category_code = 'CORE_TALENT'
                    AND tp.status = 'ACTIVE'
                """)
                response_data['statistics']['core_talent'] = cursor.fetchone()[0]
            except Exception as e:
                logger.debug(f"Core talent count error: {e}")
            
            # 승진 후보자 수
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM employees_promotioncandidate
                    WHERE is_active = true
                """)
                response_data['statistics']['promotion_candidate'] = cursor.fetchone()[0]
            except Exception as e:
                logger.debug(f"Promotion candidate count error: {e}")
            
            # 이직 위험군 수
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM employees_retentionrisk
                    WHERE risk_level IN ('CRITICAL', 'HIGH')
                    AND action_status IN ('PENDING', 'IN_PROGRESS')
                """)
                response_data['statistics']['retention_risk'] = cursor.fetchone()[0]
            except Exception as e:
                logger.debug(f"Retention risk count error: {e}")
            
            # 관리 필요 인력 수
            try:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM employees_talentpool tp
                    JOIN employees_talentcategory tc ON tp.category_id = tc.id
                    WHERE tc.category_code = 'NEEDS_ATTENTION'
                    AND tp.status IN ('ACTIVE', 'MONITORING')
                """)
                response_data['statistics']['needs_attention'] = cursor.fetchone()[0]
            except Exception as e:
                logger.debug(f"Needs attention count error: {e}")
            
            # 2. 인재풀 목록 조회
            try:
                cursor.execute("""
                    SELECT 
                        e.id, e.name, e.department, e.position,
                        tp.ai_score, tc.category_code, tp.status,
                        tp.strengths, tp.development_areas
                    FROM employees_talentpool tp
                    JOIN employees_employee e ON tp.employee_id = e.id
                    JOIN employees_talentcategory tc ON tp.category_id = tc.id
                    WHERE tp.status = 'ACTIVE'
                    ORDER BY tp.ai_score DESC
                    LIMIT 20
                """)
                
                for row in cursor.fetchall():
                    try:
                        strengths = json.loads(row[7]) if row[7] else []
                        development_areas = json.loads(row[8]) if row[8] else []
                    except:
                        strengths = []
                        development_areas = []
                    
                    response_data['talent_pool'].append({
                        'id': row[0],
                        'name': row[1],
                        'department': row[2],
                        'position': row[3],
                        'ai_score': float(row[4]) if row[4] else 0,
                        'category': row[5],
                        'status': row[6],
                        'strengths': strengths,
                        'development_areas': development_areas
                    })
            except Exception as e:
                logger.debug(f"Talent pool list error: {e}")
            
            # 3. 승진 후보자 목록
            try:
                cursor.execute("""
                    SELECT 
                        e.id, e.name, e.department, e.position,
                        pc.target_position, pc.readiness_level,
                        pc.performance_score, pc.expected_promotion_date
                    FROM employees_promotioncandidate pc
                    JOIN employees_employee e ON pc.employee_id = e.id
                    WHERE pc.is_active = true
                    ORDER BY pc.performance_score DESC
                    LIMIT 10
                """)
                
                for row in cursor.fetchall():
                    response_data['promotion_candidates'].append({
                        'id': row[0],
                        'name': row[1],
                        'department': row[2],
                        'current_position': row[3],
                        'target_position': row[4],
                        'readiness_level': row[5],
                        'performance_score': float(row[6]) if row[6] else 0,
                        'expected_date': str(row[7]) if row[7] else None
                    })
            except Exception as e:
                logger.debug(f"Promotion candidates error: {e}")
            
            # 4. 이직 위험군 목록
            try:
                cursor.execute("""
                    SELECT 
                        e.id, e.name, e.department, e.position,
                        rr.risk_level, rr.risk_score, rr.action_status
                    FROM employees_retentionrisk rr
                    JOIN employees_employee e ON rr.employee_id = e.id
                    WHERE rr.risk_level IN ('CRITICAL', 'HIGH')
                    ORDER BY rr.risk_score DESC
                    LIMIT 10
                """)
                
                for row in cursor.fetchall():
                    response_data['retention_risks'].append({
                        'id': row[0],
                        'name': row[1],
                        'department': row[2],
                        'position': row[3],
                        'risk_level': row[4],
                        'risk_score': float(row[5]) if row[5] else 0,
                        'action_status': row[6]
                    })
            except Exception as e:
                logger.debug(f"Retention risks error: {e}")
            
            # 디버그 정보 추가
            response_data['debug_info'] = {
                'database': connection.vendor,
                'talent_pool_count': len(response_data['talent_pool']),
                'promotion_count': len(response_data['promotion_candidates']),
                'retention_count': len(response_data['retention_risks'])
            }
            
    except Exception as e:
        logger.error(f"Talent API error: {e}")
        response_data['success'] = False
        response_data['error'] = str(e)
    
    return JsonResponse(response_data, safe=False)


@require_GET
def talent_detail_api_improved(request, employee_id):
    """특정 직원의 인재 정보 상세 API"""
    
    response_data = {
        'success': True,
        'employee': None,
        'talent_info': None,
        'promotion_info': None,
        'retention_info': None
    }
    
    try:
        with connection.cursor() as cursor:
            # 직원 기본 정보
            cursor.execute("""
                SELECT id, name, email, department, position, hire_date
                FROM employees_employee
                WHERE id = %s
            """, [employee_id])
            
            emp_row = cursor.fetchone()
            if emp_row:
                response_data['employee'] = {
                    'id': emp_row[0],
                    'name': emp_row[1],
                    'email': emp_row[2],
                    'department': emp_row[3],
                    'position': emp_row[4],
                    'hire_date': str(emp_row[5]) if emp_row[5] else None
                }
                
                # 인재풀 정보
                cursor.execute("""
                    SELECT tp.ai_score, tc.category_code, tp.status,
                           tp.strengths, tp.development_areas
                    FROM employees_talentpool tp
                    JOIN employees_talentcategory tc ON tp.category_id = tc.id
                    WHERE tp.employee_id = %s
                """, [employee_id])
                
                talent_row = cursor.fetchone()
                if talent_row:
                    response_data['talent_info'] = {
                        'ai_score': float(talent_row[0]) if talent_row[0] else 0,
                        'category': talent_row[1],
                        'status': talent_row[2],
                        'strengths': json.loads(talent_row[3]) if talent_row[3] else [],
                        'development_areas': json.loads(talent_row[4]) if talent_row[4] else []
                    }
                
                # 승진 정보
                cursor.execute("""
                    SELECT target_position, readiness_level, performance_score,
                           expected_promotion_date
                    FROM employees_promotioncandidate
                    WHERE employee_id = %s AND is_active = true
                """, [employee_id])
                
                promo_row = cursor.fetchone()
                if promo_row:
                    response_data['promotion_info'] = {
                        'target_position': promo_row[0],
                        'readiness_level': promo_row[1],
                        'performance_score': float(promo_row[2]) if promo_row[2] else 0,
                        'expected_date': str(promo_row[3]) if promo_row[3] else None
                    }
                
                # 이직 위험 정보
                cursor.execute("""
                    SELECT risk_level, risk_score, retention_strategy, action_status
                    FROM employees_retentionrisk
                    WHERE employee_id = %s
                """, [employee_id])
                
                risk_row = cursor.fetchone()
                if risk_row:
                    response_data['retention_info'] = {
                        'risk_level': risk_row[0],
                        'risk_score': float(risk_row[1]) if risk_row[1] else 0,
                        'retention_strategy': risk_row[2],
                        'action_status': risk_row[3]
                    }
            else:
                response_data['success'] = False
                response_data['error'] = 'Employee not found'
                
    except Exception as e:
        logger.error(f"Talent detail API error: {e}")
        response_data['success'] = False
        response_data['error'] = str(e)
    
    return JsonResponse(response_data)