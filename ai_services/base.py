"""
AI 서비스 기본 클래스 및 공통 유틸리티
"""
import openai
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AIServiceBase:
    """AI 서비스 기본 클래스"""
    
    def __init__(self):
        self.api_key = self.get_api_key()
        if self.api_key:
            openai.api_key = self.api_key
        self.model = settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else 'gpt-3.5-turbo'
        self.cache_timeout = 3600  # 1시간
        
    def get_api_key(self) -> Optional[str]:
        """API 키 가져오기"""
        # 1. Django 설정에서
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            return settings.OPENAI_API_KEY
        # 2. 환경변수에서
        return os.getenv('OPENAI_API_KEY')
    
    def call_openai(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """OpenAI API 호출"""
        if not self.api_key:
            logger.warning("OpenAI API key not found")
            return None
            
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 500),
                top_p=kwargs.get('top_p', 1),
                frequency_penalty=kwargs.get('frequency_penalty', 0),
                presence_penalty=kwargs.get('presence_penalty', 0),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def get_cached_or_compute(self, cache_key: str, compute_func, *args, **kwargs):
        """캐시에서 가져오거나 계산"""
        result = cache.get(cache_key)
        if result is None:
            result = compute_func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, self.cache_timeout)
        return result


class AIAnalyzer:
    """AI 기반 데이터 분석기"""
    
    def __init__(self):
        self.service = AIServiceBase()
        
    def analyze_trends(self, data: List[Dict], metric: str) -> Dict:
        """트렌드 분석"""
        if not data:
            return self._get_default_trend()
            
        values = [item.get(metric, 0) for item in data]
        dates = [item.get('date') for item in data]
        
        # 기본 통계
        mean_value = np.mean(values)
        std_value = np.std(values)
        
        # 트렌드 계산 (선형 회귀)
        if len(values) >= 2:
            x = np.arange(len(values))
            coefficients = np.polyfit(x, values, 1)
            trend_direction = 'increasing' if coefficients[0] > 0 else 'decreasing'
            trend_strength = abs(coefficients[0]) / (mean_value + 0.001)
        else:
            trend_direction = 'stable'
            trend_strength = 0
        
        # 예측 (간단한 이동평균)
        if len(values) >= 3:
            recent_values = values[-3:]
            predicted_next = np.mean(recent_values) + coefficients[0] if len(values) >= 2 else np.mean(recent_values)
        else:
            predicted_next = mean_value
        
        return {
            'current_value': values[-1] if values else 0,
            'mean': mean_value,
            'std': std_value,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'predicted_next': predicted_next,
            'confidence': self._calculate_confidence(values),
            'insights': self._generate_insights(values, trend_direction, trend_strength)
        }
    
    def _calculate_confidence(self, values: List[float]) -> float:
        """신뢰도 계산"""
        if len(values) < 3:
            return 0.3
        if len(values) < 10:
            return 0.6
        return min(0.9, 0.6 + len(values) * 0.01)
    
    def _generate_insights(self, values: List[float], direction: str, strength: float) -> List[str]:
        """인사이트 생성"""
        insights = []
        
        if direction == 'increasing' and strength > 0.1:
            insights.append("지속적인 상승 추세를 보이고 있습니다.")
        elif direction == 'decreasing' and strength > 0.1:
            insights.append("하락 추세가 관찰되며 주의가 필요합니다.")
        else:
            insights.append("안정적인 수준을 유지하고 있습니다.")
            
        # 변동성 체크
        if len(values) >= 3:
            volatility = np.std(values) / (np.mean(values) + 0.001)
            if volatility > 0.3:
                insights.append("높은 변동성이 관찰됩니다.")
                
        return insights
    
    def _get_default_trend(self) -> Dict:
        """기본 트렌드 데이터"""
        return {
            'current_value': 0,
            'mean': 0,
            'std': 0,
            'trend_direction': 'stable',
            'trend_strength': 0,
            'predicted_next': 0,
            'confidence': 0,
            'insights': ["데이터가 충분하지 않습니다."]
        }
    
    def analyze_anomalies(self, data: List[float], threshold: float = 2.0) -> List[int]:
        """이상치 탐지"""
        if len(data) < 3:
            return []
            
        mean = np.mean(data)
        std = np.std(data)
        
        anomalies = []
        for i, value in enumerate(data):
            z_score = abs((value - mean) / (std + 0.001))
            if z_score > threshold:
                anomalies.append(i)
                
        return anomalies
    
    def cluster_analysis(self, data: List[Dict], features: List[str], n_clusters: int = 3) -> Dict:
        """클러스터 분석"""
        if not data or len(data) < n_clusters:
            return {'clusters': [], 'insights': ["데이터가 충분하지 않습니다."]}
            
        # 특징 추출
        X = []
        for item in data:
            row = [item.get(feature, 0) for feature in features]
            X.append(row)
        
        X = np.array(X)
        
        # 정규화
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 간단한 K-means 구현 (실제로는 sklearn 사용 권장)
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 클러스터별 통계
        cluster_stats = []
        for i in range(n_clusters):
            cluster_indices = np.where(clusters == i)[0]
            cluster_data = [data[idx] for idx in cluster_indices]
            
            stats = {
                'cluster_id': i,
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(data) * 100,
                'characteristics': self._get_cluster_characteristics(cluster_data, features)
            }
            cluster_stats.append(stats)
        
        return {
            'clusters': cluster_stats,
            'insights': self._generate_cluster_insights(cluster_stats)
        }
    
    def _get_cluster_characteristics(self, cluster_data: List[Dict], features: List[str]) -> Dict:
        """클러스터 특성 추출"""
        characteristics = {}
        for feature in features:
            values = [item.get(feature, 0) for item in cluster_data]
            characteristics[feature] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values)
            }
        return characteristics
    
    def _generate_cluster_insights(self, cluster_stats: List[Dict]) -> List[str]:
        """클러스터 인사이트 생성"""
        insights = []
        
        # 가장 큰 클러스터
        largest = max(cluster_stats, key=lambda x: x['size'])
        insights.append(f"가장 큰 그룹은 전체의 {largest['percentage']:.1f}%를 차지합니다.")
        
        # 클러스터 수
        insights.append(f"총 {len(cluster_stats)}개의 그룹으로 분류됩니다.")
        
        return insights


