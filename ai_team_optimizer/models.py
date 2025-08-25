"""
AI Team Optimizer Models - AI 팀 조합 최적화 모델
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from employees.models import Employee
import uuid


class Project(models.Model):
    """프로젝트 모델"""
    
    PROJECT_STATUS_CHOICES = [
        ('PLANNING', '기획 중'),
        ('ACTIVE', '진행 중'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
        ('ON_HOLD', '보류')
    ]
    
    PROJECT_PRIORITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '긴급')
    ]
    
    # 기본 정보
    project_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200, verbose_name="프로젝트명")
    description = models.TextField(verbose_name="프로젝트 설명")
    
    # 프로젝트 속성
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, 
                            default='PLANNING', verbose_name="상태")
    priority = models.CharField(max_length=20, choices=PROJECT_PRIORITY_CHOICES, 
                              default='MEDIUM', verbose_name="우선순위")
    
    # 일정
    start_date = models.DateField(verbose_name="시작일")
    end_date = models.DateField(verbose_name="종료일")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    
    # 예산 및 리소스
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, 
                               verbose_name="예산")
    estimated_hours = models.IntegerField(default=0, verbose_name="예상 작업시간")
    
    # 프로젝트 요구사항
    required_skills = models.JSONField(default=list, verbose_name="필요 스킬")
    team_size_min = models.IntegerField(default=1, verbose_name="최소 팀 크기")
    team_size_max = models.IntegerField(default=10, verbose_name="최대 팀 크기")
    
    # 성공 지표
    success_criteria = models.JSONField(default=list, verbose_name="성공 기준")
    risk_factors = models.JSONField(default=list, verbose_name="리스크 요소")
    
    class Meta:
        verbose_name = "프로젝트"
        verbose_name_plural = "프로젝트"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_duration_days(self):
        """프로젝트 기간 계산(일)"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0


class TeamComposition(models.Model):
    """팀 구성 모델"""
    
    COMPOSITION_STATUS_CHOICES = [
        ('DRAFT', '임시'),
        ('PROPOSED', '제안됨'),
        ('APPROVED', '승인됨'),
        ('ACTIVE', '활성'),
        ('COMPLETED', '완료'),
        ('REJECTED', '거절됨')
    ]
    
    # 기본 정보
    composition_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, 
                              related_name='team_compositions', verbose_name="프로젝트")
    name = models.CharField(max_length=200, verbose_name="팀 구성명")
    description = models.TextField(blank=True, verbose_name="설명")
    
    # 상태 정보
    status = models.CharField(max_length=20, choices=COMPOSITION_STATUS_CHOICES, 
                            default='DRAFT', verbose_name="상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    
    # AI 분석 결과
    ai_generated = models.BooleanField(default=True, verbose_name="AI 생성")
    compatibility_score = models.FloatField(default=0.0, verbose_name="호환성 점수")
    efficiency_score = models.FloatField(default=0.0, verbose_name="효율성 점수")
    risk_score = models.FloatField(default=0.0, verbose_name="리스크 점수")
    overall_score = models.FloatField(default=0.0, verbose_name="종합 점수")
    
    # AI 분석 세부사항
    ai_analysis = models.JSONField(default=dict, verbose_name="AI 분석")
    optimization_suggestions = models.JSONField(default=list, verbose_name="최적화 제안")
    potential_issues = models.JSONField(default=list, verbose_name="잠재적 문제")
    
    # 메타데이터
    created_by = models.CharField(max_length=100, default='AI', verbose_name="생성자")
    ai_model_version = models.CharField(max_length=50, default='1.0', verbose_name="AI 모델 버전")
    
    class Meta:
        verbose_name = "팀 구성"
        verbose_name_plural = "팀 구성"
        ordering = ['-overall_score', '-created_at']
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    def get_team_size(self):
        """팀 크기 조회"""
        return self.team_members.count()
    
    def get_total_cost(self):
        """총 비용 계산"""
        total = 0
        for member in self.team_members.all():
            if member.daily_rate:
                total += member.daily_rate * self.project.get_duration_days()
        return total


class TeamMember(models.Model):
    """팀 멤버 모델"""
    
    ROLE_CHOICES = [
        ('LEAD', '팀 리더'),
        ('SENIOR', '시니어'),
        ('JUNIOR', '주니어'),
        ('SPECIALIST', '전문가'),
        ('CONSULTANT', '컨설턴트'),
        ('SUPPORT', '지원')
    ]
    
    ALLOCATION_CHOICES = [
        ('FULL_TIME', '풀타임'),
        ('PART_TIME', '파트타임'),
        ('CONSULTANT', '컨설팅'),
        ('TEMPORARY', '임시')
    ]
    
    # 기본 정보
    team_composition = models.ForeignKey(TeamComposition, on_delete=models.CASCADE, 
                                       related_name='team_members', verbose_name="팀 구성")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="직원")
    
    # 역할 및 배정
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="역할")
    allocation_type = models.CharField(max_length=20, choices=ALLOCATION_CHOICES, 
                                     default='FULL_TIME', verbose_name="배정 유형")
    allocation_percentage = models.FloatField(default=100.0, verbose_name="배정 비율(%)")
    
    # 책임 및 기여도
    responsibilities = models.JSONField(default=list, verbose_name="담당 업무")
    expected_contribution = models.TextField(blank=True, verbose_name="기대 기여도")
    key_skills_utilized = models.JSONField(default=list, verbose_name="활용 핵심 스킬")
    
    # 비용 정보
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                   verbose_name="일당")
    estimated_hours = models.IntegerField(default=0, verbose_name="예상 작업시간")
    
    # AI 분석
    fit_score = models.FloatField(default=0.0, verbose_name="적합도 점수")
    synergy_score = models.FloatField(default=0.0, verbose_name="시너지 점수")
    availability_score = models.FloatField(default=0.0, verbose_name="가용성 점수")
    
    # 메타데이터
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="추가일시")
    is_confirmed = models.BooleanField(default=False, verbose_name="확정 여부")
    
    class Meta:
        verbose_name = "팀 멤버"
        verbose_name_plural = "팀 멤버"
        unique_together = ['team_composition', 'employee']
        ordering = ['role', '-fit_score']
    
    def __str__(self):
        return f"{self.employee.name} ({self.get_role_display()})"
    
    def get_total_cost(self):
        """총 비용 계산"""
        if self.daily_rate:
            project_days = self.team_composition.project.get_duration_days()
            return float(self.daily_rate) * project_days * (self.allocation_percentage / 100)
        return 0


