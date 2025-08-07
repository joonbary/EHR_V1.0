"""
AI Predictions 모델 정의 - 이직 위험도 분석
"""
from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from decimal import Decimal
import json


class TurnoverRisk(models.Model):
    """이직 위험도 분석 결과"""
    
    RISK_LEVEL_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('CRITICAL', '매우 높음'),
    ]
    
    PREDICTION_STATUS_CHOICES = [
        ('ACTIVE', '활성'),
        ('MONITORING', '모니터링 중'),
        ('RESOLVED', '해결됨'),
        ('ARCHIVED', '보관됨'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='turnover_risks', verbose_name='직원')
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, verbose_name='위험 수준')
    risk_score = models.FloatField(help_text='0.0-1.0 사이 위험도 점수', verbose_name='위험도 점수')
    
    # 예측 정보
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name='예측 일시')
    predicted_departure_date = models.DateField(null=True, blank=True, verbose_name='예상 퇴사일')
    confidence_level = models.FloatField(default=0.0, verbose_name='AI 신뢰도')
    
    # 위험 요소
    primary_risk_factors = models.JSONField(default=list, verbose_name='주요 위험 요소')
    secondary_risk_factors = models.JSONField(default=list, verbose_name='부차 위험 요소')
    protective_factors = models.JSONField(default=list, verbose_name='보호 요소')
    
    # AI 분석 결과
    ai_analysis = models.JSONField(default=dict, verbose_name='AI 분석 결과')
    ai_recommendations = models.JSONField(default=list, verbose_name='AI 추천 사항')
    ai_model_version = models.CharField(max_length=50, default='v1.0', verbose_name='AI 모델 버전')
    
    # 상태 관리
    status = models.CharField(max_length=20, choices=PREDICTION_STATUS_CHOICES, default='ACTIVE', verbose_name='상태')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='마지막 업데이트')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='생성자')
    
    class Meta:
        ordering = ['-risk_score', '-prediction_date']
        verbose_name = '이직 위험도'
        verbose_name_plural = '이직 위험도'
        unique_together = ['employee', 'prediction_date']
    
    def __str__(self):
        return f"{self.employee.name} - {self.get_risk_level_display()} ({self.risk_score:.2f})"
    
    def get_risk_color(self):
        """위험도 레벨별 색상 반환"""
        colors = {
            'LOW': '#28a745',      # 녹색
            'MEDIUM': '#ffc107',   # 노란색
            'HIGH': '#fd7e14',     # 주황색
            'CRITICAL': '#dc3545'  # 빨간색
        }
        return colors.get(self.risk_level, '#6c757d')
    
    def get_risk_factors_summary(self):
        """위험 요소 요약 반환"""
        total_factors = len(self.primary_risk_factors) + len(self.secondary_risk_factors)
        return f"주요: {len(self.primary_risk_factors)}개, 부차: {len(self.secondary_risk_factors)}개"


