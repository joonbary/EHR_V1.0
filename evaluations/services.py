"""
평가 점수 자동 계산 서비스
OK금융그룹 3대 평가축(기여도/전문성/영향력) 점수 계산 로직
"""

from decimal import Decimal
from typing import Dict, Tuple, Optional
from .models import (
    CONTRIBUTION_SCORING_CHART,
    EXPERTISE_SCORING_CHART,
    IMPACT_SCORING_CHART,
    ContributionEvaluation,
    ExpertiseEvaluation,
    ImpactEvaluation,
    ComprehensiveEvaluation,
    Task
)


class EvaluationScoreCalculator:
    """평가 점수 계산 서비스"""
    
    @staticmethod
    def calculate_contribution_score(
        contribution_scope: str,
        contribution_method: str,
        achievement_rate: float
    ) -> Tuple[float, float]:
        """
        기여도 점수 계산
        
        Args:
            contribution_scope: 기여 범위 (strategic/mutual/independent/dependent)
            contribution_method: 기여 방식 (directing/leading/individual/support)
            achievement_rate: 달성률 (%)
            
        Returns:
            (base_score, final_score) 튜플
        """
        # Scoring Chart에서 기본 점수 가져오기
        base_score = 2.0  # 기본값
        
        if contribution_scope in CONTRIBUTION_SCORING_CHART:
            scope_chart = CONTRIBUTION_SCORING_CHART[contribution_scope]
            if contribution_method in scope_chart:
                base_score = float(scope_chart[contribution_method])
        
        # 달성률에 따른 점수 조정
        if achievement_rate >= 100:
            final_score = base_score
        elif achievement_rate >= 90:
            final_score = base_score - 0.5
        elif achievement_rate >= 80:
            final_score = base_score - 1.0
        elif achievement_rate >= 70:
            final_score = base_score - 1.5
        else:
            final_score = max(1.0, base_score - 2.0)
        
        return base_score, round(final_score, 1)
    
    @staticmethod
    def calculate_expertise_score(
        expertise_scores: Dict[str, int],
        expertise_focus: str = 'balanced'
    ) -> Tuple[float, bool]:
        """
        전문성 점수 계산
        
        Args:
            expertise_scores: 10개 체크리스트 항목별 점수 딕셔너리
            expertise_focus: 전문성 초점 (hard_skill/balanced)
            
        Returns:
            (total_score, is_achieved) 튜플
        """
        # 체크리스트 평균 점수 계산
        if expertise_scores:
            total = sum(expertise_scores.values())
            count = len(expertise_scores)
            average_score = total / count if count > 0 else 0
        else:
            average_score = 0
        
        total_score = round(average_score, 1)
        
        # 달성 여부 판정 (3.0점 이상)
        is_achieved = total_score >= 3.0
        
        return total_score, is_achieved
    
    @staticmethod
    def calculate_impact_score(
        impact_scope: str,
        core_values_practice: str,
        leadership_demonstration: str
    ) -> Tuple[float, bool]:
        """
        영향력 점수 계산
        
        Args:
            impact_scope: 영향력 범위 (market/corp/org/individual)
            core_values_practice: 핵심가치 실천 (exemplary_values/limited_values)
            leadership_demonstration: 리더십 발휘 (exemplary_leadership/limited_leadership)
            
        Returns:
            (total_score, is_achieved) 튜플
        """
        # Scoring Chart 기반 점수 계산
        total_score = 2.0  # 기본값
        
        if impact_scope in IMPACT_SCORING_CHART:
            scope_chart = IMPACT_SCORING_CHART[impact_scope]
            
            # 핵심가치 실천 점수
            values_score = scope_chart.get(core_values_practice, 2)
            
            # 리더십 발휘 점수
            leadership_score = scope_chart.get(leadership_demonstration, 2)
            
            # 평균 점수 계산
            total_score = (values_score + leadership_score) / 2
        
        total_score = round(total_score, 1)
        
        # 달성 여부 판정 (3.0점 이상)
        is_achieved = total_score >= 3.0
        
        return total_score, is_achieved
    
    @staticmethod
    def calculate_comprehensive_grade(
        contribution_achieved: bool,
        expertise_achieved: bool,
        impact_achieved: bool
    ) -> str:
        """
        종합 평가 등급 계산 (1차 평가)
        
        Args:
            contribution_achieved: 기여도 달성 여부
            expertise_achieved: 전문성 달성 여부
            impact_achieved: 영향력 달성 여부
            
        Returns:
            1차 평가 등급 (S/A/B/C)
        """
        achieved_count = sum([
            contribution_achieved,
            expertise_achieved,
            impact_achieved
        ])
        
        if achieved_count == 3:
            return 'S'
        elif achieved_count == 2:
            return 'A'
        elif achieved_count == 1:
            return 'B'
        else:
            return 'C'
    
    @staticmethod
    def update_contribution_evaluation(evaluation: ContributionEvaluation) -> None:
        """
        기여도 평가 업데이트
        Task 기반으로 기여도 평가 점수 재계산
        """
        tasks = evaluation.employee.tasks.filter(
            evaluation_period=evaluation.evaluation_period
        )
        
        if not tasks.exists():
            return
        
        # 종합 달성률 계산
        total_weight = sum(task.weight for task in tasks)
        weighted_achievement = Decimal('0')
        weighted_score = Decimal('0')
        
        for task in tasks:
            # 달성률 계산
            task.calculate_achievement_rate()
            
            if task.achievement_rate:
                weighted_achievement += (task.achievement_rate * task.weight)
            
            # 기여도 점수 계산
            task_score = task.calculate_contribution_score()
            weighted_score += (Decimal(str(task_score)) * task.weight)
        
        if total_weight > 0:
            evaluation.total_achievement_rate = round(weighted_achievement / total_weight, 2)
            evaluation.contribution_score = round(weighted_score / total_weight, 1)
        
        # 달성 여부 판정
        evaluation.is_achieved = (
            evaluation.contribution_score >= 3.0 or 
            (evaluation.total_achievement_rate and evaluation.total_achievement_rate >= 100)
        )
        
        evaluation.save()
    
    @staticmethod
    def update_comprehensive_evaluation(
        comprehensive: ComprehensiveEvaluation
    ) -> None:
        """
        종합 평가 업데이트
        3대 평가 결과를 바탕으로 종합 평가 등급 계산
        """
        # 각 평가 달성 여부 업데이트
        if comprehensive.contribution_evaluation:
            comprehensive.contribution_achieved = comprehensive.contribution_evaluation.is_achieved
        
        if comprehensive.expertise_evaluation:
            comprehensive.expertise_achieved = comprehensive.expertise_evaluation.is_achieved
        
        if comprehensive.impact_evaluation:
            comprehensive.impact_achieved = comprehensive.impact_evaluation.is_achieved
        
        # 1차 평가 등급 자동 계산
        comprehensive.manager_grade = EvaluationScoreCalculator.calculate_comprehensive_grade(
            comprehensive.contribution_achieved,
            comprehensive.expertise_achieved,
            comprehensive.impact_achieved
        )
        
        comprehensive.save()


