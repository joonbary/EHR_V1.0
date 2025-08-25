"""
인재 분류 및 관리 모델
AIRISS 분석 결과와 연동하여 핵심인재, 관리필요인력, 승진후보자 등을 관리
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee


class TalentCategory(models.Model):
    """인재 카테고리 정의"""
    CATEGORY_TYPES = [
        ('CORE_TALENT', '핵심인재'),
        ('HIGH_POTENTIAL', '고잠재인력'),
        ('PROMOTION_CANDIDATE', '승진후보자'),
        ('NEEDS_ATTENTION', '관리필요인력'),
        ('RETENTION_RISK', '이직위험군'),
        ('STAR_PERFORMER', '우수성과자'),
        ('FUTURE_LEADER', '미래리더'),
        ('SPECIALIST', '전문가그룹'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='카테고리명')
    category_code = models.CharField(max_length=50, choices=CATEGORY_TYPES, unique=True, verbose_name='카테고리 코드')
    description = models.TextField(verbose_name='설명')
    criteria = models.JSONField(default=dict, verbose_name='선정 기준', help_text='AI 분석 기준 및 임계값')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '인재 카테고리'
        verbose_name_plural = '인재 카테고리'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.get_category_code_display()} - {self.name}"


class TalentPool(models.Model):
    """인재풀 관리 - AIRISS 분석 결과와 연동"""
    STATUS_CHOICES = [
        ('ACTIVE', '활성'),
        ('MONITORING', '모니터링'),
        ('PENDING', '검토중'),
        ('EXCLUDED', '제외'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    category = models.ForeignKey(TalentCategory, on_delete=models.CASCADE, verbose_name='인재 카테고리')
    
    # AIRISS 분석 연동
    ai_analysis_result = models.ForeignKey(
        'airiss.AIAnalysisResult', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='AI 분석 결과',
        help_text='AIRISS 분석 결과와 연동'
    )
    
    # 평가 점수
    ai_score = models.FloatField(verbose_name='AI 평가 점수', help_text='AIRISS 분석 점수 (0-100)')
    confidence_level = models.FloatField(verbose_name='신뢰도', help_text='AI 분석 신뢰도 (0-1)')
    
    # 상태 관리
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='상태')
    review_date = models.DateField(null=True, blank=True, verbose_name='검토일')
    valid_until = models.DateField(null=True, blank=True, verbose_name='유효기간')
    
    # 추가 정보
    strengths = models.JSONField(default=list, verbose_name='강점', help_text='AIRISS 분석 강점')
    development_areas = models.JSONField(default=list, verbose_name='개발영역', help_text='AIRISS 분석 개발필요영역')
    recommendations = models.JSONField(default=list, verbose_name='추천사항', help_text='AIRISS 추천사항')
    notes = models.TextField(blank=True, verbose_name='비고')
    
    # 메타데이터
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='talent_pool_additions', verbose_name='추가자')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='추가일')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='talent_pool_updates', verbose_name='수정자')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '인재풀'
        verbose_name_plural = '인재풀'
        ordering = ['-ai_score', '-added_at']
        unique_together = [['employee', 'category']]
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['ai_score']),
            models.Index(fields=['valid_until']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.category.get_category_code_display()}"
    
    @property
    def is_valid(self):
        """유효기간 확인"""
        if not self.valid_until:
            return True
        return timezone.now().date() <= self.valid_until
    
    @classmethod
    def update_from_airiss(cls, analysis_result):
        """AIRISS 분석 결과로부터 인재풀 업데이트"""
        from airiss.models import AIAnalysisResult
        
        if not isinstance(analysis_result, AIAnalysisResult):
            return None
        
        # 분석 유형에 따른 카테고리 매핑
        category_mapping = {
            'PROMOTION_POTENTIAL': 'PROMOTION_CANDIDATE',
            'TURNOVER_RISK': 'RETENTION_RISK',
            'TALENT_RECOMMENDATION': 'CORE_TALENT',
            'TEAM_PERFORMANCE': 'STAR_PERFORMER',
        }
        
        category_code = category_mapping.get(analysis_result.analysis_type.type_code)
        if not category_code:
            return None
        
        try:
            category = TalentCategory.objects.get(category_code=category_code, is_active=True)
        except TalentCategory.DoesNotExist:
            return None
        
        # 인재풀 업데이트 또는 생성
        talent_pool, created = cls.objects.update_or_create(
            employee=analysis_result.employee,
            category=category,
            defaults={
                'ai_analysis_result': analysis_result,
                'ai_score': analysis_result.score,
                'confidence_level': analysis_result.confidence,
                'strengths': analysis_result.result_data.get('strengths', []),
                'development_areas': analysis_result.result_data.get('weaknesses', []),
                'recommendations': analysis_result.recommendations,
                'status': 'ACTIVE' if analysis_result.score >= 80 else 'MONITORING',
                'valid_until': analysis_result.valid_until,
            }
        )
        
        return talent_pool


class PromotionCandidate(models.Model):
    """승진 후보자 관리"""
    READINESS_LEVELS = [
        ('READY', '준비됨'),
        ('NEAR_READY', '곧 준비됨'),
        ('DEVELOPING', '개발중'),
        ('NOT_READY', '준비안됨'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='인재풀 연결')
    
    # 승진 정보
    current_position = models.CharField(max_length=50, verbose_name='현재 직급')
    target_position = models.CharField(max_length=50, verbose_name='목표 직급')
    readiness_level = models.CharField(max_length=20, choices=READINESS_LEVELS, verbose_name='준비도')
    expected_promotion_date = models.DateField(null=True, blank=True, verbose_name='예상 승진일')
    
    # 평가 정보
    performance_score = models.FloatField(verbose_name='성과 점수')
    potential_score = models.FloatField(verbose_name='잠재력 점수')
    ai_recommendation_score = models.FloatField(verbose_name='AI 추천 점수', help_text='AIRISS 승진 가능성 점수')
    
    # 개발 계획
    development_plan = models.JSONField(default=dict, verbose_name='개발 계획')
    completed_requirements = models.JSONField(default=list, verbose_name='완료된 요구사항')
    pending_requirements = models.JSONField(default=list, verbose_name='대기중인 요구사항')
    
    # 상태
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    review_notes = models.TextField(blank=True, verbose_name='검토 노트')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='검토자')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='검토일')
    
    class Meta:
        verbose_name = '승진 후보자'
        verbose_name_plural = '승진 후보자'
        ordering = ['-ai_recommendation_score', '-performance_score']
        unique_together = [['employee', 'target_position']]
    
    def __str__(self):
        return f"{self.employee.name} - {self.target_position} ({self.get_readiness_level_display()})"


class RetentionRisk(models.Model):
    """이직 위험 관리"""
    RISK_LEVELS = [
        ('CRITICAL', '매우높음'),
        ('HIGH', '높음'),
        ('MEDIUM', '중간'),
        ('LOW', '낮음'),
    ]
    
    ACTION_STATUS = [
        ('PENDING', '대기중'),
        ('IN_PROGRESS', '진행중'),
        ('COMPLETED', '완료'),
        ('FAILED', '실패'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='인재풀 연결')
    
    # 위험도 평가
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, verbose_name='위험 수준')
    risk_score = models.FloatField(verbose_name='위험 점수', help_text='AIRISS 이직 위험도 점수 (0-100)')
    risk_factors = models.JSONField(default=list, verbose_name='위험 요인')
    
    # 대응 계획
    retention_strategy = models.TextField(verbose_name='유지 전략')
    action_items = models.JSONField(default=list, verbose_name='조치 항목')
    action_status = models.CharField(max_length=20, choices=ACTION_STATUS, default='PENDING', verbose_name='조치 상태')
    
    # 결과 추적
    intervention_date = models.DateField(null=True, blank=True, verbose_name='개입일')
    outcome = models.TextField(blank=True, verbose_name='결과')
    is_retained = models.BooleanField(null=True, blank=True, verbose_name='유지 여부')
    
    # 메타데이터
    identified_date = models.DateTimeField(auto_now_add=True, verbose_name='식별일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='담당자')
    
    class Meta:
        verbose_name = '이직 위험'
        verbose_name_plural = '이직 위험'
        ordering = ['-risk_score', '-identified_date']
        indexes = [
            models.Index(fields=['risk_level', 'action_status']),
            models.Index(fields=['risk_score']),
        ]
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_risk_level_display()} ({self.risk_score}%)"


class TalentDevelopment(models.Model):
    """인재 개발 계획"""
    PRIORITY_LEVELS = [
        ('URGENT', '긴급'),
        ('HIGH', '높음'),
        ('MEDIUM', '중간'),
        ('LOW', '낮음'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='직원')
    talent_pool = models.ForeignKey(TalentPool, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='인재풀 연결')
    
    # 개발 계획
    development_goal = models.CharField(max_length=200, verbose_name='개발 목표')
    current_state = models.TextField(verbose_name='현재 상태')
    target_state = models.TextField(verbose_name='목표 상태')
    
    # 개발 활동
    activities = models.JSONField(default=list, verbose_name='개발 활동')
    timeline = models.JSONField(default=dict, verbose_name='일정')
    resources_needed = models.JSONField(default=list, verbose_name='필요 자원')
    
    # 진행 상황
    progress_percentage = models.IntegerField(default=0, verbose_name='진행률')
    milestones = models.JSONField(default=list, verbose_name='마일스톤')
    completed_activities = models.JSONField(default=list, verbose_name='완료된 활동')
    
    # 우선순위 및 상태
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='MEDIUM', verbose_name='우선순위')
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    
    # 날짜
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    
    # 메타데이터
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='development_plans_created', verbose_name='생성자')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '인재 개발 계획'
        verbose_name_plural = '인재 개발 계획'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.employee.name} - {self.development_goal}"