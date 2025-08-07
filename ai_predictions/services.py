"""
AI Predictions 서비스 - 이직 위험도 분석 엔진
"""
import os
import json
import logging
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Count, Avg, Q, F
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from compensation.models import EmployeeCompensation
from .models import TurnoverRisk, RiskFactor, RetentionPlan, TurnoverAlert

logger = logging.getLogger(__name__)

try:
    import openai
    openai.api_key = settings.OPENAI_API_KEY
except ImportError:
    logger.warning("OpenAI package not installed")
    openai = None

try:
    import anthropic
    anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY) if hasattr(settings, 'ANTHROPIC_API_KEY') else None
except ImportError:
    logger.warning("Anthropic package not installed")
    anthropic_client = None


class TurnoverRiskAnalyzer:
    """이직 위험도 분석 엔진"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1시간 캐시
        self.model_version = "v1.0"
        
        # 위험 요소 가중치 (기본값)
        self.risk_weights = {
            'PERFORMANCE': {
                'low_rating': 0.35,
                'declining_trend': 0.25,
                'missed_targets': 0.20,
                'peer_comparison': 0.20
            },
            'ENGAGEMENT': {
                'survey_scores': 0.30,
                'absence_rate': 0.25,
                'participation': 0.25,
                'feedback_sentiment': 0.20
            },
            'COMPENSATION': {
                'market_gap': 0.40,
                'pay_equity': 0.30,
                'bonus_history': 0.30
            },
            'WORKLOAD': {
                'overtime_hours': 0.35,
                'project_load': 0.30,
                'deadline_pressure': 0.35
            },
            'CAREER': {
                'promotion_history': 0.40,
                'skill_development': 0.30,
                'growth_opportunities': 0.30
            },
            'RELATIONSHIP': {
                'manager_relationship': 0.40,
                'peer_relationships': 0.30,
                'team_dynamics': 0.30
            }
        }
    
    def analyze_employee_risk(self, employee: Employee) -> Dict[str, Any]:
        """개별 직원의 이직 위험도 분석"""
        try:
            # 캐시 확인
            cache_key = f"turnover_risk_{employee.id}_{date.today()}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # 기본 데이터 수집
            employee_data = self._collect_employee_data(employee)
            
            # 위험 요소 계산
            risk_factors = self._calculate_risk_factors(employee, employee_data)
            
            # 종합 위험도 점수 계산
            risk_score = self._calculate_overall_risk_score(risk_factors)
            
            # 위험도 레벨 결정
            risk_level = self._determine_risk_level(risk_score)
            
            # AI 분석 추가
            ai_analysis = self._get_ai_analysis(employee, employee_data, risk_factors)
            
            # 예상 퇴사일 계산
            predicted_departure = self._predict_departure_date(employee, risk_score)
            
            # 결과 구성
            result = {
                'employee_id': employee.id,
                'employee_name': employee.name,
                'risk_score': risk_score,
                'risk_level': risk_level,
                'confidence_level': ai_analysis.get('confidence', 0.7),
                'primary_risk_factors': risk_factors.get('primary', []),
                'secondary_risk_factors': risk_factors.get('secondary', []),
                'protective_factors': risk_factors.get('protective', []),
                'predicted_departure_date': predicted_departure,
                'ai_analysis': ai_analysis,
                'recommendations': self._generate_recommendations(employee, risk_factors, ai_analysis),
                'analysis_date': timezone.now(),
                'model_version': self.model_version
            }
            
            # 캐시 저장
            cache.set(cache_key, result, self.cache_timeout)
            
            return result
            
        except Exception as e:
            logger.error(f"이직 위험도 분석 오류 (직원 {employee.id}): {e}")
            return self._get_fallback_analysis(employee)
    
    def batch_analyze_employees(self, employees: List[Employee] = None) -> List[Dict[str, Any]]:
        """여러 직원의 위험도 일괄 분석"""
        if employees is None:
            employees = Employee.objects.filter(employment_status='재직')
        
        results = []
        for employee in employees:
            try:
                analysis = self.analyze_employee_risk(employee)
                results.append(analysis)
            except Exception as e:
                logger.error(f"일괄 분석 오류 (직원 {employee.id}): {e}")
                continue
        
        # 위험도 순으로 정렬
        results.sort(key=lambda x: x['risk_score'], reverse=True)
        return results
    
    def get_high_risk_employees(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """고위험 직원 목록 조회"""
        cache_key = f"high_risk_employees_{threshold}_{date.today()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # 활성 상태의 고위험 직원 조회
        high_risk_records = TurnoverRisk.objects.filter(
            risk_score__gte=threshold,
            status='ACTIVE',
            prediction_date__date=date.today()
        ).select_related('employee')
        
        results = []
        for record in high_risk_records:
            results.append({
                'employee_id': record.employee.id,
                'employee_name': record.employee.name,
                'department': record.employee.department,
                'position': record.employee.position,
                'risk_score': record.risk_score,
                'risk_level': record.risk_level,
                'primary_factors': record.primary_risk_factors,
                'predicted_departure': record.predicted_departure_date,
                'last_analysis': record.prediction_date
            })
        
        # 위험도 순 정렬
        results.sort(key=lambda x: x['risk_score'], reverse=True)
        
        cache.set(cache_key, results, 1800)  # 30분 캐시
        return results
    
    def _collect_employee_data(self, employee: Employee) -> Dict[str, Any]:
        """직원 관련 데이터 수집"""
        data = {
            'basic_info': {
                'tenure_months': self._calculate_tenure_months(employee),
                'department': employee.department,
                'position': employee.position,
                'age': getattr(employee, 'age', None),
                'employment_type': employee.employment_type
            }
        }
        
        # 성과 평가 데이터
        try:
            recent_evaluations = ComprehensiveEvaluation.objects.filter(
                employee=employee
            ).order_by('-created_at')[:3]
            
            data['performance'] = {
                'recent_ratings': [eval.final_rating_numeric for eval in recent_evaluations if eval.final_rating_numeric],
                'avg_rating': recent_evaluations.aggregate(avg=Avg('final_rating_numeric'))['avg'] or 0,
                'evaluation_count': recent_evaluations.count(),
                'trend': self._calculate_performance_trend(recent_evaluations)
            }
        except Exception:
            data['performance'] = {'recent_ratings': [], 'avg_rating': 0, 'evaluation_count': 0, 'trend': 'stable'}
        
        # 보상 데이터
        try:
            compensation = EmployeeCompensation.objects.filter(employee=employee).first()
            if compensation:
                data['compensation'] = {
                    'total_compensation': float(compensation.total_compensation),
                    'base_salary': float(compensation.base_salary),
                    'bonus_amount': float(getattr(compensation, 'bonus_amount', 0)),
                    'last_increase_date': getattr(compensation, 'last_increase_date', None)
                }
            else:
                data['compensation'] = {'total_compensation': 0}
        except Exception:
            data['compensation'] = {'total_compensation': 0}
        
        return data
    
    def _calculate_risk_factors(self, employee: Employee, data: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """위험 요소 계산"""
        risk_factors = {'primary': [], 'secondary': [], 'protective': []}
        
        # 성과 관련 위험 요소
        perf_data = data.get('performance', {})
        avg_rating = perf_data.get('avg_rating', 0)
        
        if avg_rating > 0 and avg_rating < 2.5:
            risk_factors['primary'].append({
                'type': 'PERFORMANCE',
                'factor': '낮은 성과 평가',
                'score': 0.8,
                'description': f'평균 평가점수 {avg_rating:.1f}점으로 기준 미달'
            })
        elif avg_rating < 3.0:
            risk_factors['secondary'].append({
                'type': 'PERFORMANCE', 
                'factor': '보통 이하 성과',
                'score': 0.5,
                'description': f'평균 평가점수 {avg_rating:.1f}점으로 개선 필요'
            })
        
        # 재직 기간 관련
        tenure_months = data.get('basic_info', {}).get('tenure_months', 0)
        if tenure_months >= 24 and tenure_months <= 60:  # 2-5년차 고위험
            risk_factors['secondary'].append({
                'type': 'CAREER',
                'factor': '이직 활발 연차',
                'score': 0.6,
                'description': f'재직 {tenure_months}개월, 이직 활발한 시기'
            })
        elif tenure_months >= 120:  # 10년 이상 안정
            risk_factors['protective'].append({
                'type': 'CAREER',
                'factor': '장기 근속',
                'score': 0.7,
                'description': f'재직 {tenure_months}개월, 안정적 근속'
            })
        
        # 보상 관련
        comp_data = data.get('compensation', {})
        total_comp = comp_data.get('total_compensation', 0)
        
        if total_comp > 0:
            # 간단한 시장 비교 (실제로는 외부 데이터 필요)
            market_rate = self._estimate_market_rate(employee.position, employee.department)
            if market_rate and total_comp < market_rate * 0.85:  # 시장 대비 15% 이상 낮음
                risk_factors['primary'].append({
                    'type': 'COMPENSATION',
                    'factor': '시장 대비 낮은 급여',
                    'score': 0.9,
                    'description': f'시장 대비 {((market_rate - total_comp) / market_rate * 100):.1f}% 낮은 수준'
                })
            elif market_rate and total_comp > market_rate * 1.1:  # 시장 대비 10% 이상 높음
                risk_factors['protective'].append({
                    'type': 'COMPENSATION',
                    'factor': '경쟁력 있는 급여',
                    'score': 0.8,
                    'description': '시장 대비 경쟁력 있는 급여 수준'
                })
        
        return risk_factors
    
    def _calculate_overall_risk_score(self, risk_factors: Dict[str, List[Dict]]) -> float:
        """종합 위험도 점수 계산"""
        primary_score = sum(factor['score'] for factor in risk_factors.get('primary', [])) * 0.7
        secondary_score = sum(factor['score'] for factor in risk_factors.get('secondary', [])) * 0.3
        protective_score = sum(factor['score'] for factor in risk_factors.get('protective', [])) * 0.5
        
        # 기본 위험도 (0.2)에서 시작
        base_score = 0.2
        risk_score = base_score + primary_score + secondary_score - protective_score
        
        # 0.0 ~ 1.0 범위로 제한
        return max(0.0, min(1.0, risk_score))
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """위험도 점수를 기반으로 레벨 결정"""
        if risk_score >= 0.8:
            return 'CRITICAL'
        elif risk_score >= 0.6:
            return 'HIGH'
        elif risk_score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_ai_analysis(self, employee: Employee, data: Dict[str, Any], risk_factors: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """AI를 활용한 고도화 분석"""
        if not openai and not anthropic_client:
            return self._get_fallback_ai_analysis(employee, data, risk_factors)
        
        try:
            # AI 분석 프롬프트 생성
            prompt = self._generate_ai_prompt(employee, data, risk_factors)
            
            if openai and hasattr(settings, 'OPENAI_API_KEY'):
                return self._get_openai_analysis(prompt)
            elif anthropic_client:
                return self._get_anthropic_analysis(prompt)
            else:
                return self._get_fallback_ai_analysis(employee, data, risk_factors)
                
        except Exception as e:
            logger.error(f"AI 분석 오류: {e}")
            return self._get_fallback_ai_analysis(employee, data, risk_factors)
    
    def _generate_ai_prompt(self, employee: Employee, data: Dict[str, Any], risk_factors: Dict[str, List[Dict]]) -> str:
        """AI 분석용 프롬프트 생성"""
        return f"""