class SkillRequirement(models.Model):
    """스킬 요구사항 모델"""
    
    PROFICIENCY_CHOICES = [
        ('BASIC', '기초'),
        ('INTERMEDIATE', '중급'),
        ('ADVANCED', '고급'),
        ('EXPERT', '전문가')
    ]
    
    IMPORTANCE_CHOICES = [
        ('OPTIONAL', '선택사항'),
        ('PREFERRED', '우대사항'),
        ('REQUIRED', '필수'),
        ('CRITICAL', '핵심')
    ]
    
    # 기본 정보
    project = models.ForeignKey(Project, on_delete=models.CASCADE, 
                              related_name='skill_requirements', verbose_name="프로젝트")
    skill_name = models.CharField(max_length=100, verbose_name="스킬명")
    category = models.CharField(max_length=50, default='TECHNICAL', verbose_name="카테고리")
    
    # 요구사항
    required_proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, 
                                          verbose_name="요구 숙련도")
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, 
                                verbose_name="중요도")
    
    # 추가 정보
    description = models.TextField(blank=True, verbose_name="설명")
    weight = models.FloatField(default=1.0, verbose_name="가중치")
    
    class Meta:
        verbose_name = "스킬 요구사항"
        verbose_name_plural = "스킬 요구사항"
        unique_together = ['project', 'skill_name']
        ordering = ['importance', 'skill_name']
    
    def __str__(self):
        return f"{self.skill_name} ({self.get_importance_display()})"


