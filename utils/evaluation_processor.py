"""
평가 처리 프로세서
시퀀셜싱킹 MCP를 활용한 복잡한 평가 로직 처리
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from django.db.models import Count, Avg, Q, F
from django.db import transaction
import pandas as pd
import numpy as np


class EvaluationProcessor:
    """평가 처리를 위한 핵심 프로세서"""
    
    def __init__(self):
        self.grade_distribution = {
            'S': 0.10,   # 10%
            'A+': 0.10,  # 10%
            'A': 0.20,   # 20%
            'B+': 0.20,  # 20%
            'B': 0.30,   # 30%
            'C': 0.10,   # 10%
            'D': 0.00    # 0% (예외적 경우)
        }
        
    def process_comprehensive_evaluation(self, evaluation_period_id: int):
        """종합 평가 처리 - 시퀀셜 프로세싱"""
        from evaluations.models import ComprehensiveEvaluation, EvaluationPeriod
        
        # 1단계: 평가 데이터 수집
        evaluation_data = self._collect_evaluation_data(evaluation_period_id)
        
        # 2단계: 평가 점수 계산
        calculated_scores = self._calculate_scores(evaluation_data)
        
        # 3단계: 상대평가 적용
        relative_grades = self._apply_relative_evaluation(calculated_scores)
        
        # 4단계: Calibration 준비
        calibration_data = self._prepare_calibration(relative_grades)
        
        # 5단계: 최종 결과 저장
        self._save_evaluation_results(calibration_data)
        
        return calibration_data
    
    def _collect_evaluation_data(self, period_id: int) -> Dict:
        """평가 데이터 수집"""
        from evaluations.models import (
            ComprehensiveEvaluation, ContributionEvaluation,
            ExpertiseEvaluation, ImpactEvaluation
        )
        
        evaluations = ComprehensiveEvaluation.objects.filter(
            evaluation_period_id=period_id
        ).select_related(
            'employee', 'evaluation_period'
        ).prefetch_related(
            'contribution_evaluations',
            'expertise_evaluations',
            'impact_evaluations'
        )
        
        data = []
        for eval in evaluations:
            # 기여도 평가 집계
            contribution_scores = []
            for contrib in eval.contribution_evaluations.all():
                contribution_scores.append({
                    'task_id': contrib.task_id,
                    'score': contrib.score,
                    'weight': contrib.task.weight if hasattr(contrib.task, 'weight') else 1.0,
                    'achievement_rate': contrib.achievement_rate
                })
            
            # 전문성 평가 집계
            expertise_score = 0
            expertise_evals = eval.expertise_evaluations.all()
            if expertise_evals:
                expertise_score = expertise_evals.first().total_score
            
            # 영향력 평가 집계
            impact_score = 0
            impact_evals = eval.impact_evaluations.all()
            if impact_evals:
                impact_score = impact_evals.first().total_score
            
            data.append({
                'evaluation_id': eval.id,
                'employee_id': eval.employee_id,
                'employee_name': eval.employee.name,
                'department': eval.employee.department,
                'position': eval.employee.position,
                'growth_level': eval.employee.growth_level,
                'contribution_scores': contribution_scores,
                'expertise_score': expertise_score,
                'impact_score': impact_score,
                'contribution_achieved': eval.contribution_achieved,
                'expertise_achieved': eval.expertise_achieved,
                'impact_achieved': eval.impact_achieved
            })
        
        return {
            'period_id': period_id,
            'evaluations': data,
            'total_count': len(data)
        }
    
    def _calculate_scores(self, evaluation_data: Dict) -> List[Dict]:
        """평가 점수 계산 및 정규화"""
        calculated = []
        
        for eval in evaluation_data['evaluations']:
            # 기여도 가중평균 계산
            contribution_weighted_sum = 0
            contribution_weight_sum = 0
            
            for contrib in eval['contribution_scores']:
                contribution_weighted_sum += contrib['score'] * contrib['weight']
                contribution_weight_sum += contrib['weight']
            
            contribution_avg = (
                contribution_weighted_sum / contribution_weight_sum 
                if contribution_weight_sum > 0 else 0
            )
            
            # 3대 평가축 종합점수
            total_score = (
                contribution_avg * 0.5 +  # 기여도 50%
                eval['expertise_score'] * 0.3 +  # 전문성 30%
                eval['impact_score'] * 0.2  # 영향력 20%
            )
            
            # 달성 개수 기반 등급
            achieved_count = sum([
                eval['contribution_achieved'],
                eval['expertise_achieved'],
                eval['impact_achieved']
            ])
            
            if achieved_count == 3:
                base_grade = 'S'
            elif achieved_count == 2:
                base_grade = 'A'
            elif achieved_count == 1:
                base_grade = 'B'
            else:
                base_grade = 'C'
            
            calculated.append({
                **eval,
                'contribution_avg': contribution_avg,
                'total_score': total_score,
                'achieved_count': achieved_count,
                'base_grade': base_grade,
                'normalized_score': 0  # 정규화 점수 (다음 단계에서 계산)
            })
        
        # 점수 정규화 (부서별, 직급별)
        df = pd.DataFrame(calculated)
        
        # 부서-직급 그룹별 정규화
        for (dept, position), group in df.groupby(['department', 'position']):
            if len(group) > 1:
                # Z-score 정규화
                mean_score = group['total_score'].mean()
                std_score = group['total_score'].std()
                if std_score > 0:
                    df.loc[group.index, 'normalized_score'] = (
                        (group['total_score'] - mean_score) / std_score
                    )
                else:
                    df.loc[group.index, 'normalized_score'] = 0
            else:
                df.loc[group.index, 'normalized_score'] = 0
        
        return df.to_dict('records')
    
    def _apply_relative_evaluation(self, calculated_scores: List[Dict]) -> List[Dict]:
        """상대평가 적용"""
        # 부서별로 그룹화
        df = pd.DataFrame(calculated_scores)
        
        results = []
        
        for department, dept_group in df.groupby('department'):
            # 부서 내에서 점수 순위 매기기
            dept_group = dept_group.sort_values(
                ['total_score', 'normalized_score'], 
                ascending=False
            ).reset_index(drop=True)
            
            dept_size = len(dept_group)
            
            # 등급별 인원 계산
            grade_counts = {
                'S': int(dept_size * self.grade_distribution['S']),
                'A+': int(dept_size * self.grade_distribution['A+']),
                'A': int(dept_size * self.grade_distribution['A']),
                'B+': int(dept_size * self.grade_distribution['B+']),
                'B': int(dept_size * self.grade_distribution['B']),
                'C': int(dept_size * self.grade_distribution['C']),
                'D': int(dept_size * self.grade_distribution['D'])
            }
            
            # 반올림으로 인한 차이 조정
            total_assigned = sum(grade_counts.values())
            if total_assigned < dept_size:
                grade_counts['B'] += dept_size - total_assigned
            
            # 등급 할당
            current_index = 0
            for grade, count in grade_counts.items():
                if count > 0:
                    dept_group.loc[current_index:current_index+count-1, 'relative_grade'] = grade
                    current_index += count
            
            # 기본 등급과 상대 등급 비교
            for idx, row in dept_group.iterrows():
                row_dict = row.to_dict()
                row_dict['grade_difference'] = self._calculate_grade_difference(
                    row_dict['base_grade'], 
                    row_dict['relative_grade']
                )
                results.append(row_dict)
        
        return results
    
    def _calculate_grade_difference(self, base_grade: str, relative_grade: str) -> int:
        """등급 차이 계산"""
        grade_values = {'S': 7, 'A+': 6, 'A': 5, 'B+': 4, 'B': 3, 'C': 2, 'D': 1}
        base_value = grade_values.get(base_grade, 3)
        relative_value = grade_values.get(relative_grade, 3)
        return relative_value - base_value
    
    def _prepare_calibration(self, relative_grades: List[Dict]) -> Dict:
        """Calibration 준비 데이터 생성"""
        # 조정이 필요한 케이스 식별
        adjustment_needed = []
        
        for eval in relative_grades:
            # 기본 등급과 상대 등급의 차이가 2등급 이상인 경우
            if abs(eval['grade_difference']) >= 2:
                adjustment_needed.append({
                    **eval,
                    'adjustment_reason': self._get_adjustment_reason(eval),
                    'recommended_grade': self._get_recommended_grade(eval)
                })
        
        # 부서별 분포 통계
        df = pd.DataFrame(relative_grades)
        dept_stats = []
        
        for dept, group in df.groupby('department'):
            grade_dist = group['relative_grade'].value_counts().to_dict()
            dept_stats.append({
                'department': dept,
                'total_count': len(group),
                'grade_distribution': grade_dist,
                'avg_score': group['total_score'].mean(),
                'std_score': group['total_score'].std()
            })
        
        return {
            'evaluations': relative_grades,
            'adjustment_needed': adjustment_needed,
            'department_stats': dept_stats,
            'calibration_date': datetime.now(),
            'total_evaluations': len(relative_grades)
        }
    
    def _get_adjustment_reason(self, eval: Dict) -> str:
        """조정 사유 생성"""
        reasons = []
        
        if eval['grade_difference'] > 0:
            reasons.append(f"상대평가로 {eval['base_grade']}에서 {eval['relative_grade']}로 상향")
        elif eval['grade_difference'] < 0:
            reasons.append(f"상대평가로 {eval['base_grade']}에서 {eval['relative_grade']}로 하향")
        
        if eval['achieved_count'] == 3 and eval['relative_grade'] not in ['S', 'A+']:
            reasons.append("3대 평가축 모두 달성했으나 상대평가로 조정됨")
        
        if eval['normalized_score'] > 1.5:
            reasons.append("부서 내 상위 성과자")
        elif eval['normalized_score'] < -1.5:
            reasons.append("부서 내 하위 성과자")
        
        return "; ".join(reasons)
    
    def _get_recommended_grade(self, eval: Dict) -> str:
        """권장 등급 계산"""
        # 기본 등급과 상대 등급의 중간값 제안
        if abs(eval['grade_difference']) >= 2:
            grade_values = {'S': 7, 'A+': 6, 'A': 5, 'B+': 4, 'B': 3, 'C': 2, 'D': 1}
            reverse_values = {v: k for k, v in grade_values.items()}
            
            base_value = grade_values.get(eval['base_grade'], 3)
            relative_value = grade_values.get(eval['relative_grade'], 3)
            
            # 중간값 계산
            middle_value = (base_value + relative_value) // 2
            return reverse_values.get(middle_value, eval['relative_grade'])
        
        return eval['relative_grade']
    
    @transaction.atomic
    def _save_evaluation_results(self, calibration_data: Dict):
        """평가 결과 저장"""
        from evaluations.models import ComprehensiveEvaluation
        
        for eval_data in calibration_data['evaluations']:
            try:
                evaluation = ComprehensiveEvaluation.objects.get(
                    id=eval_data['evaluation_id']
                )
                
                # 계산된 점수 업데이트
                evaluation.contribution_score = eval_data['contribution_avg']
                evaluation.total_score = eval_data['total_score']
                
                # 상대평가 등급 저장 (1차 평가로)
                evaluation.manager_grade = eval_data['relative_grade']
                
                # Calibration 대상인 경우 표시
                if eval_data['evaluation_id'] in [
                    adj['evaluation_id'] for adj in calibration_data['adjustment_needed']
                ]:
                    evaluation.calibration_comments = (
                        f"상대평가 적용: {eval_data.get('adjustment_reason', '')}\n"
                        f"권장등급: {eval_data.get('recommended_grade', '')}"
                    )
                
                evaluation.save()
                
            except ComprehensiveEvaluation.DoesNotExist:
                print(f"평가 ID {eval_data['evaluation_id']} 를 찾을 수 없습니다.")
                continue


class CalibrationSession:
    """Calibration 세션 관리"""
    
    def __init__(self, evaluation_period_id: int):
        self.evaluation_period_id = evaluation_period_id
        self.session_data = {}
        self.participants = []
        self.decisions = []
        
    def start_session(self, participants: List[int]):
        """Calibration 세션 시작"""
        from django.contrib.auth.models import User
        
        self.participants = User.objects.filter(id__in=participants)
        self.session_data['start_time'] = datetime.now()
        self.session_data['status'] = 'in_progress'
        
        # 평가 데이터 로드
        processor = EvaluationProcessor()
        self.session_data['calibration_data'] = processor.process_comprehensive_evaluation(
            self.evaluation_period_id
        )
        
        return self.session_data
    
    def review_case(self, evaluation_id: int, decision: Dict):
        """개별 케이스 검토"""
        decision_record = {
            'evaluation_id': evaluation_id,
            'timestamp': datetime.now(),
            'participants': [p.id for p in self.participants],
            'original_grade': decision.get('original_grade'),
            'recommended_grade': decision.get('recommended_grade'),
            'final_grade': decision.get('final_grade'),
            'rationale': decision.get('rationale'),
            'unanimous': decision.get('unanimous', True)
        }
        
        self.decisions.append(decision_record)
        
        # 실시간 업데이트
        self._update_evaluation(evaluation_id, decision)
        
        return decision_record
    
    def _update_evaluation(self, evaluation_id: int, decision: Dict):
        """평가 업데이트"""
        from evaluations.models import ComprehensiveEvaluation
        
        try:
            evaluation = ComprehensiveEvaluation.objects.get(id=evaluation_id)
            evaluation.final_grade = decision['final_grade']
            evaluation.calibration_comments = (
                f"{evaluation.calibration_comments or ''}\n"
                f"Calibration 결정: {decision['rationale']}\n"
                f"참여자: {len(self.participants)}명"
            )
            evaluation.save()
        except ComprehensiveEvaluation.DoesNotExist:
            pass
    
    def finalize_session(self):
        """세션 종료"""
        self.session_data['end_time'] = datetime.now()
        self.session_data['status'] = 'completed'
        self.session_data['total_decisions'] = len(self.decisions)
        
        # 세션 결과 저장
        self._save_session_results()
        
        return self.session_data
    
    def _save_session_results(self):
        """세션 결과 저장"""
        # 여기에 세션 결과를 데이터베이스에 저장하는 로직 추가
        pass


class PerformanceTrendAnalyzer:
    """성과 트렌드 분석기"""
    
    def analyze_individual_trend(self, employee_id: int, periods: int = 4):
        """개인 성과 트렌드 분석"""
        from evaluations.models import ComprehensiveEvaluation
        
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee_id=employee_id
        ).order_by('-evaluation_period__end_date')[:periods]
        
        if not evaluations:
            return None
        
        # 트렌드 데이터 수집
        trend_data = []
        for eval in evaluations:
            trend_data.append({
                'period': eval.evaluation_period.name,
                'contribution_score': eval.contribution_score,
                'expertise_score': eval.expertise_score,
                'influence_score': eval.influence_score,
                'total_score': eval.total_score,
                'final_grade': eval.final_grade
            })
        
        # 트렌드 분석
        df = pd.DataFrame(trend_data)
        
        analysis = {
            'employee_id': employee_id,
            'evaluation_count': len(trend_data),
            'latest_grade': trend_data[0]['final_grade'] if trend_data else None,
            'average_total_score': df['total_score'].mean(),
            'score_trend': self._calculate_trend(df['total_score']),
            'contribution_trend': self._calculate_trend(df['contribution_score']),
            'expertise_trend': self._calculate_trend(df['expertise_score']),
            'influence_trend': self._calculate_trend(df['influence_score']),
            'consistency': df['total_score'].std(),
            'growth_potential': self._assess_growth_potential(df)
        }
        
        return analysis
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """트렌드 계산"""
        if len(series) < 2:
            return 'insufficient_data'
        
        # 선형 회귀로 트렌드 계산
        x = np.arange(len(series))
        y = series.values
        
        # NaN 값 처리
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return 'insufficient_data'
        
        x = x[mask]
        y = y[mask]
        
        # 기울기 계산
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _assess_growth_potential(self, df: pd.DataFrame) -> str:
        """성장 잠재력 평가"""
        if len(df) < 2:
            return 'unknown'
        
        # 최근 성과 향상도
        recent_improvement = df.iloc[0]['total_score'] - df.iloc[-1]['total_score']
        
        # 일관성 (표준편차가 낮을수록 안정적)
        consistency = df['total_score'].std()
        
        # 평균 점수
        avg_score = df['total_score'].mean()
        
        if recent_improvement > 0.5 and consistency < 0.5:
            return 'high'
        elif avg_score > 3.5 and consistency < 0.3:
            return 'stable_high'
        elif recent_improvement > 0.3:
            return 'moderate'
        else:
            return 'low'
    
    def analyze_department_performance(self, department: str, period_id: int):
        """부서 성과 분석"""
        from evaluations.models import ComprehensiveEvaluation
        from employees.models import Employee
        
        # 부서 직원들의 평가 데이터
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee__department=department,
            evaluation_period_id=period_id
        ).select_related('employee')
        
        if not evaluations:
            return None
        
        # 데이터 수집
        data = []
        for eval in evaluations:
            data.append({
                'employee_id': eval.employee_id,
                'name': eval.employee.name,
                'position': eval.employee.position,
                'growth_level': eval.employee.growth_level,
                'total_score': eval.total_score,
                'final_grade': eval.final_grade
            })
        
        df = pd.DataFrame(data)
        
        # 부서 분석
        analysis = {
            'department': department,
            'total_employees': len(df),
            'average_score': df['total_score'].mean(),
            'score_std': df['total_score'].std(),
            'grade_distribution': df['final_grade'].value_counts().to_dict(),
            'top_performers': df.nlargest(5, 'total_score')[['name', 'total_score']].to_dict('records'),
            'position_performance': df.groupby('position')['total_score'].agg(['mean', 'count']).to_dict(),
            'level_performance': df.groupby('growth_level')['total_score'].agg(['mean', 'count']).to_dict()
        }
        
        return analysis