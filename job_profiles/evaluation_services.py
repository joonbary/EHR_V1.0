"""
평가 결과 연동 서비스
Django 평가 모델과 매칭 엔진을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Avg, Count
from django.contrib.auth.models import User

from employees.models import Employee
from evaluations.models import (
    EvaluationPeriod, ComprehensiveEvaluation, 
    ContributionEvaluation, ExpertiseEvaluation, ImpactEvaluation
)
from .models import JobProfile, JobRole
from .evaluation_matcher import (
    match_profile_with_evaluation, 
    match_multiple_profiles_with_evaluation,
    analyze_promotion_readiness,
    EvaluationGradeConverter
)
from .services import JobProfileService


class EvaluationIntegratedService:
    """평가 결과를 통합한 직무 매칭 서비스"""
    
    @staticmethod
    def get_employee_profile_with_evaluation(
        employee: Employee, 
        evaluation_period: Optional[EvaluationPeriod] = None
    ) -> dict:
        """평가 결과가 포함된 직원 프로파일 생성"""
        
        # 기본 프로파일 가져오기
        profile = JobProfileService.get_employee_profile_dict(employee)
        
        # 평가 기간 설정 (없으면 최신 활성 기간)
        if not evaluation_period:
            evaluation_period = EvaluationPeriod.objects.filter(
                is_active=True
            ).first()
        
        if not evaluation_period:
            # 가장 최근 완료된 평가 기간
            evaluation_period = EvaluationPeriod.objects.filter(
                status='COMPLETED'
            ).order_by('-end_date').first()
        
        if evaluation_period:
            # 종합평가 조회
            comprehensive_eval = ComprehensiveEvaluation.objects.filter(
                employee=employee,
                evaluation_period=evaluation_period
            ).first()
            
            if comprehensive_eval:
                # 평가 결과 추가
                profile['recent_evaluation'] = {
                    'period': str(evaluation_period),
                    'professionalism': comprehensive_eval.expertise_grade or 'B',
                    'contribution': _get_contribution_level(
                        comprehensive_eval.contribution_evaluation
                    ),
                    'impact': _get_impact_level(
                        comprehensive_eval.impact_evaluation
                    ),
                    'overall_grade': comprehensive_eval.final_grade or 'B+',
                    'evaluation_date': comprehensive_eval.created_at.isoformat()
                }
                
                # 추가 평가 정보
                profile['evaluation_history'] = {
                    'total_evaluations': ComprehensiveEvaluation.objects.filter(
                        employee=employee
                    ).count(),
                    'average_grade': _calculate_average_grade(employee)
                }
        
        return profile
    
    @staticmethod
    def find_suitable_jobs_with_evaluation(
        employee: Employee,
        min_score: float = 60.0,
        top_n: int = 5,
        exclude_low_performers: bool = True,
        evaluation_weight: float = 0.3
    ) -> List[dict]:
        """평가 결과를 반영한 적합 직무 찾기"""
        
        # 평가 포함 프로파일 생성
        employee_profile = EvaluationIntegratedService.get_employee_profile_with_evaluation(
            employee
        )
        
        # 활성 직무 프로파일
        job_profiles = JobProfile.objects.filter(
            is_active=True
        ).select_related('job_role__job_type__category')
        
        # 직무 프로파일 변환
        job_dicts = [
            JobProfileService.get_job_profile_dict(jp)
            for jp in job_profiles
        ]
        
        # 평가 반영 매칭
        results = match_multiple_profiles_with_evaluation(
            job_dicts,
            employee_profile,
            top_n=top_n,
            min_score=min_score,
            exclude_low_performers=exclude_low_performers,
            evaluation_weight=evaluation_weight
        )
        
        # 추가 정보 연결
        for result in results:
            job_profile = next(
                (jp for jp in job_profiles if str(jp.id) == result['job_id']),
                None
            )
            if job_profile:
                result['job_profile_object'] = job_profile
                result['job_full_path'] = job_profile.job_role.full_path
                
                # 해당 직무의 평균 평가 등급 정보
                result['job_avg_evaluation'] = _get_job_average_evaluation(
                    job_profile.job_role
                )
        
        return results
    
    @staticmethod
    def analyze_team_promotion_readiness(
        department: str,
        target_level: str = 'MANAGER'
    ) -> dict:
        """부서별 승진 준비도 분석"""
        
        employees = Employee.objects.filter(
            department=department,
            employment_status='재직'
        ).exclude(position=target_level)
        
        # 목표 직급에 해당하는 직무들
        target_jobs = JobRole.objects.filter(
            Q(name__icontains=target_level) |
            Q(description__icontains=target_level)
        )
        
        promotion_candidates = []
        
        for employee in employees:
            # 직원별 프로파일 with 평가
            emp_profile = EvaluationIntegratedService.get_employee_profile_with_evaluation(
                employee
            )
            
            # 가장 적합한 상위 직무 찾기
            best_match = None
            best_score = 0
            
            for job_role in target_jobs:
                if hasattr(job_role, 'profile'):
                    job_dict = JobProfileService.get_job_profile_dict(
                        job_role.profile
                    )
                    match_result = match_profile_with_evaluation(
                        job_dict, 
                        emp_profile,
                        exclude_low_performers=False
                    )
                    
                    if match_result['match_score'] > best_score:
                        best_score = match_result['match_score']
                        best_match = {
                            'job_role': job_role,
                            'match_result': match_result
                        }
            
            if best_match and best_score >= 70:
                readiness = analyze_promotion_readiness(
                    emp_profile,
                    JobProfileService.get_job_profile_dict(best_match['job_role'].profile)
                )
                
                promotion_candidates.append({
                    'employee': employee,
                    'target_job': best_match['job_role'],
                    'match_score': best_score,
                    'readiness': readiness,
                    'recent_evaluation': emp_profile.get('recent_evaluation', {})
                })
        
        # 준비도별 분류
        ready_now = [c for c in promotion_candidates if c['readiness']['is_ready']]
        ready_soon = [c for c in promotion_candidates if 
                      not c['readiness']['is_ready'] and c['match_score'] >= 60]
        need_development = [c for c in promotion_candidates if c['match_score'] < 60]
        
        return {
            'department': department,
            'target_level': target_level,
            'total_employees': employees.count(),
            'promotion_candidates': {
                'ready_now': len(ready_now),
                'ready_soon': len(ready_soon),
                'need_development': len(need_development)
            },
            'top_candidates': sorted(
                ready_now, 
                key=lambda x: x['match_score'], 
                reverse=True
            )[:5],
            'recommendations': _generate_team_recommendations(
                ready_now, ready_soon, need_development
            )
        }
    
    @staticmethod
    def get_high_performer_opportunities(
        min_evaluation_grade: str = 'A'
    ) -> List[dict]:
        """고성과자를 위한 기회 찾기"""
        
        # 고성과자 찾기
        high_performers = []
        recent_evaluations = ComprehensiveEvaluation.objects.filter(
            final_grade__in=['S', 'A+', 'A'],
            evaluation_period__is_active=True
        ).select_related('employee', 'evaluation_period')
        
        opportunities = []
        
        for eval in recent_evaluations:
            employee = eval.employee
            emp_profile = EvaluationIntegratedService.get_employee_profile_with_evaluation(
                employee
            )
            
            # 현재보다 높은 수준의 직무 찾기
            suitable_jobs = EvaluationIntegratedService.find_suitable_jobs_with_evaluation(
                employee,
                min_score=70,
                top_n=3,
                exclude_low_performers=False,
                evaluation_weight=0.4  # 고성과자는 평가 가중치 높임
            )
            
            for job in suitable_jobs:
                # 현재 직무보다 상위인지 확인 (간단한 로직)
                if _is_higher_level_job(employee, job.get('job_profile_object')):
                    opportunities.append({
                        'employee': employee,
                        'current_evaluation': {
                            'grade': eval.final_grade,
                            'period': str(eval.evaluation_period)
                        },
                        'opportunity': job,
                        'recommendation_type': 'stretch_assignment' if job['match_score'] >= 85 
                                             else 'development_opportunity'
                    })
        
        return opportunities
    
    @staticmethod
    def create_evaluation_based_development_plan(
        employee: Employee,
        target_job_profile: JobProfile
    ) -> dict:
        """평가 결과 기반 개발 계획 수립"""
        
        # 평가 포함 프로파일
        emp_profile = EvaluationIntegratedService.get_employee_profile_with_evaluation(
            employee
        )
        job_dict = JobProfileService.get_job_profile_dict(target_job_profile)
        
        # 평가 반영 매칭
        match_result = match_profile_with_evaluation(
            job_dict, 
            emp_profile,
            exclude_low_performers=False
        )
        
        # 평가 결과 분석
        evaluation = emp_profile.get('recent_evaluation', {})
        
        development_plan = {
            'employee': employee,
            'target_job': target_job_profile,
            'current_match_score': match_result['match_score'],
            'evaluation_status': evaluation,
            'priority_areas': [],
            'timeline': []
        }
        
        # 평가 기반 우선순위 설정
        if evaluation.get('professionalism') in ['C', 'D']:
            development_plan['priority_areas'].append({
                'area': '전문성 향상',
                'reason': f"현재 전문성 등급 {evaluation.get('professionalism')}",
                'actions': [
                    '전문 교육 과정 이수',
                    '자격증 취득',
                    '멘토링 프로그램 참여'
                ]
            })
        
        if evaluation.get('contribution') in ['Bottom 20%', 'Bottom 10%']:
            development_plan['priority_areas'].append({
                'area': '업무 성과 개선',
                'reason': f"기여도 하위 {evaluation.get('contribution')}",
                'actions': [
                    '목표 설정 및 관리 강화',
                    '업무 효율성 개선',
                    '핵심 프로젝트 참여'
                ]
            })
        
        # 스킬 갭 기반 계획
        skill_gaps = match_result['gaps']
        if skill_gaps['basic_skills']:
            development_plan['priority_areas'].append({
                'area': '기본 역량 개발',
                'reason': f"{len(skill_gaps['basic_skills'])}개 기본 스킬 부족",
                'actions': [f"{skill} 역량 개발" for skill in skill_gaps['basic_skills'][:3]]
            })
        
        # 타임라인 생성
        if match_result['match_score'] >= 80:
            timeline_duration = "3-6개월"
        elif match_result['match_score'] >= 60:
            timeline_duration = "6-12개월"
        else:
            timeline_duration = "12-18개월"
        
        development_plan['timeline'] = [{
            'phase': '준비 기간',
            'duration': timeline_duration,
            'milestones': [
                '우선순위 영역 집중 개발',
                '중간 평가 및 피드백',
                '최종 준비도 평가'
            ]
        }]
        
        return development_plan


# 헬퍼 함수들
def _get_contribution_level(contribution_eval: Optional[ContributionEvaluation]) -> str:
    """기여도 평가를 레벨로 변환"""
    if not contribution_eval:
        return "Top 50~80%"
    
    # 달성률 기반 변환 (예시)
    if hasattr(contribution_eval, 'achievement_rate'):
        rate = contribution_eval.achievement_rate
        return EvaluationGradeConverter.percentage_to_contribution_level(rate)
    
    # 기본값
    if contribution_eval.is_achieved:
        return "Top 20~50%"
    else:
        return "Top 50~80%"


def _get_impact_level(impact_eval: Optional[ImpactEvaluation]) -> str:
    """영향력 평가를 레벨로 변환"""
    if not impact_eval:
        return "조직 내"
    
    # 영향력 범위 기반 변환
    if hasattr(impact_eval, 'impact_scope'):
        scope = impact_eval.impact_scope
        if scope == 'COMPANY':
            return "전사"
        elif scope == 'CROSS_TEAM':
            return "조직 간"
        elif scope == 'TEAM':
            return "조직 내"
    
    return "조직 내"


def _calculate_average_grade(employee: Employee) -> str:
    """직원의 평균 평가 등급 계산"""
    evaluations = ComprehensiveEvaluation.objects.filter(
        employee=employee,
        final_grade__isnull=False
    ).values_list('final_grade', flat=True)
    
    if not evaluations:
        return "N/A"
    
    # 간단한 평균 계산 (실제로는 더 정교한 로직 필요)
    grade_values = {'S': 5, 'A+': 4.5, 'A': 4, 'B+': 3.5, 'B': 3, 'C': 2, 'D': 1}
    total = sum(grade_values.get(grade, 3) for grade in evaluations)
    avg = total / len(evaluations)
    
    # 평균값을 등급으로 변환
    if avg >= 4.5:
        return 'A+'
    elif avg >= 4:
        return 'A'
    elif avg >= 3.5:
        return 'B+'
    elif avg >= 3:
        return 'B'
    else:
        return 'C'


def _get_job_average_evaluation(job_role: JobRole) -> dict:
    """특정 직무 수행자들의 평균 평가 정보"""
    # 해당 직무를 수행하는 직원들의 평가 통계
    employees_in_role = Employee.objects.filter(
        current_job_role=job_role  # 가정: Employee 모델에 current_job_role 필드 존재
    )
    
    if not employees_in_role.exists():
        return {'avg_grade': 'N/A', 'performer_count': 0}
    
    evaluations = ComprehensiveEvaluation.objects.filter(
        employee__in=employees_in_role,
        evaluation_period__is_active=True
    ).aggregate(
        avg_grade=Avg('final_grade'),  # 실제로는 등급을 숫자로 변환 필요
        count=Count('id')
    )
    
    return {
        'avg_grade': 'B+',  # 예시
        'performer_count': evaluations['count']
    }


def _is_higher_level_job(employee: Employee, job_profile: Optional[JobProfile]) -> bool:
    """현재보다 상위 직무인지 판단"""
    if not job_profile:
        return False
    
    # 간단한 로직: 직급 키워드 기반
    current_position = employee.position
    target_job_name = job_profile.job_role.name
    
    position_levels = ['STAFF', 'SENIOR', 'MANAGER', 'DIRECTOR', 'EXECUTIVE']
    
    # 현재와 목표 직급 레벨 비교
    current_level = next((i for i, level in enumerate(position_levels) 
                         if level in current_position.upper()), 0)
    target_level = next((i for i, level in enumerate(position_levels) 
                        if level in target_job_name.upper()), 0)
    
    return target_level > current_level


def _generate_team_recommendations(ready_now: list, ready_soon: list, 
                                 need_development: list) -> List[str]:
    """팀 레벨 추천사항 생성"""
    recommendations = []
    
    if len(ready_now) == 0:
        recommendations.append("승진 준비가 완료된 인원이 없음. 체계적인 육성 프로그램 필요")
    elif len(ready_now) > 3:
        recommendations.append(f"{len(ready_now)}명의 승진 준비 완료. 순차적 승진 계획 수립 필요")
    
    if len(ready_soon) > 0:
        recommendations.append(f"{len(ready_soon)}명이 단기 내 승진 가능. 집중 육성 프로그램 운영 권장")
    
    if len(need_development) > len(ready_now) + len(ready_soon):
        recommendations.append("장기 육성이 필요한 인원이 다수. 경력개발 체계 재검토 필요")
    
    return recommendations


# 사용 예시
if __name__ == "__main__":
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    # 테스트
    try:
        employee = Employee.objects.filter(
            employment_status='재직'
        ).first()
        
        if employee:
            # 평가 포함 적합 직무 찾기
            print(f"\n{employee.name}님의 평가 반영 적합 직무:")
            suitable_jobs = EvaluationIntegratedService.find_suitable_jobs_with_evaluation(
                employee,
                evaluation_weight=0.3
            )
            
            for job in suitable_jobs[:3]:
                print(f"\n- {job['job_full_path']}")
                print(f"  매칭 점수: {job['match_score']}%")
                if job.get('evaluation_applied'):
                    print(f"  평가 보너스: {job['evaluation_bonus']}점")
                    
    except Exception as e:
        print(f"테스트 중 오류: {e}")