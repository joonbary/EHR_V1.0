"""
승진 분석 및 예측 모듈
시퀀셜싱킹 MCP를 활용한 승진 후보자 분석
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
import pandas as pd
import numpy as np


class PromotionAnalyzer:
    """승진 분석 및 예측을 위한 분석기"""
    
    def __init__(self):
        # 성장레벨별 승진 요건
        self.promotion_requirements = {
            'Level_1_to_2': {
                'min_tenure_years': 2,
                'min_consecutive_a': 1,
                'min_avg_score': 3.0
            },
            'Level_2_to_3': {
                'min_tenure_years': 3,
                'min_consecutive_a': 2,
                'min_avg_score': 3.2
            },
            'Level_3_to_4': {
                'min_tenure_years': 4,
                'min_consecutive_a': 2,
                'min_avg_score': 3.5
            },
            'Level_4_to_5': {
                'min_tenure_years': 5,
                'min_consecutive_a': 3,
                'min_avg_score': 3.7
            },
            'Level_5_to_6': {
                'min_tenure_years': 7,
                'min_consecutive_a': 3,
                'min_avg_score': 4.0
            }
        }
    
    def analyze_promotion_candidates(self, target_year: int = None) -> Dict:
        """승진 후보자 종합 분석"""
        from employees.models import Employee
        from evaluations.models import ComprehensiveEvaluation
        
        if not target_year:
            target_year = timezone.now().year
        
        candidates = []
        
        # 모든 직원 대상 분석
        employees = Employee.objects.filter(
            employment_status='active',
            growth_level__lt=6  # Level 6 미만
        ).select_related('user')
        
        for employee in employees:
            # 승진 자격 분석
            eligibility = self._check_promotion_eligibility(employee)
            
            if eligibility['is_eligible'] or eligibility['will_be_eligible_soon']:
                # 성과 트렌드 분석
                performance_trend = self._analyze_performance_trend(employee)
                
                # 승진 예측 점수 계산
                promotion_score = self._calculate_promotion_score(
                    employee, eligibility, performance_trend
                )
                
                candidates.append({
                    'employee': employee,
                    'current_level': employee.growth_level,
                    'target_level': self._get_next_level(employee.growth_level),
                    'eligibility': eligibility,
                    'performance_trend': performance_trend,
                    'promotion_score': promotion_score,
                    'recommendation': self._generate_recommendation(
                        eligibility, performance_trend, promotion_score
                    )
                })
        
        # 우선순위 정렬
        candidates.sort(key=lambda x: x['promotion_score'], reverse=True)
        
        return {
            'year': target_year,
            'total_candidates': len(candidates),
            'eligible_now': sum(1 for c in candidates if c['eligibility']['is_eligible']),
            'eligible_soon': sum(1 for c in candidates if c['eligibility']['will_be_eligible_soon']),
            'candidates': candidates,
            'level_distribution': self._get_level_distribution(candidates),
            'department_distribution': self._get_department_distribution(candidates)
        }
    
    def _check_promotion_eligibility(self, employee) -> Dict:
        """승진 자격 요건 확인"""
        from evaluations.models import ComprehensiveEvaluation
        
        current_level = employee.growth_level
        next_level = self._get_next_level(current_level)
        
        if not next_level:
            return {'is_eligible': False, 'reason': '최고 레벨 도달'}
        
        # 요건 키 생성
        req_key = f"{current_level}_to_{next_level.replace('Level_', '')}"
        requirements = self.promotion_requirements.get(req_key, {})
        
        # 재직 기간 계산
        tenure_years = (timezone.now().date() - employee.hire_date).days / 365.25
        
        # 최근 평가 기록 조회
        recent_evaluations = ComprehensiveEvaluation.objects.filter(
            employee=employee,
            is_completed=True
        ).order_by('-evaluation_period__end_date')[:4]
        
        # 연속 A등급 이상 횟수 계산
        consecutive_a = 0
        for eval in recent_evaluations:
            grade = eval.final_grade or eval.manager_grade
            if grade in ['S', 'A+', 'A']:
                consecutive_a += 1
            else:
                break
        
        # 평균 성과 점수 계산
        avg_score = 0
        if recent_evaluations:
            scores = [e.total_score for e in recent_evaluations if e.total_score]
            avg_score = sum(scores) / len(scores) if scores else 0
        
        # 자격 요건 충족 여부
        is_eligible = (
            tenure_years >= requirements.get('min_tenure_years', 0) and
            consecutive_a >= requirements.get('min_consecutive_a', 0) and
            avg_score >= requirements.get('min_avg_score', 0)
        )
        
        # 곧 자격을 갖출 예정인지 확인
        will_be_eligible_soon = False
        missing_requirements = []
        
        if not is_eligible:
            if tenure_years < requirements.get('min_tenure_years', 0):
                years_needed = requirements.get('min_tenure_years', 0) - tenure_years
                if years_needed <= 1:
                    will_be_eligible_soon = True
                missing_requirements.append(f"재직기간 {years_needed:.1f}년 부족")
            
            if consecutive_a < requirements.get('min_consecutive_a', 0):
                needed = requirements.get('min_consecutive_a', 0) - consecutive_a
                if needed == 1:
                    will_be_eligible_soon = True
                missing_requirements.append(f"연속 A등급 {needed}회 부족")
            
            if avg_score < requirements.get('min_avg_score', 0):
                score_gap = requirements.get('min_avg_score', 0) - avg_score
                if score_gap <= 0.3:
                    will_be_eligible_soon = True
                missing_requirements.append(f"평균점수 {score_gap:.1f}점 부족")
        
        return {
            'is_eligible': is_eligible,
            'will_be_eligible_soon': will_be_eligible_soon,
            'tenure_years': tenure_years,
            'consecutive_a': consecutive_a,
            'avg_score': avg_score,
            'requirements': requirements,
            'missing_requirements': missing_requirements
        }
    
    def _analyze_performance_trend(self, employee) -> Dict:
        """성과 트렌드 분석"""
        from evaluations.models import ComprehensiveEvaluation
        
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee=employee,
            is_completed=True
        ).order_by('-evaluation_period__end_date')[:6]
        
        if not evaluations:
            return {
                'trend': 'no_data',
                'consistency': 0,
                'improvement_rate': 0
            }
        
        # 점수 추출
        scores = [e.total_score for e in evaluations if e.total_score]
        
        if len(scores) < 2:
            return {
                'trend': 'insufficient_data',
                'consistency': 0,
                'improvement_rate': 0
            }
        
        # 트렌드 계산
        scores_array = np.array(scores)
        x = np.arange(len(scores))
        
        # 선형 회귀
        slope, intercept = np.polyfit(x, scores_array, 1)
        
        # 일관성 (변동계수의 역수)
        consistency = 1 / (np.std(scores_array) / np.mean(scores_array)) if np.mean(scores_array) > 0 else 0
        
        # 개선율
        improvement_rate = (scores[0] - scores[-1]) / scores[-1] if scores[-1] > 0 else 0
        
        # 트렌드 판단
        if slope > 0.1:
            trend = 'improving'
        elif slope < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'consistency': consistency,
            'improvement_rate': improvement_rate,
            'recent_scores': scores[:3],
            'slope': slope
        }
    
    def _calculate_promotion_score(self, employee, eligibility: Dict, performance_trend: Dict) -> float:
        """승진 예측 점수 계산 (0-100)"""
        score = 0
        
        # 1. 자격 요건 충족도 (40점)
        if eligibility['is_eligible']:
            score += 40
        elif eligibility['will_be_eligible_soon']:
            score += 25
        
        # 2. 성과 수준 (30점)
        avg_score = eligibility.get('avg_score', 0)
        score += min(30, (avg_score / 4.0) * 30)
        
        # 3. 성과 트렌드 (20점)
        if performance_trend['trend'] == 'improving':
            score += 20
        elif performance_trend['trend'] == 'stable':
            score += 15
        elif performance_trend['trend'] == 'declining':
            score += 5
        
        # 4. 일관성 (10점)
        consistency_score = min(10, performance_trend.get('consistency', 0) * 5)
        score += consistency_score
        
        # 보너스 점수
        # 연속 S등급
        recent_s_count = 0
        from evaluations.models import ComprehensiveEvaluation
        recent_evals = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date')[:3]
        
        for eval in recent_evals:
            if (eval.final_grade or eval.manager_grade) == 'S':
                recent_s_count += 1
        
        if recent_s_count >= 2:
            score = min(100, score + 10)
        
        return round(score, 1)
    
    def _generate_recommendation(self, eligibility: Dict, performance_trend: Dict, promotion_score: float) -> str:
        """승진 추천 의견 생성"""
        if promotion_score >= 80:
            if eligibility['is_eligible']:
                return "강력 추천 - 모든 요건을 충족하며 우수한 성과를 보이고 있습니다."
            else:
                return "조건부 추천 - 우수한 성과를 보이나 일부 요건이 미충족 상태입니다."
        
        elif promotion_score >= 60:
            if performance_trend['trend'] == 'improving':
                return "추천 - 지속적인 성과 향상을 보이고 있습니다."
            else:
                return "보통 - 안정적인 성과를 유지하고 있습니다."
        
        elif promotion_score >= 40:
            missing = ', '.join(eligibility.get('missing_requirements', []))
            return f"보류 - 추가 개발이 필요합니다. ({missing})"
        
        else:
            return "재검토 필요 - 현재 승진 요건을 충족하지 못합니다."
    
    def _get_next_level(self, current_level: str) -> Optional[str]:
        """다음 성장 레벨 반환"""
        level_map = {
            'Level_1': 'Level_2',
            'Level_2': 'Level_3',
            'Level_3': 'Level_4',
            'Level_4': 'Level_5',
            'Level_5': 'Level_6',
            'Level_6': None
        }
        return level_map.get(current_level)
    
    def _get_level_distribution(self, candidates: List[Dict]) -> Dict:
        """레벨별 후보자 분포"""
        distribution = {}
        for candidate in candidates:
            level = candidate['current_level']
            if level not in distribution:
                distribution[level] = 0
            distribution[level] += 1
        return distribution
    
    def _get_department_distribution(self, candidates: List[Dict]) -> Dict:
        """부서별 후보자 분포"""
        distribution = {}
        for candidate in candidates:
            dept = candidate['employee'].department
            if dept not in distribution:
                distribution[dept] = 0
            distribution[dept] += 1
        return distribution
    
    def generate_promotion_forecast(self, years: int = 3) -> Dict:
        """향후 N년간 승진 예측"""
        from employees.models import Employee
        
        current_year = timezone.now().year
        forecast = {}
        
        for year_offset in range(years):
            target_year = current_year + year_offset
            
            # 각 레벨별 예상 승진자 수 계산
            level_forecast = {}
            
            for level in ['Level_1', 'Level_2', 'Level_3', 'Level_4', 'Level_5']:
                # 현재 레벨의 직원 수
                current_count = Employee.objects.filter(
                    employment_status='active',
                    growth_level=level
                ).count()
                
                # 평균 승진율 (과거 데이터 기반 또는 추정치)
                promotion_rate = self._estimate_promotion_rate(level, year_offset)
                
                # 예상 승진자 수
                expected_promotions = int(current_count * promotion_rate)
                
                level_forecast[level] = {
                    'current_count': current_count,
                    'promotion_rate': promotion_rate,
                    'expected_promotions': expected_promotions
                }
            
            forecast[target_year] = level_forecast
        
        return forecast
    
    def _estimate_promotion_rate(self, level: str, year_offset: int) -> float:
        """레벨별 승진율 추정"""
        # 기본 승진율 (과거 데이터 기반으로 조정 필요)
        base_rates = {
            'Level_1': 0.30,  # 30%
            'Level_2': 0.25,  # 25%
            'Level_3': 0.20,  # 20%
            'Level_4': 0.15,  # 15%
            'Level_5': 0.10   # 10%
        }
        
        # 연도별 조정 (미래로 갈수록 불확실성 증가)
        uncertainty_factor = 1 - (year_offset * 0.05)
        
        return base_rates.get(level, 0.1) * uncertainty_factor