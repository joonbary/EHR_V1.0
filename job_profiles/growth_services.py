"""
성장 경로 추천 Django 서비스
성장 경로 추천 엔진과 Django 모델을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from collections import defaultdict, Counter
import json

from employees.models import Employee
from evaluations.models import (
    EvaluationPeriod, ComprehensiveEvaluation
)
from .models import JobProfile, JobRole, JobType, JobCategory
from .growth_path_recommender import (
    recommend_growth_path,
    GrowthPathRecommender,
    GrowthPath,
    GrowthStage
)
from .services import JobProfileService
from .evaluation_services import EvaluationIntegratedService


class CareerTransitionAnalyzer:
    """경력 전환 이력 분석기"""
    
    @staticmethod
    def extract_historical_transitions(
        time_window_years: int = 5
    ) -> Dict[str, List[str]]:
        """
        직원들의 경력 전환 이력 추출
        
        Returns:
            Dict[from_job, List[to_job]]: 직무별 전환 이력
        """
        transitions = defaultdict(list)
        
        # Employee 모델에 job_history 필드가 있다고 가정
        # 실제로는 별도의 JobHistory 모델이 필요할 수 있음
        employees = Employee.objects.filter(
            employment_status='재직'
        ).prefetch_related('job_history')
        
        for employee in employees:
            # 간단한 시뮬레이션 - 실제로는 JobHistory 모델 사용
            # position 변경 이력을 기반으로 추정
            if hasattr(employee, 'job_history'):
                history = employee.job_history.order_by('start_date')
                for i in range(len(history) - 1):
                    from_job = history[i].job_title
                    to_job = history[i + 1].job_title
                    transitions[from_job].append(to_job)
            else:
                # 데이터가 없는 경우 position 기반 추정
                current_position = employee.position
                if '시니어' in current_position and '주니어' not in current_position:
                    transitions['주니어 개발자'].append(current_position)
                elif '매니저' in current_position:
                    transitions['시니어 개발자'].append(current_position)
                elif '팀장' in current_position or '리드' in current_position:
                    transitions['매니저'].append(current_position)
        
        # 직무 프로파일 기반 추가 데이터
        job_roles = JobRole.objects.all().select_related('job_type')
        
        # 카테고리와 타입 기반 전환 패턴 추가
        for role in job_roles:
            role_name = role.name
            type_name = role.job_type.name
            
            # 같은 타입 내 상위 역할로의 전환
            senior_roles = JobRole.objects.filter(
                job_type=role.job_type,
                level__gt=getattr(role, 'level', 1)  # level 필드가 있다고 가정
            )
            
            for senior_role in senior_roles:
                transitions[role_name].append(senior_role.name)
        
        # 기본 전환 패턴 추가 (도메인 지식 기반)
        default_transitions = {
            "주니어 개발자": ["시니어 개발자", "풀스택 개발자"],
            "시니어 개발자": ["개발 팀장", "테크 리드", "솔루션 아키텍트"],
            "개발 팀장": ["개발 매니저", "CTO", "VP Engineering"],
            "HR 스페셜리스트": ["HR 매니저", "HRBP"],
            "HR 매니저": ["HR 팀장", "HR 디렉터"],
            "데이터 분석가": ["시니어 데이터 분석가", "데이터 사이언티스트"],
            "프로덕트 매니저": ["시니어 PM", "프로덕트 리드", "CPO"]
        }
        
        # 기본 패턴 병합
        for from_job, to_jobs in default_transitions.items():
            transitions[from_job].extend(to_jobs)
        
        return dict(transitions)


class GrowthPathService:
    """성장 경로 추천 서비스"""
    
    def __init__(self):
        self.transition_analyzer = CareerTransitionAnalyzer()
        self.recommender = GrowthPathRecommender()
        
    def get_employee_growth_paths(
        self,
        employee: Employee,
        target_job_ids: List[str] = None,
        include_evaluation: bool = True,
        max_years: int = 10,
        top_n: int = 3
    ) -> List[Dict]:
        """
        직원의 성장 경로 추천
        
        Args:
            employee: 직원 객체
            target_job_ids: 특정 목표 직무 ID 리스트 (없으면 자동 추천)
            include_evaluation: 평가 결과 포함 여부
            max_years: 최대 고려 기간
            top_n: 추천 경로 수
        """
        # 직원 프로파일 생성
        if include_evaluation:
            employee_profile = EvaluationIntegratedService.get_employee_profile_with_evaluation(
                employee
            )
        else:
            employee_profile = JobProfileService.get_employee_profile_dict(employee)
        
        # 현재 직무 설정
        current_job = self._get_current_job_name(employee)
        employee_profile['current_job'] = current_job
        
        # 대상 직무 프로파일
        if target_job_ids:
            job_profiles = JobProfile.objects.filter(
                id__in=target_job_ids,
                is_active=True
            ).select_related('job_role__job_type__category')
        else:
            # 자동 추천: 같은 카테고리 또는 인접 카테고리의 상위 직무
            job_profiles = self._find_relevant_job_profiles(employee)
        
        # 직무 프로파일 변환
        job_profile_dicts = [
            JobProfileService.get_job_profile_dict(jp)
            for jp in job_profiles
        ]
        
        # 역사적 전환 데이터
        historical_transitions = self.transition_analyzer.extract_historical_transitions()
        
        # 성장 경로 추천
        growth_paths = recommend_growth_path(
            employee_profile,
            job_profile_dicts,
            historical_transitions,
            top_n=top_n
        )
        
        # Django 모델과 연결
        for path_info in growth_paths:
            # 대상 직무 객체 연결
            target_job_name = path_info['target_job']
            target_profile = next(
                (jp for jp in job_profiles if jp.job_role.name == target_job_name),
                None
            )
            if target_profile:
                path_info['target_job_profile'] = target_profile
                path_info['target_job_category'] = target_profile.job_role.job_type.category.name
            
            # 성장 단계별 추가 정보
            growth_path = path_info['growth_path']
            for stage in growth_path.stages:
                # 해당 직무의 현재 인원 수
                stage.current_employees = Employee.objects.filter(
                    position__icontains=stage.job_name
                ).count()
                
                # 평균 연봉 정보 (있다면)
                stage.avg_salary = self._get_average_salary(stage.job_name)
        
        return growth_paths
    
    def analyze_department_growth_potential(
        self,
        department: str
    ) -> Dict:
        """부서별 성장 잠재력 분석"""
        employees = Employee.objects.filter(
            department=department,
            employment_status='재직'
        )
        
        department_analysis = {
            'department': department,
            'total_employees': employees.count(),
            'growth_ready': 0,
            'need_development': 0,
            'blocked': 0,
            'top_growth_paths': [],
            'skill_gaps': defaultdict(int)
        }
        
        path_counter = Counter()
        
        for employee in employees:
            # 각 직원의 성장 경로 분석
            growth_paths = self.get_employee_growth_paths(
                employee,
                include_evaluation=True,
                top_n=1
            )
            
            if growth_paths:
                top_path = growth_paths[0]
                growth_path = top_path['growth_path']
                
                # 준비도 분류
                if growth_path.total_years <= 2:
                    department_analysis['growth_ready'] += 1
                elif growth_path.total_years <= 5:
                    department_analysis['need_development'] += 1
                else:
                    department_analysis['blocked'] += 1
                
                # 경로 집계
                path_counter[growth_path.target_job] += 1
                
                # 스킬 갭 집계
                for stage in growth_path.stages:
                    for skill in stage.required_skills:
                        department_analysis['skill_gaps'][skill] += 1
        
        # 가장 많이 추천된 성장 경로
        department_analysis['top_growth_paths'] = [
            {'job': job, 'count': count}
            for job, count in path_counter.most_common(5)
        ]
        
        # 가장 많이 필요한 스킬
        department_analysis['top_skill_gaps'] = [
            {'skill': skill, 'count': count}
            for skill, count in sorted(
                department_analysis['skill_gaps'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ]
        
        return department_analysis
    
    def create_personalized_development_plan(
        self,
        employee: Employee,
        target_job_profile: JobProfile,
        include_timeline: bool = True
    ) -> Dict:
        """개인별 맞춤 개발 계획 수립"""
        
        # 성장 경로 생성
        growth_paths = self.get_employee_growth_paths(
            employee,
            target_job_ids=[str(target_job_profile.id)],
            include_evaluation=True,
            top_n=1
        )
        
        if not growth_paths:
            return {
                'status': 'error',
                'message': '해당 직무로의 성장 경로를 찾을 수 없습니다.'
            }
        
        growth_path_info = growth_paths[0]
        growth_path = growth_path_info['growth_path']
        
        development_plan = {
            'employee': employee,
            'target_job': target_job_profile,
            'estimated_timeline': f"{growth_path.total_years:.1f}년",
            'success_probability': f"{growth_path.success_probability * 100:.0f}%",
            'stages': [],
            'immediate_actions': [],
            'resources': []
        }
        
        # 단계별 상세 계획
        current_date = datetime.now()
        accumulated_time = 0
        
        for idx, stage in enumerate(growth_path.stages, 1):
            stage_start = current_date + timedelta(days=accumulated_time * 365)
            stage_end = stage_start + timedelta(days=stage.expected_years * 365)
            
            stage_plan = {
                'phase': idx,
                'target_role': stage.job_name,
                'duration': f"{stage.expected_years:.1f}년",
                'start_date': stage_start.strftime('%Y-%m') if include_timeline else None,
                'end_date': stage_end.strftime('%Y-%m') if include_timeline else None,
                'key_milestones': [],
                'required_skills': stage.required_skills,
                'learning_resources': []
            }
            
            # 마일스톤 생성
            if stage.required_skills:
                for i, skill in enumerate(stage.required_skills[:3]):
                    milestone_date = stage_start + timedelta(
                        days=(stage.expected_years * 365 * (i + 1) / 4)
                    )
                    stage_plan['key_milestones'].append({
                        'milestone': f"{skill} 역량 확보",
                        'target_date': milestone_date.strftime('%Y-%m') if include_timeline else None
                    })
            
            # 학습 리소스 추천
            stage_plan['learning_resources'] = self._recommend_learning_resources(
                stage.required_skills
            )
            
            development_plan['stages'].append(stage_plan)
            accumulated_time += stage.expected_years
        
        # 즉시 실행 가능한 액션
        if growth_path.stages:
            first_stage = growth_path.stages[0]
            development_plan['immediate_actions'] = [
                f"{skill} 학습 시작" for skill in first_stage.required_skills[:3]
            ]
            
            if first_stage.difficulty_score > 70:
                development_plan['immediate_actions'].append(
                    "멘토 찾기 및 커리어 상담 신청"
                )
        
        # 추천 리소스
        development_plan['resources'] = [
            {'type': '교육과정', 'items': self._find_relevant_courses(growth_path)},
            {'type': '멘토', 'items': self._find_potential_mentors(target_job_profile)},
            {'type': '프로젝트', 'items': self._suggest_stretch_projects(employee, growth_path)}
        ]
        
        return development_plan
    
    def _get_current_job_name(self, employee: Employee) -> str:
        """직원의 현재 직무명 추출"""
        # JobRole과 연결되어 있다면 사용
        if hasattr(employee, 'current_job_role') and employee.current_job_role:
            return employee.current_job_role.name
        
        # position 필드에서 추출
        position = employee.position
        
        # 직급 매핑
        position_mapping = {
            'STAFF': '사원',
            'SENIOR': '대리',
            'MANAGER': '과장',
            'DIRECTOR': '부장',
            'EXECUTIVE': '임원'
        }
        
        # 부서별 직무 매핑
        dept_job_mapping = {
            'HR': 'HR 스페셜리스트',
            'IT': '개발자',
            'Finance': '재무 분석가',
            'Marketing': '마케팅 매니저',
            'Sales': '영업 담당자'
        }
        
        # 기본값
        base_job = dept_job_mapping.get(employee.department, '직원')
        
        # 직급 반영
        for key, value in position_mapping.items():
            if key in position:
                if key in ['SENIOR', 'STAFF']:
                    return f"주니어 {base_job}" if key == 'STAFF' else f"시니어 {base_job}"
                elif key == 'MANAGER':
                    return f"{base_job} 매니저"
                elif key == 'DIRECTOR':
                    return f"{employee.department} 팀장"
                elif key == 'EXECUTIVE':
                    return f"{employee.department} 임원"
        
        return base_job
    
    def _find_relevant_job_profiles(
        self, 
        employee: Employee,
        max_count: int = 10
    ) -> List[JobProfile]:
        """직원에게 관련성 높은 직무 프로파일 찾기"""
        # 같은 부서 또는 관련 카테고리
        relevant_categories = []
        
        dept_category_mapping = {
            'HR': ['Human Resources', 'Organization Development'],
            'IT': ['Technology', 'Engineering', 'Data'],
            'Finance': ['Finance', 'Accounting', 'Business'],
            'Marketing': ['Marketing', 'Sales', 'Business'],
            'Sales': ['Sales', 'Business Development']
        }
        
        relevant_categories = dept_category_mapping.get(
            employee.department, 
            ['General']
        )
        
        # 관련 직무 프로파일 조회
        job_profiles = JobProfile.objects.filter(
            Q(job_role__job_type__category__name__in=relevant_categories) |
            Q(job_role__description__icontains=employee.department),
            is_active=True
        ).select_related(
            'job_role__job_type__category'
        ).order_by('-job_role__job_type__level')[:max_count]
        
        return job_profiles
    
    def _get_average_salary(self, job_name: str) -> Optional[float]:
        """직무별 평균 연봉 조회"""
        # 실제로는 Salary 모델이 있어야 함
        # 여기서는 더미 데이터 반환
        salary_ranges = {
            '주니어': 4000,
            '시니어': 6000,
            '매니저': 8000,
            '팀장': 9000,
            '디렉터': 12000,
            '임원': 15000
        }
        
        for key, salary in salary_ranges.items():
            if key in job_name:
                return salary
        
        return 5000  # 기본값
    
    def _recommend_learning_resources(self, skills: List[str]) -> List[Dict]:
        """스킬별 학습 리소스 추천"""
        resources = []
        
        # 스킬별 리소스 매핑 (실제로는 DB에서 관리)
        skill_resources = {
            'Python': {
                'courses': ['Python 고급 과정', 'Django 마스터클래스'],
                'books': ['Fluent Python', 'Two Scoops of Django'],
                'online': ['Coursera Python Specialization']
            },
            '리더십': {
                'courses': ['리더십 에센셜', '팀 관리 워크샵'],
                'books': ['Good to Great', 'The Five Dysfunctions of a Team'],
                'coaching': ['리더십 코칭 프로그램']
            },
            '데이터분석': {
                'courses': ['비즈니스 애널리틱스', 'SQL 고급과정'],
                'tools': ['Tableau', 'Power BI'],
                'certification': ['데이터 분석 전문가']
            }
        }
        
        for skill in skills[:3]:  # 상위 3개 스킬
            resource = {'skill': skill, 'recommendations': []}
            
            # 정확한 매칭이 있는 경우
            if skill in skill_resources:
                resource['recommendations'] = skill_resources[skill]
            else:
                # 부분 매칭 시도
                for key, value in skill_resources.items():
                    if key in skill or skill in key:
                        resource['recommendations'] = value
                        break
            
            if resource['recommendations']:
                resources.append(resource)
        
        return resources
    
    def _find_relevant_courses(self, growth_path: GrowthPath) -> List[str]:
        """성장 경로에 맞는 교육 과정 찾기"""
        courses = []
        
        # 모든 필요 스킬 수집
        all_skills = set()
        for stage in growth_path.stages:
            all_skills.update(stage.required_skills)
        
        # 스킬 카테고리별 과정 추천
        if any('리더' in skill or '관리' in skill for skill in all_skills):
            courses.append('차세대 리더 양성 과정')
        
        if any('데이터' in skill or '분석' in skill for skill in all_skills):
            courses.append('데이터 기반 의사결정 과정')
        
        if any('개발' in skill or 'Python' in skill for skill in all_skills):
            courses.append('소프트웨어 아키텍처 과정')
        
        return courses[:5]
    
    def _find_potential_mentors(self, target_job_profile: JobProfile) -> List[str]:
        """잠재적 멘토 찾기"""
        # 실제로는 해당 직무 수행자 중 시니어 찾기
        mentors = []
        
        # 같은 직무 계열의 시니어 직원
        similar_employees = Employee.objects.filter(
            Q(position__icontains='SENIOR') | 
            Q(position__icontains='MANAGER') |
            Q(position__icontains='DIRECTOR'),
            department=target_job_profile.job_role.job_type.category.name[:2]  # 부서 추정
        )[:3]
        
        for emp in similar_employees:
            mentors.append(f"{emp.name} ({emp.position})")
        
        return mentors
    
    def _suggest_stretch_projects(
        self, 
        employee: Employee, 
        growth_path: GrowthPath
    ) -> List[str]:
        """성장을 위한 도전 과제 제안"""
        projects = []
        
        if growth_path.stages:
            first_stage = growth_path.stages[0]
            
            # 스킬 기반 프로젝트 제안
            for skill in first_stage.required_skills[:2]:
                if '리더' in skill:
                    projects.append('소규모 TF 리딩')
                elif '분석' in skill:
                    projects.append('부서 KPI 대시보드 구축')
                elif '전략' in skill:
                    projects.append('신규 사업 기획 참여')
                elif '개발' in skill:
                    projects.append('신기술 PoC 프로젝트')
        
        return projects[:3]


# 뷰에서 사용할 헬퍼 함수
def get_growth_recommendations_for_employee(employee_id: int) -> Dict:
    """직원 ID로 성장 경로 추천 받기"""
    try:
        employee = Employee.objects.get(id=employee_id)
        service = GrowthPathService()
        
        growth_paths = service.get_employee_growth_paths(
            employee,
            include_evaluation=True,
            top_n=3
        )
        
        return {
            'status': 'success',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'current_position': employee.position,
                'department': employee.department
            },
            'growth_paths': growth_paths
        }
    except Employee.DoesNotExist:
        return {
            'status': 'error',
            'message': '직원을 찾을 수 없습니다.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }


# 사용 예시
if __name__ == "__main__":
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    # 테스트
    try:
        # 첫 번째 직원의 성장 경로 분석
        employee = Employee.objects.filter(employment_status='재직').first()
        
        if employee:
            service = GrowthPathService()
            
            # 성장 경로 추천
            print(f"\n{employee.name}님의 성장 경로 추천:")
            growth_paths = service.get_employee_growth_paths(
                employee,
                include_evaluation=True,
                top_n=2
            )
            
            for idx, path in enumerate(growth_paths, 1):
                print(f"\n{idx}. {path['target_job']} 경로")
                growth_path = path['growth_path']
                print(f"   예상 기간: {growth_path.total_years:.1f}년")
                print(f"   성공 확률: {growth_path.success_probability*100:.0f}%")
                
                for stage in growth_path.stages:
                    print(f"   → {stage.job_name} ({stage.expected_years:.1f}년)")
            
            # 부서 분석
            print(f"\n\n{employee.department} 부서 성장 잠재력 분석:")
            dept_analysis = service.analyze_department_growth_potential(
                employee.department
            )
            print(f"   성장 준비 완료: {dept_analysis['growth_ready']}명")
            print(f"   개발 필요: {dept_analysis['need_development']}명")
            print(f"   주요 스킬 갭: {[s['skill'] for s in dept_analysis['top_skill_gaps'][:3]]}")
            
    except Exception as e:
        print(f"테스트 중 오류: {e}")