class TeamAnalytics(models.Model):
    """팀 분석 모델"""
    
    # 기본 정보
    team_composition = models.OneToOneField(TeamComposition, on_delete=models.CASCADE, 
                                          related_name='analytics', verbose_name="팀 구성")
    
    # 팀 역학 지표
    diversity_score = models.FloatField(default=0.0, verbose_name="다양성 점수")
    experience_balance = models.FloatField(default=0.0, verbose_name="경험 균형도")
    skill_coverage = models.FloatField(default=0.0, verbose_name="스킬 커버리지")
    communication_score = models.FloatField(default=0.0, verbose_name="소통 점수")
    
    # 성과 예측
    success_probability = models.FloatField(default=0.0, verbose_name="성공 확률")
    timeline_risk = models.FloatField(default=0.0, verbose_name="일정 리스크")
    budget_risk = models.FloatField(default=0.0, verbose_name="예산 리스크")
    quality_score = models.FloatField(default=0.0, verbose_name="품질 점수")
    
    # 상세 분석
    strengths = models.JSONField(default=list, verbose_name="강점")
    weaknesses = models.JSONField(default=list, verbose_name="약점")
    opportunities = models.JSONField(default=list, verbose_name="기회요소")
    threats = models.JSONField(default=list, verbose_name="위협요소")
    
    # AI 인사이트
    ai_recommendations = models.JSONField(default=list, verbose_name="AI 추천사항")
    improvement_suggestions = models.JSONField(default=list, verbose_name="개선 제안")
    alternative_members = models.JSONField(default=list, verbose_name="대안 멤버")
    
    # 메타데이터
    analyzed_at = models.DateTimeField(auto_now=True, verbose_name="분석일시")
    analysis_version = models.CharField(max_length=20, default='1.0', verbose_name="분석 버전")
    
    class Meta:
        verbose_name = "팀 분석"
        verbose_name_plural = "팀 분석"
    
    def __str__(self):
        return f"{self.team_composition} 분석"
    
    def get_overall_health_score(self):
        """종합 건강도 점수"""
        scores = [
            self.diversity_score,
            self.experience_balance,
            self.skill_coverage,
            self.communication_score,
            self.success_probability
        ]
        valid_scores = [s for s in scores if s > 0]
        return sum(valid_scores) / len(valid_scores) if valid_scores else 0


class OptimizationHistory(models.Model):
    """최적화 기록 모델"""
    
    ACTION_CHOICES = [
        ('CREATE', '생성'),
        ('MODIFY', '수정'),
        ('OPTIMIZE', '최적화'),
        ('APPROVE', '승인'),
        ('REJECT', '거절')
    ]
    
    # 기본 정보
    team_composition = models.ForeignKey(TeamComposition, on_delete=models.CASCADE, 
                                       related_name='optimization_history', 
                                       verbose_name="팀 구성")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="액션")
    description = models.TextField(verbose_name="설명")
    
    # 변경사항
    changes_made = models.JSONField(default=list, verbose_name="변경사항")
    score_before = models.FloatField(null=True, blank=True, verbose_name="변경 전 점수")
    score_after = models.FloatField(null=True, blank=True, verbose_name="변경 후 점수")
    
    # AI 정보
    ai_reasoning = models.TextField(blank=True, verbose_name="AI 추론")
    confidence_level = models.FloatField(default=0.0, verbose_name="신뢰도")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    created_by = models.CharField(max_length=100, default='AI', verbose_name="생성자")
    
    class Meta:
        verbose_name = "최적화 기록"
        verbose_name_plural = "최적화 기록"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team_composition} - {self.get_action_display()}"


class TeamTemplate(models.Model):
    """팀 템플릿 모델"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('DEVELOPMENT', '개발'),
        ('DESIGN', '디자인'),
        ('MARKETING', '마케팅'),
        ('RESEARCH', '연구'),
        ('CONSULTING', '컨설팅'),
        ('OPERATIONS', '운영'),
        ('CUSTOM', '커스텀')
    ]
    
    # 기본 정보
    name = models.CharField(max_length=200, verbose_name="템플릿명")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, 
                                   verbose_name="템플릿 유형")
    description = models.TextField(verbose_name="설명")
    
    # 팀 구조
    recommended_roles = models.JSONField(default=list, verbose_name="추천 역할")
    skill_requirements = models.JSONField(default=list, verbose_name="스킬 요구사항")
    team_size_range = models.JSONField(default=dict, verbose_name="팀 크기 범위")
    
    # 사용 통계
    usage_count = models.IntegerField(default=0, verbose_name="사용 횟수")
    success_rate = models.FloatField(default=0.0, verbose_name="성공률")
    average_score = models.FloatField(default=0.0, verbose_name="평균 점수")
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")
    is_active = models.BooleanField(default=True, verbose_name="활성화")
    
    class Meta:
        verbose_name = "팀 템플릿"
        verbose_name_plural = "팀 템플릿"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def increment_usage(self):
        """사용 횟수 증가"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

class TeamRecommendation(models.Model):
    """팀 추천 모델"""
    team_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recommended_for = models.CharField(max_length=200, blank=True)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_team_recommendation'
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"{self.team_name} (Score: {self.score})"