class RiskFactor(models.Model):
    """위험 요소 정의"""
    
    FACTOR_TYPE_CHOICES = [
        ('PERFORMANCE', '성과'),
        ('ENGAGEMENT', '몰입도'),
        ('COMPENSATION', '보상'),
        ('WORKLOAD', '업무량'),
        ('RELATIONSHIP', '관계'),
        ('CAREER', '경력 개발'),
        ('WORK_ENVIRONMENT', '근무 환경'),
        ('EXTERNAL', '외부 요인'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='요소명')
    factor_type = models.CharField(max_length=20, choices=FACTOR_TYPE_CHOICES, verbose_name='요소 유형')
    description = models.TextField(verbose_name='설명')
    
    # 가중치
    base_weight = models.FloatField(default=1.0, verbose_name='기본 가중치')
    adjustment_rules = models.JSONField(default=dict, verbose_name='조정 규칙')
    
    # 메타데이터
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        ordering = ['factor_type', 'name']
        verbose_name = '위험 요소'
        verbose_name_plural = '위험 요소'
    
    def __str__(self):
        return f"[{self.get_factor_type_display()}] {self.name}"


class RetentionPlan(models.Model):
    """직원 유지 계획"""
    
    PLAN_STATUS_CHOICES = [
        ('DRAFT', '초안'),
        ('ACTIVE', '실행 중'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
        ('ON_HOLD', '보류'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', '낮음'),
        ('MEDIUM', '보통'),
        ('HIGH', '높음'),
        ('URGENT', '긴급'),
    ]
    
    turnover_risk = models.OneToOneField(TurnoverRisk, on_delete=models.CASCADE, related_name='retention_plan', verbose_name='이직 위험도')
    
    # 계획 정보
    title = models.CharField(max_length=200, verbose_name='계획명')
    description = models.TextField(verbose_name='계획 설명')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='우선순위')
    status = models.CharField(max_length=20, choices=PLAN_STATUS_CHOICES, default='DRAFT', verbose_name='상태')
    
    # 액션 아이템
    action_items = models.JSONField(default=list, verbose_name='실행 항목')
    success_metrics = models.JSONField(default=list, verbose_name='성공 지표')
    
    # 담당자 및 일정
    assigned_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='retention_plans_as_manager', verbose_name='담당 관리자')
    assigned_hr = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='retention_plans_as_hr', verbose_name='담당 HR')
    
    start_date = models.DateField(verbose_name='시작일')
    target_completion_date = models.DateField(verbose_name='목표 완료일')
    actual_completion_date = models.DateField(null=True, blank=True, verbose_name='실제 완료일')
    
    # 예산 및 리소스
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='예상 예산')
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='실제 비용')
    required_resources = models.JSONField(default=list, verbose_name='필요 리소스')
    
    # 결과 추적
    effectiveness_score = models.FloatField(null=True, blank=True, verbose_name='효과성 점수')
    employee_feedback = models.TextField(blank=True, verbose_name='직원 피드백')
    manager_notes = models.TextField(blank=True, verbose_name='관리자 노트')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='생성자')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = '유지 계획'
        verbose_name_plural = '유지 계획'
    
    def __str__(self):
        return f"{self.turnover_risk.employee.name} - {self.title}"
    
    def get_progress_percentage(self):
        """진행률 계산"""
        if not self.action_items:
            return 0
        
        completed_items = sum(1 for item in self.action_items if item.get('completed', False))
        return (completed_items / len(self.action_items)) * 100
    
    def get_days_remaining(self):
        """남은 일수 계산"""
        from django.utils import timezone
        if self.target_completion_date:
            remaining = self.target_completion_date - timezone.now().date()
            return max(0, remaining.days)
        return None


class TurnoverAlert(models.Model):
    """이직 위험도 알림"""
    
    ALERT_TYPE_CHOICES = [
        ('RISK_INCREASE', '위험도 증가'),
        ('CRITICAL_LEVEL', '임계 수준 도달'),
        ('PATTERN_DETECTED', '패턴 감지'),
        ('PLAN_OVERDUE', '계획 지연'),
        ('SUCCESS_UPDATE', '성공 업데이트'),
    ]
    
    SEVERITY_CHOICES = [
        ('INFO', '정보'),
        ('WARNING', '경고'),
        ('CRITICAL', '중요'),
        ('EMERGENCY', '긴급'),
    ]
    
    turnover_risk = models.ForeignKey(TurnoverRisk, on_delete=models.CASCADE, related_name='alerts', verbose_name='이직 위험도')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, verbose_name='알림 유형')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name='심각도')
    
    # 알림 내용
    title = models.CharField(max_length=200, verbose_name='제목')
    message = models.TextField(verbose_name='메시지')
    details = models.JSONField(default=dict, verbose_name='상세 정보')
    
    # 수신자
    recipients = models.ManyToManyField(User, related_name='turnover_alerts', verbose_name='수신자')
    
    # 상태
    is_read = models.BooleanField(default=False, verbose_name='읽음')
    is_acknowledged = models.BooleanField(default=False, verbose_name='확인')
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='acknowledged_alerts', verbose_name='확인자')
    acknowledged_at = models.DateTimeField(null=True, blank=True, verbose_name='확인 시간')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='만료 시간')
    
    class Meta:
        ordering = ['-severity', '-created_at']
        verbose_name = '이직 위험도 알림'
        verbose_name_plural = '이직 위험도 알림'
    
    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"
    
    def get_severity_color(self):
        """심각도별 색상 반환"""
        colors = {
            'INFO': '#17a2b8',      # 파란색
            'WARNING': '#ffc107',   # 노란색
            'CRITICAL': '#fd7e14',  # 주황색
            'EMERGENCY': '#dc3545'  # 빨간색
        }
        return colors.get(self.severity, '#6c757d')