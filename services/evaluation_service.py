"""
평가 관리 서비스
"""
from typing import Dict, List, Optional, Tuple
from django.db import transaction, models
from datetime import date, datetime
import logging
import pandas as pd

from evaluations.models import (
    EvaluationPeriod, ComprehensiveEvaluation,
    ContributionEvaluation, ExpertiseEvaluation, ImpactEvaluation,
    Task
)
from employees.models import Employee
from core.exceptions import ValidationError, EvaluationError
from core.validators import HRValidators
from core.mcp import MCPSequentialService, MCPTaskService


logger = logging.getLogger(__name__)


class EvaluationService:
    """평가 관리 비즈니스 로직"""
    
    def __init__(self):
        self.validator = HRValidators()
        self.sequential_service = MCPSequentialService()
        self.task_service = MCPTaskService()
        
        # 평가 가중치
        self.weights = {
            'contribution': 0.5,
            'expertise': 0.3,
            'impact': 0.2
        }
        
        # 등급별 분포
        self.grade_distribution = {
            'S': 0.10,
            'A+': 0.10,
            'A': 0.20,
            'B+': 0.20,
            'B': 0.30,
            'C': 0.10,
            'D': 0.00
        }
    
    @transaction.atomic
    def create_evaluation_period(
        self,
        name: str,
        start_date: date,
        end_date: date,
        period_type: str
    ) -> EvaluationPeriod:
        """평가 기간 생성"""
        # 날짜 검증
        if start_date >= end_date:
            raise ValidationError("시작일이 종료일보다 이전이어야 합니다.")
        
        # 중복 기간 확인
        overlapping = EvaluationPeriod.objects.filter(
            models.Q(start_date__lte=end_date) & models.Q(end_date__gte=start_date)
        ).exists()
        
        if overlapping:
            raise ValidationError("중복되는 평가 기간이 존재합니다.")
        
        period = EvaluationPeriod.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            period_type=period_type,
            is_active=True
        )
        
        # 모든 직원에 대한 평가 레코드 생성
        self._create_evaluation_records(period)
        
        logger.info(f"Evaluation period created: {period.name}")
        return period
    
    def _create_evaluation_records(self, period: EvaluationPeriod):
        """평가 레코드 일괄 생성"""
        active_employees = Employee.objects.filter(is_active=True)
        
        evaluations = []
        for employee in active_employees:
            evaluations.append(
                ComprehensiveEvaluation(
                    employee=employee,
                    evaluation_period=period,
                    evaluator=employee.manager or employee,
                    contribution_achieved=False,
                    expertise_achieved=False,
                    impact_achieved=False
                )
            )
        
        ComprehensiveEvaluation.objects.bulk_create(evaluations)
        logger.info(f"Created {len(evaluations)} evaluation records")
    
    def calculate_contribution_score(
        self,
        employee_id: int,
        period_id: int,
        tasks: List[Dict]
    ) -> float:
        """기여도 점수 계산"""
        from evaluations.models import CONTRIBUTION_SCORING_CHART
        
        total_weighted_score = 0
        total_weight = 0
        
        for task_data in tasks:
            # Scoring Chart에서 점수 조회
            base_score = CONTRIBUTION_SCORING_CHART.get(
                task_data['contribution_scope'], {}
            ).get(task_data['contribution_method'], 0)
            
            # 달성률에 따른 조정
            achievement_rate = task_data.get('achievement_rate', 0)
            if achievement_rate >= 100:
                adjusted_score = base_score
            elif achievement_rate >= 90:
                adjusted_score = base_score - 0.5
            elif achievement_rate >= 80:
                adjusted_score = base_score - 1.0
            elif achievement_rate >= 70:
                adjusted_score = base_score - 1.5
            else:
                adjusted_score = max(1.0, base_score - 2.0)
            
            weight = task_data.get('weight', 1.0)
            total_weighted_score += adjusted_score * weight
            total_weight += weight
        
        if total_weight > 0:
            final_score = total_weighted_score / total_weight
        else:
            final_score = 0
        
        return round(final_score, 2)
    
    def calculate_expertise_score(
        self,
        employee_id: int,
        period_id: int,
        checklist_scores: Dict[str, int]
    ) -> Tuple[float, bool]:
        """전문성 점수 계산"""
        # 10개 체크리스트 항목 평균
        total_score = sum(checklist_scores.values())
        avg_score = total_score / len(checklist_scores) if checklist_scores else 0
        
        # 달성 여부 (평균 3.0 이상)
        is_achieved = avg_score >= 3.0
        
        return round(avg_score, 2), is_achieved
    
    def calculate_impact_score(
        self,
        employee_id: int,
        period_id: int,
        impact_data: Dict
    ) -> Tuple[float, bool]:
        """영향력 점수 계산"""
        from evaluations.models import IMPACT_SCORING_CHART
        
        impact_scope = impact_data.get('impact_scope')
        values_practice = impact_data.get('core_values_practice')
        leadership_demo = impact_data.get('leadership_demonstration')
        
        # Scoring Chart에서 점수 조회
        values_score = IMPACT_SCORING_CHART.get(impact_scope, {}).get(values_practice, 0)
        leadership_score = IMPACT_SCORING_CHART.get(impact_scope, {}).get(leadership_demo, 0)
        
        # 평균 점수
        total_score = (values_score + leadership_score) / 2
        
        # 달성 여부 (평균 3.0 이상)
        is_achieved = total_score >= 3.0
        
        return round(total_score, 2), is_achieved
    
    @transaction.atomic
    def submit_comprehensive_evaluation(
        self,
        evaluation_id: int,
        data: Dict
    ) -> ComprehensiveEvaluation:
        """종합 평가 제출"""
        try:
            evaluation = ComprehensiveEvaluation.objects.get(id=evaluation_id)
            
            # 3대 평가축 점수 업데이트
            if 'contribution_score' in data:
                evaluation.contribution_score = data['contribution_score']
                evaluation.contribution_achieved = data.get('contribution_achieved', False)
            
            if 'expertise_score' in data:
                evaluation.expertise_score = data['expertise_score']
                evaluation.expertise_achieved = data.get('expertise_achieved', False)
            
            if 'influence_score' in data:
                evaluation.influence_score = data['influence_score']
                evaluation.impact_achieved = data.get('impact_achieved', False)
            
            # 총점 계산
            scores = []
            if evaluation.contribution_score:
                scores.append(evaluation.contribution_score * self.weights['contribution'])
            if evaluation.expertise_score:
                scores.append(evaluation.expertise_score * self.weights['expertise'])
            if evaluation.influence_score:
                scores.append(evaluation.influence_score * self.weights['impact'])
            
            evaluation.total_score = sum(scores) if scores else 0
            
            # 자동 등급 산출
            evaluation.manager_grade = self._calculate_auto_grade(evaluation)
            
            # 평가 의견
            if 'evaluation_comments' in data:
                evaluation.evaluation_comments = data['evaluation_comments']
            
            evaluation.save()
            
            logger.info(f"Evaluation submitted: {evaluation_id}")
            return evaluation
            
        except ComprehensiveEvaluation.DoesNotExist:
            raise EvaluationError(f"평가 ID {evaluation_id}를 찾을 수 없습니다.")
    
    def _calculate_auto_grade(self, evaluation: ComprehensiveEvaluation) -> str:
        """자동 등급 산출"""
        achieved_count = sum([
            evaluation.contribution_achieved,
            evaluation.expertise_achieved,
            evaluation.impact_achieved
        ])
        
        if achieved_count == 3:
            return 'S'
        elif achieved_count == 2:
            return 'A'
        elif achieved_count == 1:
            return 'B'
        else:
            return 'C'
    
    def process_relative_evaluation(self, period_id: int) -> Dict:
        """상대평가 처리"""
        # 시퀀셜 서비스로 복잡한 프로세스 처리
        context = self.sequential_service.execute_process(
            'evaluation_complete',
            {'period_id': period_id}
        )
        
        return context.get_summary()
    
    def get_evaluation_statistics(self, period_id: int) -> Dict:
        """평가 통계 조회"""
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period_id=period_id
        )
        
        total_count = evaluations.count()
        completed_count = evaluations.filter(is_completed=True).count()
        
        # 등급 분포
        grade_distribution = dict(
            evaluations.values_list('final_grade').annotate(
                count=models.Count('id')
            )
        )
        
        # 부서별 평균
        dept_avg = {}
        for dept in Employee.objects.values_list('department', flat=True).distinct():
            dept_evaluations = evaluations.filter(employee__department=dept)
            if dept_evaluations.exists():
                avg_score = dept_evaluations.aggregate(
                    avg=models.Avg('total_score')
                )['avg']
                dept_avg[dept] = round(avg_score, 2) if avg_score else 0
        
        return {
            'total_count': total_count,
            'completed_count': completed_count,
            'completion_rate': (completed_count / total_count * 100) if total_count > 0 else 0,
            'grade_distribution': grade_distribution,
            'department_averages': dept_avg,
            'top_performers': self._get_top_performers(evaluations, 10),
            'improvement_needed': self._get_improvement_needed(evaluations, 10)
        }
    
    def _get_top_performers(self, evaluations, limit: int = 10) -> List[Dict]:
        """상위 성과자 조회"""
        top_evaluations = evaluations.filter(
            total_score__isnull=False
        ).order_by('-total_score')[:limit]
        
        return [
            {
                'employee_id': eval.employee.id,
                'name': eval.employee.name,
                'department': eval.employee.department,
                'total_score': eval.total_score,
                'grade': eval.final_grade or eval.manager_grade
            }
            for eval in top_evaluations
        ]
    
    def _get_improvement_needed(self, evaluations, limit: int = 10) -> List[Dict]:
        """개선 필요 직원 조회"""
        low_evaluations = evaluations.filter(
            total_score__isnull=False
        ).order_by('total_score')[:limit]
        
        return [
            {
                'employee_id': eval.employee.id,
                'name': eval.employee.name,
                'department': eval.employee.department,
                'total_score': eval.total_score,
                'improvement_areas': self._identify_improvement_areas(eval)
            }
            for eval in low_evaluations
        ]
    
    def _identify_improvement_areas(self, evaluation: ComprehensiveEvaluation) -> List[str]:
        """개선 필요 영역 식별"""
        areas = []
        
        if not evaluation.contribution_achieved:
            areas.append("기여도")
        if not evaluation.expertise_achieved:
            areas.append("전문성")
        if not evaluation.impact_achieved:
            areas.append("영향력")
        
        return areas
    
    def export_evaluation_results(self, period_id: int) -> str:
        """평가 결과 내보내기"""
        # 비동기 작업으로 처리
        task_id = self.task_service.submit_task(
            'report_generation',
            {
                'report_type': 'evaluation_results',
                'period_id': period_id
            }
        )
        
        return task_id