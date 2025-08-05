"""
성장레벨 인증 Django 서비스
인증 엔진과 Django 모델을 연결하는 서비스 레이어
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.db.models import Q, Count, Max
from django.contrib.auth.models import User
from django.core.cache import cache
import logging

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from trainings.models import TrainingEnrollment
from job_profiles.models import JobProfile
from .models import (
    GrowthLevelRequirement, JobLevelRequirement,
    GrowthLevelCertification, CertificationCheckLog
)
from .certification_engine import CertificationEngine, calculate_certification_progress

logger = logging.getLogger(__name__)


class CertificationService:
    """성장레벨 인증 서비스"""
    
    def __init__(self):
        self.engine = CertificationEngine()
    
    def check_growth_level_certification(
        self,
        employee: Employee,
        target_level: str,
        target_job_id: Optional[str] = None
    ) -> Dict:
        """
        성장레벨 인증 체크
        
        Args:
            employee: 직원 객체
            target_level: 목표 성장레벨 (예: Lv.3)
            target_job_id: 목표 직무 ID (선택)
        
        Returns:
            인증 체크 결과
        """
        # 캐시 확인
        cache_key = f"certification_check_{employee.id}_{target_level}_{target_job_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # 1. 직원 프로파일 생성
            employee_profile = self._build_employee_profile(employee)
            
            # 2. 목표 레벨 요건 조회
            level_requirements = self._get_level_requirements(target_level)
            
            if not level_requirements:
                return {
                    'status': 'error',
                    'message': f'{target_level} 레벨 요건을 찾을 수 없습니다.'
                }
            
            # 3. 직무별 추가 요건 조회
            job_requirements = None
            target_job_name = None
            
            if target_job_id:
                job_requirements = self._get_job_specific_requirements(
                    target_job_id, target_level
                )
                try:
                    job_profile = JobProfile.objects.get(id=target_job_id)
                    target_job_name = job_profile.job_role.name
                except JobProfile.DoesNotExist:
                    pass
            
            # 4. 인증 체크 실행
            check_result = self.engine.check_certification_eligibility(
                employee_profile=employee_profile,
                target_level_requirements=level_requirements,
                job_specific_requirements=job_requirements
            )
            
            # 5. 결과 포맷팅
            formatted_result = self._format_certification_result(
                check_result,
                employee,
                target_level,
                target_job_name
            )
            
            # 6. 진행률 계산
            progress = calculate_certification_progress(
                employee_profile,
                level_requirements
            )
            formatted_result['progress'] = progress
            
            # 7. 체크 로그 저장
            self._save_check_log(
                employee=employee,
                target_level=target_level,
                target_job=target_job_name,
                check_result=formatted_result
            )
            
            # 캐시 저장 (30분)
            cache.set(cache_key, formatted_result, 1800)
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Certification check error: {str(e)}")
            return {
                'status': 'error',
                'message': '인증 체크 중 오류가 발생했습니다.'
            }
    
    def _build_employee_profile(self, employee: Employee) -> Dict:
        """직원 프로파일 구성"""
        profile = {
            'employee_id': str(employee.id),
            'name': employee.name,
            'level': self._get_current_level(employee),
            'position': employee.position,
            'department': employee.department
        }
        
        # 평가 정보
        evaluations = ComprehensiveEvaluation.objects.filter(
            employee=employee
        ).order_by('-created_at')[:5]
        
        if evaluations.exists():
            latest_eval = evaluations.first()
            profile['recent_evaluation'] = {
                'overall_grade': latest_eval.final_grade,
                'professionalism': latest_eval.expertise_grade,
                'evaluation_date': latest_eval.created_at.isoformat()
            }
            
            profile['evaluation_history'] = [
                {'overall_grade': e.final_grade}
                for e in evaluations
            ]
        
        # 교육 정보
        completed_trainings = TrainingEnrollment.objects.filter(
            employee=employee,
            status='COMPLETED'
        ).select_related('course')
        
        profile['completed_courses'] = list(
            completed_trainings.values_list('course__course_code', flat=True)
        )
        
        # 교육시간 계산
        total_hours = sum(
            enrollment.course.duration_hours 
            for enrollment in completed_trainings
        )
        profile['total_training_hours'] = total_hours
        
        # 스킬 정보 (실제로는 별도 모델에서 조회)
        profile['skills'] = self._get_employee_skills(employee)
        
        # 경력 정보
        if employee.employment_date:
            total_years = (datetime.now().date() - employee.employment_date).days / 365
            profile['total_career_years'] = round(total_years, 1)
        else:
            profile['total_career_years'] = 0
        
        # 현 레벨 경력 (간단 추정)
        profile['years_in_current_level'] = self._estimate_years_in_level(employee)
        
        return profile
    
    def _get_current_level(self, employee: Employee) -> str:
        """현재 성장레벨 조회"""
        # 최신 인증 기록 확인
        latest_cert = GrowthLevelCertification.objects.filter(
            employee=employee,
            status='CERTIFIED'
        ).order_by('-certified_date').first()
        
        if latest_cert:
            return latest_cert.growth_level
        
        # 인증 기록이 없으면 직급 기반 추정
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
        
        return 'Lv.1'
    
    def _get_employee_skills(self, employee: Employee) -> List[str]:
        """직원 스킬 조회"""
        # 실제로는 스킬 모델에서 조회
        # 여기서는 부서와 직급 기반 더미 데이터
        dept_skills = {
            'HR': ['인사관리', '조직개발', '채용', '교육기획'],
            'IT': ['프로젝트관리', '시스템설계', '개발', '데이터분석'],
            'Finance': ['재무분석', '예산관리', '리스크관리', '투자분석'],
            'Marketing': ['마케팅전략', '브랜드관리', '디지털마케팅', '시장분석'],
            '전략기획팀': ['전략수립', '성과관리', '프로젝트관리', '데이터분석'],
            '영업팀': ['영업전략', '고객관리', '협상', '시장개척']
        }
        
        skills = []
        if employee.department in dept_skills:
            skills.extend(dept_skills[employee.department][:3])
        
        # 직급별 추가 스킬
        if '과장' in employee.position or '차장' in employee.position:
            skills.extend(['리더십', '팀워크'])
        elif '부장' in employee.position or '팀장' in employee.position:
            skills.extend(['조직운영', '성과관리'])
        
        return list(set(skills))
    
    def _estimate_years_in_level(self, employee: Employee) -> float:
        """현 레벨 경력 추정"""
        # 최근 레벨 변경 이력 확인
        # 실제로는 승진 이력에서 조회
        # 여기서는 간단히 총 경력의 1/3로 추정
        if employee.employment_date:
            total_years = (datetime.now().date() - employee.employment_date).days / 365
            return round(total_years / 3, 1)
        return 0
    
    def _get_level_requirements(self, level: str) -> Optional[Dict]:
        """레벨 요건 조회"""
        try:
            requirement = GrowthLevelRequirement.objects.get(
                level=level,
                is_active=True
            )
            
            return {
                'level': requirement.level,
                'level_name': requirement.level_name,
                'min_evaluation_grade': requirement.min_evaluation_grade,
                'consecutive_evaluations': requirement.consecutive_evaluations,
                'required_courses': requirement.required_courses,
                'required_course_categories': requirement.required_course_categories,
                'min_training_hours': requirement.min_training_hours,
                'required_skills': requirement.required_skills,
                'skill_proficiency_level': requirement.skill_proficiency_level,
                'min_years_in_level': requirement.min_years_in_level,
                'min_total_years': requirement.min_total_years
            }
            
        except GrowthLevelRequirement.DoesNotExist:
            # 기본값 반환
            return self._get_default_requirements(level)
    
    def _get_default_requirements(self, level: str) -> Dict:
        """기본 레벨 요건"""
        defaults = {
            'Lv.1': {
                'level': 'Lv.1',
                'level_name': '신입',
                'min_evaluation_grade': 'C',
                'consecutive_evaluations': 1,
                'required_courses': [],
                'required_skills': [],
                'min_years_in_level': 0,
                'min_total_years': 0
            },
            'Lv.2': {
                'level': 'Lv.2',
                'level_name': '일반',
                'min_evaluation_grade': 'B',
                'consecutive_evaluations': 1,
                'required_courses': ['신입사원교육'],
                'required_skills': ['업무기초'],
                'min_years_in_level': 1,
                'min_total_years': 1
            },
            'Lv.3': {
                'level': 'Lv.3',
                'level_name': '전문가',
                'min_evaluation_grade': 'B+',
                'consecutive_evaluations': 2,
                'required_courses': ['성과관리전략', '리더십기초'],
                'required_skills': ['성과관리', '전략수립', '조직운영'],
                'min_years_in_level': 2,
                'min_total_years': 3
            },
            'Lv.4': {
                'level': 'Lv.4',
                'level_name': '리더',
                'min_evaluation_grade': 'A',
                'consecutive_evaluations': 2,
                'required_courses': ['리더십고급', '전략경영'],
                'required_skills': ['리더십', '전략수립', '조직운영', '성과관리'],
                'min_years_in_level': 2,
                'min_total_years': 5
            },
            'Lv.5': {
                'level': 'Lv.5',
                'level_name': '임원',
                'min_evaluation_grade': 'A+',
                'consecutive_evaluations': 3,
                'required_courses': ['임원리더십', '경영전략'],
                'required_skills': ['경영전략', '조직운영', '리더십', '의사결정'],
                'min_years_in_level': 3,
                'min_total_years': 10
            }
        }
        
        return defaults.get(level, defaults['Lv.1'])
    
    def _get_job_specific_requirements(
        self,
        job_id: str,
        level: str
    ) -> Optional[Dict]:
        """직무별 추가 요건 조회"""
        try:
            job_req = JobLevelRequirement.objects.get(
                job_profile_id=job_id,
                required_growth_level=level,
                is_active=True
            )
            
            return {
                'job_specific_courses': job_req.job_specific_courses,
                'job_specific_skills': job_req.job_specific_skills,
                'override_eval_grade': job_req.override_eval_grade
            }
            
        except JobLevelRequirement.DoesNotExist:
            return None
    
    def _format_certification_result(
        self,
        check_result: Dict,
        employee: Employee,
        target_level: str,
        target_job: Optional[str] = None
    ) -> Dict:
        """인증 결과 포맷팅"""
        # 미충족 요건 정리
        missing_courses = check_result['missing_requirements'].get('training', {}).get('courses', [])
        missing_skills = check_result['missing_requirements'].get('skills', {}).get('skills', [])
        
        # 평가 상태
        eval_ok = check_result['checks']['evaluation']
        eval_missing = check_result['missing_requirements'].get('evaluation', {})
        
        formatted = {
            'status': 'success',
            'certification_result': check_result['certification_result'],
            'employee': {
                'id': str(employee.id),
                'name': employee.name,
                'current_level': check_result['current_level']
            },
            'target': {
                'level': target_level,
                'job': target_job
            },
            'checks': check_result['checks'],
            'details': {
                'missing_courses': missing_courses,
                'missing_skills': missing_skills,
                'eval_ok': eval_ok,
                'current_level': check_result['current_level'],
                'required_level': target_level
            },
            'expected_certification_date': check_result['expected_certification_date'],
            'recommendations': check_result['recommendations']
        }
        
        # 평가 상세
        if eval_missing:
            formatted['details']['evaluation'] = {
                'current_grade': eval_missing.get('current_grade'),
                'required_grade': eval_missing.get('required_grade'),
                'message': eval_missing.get('message')
            }
        
        return formatted
    
    def _save_check_log(
        self,
        employee: Employee,
        target_level: str,
        target_job: Optional[str],
        check_result: Dict
    ):
        """체크 로그 저장"""
        try:
            CertificationCheckLog.objects.create(
                employee=employee,
                target_level=target_level,
                target_job=target_job or '',
                check_result='READY' if check_result['certification_result'] == '충족' else 'NOT_READY',
                result_details=check_result,
                expected_certification_date=check_result.get('expected_certification_date'),
                api_source='growth_level_check'
            )
        except Exception as e:
            logger.error(f"Failed to save check log: {str(e)}")
    
    def apply_for_certification(
        self,
        employee: Employee,
        target_level: str,
        notes: str = ""
    ) -> Dict:
        """성장레벨 인증 신청"""
        try:
            # 중복 신청 확인
            existing = GrowthLevelCertification.objects.filter(
                employee=employee,
                growth_level=target_level,
                status__in=['PENDING', 'CERTIFIED']
            ).exists()
            
            if existing:
                return {
                    'success': False,
                    'message': '이미 신청했거나 인증된 레벨입니다.'
                }
            
            # 자격 체크
            check_result = self.check_growth_level_certification(
                employee=employee,
                target_level=target_level
            )
            
            if check_result['certification_result'] != '충족':
                return {
                    'success': False,
                    'message': '인증 요건을 충족하지 못했습니다.',
                    'missing_requirements': check_result['details']
                }
            
            # 인증 신청 생성
            certification = GrowthLevelCertification.objects.create(
                employee=employee,
                growth_level=target_level,
                status='PENDING',
                certification_snapshot=check_result,
                evaluation_check=check_result['checks']['evaluation'],
                training_check=check_result['checks']['training'],
                skill_check=check_result['checks']['skills'],
                experience_check=check_result['checks']['experience']
            )
            
            return {
                'success': True,
                'certification_id': str(certification.id),
                'message': '성장레벨 인증이 신청되었습니다.'
            }
            
        except Exception as e:
            logger.error(f"Certification application error: {str(e)}")
            return {
                'success': False,
                'message': '인증 신청 중 오류가 발생했습니다.'
            }
    
    def get_certification_history(
        self,
        employee: Employee
    ) -> List[Dict]:
        """인증 이력 조회"""
        certifications = GrowthLevelCertification.objects.filter(
            employee=employee
        ).order_by('-applied_date')
        
        history = []
        for cert in certifications:
            history.append({
                'id': str(cert.id),
                'level': cert.growth_level,
                'status': cert.status,
                'status_display': cert.get_status_display(),
                'applied_date': cert.applied_date.isoformat(),
                'certified_date': cert.certified_date.isoformat() if cert.certified_date else None,
                'checks': {
                    'evaluation': cert.evaluation_check,
                    'training': cert.training_check,
                    'skills': cert.skill_check,
                    'experience': cert.experience_check
                }
            })
        
        return history