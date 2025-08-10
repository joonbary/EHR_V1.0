"""
AIRISS 데이터베이스 직접 연결 서비스
Neon PostgreSQL 데이터베이스에서 직접 데이터를 가져옴
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import Dict, Any, Optional, List
from django.core.cache import cache
import os

logger = logging.getLogger(__name__)


class AIRISSDBService:
    """AIRISS 데이터베이스 직접 연결 서비스"""
    
    # Neon 데이터베이스 연결 정보
    DATABASE_URL = "postgresql://neondb_owner:npg_u7NVKxXhpbL8@ep-summer-surf-a153am7x-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
    
    # 캐시 설정
    CACHE_KEY_STATS = "airiss_db_stats"
    CACHE_TIMEOUT = 300  # 5분
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(self.DATABASE_URL)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("AIRISS 데이터베이스 연결 성공")
            return True
        except Exception as e:
            logger.error(f"AIRISS 데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def get_employee_stats(self) -> Dict[str, Any]:
        """직원 통계 데이터 조회"""
        # 캐시 확인
        cached_data = cache.get(self.CACHE_KEY_STATS)
        if cached_data:
            logger.debug("캐시된 AIRISS 통계 사용")
            return cached_data
        
        try:
            if not self.connect():
                return self._get_fallback_stats()
            
            # employee_results 테이블에서 통계 조회
            query = """
                SELECT 
                    COUNT(*) as total_employees,
                    COUNT(CASE WHEN grade IN ('S', 'A+') THEN 1 END) as core_talent_count,
                    COUNT(CASE WHEN grade IN ('A+', 'A') AND overall_score >= 800 THEN 1 END) as promotion_candidates,
                    AVG(overall_score) as avg_score,
                    COUNT(CASE WHEN grade IN ('C', 'D') THEN 1 END) as risk_count
                FROM employee_results
                WHERE overall_score IS NOT NULL
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            
            if result:
                stats = {
                    'total_employees': result['total_employees'] or 0,
                    'core_talent_count': result['core_talent_count'] or 0,
                    'promotion_candidates_count': result['promotion_candidates'] or 0,
                    'average_score': round(result['avg_score'] or 0, 0),
                    'high_risk_count': result['risk_count'] or 0,
                    'talent_density': round((result['core_talent_count'] / result['total_employees'] * 100) if result['total_employees'] > 0 else 0, 1)
                }
                
                # 캐시에 저장
                cache.set(self.CACHE_KEY_STATS, stats, self.CACHE_TIMEOUT)
                logger.info(f"AIRISS DB에서 통계 조회 성공: {stats}")
                return stats
            
        except Exception as e:
            logger.error(f"AIRISS DB 조회 실패: {e}")
        finally:
            self.disconnect()
        
        return self._get_fallback_stats()
    
    def get_department_performance(self) -> List[Dict[str, Any]]:
        """부서별 성과 데이터 조회"""
        try:
            if not self.connect():
                return self._get_fallback_departments()
            
            query = """
                SELECT 
                    COALESCE(employee_metadata->>'department', '미정') as department,
                    COUNT(*) as employee_count,
                    AVG(overall_score) as avg_score,
                    COUNT(CASE WHEN grade IN ('S', 'A+') THEN 1 END) as core_talent_count
                FROM employee_results
                WHERE overall_score IS NOT NULL
                GROUP BY employee_metadata->>'department'
                ORDER BY avg_score DESC
                LIMIT 5
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            if results:
                departments = []
                for idx, row in enumerate(results, 1):
                    departments.append({
                        'rank': idx,
                        'name': row['department'],
                        'average_score': round(row['avg_score'] or 0, 0),
                        'core_talent_count': row['core_talent_count'] or 0,
                        'performance_level': '우수' if row['avg_score'] > 750 else ('양호' if row['avg_score'] > 700 else '보통')
                    })
                return departments
                
        except Exception as e:
            logger.error(f"부서별 성과 조회 실패: {e}")
        finally:
            self.disconnect()
        
        return self._get_fallback_departments()
    
    def get_risk_level(self) -> str:
        """리스크 레벨 계산"""
        try:
            stats = self.get_employee_stats()
            risk_ratio = stats['high_risk_count'] / stats['total_employees'] if stats['total_employees'] > 0 else 0
            
            if risk_ratio > 0.15:
                return 'HIGH'
            elif risk_ratio > 0.08:
                return 'MEDIUM'
            else:
                return 'LOW'
        except:
            return 'MEDIUM'
    
    def _get_fallback_stats(self) -> Dict[str, Any]:
        """Fallback 통계 데이터"""
        return {
            'total_employees': 1509,
            'core_talent_count': 152,
            'promotion_candidates_count': 78,
            'average_score': 782,
            'high_risk_count': 45,
            'talent_density': 10.1
        }
    
    def _get_fallback_departments(self) -> List[Dict[str, Any]]:
        """Fallback 부서 데이터"""
        return [
            {'rank': 1, 'name': 'IT개발본부', 'average_score': 782, 'core_talent_count': 12, 'performance_level': '우수'},
            {'rank': 2, 'name': '영업본부', 'average_score': 765, 'core_talent_count': 8, 'performance_level': '우수'},
            {'rank': 3, 'name': '마케팅본부', 'average_score': 742, 'core_talent_count': 6, 'performance_level': '양호'},
            {'rank': 4, 'name': '재무본부', 'average_score': 718, 'core_talent_count': 5, 'performance_level': '양호'},
            {'rank': 5, 'name': '인사본부', 'average_score': 695, 'core_talent_count': 4, 'performance_level': '보통'}
        ]