class EvaluationValidator:
    """평가 유효성 검증 서비스"""
    
    @staticmethod
    def validate_task_weights(employee, evaluation_period) -> Tuple[bool, Optional[str]]:
        """
        Task 가중치 합계 검증
        
        Returns:
            (is_valid, error_message) 튜플
        """
        tasks = Task.objects.filter(
            employee=employee,
            evaluation_period=evaluation_period
        )
        
        total_weight = sum(task.weight for task in tasks)
        
        if abs(total_weight - 100) > 0.01:
            return False, f"Task 가중치 합계가 100%가 아닙니다. (현재: {total_weight}%)"
        
        return True, None


class GrowthLevelAnalyzer:
    """성장레벨 분석 서비스"""
    
    @staticmethod
    def update_employee_growth_history(employee, evaluation_period):
        """직원의 성장레벨 이력 업데이트"""
        from .models import (
            EmployeeGrowthHistory, GrowthLevel, 
            ComprehensiveEvaluation, PerformanceTrend
        )
        
        # 종합평가 가져오기
        comprehensive = ComprehensiveEvaluation.objects.filter(
            employee=employee,
            evaluation_period=evaluation_period
        ).first()
        
        if not comprehensive:
            return None
        
        # 현재 성장레벨 결정
        current_level = GrowthLevel.objects.filter(level=employee.growth_level).first()
        if not current_level:
            # 기본 레벨 생성 또는 설정
            current_level = GrowthLevel.objects.filter(level=1).first()
            if not current_level:
                current_level = GrowthLevel.objects.create(
                    level=1,
                    name="초급",
                    description="신입 또는 초급 수준"
                )
        
        # 이전 성장 이력 가져오기
        previous_history = EmployeeGrowthHistory.objects.filter(
            employee=employee
        ).order_by('-evaluation_period__end_date').first()
        
        # 성장 이력 생성 또는 업데이트
        history, created = EmployeeGrowthHistory.objects.get_or_create(
            employee=employee,
            evaluation_period=evaluation_period,
            defaults={
                'current_level': current_level,
                'previous_level': previous_history.current_level if previous_history else None,
                'change_type': 'MAINTAIN'
            }
        )
        
        # 점수 정보 업데이트
        history.contribution_score = comprehensive.contribution_score
        history.expertise_score = comprehensive.expertise_score
        history.impact_score = comprehensive.impact_score
        history.overall_score = comprehensive.overall_score
        
        # 승급 자격 계산
        history.calculate_promotion_eligibility()
        history.save()
        
        # 성과 트렌드 분석
        GrowthLevelAnalyzer.analyze_performance_trend(employee, evaluation_period)
        
        return history
    
    @staticmethod
    def analyze_performance_trend(employee, evaluation_period):
        """성과 트렌드 분석"""
        from .models import PerformanceTrend, EmployeeGrowthHistory
        
        # 현재 이력
        current_history = EmployeeGrowthHistory.objects.filter(
            employee=employee,
            evaluation_period=evaluation_period
        ).first()
        
        if not current_history:
            return None
        
        # 이전 3개 기간의 이력
        previous_histories = EmployeeGrowthHistory.objects.filter(
            employee=employee,
            evaluation_period__end_date__lt=evaluation_period.end_date
        ).order_by('-evaluation_period__end_date')[:3]
        
        # 트렌드 생성 또는 업데이트
        trend, created = PerformanceTrend.objects.get_or_create(
            employee=employee,
            evaluation_period=evaluation_period
        )
        
        if len(previous_histories) >= 1:
            previous = previous_histories[0]
            
            # 변화율 계산
            if previous.contribution_score and current_history.contribution_score:
                trend.contribution_change_rate = round(
                    ((current_history.contribution_score - previous.contribution_score) / 
                     previous.contribution_score) * 100, 2
                )
            
            if previous.expertise_score and current_history.expertise_score:
                trend.expertise_change_rate = round(
                    ((current_history.expertise_score - previous.expertise_score) / 
                     previous.expertise_score) * 100, 2
                )
            
            if previous.impact_score and current_history.impact_score:
                trend.impact_change_rate = round(
                    ((current_history.impact_score - previous.impact_score) / 
                     previous.impact_score) * 100, 2
                )
            
            if previous.overall_score and current_history.overall_score:
                trend.overall_change_rate = round(
                    ((current_history.overall_score - previous.overall_score) / 
                     previous.overall_score) * 100, 2
                )
        
        # 트렌드 분류
        trend.contribution_trend = GrowthLevelAnalyzer._classify_trend(trend.contribution_change_rate)
        trend.expertise_trend = GrowthLevelAnalyzer._classify_trend(trend.expertise_change_rate)
        trend.impact_trend = GrowthLevelAnalyzer._classify_trend(trend.impact_change_rate)
        trend.overall_trend = GrowthLevelAnalyzer._classify_trend(trend.overall_change_rate)
        
        # AI 인사이트 생성
        trend.insights = GrowthLevelAnalyzer._generate_insights(current_history, previous_histories)
        trend.recommendations = GrowthLevelAnalyzer._generate_recommendations(current_history, trend)
        
        trend.save()
        return trend
    
    @staticmethod
    def _classify_trend(change_rate):
        """변화율을 기반으로 트렌드 분류"""
        if change_rate is None:
            return 'STABLE'
        
        if change_rate > 10:
            return 'IMPROVING'
        elif change_rate > -5:
            return 'STABLE'
        elif change_rate > -15:
            return 'DECLINING'
        else:
            return 'VOLATILE'
    
    @staticmethod
    def _generate_insights(current_history, previous_histories):
        """AI 인사이트 생성"""
        insights = {
            'performance_summary': '',
            'strength_areas': [],
            'improvement_areas': [],
            'growth_trajectory': '',
            'promotion_readiness': ''
        }
        
        # 성과 요약
        if current_history.overall_score:
            if current_history.overall_score >= 3.5:
                insights['performance_summary'] = '우수한 성과를 보이고 있습니다.'
            elif current_history.overall_score >= 3.0:
                insights['performance_summary'] = '목표 수준의 성과를 달성했습니다.'
            elif current_history.overall_score >= 2.5:
                insights['performance_summary'] = '평균적인 성과를 보이고 있습니다.'
            else:
                insights['performance_summary'] = '성과 개선이 필요합니다.'
        
        # 강점 영역 분석
        scores = [
            ('기여도', current_history.contribution_score),
            ('전문성', current_history.expertise_score),
            ('영향력', current_history.impact_score)
        ]
        
        max_score = max(scores, key=lambda x: x[1] or 0)
        if max_score[1] and max_score[1] >= 3.0:
            insights['strength_areas'].append(max_score[0])
        
        # 개선 영역 분석
        min_score = min(scores, key=lambda x: x[1] or 0)
        if min_score[1] and min_score[1] < 3.0:
            insights['improvement_areas'].append(min_score[0])
        
        # 승급 준비도
        if current_history.is_promotion_eligible:
            insights['promotion_readiness'] = '승급 자격을 충족했습니다.'
        elif current_history.meets_score_requirement:
            insights['promotion_readiness'] = f'점수 요구사항은 충족했으나, {current_history.consecutive_achievements}회 연속 달성이 필요합니다.'
        else:
            insights['promotion_readiness'] = '승급을 위해 성과 개선이 필요합니다.'
        
        return insights
    
    @staticmethod
    def _generate_recommendations(current_history, trend):
        """개선 추천사항 생성"""
        recommendations = []
        
        # 점수 기반 추천
        if current_history.contribution_score and current_history.contribution_score < 3.0:
            recommendations.append({
                'area': '기여도',
                'recommendation': 'Task 달성률 향상과 더 도전적인 목표 설정을 권장합니다.',
                'priority': 'high'
            })
        
        if current_history.expertise_score and current_history.expertise_score < 3.0:
            recommendations.append({
                'area': '전문성',
                'recommendation': '지속적인 학습과 기술 향상에 집중하시기 바랍니다.',
                'priority': 'high'
            })
        
        if current_history.impact_score and current_history.impact_score < 3.0:
            recommendations.append({
                'area': '영향력',
                'recommendation': '팀워크와 리더십 발휘 기회를 늘려보세요.',
                'priority': 'medium'
            })
        
        # 트렌드 기반 추천
        if trend.overall_trend == 'DECLINING':
            recommendations.append({
                'area': '전반적 성과',
                'recommendation': '성과 하락 원인을 분석하고 개선 계획을 수립하세요.',
                'priority': 'urgent'
            })
        elif trend.overall_trend == 'STABLE' and current_history.overall_score and current_history.overall_score >= 3.0:
            recommendations.append({
                'area': '성장 동력',
                'recommendation': '안정적인 성과를 바탕으로 새로운 도전을 시도해보세요.',
                'priority': 'low'
            })
        
        return recommendations
    
    @staticmethod
    def get_promotion_candidates(evaluation_period):
        """승급 후보자 조회"""
        from .models import EmployeeGrowthHistory
        
        candidates = EmployeeGrowthHistory.objects.filter(
            evaluation_period=evaluation_period,
            is_promotion_eligible=True
        ).select_related('employee', 'current_level').order_by(
            '-overall_score', '-consecutive_achievements'
        )
        
        return candidates
    
    @staticmethod
    def get_organization_growth_summary(evaluation_period):
        """조직 전체 성장 현황 요약"""
        from .models import EmployeeGrowthHistory, GrowthLevel
        from django.db.models import Count, Avg
        
        # 레벨별 분포
        level_distribution = EmployeeGrowthHistory.objects.filter(
            evaluation_period=evaluation_period
        ).values(
            'current_level__level', 'current_level__name'
        ).annotate(
            count=Count('id'),
            avg_score=Avg('overall_score')
        ).order_by('current_level__level')
        
        # 승급 현황
        promotion_stats = EmployeeGrowthHistory.objects.filter(
            evaluation_period=evaluation_period
        ).aggregate(
            total_employees=Count('id'),
            promotion_eligible=Count('id', filter=models.Q(is_promotion_eligible=True)),
            score_qualified=Count('id', filter=models.Q(meets_score_requirement=True))
        )
        
        # 성과 트렌드
        trend_distribution = EmployeeGrowthHistory.objects.filter(
            evaluation_period=evaluation_period
        ).values('employee__performance_trends__overall_trend').annotate(
            count=Count('id')
        )
        
        return {
            'level_distribution': list(level_distribution),
            'promotion_stats': promotion_stats,
            'trend_distribution': list(trend_distribution)
        }
    
    @staticmethod
    def validate_evaluation_completion(employee, evaluation_period) -> Dict[str, bool]:
        """
        평가 완료 상태 확인
        
        Returns:
            각 평가 항목별 완료 여부 딕셔너리
        """
        return {
            'contribution': ContributionEvaluation.objects.filter(
                employee=employee,
                evaluation_period=evaluation_period
            ).exists(),
            'expertise': ExpertiseEvaluation.objects.filter(
                employee=employee,
                evaluation_period=evaluation_period
            ).exists(),
            'impact': ImpactEvaluation.objects.filter(
                employee=employee,
                evaluation_period=evaluation_period
            ).exists(),
            'comprehensive': ComprehensiveEvaluation.objects.filter(
                employee=employee,
                evaluation_period=evaluation_period
            ).exists()
        }