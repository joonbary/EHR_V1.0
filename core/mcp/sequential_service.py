"""
MCP 시퀀셜싱킹 통합 서비스
복잡한 비즈니스 로직을 순차적으로 처리
"""
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from django.db import transaction

from core.exceptions import EHRBaseException


logger = logging.getLogger(__name__)


@dataclass
class ProcessStep:
    """프로세스 단계 정의"""
    name: str
    func: Callable
    description: str
    required: bool = True
    rollback_func: Optional[Callable] = None


class ProcessContext:
    """프로세스 실행 컨텍스트"""
    
    def __init__(self):
        self.data = {}
        self.results = {}
        self.errors = []
        self.completed_steps = []
        self.start_time = datetime.now()
    
    def set(self, key: str, value: Any):
        """데이터 설정"""
        self.data[key] = value
    
    def get(self, key: str, default=None):
        """데이터 조회"""
        return self.data.get(key, default)
    
    def add_result(self, step_name: str, result: Any):
        """단계 결과 추가"""
        self.results[step_name] = result
        self.completed_steps.append(step_name)
    
    def add_error(self, step_name: str, error: Exception):
        """에러 추가"""
        self.errors.append({
            'step': step_name,
            'error': str(error),
            'type': type(error).__name__
        })
    
    def is_successful(self) -> bool:
        """성공 여부"""
        return len(self.errors) == 0
    
    def get_summary(self) -> Dict:
        """실행 요약"""
        return {
            'total_steps': len(self.completed_steps),
            'successful': self.is_successful(),
            'errors': self.errors,
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'results': self.results
        }


