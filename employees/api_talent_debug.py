"""
인재 관리 API 뷰 - 디버깅 강화 버전
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db import connection
import traceback
import logging

logger = logging.getLogger(__name__)


@require_GET
def talent_pool_api_debug(request):
    """인재풀 데이터 API - 디버깅 버전"""
    debug_info = {
        'tables_checked': [],
        'models_imported': False,
        'database_connected': False,
        'error_details': None,
        'traceback': None
    }
    
    try:
        # 1. 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            debug_info['database_connected'] = True
            
            # 테이블 존재 확인
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN (
                    'employees_talentcategory',
                    'employees_talentpool',
                    'employees_promotioncandidate',
                    'employees_retentionrisk'
                )
            """)
            tables = [row[0] for row in cursor.fetchall()]
            debug_info['tables_checked'] = tables
        
        # 2. 모델 임포트 시도
        try:
            from .models_talent import TalentPool, TalentCategory, PromotionCandidate, RetentionRisk
            debug_info['models_imported'] = True
        except ImportError as e:
            debug_info['error_details'] = f"Model import error: {str(e)}"
            raise
        
        # 3. 통계 데이터 수집
        statistics = {}
        
        # 핵심 인재 수
        try:
            core_talent_count = TalentPool.objects.filter(
                category__category_code='CORE_TALENT',
                status='ACTIVE'
            ).count()
            statistics['core_talent'] = core_talent_count
        except Exception as e:
            statistics['core_talent'] = 0
            debug_info['core_talent_error'] = str(e)
        
        # 승진 후보자 수
        try:
            promotion_count = PromotionCandidate.objects.filter(
                is_active=True
            ).count()
            statistics['promotion_candidate'] = promotion_count
        except Exception as e:
            statistics['promotion_candidate'] = 0
            debug_info['promotion_error'] = str(e)
        
        # 이직 위험군 수
        try:
            retention_count = RetentionRisk.objects.filter(
                risk_level__in=['CRITICAL', 'HIGH'],
                action_status__in=['PENDING', 'IN_PROGRESS']
            ).count()
            statistics['retention_risk'] = retention_count
        except Exception as e:
            statistics['retention_risk'] = 0
            debug_info['retention_error'] = str(e)
        
        # 관리 필요 인력 수
        try:
            needs_attention_count = TalentPool.objects.filter(
                category__category_code='NEEDS_ATTENTION',
                status__in=['ACTIVE', 'MONITORING']
            ).count()
            statistics['needs_attention'] = needs_attention_count
        except Exception as e:
            statistics['needs_attention'] = 0
            debug_info['needs_attention_error'] = str(e)
        
        # 4. 카테고리 필터
        category_filter = request.GET.get('category', '')
        
        # 5. 인재풀 데이터
        talent_pool_data = []
        try:
            talent_pool_qs = TalentPool.objects.select_related(
                'employee', 'category'
            ).filter(status__in=['ACTIVE', 'MONITORING'])
            
            if category_filter:
                talent_pool_qs = talent_pool_qs.filter(category__category_code=category_filter)
            
            for tp in talent_pool_qs[:20]:
                talent_pool_data.append({
                    'id': tp.id,
                    'name': tp.employee.name if tp.employee else 'Unknown',
                    'department': tp.employee.department if tp.employee else '-',
                    'position': tp.employee.position if tp.employee else '-',
                    'category': tp.category.get_category_code_display() if tp.category else '-',
                    'ai_score': round(tp.ai_score, 1),
                    'confidence': round(tp.confidence_level * 100, 0),
                    'status': tp.status,
                    'analyzed_date': tp.added_at.strftime('%Y-%m-%d')
                })
        except Exception as e:
            debug_info['talent_pool_error'] = str(e)
        
        # 6. 승진 후보자 데이터
        promotion_candidates = []
        try:
            for pc in PromotionCandidate.objects.filter(is_active=True).select_related('employee')[:10]:
                promotion_candidates.append({
                    'id': pc.id,
                    'name': pc.employee.name if pc.employee else 'Unknown',
                    'current_position': pc.current_position or '-',
                    'target_position': pc.target_position or '-',
                    'readiness': pc.get_readiness_level_display() if hasattr(pc, 'get_readiness_level_display') else pc.readiness_level,
                    'ai_score': round(pc.ai_recommendation_score, 1),
                    'expected_date': pc.expected_promotion_date.strftime('%Y-%m-%d') if pc.expected_promotion_date else '-',
                    'plan': pc.development_plan.get('summary', '개발 계획 수립 중') if isinstance(pc.development_plan, dict) else '개발 계획 수립 중'
                })
        except Exception as e:
            debug_info['promotion_candidates_error'] = str(e)
        
        # 7. 이직 위험 데이터
        retention_risks = []
        try:
            for rr in RetentionRisk.objects.filter(
                risk_level__in=['CRITICAL', 'HIGH']
            ).select_related('employee', 'assigned_to')[:10]:
                retention_risks.append({
                    'id': rr.id,
                    'name': rr.employee.name if rr.employee else 'Unknown',
                    'department': rr.employee.department if rr.employee and hasattr(rr.employee, 'department') else '-',
                    'risk_level': rr.get_risk_level_display() if hasattr(rr, 'get_risk_level_display') else rr.risk_level,
                    'risk_score': round(rr.risk_score, 1),
                    'factors': ', '.join(rr.risk_factors[:2]) if rr.risk_factors and isinstance(rr.risk_factors, list) else '분석 중',
                    'strategy': rr.retention_strategy[:50] + '...' if rr.retention_strategy and len(rr.retention_strategy) > 50 else rr.retention_strategy or '-',
                    'status': rr.get_action_status_display() if hasattr(rr, 'get_action_status_display') else rr.action_status,
                    'assigned': rr.assigned_to.username if rr.assigned_to else '미지정'
                })
        except Exception as e:
            debug_info['retention_risks_error'] = str(e)
        
        return JsonResponse({
            'success': True,
            'statistics': statistics,
            'talent_pool': talent_pool_data,
            'promotion_candidates': promotion_candidates,
            'retention_risks': retention_risks,
            'debug_info': debug_info
        })
        
    except Exception as e:
        logger.error(f"Talent API Error: {str(e)}")
        debug_info['error_details'] = str(e)
        debug_info['traceback'] = traceback.format_exc()
        
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
            'retention_risks': [],
            'debug_info': debug_info
        }, status=500)