class PerformancePredictor:
    """성과 예측 모델"""
    
    def __init__(self):
        self.analyzer = AIAnalyzer()
        self.service = AIServiceBase()
        
    def predict_performance(self, employee_data: Dict, historical_data: List[Dict]) -> Dict:
        """직원 성과 예측"""
        
        # 기본 예측 로직
        base_score = self._calculate_base_score(employee_data)
        
        # 과거 데이터 기반 트렌드
        if historical_data:
            trend = self.analyzer.analyze_trends(historical_data, 'performance_score')
            predicted_score = trend['predicted_next']
        else:
            predicted_score = base_score
            
        # 위험 요소 분석
        risk_factors = self._analyze_risk_factors(employee_data, historical_data)
        
        # 기회 요소 분석
        opportunities = self._analyze_opportunities(employee_data)
        
        # AI 인사이트 생성
        insights = self._generate_performance_insights(
            predicted_score, risk_factors, opportunities
        )
        
        return {
            'predicted_score': min(100, max(0, predicted_score)),
            'confidence': self._calculate_prediction_confidence(historical_data),
            'risk_factors': risk_factors,
            'opportunities': opportunities,
            'insights': insights,
            'recommendations': self._generate_recommendations(risk_factors, opportunities)
        }
    
    def _calculate_base_score(self, employee_data: Dict) -> float:
        """기본 점수 계산"""
        score = 70  # 기본값
        
        # 경력 연수
        years = employee_data.get('years_of_service', 0)
        score += min(10, years * 2)
        
        # 교육 수준
        education = employee_data.get('education_level', 0)
        score += education * 2
        
        # 스킬 수
        skills = employee_data.get('skill_count', 0)
        score += min(10, skills)
        
        return min(100, score)
    
    def _analyze_risk_factors(self, employee_data: Dict, historical_data: List[Dict]) -> List[Dict]:
        """위험 요소 분석"""
        risks = []
        
        # 근태 문제
        absence_rate = employee_data.get('absence_rate', 0)
        if absence_rate > 0.1:
            risks.append({
                'factor': '높은 결근율',
                'impact': 'high',
                'score_impact': -10
            })
            
        # 성과 하락 추세
        if historical_data and len(historical_data) >= 3:
            recent_scores = [d.get('performance_score', 0) for d in historical_data[-3:]]
            if all(recent_scores[i] > recent_scores[i+1] for i in range(len(recent_scores)-1)):
                risks.append({
                    'factor': '지속적인 성과 하락',
                    'impact': 'medium',
                    'score_impact': -5
                })
                
        return risks
    
    def _analyze_opportunities(self, employee_data: Dict) -> List[Dict]:
        """기회 요소 분석"""
        opportunities = []
        
        # 교육 참여
        training_hours = employee_data.get('training_hours', 0)
        if training_hours > 40:
            opportunities.append({
                'factor': '적극적인 교육 참여',
                'impact': 'high',
                'score_impact': 10
            })
            
        # 프로젝트 리더십
        if employee_data.get('is_project_leader', False):
            opportunities.append({
                'factor': '프로젝트 리더십 경험',
                'impact': 'medium',
                'score_impact': 5
            })
            
        return opportunities
    
    def _calculate_prediction_confidence(self, historical_data: List[Dict]) -> float:
        """예측 신뢰도 계산"""
        if not historical_data:
            return 0.3
        
        data_points = len(historical_data)
        if data_points < 3:
            return 0.4
        elif data_points < 6:
            return 0.6
        elif data_points < 12:
            return 0.75
        else:
            return min(0.9, 0.75 + data_points * 0.01)
    
    def _generate_performance_insights(self, score: float, risks: List[Dict], opportunities: List[Dict]) -> List[str]:
        """성과 인사이트 생성"""
        insights = []
        
        if score >= 80:
            insights.append("우수한 성과가 예상됩니다.")
        elif score >= 60:
            insights.append("평균 이상의 성과가 예상됩니다.")
        else:
            insights.append("성과 개선이 필요할 것으로 보입니다.")
            
        if risks:
            insights.append(f"{len(risks)}개의 위험 요소가 발견되었습니다.")
            
        if opportunities:
            insights.append(f"{len(opportunities)}개의 성장 기회가 있습니다.")
            
        return insights
    
    def _generate_recommendations(self, risks: List[Dict], opportunities: List[Dict]) -> List[str]:
        """추천 사항 생성"""
        recommendations = []
        
        for risk in risks[:3]:  # 상위 3개
            if risk['factor'] == '높은 결근율':
                recommendations.append("근태 관리 프로그램 참여를 권장합니다.")
            elif risk['factor'] == '지속적인 성과 하락':
                recommendations.append("1:1 면담을 통한 원인 파악이 필요합니다.")
                
        for opp in opportunities[:3]:  # 상위 3개
            if opp['factor'] == '적극적인 교육 참여':
                recommendations.append("심화 교육 프로그램 제공을 고려하세요.")
            elif opp['factor'] == '프로젝트 리더십 경험':
                recommendations.append("더 큰 프로젝트 책임을 맡길 수 있습니다.")
                
        return recommendations