class MCPSequentialService:
    """시퀀셜 프로세싱 서비스"""
    
    def __init__(self):
        self.processes = {}
        self._register_default_processes()
    
    def _register_default_processes(self):
        """기본 프로세스 등록"""
        # 평가 프로세스
        self.register_process('evaluation_complete', [
            ProcessStep(
                name='validate_data',
                func=self._validate_evaluation_data,
                description='평가 데이터 검증'
            ),
            ProcessStep(
                name='calculate_scores',
                func=self._calculate_evaluation_scores,
                description='평가 점수 계산'
            ),
            ProcessStep(
                name='apply_relative_evaluation',
                func=self._apply_relative_evaluation,
                description='상대평가 적용'
            ),
            ProcessStep(
                name='generate_insights',
                func=self._generate_evaluation_insights,
                description='평가 인사이트 생성'
            ),
            ProcessStep(
                name='save_results',
                func=self._save_evaluation_results,
                description='평가 결과 저장'
            )
        ])
        
        # 승진 프로세스
        self.register_process('promotion_analysis', [
            ProcessStep(
                name='collect_candidates',
                func=self._collect_promotion_candidates,
                description='승진 후보자 수집'
            ),
            ProcessStep(
                name='verify_eligibility',
                func=self._verify_promotion_eligibility,
                description='자격 요건 검증'
            ),
            ProcessStep(
                name='calculate_scores',
                func=self._calculate_promotion_scores,
                description='승진 점수 계산'
            ),
            ProcessStep(
                name='rank_candidates',
                func=self._rank_promotion_candidates,
                description='후보자 순위 결정'
            ),
            ProcessStep(
                name='generate_recommendations',
                func=self._generate_promotion_recommendations,
                description='승진 추천 생성'
            )
        ])
    
    def register_process(self, name: str, steps: List[ProcessStep]):
        """프로세스 등록"""
        self.processes[name] = steps
        logger.info(f"Process registered: {name} with {len(steps)} steps")
    
    def execute_process(self, process_name: str, initial_data: Dict = None) -> ProcessContext:
        """프로세스 실행"""
        if process_name not in self.processes:
            raise ValueError(f"Unknown process: {process_name}")
        
        context = ProcessContext()
        if initial_data:
            for key, value in initial_data.items():
                context.set(key, value)
        
        steps = self.processes[process_name]
        logger.info(f"Starting process: {process_name}")
        
        completed_steps = []
        
        try:
            with transaction.atomic():
                for step in steps:
                    try:
                        logger.info(f"Executing step: {step.name}")
                        result = step.func(context)
                        context.add_result(step.name, result)
                        completed_steps.append(step)
                        
                    except Exception as e:
                        logger.error(f"Step {step.name} failed: {str(e)}")
                        context.add_error(step.name, e)
                        
                        if step.required:
                            # 필수 단계 실패 시 롤백
                            self._rollback_steps(completed_steps, context)
                            raise
                
                if not context.is_successful():
                    raise EHRBaseException("프로세스 실행 중 오류 발생")
        
        except Exception as e:
            logger.error(f"Process {process_name} failed: {str(e)}")
            raise
        
        logger.info(f"Process {process_name} completed: {context.get_summary()}")
        return context
    
    def _rollback_steps(self, completed_steps: List[ProcessStep], context: ProcessContext):
        """완료된 단계 롤백"""
        for step in reversed(completed_steps):
            if step.rollback_func:
                try:
                    logger.info(f"Rolling back step: {step.name}")
                    step.rollback_func(context)
                except Exception as e:
                    logger.error(f"Rollback failed for {step.name}: {str(e)}")
    
    # 평가 프로세스 단계 구현
    def _validate_evaluation_data(self, context: ProcessContext) -> Dict:
        """평가 데이터 검증"""
        period_id = context.get('period_id')
        if not period_id:
            raise ValueError("평가 기간 ID가 필요합니다.")
        
        from evaluations.models import EvaluationPeriod, ComprehensiveEvaluation
        
        period = EvaluationPeriod.objects.get(id=period_id)
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period=period
        ).count()
        
        context.set('period', period)
        context.set('total_evaluations', evaluations)
        
        return {
            'period_name': period.name,
            'total_evaluations': evaluations,
            'validated': True
        }
    
    def _calculate_evaluation_scores(self, context: ProcessContext) -> Dict:
        """평가 점수 계산"""
        from evaluations.models import ComprehensiveEvaluation
        
        period = context.get('period')
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period=period
        ).select_related('employee')
        
        scores_calculated = 0
        for evaluation in evaluations:
            # 점수 계산 로직
            if not evaluation.total_score:
                # 3대 평가축 평균
                scores = []
                if evaluation.contribution_score:
                    scores.append(evaluation.contribution_score)
                if evaluation.expertise_score:
                    scores.append(evaluation.expertise_score)
                if evaluation.influence_score:
                    scores.append(evaluation.influence_score)
                
                if scores:
                    evaluation.total_score = sum(scores) / len(scores)
                    evaluation.save(update_fields=['total_score'])
                    scores_calculated += 1
        
        context.set('scores_calculated', scores_calculated)
        
        return {
            'scores_calculated': scores_calculated,
            'total_processed': evaluations.count()
        }
    
    def _apply_relative_evaluation(self, context: ProcessContext) -> Dict:
        """상대평가 적용"""
        from evaluations.models import ComprehensiveEvaluation
        import pandas as pd
        
        period = context.get('period')
        
        # 부서별로 그룹화하여 상대평가
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period=period
        ).select_related('employee').values(
            'id', 'employee__department', 'total_score'
        )
        
        df = pd.DataFrame(evaluations)
        
        grade_distribution = {
            'S': 0.10, 'A+': 0.10, 'A': 0.20,
            'B+': 0.20, 'B': 0.30, 'C': 0.10
        }
        
        updates = []
        
        for dept, group in df.groupby('employee__department'):
            # 점수 순으로 정렬
            group = group.sort_values('total_score', ascending=False)
            dept_size = len(group)
            
            # 등급별 인원 계산
            current_index = 0
            for grade, ratio in grade_distribution.items():
                count = int(dept_size * ratio)
                if count > 0:
                    eval_ids = group.iloc[current_index:current_index+count]['id'].tolist()
                    updates.extend([(eval_id, grade) for eval_id in eval_ids])
                    current_index += count
        
        # 일괄 업데이트
        for eval_id, grade in updates:
            ComprehensiveEvaluation.objects.filter(id=eval_id).update(
                manager_grade=grade
            )
        
        return {
            'total_graded': len(updates),
            'grade_distribution': dict(pd.DataFrame(updates)[1].value_counts())
        }
    
    def _generate_evaluation_insights(self, context: ProcessContext) -> Dict:
        """평가 인사이트 생성"""
        # 인사이트 생성 로직
        insights = {
            'top_performers': [],
            'improvement_needed': [],
            'department_rankings': []
        }
        
        # TODO: 실제 인사이트 생성 로직 구현
        
        context.set('insights', insights)
        return insights
    
    def _save_evaluation_results(self, context: ProcessContext) -> Dict:
        """평가 결과 저장"""
        # 최종 결과 저장
        return {
            'saved': True,
            'timestamp': datetime.now().isoformat()
        }
    
    # 승진 프로세스 단계 구현
    def _collect_promotion_candidates(self, context: ProcessContext) -> Dict:
        """승진 후보자 수집"""
        from employees.models import Employee
        
        # 승진 가능한 직원 조회
        candidates = Employee.objects.filter(
            is_active=True,
            growth_level__lt=6  # Level 6 미만
        ).select_related('user')
        
        context.set('candidates', list(candidates))
        
        return {
            'total_candidates': candidates.count(),
            'by_level': dict(candidates.values_list('growth_level').annotate(count=models.Count('id')))
        }
    
    def _verify_promotion_eligibility(self, context: ProcessContext) -> Dict:
        """승진 자격 검증"""
        candidates = context.get('candidates', [])
        eligible_candidates = []
        
        for candidate in candidates:
            # 자격 검증 로직
            is_eligible = self._check_promotion_requirements(candidate)
            if is_eligible:
                eligible_candidates.append(candidate)
        
        context.set('eligible_candidates', eligible_candidates)
        
        return {
            'total_eligible': len(eligible_candidates),
            'eligibility_rate': len(eligible_candidates) / len(candidates) if candidates else 0
        }
    
    def _check_promotion_requirements(self, employee) -> bool:
        """승진 요건 확인"""
        # TODO: 실제 요건 확인 로직 구현
        return True
    
    def _calculate_promotion_scores(self, context: ProcessContext) -> Dict:
        """승진 점수 계산"""
        eligible_candidates = context.get('eligible_candidates', [])
        scored_candidates = []
        
        for candidate in eligible_candidates:
            score = self._compute_promotion_score(candidate)
            scored_candidates.append({
                'employee': candidate,
                'score': score
            })
        
        context.set('scored_candidates', scored_candidates)
        
        return {
            'total_scored': len(scored_candidates),
            'average_score': sum(c['score'] for c in scored_candidates) / len(scored_candidates) if scored_candidates else 0
        }
    
    def _compute_promotion_score(self, employee) -> float:
        """승진 점수 계산"""
        # TODO: 실제 점수 계산 로직 구현
        return 75.0
    
    def _rank_promotion_candidates(self, context: ProcessContext) -> Dict:
        """후보자 순위 결정"""
        scored_candidates = context.get('scored_candidates', [])
        
        # 점수 기준 정렬
        ranked_candidates = sorted(
            scored_candidates,
            key=lambda x: x['score'],
            reverse=True
        )
        
        context.set('ranked_candidates', ranked_candidates)
        
        return {
            'total_ranked': len(ranked_candidates),
            'top_score': ranked_candidates[0]['score'] if ranked_candidates else 0
        }
    
    def _generate_promotion_recommendations(self, context: ProcessContext) -> Dict:
        """승진 추천 생성"""
        ranked_candidates = context.get('ranked_candidates', [])
        recommendations = []
        
        for rank, candidate_info in enumerate(ranked_candidates[:10], 1):
            recommendations.append({
                'rank': rank,
                'employee_id': candidate_info['employee'].id,
                'name': candidate_info['employee'].name,
                'score': candidate_info['score'],
                'recommendation': self._get_recommendation_text(candidate_info['score'])
            })
        
        context.set('recommendations', recommendations)
        
        return {
            'total_recommendations': len(recommendations),
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_recommendation_text(self, score: float) -> str:
        """추천 문구 생성"""
        if score >= 90:
            return "강력 추천 - 즉시 승진 가능"
        elif score >= 80:
            return "추천 - 승진 적합"
        elif score >= 70:
            return "조건부 추천 - 추가 검토 필요"
        else:
            return "보류 - 개발 필요"