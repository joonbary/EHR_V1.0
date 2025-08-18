"""
교육 과정 모델
"""

from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
import uuid


class TrainingCategory(models.Model):
    """교육 카테고리"""
    name = models.CharField(max_length=100, verbose_name='카테고리명')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '교육 카테고리'
        verbose_name_plural = '교육 카테고리'
    
    def __str__(self):
        return self.name


class TrainingCourse(models.Model):
    """교육 과정"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_code = models.CharField(max_length=50, unique=True, verbose_name='과정코드')
    title = models.CharField(max_length=200, verbose_name='과정명')
    category = models.ForeignKey(TrainingCategory, on_delete=models.SET_NULL, null=True, verbose_name='카테고리')
    
    # 교육 내용
    description = models.TextField(verbose_name='과정 설명')
    objectives = models.JSONField(default=list, verbose_name='학습목표')
    target_audience = models.TextField(blank=True, verbose_name='대상자')
    
    # 스킬 매핑
    related_skills = models.JSONField(default=list, verbose_name='관련 스킬')
    skill_level = models.CharField(
        max_length=20,
        choices=[
            ('BASIC', '기초'),
            ('INTERMEDIATE', '중급'),
            ('ADVANCED', '고급'),
            ('EXPERT', '전문가')
        ],
        default='INTERMEDIATE',
        verbose_name='스킬 수준'
    )
    
    # 교육 정보
    duration_hours = models.IntegerField(default=8, verbose_name='교육시간')
    course_type = models.CharField(
        max_length=20,
        choices=[
            ('ONLINE', '온라인'),
            ('OFFLINE', '오프라인'),
            ('BLENDED', '혼합형'),
            ('SELF_STUDY', '자율학습')
        ],
        default='ONLINE',
        verbose_name='교육유형'
    )
    
    # 성장레벨 연계
    min_growth_level = models.CharField(max_length=10, blank=True, verbose_name='최소 성장레벨')
    certification_eligible = models.BooleanField(default=False, verbose_name='인증교육여부')
    growth_level_impact = models.JSONField(
        default=dict,
        verbose_name='성장레벨 영향',
        help_text='예: {"Lv.3": 0.2, "Lv.4": 0.1}'
    )
    
    # 메타 정보
    provider = models.CharField(max_length=100, blank=True, verbose_name='교육제공처')
    cost = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name='비용')
    is_mandatory = models.BooleanField(default=False, verbose_name='필수교육여부')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '교육과정'
        verbose_name_plural = '교육과정'
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"[{self.course_code}] {self.title}"


class TrainingEnrollment(models.Model):
    """교육 수강 신청"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, verbose_name='교육과정')
    
    # 수강 상태
    status = models.CharField(
        max_length=20,
        choices=[
            ('APPLIED', '신청'),
            ('APPROVED', '승인'),
            ('REJECTED', '반려'),
            ('IN_PROGRESS', '수강중'),
            ('COMPLETED', '이수'),
            ('INCOMPLETE', '미이수'),
            ('CANCELLED', '취소')
        ],
        default='APPLIED',
        verbose_name='상태'
    )
    
    # 수강 정보
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name='신청일')
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name='승인일')
    start_date = models.DateField(null=True, blank=True, verbose_name='수강시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='수강종료일')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name='이수일')
    
    # 평가 정보
    attendance_rate = models.FloatField(default=0, verbose_name='출석률')
    test_score = models.FloatField(null=True, blank=True, verbose_name='평가점수')
    satisfaction_score = models.IntegerField(null=True, blank=True, verbose_name='만족도')
    
    # 추천 정보
    recommendation_reason = models.TextField(blank=True, verbose_name='추천사유')
    recommendation_priority = models.IntegerField(default=50, verbose_name='추천우선순위')
    
    # 기타
    notes = models.TextField(blank=True, verbose_name='비고')
    
    class Meta:
        verbose_name = '교육수강'
        verbose_name_plural = '교육수강'
        unique_together = [['employee', 'course', 'start_date']]
        ordering = ['-enrolled_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.course.title}"


class TrainingRecommendation(models.Model):
    """교육 추천 이력"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    course = models.ForeignKey(TrainingCourse, on_delete=models.CASCADE, verbose_name='교육과정')
    
    # 추천 컨텍스트
    target_job = models.CharField(max_length=100, verbose_name='목표직무')
    missing_skills = models.JSONField(default=list, verbose_name='부족스킬')
    match_score = models.FloatField(verbose_name='매치점수')
    priority = models.IntegerField(verbose_name='우선순위')
    
    # 추천 사유
    recommendation_type = models.CharField(
        max_length=30,
        choices=[
            ('SKILL_GAP', '스킬갭 해소'),
            ('GROWTH_LEVEL', '성장레벨 향상'),
            ('MANDATORY', '필수교육'),
            ('CAREER_PATH', '경력개발'),
            ('PERFORMANCE', '성과향상')
        ],
        verbose_name='추천유형'
    )
    recommendation_comment = models.TextField(verbose_name='추천코멘트')
    
    # 추천 결과
    is_enrolled = models.BooleanField(default=False, verbose_name='수강신청여부')
    enrolled_date = models.DateTimeField(null=True, blank=True, verbose_name='신청일')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='추천일')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='만료일')
    
    class Meta:
        verbose_name = '교육추천'
        verbose_name_plural = '교육추천'
        ordering = ['-created_at', 'priority']
    
    def __str__(self):
        return f"{self.employee.name} - {self.course.title} (우선순위: {self.priority})"


class SkillTrainingMapping(models.Model):
    """스킬-교육 매핑 테이블"""
    skill_name = models.CharField(max_length=100, verbose_name='스킬명')
    skill_category = models.CharField(max_length=50, verbose_name='스킬카테고리')
    courses = models.ManyToManyField(TrainingCourse, verbose_name='관련교육')
    
    # 매핑 강도
    relevance_score = models.FloatField(default=1.0, verbose_name='관련도점수')
    is_core_skill = models.BooleanField(default=False, verbose_name='핵심스킬여부')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '스킬-교육 매핑'
        verbose_name_plural = '스킬-교육 매핑'
        ordering = ['skill_category', 'skill_name']
    
    def __str__(self):
        return f"{self.skill_name} ({self.skill_category})"