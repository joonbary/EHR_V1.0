"""
AI Insights 모델 정의
"""
from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
import json


class AIInsight(models.Model):
    """AI가 생성한 인사이트"""
    
    PRIORITY_CHOICES = [
        ('URGENT', '긴급'),
        ('HIGH', '높음'),
        ('MEDIUM', '보통'),
        ('LOW', '낮음'),
    ]
    
    CATEGORY_CHOICES = [
        ('TURNOVER', '이직 위험'),
        ('PERFORMANCE', '성과'),
        ('ENGAGEMENT', '몰입도'),
        ('COMPENSATION', '보상'),
        ('TEAM', '팀 역학'),
        ('LEADERSHIP', '리더십'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='설명')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='카테고리')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='우선순위')
    
    # 영향 범위
    affected_employees = models.ManyToManyField(Employee, blank=True, related_name='affected_by_insights', verbose_name='영향받는 직원')
    affected_department = models.CharField(max_length=100, blank=True, verbose_name='영향받는 부서')
    
    # AI 분석 데이터
    ai_confidence = models.FloatField(default=0.0, verbose_name='AI 신뢰도')
    ai_model_used = models.CharField(max_length=50, default='gpt-4', verbose_name='사용된 AI 모델')
    raw_analysis = models.JSONField(default=dict, verbose_name='원본 분석 데이터')
    
    # 추천 액션
    recommended_actions = models.JSONField(default=list, verbose_name='추천 액션')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    is_resolved = models.BooleanField(default=False, verbose_name='해결됨')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='해결일시')
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='해결자')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'AI 인사이트'
        verbose_name_plural = 'AI 인사이트'
    
    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"
    
    def get_recommended_actions_list(self):
        """추천 액션 리스트 반환"""
        if isinstance(self.recommended_actions, str):
            return json.loads(self.recommended_actions)
        return self.recommended_actions


class DailyMetrics(models.Model):
    """일일 HR 메트릭"""
    
    date = models.DateField(unique=True, verbose_name='날짜')
    
    # 인력 지표
    total_employees = models.IntegerField(default=0, verbose_name='총 직원수')
    new_hires = models.IntegerField(default=0, verbose_name='신규 입사')
    resignations = models.IntegerField(default=0, verbose_name='퇴사')
    
    # 성과 지표
    avg_performance_score = models.FloatField(default=0.0, verbose_name='평균 성과 점수')
    high_performers_count = models.IntegerField(default=0, verbose_name='고성과자 수')
    low_performers_count = models.IntegerField(default=0, verbose_name='저성과자 수')
    
    # 몰입도 지표
    avg_engagement_score = models.FloatField(default=0.0, verbose_name='평균 몰입도')
    burnout_risk_count = models.IntegerField(default=0, verbose_name='번아웃 위험 인원')
    
    # 보상 지표
    avg_compensation = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='평균 보상')
    compensation_budget_used = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='보상 예산 사용률')
    
    # AI 분석
    ai_summary = models.TextField(blank=True, verbose_name='AI 요약')
    ai_predictions = models.JSONField(default=dict, verbose_name='AI 예측')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        ordering = ['-date']
        verbose_name = '일일 메트릭'
        verbose_name_plural = '일일 메트릭'
    
    def __str__(self):
        return f"{self.date} 메트릭"


class ActionItem(models.Model):
    """AI가 추천한 액션 아이템"""
    
    STATUS_CHOICES = [
        ('PENDING', '대기중'),
        ('IN_PROGRESS', '진행중'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
    ]
    
    PRIORITY_CHOICES = [
        ('URGENT', '긴급'),
        ('HIGH', '높음'),
        ('MEDIUM', '보통'),
        ('LOW', '낮음'),
    ]
    
    insight = models.ForeignKey(AIInsight, on_delete=models.CASCADE, related_name='action_items', verbose_name='관련 인사이트')
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='설명')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM', verbose_name='우선순위')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='상태')
    
    # 담당자
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, 
                                   related_name='assigned_actions', verbose_name='담당자')
    
    # 대상
    target_employee = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL, related_name='targeted_by_actions', verbose_name='대상 직원')
    target_department = models.CharField(max_length=100, blank=True, verbose_name='대상 부서')
    
    # 일정
    due_date = models.DateField(null=True, blank=True, verbose_name='마감일')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일시')
    
    # AI 추천 정보
    expected_impact = models.TextField(blank=True, verbose_name='예상 효과')
    ai_confidence = models.FloatField(default=0.0, verbose_name='AI 신뢰도')
    
    # 메타데이터
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    notes = models.TextField(blank=True, verbose_name='메모')
    
    class Meta:
        ordering = ['-priority', 'due_date']
        verbose_name = '액션 아이템'
        verbose_name_plural = '액션 아이템'
    
    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"