class TalentRiskAnalyzer:
    """인재 이탈 위험 분석기"""
    
    def __init__(self):
        self.analyzer = AIAnalyzer()
        
    def analyze_turnover_risk(self, employee_data: Dict) -> Dict:
        """이탈 위험도 분석"""
        
        risk_score = 0
        risk_factors = []
        
        # 근속 연수 (3년 미만 위험)
        tenure = employee_data.get('years_of_service', 0)
        if tenure < 3:
            risk_score += 20
            risk_factors.append({
                'factor': '짧은 근속 기간',
                'weight': 20,
                'description': f'근속 {tenure}년'
            })
            
        # 최근 승진 여부
        last_promotion = employee_data.get('months_since_last_promotion', 0)
        if last_promotion > 24:
            risk_score += 15
            risk_factors.append({
                'factor': '장기간 승진 없음',
                'weight': 15,
                'description': f'{last_promotion}개월째 같은 직급'
            })
            
        # 급여 수준
        salary_percentile = employee_data.get('salary_percentile', 50)
        if salary_percentile < 30:
            risk_score += 25
            risk_factors.append({
                'factor': '낮은 급여 수준',
                'weight': 25,
                'description': f'하위 {salary_percentile}%'
            })
            
        # 성과 평가
        performance_trend = employee_data.get('performance_trend', 'stable')
        if performance_trend == 'declining':
            risk_score += 15
            risk_factors.append({
                'factor': '성과 하락 추세',
                'weight': 15,
                'description': '최근 3개월 하락세'
            })
            
        # 교육 참여도
        training_hours = employee_data.get('training_hours_last_year', 0)
        if training_hours < 20:
            risk_score += 10
            risk_factors.append({
                'factor': '낮은 교육 참여',
                'weight': 10,
                'description': f'연간 {training_hours}시간'
            })
            
        # 위험 수준 판단
        if risk_score >= 70:
            risk_level = 'critical'
            risk_label = '매우 높음'
        elif risk_score >= 50:
            risk_level = 'high'
            risk_label = '높음'
        elif risk_score >= 30:
            risk_level = 'medium'
            risk_label = '보통'
        else:
            risk_level = 'low'
            risk_label = '낮음'
            
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_label': risk_label,
            'risk_factors': sorted(risk_factors, key=lambda x: x['weight'], reverse=True),
            'retention_strategies': self._generate_retention_strategies(risk_factors),
            'estimated_loss_impact': self._calculate_loss_impact(employee_data)
        }
    
    def _generate_retention_strategies(self, risk_factors: List[Dict]) -> List[Dict]:
        """리텐션 전략 생성"""
        strategies = []
        
        for factor in risk_factors:
            if factor['factor'] == '낮은 급여 수준':
                strategies.append({
                    'strategy': '급여 조정 검토',
                    'priority': 'high',
                    'timeline': '1개월 이내',
                    'expected_impact': '높음'
                })
            elif factor['factor'] == '장기간 승진 없음':
                strategies.append({
                    'strategy': '경력 개발 계획 수립',
                    'priority': 'high',
                    'timeline': '2주 이내',
                    'expected_impact': '중간'
                })
            elif factor['factor'] == '성과 하락 추세':
                strategies.append({
                    'strategy': '1:1 코칭 프로그램',
                    'priority': 'medium',
                    'timeline': '1주 이내',
                    'expected_impact': '중간'
                })
                
        return strategies
    
    def _calculate_loss_impact(self, employee_data: Dict) -> Dict:
        """이탈 시 영향도 계산"""
        
        # 기본 교체 비용 (연봉의 50-200%)
        salary = employee_data.get('annual_salary', 0)
        position_level = employee_data.get('position_level', 1)
        
        replacement_cost = salary * (0.5 + position_level * 0.3)
        
        # 지식 손실 비용
        expertise_level = employee_data.get('expertise_level', 1)
        knowledge_cost = salary * expertise_level * 0.2
        
        # 프로젝트 영향
        active_projects = employee_data.get('active_projects', 0)
        project_impact = active_projects * salary * 0.1
        
        total_impact = replacement_cost + knowledge_cost + project_impact
        
        return {
            'total_impact': total_impact,
            'replacement_cost': replacement_cost,
            'knowledge_cost': knowledge_cost,
            'project_impact': project_impact,
            'time_to_fill': 30 + position_level * 15,  # days
            'productivity_loss_months': 3 + expertise_level
        }