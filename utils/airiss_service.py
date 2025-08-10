"""
AIRISS AI 인사분석 시스템 연동 서비스
"""
import requests
import logging
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class AIRISSService:
    """AIRISS AI 인사분석 시스템 API 클라이언트"""
    
    # API Base URL
    BASE_URL = "https://web-production-4066.up.railway.app/api/v1/airiss"
    
    # 캐시 키와 타임아웃 설정
    CACHE_KEY_TALENT = "airiss_talent_analysis"
    CACHE_KEY_DEPT = "airiss_department_performance"
    CACHE_KEY_RISK = "airiss_risk_analysis"
    CACHE_TIMEOUT = 300  # 5분 캐싱
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
    def get_talent_analysis(self) -> Optional[Dict[str, Any]]:
        """인재풀 분석 데이터 조회"""
        # 캐시 확인
        cached_data = cache.get(self.CACHE_KEY_TALENT)
        if cached_data:
            logger.debug("Using cached talent analysis data")
            return cached_data
            
        try:
            response = self.session.get(
                f"{self.BASE_URL}/talent-analysis",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 캐시에 저장
            cache.set(self.CACHE_KEY_TALENT, data, self.CACHE_TIMEOUT)
            logger.info("Successfully fetched talent analysis data from AIRISS")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch talent analysis from AIRISS: {e}")
            return self._get_fallback_talent_data()
    
    def get_department_performance(self) -> Optional[Dict[str, Any]]:
        """부서별 성과 데이터 조회"""
        # 캐시 확인
        cached_data = cache.get(self.CACHE_KEY_DEPT)
        if cached_data:
            logger.debug("Using cached department performance data")
            return cached_data
            
        try:
            response = self.session.get(
                f"{self.BASE_URL}/department-performance",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 캐시에 저장
            cache.set(self.CACHE_KEY_DEPT, data, self.CACHE_TIMEOUT)
            logger.info("Successfully fetched department performance data from AIRISS")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch department performance from AIRISS: {e}")
            return self._get_fallback_department_data()
    
    def get_risk_analysis(self) -> Optional[Dict[str, Any]]:
        """리스크 분석 데이터 조회"""
        # 캐시 확인
        cached_data = cache.get(self.CACHE_KEY_RISK)
        if cached_data:
            logger.debug("Using cached risk analysis data")
            return cached_data
            
        try:
            response = self.session.get(
                f"{self.BASE_URL}/risk-analysis",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # 캐시에 저장
            cache.set(self.CACHE_KEY_RISK, data, self.CACHE_TIMEOUT)
            logger.info("Successfully fetched risk analysis data from AIRISS")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch risk analysis from AIRISS: {e}")
            return self._get_fallback_risk_data()
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 AIRISS 데이터 한번에 조회"""
        return {
            'talent': self.get_talent_analysis(),
            'department': self.get_department_performance(),
            'risk': self.get_risk_analysis()
        }
    
    def clear_cache(self):
        """캐시 초기화"""
        cache.delete(self.CACHE_KEY_TALENT)
        cache.delete(self.CACHE_KEY_DEPT)
        cache.delete(self.CACHE_KEY_RISK)
        logger.info("AIRISS cache cleared")
    
    # Fallback 데이터 (API 실패 시 사용)
    def _get_fallback_talent_data(self) -> Dict[str, Any]:
        """API 실패 시 사용할 기본 인재풀 데이터"""
        return {
            'summary': {
                'core_talent_count': 152,
                'promotion_candidates_count': 78,
                'talent_density': 18.5,
                'excellent_talent_count': 245,
                'development_needed_count': 120,
                'risk_talent_count': 45
            },
            'talent_pool': {
                'S': 52,
                'A+': 100,
                'A': 245,
                'B': 420,
                'C': 120,
                'D': 45
            }
        }
    
    def _get_fallback_department_data(self) -> Dict[str, Any]:
        """API 실패 시 사용할 기본 부서별 성과 데이터"""
        return {
            'departments': [
                {
                    'rank': 1,
                    'name': 'IT개발본부',
                    'average_score': 782,
                    'core_talent_count': 12,
                    'performance_level': '우수',
                    'total_employees': 85
                },
                {
                    'rank': 2,
                    'name': '영업본부',
                    'average_score': 765,
                    'core_talent_count': 8,
                    'performance_level': '우수',
                    'total_employees': 120
                },
                {
                    'rank': 3,
                    'name': '마케팅본부',
                    'average_score': 742,
                    'core_talent_count': 6,
                    'performance_level': '양호',
                    'total_employees': 45
                },
                {
                    'rank': 4,
                    'name': '재무본부',
                    'average_score': 718,
                    'core_talent_count': 5,
                    'performance_level': '양호',
                    'total_employees': 38
                },
                {
                    'rank': 5,
                    'name': '인사본부',
                    'average_score': 695,
                    'core_talent_count': 4,
                    'performance_level': '보통',
                    'total_employees': 28
                }
            ]
        }
    
    def _get_fallback_risk_data(self) -> Dict[str, Any]:
        """API 실패 시 사용할 기본 리스크 분석 데이터"""
        return {
            'risk_summary': {
                'overall_risk_level': 'MEDIUM',
                'high_risk_count': 45,
                'retention_targets': 28,
                'recommendations': [
                    '핵심인재 리텐션 프로그램 강화 필요',
                    'IT개발본부 승진 적체 해소 방안 마련 시급',
                    '영업본부 성과급 체계 개선 검토 필요',
                    '신입사원 온보딩 프로그램 강화로 조기 이탈 방지',
                    '부서간 인재 순환 프로그램 활성화 권장'
                ]
            },
            'risk_factors': {
                'resignation_risk': 12,
                'performance_risk': 18,
                'engagement_risk': 15
            }
        }


def format_talent_pool_for_chart(talent_data: Dict[str, Any]) -> Dict[str, Any]:
    """인재풀 데이터를 차트용 포맷으로 변환"""
    if not talent_data or 'summary' not in talent_data:
        return {
            'labels': [],
            'data': [],
            'backgroundColor': []
        }
    
    summary = talent_data['summary']
    
    return {
        'labels': [
            '핵심인재',
            '우수인재',
            '개발필요',
            '위험인재'
        ],
        'data': [
            summary.get('core_talent_count', 0),
            summary.get('excellent_talent_count', 0),
            summary.get('development_needed_count', 0),
            summary.get('risk_talent_count', 0)
        ],
        'backgroundColor': [
            'rgba(139, 92, 246, 0.8)',  # 보라색 - 핵심인재
            'rgba(0, 212, 255, 0.8)',    # 파란색 - 우수인재
            'rgba(255, 183, 0, 0.8)',    # 노란색 - 개발필요
            'rgba(239, 68, 68, 0.8)'     # 빨간색 - 위험인재
        ],
        'borderColor': [
            'rgba(139, 92, 246, 1)',
            'rgba(0, 212, 255, 1)',
            'rgba(255, 183, 0, 1)',
            'rgba(239, 68, 68, 1)'
        ]
    }


def get_risk_level_color(level: str) -> str:
    """리스크 레벨에 따른 색상 반환"""
    colors = {
        'HIGH': '#ef4444',     # 빨간색
        'MEDIUM': '#ff6b00',   # 주황색
        'LOW': '#10b981'       # 초록색
    }
    return colors.get(level, '#6b7280')  # 기본값: 회색