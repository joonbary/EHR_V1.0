"""
성장레벨 인증 관련 모델
"""

from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from job_profiles.models import JobProfile
import uuid


class GrowthLevelRequirement(models.Model):
    """성장레벨별 인증 요건"""
    level = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='성장레벨',
        help_text='예: Lv.1, Lv.2, Lv.3, Lv.4, Lv.5'
    )
    level_name = models.CharField(max_length=50, verbose_name='레벨명')
    
    # 평가 요건
    min_evaluation_grade = models.CharField(
        max_length=10,
        verbose_name='최소 평가등급',
        help_text='예: B+, A, A+, S'
    )
    consecutive_evaluations = models.IntegerField(
        default=1,
        verbose_name='연속 평가 횟수',
        help_text='최소 등급 이상을 받아야 하는 연속 평가 횟수'
    )
    
    # 교육 요건
    required_courses = models.JSONField(
        default=list,
        verbose_name='필수 교육과정',
        help_text='과정 코드 리스트'
    )
    required_course_categories = models.JSONField(
        default=dict,
        verbose_name='카테고리별 필수 교육 수',
        help_text='예: {"리더십": 2, "직무역량": 3}'
    )
    min_training_hours = models.IntegerField(
        default=0,
        verbose_name='최소 교육시간'
    )
    
    # 스킬 요건
    required_skills = models.JSONField(
        default=list,
        verbose_name='필수 스킬',
        help_text='스킬 리스트'
    )
    skill_proficiency_level = models.CharField(
        max_length=20,
        default='INTERMEDIATE',
        verbose_name='스킬 숙련도',
        choices=[
            ('BASIC', '기초'),
            ('INTERMEDIATE', '중급'),
            ('ADVANCED', '고급'),
            ('EXPERT', '전문가')
        ]
    )
    
    # 경력 요건
    min_years_in_level = models.FloatField(
        default=0,
        verbose_name='현 레벨 최소 경력(년)'
    )
    min_total_years = models.FloatField(
        default=0,
        verbose_name='총 경력 최소(년)'
    )
    
    # 추가 요건
    additional_requirements = models.JSONField(
        default=dict,
        verbose_name='추가 요건',
        help_text='기타 특수 요건'
    )
    
    # 메타 정보
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '성장레벨 요건'
        verbose_name_plural = '성장레벨 요건'
        ordering = ['level']
    
    def __str__(self):
        return f"{self.level} - {self.level_name}"


class JobLevelRequirement(models.Model):
    """직무별 성장레벨 요건"""
    job_profile = models.ForeignKey(
        JobProfile,
        on_delete=models.CASCADE,
        verbose_name='직무프로파일'
    )
    required_growth_level = models.CharField(
        max_length=10,
        verbose_name='필수 성장레벨'
    )
    
    # 직무별 추가 요건
    job_specific_courses = models.JSONField(
        default=list,
        verbose_name='직무별 필수 교육',
        help_text='해당 직무에만 필요한 추가 교육'
    )
    job_specific_skills = models.JSONField(
        default=list,
        verbose_name='직무별 필수 스킬',
        help_text='해당 직무에만 필요한 추가 스킬'
    )
    
    # 평가 요건 오버라이드
    override_eval_grade = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='평가등급 오버라이드',
        help_text='비어있으면 레벨 기본값 사용'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '직무별 레벨 요건'
        verbose_name_plural = '직무별 레벨 요건'
        unique_together = [['job_profile', 'required_growth_level']]
    
    def __str__(self):
        return f"{self.job_profile.job_role.name} - {self.required_growth_level}"


class GrowthLevelCertification(models.Model):
    """성장레벨 인증 기록"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    growth_level = models.CharField(max_length=10, verbose_name='인증레벨')
    
    # 인증 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', '검토중'),
            ('CERTIFIED', '인증완료'),
            ('REJECTED', '반려'),
            ('EXPIRED', '만료')
        ],
        default='PENDING',
        verbose_name='상태'
    )
    
    # 인증 일자
    applied_date = models.DateTimeField(auto_now_add=True, verbose_name='신청일')
    certified_date = models.DateTimeField(null=True, blank=True, verbose_name='인증일')
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name='만료일')
    
    # 인증 시점 스냅샷
    certification_snapshot = models.JSONField(
        default=dict,
        verbose_name='인증시점 데이터',
        help_text='인증 당시의 평가, 교육, 스킬 정보'
    )
    
    # 인증 결과
    evaluation_check = models.BooleanField(default=False, verbose_name='평가요건충족')
    training_check = models.BooleanField(default=False, verbose_name='교육요건충족')
    skill_check = models.BooleanField(default=False, verbose_name='스킬요건충족')
    experience_check = models.BooleanField(default=False, verbose_name='경력요건충족')
    
    missing_requirements = models.JSONField(
        default=dict,
        verbose_name='미충족 요건',
        help_text='부족한 요건 상세'
    )
    
    # 검토 정보
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='검토자'
    )
    review_notes = models.TextField(blank=True, verbose_name='검토의견')
    
    class Meta:
        verbose_name = '성장레벨 인증'
        verbose_name_plural = '성장레벨 인증'
        ordering = ['-applied_date']
        unique_together = [['employee', 'growth_level', 'status']]
    
    def __str__(self):
        return f"{self.employee.name} - {self.growth_level} ({self.get_status_display()})"


class CertificationCheckLog(models.Model):
    """인증 체크 로그"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    target_level = models.CharField(max_length=10, verbose_name='목표레벨')
    target_job = models.CharField(max_length=100, blank=True, verbose_name='목표직무')
    
    # 체크 시점
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='체크시점')
    
    # 체크 결과
    check_result = models.CharField(
        max_length=20,
        choices=[
            ('READY', '인증가능'),
            ('NOT_READY', '미충족'),
            ('PARTIAL', '부분충족')
        ],
        verbose_name='체크결과'
    )
    
    # 상세 결과
    result_details = models.JSONField(
        default=dict,
        verbose_name='결과상세',
        help_text='각 요건별 충족 여부 및 부족 사항'
    )
    
    # 예상 인증일
    expected_certification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='예상인증일'
    )
    
    # API 호출 정보
    api_source = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='API출처',
        help_text='어떤 API에서 호출되었는지'
    )
    
    class Meta:
        verbose_name = '인증체크로그'
        verbose_name_plural = '인증체크로그'
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.employee.name} - {self.target_level} ({self.checked_at.strftime('%Y-%m-%d')})"