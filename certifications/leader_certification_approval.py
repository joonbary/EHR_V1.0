"""
직무요건 기반 리더 인증 자동심사 시스템
HR Rule Engine + Django Automation Architecture

이 시스템은 직원의 리더 인증 신청을 자동으로 심사하고,
직무 요건 충족도에 따라 승인/반려/추가검토를 결정합니다.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from decimal import Decimal

from django.db import models, transaction
from django.db.models import Q, Count, Avg, F, Prefetch
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

from employees.models import Employee
from evaluations.models import ComprehensiveEvaluation
from trainings.models import TrainingEnrollment, TrainingCourse
from job_profiles.models import JobProfile, JobRole
from .models import (
    GrowthLevelRequirement, JobLevelRequirement,
    GrowthLevelCertification, CertificationCheckLog
)

logger = logging.getLogger(__name__)


# ===========================
# 1. 도메인 모델 및 열거형
# ===========================

class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "PENDING"              # 검토 대기
    AUTO_APPROVED = "AUTO_APPROVED"  # 자동 승인
    AUTO_REJECTED = "AUTO_REJECTED"  # 자동 반려
    MANUAL_REVIEW = "MANUAL_REVIEW"  # 수동 검토 필요
    APPROVED = "APPROVED"            # 최종 승인
    REJECTED = "REJECTED"            # 최종 반려
    EXPIRED = "EXPIRED"              # 만료


class RequirementType(Enum):
    """요건 유형"""
    EVALUATION = "EVALUATION"        # 평가
    TRAINING = "TRAINING"            # 교육
    SKILLS = "SKILLS"                # 스킬
    EXPERIENCE = "EXPERIENCE"        # 경력
    LEADERSHIP = "LEADERSHIP"        # 리더십 경험
    SPECIAL = "SPECIAL"              # 특수 요건


@dataclass
class ValidationResult:
    """검증 결과"""
    requirement_type: RequirementType
    is_satisfied: bool
    score: float  # 0.0 ~ 1.0
    details: Dict[str, Any]
    missing_items: List[str] = field(default_factory=list)
    recommendation: Optional[str] = None


@dataclass
class ApprovalDecision:
    """승인 결정"""
    status: ApprovalStatus
    score: float  # 종합 점수
    validation_results: List[ValidationResult]
    reasons: List[str]
    recommendations: List[str]
    next_review_date: Optional[datetime] = None
    auto_approved: bool = False


# ===========================
# 2. 인증 심사 규칙 엔진
# ===========================

class CertificationRuleEngine:
    """인증 심사 규칙 엔진"""
    
    def __init__(self):
        self.min_auto_approval_score = 0.85  # 자동 승인 최소 점수
        self.min_manual_review_score = 0.70  # 수동 검토 최소 점수
        self.weight_config = {
            RequirementType.EVALUATION: 0.30,
            RequirementType.TRAINING: 0.25,
            RequirementType.SKILLS: 0.20,
            RequirementType.EXPERIENCE: 0.15,
            RequirementType.LEADERSHIP: 0.10
        }
    
    def evaluate_certification(
        self,
        employee_profile: Dict,
        target_level_requirements: Dict,
        job_specific_requirements: Optional[Dict] = None,
        target_job_profile: Optional[Dict] = None
    ) -> ApprovalDecision:
        """인증 신청 평가"""
        
        validation_results = []
        
        # 1. 평가 요건 검증
        eval_result = self._validate_evaluation_requirement(
            employee_profile, target_level_requirements, job_specific_requirements
        )
        validation_results.append(eval_result)
        
        # 2. 교육 요건 검증
        training_result = self._validate_training_requirement(
            employee_profile, target_level_requirements, job_specific_requirements
        )
        validation_results.append(training_result)
        
        # 3. 스킬 요건 검증
        skill_result = self._validate_skill_requirement(
            employee_profile, target_level_requirements, job_specific_requirements
        )
        validation_results.append(skill_result)
        
        # 4. 경력 요건 검증
        exp_result = self._validate_experience_requirement(
            employee_profile, target_level_requirements
        )
        validation_results.append(exp_result)
        
        # 5. 리더십 경험 검증 (리더 레벨인 경우)
        if self._is_leadership_level(target_level_requirements.get('level')):
            leadership_result = self._validate_leadership_requirement(
                employee_profile, target_job_profile
            )
            validation_results.append(leadership_result)
        
        # 6. 종합 평가 및 결정
        decision = self._make_approval_decision(validation_results)
        
        return decision
    
    def _validate_evaluation_requirement(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict]
    ) -> ValidationResult:
        """평가 요건 검증"""
        
        required_grade = level_req.get('min_evaluation_grade', 'B+')
        if job_req and job_req.get('override_eval_grade'):
            required_grade = job_req['override_eval_grade']
        
        consecutive_required = level_req.get('consecutive_evaluations', 1)
        eval_history = employee_profile.get('evaluation_history', [])
        
        # 최근 평가 확인
        if not eval_history:
            return ValidationResult(
                requirement_type=RequirementType.EVALUATION,
                is_satisfied=False,
                score=0.0,
                details={'message': '평가 이력이 없습니다'},
                missing_items=['평가 이력']
            )
        
        # 연속 평가 체크
        grade_values = {'S': 5, 'A+': 4, 'A': 3, 'B+': 2, 'B': 1, 'C': 0}
        required_value = grade_values.get(required_grade, 2)
        
        consecutive_count = 0
        total_score = 0
        
        for i, eval in enumerate(eval_history[:consecutive_required]):
            grade = eval.get('overall_grade', 'C')
            grade_value = grade_values.get(grade, 0)
            
            if grade_value >= required_value:
                consecutive_count += 1
                # 최근 평가일수록 가중치 높음
                weight = 1.0 - (i * 0.1)
                total_score += (grade_value / 5.0) * weight
            else:
                break
        
        is_satisfied = consecutive_count >= consecutive_required
        score = min(1.0, total_score / consecutive_required)
        
        details = {
            'required_grade': required_grade,
            'consecutive_required': consecutive_required,
            'consecutive_achieved': consecutive_count,
            'recent_grades': [e.get('overall_grade') for e in eval_history[:3]]
        }
        
        missing_items = []
        if not is_satisfied:
            missing_items.append(f"{consecutive_required}회 연속 {required_grade} 이상")
        
        recommendation = None
        if score >= 0.8 and not is_satisfied:
            recommendation = "다음 평가에서 목표 등급 달성 시 요건 충족 가능"
        
        return ValidationResult(
            requirement_type=RequirementType.EVALUATION,
            is_satisfied=is_satisfied,
            score=score,
            details=details,
            missing_items=missing_items,
            recommendation=recommendation
        )
    
    def _validate_training_requirement(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict]
    ) -> ValidationResult:
        """교육 요건 검증"""
        
        completed_courses = set(employee_profile.get('completed_courses', []))
        required_courses = set(level_req.get('required_courses', []))
        
        if job_req:
            required_courses.update(job_req.get('job_specific_courses', []))
        
        # 필수 교육 충족도
        missing_courses = list(required_courses - completed_courses)
        course_completion_rate = len(required_courses & completed_courses) / max(len(required_courses), 1)
        
        # 교육 시간 충족도
        min_hours = level_req.get('min_training_hours', 0)
        total_hours = employee_profile.get('total_training_hours', 0)
        hours_completion_rate = min(1.0, total_hours / max(min_hours, 1))
        
        # 카테고리별 요건
        category_req = level_req.get('required_course_categories', {})
        category_completion = employee_profile.get('course_categories_completed', {})
        
        category_scores = []
        for category, required_count in category_req.items():
            completed_count = category_completion.get(category, 0)
            category_scores.append(min(1.0, completed_count / required_count))
        
        category_completion_rate = sum(category_scores) / max(len(category_scores), 1) if category_scores else 1.0
        
        # 종합 점수 (가중 평균)
        score = (
            course_completion_rate * 0.5 +
            hours_completion_rate * 0.3 +
            category_completion_rate * 0.2
        )
        
        is_satisfied = (
            len(missing_courses) == 0 and
            total_hours >= min_hours and
            category_completion_rate == 1.0
        )
        
        details = {
            'required_courses': list(required_courses),
            'completed_courses': list(completed_courses),
            'missing_courses': missing_courses,
            'total_hours': total_hours,
            'min_hours': min_hours,
            'category_completion': category_completion
        }
        
        missing_items = missing_courses.copy()
        if total_hours < min_hours:
            missing_items.append(f"교육시간 {min_hours - total_hours}시간 부족")
        
        recommendation = None
        if score >= 0.7 and not is_satisfied:
            recommendation = f"우선순위: {', '.join(missing_courses[:2])}" if missing_courses else "교육시간 추가 이수 필요"
        
        return ValidationResult(
            requirement_type=RequirementType.TRAINING,
            is_satisfied=is_satisfied,
            score=score,
            details=details,
            missing_items=missing_items,
            recommendation=recommendation
        )
    
    def _validate_skill_requirement(
        self,
        employee_profile: Dict,
        level_req: Dict,
        job_req: Optional[Dict]
    ) -> ValidationResult:
        """스킬 요건 검증"""
        
        employee_skills = set(employee_profile.get('skills', []))
        required_skills = set(level_req.get('required_skills', []))
        
        if job_req:
            required_skills.update(job_req.get('job_specific_skills', []))
        
        # 스킬 매칭
        missing_skills = list(required_skills - employee_skills)
        skill_match_rate = len(required_skills & employee_skills) / max(len(required_skills), 1)
        
        # 스킬 레벨 고려 (있는 경우)
        skill_levels = employee_profile.get('skill_levels', {})
        skill_proficiency = level_req.get('skill_proficiency_level', 'INTERMEDIATE')
        
        proficiency_scores = []
        for skill in (required_skills & employee_skills):
            emp_level = skill_levels.get(skill, 'BASIC')
            if self._compare_skill_levels(emp_level, skill_proficiency) >= 0:
                proficiency_scores.append(1.0)
            else:
                proficiency_scores.append(0.5)
        
        proficiency_rate = sum(proficiency_scores) / max(len(proficiency_scores), 1) if proficiency_scores else 0
        
        # 종합 점수
        score = skill_match_rate * 0.7 + proficiency_rate * 0.3
        is_satisfied = len(missing_skills) == 0 and proficiency_rate >= 0.8
        
        details = {
            'required_skills': list(required_skills),
            'employee_skills': list(employee_skills),
            'missing_skills': missing_skills,
            'skill_match_rate': skill_match_rate,
            'proficiency_rate': proficiency_rate
        }
        
        missing_items = missing_skills.copy()
        
        recommendation = None
        if score >= 0.6 and not is_satisfied:
            if missing_skills:
                recommendation = f"핵심 스킬 개발 필요: {', '.join(missing_skills[:2])}"
            else:
                recommendation = "보유 스킬의 숙련도 향상 필요"
        
        return ValidationResult(
            requirement_type=RequirementType.SKILLS,
            is_satisfied=is_satisfied,
            score=score,
            details=details,
            missing_items=missing_items,
            recommendation=recommendation
        )
    
    def _validate_experience_requirement(
        self,
        employee_profile: Dict,
        level_req: Dict
    ) -> ValidationResult:
        """경력 요건 검증"""
        
        # 현 레벨 경력
        years_in_level = employee_profile.get('years_in_current_level', 0)
        min_years_in_level = level_req.get('min_years_in_level', 0)
        
        # 총 경력
        total_years = employee_profile.get('total_career_years', 0)
        min_total_years = level_req.get('min_total_years', 0)
        
        # 충족도 계산
        level_exp_rate = min(1.0, years_in_level / max(min_years_in_level, 0.1))
        total_exp_rate = min(1.0, total_years / max(min_total_years, 0.1))
        
        score = (level_exp_rate + total_exp_rate) / 2
        is_satisfied = years_in_level >= min_years_in_level and total_years >= min_total_years
        
        details = {
            'years_in_level': years_in_level,
            'min_years_in_level': min_years_in_level,
            'total_years': total_years,
            'min_total_years': min_total_years
        }
        
        missing_items = []
        if years_in_level < min_years_in_level:
            missing_items.append(f"현 레벨 경력 {min_years_in_level - years_in_level:.1f}년 부족")
        if total_years < min_total_years:
            missing_items.append(f"총 경력 {min_total_years - total_years:.1f}년 부족")
        
        recommendation = None
        if score >= 0.8 and not is_satisfied:
            months_needed = max(
                (min_years_in_level - years_in_level) * 12,
                (min_total_years - total_years) * 12
            )
            recommendation = f"약 {int(months_needed)}개월 후 충족 예상"
        
        return ValidationResult(
            requirement_type=RequirementType.EXPERIENCE,
            is_satisfied=is_satisfied,
            score=score,
            details=details,
            missing_items=missing_items,
            recommendation=recommendation
        )
    
    def _validate_leadership_requirement(
        self,
        employee_profile: Dict,
        target_job_profile: Optional[Dict]
    ) -> ValidationResult:
        """리더십 경험 검증"""
        
        leadership_exp = employee_profile.get('leadership_experience', {})
        
        # 리더십 경험 유무
        has_leadership = leadership_exp.get('years', 0) > 0
        leadership_years = leadership_exp.get('years', 0)
        leadership_type = leadership_exp.get('type', '')
        
        # 팀 규모 경험
        team_size = leadership_exp.get('max_team_size', 0)
        min_team_size = 5  # 기본 최소 팀 규모
        
        if target_job_profile:
            # 직무에 따른 요구 팀 규모 조정
            if '본부' in target_job_profile.get('name', ''):
                min_team_size = 20
            elif '팀장' in target_job_profile.get('name', ''):
                min_team_size = 10
        
        # 리더십 성과
        leadership_achievements = employee_profile.get('leadership_achievements', [])
        achievement_score = min(1.0, len(leadership_achievements) / 3)  # 3개 이상이면 만점
        
        # 종합 점수
        exp_score = min(1.0, leadership_years / 3)  # 3년 이상이면 만점
        size_score = min(1.0, team_size / min_team_size)
        
        score = (exp_score * 0.4 + size_score * 0.3 + achievement_score * 0.3)
        is_satisfied = has_leadership and leadership_years >= 1 and team_size >= min_team_size
        
        details = {
            'has_leadership': has_leadership,
            'leadership_years': leadership_years,
            'leadership_type': leadership_type,
            'team_size': team_size,
            'min_team_size': min_team_size,
            'achievements': len(leadership_achievements)
        }
        
        missing_items = []
        if not has_leadership:
            missing_items.append("리더십 경험 없음")
        elif team_size < min_team_size:
            missing_items.append(f"최소 {min_team_size}명 이상 팀 관리 경험 필요")
        
        recommendation = None
        if score >= 0.5 and not is_satisfied:
            recommendation = "프로젝트 리더 또는 TF장 경험을 통한 리더십 역량 개발 권장"
        
        return ValidationResult(
            requirement_type=RequirementType.LEADERSHIP,
            is_satisfied=is_satisfied,
            score=score,
            details=details,
            missing_items=missing_items,
            recommendation=recommendation
        )
    
    def _is_leadership_level(self, level: str) -> bool:
        """리더십 레벨 여부 확인"""
        return level in ['Lv.3', 'Lv.4', 'Lv.5']
    
    def _compare_skill_levels(self, level1: str, level2: str) -> int:
        """스킬 레벨 비교"""
        levels = {'BASIC': 1, 'INTERMEDIATE': 2, 'ADVANCED': 3, 'EXPERT': 4}
        return levels.get(level1, 1) - levels.get(level2, 1)
    
    def _make_approval_decision(
        self,
        validation_results: List[ValidationResult]
    ) -> ApprovalDecision:
        """승인 결정"""
        
        # 가중 평균 점수 계산
        total_score = 0
        total_weight = 0
        
        for result in validation_results:
            weight = self.weight_config.get(result.requirement_type, 0.1)
            total_score += result.score * weight
            total_weight += weight
        
        final_score = total_score / total_weight if total_weight > 0 else 0
        
        # 필수 요건 체크
        mandatory_types = [RequirementType.EVALUATION, RequirementType.EXPERIENCE]
        mandatory_satisfied = all(
            r.is_satisfied for r in validation_results
            if r.requirement_type in mandatory_types
        )
        
        # 전체 충족 여부
        all_satisfied = all(r.is_satisfied for r in validation_results)
        
        # 승인 상태 결정
        if all_satisfied and final_score >= self.min_auto_approval_score:
            status = ApprovalStatus.AUTO_APPROVED
            auto_approved = True
        elif not mandatory_satisfied or final_score < self.min_manual_review_score:
            status = ApprovalStatus.AUTO_REJECTED
            auto_approved = False
        else:
            status = ApprovalStatus.MANUAL_REVIEW
            auto_approved = False
        
        # 사유 및 권고사항 생성
        reasons = []
        recommendations = []
        
        for result in validation_results:
            if not result.is_satisfied:
                reasons.append(f"{result.requirement_type.value}: {', '.join(result.missing_items)}")
            
            if result.recommendation:
                recommendations.append(result.recommendation)
        
        # 다음 검토일 설정 (수동 검토 필요시)
        next_review_date = None
        if status == ApprovalStatus.MANUAL_REVIEW:
            next_review_date = datetime.now() + timedelta(days=3)
        
        return ApprovalDecision(
            status=status,
            score=final_score,
            validation_results=validation_results,
            reasons=reasons or ["모든 요건을 충족합니다."],
            recommendations=recommendations,
            next_review_date=next_review_date,
            auto_approved=auto_approved
        )


# ===========================
# 3. 워크플로우 관리
# ===========================

class CertificationWorkflow:
    """인증 워크플로우 관리"""
    
    def __init__(self):
        self.rule_engine = CertificationRuleEngine()
        self.notification_service = NotificationService()
    
    @transaction.atomic
    def process_certification_application(
        self,
        certification_id: str
    ) -> Dict[str, Any]:
        """인증 신청 처리"""
        
        try:
            # 1. 인증 신청 조회
            certification = GrowthLevelCertification.objects.select_for_update().get(
                id=certification_id,
                status='PENDING'
            )
            
            # 2. 직원 프로파일 구성
            employee_profile = self._build_employee_profile(certification.employee)
            
            # 3. 요건 조회
            level_requirements = self._get_level_requirements(certification.growth_level)
            job_requirements = self._get_job_requirements(
                certification.employee,
                certification.growth_level
            )
            
            # 4. 자동 심사 실행
            decision = self.rule_engine.evaluate_certification(
                employee_profile=employee_profile,
                target_level_requirements=level_requirements,
                job_specific_requirements=job_requirements
            )
            
            # 5. 결과 저장
            self._update_certification_status(certification, decision)
            
            # 6. 워크플로우 액션 실행
            self._execute_workflow_actions(certification, decision)
            
            # 7. 알림 발송
            self._send_notifications(certification, decision)
            
            # 8. 로그 기록
            self._log_certification_decision(certification, decision)
            
            return {
                'success': True,
                'certification_id': str(certification.id),
                'decision': {
                    'status': decision.status.value,
                    'score': decision.score,
                    'auto_approved': decision.auto_approved,
                    'reasons': decision.reasons,
                    'recommendations': decision.recommendations
                }
            }
            
        except GrowthLevelCertification.DoesNotExist:
            return {
                'success': False,
                'error': 'Certification not found or not in pending status'
            }
        except Exception as e:
            logger.error(f"Certification processing error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_employee_profile(self, employee: Employee) -> Dict:
        """직원 프로파일 구성"""
        from certifications.certification_services import CertificationService
        service = CertificationService()
        return service._build_employee_profile(employee)
    
    def _get_level_requirements(self, level: str) -> Dict:
        """레벨 요건 조회"""
        try:
            req = GrowthLevelRequirement.objects.get(level=level, is_active=True)
            return {
                'level': req.level,
                'min_evaluation_grade': req.min_evaluation_grade,
                'consecutive_evaluations': req.consecutive_evaluations,
                'required_courses': req.required_courses,
                'required_course_categories': req.required_course_categories,
                'min_training_hours': req.min_training_hours,
                'required_skills': req.required_skills,
                'skill_proficiency_level': req.skill_proficiency_level,
                'min_years_in_level': req.min_years_in_level,
                'min_total_years': req.min_total_years
            }
        except GrowthLevelRequirement.DoesNotExist:
            # 기본값 반환
            return self._get_default_requirements(level)
    
    def _get_default_requirements(self, level: str) -> Dict:
        """기본 레벨 요건"""
        defaults = {
            'Lv.3': {
                'level': 'Lv.3',
                'min_evaluation_grade': 'B+',
                'consecutive_evaluations': 2,
                'required_courses': ['성과관리전략', '리더십기초'],
                'required_skills': ['성과관리', '전략수립', '조직운영'],
                'min_years_in_level': 2,
                'min_total_years': 3
            }
        }
        return defaults.get(level, defaults['Lv.3'])
    
    def _get_job_requirements(
        self,
        employee: Employee,
        level: str
    ) -> Optional[Dict]:
        """직무별 추가 요건"""
        # 직원의 목표 직무 찾기 (예: 부서 + 레벨 기반)
        # 실제로는 더 정교한 로직 필요
        return None
    
    def _update_certification_status(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """인증 상태 업데이트"""
        
        # 상태 매핑
        status_map = {
            ApprovalStatus.AUTO_APPROVED: 'CERTIFIED',
            ApprovalStatus.AUTO_REJECTED: 'REJECTED',
            ApprovalStatus.MANUAL_REVIEW: 'PENDING',
            ApprovalStatus.APPROVED: 'CERTIFIED',
            ApprovalStatus.REJECTED: 'REJECTED'
        }
        
        certification.status = status_map.get(decision.status, 'PENDING')
        
        # 자동 승인인 경우
        if decision.status == ApprovalStatus.AUTO_APPROVED:
            certification.certified_date = timezone.now()
            certification.expiry_date = timezone.now() + timedelta(days=365 * 2)  # 2년 유효
            certification.reviewed_by = None  # 시스템 자동
            certification.review_notes = "시스템 자동 승인"
        
        # 검증 결과 저장
        validation_summary = {}
        for result in decision.validation_results:
            validation_summary[result.requirement_type.value] = {
                'satisfied': result.is_satisfied,
                'score': result.score,
                'missing': result.missing_items
            }
        
        certification.missing_requirements = {
            'validation_summary': validation_summary,
            'final_score': decision.score,
            'reasons': decision.reasons,
            'recommendations': decision.recommendations
        }
        
        certification.save()
    
    def _execute_workflow_actions(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """워크플로우 액션 실행"""
        
        if decision.status == ApprovalStatus.AUTO_APPROVED:
            # 자동 승인 액션
            self._execute_approval_actions(certification)
            
        elif decision.status == ApprovalStatus.MANUAL_REVIEW:
            # 수동 검토 태스크 생성
            self._create_review_task(certification, decision)
            
        elif decision.status == ApprovalStatus.AUTO_REJECTED:
            # 반려 액션
            self._execute_rejection_actions(certification, decision)
    
    def _execute_approval_actions(self, certification: GrowthLevelCertification):
        """승인 액션 실행"""
        
        # 1. 직원 레벨 업데이트 (별도 시스템 연동)
        # 2. HR 시스템 연동
        # 3. 급여/보상 시스템 알림
        # 4. 교육 시스템 레벨 업데이트
        
        logger.info(f"Certification approved for {certification.employee.name}")
    
    def _create_review_task(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """검토 태스크 생성"""
        
        # HR 담당자에게 검토 요청 생성
        # 실제로는 태스크 관리 시스템과 연동
        
        review_data = {
            'certification_id': str(certification.id),
            'employee': certification.employee.name,
            'target_level': certification.growth_level,
            'score': decision.score,
            'missing_items': [r.missing_items for r in decision.validation_results if r.missing_items],
            'due_date': decision.next_review_date
        }
        
        # 캐시에 임시 저장 (실제로는 DB)
        cache_key = f"review_task_{certification.id}"
        cache.set(cache_key, review_data, 60 * 60 * 24 * 7)  # 7일
        
        logger.info(f"Review task created for {certification.employee.name}")
    
    def _execute_rejection_actions(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """반려 액션 실행"""
        
        # 1. 개선 계획 생성 권고
        # 2. 교육 추천 시스템 연동
        # 3. 멘토링 프로그램 추천
        
        logger.info(f"Certification rejected for {certification.employee.name}")
    
    def _send_notifications(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """알림 발송"""
        
        self.notification_service.send_certification_result(
            employee=certification.employee,
            certification=certification,
            decision=decision
        )
        
        # HR 담당자 알림 (수동 검토 필요시)
        if decision.status == ApprovalStatus.MANUAL_REVIEW:
            self.notification_service.notify_hr_review_required(
                certification=certification,
                decision=decision
            )
    
    def _log_certification_decision(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """결정 로그 기록"""
        
        CertificationCheckLog.objects.create(
            employee=certification.employee,
            target_level=certification.growth_level,
            check_result='READY' if decision.status in [ApprovalStatus.AUTO_APPROVED, ApprovalStatus.APPROVED] else 'NOT_READY',
            result_details={
                'decision_status': decision.status.value,
                'final_score': decision.score,
                'validation_results': [
                    {
                        'type': r.requirement_type.value,
                        'satisfied': r.is_satisfied,
                        'score': r.score,
                        'missing': r.missing_items
                    }
                    for r in decision.validation_results
                ],
                'auto_processed': decision.auto_approved,
                'timestamp': datetime.now().isoformat()
            },
            api_source='certification_workflow'
        )


# ===========================
# 4. 알림 서비스
# ===========================

class NotificationService:
    """알림 서비스"""
    
    def send_certification_result(
        self,
        employee: Employee,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """인증 결과 알림"""
        
        if decision.status == ApprovalStatus.AUTO_APPROVED:
            self._send_approval_notification(employee, certification)
        elif decision.status == ApprovalStatus.AUTO_REJECTED:
            self._send_rejection_notification(employee, certification, decision)
        elif decision.status == ApprovalStatus.MANUAL_REVIEW:
            self._send_review_notification(employee, certification)
    
    def _send_approval_notification(
        self,
        employee: Employee,
        certification: GrowthLevelCertification
    ):
        """승인 알림"""
        
        subject = f"축하합니다! {certification.growth_level} 인증이 승인되었습니다"
        
        context = {
            'employee_name': employee.name,
            'growth_level': certification.growth_level,
            'certified_date': certification.certified_date,
            'expiry_date': certification.expiry_date
        }
        
        # 이메일 발송 (실제 구현시)
        # message = render_to_string('certifications/approval_email.html', context)
        # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [employee.user.email])
        
        logger.info(f"Approval notification sent to {employee.name}")
    
    def _send_rejection_notification(
        self,
        employee: Employee,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """반려 알림"""
        
        subject = f"{certification.growth_level} 인증 심사 결과 안내"
        
        context = {
            'employee_name': employee.name,
            'growth_level': certification.growth_level,
            'reasons': decision.reasons,
            'recommendations': decision.recommendations,
            'score': f"{decision.score * 100:.1f}%"
        }
        
        logger.info(f"Rejection notification sent to {employee.name}")
    
    def _send_review_notification(
        self,
        employee: Employee,
        certification: GrowthLevelCertification
    ):
        """검토중 알림"""
        
        subject = f"{certification.growth_level} 인증 신청이 검토 중입니다"
        
        context = {
            'employee_name': employee.name,
            'growth_level': certification.growth_level,
            'expected_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        }
        
        logger.info(f"Review notification sent to {employee.name}")
    
    def notify_hr_review_required(
        self,
        certification: GrowthLevelCertification,
        decision: ApprovalDecision
    ):
        """HR 검토 요청 알림"""
        
        # HR 담당자 조회 (실제 구현시)
        hr_users = User.objects.filter(groups__name='HR', is_active=True)
        
        subject = f"[검토필요] {certification.employee.name}의 {certification.growth_level} 인증"
        
        context = {
            'employee': certification.employee,
            'certification': certification,
            'score': f"{decision.score * 100:.1f}%",
            'validation_summary': decision.validation_results,
            'due_date': decision.next_review_date
        }
        
        logger.info(f"HR review notification sent for {certification.employee.name}")


# ===========================
# 5. 관리자 서비스
# ===========================

class CertificationAdminService:
    """인증 관리자 서비스"""
    
    def __init__(self):
        self.workflow = CertificationWorkflow()
    
    def get_pending_reviews(self, reviewer: User) -> List[Dict]:
        """대기중인 검토 목록 조회"""
        
        # 권한 확인
        if not self._has_review_permission(reviewer):
            return []
        
        # 수동 검토 대기 건 조회
        pending_certs = GrowthLevelCertification.objects.filter(
            status='PENDING',
            missing_requirements__final_score__gte=0.7,  # 수동 검토 대상
            missing_requirements__final_score__lt=0.85   # 자동 승인 미만
        ).select_related('employee').order_by('applied_date')
        
        results = []
        for cert in pending_certs:
            # 캐시에서 검토 정보 조회
            cache_key = f"review_task_{cert.id}"
            review_data = cache.get(cache_key, {})
            
            results.append({
                'certification_id': str(cert.id),
                'employee': {
                    'id': str(cert.employee.id),
                    'name': cert.employee.name,
                    'department': cert.employee.department,
                    'position': cert.employee.position
                },
                'target_level': cert.growth_level,
                'applied_date': cert.applied_date.isoformat(),
                'score': review_data.get('score', 0),
                'missing_items': review_data.get('missing_items', []),
                'due_date': review_data.get('due_date')
            })
        
        return results
    
    @transaction.atomic
    def manual_review_decision(
        self,
        reviewer: User,
        certification_id: str,
        approved: bool,
        notes: str = ""
    ) -> Dict[str, Any]:
        """수동 검토 결정"""
        
        try:
            # 권한 확인
            if not self._has_review_permission(reviewer):
                return {'success': False, 'error': 'No permission'}
            
            # 인증 조회
            certification = GrowthLevelCertification.objects.select_for_update().get(
                id=certification_id,
                status='PENDING'
            )
            
            # 상태 업데이트
            if approved:
                certification.status = 'CERTIFIED'
                certification.certified_date = timezone.now()
                certification.expiry_date = timezone.now() + timedelta(days=365 * 2)
            else:
                certification.status = 'REJECTED'
            
            certification.reviewed_by = reviewer
            certification.review_notes = notes
            certification.save()
            
            # 워크플로우 액션
            if approved:
                self.workflow._execute_approval_actions(certification)
            else:
                # 반려 사유와 함께 액션 실행
                decision = ApprovalDecision(
                    status=ApprovalStatus.REJECTED,
                    score=0,
                    validation_results=[],
                    reasons=[notes],
                    recommendations=[]
                )
                self.workflow._execute_rejection_actions(certification, decision)
            
            # 알림 발송
            self._send_manual_review_notification(certification, approved, notes)
            
            # 로그 기록
            CertificationCheckLog.objects.create(
                employee=certification.employee,
                target_level=certification.growth_level,
                check_result='READY' if approved else 'NOT_READY',
                result_details={
                    'manual_review': True,
                    'reviewer': reviewer.username,
                    'approved': approved,
                    'notes': notes,
                    'timestamp': datetime.now().isoformat()
                },
                api_source='manual_review'
            )
            
            return {
                'success': True,
                'certification_id': str(certification.id),
                'status': certification.status
            }
            
        except GrowthLevelCertification.DoesNotExist:
            return {'success': False, 'error': 'Certification not found'}
        except Exception as e:
            logger.error(f"Manual review error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_certification_analytics(self, date_from: datetime, date_to: datetime) -> Dict:
        """인증 분석 데이터"""
        
        # 기간 내 인증 통계
        certifications = GrowthLevelCertification.objects.filter(
            applied_date__range=[date_from, date_to]
        )
        
        # 상태별 집계
        status_counts = certifications.values('status').annotate(
            count=Count('id')
        )
        
        # 레벨별 집계
        level_counts = certifications.values('growth_level').annotate(
            count=Count('id')
        )
        
        # 자동 처리율
        auto_processed = CertificationCheckLog.objects.filter(
            checked_at__range=[date_from, date_to],
            result_details__auto_processed=True
        ).count()
        
        total_processed = CertificationCheckLog.objects.filter(
            checked_at__range=[date_from, date_to]
        ).count()
        
        auto_rate = (auto_processed / total_processed * 100) if total_processed > 0 else 0
        
        return {
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'total_applications': certifications.count(),
            'status_distribution': {
                item['status']: item['count'] 
                for item in status_counts
            },
            'level_distribution': {
                item['growth_level']: item['count'] 
                for item in level_counts
            },
            'auto_processing_rate': auto_rate,
            'average_processing_time': self._calculate_avg_processing_time(certifications)
        }
    
    def _has_review_permission(self, user: User) -> bool:
        """검토 권한 확인"""
        return user.groups.filter(name='HR').exists() or user.is_superuser
    
    def _send_manual_review_notification(
        self,
        certification: GrowthLevelCertification,
        approved: bool,
        notes: str
    ):
        """수동 검토 결과 알림"""
        notification_service = NotificationService()
        
        if approved:
            notification_service._send_approval_notification(
                certification.employee,
                certification
            )
        else:
            decision = ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                score=0,
                validation_results=[],
                reasons=[notes],
                recommendations=[]
            )
            notification_service._send_rejection_notification(
                certification.employee,
                certification,
                decision
            )
    
    def _calculate_avg_processing_time(
        self,
        certifications
    ) -> float:
        """평균 처리 시간 계산"""
        
        processed = certifications.exclude(
            status='PENDING'
        ).exclude(
            certified_date__isnull=True
        )
        
        if not processed.exists():
            return 0
        
        total_hours = 0
        count = 0
        
        for cert in processed:
            if cert.certified_date:
                delta = cert.certified_date - cert.applied_date
                total_hours += delta.total_seconds() / 3600
                count += 1
        
        return total_hours / count if count > 0 else 0


# ===========================
# 6. 실행 및 테스트
# ===========================

if __name__ == "__main__":
    """
    테스트 실행 예시
    """
    
    # Django 환경 설정
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ehr_system.settings')
    django.setup()
    
    # 테스트 데이터
    test_employee_profile = {
        'employee_id': 'E001',
        'name': '김과장',
        'level': 'Lv.2',
        'position': '과장',
        'department': '전략기획팀',
        'evaluation_history': [
            {'overall_grade': 'A'},
            {'overall_grade': 'A'},
            {'overall_grade': 'B+'}
        ],
        'completed_courses': ['성과관리전략', '리더십기초'],
        'total_training_hours': 120,
        'skills': ['성과관리', '전략수립', '프로젝트관리'],
        'years_in_current_level': 2.5,
        'total_career_years': 7,
        'leadership_experience': {
            'years': 2,
            'type': 'TF장',
            'max_team_size': 8
        }
    }
    
    test_level_requirements = {
        'level': 'Lv.3',
        'min_evaluation_grade': 'B+',
        'consecutive_evaluations': 2,
        'required_courses': ['성과관리전략', '리더십기초', '조직운영실무'],
        'required_skills': ['성과관리', '전략수립', '조직운영'],
        'min_years_in_level': 2,
        'min_total_years': 5
    }
    
    # 규칙 엔진 테스트
    engine = CertificationRuleEngine()
    decision = engine.evaluate_certification(
        employee_profile=test_employee_profile,
        target_level_requirements=test_level_requirements
    )
    
    print(f"인증 심사 결과")
    print(f"상태: {decision.status.value}")
    print(f"점수: {decision.score:.2%}")
    print(f"자동 승인: {decision.auto_approved}")
    print(f"\n사유:")
    for reason in decision.reasons:
        print(f"  - {reason}")
    print(f"\n권고사항:")
    for rec in decision.recommendations:
        print(f"  - {rec}")