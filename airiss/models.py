from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
import json


class AIAnalysisType(models.Model):
    """AI 분석 유형 정의"""
    TYPE_CHOICES = [
        ('TURNOVER_RISK', '퇴사 위험도 예측'),
        ('PROMOTION_POTENTIAL', '승진 가능성 분석'),
        ('TEAM_PERFORMANCE', '팀 성과 예측'),
        ('TALENT_RECOMMENDATION', '인재 추천'),
        ('COMPENSATION_OPTIMIZATION', '급여 최적화'),
        ('SKILL_GAP_ANALYSIS', '역량 격차 분석'),
        ('CAREER_PATH', '경력 경로 추천'),
        ('ENGAGEMENT_PREDICTION', '직원 참여도 예측'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    type_code = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'AI 분석 유형'
        verbose_name_plural = 'AI 분석 유형'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AIAnalysisResult(models.Model):
    """AI 분석 결과 저장"""
    analysis_type = models.ForeignKey(AIAnalysisType, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    department = models.CharField(max_length=20, null=True, blank=True, help_text="부서명")
    
    # 분석 점수 및 결과
    score = models.FloatField(help_text="예측 점수 (0-100)")
    confidence = models.FloatField(help_text="신뢰도 (0-1)")
    result_data = models.JSONField(default=dict, help_text="상세 분석 결과")
    
    # 추천 및 인사이트
    recommendations = models.JSONField(default=list, help_text="추천 사항")
    insights = models.TextField(blank=True, help_text="주요 인사이트")
    
    # 메타데이터
    analyzed_at = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'AI 분석 결과'
        verbose_name_plural = 'AI 분석 결과'
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['analysis_type', 'employee']),
            models.Index(fields=['analyzed_at']),
        ]
    
    def __str__(self):
        if self.employee:
            return f"{self.analysis_type.name} - {self.employee.name}"
        elif self.department:
            return f"{self.analysis_type.name} - {self.department} 부서"
        return f"{self.analysis_type.name} - 전사 분석"
    
    @property
    def is_valid(self):
        """분석 결과가 아직 유효한지 확인"""
        if not self.valid_until:
            return True
        return timezone.now() < self.valid_until


class HRChatbotConversation(models.Model):
    """HR 챗봇 대화 기록"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    
    # 대화 내용
    messages = models.JSONField(default=list, help_text="대화 메시지 리스트")
    context = models.JSONField(default=dict, help_text="대화 컨텍스트")
    
    # 상태 관리
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    
    # 평가
    satisfaction_score = models.IntegerField(null=True, blank=True, help_text="만족도 (1-5)")
    feedback = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'HR 챗봇 대화'
        verbose_name_plural = 'HR 챗봇 대화'
        ordering = ['-last_message_at']
    
    def __str__(self):
        return f"대화 {self.id} - {self.user.username}"
    
    def add_message(self, role, content, metadata=None):
        """대화에 메시지 추가"""
        message = {
            'role': role,  # 'user', 'assistant', 'system'
            'content': content,
            'timestamp': timezone.now().isoformat(),
        }
        if metadata:
            message['metadata'] = metadata
        
        self.messages.append(message)
        self.save()


class AIInsight(models.Model):
    """AI 기반 HR 인사이트"""
    PRIORITY_CHOICES = [
        ('HIGH', '높음'),
        ('MEDIUM', '중간'),
        ('LOW', '낮음'),
    ]
    
    CATEGORY_CHOICES = [
        ('RETENTION', '인재 유지'),
        ('PERFORMANCE', '성과 관리'),
        ('DEVELOPMENT', '인재 개발'),
        ('COMPENSATION', '보상 관리'),
        ('ENGAGEMENT', '직원 참여'),
        ('DIVERSITY', '다양성 및 포용성'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # 인사이트 내용
    description = models.TextField()
    impact_analysis = models.TextField(help_text="예상 영향 분석")
    action_items = models.JSONField(default=list, help_text="권장 조치 사항")
    
    # 대상
    target_departments = models.JSONField(default=list, blank=True, help_text="대상 부서 리스트")
    target_employees = models.ManyToManyField(Employee, blank=True)
    
    # 메타데이터
    generated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    
    # 추적
    views_count = models.IntegerField(default=0)
    actions_taken = models.JSONField(default=list)
    
    class Meta:
        verbose_name = 'AI 인사이트'
        verbose_name_plural = 'AI 인사이트'
        ordering = ['-generated_at', '-priority']
    
    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"


class AIModelConfig(models.Model):
    """AI 모델 설정 관리"""
    model_name = models.CharField(max_length=100, unique=True)
    analysis_type = models.ForeignKey(AIAnalysisType, on_delete=models.CASCADE)
    
    # 모델 파라미터
    parameters = models.JSONField(default=dict, help_text="모델 파라미터")
    thresholds = models.JSONField(default=dict, help_text="임계값 설정")
    
    # 모델 정보
    version = models.CharField(max_length=50)
    accuracy = models.FloatField(null=True, blank=True, help_text="모델 정확도")
    last_trained = models.DateTimeField(null=True, blank=True)
    
    # 상태
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'AI 모델 설정'
        verbose_name_plural = 'AI 모델 설정'
        ordering = ['model_name']
    
    def __str__(self):
        return f"{self.model_name} v{self.version}"
