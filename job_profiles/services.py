"""
직무 프로파일 관련 비즈니스 로직 서비스
Django 모델과 매칭 엔진을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Prefetch
from django.contrib.auth.models import User

from employees.models import Employee
from .models import JobProfile, JobRole
from .matching_engine import match_profile, match_multiple_profiles, ProfileMatcher


class JobProfileService:
    """직무 프로파일 관련 서비스"""
    
    @staticmethod
    def get_employee_profile_dict(employee: Employee) -> dict:
        """Employee 모델을 매칭용 딕셔너리로 변환"""
        # 직원의 교육이수, 자격증 정보 수집 (추후 모델 확장 시 실제 데이터 사용)
        profile = {
            'employee_id': str(employee.id),
            'name': employee.name,
            'career_years': employee.get_career_years() if hasattr(employee, 'get_career_years') else 0,
            'current_position': employee.position,
            'current_department': employee.department,
            'certifications': [],  # 추후 자격증 모델 연동
            'completed_courses': [],  # 추후 교육이수 모델 연동
            'skills': []  # 추후 스킬 모델 연동
        }
        
        # 임시로 직급과 부서 기반 스킬 추론
        if employee.department == 'HR' or employee.department == '인사':
            profile['skills'].extend(['인사관리', '조직문화'])
            profile['certifications'].append('노동법기초')
        
        if employee.position in ['MANAGER', '과장', '부장']:
            profile['skills'].extend(['리더십', '프로젝트관리'])
            profile['career_years'] = 5  # 임시 설정
        
        return profile
    
    @staticmethod
    def get_job_profile_dict(job_profile: JobProfile) -> dict:
        """JobProfile 모델을 매칭용 딕셔너리로 변환"""
        return {
            'job_id': str(job_profile.id),
            'job_name': job_profile.job_role.name,
            'job_code': job_profile.job_role.code,
            'role_responsibility': job_profile.role_responsibility,
            'qualification': job_profile.qualification,
            'basic_skills': job_profile.basic_skills or [],
            'applied_skills': job_profile.applied_skills or [],
            'related_certifications': job_profile.related_certifications or []
        }
    
    @staticmethod
    def match_employee_to_job(employee: Employee, job_profile: JobProfile) -> dict:
        """직원과 특정 직무 간의 매칭 수행"""
        employee_dict = JobProfileService.get_employee_profile_dict(employee)
        job_dict = JobProfileService.get_job_profile_dict(job_profile)
        
        result = match_profile(job_dict, employee_dict)
        
        # 추가 정보 포함
        result['job_info'] = {
            'id': str(job_profile.id),
            'name': job_profile.job_role.name,
            'full_path': job_profile.job_role.full_path
        }
        result['employee_info'] = {
            'id': str(employee.id),
            'name': employee.name,
            'current_position': employee.position
        }
        
        return result
    
    @staticmethod
    def find_suitable_jobs_for_employee(
        employee: Employee, 
        min_score: float = 60.0,
        top_n: int = 5,
        exclude_current: bool = True
    ) -> List[dict]:
        """직원에게 적합한 직무 찾기"""
        
        # 활성화된 모든 직무 프로파일 조회
        job_profiles = JobProfile.objects.filter(
            is_active=True
        ).select_related('job_role__job_type__category')
        
        # 현재 직무 제외 (옵션)
        if exclude_current and hasattr(employee, 'current_job_role'):
            job_profiles = job_profiles.exclude(
                job_role=employee.current_job_role
            )
        
        # 프로파일 변환
        employee_dict = JobProfileService.get_employee_profile_dict(employee)
        job_dicts = [
            JobProfileService.get_job_profile_dict(jp) 
            for jp in job_profiles
        ]
        
        # 매칭 수행
        results = match_multiple_profiles(
            job_dicts, 
            employee_dict, 
            top_n=top_n, 
            min_score=min_score
        )
        
        # JobProfile 객체 참조 추가
        for result in results:
            job_profile = next(
                (jp for jp in job_profiles if str(jp.id) == result['job_id']), 
                None
            )
            if job_profile:
                result['job_profile_object'] = job_profile
                result['job_full_path'] = job_profile.job_role.full_path
        
        return results
    
    @staticmethod
    def analyze_team_skill_gaps(department: str) -> dict:
        """부서별 스킬 갭 분석"""
        # 부서 직원들
        employees = Employee.objects.filter(
            department=department,
            employment_status='재직'
        )
        
        # 부서 관련 직무들 (부서명으로 추론)
        related_job_profiles = JobProfile.objects.filter(
            Q(job_role__name__icontains=department) |
            Q(job_role__job_type__name__icontains=department),
            is_active=True
        ).distinct()
        
        # 전체 필요 스킬 수집
        all_required_skills = set()
        for jp in related_job_profiles:
            all_required_skills.update(jp.basic_skills or [])
            all_required_skills.update(jp.applied_skills or [])
        
        # 부서 보유 스킬 수집 (임시)
        team_skills = set()
        for emp in employees:
            profile = JobProfileService.get_employee_profile_dict(emp)
            team_skills.update(profile.get('skills', []))
            team_skills.update(profile.get('certifications', []))
        
        # 갭 분석
        skill_gaps = list(all_required_skills - team_skills)
        coverage_rate = len(team_skills) / len(all_required_skills) * 100 if all_required_skills else 0
        
        return {
            'department': department,
            'total_employees': employees.count(),
            'related_job_profiles': related_job_profiles.count(),
            'required_skills_count': len(all_required_skills),
            'current_skills_count': len(team_skills),
            'coverage_rate': round(coverage_rate, 2),
            'skill_gaps': skill_gaps[:10],  # 상위 10개만
            'recommendations': [
                f"{skill} 역량 보유 인력 확보 필요" for skill in skill_gaps[:3]
            ]
        }
    
    @staticmethod
    def get_career_path_recommendations(employee: Employee) -> List[dict]:
        """직원의 경력 개발 경로 추천"""
        current_matches = JobProfileService.find_suitable_jobs_for_employee(
            employee, 
            min_score=50.0,  # 낮은 임계값으로 더 많은 옵션 제공
            top_n=10
        )
        
        recommendations = []
        for match in current_matches:
            if match['match_score'] >= 80:
                readiness = "즉시 전환 가능"
                timeframe = "0-6개월"
            elif match['match_score'] >= 65:
                readiness = "단기 준비 필요"
                timeframe = "6-12개월"
            else:
                readiness = "중장기 준비 필요"
                timeframe = "1-2년"
            
            recommendations.append({
                'job_profile': match.get('job_profile_object'),
                'match_score': match['match_score'],
                'readiness': readiness,
                'timeframe': timeframe,
                'priority_skills': match['gaps']['basic_skills'][:3],
                'total_gap_count': (
                    len(match['gaps']['basic_skills']) + 
                    len(match['gaps']['applied_skills'])
                )
            })
        
        return recommendations


class SkillDevelopmentService:
    """스킬 개발 관련 서비스"""
    
    @staticmethod
    def create_development_plan(employee: Employee, target_job_profile: JobProfile) -> dict:
        """개인별 역량 개발 계획 생성"""
        match_result = JobProfileService.match_employee_to_job(employee, target_job_profile)
        
        # 스킬 갭 우선순위 설정
        basic_gaps = match_result['gaps']['basic_skills']
        applied_gaps = match_result['gaps']['applied_skills']
        
        # 개발 계획 생성
        development_plan = {
            'employee': employee,
            'target_job': target_job_profile,
            'current_match_score': match_result['match_score'],
            'phases': []
        }
        
        # Phase 1: 기본 스킬 (0-6개월)
        if basic_gaps:
            development_plan['phases'].append({
                'phase': 1,
                'title': '기본 역량 개발',
                'duration': '0-6개월',
                'skills': basic_gaps,
                'learning_methods': [
                    '사내 교육 프로그램 이수',
                    '온라인 강의 수강',
                    '멘토링 프로그램 참여'
                ]
            })
        
        # Phase 2: 응용 스킬 (6-12개월)
        if applied_gaps:
            development_plan['phases'].append({
                'phase': 2,
                'title': '전문 역량 개발',
                'duration': '6-12개월',
                'skills': applied_gaps[:5],  # 상위 5개
                'learning_methods': [
                    '실무 프로젝트 참여',
                    '전문 자격증 취득',
                    '외부 전문 교육 이수'
                ]
            })
        
        # Phase 3: 실무 경험 (12개월 이상)
        if match_result['match_score'] < 80:
            development_plan['phases'].append({
                'phase': 3,
                'title': '실무 경험 축적',
                'duration': '12개월 이상',
                'activities': [
                    '관련 부서 협업 프로젝트',
                    '직무 순환 프로그램',
                    '태스크 포스 참여'
                ]
            })
        
        return development_plan


# 사용 예시
if __name__ == "__main__":
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    # 테스트용 직원과 직무 가져오기
    try:
        employee = Employee.objects.first()
        job_profile = JobProfile.objects.first()
        
        if employee and job_profile:
            # 매칭 테스트
            result = JobProfileService.match_employee_to_job(employee, job_profile)
            print(f"\n{employee.name} - {job_profile.job_role.name} 매칭 결과:")
            print(f"매칭 점수: {result['match_score']}%")
            
            # 추천 직무 찾기
            suitable_jobs = JobProfileService.find_suitable_jobs_for_employee(employee)
            print(f"\n{employee.name}님께 추천하는 직무:")
            for job in suitable_jobs[:3]:
                print(f"- {job['job_full_path']}: {job['match_score']}%")
        
    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")