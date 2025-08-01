"""
성장레벨 인증 평가 엔진
직원의 현재 상태가 특정 레벨 인증 요건을 충족하는지 평가
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CertificationEngine:
    """인증 평가 엔진"""
    
    def __init__(self):
        self.grade_hierarchy = {
            'S': 5, 'A+': 4, 'A': 3, 'B+': 2, 'B': 1, 'C': 0
        }
    
    def check_certification_eligibility(
        self,
        employee_profile: Dict,
        target_level_requirements: Dict,
        job_specific_requirements: Optional[Dict] = None
    ) -> Dict:
        """
        성장레벨 인증 자격 체크
        
        Args:
            employee_profile: 직원 정보 (평가, 교육, 스킬 등)
            target_level_requirements: 목표 레벨의 기본 요건
            job_specific_requirements: 직무별 추가 요건
        
        Returns:
            인증 체크 결과
        """
        result = {
            'certification_result': '미충족',  # 충족/미충족/부분충족
            'current_level': employee_profile.get('level', 'Lv.1'),
            'target_level': target_level_requirements.get('level'),
            'checks': {
                'evaluation': False,
                'training': False,
                'skills': False,
                'experience': False
            },
            'missing_requirements': {
                'evaluation': {},
                'training': {},
                'skills': {},
                'experience': {}
            },
            'expected_certification_date': None,
            'recommendations': []
        }
        
        # 1. 평가 요건 체크
        eval_check = self._check_evaluation_requirements(
            employee_profile,
            target_level_requirements,
            job_specific_requirements
        )
        result['checks']['evaluation'] = eval_check['passed']
        result['missing_requirements']['evaluation'] = eval_check['missing']
        
        # 2. 교육 요건 체크
        training_check = self._check_training_requirements(
            employee_profile,
            target_level_requirements,
            job_specific_requirements
        )
        result['checks']['training'] = training_check['passed']
        result['missing_requirements']['training'] = training_check['missing']
        
        # 3. 스킬 요건 체크
        skill_check = self._check_skill_requirements(
            employee_profile,
            target_level_requirements,
            job_specific_requirements
        )
        result['checks']['skills'] = skill_check['passed']
        result['missing_requirements']['skills'] = skill_check['missing']
        
        # 4. 경력 요건 체크
        exp_check = self._check_experience_requirements(
            employee_profile,
            target_level_requirements
        )
        result['checks']['experience'] = exp_check['passed']
        result['missing_requirements']['experience'] = exp_check['missing']
        
        # 5. 종합 판정
        all_passed = all(result['checks'].values())
        some_passed = any(result['checks'].values())
        
        if all_passed:
            result['certification_result'] = '충족'
        elif some_passed:
            result['certification_result'] = '부분충족'
        else:
            result['certification_result'] = '미충족'
        
        # 6. 예상 인증일 계산
        if not all_passed:
            result['expected_certification_date'] = self._estimate_certification_date(
                result['missing_requirements']
            )
        
        # 7. 개선 권고사항 생성
        result['recommendations'] = self._generate_recommendations(
            result['missing_requirements']
        )
        
        return result
    
    def _check_evaluation_requirements(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict] = None
    ) -> Dict:
        """평가 요건 체크"""
        # 요구 등급 결정 (직무별 오버라이드 우선)
        required_grade = level_req.get('min_evaluation_grade', 'B+')
        if job_req and job_req.get('override_eval_grade'):
            required_grade = job_req['override_eval_grade']
        
        consecutive_required = level_req.get('consecutive_evaluations', 1)
        
        # 최근 평가 이력 확인
        eval_history = employee_profile.get('evaluation_history', [])
        recent_eval = employee_profile.get('recent_evaluation', {})
        
        if not recent_eval:
            return {
                'passed': False,
                'missing': {
                    'message': '평가 이력이 없습니다',
                    'required_grade': required_grade,
                    'consecutive_required': consecutive_required
                }
            }
        
        # 현재 등급 확인
        current_grade = recent_eval.get('overall_grade', 'C')
        grade_ok = self._compare_grades(current_grade, required_grade) >= 0
        
        # 연속 평가 확인
        consecutive_count = 0
        for eval in eval_history[:consecutive_required]:
            if self._compare_grades(eval.get('overall_grade', 'C'), required_grade) >= 0:
                consecutive_count += 1
            else:
                break
        
        consecutive_ok = consecutive_count >= consecutive_required
        
        if grade_ok and consecutive_ok:
            return {'passed': True, 'missing': {}}
        else:
            missing = {
                'current_grade': current_grade,
                'required_grade': required_grade,
                'consecutive_count': consecutive_count,
                'consecutive_required': consecutive_required
            }
            
            if not grade_ok:
                missing['message'] = f'평가 등급이 {required_grade} 이상이어야 합니다'
            else:
                missing['message'] = f'{consecutive_required}회 연속 {required_grade} 이상 필요'
            
            return {'passed': False, 'missing': missing}
    
    def _check_training_requirements(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict] = None
    ) -> Dict:
        """교육 요건 체크"""
        completed_courses = set(employee_profile.get('completed_courses', []))
        
        # 필수 교육 목록 수집
        required_courses = set(level_req.get('required_courses', []))
        if job_req:
            required_courses.update(job_req.get('job_specific_courses', []))
        
        # 카테고리별 요건
        category_requirements = level_req.get('required_course_categories', {})
        
        # 최소 교육시간
        min_hours = level_req.get('min_training_hours', 0)
        
        # 필수 교육 체크
        missing_courses = list(required_courses - completed_courses)
        
        # 카테고리별 체크 (실제로는 교육 이력에서 카테고리 정보 필요)
        missing_categories = {}
        for category, required_count in category_requirements.items():
            # 여기서는 간단히 처리
            completed_in_category = 0  # 실제로는 카테고리별 완료 수 계산
            if completed_in_category < required_count:
                missing_categories[category] = {
                    'required': required_count,
                    'completed': completed_in_category
                }
        
        # 교육시간 체크
        total_hours = employee_profile.get('total_training_hours', 0)
        hours_ok = total_hours >= min_hours
        
        # 종합 판정
        courses_ok = len(missing_courses) == 0
        categories_ok = len(missing_categories) == 0
        
        if courses_ok and categories_ok and hours_ok:
            return {'passed': True, 'missing': {}}
        else:
            missing = {}
            
            if missing_courses:
                missing['courses'] = missing_courses
                missing['message'] = f'필수 교육 {len(missing_courses)}개 미이수'
            
            if missing_categories:
                missing['categories'] = missing_categories
            
            if not hours_ok:
                missing['hours'] = {
                    'current': total_hours,
                    'required': min_hours
                }
            
            return {'passed': False, 'missing': missing}
    
    def _check_skill_requirements(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict] = None
    ) -> Dict:
        """스킬 요건 체크"""
        employee_skills = set(employee_profile.get('skills', []))
        
        # 필수 스킬 목록
        required_skills = set(level_req.get('required_skills', []))
        if job_req:
            required_skills.update(job_req.get('job_specific_skills', []))
        
        # 부족한 스킬
        missing_skills = list(required_skills - employee_skills)
        
        if len(missing_skills) == 0:
            return {'passed': True, 'missing': {}}
        else:
            return {
                'passed': False,
                'missing': {
                    'skills': missing_skills,
                    'message': f'{len(missing_skills)}개 스킬 부족'
                }
            }
    
    def _check_experience_requirements(
        self,
        employee_profile: Dict,
        level_req: Dict
    ) -> Dict:
        """경력 요건 체크"""
        # 현 레벨 경력
        years_in_level = employee_profile.get('years_in_current_level', 0)
        min_years_in_level = level_req.get('min_years_in_level', 0)
        
        # 총 경력
        total_years = employee_profile.get('total_career_years', 0)
        min_total_years = level_req.get('min_total_years', 0)
        
        level_years_ok = years_in_level >= min_years_in_level
        total_years_ok = total_years >= min_total_years
        
        if level_years_ok and total_years_ok:
            return {'passed': True, 'missing': {}}
        else:
            missing = {}
            
            if not level_years_ok:
                missing['level_years'] = {
                    'current': years_in_level,
                    'required': min_years_in_level,
                    'shortage': min_years_in_level - years_in_level
                }
            
            if not total_years_ok:
                missing['total_years'] = {
                    'current': total_years,
                    'required': min_total_years,
                    'shortage': min_total_years - total_years
                }
            
            missing['message'] = '경력 요건 미충족'
            
            return {'passed': False, 'missing': missing}
    
    def _compare_grades(self, grade1: str, grade2: str) -> int:
        """평가 등급 비교 (grade1 - grade2)"""
        val1 = self.grade_hierarchy.get(grade1, 0)
        val2 = self.grade_hierarchy.get(grade2, 0)
        return val1 - val2
    
    def _estimate_certification_date(self, missing_requirements: Dict) -> Optional[str]:
        """예상 인증 가능일 계산"""
        estimated_days = 0
        
        # 평가 요건
        if missing_requirements.get('evaluation'):
            eval_missing = missing_requirements['evaluation']
            if 'consecutive_required' in eval_missing:
                # 분기별 평가 가정 (3개월)
                remaining = eval_missing['consecutive_required'] - eval_missing.get('consecutive_count', 0)
                estimated_days = max(estimated_days, remaining * 90)
        
        # 교육 요건
        if missing_requirements.get('training'):
            training_missing = missing_requirements['training']
            if 'courses' in training_missing:
                # 교육당 평균 1개월 소요 가정
                estimated_days = max(estimated_days, len(training_missing['courses']) * 30)
            
            if 'hours' in training_missing:
                # 시간 부족분을 월 20시간으로 계산
                shortage = training_missing['hours']['required'] - training_missing['hours']['current']
                months_needed = shortage / 20
                estimated_days = max(estimated_days, months_needed * 30)
        
        # 스킬 요건
        if missing_requirements.get('skills'):
            skills_missing = missing_requirements['skills']
            if 'skills' in skills_missing:
                # 스킬당 평균 2개월 소요 가정
                estimated_days = max(estimated_days, len(skills_missing['skills']) * 60)
        
        # 경력 요건
        if missing_requirements.get('experience'):
            exp_missing = missing_requirements['experience']
            if 'level_years' in exp_missing:
                shortage_years = exp_missing['level_years']['shortage']
                estimated_days = max(estimated_days, shortage_years * 365)
            
            if 'total_years' in exp_missing:
                shortage_years = exp_missing['total_years']['shortage']
                estimated_days = max(estimated_days, shortage_years * 365)
        
        if estimated_days > 0:
            expected_date = datetime.now() + timedelta(days=estimated_days)
            return expected_date.strftime('%Y-%m-%d')
        
        return None
    
    def _generate_recommendations(self, missing_requirements: Dict) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []
        
        # 평가 관련
        if missing_requirements.get('evaluation'):
            eval_missing = missing_requirements['evaluation']
            if 'required_grade' in eval_missing:
                recommendations.append(
                    f"다음 평가에서 {eval_missing['required_grade']} 이상 획득 필요"
                )
        
        # 교육 관련
        if missing_requirements.get('training'):
            training_missing = missing_requirements['training']
            if 'courses' in training_missing:
                courses_str = ', '.join(training_missing['courses'][:3])
                recommendations.append(
                    f"필수 교육 이수 필요: {courses_str} 등"
                )
        
        # 스킬 관련
        if missing_requirements.get('skills'):
            skills_missing = missing_requirements['skills']
            if 'skills' in skills_missing:
                skills_str = ', '.join(skills_missing['skills'][:3])
                recommendations.append(
                    f"스킬 개발 필요: {skills_str}"
                )
        
        # 경력 관련
        if missing_requirements.get('experience'):
            exp_missing = missing_requirements['experience']
            if 'level_years' in exp_missing:
                recommendations.append(
                    f"현 레벨에서 {exp_missing['level_years']['shortage']:.1f}년 더 경력 필요"
                )
        
        return recommendations


def calculate_certification_progress(
    current_status: Dict,
    requirements: Dict
) -> Dict:
    """
    인증 진행률 계산
    
    Returns:
        각 영역별 진행률 및 종합 진행률
    """
    progress = {
        'evaluation': 0,
        'training': 0,
        'skills': 0,
        'experience': 0,
        'overall': 0
    }
    
    # 평가 진행률
    if requirements.get('min_evaluation_grade'):
        # 등급 기반 진행률 (간단 버전)
        if current_status.get('recent_evaluation', {}).get('overall_grade'):
            progress['evaluation'] = 50  # 평가 있으면 50%
            
            grade_hierarchy = {'S': 5, 'A+': 4, 'A': 3, 'B+': 2, 'B': 1, 'C': 0}
            current = grade_hierarchy.get(
                current_status['recent_evaluation']['overall_grade'], 0
            )
            required = grade_hierarchy.get(requirements['min_evaluation_grade'], 2)
            
            if current >= required:
                progress['evaluation'] = 100
            else:
                progress['evaluation'] += (current / required) * 50
    
    # 교육 진행률
    if requirements.get('required_courses'):
        required = set(requirements['required_courses'])
        completed = set(current_status.get('completed_courses', []))
        if required:
            progress['training'] = len(completed & required) / len(required) * 100
    
    # 스킬 진행률
    if requirements.get('required_skills'):
        required = set(requirements['required_skills'])
        current = set(current_status.get('skills', []))
        if required:
            progress['skills'] = len(current & required) / len(required) * 100
    
    # 경력 진행률
    if requirements.get('min_years_in_level'):
        current_years = current_status.get('years_in_current_level', 0)
        required_years = requirements['min_years_in_level']
        if required_years > 0:
            progress['experience'] = min(100, (current_years / required_years) * 100)
    
    # 종합 진행률 (가중평균)
    weights = {
        'evaluation': 0.3,
        'training': 0.3,
        'skills': 0.25,
        'experience': 0.15
    }
    
    progress['overall'] = sum(
        progress[key] * weight 
        for key, weight in weights.items()
    )
    
    return progress