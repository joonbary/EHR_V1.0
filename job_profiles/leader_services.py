"""
리더 추천 Django 서비스
리더 추천 엔진과 Django 모델을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg, F
from django.contrib.auth.models import User
from collections import defaultdict
import json

from employees.models import Employee
from evaluations.models import (
    EvaluationPeriod, ComprehensiveEvaluation
)
from .models import JobProfile, JobRole
from .leader_recommender import (
    recommend_leader_candidates,
    analyze_organization_talent_pool,
    LeaderRecommender
)
from .services import JobProfileService
from .evaluation_services import EvaluationIntegratedService
from .recommendation_comment_generator import generate_recommendation_comment


class LeaderRecommendationService:
    """리더 추천 서비스"""
    
    def __init__(self):
        self.recommender = LeaderRecommender()
        
    def find_leader_candidates(
        self,
        target_job_profile: JobProfile,
        department: Optional[str] = None,
        min_evaluation_grade: str = "B+",
        min_growth_level: str = "Lv.3",
        top_n: int = 10,
        exclude_low_performers: bool = True
    ) -> List[Dict]:
        """
        특정 직무에 대한 리더 후보 찾기
        
        Args:
            target_job_profile: 목표 리더 직무
            department: 특정 부서로 제한 (None이면 전체)
            min_evaluation_grade: 최소 평가 등급
            min_growth_level: 최소 성장 레벨
            top_n: 추천 인원 수
            exclude_low_performers: 저성과자 제외 여부
        """
        # 대상 직무 정보 변환
        target_job = self._convert_job_profile_to_dict(target_job_profile)
        
        # 후보 직원 조회
        employee_query = Employee.objects.filter(
            employment_status='재직'
        )
        
        if department:
            employee_query = employee_query.filter(department=department)
        
        # 직원 정보 변환
        all_employees = []
        for employee in employee_query:
            emp_dict = self._convert_employee_to_dict(employee)
            if emp_dict:
                all_employees.append(emp_dict)
        
        # 리더 후보 추천
        candidates = recommend_leader_candidates(
            target_job=target_job,
            all_employees=all_employees,
            min_evaluation_grade=min_evaluation_grade,
            min_growth_level=min_growth_level,
            top_n=top_n,
            exclude_low_performers=exclude_low_performers
        )
        
        # Django 모델과 연결
        for candidate in candidates:
            emp_obj = Employee.objects.get(id=candidate['employee_id'])
            candidate['employee_object'] = emp_obj
            candidate['photo_url'] = self._get_employee_photo_url(emp_obj)
            candidate['current_projects'] = self._get_current_projects(emp_obj)
            
        return candidates
    
    def get_succession_candidates(
        self,
        retiring_position: str,
        months_ahead: int = 12
    ) -> Dict:
        """
        승계 계획을 위한 후보자 분석
        
        Args:
            retiring_position: 퇴직 예정 직위
            months_ahead: 승계 준비 기간 (개월)
        """
        # 해당 직위의 직무 프로파일 찾기
        target_profiles = JobProfile.objects.filter(
            Q(job_role__name__icontains=retiring_position) |
            Q(job_role__description__icontains=retiring_position),
            is_active=True
        )
        
        if not target_profiles.exists():
            return {
                'status': 'error',
                'message': f'{retiring_position} 직무를 찾을 수 없습니다.'
            }
        
        target_profile = target_profiles.first()
        
        # 승계 후보 찾기 (높은 기준 적용)
        candidates = self.find_leader_candidates(
            target_job_profile=target_profile,
            min_evaluation_grade="A",
            min_growth_level="Lv.4",
            top_n=5,
            exclude_low_performers=True
        )
        
        # 승계 준비도 분석
        succession_plan = {
            'retiring_position': retiring_position,
            'target_job_profile': target_profile,
            'months_ahead': months_ahead,
            'candidates': [],
            'timeline': []
        }
        
        for candidate in candidates:
            # 준비 기간 계산
            readiness_score = candidate['match_score']
            
            if readiness_score >= 90:
                preparation_months = 3  # 즉시 가능
            elif readiness_score >= 80:
                preparation_months = 6  # 단기 준비
            elif readiness_score >= 70:
                preparation_months = 12  # 중기 준비
            else:
                preparation_months = 18  # 장기 준비
            
            candidate_info = {
                'employee': candidate['employee_object'],
                'readiness_score': readiness_score,
                'preparation_months': preparation_months,
                'is_ready': preparation_months <= months_ahead,
                'development_plan': self._create_succession_development_plan(
                    candidate,
                    target_profile,
                    months_ahead
                )
            }
            
            succession_plan['candidates'].append(candidate_info)
        
        # 타임라인 생성
        succession_plan['timeline'] = self._create_succession_timeline(
            succession_plan['candidates'],
            months_ahead
        )
        
        return succession_plan
    
    def analyze_leadership_pipeline(
        self,
        organization_level: str = 'company'  # 'company', 'division', 'department'
    ) -> Dict:
        """
        리더십 파이프라인 분석
        
        Returns:
            조직의 리더십 파이프라인 현황
        """
        pipeline_analysis = {
            'level': organization_level,
            'timestamp': datetime.now().isoformat(),
            'leadership_levels': {},
            'talent_flow': {},
            'risk_areas': [],
            'recommendations': []
        }
        
        # 리더십 레벨 정의
        leadership_levels = [
            {'name': '팀원', 'positions': ['사원', '대리']},
            {'name': '팀리더', 'positions': ['과장', '차장']},
            {'name': '팀장', 'positions': ['팀장', '부장']},
            {'name': '임원', 'positions': ['이사', '상무', '전무', '부사장']}
        ]
        
        # 각 레벨별 인원 및 준비도 분석
        for level in leadership_levels:
            level_employees = Employee.objects.filter(
                employment_status='재직',
                position__in=level['positions']
            )
            
            # 다음 레벨 준비자 수 계산
            next_level_ready = 0
            high_potentials = 0
            
            for emp in level_employees:
                # 최근 평가 확인
                recent_eval = self._get_recent_evaluation(emp)
                if recent_eval and recent_eval.final_grade in ['S', 'A+', 'A']:
                    high_potentials += 1
                    
                    # 성장 레벨 확인 (간단한 로직)
                    if self._get_growth_level(emp) >= 3:
                        next_level_ready += 1
            
            pipeline_analysis['leadership_levels'][level['name']] = {
                'total_count': level_employees.count(),
                'high_potentials': high_potentials,
                'next_level_ready': next_level_ready,
                'readiness_ratio': next_level_ready / max(level_employees.count(), 1)
            }
        
        # 인재 흐름 분석
        pipeline_analysis['talent_flow'] = self._analyze_talent_flow()
        
        # 리스크 영역 식별
        for level_name, stats in pipeline_analysis['leadership_levels'].items():
            if stats['readiness_ratio'] < 0.2:
                pipeline_analysis['risk_areas'].append({
                    'level': level_name,
                    'risk': '후계자 부족',
                    'readiness_ratio': stats['readiness_ratio']
                })
        
        # 추천사항 생성
        pipeline_analysis['recommendations'] = self._generate_pipeline_recommendations(
            pipeline_analysis
        )
        
        return pipeline_analysis
    
    def create_talent_pool_report(
        self,
        job_categories: List[str] = None
    ) -> Dict:
        """
        인재 풀 종합 리포트 생성
        
        Args:
            job_categories: 분석할 직무 카테고리 (None이면 전체)
        """
        # 직무 프로파일 조회
        job_profiles_query = JobProfile.objects.filter(is_active=True)
        
        if job_categories:
            job_profiles_query = job_profiles_query.filter(
                job_role__job_type__category__name__in=job_categories
            )
        
        job_profiles = list(job_profiles_query)
        
        # 전체 직원 데이터
        all_employees = Employee.objects.filter(
            employment_status='재직'
        )
        
        # 직원 데이터 변환
        employee_dicts = []
        for emp in all_employees:
            emp_dict = self._convert_employee_to_dict(emp)
            if emp_dict:
                employee_dicts.append(emp_dict)
        
        # 직무 프로파일 변환
        job_profile_dicts = [
            self._convert_job_profile_to_dict(jp)
            for jp in job_profiles
        ]
        
        # 인재 풀 분석
        talent_pool = analyze_organization_talent_pool(
            all_employees=employee_dicts,
            job_profiles=job_profile_dicts
        )
        
        # 리포트 생성
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_employees': len(all_employees),
                'total_departments': talent_pool['total_departments'],
                'leadership_ready': talent_pool['organization_stats']['total_team_lead_candidates'],
                'high_potentials': talent_pool['organization_stats']['total_high_potentials']
            },
            'department_analysis': {},
            'job_category_analysis': {},
            'recommendations': []
        }
        
        # 부서별 상세 분석
        for dept, details in talent_pool['department_details'].items():
            dept_employees = all_employees.filter(department=dept)
            
            report['department_analysis'][dept] = {
                'total': details['total_employees'],
                'leadership_candidates': len(details['team_lead_candidates']),
                'high_potentials': len(details['high_potentials']),
                'avg_tenure': dept_employees.aggregate(
                    avg=Avg(F('employment_date'))
                )['avg'],
                'top_candidates': details['team_lead_candidates'][:3],
                'critical_skills': details['top_skills'][:5]
            }
        
        # 직무 카테고리별 분석
        if job_categories:
            for category in job_categories:
                category_profiles = [
                    jp for jp in job_profiles 
                    if jp.job_role.job_type.category.name == category
                ]
                
                category_ready = 0
                for profile in category_profiles:
                    candidates = self.find_leader_candidates(
                        target_job_profile=profile,
                        top_n=100,  # 전체 적격자 수 파악
                        exclude_low_performers=True
                    )
                    category_ready += len(candidates)
                
                report['job_category_analysis'][category] = {
                    'total_positions': len(category_profiles),
                    'qualified_candidates': category_ready,
                    'fill_ratio': category_ready / max(len(category_profiles), 1)
                }
        
        # 종합 추천사항
        report['recommendations'] = self._generate_talent_pool_recommendations(report)
        
        return report
    
    def _convert_job_profile_to_dict(self, job_profile: JobProfile) -> dict:
        """JobProfile 모델을 딕셔너리로 변환"""
        job_dict = JobProfileService.get_job_profile_dict(job_profile)
        
        # 리더 추천에 필요한 추가 정보
        job_dict['evaluation_standard'] = {
            'overall': 'B+',  # 기본값
            'professionalism': 'A'
        }
        
        # 직급에 따른 레벨 요구사항
        if '팀장' in job_dict['job_name']:
            job_dict['min_required_level'] = 'Lv.3'
        elif '본부장' in job_dict['job_name'] or '센터장' in job_dict['job_name']:
            job_dict['min_required_level'] = 'Lv.4'
        elif '임원' in job_dict['job_name']:
            job_dict['min_required_level'] = 'Lv.5'
        else:
            job_dict['min_required_level'] = 'Lv.2'
        
        return job_dict
    
    def _convert_employee_to_dict(self, employee: Employee) -> Optional[dict]:
        """Employee 모델을 딕셔너리로 변환"""
        try:
            # 기본 정보
            emp_dict = {
                'employee_id': str(employee.id),
                'name': employee.name,
                'position': employee.position,
                'department': employee.department,
                'career_years': self._calculate_career_years(employee),
                'skills': [],
                'certifications': []
            }
            
            # 성장 레벨 (position 기반 추정)
            emp_dict['level'] = self._estimate_growth_level(employee)
            
            # 평가 정보
            recent_eval = self._get_recent_evaluation(employee)
            if recent_eval:
                emp_dict['recent_evaluation'] = {
                    'overall_grade': recent_eval.final_grade,
                    'professionalism': recent_eval.expertise_grade,
                    'contribution': self._get_contribution_level(recent_eval),
                    'impact': self._get_impact_level(recent_eval)
                }
                
                # 최근 평가 이력
                recent_evals = ComprehensiveEvaluation.objects.filter(
                    employee=employee
                ).order_by('-created_at')[:4]
                
                emp_dict['recent_evaluations'] = [
                    {
                        'overall_grade': e.final_grade,
                        'professionalism': e.expertise_grade
                    }
                    for e in recent_evals
                ]
            
            # 리더십 경험 (position에서 추정)
            leadership_exp = self._estimate_leadership_experience(employee)
            if leadership_exp:
                emp_dict['leadership_experience'] = leadership_exp
            
            # 스킬 (더미 데이터 - 실제로는 별도 모델 필요)
            emp_dict['skills'] = self._get_employee_skills(employee)
            
            # 자격증 (더미 데이터)
            emp_dict['certifications'] = self._get_employee_certifications(employee)
            
            return emp_dict
            
        except Exception as e:
            print(f"Error converting employee {employee.id}: {e}")
            return None
    
    def _calculate_career_years(self, employee: Employee) -> int:
        """경력 년수 계산"""
        if employee.employment_date:
            years = (datetime.now().date() - employee.employment_date).days / 365
            return int(years)
        return 0
    
    def _estimate_growth_level(self, employee: Employee) -> str:
        """직급 기반 성장 레벨 추정"""
        position = employee.position
        
        if 'STAFF' in position or '사원' in position:
            return 'Lv.1'
        elif 'SENIOR' in position or '대리' in position:
            return 'Lv.2'
        elif 'MANAGER' in position or '과장' in position:
            return 'Lv.3'
        elif 'DIRECTOR' in position or '차장' in position or '부장' in position:
            return 'Lv.4'
        elif 'EXECUTIVE' in position or '임원' in position:
            return 'Lv.5'
        
        return 'Lv.2'  # 기본값
    
    def _get_growth_level(self, employee: Employee) -> int:
        """성장 레벨을 숫자로 반환"""
        level_str = self._estimate_growth_level(employee)
        return int(level_str.replace('Lv.', ''))
    
    def _estimate_leadership_experience(self, employee: Employee) -> Optional[dict]:
        """리더십 경험 추정"""
        position = employee.position.lower()
        
        if '팀장' in position or 'lead' in position:
            return {
                'years': min(5, self._calculate_career_years(employee) - 5),
                'type': '팀장'
            }
        elif '파트장' in position or 'manager' in position:
            return {
                'years': min(3, self._calculate_career_years(employee) - 3),
                'type': '파트장'
            }
        elif self._calculate_career_years(employee) > 7:
            return {
                'years': 1,
                'type': 'TF 리더'
            }
        
        return None
    
    def _get_recent_evaluation(self, employee: Employee):
        """최근 평가 조회"""
        return ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at').first()
    
    def _get_contribution_level(self, evaluation) -> str:
        """기여도 레벨 변환"""
        # 실제로는 평가 모델의 필드에 따라 구현
        return "Top 20%"
    
    def _get_impact_level(self, evaluation) -> str:
        """영향력 레벨 변환"""
        # 실제로는 평가 모델의 필드에 따라 구현
        return "조직 간"
    
    def _get_employee_skills(self, employee: Employee) -> List[str]:
        """직원 스킬 조회"""
        # 부서와 직급 기반 기본 스킬 설정
        skills = []
        
        dept_skills = {
            'HR': ['인사관리', '조직개발', '채용', '교육기획'],
            'IT': ['프로젝트관리', '시스템설계', '개발', '데이터분석'],
            'Finance': ['재무분석', '예산관리', '리스크관리', '투자분석'],
            'Marketing': ['마케팅전략', '브랜드관리', '디지털마케팅', '시장분석'],
            'Sales': ['영업전략', '고객관리', '협상', '시장개척']
        }
        
        # 부서별 기본 스킬
        if employee.department in dept_skills:
            skills.extend(dept_skills[employee.department][:2])
        
        # 직급별 추가 스킬
        if '과장' in employee.position or '차장' in employee.position:
            skills.extend(['프로젝트관리', '팀워크'])
        elif '부장' in employee.position or '팀장' in employee.position:
            skills.extend(['조직관리', '성과관리', '리더십'])
        
        return skills
    
    def _get_employee_certifications(self, employee: Employee) -> List[str]:
        """직원 자격증 조회"""
        # 더미 데이터
        dept_certs = {
            'HR': ['PHR', '노무사'],
            'IT': ['PMP', 'AWS 인증'],
            'Finance': ['CPA', 'CFA'],
            'Marketing': ['구글 애널리틱스', '디지털마케팅'],
            'Sales': ['영업관리사', '국제무역사']
        }
        
        if employee.department in dept_certs:
            # 경력에 따라 자격증 수 조정
            years = self._calculate_career_years(employee)
            if years > 10:
                return dept_certs[employee.department]
            elif years > 5:
                return dept_certs[employee.department][:1]
        
        return []
    
    def _get_employee_photo_url(self, employee: Employee) -> Optional[str]:
        """직원 사진 URL"""
        # 실제로는 프로필 사진 모델에서 조회
        return None
    
    def _get_current_projects(self, employee: Employee) -> List[str]:
        """현재 진행 중인 프로젝트"""
        # 실제로는 프로젝트 할당 모델에서 조회
        return []
    
    def _create_succession_development_plan(
        self,
        candidate: dict,
        target_profile: JobProfile,
        months_ahead: int
    ) -> dict:
        """승계 후보자 개발 계획"""
        missing_skills = candidate.get('missing_skills', [])
        
        plan = {
            'duration_months': min(months_ahead, 12),
            'focus_areas': missing_skills[:3],
            'milestones': [],
            'mentoring': None
        }
        
        # 마일스톤 설정
        if missing_skills:
            for i, skill in enumerate(missing_skills[:3]):
                milestone_month = (i + 1) * 3
                plan['milestones'].append({
                    'month': milestone_month,
                    'goal': f'{skill} 역량 확보',
                    'measurement': '관련 프로젝트 수행'
                })
        
        # 멘토링 필요성
        if candidate['match_score'] < 80:
            plan['mentoring'] = {
                'needed': True,
                'type': '현직 임원 멘토링',
                'frequency': '월 2회'
            }
        
        return plan
    
    def _create_succession_timeline(
        self,
        candidates: List[dict],
        months_ahead: int
    ) -> List[dict]:
        """승계 타임라인 생성"""
        timeline = []
        
        # 주요 마일스톤
        timeline.append({
            'month': 0,
            'event': '승계 계획 수립',
            'actions': ['후보자 선정', '개발 계획 수립']
        })
        
        timeline.append({
            'month': int(months_ahead * 0.25),
            'event': '1차 준비도 평가',
            'actions': ['역량 평가', '개발 진행 상황 점검']
        })
        
        timeline.append({
            'month': int(months_ahead * 0.5),
            'event': '중간 평가',
            'actions': ['최종 후보 2-3명 선정', '집중 육성']
        })
        
        timeline.append({
            'month': int(months_ahead * 0.75),
            'event': '최종 준비',
            'actions': ['업무 인수인계 준비', '최종 후보 확정']
        })
        
        timeline.append({
            'month': months_ahead,
            'event': '승계 실행',
            'actions': ['공식 발표', '업무 이관']
        })
        
        return timeline
    
    def _analyze_talent_flow(self) -> dict:
        """인재 흐름 분석"""
        # 최근 1년간 승진/이동 데이터 분석
        # 실제로는 인사이동 이력 모델 필요
        
        return {
            'promotions_last_year': 15,
            'lateral_moves': 8,
            'external_hires_leadership': 3,
            'turnover_leadership': 2
        }
    
    def _generate_pipeline_recommendations(
        self,
        pipeline_analysis: dict
    ) -> List[str]:
        """파이프라인 분석 기반 추천사항"""
        recommendations = []
        
        # 각 레벨별 준비도 확인
        for level, stats in pipeline_analysis['leadership_levels'].items():
            if stats['readiness_ratio'] < 0.2:
                recommendations.append(
                    f"{level} 레벨의 차세대 리더 육성 프로그램 강화 필요"
                )
        
        # 고성과자 비율 확인
        total_employees = sum(
            stats['total_count'] 
            for stats in pipeline_analysis['leadership_levels'].values()
        )
        total_high_potentials = sum(
            stats['high_potentials'] 
            for stats in pipeline_analysis['leadership_levels'].values()
        )
        
        if total_high_potentials / max(total_employees, 1) < 0.15:
            recommendations.append(
                "전사적 고성과자 발굴 및 육성 체계 개선 필요"
            )
        
        return recommendations
    
    def _generate_talent_pool_recommendations(
        self,
        report: dict
    ) -> List[str]:
        """인재 풀 리포트 기반 추천사항"""
        recommendations = []
        
        # 부서별 불균형 확인
        dept_candidates = [
            dept['leadership_candidates'] 
            for dept in report['department_analysis'].values()
        ]
        
        if max(dept_candidates) > min(dept_candidates) * 3:
            recommendations.append(
                "부서 간 리더십 후보자 불균형 해소를 위한 순환보직 고려"
            )
        
        # 전체 리더십 준비도
        total_ready = report['summary']['leadership_ready']
        total_employees = report['summary']['total_employees']
        
        if total_ready / total_employees < 0.1:
            recommendations.append(
                "차세대 리더 Pool 확대를 위한 체계적 육성 프로그램 필요"
            )
        
        return recommendations


# 사용 예시
if __name__ == "__main__":
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    try:
        service = LeaderRecommendationService()
        
        # 팀장 직무 찾기
        team_lead_profile = JobProfile.objects.filter(
            job_role__name__icontains='팀장'
        ).first()
        
        if team_lead_profile:
            print(f"\n{team_lead_profile.job_role.name} 후보 추천:")
            
            # 리더 후보 찾기
            candidates = service.find_leader_candidates(
                target_job_profile=team_lead_profile,
                min_evaluation_grade="B+",
                top_n=3
            )
            
            for idx, candidate in enumerate(candidates, 1):
                print(f"\n{idx}. {candidate['name']} ({candidate['department']})")
                print(f"   매칭 점수: {candidate['match_score']:.1f}")
                print(f"   추천 사유: {candidate['recommendation_reason']}")
        
        # 리더십 파이프라인 분석
        print("\n\n리더십 파이프라인 분석:")
        pipeline = service.analyze_leadership_pipeline()
        
        for level, stats in pipeline['leadership_levels'].items():
            print(f"\n{level}:")
            print(f"  인원: {stats['total_count']}명")
            print(f"  고성과자: {stats['high_potentials']}명")
            print(f"  승진준비: {stats['next_level_ready']}명")
            
    except Exception as e:
        print(f"테스트 중 오류: {e}")