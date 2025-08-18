"""
AIRISS AI 분석 서비스
AI 기반 HR 데이터 분석 및 예측 서비스
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db.models import Avg, Count, Q, F, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from employees.models import Employee

User = get_user_model()

# Optional imports - 일부 모델이 없어도 서비스가 동작하도록 처리
try:
    from evaluations.models import EvaluationPeriod, PerformanceEvaluation
except ImportError:
    EvaluationPeriod = None
    PerformanceEvaluation = None

try:
    from compensation.models import EmployeeCompensation
except ImportError:
    EmployeeCompensation = None

from .models import (
    AIAnalysisType, AIAnalysisResult, AIInsight,
    HRChatbotConversation, AIModelConfig
)


class AIAnalysisService:
    """AI 기반 HR 분석 서비스"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        
    def analyze_turnover_risk(self, employee: Employee) -> Dict[str, Any]:
        """직원의 퇴사 위험도 분석"""
        risk_factors = {
            'tenure': self._calculate_tenure_risk(employee),
            'performance': self._calculate_performance_risk(employee),
            'compensation': self._calculate_compensation_risk(employee),
            'engagement': self._calculate_engagement_risk(employee),
            'growth': self._calculate_growth_risk(employee),
        }
        
        # 가중 평균으로 최종 위험도 계산
        weights = {
            'tenure': 0.15,
            'performance': 0.25,
            'compensation': 0.20,
            'engagement': 0.25,
            'growth': 0.15,
        }
        
        risk_score = sum(
            risk_factors[factor] * weights[factor] 
            for factor in risk_factors
        )
        
        # 추천사항 생성
        recommendations = self._generate_retention_recommendations(
            employee, risk_factors, risk_score
        )
        
        # 인사이트 생성
        insights = self._generate_turnover_insights(
            employee, risk_factors, risk_score
        )
        
        return {
            'score': round(risk_score, 2),
            'confidence': self._calculate_confidence(risk_factors),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'insights': insights,
            'risk_level': self._get_risk_level(risk_score),
        }
    
    def analyze_promotion_potential(self, employee: Employee) -> Dict[str, Any]:
        """직원의 승진 가능성 분석"""
        potential_factors = {
            'performance': self._evaluate_performance_history(employee),
            'skills': self._evaluate_skill_development(employee),
            'leadership': self._evaluate_leadership_potential(employee),
            'tenure': self._evaluate_tenure_readiness(employee),
            'impact': self._evaluate_business_impact(employee),
        }
        
        # 가중 평균으로 승진 가능성 점수 계산
        weights = {
            'performance': 0.30,
            'skills': 0.20,
            'leadership': 0.25,
            'tenure': 0.10,
            'impact': 0.15,
        }
        
        potential_score = sum(
            potential_factors[factor] * weights[factor]
            for factor in potential_factors
        )
        
        # 승진 준비도 평가
        readiness = self._assess_promotion_readiness(
            employee, potential_factors, potential_score
        )
        
        # 개발 필요 영역 식별
        development_areas = self._identify_development_areas(
            employee, potential_factors
        )
        
        return {
            'score': round(potential_score, 2),
            'confidence': self._calculate_confidence(potential_factors),
            'potential_factors': potential_factors,
            'readiness': readiness,
            'development_areas': development_areas,
            'timeline': self._estimate_promotion_timeline(potential_score),
        }
    
    def analyze_team_performance(self, department: str) -> Dict[str, Any]:
        """팀/부서 성과 예측 및 분석"""
        # 팀 구성원 분석
        team_members = Employee.objects.filter(department=department)
        
        team_metrics = {
            'size': team_members.count(),
            'avg_performance': self._calculate_team_avg_performance(team_members),
            'skill_diversity': self._calculate_skill_diversity(team_members),
            'experience_balance': self._calculate_experience_balance(team_members),
            'collaboration': self._calculate_collaboration_score(team_members),
        }
        
        # 팀 성과 예측
        predicted_performance = self._predict_team_performance(team_metrics)
        
        # 팀 강점 및 약점 분석
        strengths = self._identify_team_strengths(team_metrics)
        weaknesses = self._identify_team_weaknesses(team_metrics)
        
        # 팀 최적화 제안
        optimization_suggestions = self._generate_team_optimization(
            department, team_metrics, strengths, weaknesses
        )
        
        return {
            'score': round(predicted_performance, 2),
            'confidence': 0.85,
            'team_metrics': team_metrics,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'optimization_suggestions': optimization_suggestions,
            'risk_areas': self._identify_team_risks(team_metrics),
        }
    
    def recommend_talents(self, position: str, department: Optional[str] = None) -> List[Dict[str, Any]]:
        """특정 포지션에 적합한 인재 추천"""
        # 포지션 요구사항 분석
        requirements = self._analyze_position_requirements(position)
        
        # 후보자 검색
        candidates = Employee.objects.filter(
            employment_status='ACTIVE'
        )
        
        if department:
            # 내부 이동 가능한 직원만
            candidates = candidates.exclude(department=department)
        
        # 각 후보자 평가
        recommendations = []
        for candidate in candidates[:50]:  # 상위 50명만 평가
            fit_score = self._calculate_position_fit(candidate, requirements)
            if fit_score >= 70:
                recommendations.append({
                    'employee': candidate,
                    'fit_score': fit_score,
                    'strengths': self._identify_candidate_strengths(candidate, requirements),
                    'gaps': self._identify_candidate_gaps(candidate, requirements),
                    'development_plan': self._create_development_plan(candidate, requirements),
                })
        
        # 점수 기준 정렬
        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
        
        return recommendations[:10]  # 상위 10명 추천
    
    def optimize_compensation(self, department: Optional[str] = None) -> Dict[str, Any]:
        """급여 최적화 분석"""
        if department:
            employees = Employee.objects.filter(department=department)
        else:
            employees = Employee.objects.filter(employment_status='ACTIVE')
        
        # 현재 보상 분석
        compensation_analysis = self._analyze_current_compensation(employees)
        
        # 시장 비교 (시뮬레이션)
        market_comparison = self._compare_with_market(compensation_analysis)
        
        # 공정성 분석
        equity_analysis = self._analyze_compensation_equity(employees)
        
        # 최적화 제안
        optimization_recommendations = self._generate_compensation_optimization(
            compensation_analysis, market_comparison, equity_analysis
        )
        
        return {
            'current_analysis': compensation_analysis,
            'market_comparison': market_comparison,
            'equity_analysis': equity_analysis,
            'recommendations': optimization_recommendations,
            'budget_impact': self._calculate_budget_impact(optimization_recommendations),
        }
    
    # Private helper methods
    def _calculate_tenure_risk(self, employee: Employee) -> float:
        """근속 기간 기반 위험도"""
        tenure_years = (timezone.now().date() - employee.hire_date).days / 365
        
        if tenure_years < 1:
            return 70  # 1년 미만 높은 위험
        elif tenure_years < 2:
            return 50  # 1-2년 중간 위험
        elif tenure_years < 5:
            return 30  # 2-5년 낮은 위험
        else:
            return 20  # 5년 이상 매우 낮은 위험
    
    def _calculate_performance_risk(self, employee: Employee) -> float:
        """성과 기반 위험도"""
        # 최근 평가 조회
        recent_evaluations = PerformanceEvaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date')[:3]
        
        if not recent_evaluations:
            return 50  # 평가 없음 - 중간 위험
        
        avg_score = sum(e.overall_score for e in recent_evaluations) / len(recent_evaluations)
        
        if avg_score >= 90:
            return 10  # 우수 성과 - 낮은 위험
        elif avg_score >= 70:
            return 30  # 양호 성과 - 중간 위험
        else:
            return 60  # 저조한 성과 - 높은 위험
    
    def _calculate_compensation_risk(self, employee: Employee) -> float:
        """보상 기반 위험도"""
        try:
            comp = EmployeeCompensation.objects.get(employee=employee)
            # 동일 직급 평균과 비교 (시뮬레이션)
            position_avg = EmployeeCompensation.objects.filter(
                employee__position=employee.position
            ).aggregate(avg=Avg('base_salary'))['avg'] or comp.base_salary
            
            ratio = comp.base_salary / position_avg
            
            if ratio >= 1.1:
                return 10  # 평균 이상 - 낮은 위험
            elif ratio >= 0.9:
                return 30  # 평균 수준 - 중간 위험
            else:
                return 60  # 평균 이하 - 높은 위험
        except EmployeeCompensation.DoesNotExist:
            return 50  # 보상 정보 없음
    
    def _calculate_engagement_risk(self, employee: Employee) -> float:
        """참여도 기반 위험도 (시뮬레이션)"""
        # 실제로는 설문조사, 출근율, 프로젝트 참여도 등을 분석
        return random.randint(20, 60)
    
    def _calculate_growth_risk(self, employee: Employee) -> float:
        """성장 기회 기반 위험도"""
        # 최근 승진 이력 확인 (시뮬레이션)
        months_since_promotion = random.randint(6, 48)
        
        if months_since_promotion < 12:
            return 10  # 최근 승진 - 낮은 위험
        elif months_since_promotion < 24:
            return 30  # 1-2년 - 중간 위험
        else:
            return 50  # 2년 이상 - 높은 위험
    
    def _calculate_confidence(self, factors: Dict[str, float]) -> float:
        """분석 신뢰도 계산"""
        # 데이터 완성도에 따른 신뢰도 (시뮬레이션)
        return min(0.95, 0.7 + random.random() * 0.25)
    
    def _get_risk_level(self, score: float) -> str:
        """위험도 수준 결정"""
        if score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_retention_recommendations(self, employee: Employee, 
                                          risk_factors: Dict[str, float], 
                                          risk_score: float) -> List[str]:
        """유지 전략 추천"""
        recommendations = []
        
        if risk_factors['compensation'] > 50:
            recommendations.append("급여 조정 검토 - 시장 수준 대비 분석 필요")
        
        if risk_factors['growth'] > 50:
            recommendations.append("경력 개발 계획 수립 - 승진 기회 또는 새로운 책임 부여")
        
        if risk_factors['engagement'] > 50:
            recommendations.append("1:1 면담 실시 - 업무 만족도 및 개선사항 파악")
        
        if risk_factors['performance'] > 50:
            recommendations.append("성과 개선 프로그램 제공 - 멘토링 또는 교육 지원")
        
        if risk_score > 70:
            recommendations.insert(0, "즉시 관리자 개입 필요 - 긴급 면담 실시")
        
        return recommendations
    
    def _generate_turnover_insights(self, employee: Employee,
                                   risk_factors: Dict[str, float],
                                   risk_score: float) -> str:
        """퇴사 위험 인사이트 생성"""
        insights = []
        
        # 주요 위험 요인 식별
        high_risk_factors = [
            factor for factor, score in risk_factors.items() 
            if score > 50
        ]
        
        if high_risk_factors:
            insights.append(
                f"주요 위험 요인: {', '.join(high_risk_factors)}"
            )
        
        # 위험 수준별 메시지
        if risk_score > 70:
            insights.append(
                "높은 퇴사 위험도를 보이고 있어 즉각적인 조치가 필요합니다."
            )
        elif risk_score > 40:
            insights.append(
                "중간 수준의 퇴사 위험도를 보이고 있어 예방적 관리가 권장됩니다."
            )
        else:
            insights.append(
                "낮은 퇴사 위험도를 보이고 있으나 지속적인 모니터링이 필요합니다."
            )
        
        return " ".join(insights)
    
    def _evaluate_performance_history(self, employee: Employee) -> float:
        """성과 이력 평가"""
        evaluations = PerformanceEvaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date')[:5]
        
        if not evaluations:
            return 50
        
        # 성과 추세 분석
        scores = [e.overall_score for e in evaluations]
        avg_score = sum(scores) / len(scores)
        
        # 상승 추세 가산점
        if len(scores) >= 2 and scores[0] > scores[-1]:
            trend_bonus = 10
        else:
            trend_bonus = 0
        
        return min(100, avg_score + trend_bonus)
    
    def _evaluate_skill_development(self, employee: Employee) -> float:
        """스킬 개발 평가 (시뮬레이션)"""
        # 실제로는 교육 이수, 자격증 취득 등을 분석
        return random.randint(60, 90)
    
    def _evaluate_leadership_potential(self, employee: Employee) -> float:
        """리더십 잠재력 평가 (시뮬레이션)"""
        # 실제로는 360도 평가, 프로젝트 리드 경험 등을 분석
        return random.randint(50, 85)
    
    def _evaluate_tenure_readiness(self, employee: Employee) -> float:
        """근속 기간 기반 준비도"""
        tenure_years = (timezone.now().date() - employee.hire_date).days / 365
        
        if tenure_years < 2:
            return 30
        elif tenure_years < 4:
            return 60
        elif tenure_years < 6:
            return 80
        else:
            return 90
    
    def _evaluate_business_impact(self, employee: Employee) -> float:
        """비즈니스 영향력 평가 (시뮬레이션)"""
        # 실제로는 프로젝트 성과, 매출 기여도 등을 분석
        return random.randint(55, 88)
    
    def _assess_promotion_readiness(self, employee: Employee,
                                   factors: Dict[str, float],
                                   score: float) -> Dict[str, Any]:
        """승진 준비도 평가"""
        readiness_level = 'NOT_READY'
        if score >= 80:
            readiness_level = 'READY'
        elif score >= 65:
            readiness_level = 'ALMOST_READY'
        elif score >= 50:
            readiness_level = 'DEVELOPING'
        
        return {
            'level': readiness_level,
            'strengths': [f for f, s in factors.items() if s >= 70],
            'areas_to_improve': [f for f, s in factors.items() if s < 50],
        }
    
    def _identify_development_areas(self, employee: Employee,
                                   factors: Dict[str, float]) -> List[Dict[str, Any]]:
        """개발 필요 영역 식별"""
        areas = []
        
        for factor, score in factors.items():
            if score < 70:
                areas.append({
                    'area': factor,
                    'current_score': score,
                    'target_score': 80,
                    'recommendations': self._get_development_recommendations(factor),
                })
        
        return areas
    
    def _get_development_recommendations(self, factor: str) -> List[str]:
        """영역별 개발 추천사항"""
        recommendations_map = {
            'skills': [
                "전문 교육 프로그램 참여",
                "관련 자격증 취득",
                "멘토링 프로그램 참여"
            ],
            'leadership': [
                "리더십 교육 이수",
                "프로젝트 리드 경험 확대",
                "팀 관리 실습 기회"
            ],
            'performance': [
                "성과 개선 계획 수립",
                "정기적인 피드백 세션",
                "목표 재설정 및 모니터링"
            ],
        }
        
        return recommendations_map.get(factor, ["개별 개발 계획 수립 필요"])
    
    def _estimate_promotion_timeline(self, score: float) -> str:
        """승진 예상 시기"""
        if score >= 80:
            return "6개월 이내"
        elif score >= 65:
            return "6-12개월"
        elif score >= 50:
            return "1-2년"
        else:
            return "2년 이상"
    
    def _calculate_team_avg_performance(self, team_members) -> float:
        """팀 평균 성과"""
        total_score = 0
        count = 0
        
        for member in team_members:
            latest_eval = PerformanceEvaluation.objects.filter(
                employee=member
            ).order_by('-evaluation_period__end_date').first()
            
            if latest_eval:
                total_score += latest_eval.overall_score
                count += 1
        
        return total_score / count if count > 0 else 50
    
    def _calculate_skill_diversity(self, team_members) -> float:
        """팀 스킬 다양성 (시뮬레이션)"""
        # 실제로는 각 멤버의 스킬 프로필을 분석
        return random.randint(60, 90)
    
    def _calculate_experience_balance(self, team_members) -> float:
        """팀 경험 균형도"""
        tenures = []
        for member in team_members:
            tenure_years = (timezone.now().date() - member.hire_date).days / 365
            tenures.append(tenure_years)
        
        if not tenures:
            return 50
        
        # 다양한 경력 수준이 섞여있을수록 높은 점수
        avg_tenure = sum(tenures) / len(tenures)
        variance = sum((t - avg_tenure) ** 2 for t in tenures) / len(tenures)
        
        # 적절한 분산이 있으면 높은 점수
        if 2 <= variance <= 10:
            return 85
        elif variance < 2:
            return 60  # 너무 비슷한 경력
        else:
            return 70  # 너무 큰 격차
    
    def _calculate_collaboration_score(self, team_members) -> float:
        """팀 협업 점수 (시뮬레이션)"""
        # 실제로는 프로젝트 협업 데이터, 피어 리뷰 등을 분석
        return random.randint(65, 88)
    
    def _predict_team_performance(self, metrics: Dict[str, float]) -> float:
        """팀 성과 예측"""
        weights = {
            'avg_performance': 0.35,
            'skill_diversity': 0.20,
            'experience_balance': 0.15,
            'collaboration': 0.30,
        }
        
        # 팀 크기 보정
        size_factor = 1.0
        if metrics['size'] < 5:
            size_factor = 0.9  # 너무 작은 팀
        elif metrics['size'] > 15:
            size_factor = 0.85  # 너무 큰 팀
        
        base_score = sum(
            metrics.get(key, 50) * weight 
            for key, weight in weights.items()
        )
        
        return base_score * size_factor
    
    def _identify_team_strengths(self, metrics: Dict[str, float]) -> List[str]:
        """팀 강점 식별"""
        strengths = []
        
        if metrics.get('avg_performance', 0) > 75:
            strengths.append("높은 개인 성과 수준")
        
        if metrics.get('skill_diversity', 0) > 80:
            strengths.append("다양한 전문성 보유")
        
        if metrics.get('collaboration', 0) > 80:
            strengths.append("우수한 팀워크")
        
        if metrics.get('experience_balance', 0) > 80:
            strengths.append("균형잡힌 경력 구성")
        
        return strengths
    
    def _identify_team_weaknesses(self, metrics: Dict[str, float]) -> List[str]:
        """팀 약점 식별"""
        weaknesses = []
        
        if metrics.get('avg_performance', 100) < 60:
            weaknesses.append("성과 개선 필요")
        
        if metrics.get('skill_diversity', 100) < 60:
            weaknesses.append("스킬 다양성 부족")
        
        if metrics.get('collaboration', 100) < 60:
            weaknesses.append("팀워크 강화 필요")
        
        if metrics['size'] < 5:
            weaknesses.append("팀 규모 확대 필요")
        elif metrics['size'] > 15:
            weaknesses.append("팀 규모 최적화 필요")
        
        return weaknesses
    
    def _generate_team_optimization(self, department: str,
                                   metrics: Dict[str, float],
                                   strengths: List[str],
                                   weaknesses: List[str]) -> List[Dict[str, str]]:
        """팀 최적화 제안"""
        suggestions = []
        
        if "성과 개선 필요" in weaknesses:
            suggestions.append({
                'type': 'PERFORMANCE',
                'action': '팀 성과 향상 프로그램 실시',
                'details': '개별 코칭, 목표 재설정, 성과 모니터링 강화'
            })
        
        if "스킬 다양성 부족" in weaknesses:
            suggestions.append({
                'type': 'SKILL',
                'action': '신규 인재 영입 또는 교육 강화',
                'details': '부족한 스킬 영역 파악 후 채용 또는 교육 계획 수립'
            })
        
        if "팀워크 강화 필요" in weaknesses:
            suggestions.append({
                'type': 'COLLABORATION',
                'action': '팀 빌딩 활동 강화',
                'details': '정기적인 팀 미팅, 협업 프로젝트, 팀 빌딩 이벤트'
            })
        
        return suggestions
    
    def _identify_team_risks(self, metrics: Dict[str, float]) -> List[Dict[str, str]]:
        """팀 위험 요소 식별"""
        risks = []
        
        if metrics.get('avg_performance', 100) < 50:
            risks.append({
                'type': 'PERFORMANCE_RISK',
                'level': 'HIGH',
                'description': '전반적인 성과 저하 위험'
            })
        
        if metrics['size'] < 3:
            risks.append({
                'type': 'CAPACITY_RISK',
                'level': 'HIGH',
                'description': '인력 부족으로 인한 업무 과부하 위험'
            })
        
        return risks
    
    def _analyze_position_requirements(self, position: str) -> Dict[str, Any]:
        """포지션 요구사항 분석"""
        # 실제로는 직무 기술서, 역량 모델 등을 분석
        return {
            'required_skills': ['리더십', '전략적 사고', '의사소통'],
            'experience_years': 5,
            'education_level': 'BACHELOR',
            'competencies': ['문제해결', '팀워크', '혁신'],
        }
    
    def _calculate_position_fit(self, candidate: Employee, 
                               requirements: Dict[str, Any]) -> float:
        """후보자-포지션 적합도 계산"""
        # 시뮬레이션 점수
        base_score = random.randint(40, 95)
        
        # 경력 보정
        tenure_years = (timezone.now().date() - candidate.hire_date).days / 365
        if tenure_years >= requirements['experience_years']:
            base_score += 5
        
        return min(100, base_score)
    
    def _identify_candidate_strengths(self, candidate: Employee,
                                     requirements: Dict[str, Any]) -> List[str]:
        """후보자 강점 식별"""
        strengths = []
        
        # 시뮬레이션
        if random.random() > 0.5:
            strengths.append("우수한 성과 이력")
        if random.random() > 0.5:
            strengths.append("관련 경험 보유")
        if random.random() > 0.5:
            strengths.append("리더십 잠재력")
        
        return strengths
    
    def _identify_candidate_gaps(self, candidate: Employee,
                                requirements: Dict[str, Any]) -> List[str]:
        """후보자 부족 영역 식별"""
        gaps = []
        
        # 시뮬레이션
        if random.random() > 0.7:
            gaps.append("특정 기술 역량 개발 필요")
        if random.random() > 0.8:
            gaps.append("리더십 경험 부족")
        
        return gaps
    
    def _create_development_plan(self, candidate: Employee,
                                requirements: Dict[str, Any]) -> List[str]:
        """개발 계획 생성"""
        plan = []
        
        # 시뮬레이션
        plan.append("3개월 내 핵심 역량 교육 이수")
        plan.append("6개월 내 프로젝트 리드 경험")
        plan.append("멘토링 프로그램 참여")
        
        return plan
    
    def _analyze_current_compensation(self, employees) -> Dict[str, Any]:
        """현재 보상 현황 분석"""
        compensations = EmployeeCompensation.objects.filter(
            employee__in=employees
        )
        
        if not compensations:
            return {'total': 0, 'average': 0, 'min': 0, 'max': 0}
        
        salaries = [c.base_salary for c in compensations]
        
        return {
            'total': sum(salaries),
            'average': sum(salaries) / len(salaries),
            'min': min(salaries),
            'max': max(salaries),
            'count': len(salaries),
        }
    
    def _compare_with_market(self, compensation_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """시장 급여 비교 (시뮬레이션)"""
        avg_salary = compensation_analysis.get('average', 0)
        
        # 시뮬레이션된 시장 데이터
        market_avg = avg_salary * random.uniform(0.9, 1.1)
        
        return {
            'market_average': market_avg,
            'company_average': avg_salary,
            'difference_percent': ((avg_salary - market_avg) / market_avg * 100) if market_avg else 0,
            'competitiveness': 'COMPETITIVE' if avg_salary >= market_avg else 'BELOW_MARKET',
        }
    
    def _analyze_compensation_equity(self, employees) -> Dict[str, Any]:
        """보상 공정성 분석"""
        # 직급별 급여 분포 분석
        position_stats = {}
        
        for emp in employees:
            try:
                comp = EmployeeCompensation.objects.get(employee=emp)
                position = emp.position
                
                if position not in position_stats:
                    position_stats[position] = []
                
                position_stats[position].append(comp.base_salary)
            except EmployeeCompensation.DoesNotExist:
                continue
        
        # 각 직급별 급여 편차 계산
        equity_scores = {}
        for position, salaries in position_stats.items():
            if len(salaries) > 1:
                avg = sum(salaries) / len(salaries)
                variance = sum((s - avg) ** 2 for s in salaries) / len(salaries)
                std_dev = variance ** 0.5
                cv = (std_dev / avg * 100) if avg else 0  # 변동계수
                
                equity_scores[position] = {
                    'coefficient_of_variation': cv,
                    'equity_level': 'HIGH' if cv < 10 else 'MEDIUM' if cv < 20 else 'LOW',
                }
        
        return equity_scores
    
    def _generate_compensation_optimization(self, current: Dict[str, Any],
                                          market: Dict[str, Any],
                                          equity: Dict[str, Any]) -> List[Dict[str, str]]:
        """보상 최적화 제안"""
        recommendations = []
        
        # 시장 경쟁력 개선
        if market.get('competitiveness') == 'BELOW_MARKET':
            recommendations.append({
                'type': 'MARKET_ADJUSTMENT',
                'action': '시장 수준 급여 조정',
                'details': f"평균 {abs(market['difference_percent']):.1f}% 인상 검토",
                'priority': 'HIGH'
            })
        
        # 내부 공정성 개선
        low_equity_positions = [
            pos for pos, stats in equity.items()
            if stats.get('equity_level') == 'LOW'
        ]
        
        if low_equity_positions:
            recommendations.append({
                'type': 'EQUITY_IMPROVEMENT',
                'action': '내부 급여 공정성 개선',
                'details': f"직급별 급여 편차 조정: {', '.join(low_equity_positions)}",
                'priority': 'MEDIUM'
            })
        
        # 성과 기반 보상 강화
        recommendations.append({
            'type': 'PERFORMANCE_PAY',
            'action': '성과급 제도 개선',
            'details': '개인/팀 성과와 보상 연계 강화',
            'priority': 'MEDIUM'
        })
        
        return recommendations
    
    def _calculate_budget_impact(self, recommendations: List[Dict[str, str]]) -> Dict[str, float]:
        """예산 영향 계산 (시뮬레이션)"""
        total_impact = 0
        
        for rec in recommendations:
            if rec['type'] == 'MARKET_ADJUSTMENT':
                # 시뮬레이션: 전체 급여의 5-10% 증가
                total_impact += random.uniform(0.05, 0.10)
            elif rec['type'] == 'EQUITY_IMPROVEMENT':
                # 시뮬레이션: 전체 급여의 2-5% 증가
                total_impact += random.uniform(0.02, 0.05)
        
        return {
            'percentage_increase': total_impact * 100,
            'confidence': 0.75,
        }


class HRChatbotService:
    """HR 챗봇 서비스"""
    
    def __init__(self):
        self.faq_responses = self._load_faq_responses()
    
    def process_message(self, user: User, message: str, 
                       conversation: Optional[HRChatbotConversation] = None) -> Dict[str, Any]:
        """사용자 메시지 처리"""
        # 대화 컨텍스트 생성 또는 로드
        if not conversation:
            conversation = HRChatbotConversation.objects.create(
                user=user,
                employee=getattr(user, 'employee', None)
            )
        
        # 메시지 저장
        conversation.add_message('user', message)
        
        # 의도 파악
        intent = self._identify_intent(message)
        
        # 응답 생성
        if intent == 'FAQ':
            response = self._handle_faq(message)
        elif intent == 'POLICY':
            response = self._handle_policy_query(message)
        elif intent == 'PERSONAL':
            response = self._handle_personal_query(user, message)
        elif intent == 'ANALYSIS':
            response = self._handle_analysis_request(user, message)
        else:
            response = self._handle_general_query(message)
        
        # 응답 저장
        conversation.add_message('assistant', response['content'])
        
        return {
            'conversation_id': conversation.id,
            'response': response['content'],
            'suggested_actions': response.get('actions', []),
            'references': response.get('references', []),
        }
    
    def _load_faq_responses(self) -> Dict[str, str]:
        """FAQ 응답 로드"""
        return {
            '연차': '연차는 입사일 기준으로 매년 발생하며, 근속기간에 따라 15일~25일이 부여됩니다.',
            '급여명세서': '급여명세서는 매월 급여일에 이메일로 발송되며, HR 시스템에서도 확인 가능합니다.',
            '재직증명서': '재직증명서는 HR 시스템의 "증명서 발급" 메뉴에서 즉시 발급 가능합니다.',
            '교육': '교육 신청은 HR 시스템의 "교육/훈련" 메뉴에서 가능하며, 부서장 승인이 필요합니다.',
            '평가': '평가는 연 2회(상/하반기) 실시되며, 자기평가 → 1차평가 → 2차평가 순으로 진행됩니다.',
        }
    
    def _identify_intent(self, message: str) -> str:
        """메시지 의도 파악"""
        message_lower = message.lower()
        
        # 키워드 기반 의도 분류
        if any(keyword in message_lower for keyword in ['연차', '휴가', '급여', '재직증명']):
            return 'FAQ'
        elif any(keyword in message_lower for keyword in ['정책', '규정', '제도']):
            return 'POLICY'
        elif any(keyword in message_lower for keyword in ['내', '나의', '제']):
            return 'PERSONAL'
        elif any(keyword in message_lower for keyword in ['분석', '예측', '추천']):
            return 'ANALYSIS'
        else:
            return 'GENERAL'
    
    def _handle_faq(self, message: str) -> Dict[str, Any]:
        """FAQ 처리"""
        for keyword, response in self.faq_responses.items():
            if keyword in message:
                return {
                    'content': response,
                    'actions': ['추가 문의하기', '관련 정책 보기'],
                }
        
        return {
            'content': '관련 FAQ를 찾을 수 없습니다. 좀 더 구체적으로 질문해 주시거나, HR 담당자에게 문의해 주세요.',
            'actions': ['HR 담당자 연결', '다시 질문하기'],
        }
    
    def _handle_policy_query(self, message: str) -> Dict[str, Any]:
        """정책 관련 질의 처리"""
        return {
            'content': 'HR 정책과 관련된 문의입니다. 구체적인 정책 내용은 HR 포털의 "정책/규정" 섹션에서 확인하실 수 있습니다.',
            'references': [
                {'title': 'HR 정책 가이드', 'url': '/hr/policies'},
                {'title': '취업규칙', 'url': '/hr/policies/rules'},
            ],
            'actions': ['정책 문서 보기', 'HR 담당자 문의'],
        }
    
    def _handle_personal_query(self, user: User, message: str) -> Dict[str, Any]:
        """개인 정보 관련 질의 처리"""
        if not hasattr(user, 'employee'):
            return {
                'content': '직원 정보를 찾을 수 없습니다. HR 담당자에게 문의해 주세요.',
                'actions': ['HR 담당자 연결'],
            }
        
        return {
            'content': '개인 정보 조회를 위해서는 HR 시스템의 "내 정보" 메뉴를 이용해 주세요.',
            'actions': ['내 정보 보기', '정보 수정 요청'],
        }
    
    def _handle_analysis_request(self, user: User, message: str) -> Dict[str, Any]:
        """분석 요청 처리"""
        return {
            'content': 'AI 기반 분석을 요청하셨습니다. AIRISS 대시보드에서 다양한 분석 결과를 확인하실 수 있습니다.',
            'actions': ['AIRISS 대시보드 이동', '분석 리포트 요청'],
        }
    
    def _handle_general_query(self, message: str) -> Dict[str, Any]:
        """일반 질의 처리"""
        return {
            'content': '무엇을 도와드릴까요? HR 관련 질문이나 요청사항을 말씀해 주세요.',
            'actions': ['자주 묻는 질문', 'HR 담당자 연결', '메뉴 보기'],
        }


class AIInsightService:
    """AI 인사이트 생성 서비스"""
    
    def generate_insights(self) -> List[AIInsight]:
        """전사 HR 인사이트 생성"""
        insights = []
        
        # 퇴사 위험 인사이트
        high_risk_count = self._count_high_risk_employees()
        if high_risk_count > 5:
            insights.append(
                self._create_retention_insight(high_risk_count)
            )
        
        # 팀 성과 인사이트
        low_performing_teams = self._identify_low_performing_teams()
        if low_performing_teams:
            insights.append(
                self._create_team_performance_insight(low_performing_teams)
            )
        
        # 승진 준비 인사이트
        promotion_ready = self._count_promotion_ready_employees()
        if promotion_ready > 10:
            insights.append(
                self._create_promotion_insight(promotion_ready)
            )
        
        # 보상 공정성 인사이트
        equity_issues = self._identify_compensation_issues()
        if equity_issues:
            insights.append(
                self._create_compensation_insight(equity_issues)
            )
        
        return insights
    
    def _count_high_risk_employees(self) -> int:
        """높은 퇴사 위험 직원 수 계산"""
        # 최근 분석 결과에서 높은 위험도 직원 조회
        high_risk = AIAnalysisResult.objects.filter(
            analysis_type__type_code='TURNOVER_RISK',
            score__gte=70,
            analyzed_at__gte=timezone.now() - timedelta(days=30)
        ).values('employee').distinct().count()
        
        return high_risk
    
    def _create_retention_insight(self, count: int) -> AIInsight:
        """인재 유지 인사이트 생성"""
        return AIInsight(
            title=f"{count}명의 핵심 인재가 높은 퇴사 위험도를 보이고 있습니다",
            category='RETENTION',
            priority='HIGH',
            description=f"최근 AI 분석 결과, {count}명의 직원이 70% 이상의 퇴사 위험도를 보이고 있습니다. "
                       "즉각적인 관리 개입이 필요합니다.",
            impact_analysis="핵심 인재 이탈 시 업무 공백, 채용 비용 증가, 팀 사기 저하 등의 부정적 영향이 예상됩니다.",
            action_items=[
                "해당 직원들과 1:1 면담 실시",
                "보상 및 경력 개발 계획 검토",
                "업무 만족도 개선 방안 수립",
            ]
        )
    
    def _identify_low_performing_teams(self) -> List[str]:
        """저성과 팀 식별"""
        # 시뮬레이션: 실제로는 팀 성과 데이터 분석
        return []
    
    def _create_team_performance_insight(self, teams: List[str]) -> AIInsight:
        """팀 성과 인사이트 생성"""
        team_names = teams
        
        return AIInsight(
            title=f"{len(teams)}개 팀의 성과 개선이 필요합니다",
            category='PERFORMANCE',
            priority='MEDIUM',
            description=f"AI 분석 결과, {', '.join(team_names)} 팀의 성과가 목표 대비 저조한 것으로 나타났습니다.",
            impact_analysis="팀 성과 저하는 전체 조직 목표 달성에 부정적 영향을 미칠 수 있습니다.",
            action_items=[
                "팀별 성과 진단 미팅 실시",
                "성과 개선 계획 수립",
                "필요 시 팀 재구성 검토",
            ]
        )
    
    def _count_promotion_ready_employees(self) -> int:
        """승진 준비된 직원 수 계산"""
        # 최근 분석 결과에서 승진 준비도 높은 직원 조회
        ready_count = AIAnalysisResult.objects.filter(
            analysis_type__type_code='PROMOTION_POTENTIAL',
            score__gte=80,
            analyzed_at__gte=timezone.now() - timedelta(days=30)
        ).values('employee').distinct().count()
        
        return ready_count
    
    def _create_promotion_insight(self, count: int) -> AIInsight:
        """승진 인사이트 생성"""
        return AIInsight(
            title=f"{count}명의 직원이 승진 준비가 완료되었습니다",
            category='DEVELOPMENT',
            priority='MEDIUM',
            description=f"AI 분석 결과, {count}명의 직원이 다음 직급으로의 승진 준비가 완료된 것으로 평가됩니다.",
            impact_analysis="적시에 승진 기회를 제공하지 않을 경우 우수 인재 이탈 위험이 있습니다.",
            action_items=[
                "승진 심사 일정 수립",
                "승진 후보자 pool 검토",
                "경력 개발 면담 실시",
            ]
        )
    
    def _identify_compensation_issues(self) -> List[str]:
        """보상 관련 이슈 식별"""
        # 시뮬레이션: 실제로는 보상 공정성 데이터 분석
        return []
    
    def _create_compensation_insight(self, issues: List[str]) -> AIInsight:
        """보상 인사이트 생성"""
        return AIInsight(
            title="보상 체계 개선이 필요합니다",
            category='COMPENSATION',
            priority='MEDIUM',
            description="AI 분석 결과, 일부 직급/부서에서 보상 공정성 이슈가 발견되었습니다.",
            impact_analysis="보상 불공정은 직원 만족도 저하와 이직률 증가로 이어질 수 있습니다.",
            action_items=[
                "직급별 급여 밴드 재검토",
                "시장 급여 조사 실시",
                "성과 기반 보상 제도 개선",
            ]
        )