다음 직원의 이직 위험도를 분석하고 전문적인 인사이트를 제공하세요.

직원 정보:
- 이름: {employee.name}
- 부서: {employee.department}
- 직책: {employee.position} 
- 재직기간: {data.get('basic_info', {}).get('tenure_months', 0)}개월

성과 데이터:
- 평균 평가점수: {data.get('performance', {}).get('avg_rating', 0):.1f}점
- 평가 트렌드: {data.get('performance', {}).get('trend', 'stable')}

위험 요소:
- 주요 위험: {len(risk_factors.get('primary', []))}개
- 부차 위험: {len(risk_factors.get('secondary', []))}개  
- 보호 요소: {len(risk_factors.get('protective', []))}개

JSON 형식으로 응답해주세요:
{{
    "confidence": 0.0-1.0,
    "key_insights": ["인사이트1", "인사이트2"],
    "risk_factors_analysis": "위험 요소 종합 분석",
    "retention_probability": 0.0-1.0,
    "recommended_interventions": ["개입방안1", "개입방안2"],
    "timeline_prediction": "예상 시나리오"
}}

한국 기업 문화와 HR 관행을 고려하여 분석해주세요.
        """.strip()
    
    def _get_openai_analysis(self, prompt: str) -> Dict[str, Any]:
        """OpenAI를 통한 분석"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 HR 전문가이자 이직 위험도 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # JSON 추출 시도
            try:
                start = analysis_text.find('{')
                end = analysis_text.rfind('}') + 1
                if start != -1 and end != 0:
                    analysis_json = json.loads(analysis_text[start:end])
                    return analysis_json
            except:
                pass
                
            # JSON 파싱 실패 시 기본 구조 반환
            return {
                'confidence': 0.7,
                'key_insights': ['AI 분석 결과 처리 중'],
                'risk_factors_analysis': analysis_text[:200],
                'retention_probability': 0.6,
                'recommended_interventions': ['상세 분석 필요'],
                'timeline_prediction': '추가 분석 진행 중'
            }
            
        except Exception as e:
            logger.error(f"OpenAI 분석 오류: {e}")
            raise
    
    def _get_fallback_ai_analysis(self, employee: Employee, data: Dict[str, Any], risk_factors: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """AI 서비스 사용 불가 시 기본 분석"""
        primary_count = len(risk_factors.get('primary', []))
        secondary_count = len(risk_factors.get('secondary', []))
        protective_count = len(risk_factors.get('protective', []))
        
        confidence = 0.6 if primary_count + secondary_count > 0 else 0.4
        retention_prob = max(0.3, 1.0 - (primary_count * 0.3 + secondary_count * 0.1))
        
        insights = []
        if primary_count > 0:
            insights.append(f"{primary_count}개의 주요 위험 요소가 감지됨")
        if protective_count > 0:
            insights.append(f"{protective_count}개의 보호 요소가 있어 안정성 확보")
        
        interventions = []
        for factor in risk_factors.get('primary', [])[:2]:
            if factor['type'] == 'PERFORMANCE':
                interventions.append('성과 개선 지원 프로그램')
            elif factor['type'] == 'COMPENSATION':
                interventions.append('보상 패키지 재검토')
            elif factor['type'] == 'CAREER':
                interventions.append('경력 개발 기회 제공')
        
        return {
            'confidence': confidence,
            'key_insights': insights or ['표준 위험도 분석 완료'],
            'risk_factors_analysis': f'주요 위험 {primary_count}개, 부차 위험 {secondary_count}개 확인',
            'retention_probability': retention_prob,
            'recommended_interventions': interventions or ['지속적인 모니터링'],
            'timeline_prediction': '3-6개월 내 재검토 권장'
        }
    
    def _predict_departure_date(self, employee: Employee, risk_score: float) -> Optional[date]:
        """예상 퇴사일 예측"""
        if risk_score < 0.5:
            return None  # 낮은 위험도는 예측하지 않음
        
        # 위험도 기반 예상 기간 계산
        base_days = 90  # 3개월 기본
        
        if risk_score >= 0.9:
            days_range = (14, 60)   # 2주-2개월
        elif risk_score >= 0.7:
            days_range = (30, 120)  # 1-4개월
        elif risk_score >= 0.5:
            days_range = (60, 180)  # 2-6개월
        else:
            days_range = (90, 365)  # 3개월-1년
        
        # 위험도에 따른 예상 일수
        predicted_days = int(days_range[0] + (days_range[1] - days_range[0]) * (1 - risk_score))
        
        return date.today() + timedelta(days=predicted_days)
    
    def _generate_recommendations(self, employee: Employee, risk_factors: Dict[str, List[Dict]], ai_analysis: Dict[str, Any]) -> List[str]:
        """맞춤형 추천사항 생성"""
        recommendations = []
        
        # AI 추천사항 우선 사용
        ai_recommendations = ai_analysis.get('recommended_interventions', [])
        if ai_recommendations:
            recommendations.extend(ai_recommendations)
        
        # 위험 요소별 기본 추천사항
        for factor in risk_factors.get('primary', []):
            factor_type = factor.get('type')
            if factor_type == 'PERFORMANCE':
                recommendations.append('개별 성과 향상 계획 수립')
            elif factor_type == 'COMPENSATION':
                recommendations.append('급여 및 복리후생 재검토')
            elif factor_type == 'CAREER':
                recommendations.append('경력 개발 로드맵 제공')
            elif factor_type == 'WORKLOAD':
                recommendations.append('업무량 조정 및 분산')
            elif factor_type == 'RELATIONSHIP':
                recommendations.append('관계 개선을 위한 1:1 미팅')
        
        # 기본 추천사항
        if not recommendations:
            recommendations = [
                '정기적인 1:1 면담 실시',
                '직무 만족도 조사 참여',
                '전문성 향상 교육 제공'
            ]
        
        return list(set(recommendations))  # 중복 제거
    
    def _calculate_tenure_months(self, employee: Employee) -> int:
        """재직 기간 계산 (월)"""
        if not employee.hire_date:
            return 0
        
        today = date.today()
        months = (today.year - employee.hire_date.year) * 12 + (today.month - employee.hire_date.month)
        return max(0, months)
    
    def _calculate_performance_trend(self, evaluations) -> str:
        """성과 트렌드 계산"""
        if len(evaluations) < 2:
            return 'stable'
        
        ratings = [eval.final_rating_numeric for eval in evaluations if eval.final_rating_numeric]
        if len(ratings) < 2:
            return 'stable'
        
        recent_avg = sum(ratings[:2]) / len(ratings[:2])
        older_avg = sum(ratings[2:]) / len(ratings[2:]) if len(ratings) > 2 else recent_avg
        
        diff = recent_avg - older_avg
        if diff > 0.3:
            return 'improving'
        elif diff < -0.3:
            return 'declining'
        else:
            return 'stable'
    
    def _estimate_market_rate(self, position: str, department: str) -> Optional[float]:
        """시장 급여 추정 (간단한 추정)"""
        # 실제로는 외부 급여 데이터베이스 연동 필요
        base_rates = {
            '개발팀': {'주임': 4000, '대리': 5000, '과장': 6500, '차장': 8000, '부장': 10000},
            '마케팅팀': {'주임': 3500, '대리': 4500, '과장': 6000, '차장': 7500, '부장': 9500},
            '영업팀': {'주임': 3800, '대리': 4800, '과장': 6200, '차장': 7800, '부장': 9800},
            '기획팀': {'주임': 3700, '대리': 4700, '과장': 6100, '차장': 7700, '부장': 9700}
        }
        
        return base_rates.get(department, {}).get(position.split()[-1], None)
    
    def _get_fallback_analysis(self, employee: Employee) -> Dict[str, Any]:
        """분석 실패 시 기본 결과"""
        return {
            'employee_id': employee.id,
            'employee_name': employee.name,
            'risk_score': 0.3,
            'risk_level': 'MEDIUM',
            'confidence_level': 0.5,
            'primary_risk_factors': [],
            'secondary_risk_factors': [{'type': 'GENERAL', 'factor': '정기 모니터링 필요', 'score': 0.3}],
            'protective_factors': [],
            'predicted_departure_date': None,
            'ai_analysis': {
                'confidence': 0.5,
                'key_insights': ['기본 분석 완료'],
                'risk_factors_analysis': '추가 데이터 필요',
                'retention_probability': 0.7,
                'recommended_interventions': ['정기적인 면담'],
                'timeline_prediction': '지속 모니터링'
            },
            'recommendations': ['정기적인 상담', '만족도 조사'],
            'analysis_date': timezone.now(),
            'model_version': self.model_version
        }


class TurnoverAlertSystem:
    """이직 위험도 알림 시스템"""
    
    def __init__(self):
        self.alert_thresholds = {
            'CRITICAL': 0.8,
            'HIGH': 0.6,
            'MEDIUM': 0.4
        }
    
    def check_and_create_alerts(self, employee: Employee, risk_analysis: Dict[str, Any]) -> List[TurnoverAlert]:
        """위험도 분석 결과를 바탕으로 알림 생성"""
        alerts = []
        risk_score = risk_analysis.get('risk_score', 0)
        
        # 임계 수준 알림
        if risk_score >= self.alert_thresholds['CRITICAL']:
            alert = self._create_critical_alert(employee, risk_analysis)
            if alert:
                alerts.append(alert)
        
        # 위험도 증가 알림 (이전 분석과 비교)
        previous_risk = self._get_previous_risk_score(employee)
        if previous_risk and risk_score > previous_risk + 0.2:
            alert = self._create_risk_increase_alert(employee, risk_analysis, previous_risk)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _create_critical_alert(self, employee: Employee, risk_analysis: Dict[str, Any]) -> Optional[TurnoverAlert]:
        """임계 위험도 알림 생성"""
        try:
            # 기존 임계 알림 확인 (중복 방지)
            existing_alert = TurnoverAlert.objects.filter(
                turnover_risk__employee=employee,
                alert_type='CRITICAL_LEVEL',
                created_at__date=date.today()
            ).first()
            
            if existing_alert:
                return None  # 오늘 이미 생성된 알림이 있으면 스킵
            
            alert = TurnoverAlert.objects.create(
                turnover_risk=TurnoverRisk.objects.filter(employee=employee).first(),
                alert_type='CRITICAL_LEVEL',
                severity='EMERGENCY',
                title=f"[긴급] {employee.name} 이직 위험도 임계 수준",
                message=f"{employee.name}님의 이직 위험도가 {risk_analysis.get('risk_score', 0):.1%}로 매우 높습니다. 즉시 개입이 필요합니다.",
                details={
                    'risk_score': risk_analysis.get('risk_score'),
                    'primary_factors': risk_analysis.get('primary_risk_factors', []),
                    'ai_insights': risk_analysis.get('ai_analysis', {}).get('key_insights', [])
                }
            )
            
            # 수신자 설정 (관리자, HR 등)
            recipients = self._get_alert_recipients(employee, 'CRITICAL')
            alert.recipients.set(recipients)
            
            return alert
            
        except Exception as e:
            logger.error(f"임계 알림 생성 오류: {e}")
            return None
    
    def _create_risk_increase_alert(self, employee: Employee, risk_analysis: Dict[str, Any], previous_score: float) -> Optional[TurnoverAlert]:
        """위험도 증가 알림 생성"""
        try:
            current_score = risk_analysis.get('risk_score', 0)
            increase_pct = ((current_score - previous_score) / previous_score) * 100
            
            alert = TurnoverAlert.objects.create(
                turnover_risk=TurnoverRisk.objects.filter(employee=employee).first(),
                alert_type='RISK_INCREASE',
                severity='WARNING',
                title=f"{employee.name} 이직 위험도 증가",
                message=f"{employee.name}님의 이직 위험도가 {previous_score:.1%}에서 {current_score:.1%}로 {increase_pct:.1f}% 증가했습니다.",
                details={
                    'previous_score': previous_score,
                    'current_score': current_score,
                    'increase_percentage': increase_pct,
                    'trend_factors': risk_analysis.get('primary_risk_factors', [])
                }
            )
            
            recipients = self._get_alert_recipients(employee, 'WARNING')
            alert.recipients.set(recipients)
            
            return alert
            
        except Exception as e:
            logger.error(f"위험도 증가 알림 생성 오류: {e}")
            return None
    
    def _get_previous_risk_score(self, employee: Employee) -> Optional[float]:
        """이전 위험도 점수 조회"""
        previous_risk = TurnoverRisk.objects.filter(
            employee=employee,
            prediction_date__date__lt=date.today()
        ).order_by('-prediction_date').first()
        
        return previous_risk.risk_score if previous_risk else None
    
    def _get_alert_recipients(self, employee: Employee, severity: str) -> List:
        """알림 수신자 결정"""
        from django.contrib.auth.models import User
        
        recipients = []
        
        # 직속 상관
        if hasattr(employee, 'manager') and employee.manager:
            if hasattr(employee.manager, 'user') and employee.manager.user:
                recipients.append(employee.manager.user)
        
        # HR 담당자 (모든 알림)
        hr_users = User.objects.filter(
            groups__name__in=['HR', '인사팀']
        )
        recipients.extend(hr_users)
        
        # 임계 수준일 경우 경영진 추가
        if severity in ['CRITICAL', 'EMERGENCY']:
            executive_users = User.objects.filter(
                groups__name__in=['경영진', 'Executive']
            )
            recipients.extend(executive_users)
        
        return list(set(recipients))  # 중복 제거