@require_GET 
def test_talent_db(request):
    """인재 관리 DB 연결 테스트"""
    results = {
        'database_connected': False,
        'tables_exist': {},
        'models_work': {},
        'sample_data': {}
    }
    
    try:
        # 1. 데이터베이스 연결 테스트
        with connection.cursor() as cursor:
            # SQLite와 PostgreSQL 구분
            if connection.vendor == 'postgresql':
                cursor.execute("SELECT current_database(), current_user")
                db_info = cursor.fetchone()
                results['database_info'] = {
                    'database': db_info[0],
                    'user': db_info[1],
                    'vendor': 'postgresql'
                }
            else:
                cursor.execute("SELECT 1")
                results['database_info'] = {
                    'vendor': connection.vendor,
                    'database': 'sqlite'
                }
            results['database_connected'] = True
            
            # 2. 테이블 존재 확인
            tables_to_check = [
                'employees_talentcategory',
                'employees_talentpool',
                'employees_promotioncandidate',
                'employees_retentionrisk',
                'employees_employee'
            ]
            
            for table in tables_to_check:
                if connection.vendor == 'postgresql':
                    cursor.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, [table])
                    exists = cursor.fetchone()[0]
                else:  # SQLite
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=%s
                    """, [table])
                    exists = cursor.fetchone() is not None
                results['tables_exist'][table] = exists
                
                if exists:
                    # 테이블의 레코드 수 확인
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    results['tables_exist'][f"{table}_count"] = count
        
        # 3. 모델 작동 테스트
        try:
            from .models_talent import TalentCategory, TalentPool, PromotionCandidate, RetentionRisk
            from .models import Employee
            
            results['models_work']['import'] = True
            
            # 각 모델 쿼리 테스트
            results['models_work']['TalentCategory'] = TalentCategory.objects.count()
            results['models_work']['TalentPool'] = TalentPool.objects.count()
            results['models_work']['PromotionCandidate'] = PromotionCandidate.objects.count()
            results['models_work']['RetentionRisk'] = RetentionRisk.objects.count()
            results['models_work']['Employee'] = Employee.objects.count()
            
            # 샘플 데이터 가져오기
            if TalentCategory.objects.exists():
                category = TalentCategory.objects.first()
                results['sample_data']['category'] = {
                    'id': category.id,
                    'name': category.name,
                    'code': category.category_code
                }
            
            if Employee.objects.exists():
                employee = Employee.objects.first()
                results['sample_data']['employee'] = {
                    'id': employee.id,
                    'name': employee.name,
                    'department': getattr(employee, 'department', 'N/A')
                }
                
        except Exception as e:
            results['models_work']['error'] = str(e)
            results['models_work']['traceback'] = traceback.format_exc()
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        results['error'] = str(e)
        results['traceback'] = traceback.format_exc()
        
        return JsonResponse({
            'success': False,
            'results': results,
            'error': str(e)
        }, status=500)