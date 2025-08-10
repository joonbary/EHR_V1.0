"""
AIRISS MSA API 연동 서비스
정제된 데이터를 AIRISS API에서 직접 가져옴
"""
import requests
import logging
from typing import Dict, Any, List, Optional
from django.core.cache import cache
from django.conf import settings
import json

logger = logging.getLogger(__name__)


class AIRISSAPIService:
    """AIRISS MSA API 연동 서비스"""
    
    # AIRISS API 엔드포인트
    BASE_URL = "https://airiss-fastapi-production.up.railway.app"
    
    # API 엔드포인트
    ENDPOINTS = {
        'employee_analysis': '/api/v1/ai/employees/analysis',
        'risk_assessment': '/api/v1/ai/risk/assessment',
        'department_stats': '/api/v1/ai/departments/statistics',
        'recommendations': '/api/v1/ai/recommendations',
        'batch_analysis': '/api/v1/ai/batch/analysis'
    }
    
    # 캐시 설정
    CACHE_PREFIX = "airiss_api"
    CACHE_TIMEOUT = 600  # 10분
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """캐시 키 생성"""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{self.CACHE_PREFIX}:{endpoint}:{param_str}"
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """API 요청 실행"""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"AIRISS API 오류: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("AIRISS API 타임아웃")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("AIRISS API 연결 실패")
            return None
        except Exception as e:
            logger.error(f"AIRISS API 요청 실패: {e}")
            return None
    
    def get_risk_employees(self, limit: int = 20) -> List[Dict[str, Any]]:
        """이직 위험 직원 목록 조회 (정제된 데이터)"""
        # 캐시 확인
        cache_key = self._get_cache_key('risk_employees', {'limit': limit})
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug("캐시된 AIRISS 위험 직원 데이터 사용")
            return cached_data
        
        # API 호출
        endpoint = self.ENDPOINTS['risk_assessment']
        params = {
            'limit': limit,
            'risk_level': 'high',
            'include_analysis': True
        }
        
        response = self._make_request(endpoint, params=params)
        
        if response and 'data' in response:
            risk_employees = []
            for item in response['data']:
                risk_employees.append({
                    'employee_id': item.get('employee_id'),
                    'name': item.get('name', '미상'),
                    'department': item.get('department', '미정'),
                    'position': item.get('position', '미정'),
                    'risk_score': item.get('risk_score', 0),
                    'risk_level': item.get('risk_level', 'UNKNOWN'),
                    'overall_score': item.get('overall_score', 0),
                    'grade': item.get('grade', 'N/A'),
                    'key_factors': item.get('key_factors', []),
                    'ai_insights': item.get('ai_insights', ''),
                    'recommended_actions': item.get('recommended_actions', [])
                })
            
            # 캐시 저장
            cache.set(cache_key, risk_employees, self.CACHE_TIMEOUT)
            logger.info(f"AIRISS API에서 {len(risk_employees)}명의 위험 직원 조회 성공")
            return risk_employees
        
        # 실패 시 기본값
        return self._get_fallback_risk_employees()
    
    def get_department_statistics(self) -> Dict[str, Any]:
        """부서별 통계 조회 (정제된 데이터)"""
        # 캐시 확인
        cache_key = self._get_cache_key('dept_stats')
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # API 호출
        endpoint = self.ENDPOINTS['department_stats']
        response = self._make_request(endpoint)
        
        if response and 'data' in response:
            dept_stats = {}
            for dept in response['data']:
                dept_name = dept.get('department_name', '미정')
                dept_stats[dept_name] = {
                    'total_employees': dept.get('total_count', 0),
                    'high_risk_count': dept.get('high_risk_count', 0),
                    'average_score': dept.get('avg_score', 0),
                    'risk_ratio': dept.get('risk_ratio', 0),
                    'top_risks': dept.get('top_risk_factors', []),
                    'trend': dept.get('trend', 'stable')
                }
            
            # 캐시 저장
            cache.set(cache_key, dept_stats, self.CACHE_TIMEOUT)
            return dept_stats
        
        return self._get_fallback_department_stats()
    
    def get_ai_recommendations(self, employee_ids: List[str] = None) -> List[Dict[str, Any]]:
        """AI 추천사항 조회"""
        # API 호출
        endpoint = self.ENDPOINTS['recommendations']
        data = {
            'employee_ids': employee_ids,
            'recommendation_type': 'retention',
            'priority': 'high'
        }
        
        response = self._make_request(endpoint, method='POST', data=data)
        
        if response and 'recommendations' in response:
            return response['recommendations']
        
        # 기본 추천사항
        return [
            {
                'type': 'immediate',
                'action': '1:1 면담 실시',
                'priority': 'high',
                'expected_impact': 'high'
            },
            {
                'type': 'short_term',
                'action': '경력개발 계획 수립',
                'priority': 'medium',
                'expected_impact': 'medium'
            },
            {
                'type': 'long_term',
                'action': '보상체계 재검토',
                'priority': 'medium',
                'expected_impact': 'high'
            }
        ]
    
    def get_batch_analysis(self, department: str = None) -> Dict[str, Any]:
        """배치 분석 실행"""
        endpoint = self.ENDPOINTS['batch_analysis']
        data = {
            'department': department,
            'analysis_type': 'comprehensive',
            'include_predictions': True
        }
        
        response = self._make_request(endpoint, method='POST', data=data)
        
        if response:
            return {
                'total_analyzed': response.get('total_analyzed', 0),
                'high_risk_identified': response.get('high_risk_count', 0),
                'average_risk_score': response.get('avg_risk_score', 0),
                'key_insights': response.get('insights', []),
                'timestamp': response.get('timestamp')
            }
        
        return {
            'total_analyzed': 0,
            'high_risk_identified': 0,
            'average_risk_score': 0,
            'key_insights': [],
            'timestamp': None
        }
    
    def _get_fallback_risk_employees(self) -> List[Dict[str, Any]]:
        """폴백 위험 직원 데이터"""
        return [
            {
                'employee_id': 'EMP001',
                'name': '김철수',
                'department': '마케팅본부',
                'position': '대리',
                'risk_score': 0.85,
                'risk_level': 'HIGH',
                'overall_score': 580,
                'grade': 'C',
                'key_factors': ['낮은 성과 점수', '장기 근속'],
                'ai_insights': '이직 가능성이 높은 것으로 분석됨',
                'recommended_actions': ['1:1 면담', '경력 상담']
            },
            {
                'employee_id': 'EMP002',
                'name': '이영희',
                'department': 'IT본부',
                'position': '사원',
                'risk_score': 0.75,
                'risk_level': 'MEDIUM',
                'overall_score': 620,
                'grade': 'C',
                'key_factors': ['업무 과부하', '성장 기회 부족'],
                'ai_insights': '번아웃 위험이 있음',
                'recommended_actions': ['업무 재배분', '교육 기회 제공']
            }
        ]
    
    def _get_fallback_department_stats(self) -> Dict[str, Any]:
        """폴백 부서별 통계"""
        return {
            '마케팅본부': {
                'total_employees': 120,
                'high_risk_count': 15,
                'average_score': 720,
                'risk_ratio': 12.5,
                'top_risks': ['낮은 성과', '장기 근속'],
                'trend': 'increasing'
            },
            'IT본부': {
                'total_employees': 85,
                'high_risk_count': 8,
                'average_score': 750,
                'risk_ratio': 9.4,
                'top_risks': ['업무 과부하', '경쟁사 스카웃'],
                'trend': 'stable'
            },
            '영업본부': {
                'total_employees': 150,
                'high_risk_count': 12,
                'average_score': 740,
                'risk_ratio': 8.0,
                'top_risks': ['성과 압박', '보상 불만족'],
                'trend': 'decreasing'
            }
        }